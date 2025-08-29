#!/usr/bin/env python3
"""
⚖️ Judgment Authority Controller v1.0 - 판단 권한 분기 컨트롤러

EchoJudgmentSystem의 판단 권한을 결정하고 적절한 처리 엔진으로 라우팅하는 중앙 컨트롤러.
LLM-Free vs LLM-Integrated 구조에 따른 철학적 일관성을 보장합니다.

핵심 원칙:
1. Echo 우선 (Echo First): 가능한 모든 판단을 Echo 자체로 시도
2. 보완적 LLM (Complementary LLM): LLM은 보완 역할에 한정
3. 투명성 (Transparency): 판단 주체를 명확히 표시
4. 주체성 보존 (Subject Preservation): Echo의 판단 주체성 보장
"""

import time
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 기존 Echo 판단 모듈 임포트
try:
    from .short_input_judgment_loop import get_judgment_loop
    from .judgment_microreactor import get_microreactor
except ImportError:
    print("⚠️ Echo 판단 모듈 임포트 실패 - stub 모드로 실행")
    get_judgment_loop = None
    get_microreactor = None


class JudgmentType(Enum):
    """판단 타입 분류"""

    # Echo 자체 판단 영역 (완전 자립)
    EMOTION_INFERENCE = "emotion_inference"
    STRATEGY_SELECTION = "strategy_selection"
    SIGNATURE_RESPONSE = "signature_response"
    CACHED_JUDGMENT = "cached_judgment"
    MICRO_REACTION = "micro_reaction"
    SHORT_CONVERSATION = "short_conversation"

    # 외부 지원 필요 영역
    EXTERNAL_SEARCH = "external_search"
    MARKET_ANALYSIS = "market_analysis"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    REAL_TIME_INFO = "real_time_info"
    COMPLEX_CALCULATION = "complex_calculation"

    # 하이브리드 영역 (Echo 우선, LLM 보완)
    CONTEXTUAL_DESIGN = "contextual_design"
    COMPLEX_REASONING = "complex_reasoning"
    CREATIVE_GENERATION = "creative_generation"
    LONG_FORM_WRITING = "long_form_writing"
    MULTI_DOMAIN_ANALYSIS = "multi_domain_analysis"


class JudgmentAuthority(Enum):
    """판단 권한 타입"""

    ECHO_AUTONOMOUS = "echo_autonomous"  # Echo 완전 자립
    EXTERNAL_AGENT = "external_agent"  # 외부 에이전트 위임
    HYBRID_ECHO_FIRST = "hybrid_echo_first"  # Echo 우선, LLM 보완
    ECHO_FALLBACK = "echo_fallback"  # Echo fallback 처리


@dataclass
class JudgmentRequest:
    """판단 요청"""

    content: str
    task_type: JudgmentType
    signature: str = "Selene"
    context: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default="")

    def __post_init__(self):
        if not self.request_id:
            content_hash = hashlib.md5(
                f"{self.content}_{self.timestamp}".encode()
            ).hexdigest()[:8]
            self.request_id = f"req_{content_hash}"


