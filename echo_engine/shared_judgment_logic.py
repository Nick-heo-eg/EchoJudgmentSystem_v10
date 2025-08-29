#!/usr/bin/env python3
"""
🔗 EchoJudgmentSystem v10.5 - Shared Judgment Logic
공통 판단 로직 모듈 - LLM-Free와 Claude 판단 흐름에서 공통으로 사용

이 모듈은 다음 로직들을 범용화합니다:
- 감정 추론 (emotion inference)
- 전략 추천 (strategy recommendation)
- 판단 라벨링 (judgment labeling)
- 신뢰도 계산 (confidence calculation)
- 추론 과정 기록 (reasoning trace building)
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os

# LLM-Free 시스템 컴포넌트 임포트
try:
    from .llm_free.pattern_based_reasoner import PatternBasedReasoner
    from .llm_free.llm_free_judge import FallbackJudge
except ImportError:
    PatternBasedReasoner = None
    FallbackJudge = None

# 통합 설정 시스템
try:
    import sys

    # sys.path 수정 불필요 (portable_paths 사용)
    from config_loader import get_config, get_config_loader

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class JudgmentMode(Enum):
    """판단 모드"""

    LLM_FREE = "llm_free"
    CLAUDE = "claude"
    HYBRID = "hybrid"
    FIST_ENHANCED = "fist_enhanced"


class ProcessingStage(Enum):
    """처리 단계"""

    INPUT_PREPROCESSING = "input_preprocessing"
    EMOTION_INFERENCE = "emotion_inference"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"
    CONTEXT_ANALYSIS = "context_analysis"
    CONFIDENCE_CALCULATION = "confidence_calculation"
    JUDGMENT_GENERATION = "judgment_generation"
    RESPONSE_FORMATTING = "response_formatting"


@dataclass
class SharedJudgmentResult:
    """공통 판단 결과 데이터 클래스"""

    # 핵심 결과
    judgment: str
    confidence: float
    emotion_detected: str
    strategy_suggested: str

    # 추론 과정
    reasoning_trace: List[str] = field(default_factory=list)
    processing_stages: Dict[str, Any] = field(default_factory=dict)

    # 성능 정보
    processing_time: float = 0.0
    stage_timings: Dict[str, float] = field(default_factory=dict)

    # 메타데이터
    judgment_mode: JudgmentMode = JudgmentMode.HYBRID
    fallback_used: bool = False
    error_occurred: bool = False
    error_message: Optional[str] = None

    # 추가 정보
    alternatives: List[str] = field(default_factory=list)
    context_detected: str = "general"
    keywords_extracted: List[str] = field(default_factory=list)
    patterns_matched: List[str] = field(default_factory=list)

    # 원본 데이터 (디버깅용)
    raw_emotion_analysis: Dict[str, Any] = field(default_factory=dict)
    raw_strategy_analysis: Dict[str, Any] = field(default_factory=dict)
    raw_context_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JudgmentRequest:
    """판단 요청 데이터 클래스"""

    text: str
    context: Optional[str] = None
    judgment_mode: JudgmentMode = JudgmentMode.HYBRID

    # 요청 설정
    include_emotion: bool = True
    include_strategy: bool = True
    include_context: bool = True
    include_alternatives: bool = False

    # 성능 설정
    timeout: Optional[float] = None
    max_reasoning_depth: int = 3

    # 메타데이터
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user_context: Dict[str, Any] = field(default_factory=dict)


class SharedJudgmentEngine:
    """공통 판단 엔진 - LLM-Free와 Claude 공통 로직 제공"""

    def __init__(self):
        self.reasoning_engine = None
        self.fallback_judge = None
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "stage_performance": {},
        }

        # 초기화
        self._initialize_components()

    def _initialize_components(self):
        """컴포넌트 초기화"""
        try:
            # LLM-Free 컴포넌트 초기화
            if PatternBasedReasoner and FallbackJudge:
                # 기본 규칙셋 로드
                ruleset = self._load_default_ruleset()
                self.reasoning_engine = PatternBasedReasoner(ruleset)
                self.fallback_judge = FallbackJudge()
                print("✅ LLM-Free 컴포넌트 초기화 완료")
            else:
                print("⚠️ LLM-Free 컴포넌트 불러오기 실패")

        except Exception as e:
            print(f"⚠️ 공통 판단 엔진 초기화 중 오류: {e}")

    def _load_default_ruleset(self) -> Dict[str, Any]:
        """기본 규칙셋 로드"""
        if CONFIG_AVAILABLE:
            try:
                # 통합 설정에서 LLM-Free 설정 가져오기
                emotion_patterns = get_config("llm_free.emotion_analysis.patterns", {})
                strategy_patterns = get_config(
                    "llm_free.strategy_analysis.patterns", {}
                )
                context_patterns = get_config("llm_free.context_analysis.patterns", {})

                if emotion_patterns:
                    return {
                        "emotion_patterns": emotion_patterns,
                        "strategy_patterns": strategy_patterns,
                        "context_patterns": context_patterns,
                    }
            except Exception as e:
                print(f"⚠️ 통합 설정에서 규칙셋 로드 실패: {e}")

        # 폴백 규칙셋
        return {
            "emotion_patterns": {
                "joy": ["기쁘", "행복", "좋", "최고", "성공", "축하", "만족", "즐거"],
                "sadness": [
                    "슬프",
                    "우울",
                    "힘들",
                    "속상",
                    "실망",
                    "포기",
                    "아쉽",
                    "안타까",
                ],
                "anger": ["화", "짜증", "분노", "열받", "억울", "불만", "불쾌", "갑갑"],
                "fear": [
                    "무서",
                    "걱정",
                    "불안",
                    "두려",
                    "긴장",
                    "스트레스",
                    "조심",
                    "위험",
                ],
                "surprise": [
                    "놀라",
                    "와우",
                    "헐",
                    "대박",
                    "깜짝",
                    "어머",
                    "신기",
                    "의외",
                ],
                "neutral": ["그냥", "보통", "평범", "일반", "그런대로", "괜찮"],
            },
            "strategy_patterns": {
                "logical": [
                    "분석",
                    "논리",
                    "이성",
                    "합리",
                    "데이터",
                    "객관적",
                    "체계",
                    "순서",
                ],
                "empathetic": [
                    "감정",
                    "공감",
                    "이해",
                    "마음",
                    "느낌",
                    "따뜻",
                    "위로",
                    "배려",
                ],
                "creative": [
                    "창의",
                    "새로운",
                    "혁신",
                    "아이디어",
                    "독창적",
                    "참신",
                    "상상",
                    "발상",
                ],
                "cautious": [
                    "신중",
                    "조심",
                    "안전",
                    "확실",
                    "검토",
                    "보수적",
                    "꼼꼼",
                    "세심",
                ],
                "balanced": [
                    "균형",
                    "중간",
                    "적당",
                    "조화",
                    "고려",
                    "종합",
                    "전체적",
                    "고루",
                ],
            },
            "context_patterns": {
                "work": [
                    "회의",
                    "업무",
                    "직장",
                    "동료",
                    "상사",
                    "프로젝트",
                    "업무",
                    "회사",
                ],
                "personal": [
                    "친구",
                    "가족",
                    "연인",
                    "개인",
                    "취미",
                    "여행",
                    "일상",
                    "생활",
                ],
                "academic": [
                    "공부",
                    "학교",
                    "시험",
                    "과제",
                    "교수",
                    "학습",
                    "연구",
                    "수업",
                ],
                "social": [
                    "모임",
                    "파티",
                    "사람들",
                    "관계",
                    "소통",
                    "네트워킹",
                    "만남",
                    "교류",
                ],
                "health": [
                    "건강",
                    "운동",
                    "병원",
                    "치료",
                    "몸",
                    "마음",
                    "정신",
                    "신체",
                ],
                "financial": [
                    "돈",
                    "경제",
                    "투자",
                    "저축",
                    "비용",
                    "가격",
                    "수입",
                    "지출",
                ],
            },
        }

    def process_judgment(self, request: JudgmentRequest) -> SharedJudgmentResult:
        """
        통합 판단 처리 - 핵심 공통 로직

        Args:
            request: 판단 요청

        Returns:
            SharedJudgmentResult: 판단 결과
        """
        start_time = time.time()
        self.performance_stats["total_requests"] += 1

        # 결과 객체 초기화
        result = SharedJudgmentResult(
            judgment="",
            confidence=0.0,
            emotion_detected="neutral",
            strategy_suggested="balanced",
            judgment_mode=request.judgment_mode,
        )

        try:
            # 1. 입력 전처리
            stage_start = time.time()
            preprocessed_input = self._preprocess_input(request.text, request.context)
            result.stage_timings["preprocessing"] = time.time() - stage_start
            result.reasoning_trace.append(
                f"입력 전처리 완료 (길이: {len(request.text)}자)"
            )

            # 2. 감정 추론
            if request.include_emotion:
                stage_start = time.time()
                emotion_result = self._analyze_emotion(preprocessed_input, request.text)
                result.emotion_detected = emotion_result["emotion"]
                result.raw_emotion_analysis = emotion_result
                result.stage_timings["emotion"] = time.time() - stage_start
                result.reasoning_trace.append(
                    f"감정 분석: {emotion_result['emotion']} (신뢰도: {emotion_result['confidence']:.3f})"
                )

            # 3. 전략 추천
            if request.include_strategy:
                stage_start = time.time()
                strategy_result = self._recommend_strategy(
                    preprocessed_input, request.text, result.emotion_detected
                )
                result.strategy_suggested = strategy_result["strategy"]
                result.raw_strategy_analysis = strategy_result
                result.stage_timings["strategy"] = time.time() - stage_start
                result.reasoning_trace.append(
                    f"전략 추천: {strategy_result['strategy']} (신뢰도: {strategy_result['confidence']:.3f})"
                )

            # 4. 문맥 분석
            if request.include_context:
                stage_start = time.time()
                context_result = self._analyze_context(
                    preprocessed_input, request.context or ""
                )
                result.context_detected = context_result["context"]
                result.raw_context_analysis = context_result
                result.stage_timings["context"] = time.time() - stage_start
                result.reasoning_trace.append(
                    f"문맥 분석: {context_result['context']} (신뢰도: {context_result['confidence']:.3f})"
                )

            # 5. 키워드 및 패턴 추출
            stage_start = time.time()
            result.keywords_extracted = self._extract_keywords(preprocessed_input)
            result.patterns_matched = self._match_patterns(preprocessed_input)
            result.stage_timings["extraction"] = time.time() - stage_start
            result.reasoning_trace.append(
                f"키워드 추출: {len(result.keywords_extracted)}개, 패턴: {len(result.patterns_matched)}개"
            )

            # 6. 신뢰도 계산
            stage_start = time.time()
            result.confidence = self._calculate_confidence(result)
            result.stage_timings["confidence"] = time.time() - stage_start
            result.reasoning_trace.append(f"신뢰도 계산: {result.confidence:.3f}")

            # 7. 판단 생성
            stage_start = time.time()
            result.judgment = self._generate_judgment(result, request)
            result.stage_timings["judgment"] = time.time() - stage_start
            result.reasoning_trace.append("최종 판단 생성 완료")

            # 8. 대안 제안 (옵션)
            if request.include_alternatives:
                stage_start = time.time()
                result.alternatives = self._generate_alternatives(result, request)
                result.stage_timings["alternatives"] = time.time() - stage_start
                result.reasoning_trace.append(
                    f"대안 생성: {len(result.alternatives)}개"
                )

            # 성공 통계 업데이트
            self.performance_stats["successful_requests"] += 1

        except Exception as e:
            # 오류 처리
            result.error_occurred = True
            result.error_message = str(e)
            result.judgment = f"판단 처리 중 오류가 발생했습니다: {str(e)[:100]}"
            result.confidence = 0.0
            result.reasoning_trace.append(f"오류 발생: {str(e)}")

            self.performance_stats["failed_requests"] += 1
            print(f"❌ 공통 판단 처리 오류: {e}")

        # 최종 처리 시간 계산
        result.processing_time = time.time() - start_time
        self._update_performance_stats(result.processing_time)

        return result

    def _preprocess_input(self, text: str, context: Optional[str] = None) -> str:
        """입력 전처리"""
        if not text:
            return ""

        # 기본 정리
        processed = text.strip()

        # 문맥 정보가 있다면 결합
        if context and context.strip():
            processed = f"{processed} [맥락: {context.strip()}]"

        return processed

    def _analyze_emotion(
        self, processed_text: str, original_text: str
    ) -> Dict[str, Any]:
        """감정 분석"""
        if self.reasoning_engine:
            try:
                emotion_result = self.reasoning_engine.analyze_sentiment(original_text)
                return {
                    "emotion": emotion_result["sentiment"],
                    "confidence": emotion_result["confidence"],
                    "details": emotion_result["details"],
                    "method": "pattern_based",
                }
            except Exception as e:
                print(f"⚠️ 패턴 기반 감정 분석 실패: {e}")

        # 폴백: 간단한 키워드 기반 감정 분석
        emotion_keywords = {
            "joy": ["기쁘", "행복", "좋", "최고", "성공"],
            "sadness": ["슬프", "우울", "힘들", "속상"],
            "anger": ["화", "짜증", "분노", "열받"],
            "fear": ["무서", "걱정", "불안", "두려"],
            "surprise": ["놀라", "와우", "대박"],
        }

        text_lower = original_text.lower()
        emotion_scores = {}

        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            top_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[top_emotion] / 3.0, 1.0)
        else:
            top_emotion = "neutral"
            confidence = 0.5

        return {
            "emotion": top_emotion,
            "confidence": confidence,
            "details": emotion_scores,
            "method": "keyword_fallback",
        }

    def _recommend_strategy(
        self, processed_text: str, original_text: str, emotion: str
    ) -> Dict[str, Any]:
        """전략 추천"""
        if self.reasoning_engine:
            try:
                strategy_result = self.reasoning_engine.suggest_strategy(original_text)
                return {
                    "strategy": strategy_result["strategy"],
                    "confidence": strategy_result["confidence"],
                    "details": strategy_result["details"],
                    "method": "pattern_based",
                }
            except Exception as e:
                print(f"⚠️ 패턴 기반 전략 추천 실패: {e}")

        # 폴백: 감정 기반 전략 매핑
        emotion_strategy_mapping = {
            "joy": "empathetic",  # 기쁨 → 공감적 접근
            "sadness": "empathetic",  # 슬픔 → 공감적 접근
            "anger": "cautious",  # 분노 → 신중한 접근
            "fear": "logical",  # 두려움 → 논리적 접근
            "surprise": "creative",  # 놀라움 → 창의적 접근
            "neutral": "balanced",  # 중성 → 균형적 접근
        }

        strategy = emotion_strategy_mapping.get(emotion, "balanced")
        confidence = 0.6 if emotion != "neutral" else 0.4

        return {
            "strategy": strategy,
            "confidence": confidence,
            "details": {strategy: confidence},
            "method": "emotion_mapping_fallback",
        }

    def _analyze_context(self, processed_text: str, context: str) -> Dict[str, Any]:
        """문맥 분석"""
        if self.reasoning_engine:
            try:
                context_result = self.reasoning_engine.detect_context(
                    processed_text, context
                )
                return {
                    "context": context_result["context"],
                    "confidence": context_result["confidence"],
                    "details": context_result["details"],
                    "method": "pattern_based",
                }
            except Exception as e:
                print(f"⚠️ 패턴 기반 문맥 분석 실패: {e}")

        # 폴백: 간단한 키워드 기반 문맥 분석
        context_keywords = {
            "work": ["회의", "업무", "직장", "동료", "상사"],
            "personal": ["친구", "가족", "연인", "개인"],
            "academic": ["공부", "학교", "시험", "과제"],
            "social": ["모임", "파티", "사람들", "관계"],
        }

        combined_text = f"{processed_text} {context}".lower()
        context_scores = {}

        for ctx_type, keywords in context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                context_scores[ctx_type] = score

        if context_scores:
            top_context = max(context_scores, key=context_scores.get)
            confidence = min(context_scores[top_context] / 2.0, 1.0)
        else:
            top_context = "general"
            confidence = 0.3

        return {
            "context": top_context,
            "confidence": confidence,
            "details": context_scores,
            "method": "keyword_fallback",
        }

    def _extract_keywords(self, processed_text: str) -> List[str]:
        """키워드 추출"""
        if not processed_text:
            return []

        # 단어 분리
        words = processed_text.split()

        # 불용어 제거
        stop_words = {
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "의",
            "에",
            "에서",
            "으로",
            "와",
            "과",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 1]

        # 중복 제거 및 상위 10개 반환
        return list(dict.fromkeys(keywords))[:10]

    def _match_patterns(self, processed_text: str) -> List[str]:
        """패턴 매칭"""
        patterns = []
        text_lower = processed_text.lower()

        # 질문 패턴
        if "?" in processed_text or any(
            word in text_lower for word in ["어떻게", "왜", "무엇", "언제"]
        ):
            patterns.append("question_pattern")

        # 감정 강화 패턴
        if any(word in text_lower for word in ["너무", "정말", "아주", "엄청"]):
            patterns.append("emotion_intensifier")

        # 부정 표현 패턴
        if any(word in text_lower for word in ["안", "못", "아니", "없"]):
            patterns.append("negative_expression")

        # 긍정 표현 패턴
        if any(word in text_lower for word in ["좋", "잘", "성공"]):
            patterns.append("positive_expression")

        # 요청 패턴
        if any(word in text_lower for word in ["도와주", "부탁", "조언"]):
            patterns.append("request_pattern")

        return patterns

    def _calculate_confidence(self, result: SharedJudgmentResult) -> float:
        """신뢰도 계산"""
        confidence_factors = []

        # 감정 분석 신뢰도
        if result.raw_emotion_analysis:
            confidence_factors.append(
                result.raw_emotion_analysis.get("confidence", 0.5)
            )

        # 전략 분석 신뢰도
        if result.raw_strategy_analysis:
            confidence_factors.append(
                result.raw_strategy_analysis.get("confidence", 0.5)
            )

        # 문맥 분석 신뢰도
        if result.raw_context_analysis:
            confidence_factors.append(
                result.raw_context_analysis.get("confidence", 0.3)
            )

        # 키워드 매칭 점수
        keyword_score = min(len(result.keywords_extracted) / 10.0, 1.0)
        confidence_factors.append(keyword_score)

        # 패턴 매칭 점수
        pattern_score = min(len(result.patterns_matched) / 5.0, 1.0)
        confidence_factors.append(pattern_score)

        # 평균 계산
        if confidence_factors:
            avg_confidence = sum(confidence_factors) / len(confidence_factors)
            return round(avg_confidence, 3)

        return 0.5

    def _generate_judgment(
        self, result: SharedJudgmentResult, request: JudgmentRequest
    ) -> str:
        """판단 생성"""
        emotion = result.emotion_detected
        strategy = result.strategy_suggested
        context = result.context_detected

        # 감정-전략-문맥 조합에 따른 판단 템플릿
        judgment_templates = {
            (
                "joy",
                "empathetic",
                "personal",
            ): "기쁜 마음이 느껴집니다. 이 긍정적인 감정을 주변 사람들과 나누시면 더욱 의미있을 것 같아요.",
            (
                "sadness",
                "empathetic",
                "personal",
            ): "힘든 시간을 보내고 계시는군요. 이런 감정도 자연스러운 것이니 너무 자책하지 마시고, 천천히 회복해나가시길 바랍니다.",
            (
                "anger",
                "cautious",
                "work",
            ): "화가 나는 상황이지만, 직장에서는 신중하게 접근하는 것이 좋겠습니다. 잠시 숨을 고르고 상황을 객관적으로 바라보세요.",
            (
                "fear",
                "logical",
                "work",
            ): "불안한 상황이지만 차근차근 분석해보시면 해결책이 보일 것입니다. 구체적인 계획을 세워보시는 것을 추천합니다.",
            (
                "surprise",
                "creative",
                "general",
            ): "예상치 못한 상황이네요. 이를 새로운 기회로 받아들이고 창의적으로 접근해보시는 것은 어떨까요?",
        }

        # 템플릿 매칭 시도
        template_key = (emotion, strategy, context)
        if template_key in judgment_templates:
            return judgment_templates[template_key]

        # 감정-전략 조합으로 재시도
        emotion_strategy_templates = {
            (
                "joy",
                "empathetic",
            ): "긍정적인 감정이 느껴집니다. 이 기쁨을 다른 사람들과 함께 나누시면 좋겠어요.",
            (
                "sadness",
                "empathetic",
            ): "어려운 상황이시군요. 지금의 감정을 있는 그대로 받아들이고, 천천히 극복해나가시길 응원합니다.",
            (
                "anger",
                "cautious",
            ): "화가 나시는 상황이지만, 냉정하게 한 번 더 생각해보시는 것이 좋겠습니다.",
            (
                "fear",
                "logical",
            ): "불안한 마음이 들지만, 논리적으로 상황을 분석해보시면 해결방안이 보일 것입니다.",
            (
                "surprise",
                "creative",
            ): "놀라운 상황이네요. 새로운 관점으로 접근해보시는 것은 어떨까요?",
            (
                "neutral",
                "balanced",
            ): "현재 상황을 균형있게 판단해보시는 것이 좋겠습니다.",
        }

        emotion_strategy_key = (emotion, strategy)
        if emotion_strategy_key in emotion_strategy_templates:
            return emotion_strategy_templates[emotion_strategy_key]

        # 기본 판단
        return f"현재 {emotion} 감정 상태에서 {strategy} 접근 방식을 권장합니다. 상황을 차근차근 살펴보시면 좋은 결과가 있을 것입니다."

    def _generate_alternatives(
        self, result: SharedJudgmentResult, request: JudgmentRequest
    ) -> List[str]:
        """대안 생성"""
        alternatives = []

        emotion = result.emotion_detected
        strategy = result.strategy_suggested

        # 전략별 대안 제안
        strategy_alternatives = {
            "logical": [
                "데이터를 더 수집해서 분석해보세요.",
                "단계별로 체계적으로 접근해보시는 것이 좋겠습니다.",
                "pros and cons를 정리해보시면 도움이 될 것입니다.",
            ],
            "empathetic": [
                "관련된 사람들의 입장을 고려해보세요.",
                "감정적인 부분도 중요하게 다뤄주세요.",
                "소통을 통해 서로의 마음을 이해해보세요.",
            ],
            "creative": [
                "기존과 다른 새로운 방법을 시도해보세요.",
                "브레인스토밍을 통해 아이디어를 발전시켜보세요.",
                "다른 분야의 접근법을 참고해보시는 것도 좋겠습니다.",
            ],
            "cautious": [
                "충분한 검토 시간을 가져보세요.",
                "리스크를 미리 파악하고 대비책을 마련하세요.",
                "전문가의 조언을 구해보시는 것도 좋겠습니다.",
            ],
        }

        # 현재 전략에 맞는 대안들 추가
        if strategy in strategy_alternatives:
            alternatives.extend(strategy_alternatives[strategy][:2])  # 최대 2개

        # 감정별 추가 대안
        if emotion == "sadness":
            alternatives.append("시간을 두고 천천히 접근해보세요.")
        elif emotion == "anger":
            alternatives.append("잠시 휴식을 취한 후 다시 생각해보세요.")
        elif emotion == "fear":
            alternatives.append("작은 단계부터 시작해서 점진적으로 진행해보세요.")

        return alternatives[:3]  # 최대 3개 반환

    def _update_performance_stats(self, processing_time: float):
        """성능 통계 업데이트"""
        total_successful = self.performance_stats["successful_requests"]
        current_avg = self.performance_stats["average_processing_time"]

        if total_successful == 1:
            self.performance_stats["average_processing_time"] = processing_time
        else:
            new_avg = (
                current_avg * (total_successful - 1) + processing_time
            ) / total_successful
            self.performance_stats["average_processing_time"] = new_avg

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        total_requests = self.performance_stats["total_requests"]
        if total_requests > 0:
            success_rate = (
                self.performance_stats["successful_requests"] / total_requests
            ) * 100
            failure_rate = (
                self.performance_stats["failed_requests"] / total_requests
            ) * 100
        else:
            success_rate = 0.0
            failure_rate = 0.0

        return {
            **self.performance_stats,
            "success_rate": round(success_rate, 2),
            "failure_rate": round(failure_rate, 2),
        }


# 편의 함수들
def quick_shared_judgment(
    text: str,
    context: Optional[str] = None,
    judgment_mode: JudgmentMode = JudgmentMode.HYBRID,
) -> SharedJudgmentResult:
    """빠른 공통 판단 함수"""
    engine = SharedJudgmentEngine()
    request = JudgmentRequest(text=text, context=context, judgment_mode=judgment_mode)
    return engine.process_judgment(request)


def extract_emotion_and_strategy(text: str) -> Tuple[str, str, float]:
    """감정과 전략만 빠르게 추출하는 함수"""
    engine = SharedJudgmentEngine()
    request = JudgmentRequest(
        text=text, include_context=False, include_alternatives=False
    )
    result = engine.process_judgment(request)
    return result.emotion_detected, result.strategy_suggested, result.confidence


# 전역 엔진 인스턴스 (성능 최적화)
_shared_engine = None


def get_shared_judgment_engine() -> SharedJudgmentEngine:
    """공통 판단 엔진 싱글톤 인스턴스 반환"""
    global _shared_engine
    if _shared_engine is None:
        _shared_engine = SharedJudgmentEngine()
    return _shared_engine


if __name__ == "__main__":
    # 테스트 코드
    print("🔗 공통 판단 로직 테스트")
    print("=" * 50)

    test_cases = [
        ("오늘 승진 소식을 들었어요! 너무 기뻐요!", "개인"),
        ("회의에서 제안이 거절당했어요. 화가 나네요.", "업무"),
        ("새로운 프로젝트 아이디어가 있는데 어떻게 시작해야 할까요?", "업무"),
        ("친구와 갈등이 있어서 마음이 아파요.", "개인관계"),
        ("시험이 다가와서 너무 불안해요.", "학업"),
    ]

    engine = SharedJudgmentEngine()

    for i, (text, context) in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        print(f"입력: {text}")
        print(f"맥락: {context}")

        request = JudgmentRequest(text=text, context=context, include_alternatives=True)

        result = engine.process_judgment(request)

        print(f"✅ 판단: {result.judgment}")
        print(f"📊 신뢰도: {result.confidence:.3f}")
        print(f"😊 감정: {result.emotion_detected}")
        print(f"🎯 전략: {result.strategy_suggested}")
        print(f"🏷️ 문맥: {result.context_detected}")
        print(f"🔑 키워드: {', '.join(result.keywords_extracted[:5])}")
        print(f"🔍 패턴: {', '.join(result.patterns_matched)}")
        print(f"⏱️ 처리시간: {result.processing_time:.3f}초")

        if result.alternatives:
            print(f"💡 대안:")
            for alt in result.alternatives:
                print(f"   • {alt}")

        print(
            f"🔄 추론과정: {' → '.join(result.reasoning_trace[-3:])}"
        )  # 마지막 3단계만

    # 성능 통계
    print(f"\n📈 성능 통계:")
    stats = engine.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
