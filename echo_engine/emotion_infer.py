#!/usr/bin/env python3
"""
💭 EchoJudgmentSystem v10 - Emotion Inference Engine
Foundation Doctrine 기반 감정 추론 및 리듬 분석 시스템

TT.004: "감정은 데이터가 아니라 판단의 리듬이다. 리듬은 패턴이 되어 예측을 가능하게 한다."
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json

# Foundation Doctrine 연동
try:
    from .echo_foundation_doctrine import SYSTEM_PHILOSOPHY, RHYTHM_PATTERNS
except ImportError:
    # fallback for testing
    RHYTHM_PATTERNS = {
        "emotional_flow": {
            "joy": {"next_likely": ["satisfaction", "excitement"], "decay_rate": 0.7},
            "sadness": {
                "next_likely": ["contemplation", "acceptance"],
                "decay_rate": 0.8,
            },
            "anger": {
                "next_likely": ["frustration", "determination"],
                "decay_rate": 0.6,
            },
            "fear": {"next_likely": ["anxiety", "caution"], "decay_rate": 0.9},
            "surprise": {"next_likely": ["curiosity", "confusion"], "decay_rate": 0.5},
            "neutral": {"next_likely": ["calm", "readiness"], "decay_rate": 0.4},
        }
    }
    SYSTEM_PHILOSOPHY = None


@dataclass
class EmotionInferenceResult:
    """감정 추론 결과"""

    primary_emotion: str
    confidence: float
    secondary_emotions: List[Tuple[str, float]]
    emotional_intensity: float
    predicted_next_emotions: List[str]
    decay_rate: float
    analysis_time: float
    context_factors: Dict[str, Any]
    foundation_compliance: Dict[str, Any]

    @property
    def dominant_emotion(self) -> str:
        """기존 코드 호환을 위한 속성: primary_emotion을 참조"""
        return self.primary_emotion


@dataclass
class EmotionContext:
    """공명 합성을 위한 핵심 감정 요약 객체"""

    primary_emotion: str
    intensity: float
    confidence: float


class EmotionInferenceEngine:
    """Foundation Doctrine 기반 감정 추론 엔진"""

    def __init__(self):
        self.emotion_patterns = RHYTHM_PATTERNS.get("emotional_flow", {})
        self.inference_history = []
        self.context_memory = {}

        # 감정 키워드 사전 (한국어 + 영어)
        self.emotion_keywords = {
            "joy": {
                "korean": [
                    "기쁘",
                    "행복",
                    "즐거",
                    "신나",
                    "좋아",
                    "만족",
                    "최고",
                    "완벽",
                    "사랑",
                    "감사",
                ],
                "english": [
                    "happy",
                    "joy",
                    "excited",
                    "love",
                    "great",
                    "awesome",
                    "perfect",
                    "satisfied",
                    "pleased",
                    "delighted",
                ],
                "intensity_modifiers": [
                    "정말",
                    "너무",
                    "아주",
                    "매우",
                    "완전",
                    "very",
                    "really",
                    "extremely",
                    "absolutely",
                ],
            },
            "sadness": {
                "korean": [
                    "슬프",
                    "우울",
                    "힘들",
                    "외롭",
                    "속상",
                    "안타까",
                    "아쉽",
                    "실망",
                    "울적",
                    "처량",
                ],
                "english": [
                    "sad",
                    "depressed",
                    "lonely",
                    "disappointed",
                    "upset",
                    "down",
                    "blue",
                    "melancholy",
                    "gloomy",
                ],
                "intensity_modifiers": [
                    "너무",
                    "많이",
                    "정말",
                    "매우",
                    "완전",
                    "very",
                    "really",
                    "extremely",
                    "deeply",
                ],
            },
            "anger": {
                "korean": [
                    "화",
                    "짜증",
                    "분노",
                    "열받",
                    "빡치",
                    "싫어",
                    "미워",
                    "답답",
                    "억울",
                    "분하",
                ],
                "english": [
                    "angry",
                    "mad",
                    "furious",
                    "annoyed",
                    "irritated",
                    "hate",
                    "rage",
                    "frustrated",
                    "pissed",
                ],
                "intensity_modifiers": [
                    "정말",
                    "너무",
                    "완전",
                    "매우",
                    "really",
                    "extremely",
                    "very",
                    "absolutely",
                ],
            },
            "fear": {
                "korean": [
                    "무서",
                    "두려",
                    "걱정",
                    "불안",
                    "겁",
                    "떨리",
                    "조마조마",
                    "긴장",
                    "스트레스",
                ],
                "english": [
                    "scared",
                    "afraid",
                    "worried",
                    "anxious",
                    "nervous",
                    "terrified",
                    "panic",
                    "stress",
                    "fear",
                ],
                "intensity_modifiers": [
                    "너무",
                    "정말",
                    "매우",
                    "완전",
                    "very",
                    "really",
                    "extremely",
                    "absolutely",
                ],
            },
            "surprise": {
                "korean": [
                    "놀라",
                    "깜짝",
                    "신기",
                    "의외",
                    "예상외",
                    "헐",
                    "와우",
                    "대박",
                    "어머",
                ],
                "english": [
                    "surprised",
                    "shocked",
                    "amazed",
                    "wow",
                    "incredible",
                    "unexpected",
                    "astonished",
                    "stunned",
                ],
                "intensity_modifiers": [
                    "정말",
                    "너무",
                    "완전",
                    "매우",
                    "really",
                    "very",
                    "extremely",
                    "absolutely",
                ],
            },
            "neutral": {
                "korean": [
                    "평범",
                    "그냥",
                    "보통",
                    "일반",
                    "괜찮",
                    "무난",
                    "평온",
                    "차분",
                    "안정",
                ],
                "english": [
                    "normal",
                    "okay",
                    "fine",
                    "average",
                    "calm",
                    "peaceful",
                    "stable",
                    "neutral",
                ],
                "intensity_modifiers": [
                    "좀",
                    "약간",
                    "조금",
                    "somewhat",
                    "slightly",
                    "a bit",
                ],
            },
        }

        # 감정 전환 규칙
        self.emotion_transitions = {
            "joy": {
                "to_sadness": 0.1,
                "to_anger": 0.05,
                "to_fear": 0.05,
                "to_surprise": 0.2,
                "to_neutral": 0.3,
            },
            "sadness": {
                "to_joy": 0.15,
                "to_anger": 0.25,
                "to_fear": 0.3,
                "to_surprise": 0.1,
                "to_neutral": 0.4,
            },
            "anger": {
                "to_joy": 0.1,
                "to_sadness": 0.2,
                "to_fear": 0.15,
                "to_surprise": 0.1,
                "to_neutral": 0.5,
            },
            "fear": {
                "to_joy": 0.05,
                "to_sadness": 0.3,
                "to_anger": 0.2,
                "to_surprise": 0.15,
                "to_neutral": 0.4,
            },
            "surprise": {
                "to_joy": 0.4,
                "to_sadness": 0.1,
                "to_anger": 0.1,
                "to_fear": 0.1,
                "to_neutral": 0.3,
            },
            "neutral": {
                "to_joy": 0.2,
                "to_sadness": 0.15,
                "to_anger": 0.15,
                "to_fear": 0.15,
                "to_surprise": 0.2,
            },
        }

    def infer_emotion(
        self, text: str, context: Dict[str, Any] = None
    ) -> EmotionInferenceResult:
        """Foundation Doctrine 기반 감정 추론"""
        start_time = time.time()

        # 텍스트 전처리
        text = self._preprocess_text(text)

        # 감정 점수 계산
        emotion_scores = self._calculate_emotion_scores(text)

        # 1차 감정 결정
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]

        # 2차 감정들 추출
        secondary_emotions = sorted(
            [
                (emotion, score)
                for emotion, score in emotion_scores.items()
                if emotion != primary_emotion
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        # 감정 강도 계산
        emotional_intensity = self._calculate_intensity(text, primary_emotion)

        # 다음 감정 예측 (Foundation Doctrine 기반)
        predicted_next_emotions = self._predict_next_emotions(primary_emotion)

        # 감쇠율 조회
        decay_rate = self.emotion_patterns.get(primary_emotion, {}).get(
            "decay_rate", 0.5
        )

        # 컨텍스트 요소 분석
        context_factors = self._analyze_context_factors(text, context)

        # Foundation Doctrine 준수 검증
        foundation_compliance = self._validate_foundation_compliance(
            primary_emotion, confidence, context_factors
        )

        # 결과 생성
        result = EmotionInferenceResult(
            primary_emotion=primary_emotion,
            confidence=confidence,
            secondary_emotions=secondary_emotions,
            emotional_intensity=emotional_intensity,
            predicted_next_emotions=predicted_next_emotions,
            decay_rate=decay_rate,
            analysis_time=time.time() - start_time,
            context_factors=context_factors,
            foundation_compliance=foundation_compliance,
        )

        # 추론 이력 저장
        self.inference_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "text": text[:100] + "..." if len(text) > 100 else text,
                "result": result,
            }
        )

        # 이력 크기 제한
        if len(self.inference_history) > 100:
            self.inference_history = self.inference_history[-100:]

        return result

    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 특수 문자 정리
        text = re.sub(r"[^\w\s가-힣]", " ", text)
        # 연속 공백 제거
        text = re.sub(r"\s+", " ", text)
        # 소문자 변환
        text = text.lower().strip()
        return text

    def _calculate_emotion_scores(self, text: str) -> Dict[str, float]:
        """고급 감정 점수 계산 - 다층적 분석"""
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_keywords.keys()}

        # 1단계: 키워드 기반 분석
        keyword_scores = self._analyze_keywords(text)

        # 2단계: 문법적 패턴 분석
        grammatical_scores = self._analyze_grammatical_patterns(text)

        # 3단계: 감정 강도 분석
        intensity_multiplier = self._calculate_emotion_intensity(text)

        # 4단계: 부정 표현 분석
        negation_factor = self._analyze_negation(text)

        # 5단계: 문장 구조 분석
        structural_scores = self._analyze_sentence_structure(text)

        # 점수 통합
        for emotion in emotion_scores.keys():
            base_score = keyword_scores.get(emotion, 0.0)
            grammar_boost = grammatical_scores.get(emotion, 0.0)
            structure_boost = structural_scores.get(emotion, 0.0)

            # 종합 점수 계산
            combined_score = (
                base_score * 0.5 + grammar_boost * 0.3 + structure_boost * 0.2
            )
            combined_score *= intensity_multiplier
            combined_score *= negation_factor.get(emotion, 1.0)

            emotion_scores[emotion] = max(0.0, combined_score)

        # 정규화
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {
                emotion: score / total_score
                for emotion, score in emotion_scores.items()
            }
        else:
            # 감정을 찾지 못한 경우 - 문장 길이와 톤을 고려한 기본값
            emotion_scores = self._get_default_emotion_scores(text)

        return emotion_scores

    def _analyze_keywords(self, text: str) -> Dict[str, float]:
        """키워드 기반 감정 분석"""
        scores = {emotion: 0.0 for emotion in self.emotion_keywords.keys()}

        for emotion, keywords in self.emotion_keywords.items():
            score = 0.0

            # 정확한 키워드 매칭
            for keyword in keywords["korean"] + keywords["english"]:
                if keyword in text:
                    score += 1.0

                    # 강도 수식어 근접성 체크
                    for modifier in keywords["intensity_modifiers"]:
                        if modifier in text:
                            keyword_pos = text.find(keyword)
                            modifier_pos = text.find(modifier)
                            distance = abs(keyword_pos - modifier_pos)
                            if distance < 15:  # 가까운 거리에 있으면
                                score += 0.8 * (
                                    1 - distance / 15
                                )  # 거리에 반비례하여 가중치 적용

            scores[emotion] = score

        return scores

    def _analyze_grammatical_patterns(self, text: str) -> Dict[str, float]:
        """문법적 패턴 기반 감정 분석"""
        scores = {emotion: 0.0 for emotion in self.emotion_keywords.keys()}

        # 감탄사 패턴
        if re.search(r"[!]{2,}", text):  # 연속된 느낌표
            scores["joy"] += 0.8
            scores["anger"] += 0.6
            scores["surprise"] += 0.7

        # 질문 패턴
        if "?" in text or any(
            q in text for q in ["왜", "어떻게", "why", "how", "what"]
        ):
            scores["surprise"] += 0.4
            scores["fear"] += 0.2

        # 완료형 패턴 ("~했어", "~됐어")
        if re.search(r"했어|됐어|finished|done", text):
            scores["joy"] += 0.3
            scores["sadness"] += 0.2

        # 부정적 추측 패턴
        if any(
            pattern in text for pattern in ["아마", "혹시", "maybe", "perhaps", "might"]
        ):
            scores["fear"] += 0.3
            scores["neutral"] += 0.2

        return scores

    def _analyze_sentence_structure(self, text: str) -> Dict[str, float]:
        """문장 구조 기반 감정 분석"""
        scores = {emotion: 0.0 for emotion in self.emotion_keywords.keys()}

        # 문장 길이 분석
        length = len(text)
        if length < 5:  # 매우 짧은 문장
            scores["neutral"] += 0.3
        elif length > 50:  # 긴 문장
            scores["sadness"] += 0.2
            scores["anger"] += 0.2

        # 반복 패턴 ("정말정말", "ㅋㅋㅋ")
        if re.search(r"(.)\1{2,}", text) or re.search(r"(..)\1+", text):
            scores["joy"] += 0.5
            scores["surprise"] += 0.3

        # 이모티콘/이모지 패턴
        emoticon_patterns = {
            "joy": [":)", "^^", "^_^", "😊", "😄", "😃", "😀", "🎉", "✨", "💛", "🌟"],
            "sadness": [":(", "T_T", "ㅠㅠ", "😢", "😭", "😞", "💔"],
            "anger": [">:(", "😠", "😡", "💢", "🔥"],
            "surprise": [":O", "😮", "😲", "😯", "❗", "❓", "‼️"],
            "fear": ["😰", "😨", "😱", "💦"],
        }

        for emotion, patterns in emoticon_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    scores[emotion] += 0.7

        return scores

    def _calculate_emotion_intensity(self, text: str) -> float:
        """감정 강도 계산"""
        intensity = 1.0

        # 대문자 사용
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        intensity += uppercase_ratio * 0.5

        # 느낌표 개수
        exclamation_count = text.count("!")
        intensity += min(exclamation_count * 0.2, 1.0)

        # 반복 강조
        if re.search(r"정말|너무|매우|완전|진짜", text):
            intensity += 0.3

        return min(intensity, 2.0)  # 최대 2배까지

    def _analyze_negation(self, text: str) -> Dict[str, float]:
        """부정 표현 분석"""
        negation_factors = {emotion: 1.0 for emotion in self.emotion_keywords.keys()}

        # 부정 패턴들
        negation_patterns = [
            "안",
            "못",
            "없",
            "아니",
            "don't",
            "not",
            "no",
            "never",
            "can't",
        ]

        for pattern in negation_patterns:
            if pattern in text:
                # 부정어가 있으면 긍정적 감정은 줄이고 부정적 감정은 늘림
                negation_factors["joy"] *= 0.3
                negation_factors["surprise"] *= 0.5
                negation_factors["sadness"] *= 1.3
                negation_factors["anger"] *= 1.2
                negation_factors["fear"] *= 1.2
                break

        return negation_factors

    def _get_default_emotion_scores(self, text: str) -> Dict[str, float]:
        """기본 감정 점수 (감정을 찾지 못한 경우)"""
        # 문장의 톤을 분석하여 기본 감정 설정
        if "?" in text:
            return {"surprise": 0.4, "neutral": 0.6}
        elif "!" in text:
            return {"joy": 0.3, "surprise": 0.2, "neutral": 0.5}
        elif len(text) < 5:
            return {"neutral": 1.0}
        else:
            return {"neutral": 0.8, "joy": 0.1, "surprise": 0.1}

    def _calculate_contextual_weight(self, text: str, emotion: str) -> float:
        """문맥적 가중치 계산"""
        weight = 1.0

        # 부정 표현 체크
        negative_patterns = ["안", "못", "없", "don't", "not", "no", "never"]
        for pattern in negative_patterns:
            if pattern in text:
                if emotion in ["joy", "surprise"]:
                    weight *= 0.5  # 긍정 감정 약화
                elif emotion in ["sadness", "anger", "fear"]:
                    weight *= 1.2  # 부정 감정 강화

        # 질문 형태 체크
        if "?" in text or any(
            word in text for word in ["어떻게", "왜", "뭐", "what", "how", "why"]
        ):
            if emotion == "surprise":
                weight *= 1.3
            elif emotion == "neutral":
                weight *= 1.1

        # 감탄 표현 체크
        if "!" in text or any(
            word in text for word in ["와", "헉", "어머", "wow", "oh"]
        ):
            if emotion in ["joy", "surprise", "anger"]:
                weight *= 1.2

        return weight

    def _calculate_intensity(self, text: str, emotion: str) -> float:
        """감정 강도 계산"""
        base_intensity = 0.5

        # 강도 수식어 체크
        intensity_modifiers = {
            "high": [
                "정말",
                "너무",
                "완전",
                "매우",
                "아주",
                "extremely",
                "very",
                "really",
                "absolutely",
            ],
            "medium": ["좀", "조금", "약간", "somewhat", "slightly", "a bit"],
            "low": ["별로", "그냥", "not really", "not very"],
        }

        for level, modifiers in intensity_modifiers.items():
            for modifier in modifiers:
                if modifier in text:
                    if level == "high":
                        base_intensity += 0.3
                    elif level == "medium":
                        base_intensity += 0.1
                    elif level == "low":
                        base_intensity -= 0.2

        # 반복 표현 체크
        repeated_chars = re.findall(r"(.)\1{2,}", text)
        if repeated_chars:
            base_intensity += 0.2

        # 대문자 사용 체크 (영어)
        if re.search(r"[A-Z]{2,}", text):
            base_intensity += 0.1

        return max(0.0, min(1.0, base_intensity))

    def _predict_next_emotions(self, current_emotion: str) -> List[str]:
        """다음 감정 예측 (Foundation Doctrine 기반)"""
        if current_emotion in self.emotion_patterns:
            return self.emotion_patterns[current_emotion]["next_likely"]
        else:
            # 기본 전환 규칙 사용
            transitions = self.emotion_transitions.get(current_emotion, {})
            return sorted(
                transitions.keys(), key=lambda x: transitions.get(x, 0), reverse=True
            )[:2]

    def _analyze_context_factors(
        self, text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """컨텍스트 요소 분석"""
        factors = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "question_present": "?" in text,
            "exclamation_present": "!" in text,
            "time_indicators": self._detect_time_indicators(text),
            "personal_pronouns": self._detect_personal_pronouns(text),
            "context_provided": context is not None,
        }

        if context:
            factors.update(
                {"context_keys": list(context.keys()), "context_size": len(context)}
            )

        return factors

    def _detect_time_indicators(self, text: str) -> List[str]:
        """시간 지시어 감지"""
        time_indicators = []
        patterns = {
            "past": [
                "했었",
                "였었",
                "과거",
                "예전",
                "전에",
                "was",
                "were",
                "ago",
                "before",
            ],
            "present": ["지금", "현재", "요즘", "오늘", "now", "today", "currently"],
            "future": ["미래", "앞으로", "내일", "will", "tomorrow", "next", "future"],
        }

        for tense, words in patterns.items():
            for word in words:
                if word in text:
                    time_indicators.append(tense)
                    break

        return time_indicators

    def _detect_personal_pronouns(self, text: str) -> List[str]:
        """인칭 대명사 감지"""
        pronouns = []
        patterns = {
            "first_person": ["나", "내", "우리", "I", "me", "my", "we", "us", "our"],
            "second_person": ["너", "당신", "you", "your"],
            "third_person": [
                "그",
                "그녀",
                "그들",
                "he",
                "she",
                "they",
                "him",
                "her",
                "them",
            ],
        }

        for person, words in patterns.items():
            for word in words:
                if word in text:
                    pronouns.append(person)
                    break

        return pronouns

    def _validate_foundation_compliance(
        self, emotion: str, confidence: float, context_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Foundation Doctrine 준수 검증"""
        compliance = {"is_compliant": True, "violations": [], "doctrine_alignment": {}}

        # TT.004 검증: 감정은 데이터가 아니라 판단의 리듬이다
        if confidence < 0.3:
            compliance["violations"].append("감정 신뢰도 부족 (TT.004 위반)")
            compliance["is_compliant"] = False

        # 리듬 패턴 존재 확인
        if emotion in self.emotion_patterns:
            compliance["doctrine_alignment"]["rhythm_pattern_exists"] = True
        else:
            compliance["doctrine_alignment"]["rhythm_pattern_exists"] = False
            compliance["violations"].append("리듬 패턴 미정의 (TT.004 위반)")

        # 컨텍스트 고려 검증
        if not context_factors.get("context_provided", False):
            compliance["violations"].append("컨텍스트 미고려 (적응성 위반)")

        return compliance

    def get_emotion_flow_analysis(self, limit: int = 10) -> Dict[str, Any]:
        """감정 흐름 분석"""
        if len(self.inference_history) < 2:
            return {
                "message": "분석할 데이터 부족",
                "history_count": len(self.inference_history),
            }

        recent_history = self.inference_history[-limit:]

        # 감정 변화 패턴 분석
        emotion_sequence = [entry["result"].primary_emotion for entry in recent_history]
        transitions = []

        for i in range(len(emotion_sequence) - 1):
            current = emotion_sequence[i]
            next_emotion = emotion_sequence[i + 1]
            transitions.append((current, next_emotion))

        # 전환 빈도 계산
        transition_counts = {}
        for current, next_emotion in transitions:
            key = f"{current} → {next_emotion}"
            transition_counts[key] = transition_counts.get(key, 0) + 1

        # 평균 신뢰도 계산
        avg_confidence = sum(
            entry["result"].confidence for entry in recent_history
        ) / len(recent_history)

        # 평균 강도 계산
        avg_intensity = sum(
            entry["result"].emotional_intensity for entry in recent_history
        ) / len(recent_history)

        return {
            "analysis_period": f"최근 {len(recent_history)}개 추론",
            "emotion_sequence": emotion_sequence,
            "most_common_transitions": sorted(
                transition_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "average_confidence": round(avg_confidence, 3),
            "average_intensity": round(avg_intensity, 3),
            "dominant_emotion": max(set(emotion_sequence), key=emotion_sequence.count),
            "emotion_diversity": len(set(emotion_sequence)),
            "foundation_compliance_rate": self._calculate_compliance_rate(
                recent_history
            ),
        }

    def _calculate_compliance_rate(self, history: List[Dict]) -> float:
        """Foundation Doctrine 준수율 계산"""
        if not history:
            return 0.0

        compliant_count = sum(
            1
            for entry in history
            if entry["result"].foundation_compliance["is_compliant"]
        )
        return compliant_count / len(history)


def infer_emotion(text: str, context: Dict[str, Any] = None) -> EmotionInferenceResult:
    """감정 추론 편의 함수"""
    engine = EmotionInferenceEngine()
    return engine.infer_emotion(text, context)


def analyze_emotional_rhythm(texts: List[str]) -> Dict[str, Any]:
    """감정 리듬 분석 편의 함수"""
    engine = EmotionInferenceEngine()

    results = []
    for text in texts:
        result = engine.infer_emotion(text)
        results.append(result)

    return engine.get_emotion_flow_analysis()


# 테스트 함수
def test_emotion_inference():
    """감정 추론 엔진 테스트"""
    print("💭 Foundation 기반 감정 추론 엔진 테스트 시작...")

    engine = EmotionInferenceEngine()

    test_cases = [
        "오늘 정말 기쁜 일이 있었어요! 너무 행복해요.",
        "좀 슬프고 우울한 하루였어요. 힘들었습니다.",
        "화가 나고 짜증이 나요. 정말 열받아요!",
        "무서워요. 너무 불안하고 걱정되네요.",
        "어? 이게 뭐예요? 정말 놀랐어요!",
        "그냥 평범한 하루였어요. 특별한 일은 없었고요.",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n🔍 테스트 {i}: {text}")

        result = engine.infer_emotion(text)

        print(f"  💭 주요 감정: {result.primary_emotion}")
        print(f"  📊 신뢰도: {result.confidence:.3f}")
        print(f"  🔥 강도: {result.emotional_intensity:.3f}")
        print(f"  🔮 다음 예측: {result.predicted_next_emotions}")
        print(f"  📉 감쇠율: {result.decay_rate:.3f}")
        print(f"  ⚖️ Foundation 준수: {result.foundation_compliance['is_compliant']}")
        print(f"  ⏱️ 분석 시간: {result.analysis_time:.4f}초")

        if result.foundation_compliance["violations"]:
            print(f"  ⚠️ 위반사항: {result.foundation_compliance['violations']}")

    # 감정 흐름 분석
    print("\n📈 감정 흐름 분석:")
    flow_analysis = engine.get_emotion_flow_analysis()
    print(f"  주요 감정: {flow_analysis['dominant_emotion']}")
    print(f"  평균 신뢰도: {flow_analysis['average_confidence']}")
    print(f"  평균 강도: {flow_analysis['average_intensity']}")
    print(f"  Foundation 준수율: {flow_analysis['foundation_compliance_rate']:.1%}")

    if flow_analysis["most_common_transitions"]:
        print("  주요 전환 패턴:")
        for transition, count in flow_analysis["most_common_transitions"]:
            print(f"    {transition}: {count}회")

    print("\n🎉 감정 추론 엔진 테스트 완료!")


def to_emotion_context(result: EmotionInferenceResult) -> EmotionContext:
    return EmotionContext(
        primary_emotion=result.primary_emotion,
        intensity=result.emotional_intensity,
        confidence=result.confidence,
    )


# 실행 테스트
if __name__ == "__main__":
    test_emotion_inference()