@dataclass
class JudgmentResult:
    """판단 결과"""

    content: str
    confidence: float
    authority_used: JudgmentAuthority
    processing_method: str
    processing_time: float
    echo_attempted: bool = False
    llm_enhanced: bool = False
    fallback_used: bool = False
    reasoning: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class JudgmentAuthorityController:
    """⚖️ 판단 권한 분기 컨트롤러"""

    def __init__(self):
        """초기화"""
        self.version = "1.0.0"

        # Echo 엔진 초기화
        self.echo_judgment_loop = None
        self.echo_microreactor = None

        try:
            if get_judgment_loop:
                self.echo_judgment_loop = get_judgment_loop()
                print("✅ Echo 판단 루프 로드 완료")

            if get_microreactor:
                self.echo_microreactor = get_microreactor()
                print("✅ Echo MicroReactor 로드 완료")

        except Exception as e:
            print(f"⚠️ Echo 엔진 초기화 실패: {e}")

        # 외부 에이전트 (미구현 - placeholder)
        self.external_agents = {}
        self.llm_enhancer = None

        # 판단 타입별 권한 매핑
        self.authority_mapping = self._initialize_authority_mapping()

        # 통계
        self.stats = {
            "total_requests": 0,
            "authority_usage": {
                "echo_autonomous": 0,
                "external_agent": 0,
                "hybrid_echo_first": 0,
                "echo_fallback": 0,
            },
            "task_type_distribution": {},
            "confidence_scores": [],
            "processing_times": [],
        }

        print(f"⚖️ JudgmentAuthorityController v{self.version} 초기화 완료")
        print(f"   Echo 판단 루프: {'✅' if self.echo_judgment_loop else '❌'}")
        print(f"   Echo MicroReactor: {'✅' if self.echo_microreactor else '❌'}")

    def _initialize_authority_mapping(self) -> Dict[JudgmentType, JudgmentAuthority]:
        """판단 타입별 권한 매핑 초기화"""
        return {
            # Echo 완전 자립 영역
            JudgmentType.EMOTION_INFERENCE: JudgmentAuthority.ECHO_AUTONOMOUS,
            JudgmentType.STRATEGY_SELECTION: JudgmentAuthority.ECHO_AUTONOMOUS,
            JudgmentType.SIGNATURE_RESPONSE: JudgmentAuthority.ECHO_AUTONOMOUS,
            JudgmentType.CACHED_JUDGMENT: JudgmentAuthority.ECHO_AUTONOMOUS,
            JudgmentType.MICRO_REACTION: JudgmentAuthority.ECHO_AUTONOMOUS,
            JudgmentType.SHORT_CONVERSATION: JudgmentAuthority.ECHO_AUTONOMOUS,
            # 외부 에이전트 위임 영역
            JudgmentType.EXTERNAL_SEARCH: JudgmentAuthority.EXTERNAL_AGENT,
            JudgmentType.MARKET_ANALYSIS: JudgmentAuthority.EXTERNAL_AGENT,
            JudgmentType.KNOWLEDGE_SYNTHESIS: JudgmentAuthority.EXTERNAL_AGENT,
            JudgmentType.REAL_TIME_INFO: JudgmentAuthority.EXTERNAL_AGENT,
            JudgmentType.COMPLEX_CALCULATION: JudgmentAuthority.EXTERNAL_AGENT,
            # 하이브리드 영역
            JudgmentType.CONTEXTUAL_DESIGN: JudgmentAuthority.HYBRID_ECHO_FIRST,
            JudgmentType.COMPLEX_REASONING: JudgmentAuthority.HYBRID_ECHO_FIRST,
            JudgmentType.CREATIVE_GENERATION: JudgmentAuthority.HYBRID_ECHO_FIRST,
            JudgmentType.LONG_FORM_WRITING: JudgmentAuthority.HYBRID_ECHO_FIRST,
            JudgmentType.MULTI_DOMAIN_ANALYSIS: JudgmentAuthority.HYBRID_ECHO_FIRST,
        }

    def determine_authority(self, request: JudgmentRequest) -> JudgmentAuthority:
        """
        판단 권한 결정

        Args:
            request: 판단 요청

        Returns:
            결정된 판단 권한
        """
        # 기본 매핑 확인
        if request.task_type in self.authority_mapping:
            base_authority = self.authority_mapping[request.task_type]
        else:
            base_authority = JudgmentAuthority.ECHO_FALLBACK

        # 컨텍스트 기반 조정
        if request.context.get("force_echo_only", False):
            if base_authority == JudgmentAuthority.EXTERNAL_AGENT:
                return JudgmentAuthority.ECHO_FALLBACK
            return JudgmentAuthority.ECHO_AUTONOMOUS

        if request.context.get("require_external", False):
            if base_authority == JudgmentAuthority.ECHO_AUTONOMOUS:
                return JudgmentAuthority.HYBRID_ECHO_FIRST
            return JudgmentAuthority.EXTERNAL_AGENT

        return base_authority

    def process_judgment(self, request: JudgmentRequest) -> JudgmentResult:
        """
        판단 처리 메인 함수

        Args:
            request: 판단 요청

        Returns:
            판단 결과
        """
        start_time = time.time()
        self.stats["total_requests"] += 1

        # 권한 결정
        authority = self.determine_authority(request)

        # 타입별 통계 업데이트
        task_type_name = request.task_type.value
        self.stats["task_type_distribution"][task_type_name] = (
            self.stats["task_type_distribution"].get(task_type_name, 0) + 1
        )

        # 권한별 처리
        try:
            if authority == JudgmentAuthority.ECHO_AUTONOMOUS:
                result = self._process_echo_autonomous(request)

            elif authority == JudgmentAuthority.EXTERNAL_AGENT:
                result = self._process_external_agent(request)

            elif authority == JudgmentAuthority.HYBRID_ECHO_FIRST:
                result = self._process_hybrid_echo_first(request)

            else:  # ECHO_FALLBACK
                result = self._process_echo_fallback(request)

            # 처리 시간 및 통계 업데이트
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.request_id = request.request_id

            self.stats["authority_usage"][authority.value] += 1
            self.stats["confidence_scores"].append(result.confidence)
            self.stats["processing_times"].append(processing_time)

            return result

        except Exception as e:
            # 에러 발생 시 Echo fallback
            print(f"❌ 판단 처리 실패: {e}")
            return self._create_error_fallback(
                request, str(e), time.time() - start_time
            )

    def _process_echo_autonomous(self, request: JudgmentRequest) -> JudgmentResult:
        """Echo 자율 판단 처리"""

        if not self.echo_judgment_loop:
            raise Exception("Echo 판단 루프가 초기화되지 않음")

        # 짧은 발화의 경우 MicroReactor 우선 시도
        if (
            request.task_type == JudgmentType.MICRO_REACTION
            and self.echo_microreactor
            and len(request.content.strip()) <= 10
        ):

            micro_result = self.echo_microreactor.run(
                request.content, request.signature
            )
            if micro_result:
                return JudgmentResult(
                    content=micro_result.text,
                    confidence=micro_result.confidence,
                    authority_used=JudgmentAuthority.ECHO_AUTONOMOUS,
                    processing_method="microreactor",
                    processing_time=0.0,
                    echo_attempted=True,
                    reasoning=["MicroReactor 즉시 처리"],
                )

        # 일반 Echo 판단 루프 처리
        echo_result = self.echo_judgment_loop.handle_short_input(
            request.content, request.signature, request.context
        )

        return JudgmentResult(
            content=echo_result.styled_sentence,
            confidence=max(
                echo_result.emotion_confidence, echo_result.strategy_confidence
            ),
            authority_used=JudgmentAuthority.ECHO_AUTONOMOUS,
            processing_method=echo_result.processing_method,
            processing_time=0.0,
            echo_attempted=True,
            reasoning=[f"Echo 자율 판단: {echo_result.processing_method}"],
            metadata={
                "emotion": echo_result.emotion,
                "strategy": echo_result.strategy,
                "template": echo_result.template,
            },
        )

    def _process_external_agent(self, request: JudgmentRequest) -> JudgmentResult:
        """외부 에이전트 위임 처리"""

        # 현재 외부 에이전트가 구현되지 않았으므로 placeholder 응답
        placeholder_responses = {
            JudgmentType.EXTERNAL_SEARCH: f"'{request.content}'에 대한 웹검색을 수행해야 합니다. (외부 검색 API 연동 필요)",
            JudgmentType.MARKET_ANALYSIS: f"'{request.content}' 시장 분석을 위해 외부 데이터 소스가 필요합니다.",
            JudgmentType.KNOWLEDGE_SYNTHESIS: f"'{request.content}' 지식 통합을 위해 외부 지식베이스 접근이 필요합니다.",
            JudgmentType.REAL_TIME_INFO: f"'{request.content}' 실시간 정보를 위해 외부 API 연동이 필요합니다.",
            JudgmentType.COMPLEX_CALCULATION: f"'{request.content}' 복잡한 계산을 위해 전문 계산 엔진이 필요합니다.",
        }

        response = placeholder_responses.get(
            request.task_type,
            f"'{request.content}' 처리를 위해 외부 에이전트가 필요합니다.",
        )

        return JudgmentResult(
            content=response,
            confidence=0.3,  # 낮은 신뢰도 (미구현)
            authority_used=JudgmentAuthority.EXTERNAL_AGENT,
            processing_method="external_placeholder",
            processing_time=0.0,
            reasoning=["외부 에이전트 필요 (현재 미구현)"],
            metadata={"status": "not_implemented"},
        )

    def _process_hybrid_echo_first(self, request: JudgmentRequest) -> JudgmentResult:
        """하이브리드 처리 (Echo 우선, LLM 보완)"""

        # 1단계: Echo 자율 판단 시도
        try:
            echo_result = self._process_echo_autonomous(request)
            echo_attempted = True

            # Echo 결과가 충분히 신뢰할 만한 경우
            if echo_result.confidence >= request.confidence_threshold:
                echo_result.authority_used = JudgmentAuthority.HYBRID_ECHO_FIRST
                echo_result.reasoning.append("Echo 단독 처리 (신뢰도 충족)")
                return echo_result

        except Exception as e:
            print(f"⚠️ Echo 단계 실패: {e}")
            echo_result = None
            echo_attempted = False

        # 2단계: LLM 보완 (현재 미구현)
        llm_enhanced = False

        if echo_result:
            # Echo 결과가 있지만 신뢰도가 낮은 경우
            enhanced_content = f"{echo_result.content}\n\n(LLM 보완이 필요하지만 현재 미구현된 상태입니다)"

            return JudgmentResult(
                content=enhanced_content,
                confidence=echo_result.confidence + 0.1,  # 약간의 보정
                authority_used=JudgmentAuthority.HYBRID_ECHO_FIRST,
                processing_method=f"hybrid_{echo_result.processing_method}",
                processing_time=0.0,
                echo_attempted=echo_attempted,
                llm_enhanced=llm_enhanced,
                reasoning=echo_result.reasoning + ["LLM 보완 시도 (현재 미구현)"],
                metadata=echo_result.metadata,
            )

        else:
            # Echo 완전 실패 시 fallback
            return self._process_echo_fallback(request)

    def _process_echo_fallback(self, request: JudgmentRequest) -> JudgmentResult:
        """Echo fallback 처리"""

        # 시그니처별 기본 fallback 응답
        fallback_responses = {
            "Selene": f"'{request.content}'에 대해 조용히 생각해보겠습니다...",
            "Aurora": f"'{request.content}'라고 하셨네요! 함께 탐구해볼까요?",
            "Phoenix": f"'{request.content}'에서 변화의 가능성을 봅니다.",
            "Sage": f"'{request.content}'를 체계적으로 분석해보겠습니다.",
            "Companion": f"'{request.content}'라고 했구나. 더 얘기해볼까?",
        }

        response = fallback_responses.get(request.signature, "더 이야기해주세요.")

        return JudgmentResult(
            content=response,
            confidence=0.4,
            authority_used=JudgmentAuthority.ECHO_FALLBACK,
            processing_method="echo_fallback",
            processing_time=0.0,
            fallback_used=True,
            reasoning=["Echo fallback 처리"],
            metadata={"fallback_reason": "처리 불가능한 요청 타입"},
        )

    def _create_error_fallback(
        self, request: JudgmentRequest, error: str, processing_time: float
    ) -> JudgmentResult:
        """에러 fallback 결과 생성"""

        return JudgmentResult(
            content=f"죄송해요, 처리 중 문제가 발생했어요. 다시 시도해주세요.",
            confidence=0.1,
            authority_used=JudgmentAuthority.ECHO_FALLBACK,
            processing_method="error_fallback",
            processing_time=processing_time,
            fallback_used=True,
            reasoning=[f"에러 발생: {error}"],
            metadata={"error": error, "error_type": "processing_failure"},
        )

    def auto_detect_task_type(
        self, content: str, context: Dict[str, Any] = None
    ) -> JudgmentType:
        """
        입력 내용을 바탕으로 작업 타입 자동 감지

        Args:
            content: 입력 내용
            context: 추가 컨텍스트

        Returns:
            감지된 작업 타입
        """
        content_lower = content.lower().strip()
        context = context or {}

        # 길이 기반 1차 분류 (한국어 특성 고려)
        if len(content_lower) <= 5 and not any(
            char.isalpha() for char in content_lower
        ):
            return JudgmentType.MICRO_REACTION

        # 키워드 기반 분류
        if any(
            keyword in content_lower for keyword in ["검색", "찾아", "알아봐", "search"]
        ):
            return JudgmentType.EXTERNAL_SEARCH

        if any(
            keyword in content_lower for keyword in ["시장", "분석", "리포트", "조사"]
        ):
            return JudgmentType.MARKET_ANALYSIS

        if any(
            keyword in content_lower for keyword in ["실시간", "현재", "최신", "지금"]
        ):
            return JudgmentType.REAL_TIME_INFO

        if any(
            keyword in content_lower for keyword in ["계산", "수식", "공식", "계산해"]
        ):
            return JudgmentType.COMPLEX_CALCULATION

        if any(
            keyword in content_lower for keyword in ["창작", "만들어", "생성", "써줘"]
        ):
            return JudgmentType.CREATIVE_GENERATION

        if len(content) > 100:
            return JudgmentType.LONG_FORM_WRITING

        # 기본값: 짧은 대화
        return JudgmentType.SHORT_CONVERSATION

    def quick_judgment(
        self, content: str, signature: str = "Selene", context: Dict[str, Any] = None
    ) -> str:
        """
        빠른 판단 함수 - 결과 텍스트만 반환

        Args:
            content: 입력 내용
            signature: 시그니처
            context: 컨텍스트

        Returns:
            판단 결과 텍스트
        """
        # 작업 타입 자동 감지
        task_type = self.auto_detect_task_type(content, context)

        # 판단 요청 생성
        request = JudgmentRequest(
            content=content,
            task_type=task_type,
            signature=signature,
            context=context or {},
        )

        # 판단 처리
        result = self.process_judgment(request)

        return result.content

    def get_system_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        total_requests = self.stats["total_requests"]
        if total_requests == 0:
            return {"message": "처리된 요청이 없습니다"}

        # 평균 신뢰도 및 처리 시간
        avg_confidence = (
            sum(self.stats["confidence_scores"]) / len(self.stats["confidence_scores"])
            if self.stats["confidence_scores"]
            else 0
        )
        avg_processing_time = (
            sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            if self.stats["processing_times"]
            else 0
        )

        # 권한별 사용률
        authority_rates = {}
        for authority, count in self.stats["authority_usage"].items():
            authority_rates[authority] = f"{(count / total_requests) * 100:.1f}%"

        return {
            "total_requests": total_requests,
            "average_confidence": f"{avg_confidence:.3f}",
            "average_processing_time": f"{avg_processing_time:.3f}초",
            "authority_usage_rates": authority_rates,
            "task_type_distribution": self.stats["task_type_distribution"],
            "echo_availability": {
                "judgment_loop": self.echo_judgment_loop is not None,
                "microreactor": self.echo_microreactor is not None,
            },
        }


