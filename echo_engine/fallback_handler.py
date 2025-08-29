"""
🔄 Echo Fallback Handler
로컬 파싱 실패 시 외부 LLM이나 고급 분석을 호출하되,
Echo의 존재적 판단은 유지하는 신중한 fallback 시스템
"""

import json
import os
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

# 외부 LLM API 연동 시뮬레이션 (실제로는 openai, anthropic 등 사용)
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class EchoFallbackHandler:
    """
    Echo 시스템의 신중한 fallback 처리기
    '필요할 때만, 최소한으로, 존재를 유지하며' 외부 도움을 요청
    """

    def __init__(self, config_path: str = "config/fallback_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Fallback 전략 설정
        self.fallback_strategies = {
            "openai_api": {
                "enabled": OPENAI_AVAILABLE and bool(self.config.get("openai_api_key")),
                "priority": 1,
                "timeout": 15,
            },
            "llm_api": {"enabled": True, "priority": 2, "timeout": 10},
            "web_search": {"enabled": True, "priority": 3, "timeout": 15},
            "vector_search": {"enabled": True, "priority": 4, "timeout": 5},
            "template_matching": {"enabled": True, "priority": 5, "timeout": 2},
        }

        # 사용 통계
        self.usage_stats = {
            "total_fallback_requests": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "strategy_usage": {},
            "average_response_time": 0.0,
            "last_used": None,
        }

        # Echo의 자율성 보호 설정
        self.autonomy_protection = {
            "max_daily_fallbacks": 100,
            "confidence_boost_limit": 0.15,  # 외부 결과로 인한 신뢰도 상승 제한
            "echo_interpretation_required": True,  # Echo의 재해석 필수
            "preserve_signature_logic": True,  # 시그니처 결정은 Echo가 담당
        }

        self.logger = logging.getLogger(__name__)

    def handle_fallback(
        self,
        original_text: str,
        local_result: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Fallback 처리 메인 함수
        여러 전략을 시도하되 Echo의 존재적 판단을 유지
        """
        print(f"🔄 Echo Fallback 시작: '{original_text[:40]}...'")

        self.usage_stats["total_fallback_requests"] += 1
        start_time = time.time()

        # 1단계: 일일 사용 한도 확인
        if not self._check_daily_limit():
            print("   ⚠️  일일 Fallback 한도 초과, 로컬 결과 유지")
            return self._create_fallback_result(local_result, "daily_limit_exceeded")

        # 2단계: 최적 전략 선택
        strategy = self._select_fallback_strategy(original_text, local_result)
        print(f"   🎯 선택된 전략: {strategy}")

        # 3단계: 전략별 실행
        try:
            external_result = self._execute_fallback_strategy(
                strategy, original_text, local_result, context
            )

            # 4단계: Echo의 재해석 (중요!)
            echo_interpreted_result = self._echo_reinterpret_external_result(
                external_result, local_result, original_text
            )

            # 5단계: 최종 결과 구성
            final_result = self._create_fallback_result(
                echo_interpreted_result, strategy, external_result
            )

            self.usage_stats["successful_fallbacks"] += 1
            print(f"   ✅ Fallback 성공: {strategy} → {final_result['confidence']:.2f}")

        except Exception as e:
            print(f"   ❌ Fallback 실패: {e}")
            final_result = self._create_fallback_result(local_result, "fallback_failed")
            self.usage_stats["failed_fallbacks"] += 1

        # 통계 업데이트
        processing_time = time.time() - start_time
        self._update_usage_stats(strategy, processing_time)

        return final_result

    def _select_fallback_strategy(self, text: str, local_result: Dict[str, Any]) -> str:
        """상황에 맞는 최적 fallback 전략 선택"""
        text_length = len(text)
        complexity = local_result.get("complexity_score", 0)
        local_confidence = local_result.get("confidence", 0)

        # 전략 선택 로직 (우선순위 순서대로)
        # 1순위: OpenAI API (활성화되어 있으면 최우선)
        if self.fallback_strategies["openai_api"]["enabled"]:
            return "openai_api"

        # 2순위: 긴 복잡한 텍스트는 LLM이 적합
        elif text_length > 100 and complexity > 7:
            if self.fallback_strategies["llm_api"]["enabled"]:
                return "llm_api"

        # 3순위: 신뢰도가 매우 낮으면 벡터 검색 시도
        elif local_confidence < 0.3:
            if self.fallback_strategies["vector_search"]["enabled"]:
                return "vector_search"

        # 4순위: 기본값은 LLM API
        elif self.fallback_strategies["llm_api"]["enabled"]:
            return "llm_api"

        # 5순위: 짧은 질문은 템플릿 매칭
        elif "?" in text and len(text) < 50:
            if self.fallback_strategies["template_matching"]["enabled"]:
                return "template_matching"

        # 모든 전략이 비활성화된 경우
        return "template_matching"  # 최후의 수단

    def _execute_fallback_strategy(
        self,
        strategy: str,
        text: str,
        local_result: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """선택된 전략 실행"""
        strategy_config = self.fallback_strategies.get(strategy, {})
        timeout = strategy_config.get("timeout", 10)

        if strategy == "openai_api":
            return self._actual_openai_call(text, local_result)
        elif strategy == "llm_api":
            return self._llm_api_fallback(text, local_result, timeout)
        elif strategy == "web_search":
            return self._web_search_fallback(text, local_result, timeout)
        elif strategy == "vector_search":
            return self._vector_search_fallback(text, local_result, timeout)
        elif strategy == "template_matching":
            return self._template_matching_fallback(text, local_result, timeout)
        else:
            raise ValueError(f"Unknown fallback strategy: {strategy}")

    def _llm_api_fallback(
        self, text: str, local_result: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """LLM API를 통한 fallback (현재는 Mock)"""
        print("   🤖 LLM API Fallback 호출")

        if OPENAI_AVAILABLE and self.config.get("openai_api_key"):
            # 실제 OpenAI API 호출 (비용 주의!)
            return self._actual_openai_call(text, local_result)
        else:
            # Mock LLM 응답
            return self._mock_llm_api_call(text, local_result)

    def _actual_openai_call(
        self, text: str, local_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실제 OpenAI API 호출"""
        print("   🔥 OpenAI GPT-3.5 실제 호출")

        prompt = f"""
        다음 텍스트를 분석하고 Echo 시스템에서 사용할 수 있는 구조화된 결과를 JSON 형태로 반환해주세요.

        텍스트: "{text}"

        분석 항목:
        1. intent (judgment/information/assistance/conversation 중 하나)
        2. topic (주요 주제)
        3. emotion (감정 상태)
        4. keywords (핵심 키워드 5개 이하)
        5. confidence (0.0-1.0 사이 신뢰도)

        JSON 형태로만 응답:
        """

        try:
            client = openai.OpenAI(api_key=self.config.get("openai_api_key"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )

            result_text = response.choices[0].message.content.strip()

            # JSON 파싱 시도
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # JSON이 아닐 경우 기본 구조로 변환
                result = {
                    "intent": "conversation",
                    "topic": "general",
                    "emotion": "neutral",
                    "keywords": text.split()[:5],
                    "confidence": 0.7,
                    "raw_response": result_text,
                }

            result["api_source"] = "openai_gpt3.5"
            result["external_reasoning"] = "OpenAI GPT-3.5를 통한 분석"

            return result

        except Exception as e:
            print(f"   ⚠️  OpenAI API 호출 실패: {e}")
            return self._mock_llm_api_call(text, local_result)

    def _mock_llm_api_call(
        self, text: str, local_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock LLM API 호출 (실제 API 비용 절약용)"""
        time.sleep(0.5)  # API 지연 시뮬레이션

        # 텍스트 분석을 통한 고도화된 Mock 응답
        text_lower = text.lower()

        # Intent 고급 추론
        intent_scores = {}
        if any(
            word in text_lower
            for word in ["판단", "평가", "분석", "어떻게 생각", "어떤지"]
        ):
            intent_scores["judgment"] = 0.9
        if any(word in text_lower for word in ["알려", "설명", "정보", "뭐", "무엇"]):
            intent_scores["information"] = 0.8
        if any(word in text_lower for word in ["도움", "지원", "추천", "해줘"]):
            intent_scores["assistance"] = 0.85

        best_intent = (
            max(intent_scores.keys(), key=lambda x: intent_scores[x])
            if intent_scores
            else "conversation"
        )

        # 주제 고급 추론
        topic_mapping = {
            "노인|어르신|돌봄|요양": "노인복지정책",
            "ai|인공지능|알고리즘|편향": "ai_거버넌스",
            "기후|환경|탄소|온실가스": "환경기후정책",
            "지역|공동체|마을|주민": "지역사회혁신",
            "정책|제도|법|규제": "공공정책",
            "교육|학습|가르치|배우": "교육정책",
        }

        detected_topic = "일반_상담"
        for pattern, topic in topic_mapping.items():
            if any(keyword in text_lower for keyword in pattern.split("|")):
                detected_topic = topic
                break

        # 감정 상태 고급 분석
        emotion_patterns = {
            "urgent": ["빨리", "시급", "당장", "즉시"],
            "concerned": ["걱정", "문제", "힘든", "어려운"],
            "curious": ["궁금", "알고 싶", "어떻게"],
            "positive": ["좋", "훌륭", "감사", "기쁜"],
        }

        detected_emotion = "neutral"
        for emotion, patterns in emotion_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                detected_emotion = emotion
                break

        # 엔티티 추출
        entities = {}
        import re

        locations = re.findall(
            r"(서울|부산|대구|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주|금정구|해운대|강남|송파)",
            text,
        )
        if locations:
            entities["locations"] = list(set(locations))

        numbers = re.findall(r"\d+", text)
        if numbers:
            entities["numbers"] = numbers

        return {
            "intent": best_intent,
            "topic": detected_topic,
            "emotion": detected_emotion,
            "entities": entities,
            "keywords": [word for word in text_lower.split() if len(word) > 2][:10],
            "confidence": 0.87,
            "external_reasoning": f"고급 언어모델 분석: '{text[:30]}...'는 {best_intent} 의도의 {detected_topic} 관련 {detected_emotion} 감정 표현",
            "processing_quality": "high",
            "api_source": "mock_llm",
        }

    def _actual_openai_call(
        self, text: str, local_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실제 OpenAI API 호출 (비용 발생 주의!)"""
        # 실제 구현 시에만 활성화
        prompt = f"""
        다음 텍스트를 분석하여 JSON 형태로 응답해주세요:

        텍스트: "{text}"

        분석 항목:
        1. intent (judgment/information/assistance/conversation 중 하나)
        2. topic (주요 주제)
        3. emotion (감정 상태)
        4. keywords (핵심 키워드 5개 이하)
        5. confidence (0.0-1.0 사이 신뢰도)

        JSON 형태로만 응답:
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            result["api_source"] = "openai_gpt3.5"
            result["external_reasoning"] = "OpenAI GPT-3.5를 통한 분석"

            return result

        except Exception as e:
            print(f"   ⚠️  OpenAI API 호출 실패: {e}")
            return self._mock_llm_api_call(text, local_result)

    def _web_search_fallback(
        self, text: str, local_result: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """웹 검색 기반 fallback (Mock)"""
        print("   🌐 웹 검색 Fallback")
        time.sleep(1.0)  # 웹 검색 지연 시뮬레이션

        # Mock 웹 검색 결과
        search_terms = [word for word in text.split() if len(word) > 2][:3]

        return {
            "intent": local_result.get("intent", "information"),
            "topic": f"웹검색_{search_terms[0] if search_terms else 'general'}",
            "emotion": "curious",
            "keywords": search_terms,
            "confidence": 0.75,
            "external_reasoning": f"웹 검색 기반 분석: {search_terms} 키워드 관련 정보",
            "search_terms": search_terms,
            "api_source": "web_search",
        }

    def _vector_search_fallback(
        self, text: str, local_result: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """벡터 검색 기반 fallback"""
        print("   🧭 벡터 검색 Fallback")

        try:
            # EchoVectorCapsule과 연동 시도
            from .vector_search_engine import search_capsules

            search_results = search_capsules(text, "Echo-Aurora", top_k=3)

            if search_results:
                # 최고 유사도 결과 기반으로 intent/topic 추론
                top_result = search_results[0]
                metadata = top_result["metadata"]

                return {
                    "intent": "information",  # 벡터 검색은 주로 정보 요청
                    "topic": metadata.get("topic", "unknown"),
                    "emotion": "curious",
                    "keywords": metadata.get("tags", [])[:5],
                    "confidence": min(0.85, top_result["similarity"] + 0.1),
                    "external_reasoning": f"벡터 검색 매칭: {metadata.get('capsule_id')} 캡슐과 유사도 {top_result['similarity']:.2f}",
                    "matched_capsule": metadata.get("capsule_id"),
                    "api_source": "vector_search",
                }
            else:
                raise ValueError("벡터 검색 결과 없음")

        except Exception as e:
            print(f"   ⚠️  벡터 검색 실패: {e}")
            return self._template_matching_fallback(text, local_result, timeout)

    def _template_matching_fallback(
        self, text: str, local_result: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """템플릿 매칭 기반 fallback (최후의 수단)"""
        print("   📋 템플릿 매칭 Fallback")

        # 간단한 패턴 매칭
        patterns = {
            "인사": r"안녕|반가워|처음|만나서",
            "질문": r"\?|어떻게|왜|언제|뭐",
            "요청": r"해줘|부탁|도와줘|알려줘",
            "감사": r"고마워|감사|고맙|덕분",
        }

        import re

        matched_pattern = "일반대화"
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, text):
                matched_pattern = pattern_name
                break

        intent_mapping = {
            "인사": "conversation",
            "질문": "information",
            "요청": "assistance",
            "감사": "conversation",
            "일반대화": "conversation",
        }

        return {
            "intent": intent_mapping[matched_pattern],
            "topic": f"template_{matched_pattern}",
            "emotion": "neutral",
            "keywords": [matched_pattern],
            "confidence": 0.6,
            "external_reasoning": f"템플릿 매칭: {matched_pattern} 패턴 감지",
            "matched_template": matched_pattern,
            "api_source": "template_matching",
        }

    def _echo_reinterpret_external_result(
        self,
        external_result: Dict[str, Any],
        local_result: Dict[str, Any],
        original_text: str,
    ) -> Dict[str, Any]:
        """Echo의 존재적 재해석 (핵심!)"""
        print("   🌀 Echo 재해석 진행...")

        # Echo의 자율성 보호: 외부 결과를 참고하되 Echo의 논리로 재구성
        echo_interpreted = {
            "intent": external_result.get(
                "intent", local_result.get("intent", "unknown")
            ),
            "topic": external_result.get("topic", local_result.get("topic", "unknown")),
            "emotion": external_result.get(
                "emotion", local_result.get("emotion", "neutral")
            ),
            "keywords": list(
                set(
                    external_result.get("keywords", [])
                    + local_result.get("keywords", [])
                )
            )[:10],
            "entities": {
                **local_result.get("entities", {}),
                **external_result.get("entities", {}),
            },
        }

        # Echo의 신뢰도 로직 적용
        external_confidence = external_result.get("confidence", 0.5)
        local_confidence = local_result.get("confidence", 0.0)

        # Echo가 외부 결과를 얼마나 신뢰할지 결정
        echo_trust_factor = self._calculate_echo_trust_factor(
            external_result, local_result
        )

        # 신뢰도 융합 (Echo의 자율성 보호를 위해 제한적으로)
        base_confidence = max(local_confidence, 0.4)  # 최소 기준 확보
        external_boost = min(
            self.autonomy_protection["confidence_boost_limit"],
            (external_confidence - 0.5) * echo_trust_factor,
        )

        final_confidence = min(0.95, base_confidence + external_boost)
        echo_interpreted["confidence"] = final_confidence

        # Echo의 메타 인식 추가
        echo_interpreted["echo_meta_analysis"] = {
            "external_source_trusted": echo_trust_factor > 0.5,
            "echo_interpretation_applied": True,
            "confidence_adjustment": external_boost,
            "maintains_echo_autonomy": True,
            "reinterpretation_reason": self._get_reinterpretation_reason(
                external_result, local_result
            ),
        }

        return echo_interpreted

    def _calculate_echo_trust_factor(
        self, external: Dict[str, Any], local: Dict[str, Any]
    ) -> float:
        """Echo가 외부 결과를 얼마나 신뢰할지 계산"""
        factors = []

        # 외부 소스 신뢰도
        api_source = external.get("api_source", "unknown")
        source_trust = {
            "openai_gpt3.5": 0.8,
            "claude": 0.85,
            "mock_llm": 0.6,
            "vector_search": 0.9,  # 자체 데이터 기반이므로 높은 신뢰
            "web_search": 0.5,
            "template_matching": 0.4,
        }
        factors.append(source_trust.get(api_source, 0.5))

        # 로컬과 외부 결과의 일치도
        intent_match = 1.0 if external.get("intent") == local.get("intent") else 0.3
        factors.append(intent_match)

        # 외부 결과의 신뢰도
        external_confidence = external.get("confidence", 0.5)
        factors.append(min(1.0, external_confidence))

        # 가중 평균
        trust_factor = sum(factors) / len(factors)

        return trust_factor

    def _get_reinterpretation_reason(
        self, external: Dict[str, Any], local: Dict[str, Any]
    ) -> str:
        """재해석 이유 설명"""
        api_source = external.get("api_source", "unknown")

        if api_source == "vector_search":
            return "자체 캡슐 데이터와의 매칭을 통한 신뢰성 높은 재해석"
        elif api_source in ["openai_gpt3.5", "claude"]:
            return "외부 언어모델 분석을 Echo 논리로 재구성"
        elif api_source == "web_search":
            return "웹 검색 정보를 Echo의 판단 기준으로 필터링"
        else:
            return "외부 분석 결과를 Echo의 존재적 관점에서 재해석"

    def _create_fallback_result(
        self,
        interpreted_result: Dict[str, Any],
        strategy: str,
        external_raw: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """최종 fallback 결과 구성"""
        result = {
            **interpreted_result,
            "fallback_used": True,
            "fallback_strategy": strategy,
            "fallback_timestamp": datetime.now().isoformat(),
            "echo_autonomy_preserved": True,
        }

        # 외부 데이터는 메타 정보로만 보존
        if external_raw:
            result["external_analysis"] = {
                "source": external_raw.get("api_source", "unknown"),
                "confidence": external_raw.get("confidence", 0.0),
                "reasoning": external_raw.get("external_reasoning", ""),
            }

        return result

    def _check_daily_limit(self) -> bool:
        """일일 fallback 사용 한도 확인"""
        # 간단한 구현 - 실제로는 날짜별 사용량 추적 필요
        max_daily = self.autonomy_protection["max_daily_fallbacks"]
        current_usage = self.usage_stats["total_fallback_requests"]

        return current_usage < max_daily

    def _update_usage_stats(self, strategy: str, processing_time: float):
        """사용 통계 업데이트"""
        self.usage_stats["strategy_usage"][strategy] = (
            self.usage_stats["strategy_usage"].get(strategy, 0) + 1
        )

        # 평균 응답 시간 계산
        current_avg = self.usage_stats["average_response_time"]
        total_requests = self.usage_stats["total_fallback_requests"]

        new_avg = (
            (current_avg * (total_requests - 1)) + processing_time
        ) / total_requests
        self.usage_stats["average_response_time"] = new_avg

        self.usage_stats["last_used"] = datetime.now().isoformat()

    def _load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        # 기본 설정 (실제로는 YAML 파일에서 로드)
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),  # 환경변수에서 로드
            "claude_api_key": None,
            "enable_web_search": True,
            "fallback_timeout": 15,
            "max_retries": 2,
            "echo_autonomy_mode": "strict",  # strict, balanced, permissive
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """사용 통계 반환"""
        stats = self.usage_stats.copy()

        # 성공률 계산
        total = stats["total_fallback_requests"]
        if total > 0:
            stats["success_rate"] = (
                f"{(stats['successful_fallbacks'] / total) * 100:.1f}%"
            )
            stats["echo_autonomy_rate"] = (
                f"{((total - stats['fallback_used']) / total) * 100:.1f}%"
                if "fallback_used" in stats
                else "100.0%"
            )

        return stats

    def reset_daily_stats(self):
        """일일 통계 리셋 (스케줄러에서 호출)"""
        self.usage_stats = {
            "total_fallback_requests": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "strategy_usage": {},
            "average_response_time": 0.0,
            "last_used": None,
        }
        print("📊 Fallback 일일 통계가 리셋되었습니다.")


# 전역 fallback 핸들러
fallback_handler = EchoFallbackHandler()


# 편의 함수
def handle_fallback(
    text: str, local_result: Dict[str, Any], context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Fallback 처리 단축 함수"""
    return fallback_handler.handle_fallback(text, local_result, context)


def get_fallback_stats() -> Dict[str, Any]:
    """Fallback 통계 단축 함수"""
    return fallback_handler.get_usage_stats()


# CLI 테스트
def main():
    print("🔄 Echo Fallback Handler 테스트")
    print("=" * 50)

    # Mock 로컬 파싱 결과들
    test_cases = [
        {
            "text": "복잡한 정책 상황에서 다양한 이해관계자들의 상충하는 요구사항을 조율하면서도 공정성을 보장할 수 있는 체계적인 접근 방법론을 제시해주세요",
            "local_result": {
                "intent": "unknown",
                "topic": "unknown",
                "confidence": 0.2,
                "complexity_score": 9.5,
            },
        },
        {
            "text": "AI 윤리가 중요한가요?",
            "local_result": {
                "intent": "information",
                "topic": "ai_윤리",
                "confidence": 0.5,
                "complexity_score": 2.0,
            },
        },
        {
            "text": "안녕하세요!",
            "local_result": {
                "intent": "conversation",
                "topic": "인사",
                "confidence": 0.9,
                "complexity_score": 1.0,
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*40}")
        print(f"테스트 {i}: {test_case['text']}")
        print(
            f"로컬 결과 - Intent: {test_case['local_result']['intent']}, Confidence: {test_case['local_result']['confidence']}"
        )
        print("-" * 40)

        result = handle_fallback(test_case["text"], test_case["local_result"])

        print(f"Fallback 결과:")
        print(f"  Strategy: {result.get('fallback_strategy')}")
        print(f"  Intent: {result.get('intent')}")
        print(f"  Topic: {result.get('topic')}")
        print(f"  Final Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Echo Autonomy: {result.get('echo_autonomy_preserved', False)}")

        if result.get("echo_meta_analysis"):
            meta = result["echo_meta_analysis"]
            print(f"  Echo Meta: {meta.get('reinterpretation_reason', 'N/A')}")

    print(f"\n{'='*40}")
    print("📊 Fallback 사용 통계:")
    stats = get_fallback_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Echo Fallback Handler 테스트 완료!")


if __name__ == "__main__":
    main()
