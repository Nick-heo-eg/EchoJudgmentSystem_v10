# -*- coding: utf-8 -*-
"""
LLM-First 3-Call Chain Conversation Router
모든 입력을 LLM#1(NLU) → LLM#2(Draft) → LLM#3(Rewrite) 경로로 처리
"""
from __future__ import annotations
import time, json, uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class ConversationTrace:
    """대화 처리 추적"""

    request_id: str
    user_input: str
    nlu_result: Dict[str, Any]
    draft_response: str
    final_response: str
    verification_result: Dict[str, Any]
    total_latency_ms: int
    tokens_used: int
    success: bool
    error: Optional[str] = None


class ConversationRouter:
    """LLM-First 3-콜 체인 라우터"""

    def __init__(self):
        self.config = self._load_config()
        self.trace_writer = self._init_trace_writer()

    def _load_config(self) -> Dict[str, Any]:
        """글로벌 설정 로드"""
        config_path = (
            Path(__file__).parent.parent.parent / "config" / "global_config.yaml"
        )
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _init_trace_writer(self):
        """추적 로그 라이터 초기화"""
        from echo_engine.logging.trace_writer import TraceWriter

        return TraceWriter()

    def handle_message(
        self, text: str, context: Dict[str, Any] = None
    ) -> tuple[str, ConversationTrace]:
        """메시지 처리 메인 함수"""
        request_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # 1. NLU (Natural Language Understanding)
            nlu_result = self._call_llm_nlu(text)

            # 2. Echo Policy 적용
            policy = self._merge_echo_policy(nlu_result, context or {})

            # 3. Draft 생성
            draft_response = self._call_llm_draft(nlu_result, policy)

            # 4. Echo Verification
            verification = self._echo_verify(draft_response, policy)

            # 5. Final Rewrite
            if verification["requires_fix"]:
                final_response = self._call_llm_rewrite(
                    verification["suggested_fix"], policy
                )
            else:
                final_response = self._call_llm_rewrite(draft_response, policy)

            # 6. 추적 기록
            total_latency = int((time.time() - start_time) * 1000)
            trace = ConversationTrace(
                request_id=request_id,
                user_input=text,
                nlu_result=nlu_result,
                draft_response=draft_response,
                final_response=final_response,
                verification_result=verification,
                total_latency_ms=total_latency,
                tokens_used=self._calculate_tokens(text, final_response),
                success=True,
            )

            self.trace_writer.write(trace)
            return final_response, trace

        except Exception as e:
            # 실패 처리 - Fail-Closed 모드
            error_msg = self._handle_failure(str(e), context)
            trace = ConversationTrace(
                request_id=request_id,
                user_input=text,
                nlu_result={},
                draft_response="",
                final_response=error_msg,
                verification_result={},
                total_latency_ms=int((time.time() - start_time) * 1000),
                tokens_used=0,
                success=False,
                error=str(e),
            )

            self.trace_writer.write(trace)
            return error_msg, trace

    def _call_llm_nlu(self, text: str) -> Dict[str, Any]:
        """LLM#1: 자연어 이해 (JSON 반환)"""
        from echo_engine.providers.llm_client import get_llm_client

        prompt = f"""사용자 입력을 분석하여 JSON으로 반환하세요. 불확실한 경우 '?' 표기.

입력: {text}

반환할 JSON 형식:
{{
  "intent": "health|planning|development|problem_solving|casual",
  "domain": "의료|계획|개발|문제해결|일상",
  "entities": {{"key": "value"}},
  "emotion": "neutral|concern|stress|curiosity|joy",
  "missing_info": ["필요한 추가 정보들"],
  "urgency": "low|medium|high",
  "safety_flags": []
}}"""

        client = get_llm_client()
        response = client.generate(
            prompt, model="gpt-3.5-turbo", max_tokens=300, temperature=0.1
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본값
            return {
                "intent": "casual",
                "domain": "일상",
                "entities": {},
                "emotion": "neutral",
                "missing_info": [],
                "urgency": "low",
                "safety_flags": [],
            }

    def _merge_echo_policy(
        self, nlu_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Echo 정책 적용"""
        from .policies.echo_policy import EchoPolicy

        policy_engine = EchoPolicy()
        return policy_engine.merge(nlu_result, context)

    def _call_llm_draft(
        self, nlu_result: Dict[str, Any], policy: Dict[str, Any]
    ) -> str:
        """LLM#2: 초안 생성"""
        from echo_engine.providers.llm_client import get_llm_client

        domain_context = self._get_domain_context(nlu_result["domain"])
        signature_guide = policy.get("signature_tone", "")

        prompt = f"""다음 분석 결과를 바탕으로 행동 지향적 응답 초안을 작성하세요:

분석: {json.dumps(nlu_result, ensure_ascii=False)}
정책: {policy.get('guidelines', '')}
시그니처: {signature_guide}
도메인 가이드: {domain_context}

응답 요구사항:
1. 구체적이고 실행 가능한 조언
2. 필요시 단계별 가이드 제공
3. 안전 고지 포함 (의료/위급 상황)
4. 다음 질문 2-3개 준비
5. 공감과 지지적 톤

초안을 작성하세요:"""

        client = get_llm_client()
        return client.generate(
            prompt, model="gpt-3.5-turbo", max_tokens=800, temperature=0.7
        )

    def _call_llm_rewrite(self, draft: str, policy: Dict[str, Any]) -> str:
        """LLM#3: 최종 리라이트"""
        from echo_engine.providers.llm_client import get_llm_client

        signature_rules = policy.get("signature_rules", {})

        prompt = f"""다음 초안을 자연스러운 한국어로 다듬어주세요:

초안: {draft}

리라이트 규칙:
1. 자연스러운 한국어 조사·호흡
2. 중복 표현 제거
3. 시그니처 톤 일관성: {signature_rules.get('tone', 'friendly')}
4. 적절한 길이 (너무 길거나 짧지 않게)
5. 이모지 1-2개 자연스럽게 포함

최종 응답:"""

        client = get_llm_client()
        return client.generate(
            prompt, model="gpt-3.5-turbo", max_tokens=600, temperature=0.3
        )

    def _echo_verify(self, draft: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Echo 검증 레이어"""
        from echo_engine.verify.echo_verify import EchoVerifier

        verifier = EchoVerifier()
        return verifier.check(draft, policy)

    def _get_domain_context(self, domain: str) -> str:
        """도메인별 컨텍스트 가이드"""
        domain_guides = {
            "의료": "의학적 조언이 아닌 일반적 건강 정보만 제공. 위급 상황 시 의료진 상담 권유.",
            "계획": "구체적이고 실행 가능한 단계별 계획. 우선순위와 시간 배분 포함.",
            "개발": "실용적인 코드 예시와 디버깅 단계. 모범 사례와 보안 고려사항 포함.",
            "문제해결": "체계적 분석과 단계별 해결 프로세스. 다양한 관점과 대안 제시.",
            "일상": "공감적이고 지지적인 대화. 자연스럽고 따뜻한 톤.",
        }
        return domain_guides.get(domain, "자연스럽고 도움되는 대화")

    def _handle_failure(self, error: str, context: Dict[str, Any]) -> str:
        """실패 처리 - Fail-Closed 모드"""
        admin_mode = context.get("admin_mode", False)

        if admin_mode and context.get("emergency_only", False):
            # 관리자 모드에서 위급 상황일 때만 템플릿 사용
            return self._get_admin_fallback(error)

        # 일반 사용자는 재시도 안내
        if "rate" in error.lower() or "limit" in error.lower():
            return self.config.get("failure_messages", {}).get(
                "rate_limit", "현재 요청이 많아 잠시 대기 중입니다. 곧 응답드릴게요."
            )
        else:
            return self.config.get("failure_messages", {}).get(
                "llm_unavailable",
                "고급 언어 모듈 연결이 불안정합니다. 곧바로 다시 시도할게요. 위급 상황이면 바로 알려주세요.",
            )

    def _get_admin_fallback(self, error: str) -> str:
        """관리자 전용 폴백"""
        return f"[ADMIN] 시스템 장애 감지: {error}\n기본 응답 모드로 전환됩니다. 사용자에게는 재시도 안내를 제공하세요."

    def _calculate_tokens(self, input_text: str, output_text: str) -> int:
        """토큰 사용량 추정"""
        # 간단한 추정 (실제로는 tokenizer 사용)
        return len(input_text.split()) + len(output_text.split())


# 편의 함수
def route_conversation(
    text: str, context: Dict[str, Any] = None
) -> tuple[str, ConversationTrace]:
    """대화 라우팅 메인 함수"""
    router = ConversationRouter()
    return router.handle_message(text, context)