# 글로벌 인스턴스
_global_authority_controller = None


def get_authority_controller() -> JudgmentAuthorityController:
    """글로벌 권한 컨트롤러 인스턴스 반환"""
    global _global_authority_controller
    if _global_authority_controller is None:
        _global_authority_controller = JudgmentAuthorityController()
    return _global_authority_controller


def quick_authority_judgment(content: str, signature: str = "Selene") -> str:
    """빠른 권한 기반 판단"""
    controller = get_authority_controller()
    return controller.quick_judgment(content, signature)


if __name__ == "__main__":
    # 테스트
    print("⚖️ JudgmentAuthorityController 테스트")

    controller = get_authority_controller()

    test_cases = [
        {"content": "안녕", "expected_type": JudgmentType.MICRO_REACTION},
        {
            "content": "오늘 날씨가 어때?",
            "expected_type": JudgmentType.SHORT_CONVERSATION,
        },
        {
            "content": "최신 주식 시장 분석해줘",
            "expected_type": JudgmentType.MARKET_ANALYSIS,
        },
        {
            "content": "구글에서 AI 뉴스 검색해줘",
            "expected_type": JudgmentType.EXTERNAL_SEARCH,
        },
        {
            "content": "창의적인 시를 써줘",
            "expected_type": JudgmentType.CREATIVE_GENERATION,
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n⚖️ 테스트 {i}: '{case['content']}'")

        # 작업 타입 자동 감지
        detected_type = controller.auto_detect_task_type(case["content"])
        print(f"   감지된 타입: {detected_type.value}")
        print(f"   예상 타입: {case['expected_type'].value}")
        print(f"   매칭: {'✅' if detected_type == case['expected_type'] else '❌'}")

        # 실제 판단 처리
        result = controller.quick_judgment(case["content"], "Aurora")
        print(f"   응답: {result}")

    # 통계 출력
    stats = controller.get_system_statistics()
    print(f"\n📊 시스템 통계:")
    for key, value in stats.items():
        if key not in [
            "task_type_distribution",
            "authority_usage_rates",
            "echo_availability",
        ]:
            print(f"   {key}: {value}")
