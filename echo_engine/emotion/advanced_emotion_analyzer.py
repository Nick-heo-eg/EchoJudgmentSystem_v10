#!/usr/bin/env python3
"""
🧠 Advanced Emotion Analyzer v1.0
다차원 감정 벡터 추론을 위한 고도화 감정 분석 모듈

Phase 1: LLM-Free 판단 시스템 핵심 모듈
- 감정 강도, 변동성, 상황 의존성 등을 포함한 감정 벡터 추론
- 기존 emotion_infer.py와 연동하되 고도화된 분석 제공
- PyTorch/NumPy 기반 경량 실행
"""

import re
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import json
import os

# 기존 모듈과 연동
try:
    from echo_engine.emotion_infer import infer_emotion, EmotionInferenceResult

    EMOTION_INFER_AVAILABLE = True
except ImportError:
    EMOTION_INFER_AVAILABLE = False


class AdvancedEmotionAnalyzer:
    """고도화 감정 분석기 - 다차원 감정 벡터 추론"""

    def __init__(self):
        """초기화"""
        self.version = "1.0.0"
        self.analysis_count = 0
        self.emotion_history = []

        # 감정 강도 계산용 패턴들
        self.intensity_patterns = {
            "high": [
                r"정말",
                r"너무",
                r"완전",
                r"진짜",
                r"매우",
                r"아주",
                r"엄청",
                r"!{2,}",
                r"[ㅋㅎ]{3,}",
                r"ㅠ{2,}",
                r"[♥❤💕💖]{2,}",
            ],
            "medium": [
                r"좀",
                r"조금",
                r"약간",
                r"살짝",
                r"다소",
                r"어느정도",
                r"!\w",
                r"[ㅋㅎ]{1,2}",
                r"ㅠ",
            ],
            "low": [r"그냥", r"별로", r"딱히", r"그리", r"그저", r"단지"],
        }

        # 안정성 평가용 키워드
        self.stability_indicators = {
            "unstable": [
                r"갑자기",
                r"순간",
                r"급에",
                r"바로",
                r"즉시",
                r"이제야",
                r"문득",
                r"변덕",
                r"기복",
                r"롤러코스터",
            ],
            "stable": [
                r"계속",
                r"줄곧",
                r"꾸준히",
                r"항상",
                r"지속적",
                r"일관되게",
                r"변함없이",
                r"안정적",
            ],
        }

        # 상황 의존성 키워드
        self.context_keywords = {
            "temporal": [r"오늘", r"어제", r"내일", r"요즘", r"최근", r"지금", r"현재"],
            "spatial": [r"집", r"회사", r"학교", r"밖", r"여기", r"거기", r"곳"],
            "social": [r"친구", r"가족", r"동료", r"사람", r"혼자", r"함께", r"우리"],
            "activity": [r"일", r"공부", r"운동", r"게임", r"영화", r"음악", r"여행"],
        }

        print(f"🧠 Advanced Emotion Analyzer v{self.version} 초기화 완료")

    def analyze_emotion_advanced(
        self, text: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        다차원 감정 벡터 추론 메인 함수

        Args:
            text: 분석할 텍스트
            context: 추가 컨텍스트 정보

        Returns:
            고도화된 감정 분석 결과
        """
        self.analysis_count += 1
        start_time = time.time()

        # 1. 기본 감정 분석 (기존 모듈 활용)
        base_emotions = self._get_base_emotions(text)

        # 2. 감정 강도 계산
        intensity = self._calculate_intensity(text)

        # 3. 안정성 평가
        stability = self._calculate_stability(text)

        # 4. 상황 의존성 계산
        context_dependency = self._calculate_context_dependency(text, context)

        # 5. 시간적 감쇠율 추정
        temporal_decay = self._estimate_temporal_decay(text, base_emotions)

        # 6. 감정 복잡도 계산
        complexity = self._calculate_emotion_complexity(base_emotions, intensity)

        # 7. 메타 정보 수집
        meta_info = self._collect_meta_information(text, context)

        # 결과 구성
        result = {
            "primary": base_emotions,
            "intensity": intensity,
            "stability": stability,
            "context_dependency": context_dependency,
            "temporal_decay": temporal_decay,
            "complexity": complexity,
            "meta": {
                **meta_info,
                "analysis_id": self.analysis_count,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
            },
        }

        # 히스토리에 저장
        self.emotion_history.append(result)

        # 히스토리 크기 제한
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]

        return result

    def _get_base_emotions(self, text: str) -> Dict[str, float]:
        """기존 감정 추론 시스템 활용"""
        if EMOTION_INFER_AVAILABLE:
            try:
                result = infer_emotion(text)
                if hasattr(result, "primary_emotion") and hasattr(result, "confidence"):
                    # EmotionInferenceResult 객체인 경우
                    primary = result.primary_emotion
                    confidence = result.confidence

                    # 보조 감정들도 추출
                    secondary = {}
                    if hasattr(result, "secondary_emotions"):
                        for emotion, score in result.secondary_emotions[:3]:
                            secondary[emotion] = score

                    # 주요 감정과 보조 감정들을 합침
                    emotions = {primary: confidence, **secondary}
                    return emotions

            except Exception as e:
                print(f"⚠️ 기존 감정 추론 시스템 오류: {e}")

        # Fallback: 간단한 키워드 기반 분석
        return self._fallback_emotion_analysis(text)

    def _fallback_emotion_analysis(self, text: str) -> Dict[str, float]:
        """기존 시스템 사용 불가시 fallback 감정 분석"""
        emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "neutral": 0.0,
        }

        # 간단한 키워드 매칭
        emotion_keywords = {
            "joy": [r"기쁘", r"행복", r"좋", r"신나", r"즐거", r"만족", r"사랑"],
            "sadness": [r"슬프", r"우울", r"힘들", r"외롭", r"속상", r"아쉽", r"실망"],
            "anger": [r"화", r"짜증", r"분노", r"열받", r"빡치", r"싫", r"미워"],
            "fear": [r"무서", r"두려", r"걱정", r"불안", r"겁", r"떨리", r"조마조마"],
            "surprise": [r"놀라", r"깜짝", r"신기", r"의외", r"헐", r"와우", r"대박"],
        }

        text_lower = text.lower()
        total_matches = 0

        for emotion, keywords in emotion_keywords.items():
            matches = sum(1 for keyword in keywords if re.search(keyword, text_lower))
            emotions[emotion] = matches
            total_matches += matches

        # 정규화
        if total_matches > 0:
            emotions = {k: v / total_matches for k, v in emotions.items()}
        else:
            emotions["neutral"] = 1.0

        return emotions

    def _calculate_intensity(self, text: str) -> float:
        """감정 강도 계산 (0.0 ~ 1.0)"""
        intensity_score = 0.0

        # 강도 패턴별 점수 계산
        for level, patterns in self.intensity_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, text))

            if level == "high":
                intensity_score += matches * 0.8
            elif level == "medium":
                intensity_score += matches * 0.5
            elif level == "low":
                intensity_score -= matches * 0.3

        # 대문자 사용률
        if len(text) > 0:
            uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
            intensity_score += uppercase_ratio * 0.5

        # 문장 길이 고려 (긴 문장은 감정이 더 강할 수 있음)
        length_factor = min(len(text) / 100, 0.3)
        intensity_score += length_factor

        # 0.0 ~ 1.0 범위로 정규화
        return max(0.0, min(intensity_score, 1.0))

    def _calculate_stability(self, text: str) -> float:
        """감정 안정성 계산 (0.0: 불안정, 1.0: 안정)"""
        stability_score = 0.5  # 기본값

        # 불안정 지시어 체크
        unstable_matches = sum(
            1
            for pattern in self.stability_indicators["unstable"]
            if re.search(pattern, text)
        )

        # 안정 지시어 체크
        stable_matches = sum(
            1
            for pattern in self.stability_indicators["stable"]
            if re.search(pattern, text)
        )

        # 점수 조정
        stability_score += (stable_matches * 0.2) - (unstable_matches * 0.2)

        # 과거 히스토리와 비교 (일관성 체크)
        if len(self.emotion_history) > 0:
            recent_emotions = [entry["primary"] for entry in self.emotion_history[-5:]]
            consistency = self._calculate_emotion_consistency(recent_emotions)
            stability_score += consistency * 0.3

        return max(0.0, min(stability_score, 1.0))

    def _calculate_context_dependency(
        self, text: str, context: Optional[Dict]
    ) -> float:
        """상황 의존성 계산 (0.0: 독립적, 1.0: 상황 의존적)"""
        dependency_score = 0.0

        # 상황 키워드 출현 빈도
        total_context_mentions = 0
        for category, keywords in self.context_keywords.items():
            matches = sum(1 for keyword in keywords if re.search(keyword, text))
            total_context_mentions += matches

        # 키워드 밀도 기반 의존성
        if len(text) > 0:
            keyword_density = total_context_mentions / max(len(text.split()), 1)
            dependency_score += keyword_density * 2.0

        # 외부 컨텍스트 정보 활용
        if context:
            context_factors = len(context.keys())
            dependency_score += min(context_factors * 0.1, 0.3)

        # 지시대명사 및 생략 패턴 (상황 의존성 증가)
        referential_patterns = [r"그", r"이", r"저", r"요거", r"그거", r"이거"]
        referential_matches = sum(
            1 for pattern in referential_patterns if re.search(pattern, text)
        )
        dependency_score += referential_matches * 0.1

        return max(0.0, min(dependency_score, 1.0))

    def _estimate_temporal_decay(self, text: str, emotions: Dict[str, float]) -> float:
        """시간적 감쇠율 추정 (0.0: 빠른 감쇠, 1.0: 지속적)"""

        # 감정별 기본 감쇠율
        emotion_decay_rates = {
            "joy": 0.3,  # 기쁨은 비교적 빨리 사라짐
            "sadness": 0.7,  # 슬픔은 오래 지속
            "anger": 0.4,  # 분노는 중간 정도 지속
            "fear": 0.6,  # 두려움은 오래 남음
            "surprise": 0.1,  # 놀라움은 순간적
            "neutral": 0.9,  # 중립은 안정적
        }

        # 주요 감정의 가중 평균 감쇠율
        weighted_decay = 0.0
        total_weight = 0.0

        for emotion, confidence in emotions.items():
            if emotion in emotion_decay_rates:
                weighted_decay += emotion_decay_rates[emotion] * confidence
                total_weight += confidence

        base_decay = weighted_decay / max(total_weight, 0.1)

        # 텍스트 패턴 기반 조정
        persistence_patterns = [r"계속", r"항상", r"늘", r"지속", r"오래"]
        temporary_patterns = [r"잠깐", r"순간", r"금방", r"곧", r"일시적"]

        persistence_matches = sum(
            1 for pattern in persistence_patterns if re.search(pattern, text)
        )
        temporary_matches = sum(
            1 for pattern in temporary_patterns if re.search(pattern, text)
        )

        decay_adjustment = (temporary_matches * 0.2) - (persistence_matches * 0.2)

        return max(0.0, min(base_decay + decay_adjustment, 1.0))

    def _calculate_emotion_complexity(
        self, emotions: Dict[str, float], intensity: float
    ) -> float:
        """감정 복잡도 계산 (0.0: 단순, 1.0: 복잡)"""

        # 활성 감정 개수 (threshold 이상의 감정들)
        threshold = 0.1
        active_emotions = sum(1 for score in emotions.values() if score > threshold)

        # Shannon entropy 계산 (감정 분포의 복잡도)
        entropy = 0.0
        total_score = sum(emotions.values())

        if total_score > 0:
            for score in emotions.values():
                if score > 0:
                    p = score / total_score
                    entropy -= p * math.log2(p)

        # 정규화된 엔트로피 (log2(6) = 최대 엔트로피, 6개 기본 감정)
        normalized_entropy = entropy / math.log2(6) if entropy > 0 else 0

        # 복잡도 = 활성 감정 수 + 엔트로피 + 강도 보정
        complexity = (
            (active_emotions / 6) * 0.4  # 활성 감정 비율
            + normalized_entropy * 0.4  # 분포 복잡도
            + intensity * 0.2  # 강도 영향
        )

        return max(0.0, min(complexity, 1.0))

    def _calculate_emotion_consistency(self, emotion_history: List[Dict]) -> float:
        """감정 일관성 계산"""
        if len(emotion_history) < 2:
            return 0.5

        # 주요 감정의 변화 폭 계산
        primary_emotions = []
        for emotions in emotion_history:
            if emotions:
                primary = max(emotions.items(), key=lambda x: x[1])[0]
                primary_emotions.append(primary)

        # 연속된 감정 변화 계산
        changes = 0
        for i in range(1, len(primary_emotions)):
            if primary_emotions[i] != primary_emotions[i - 1]:
                changes += 1

        # 일관성 = 1 - (변화율)
        consistency = 1.0 - (changes / max(len(primary_emotions) - 1, 1))
        return max(0.0, min(consistency, 1.0))

    def _collect_meta_information(
        self, text: str, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """메타 정보 수집"""
        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r"[.!?]", text)),
            "special_chars": len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', text)),
            "emoji_count": len(re.findall(r"[😀-🙏]", text)),
            "context_provided": context is not None,
            "has_question": "?" in text,
            "has_exclamation": "!" in text,
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        }

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환"""
        return {
            "version": self.version,
            "total_analyses": self.analysis_count,
            "history_size": len(self.emotion_history),
            "last_analysis": self.emotion_history[-1] if self.emotion_history else None,
        }

    def export_emotion_patterns(self, filepath: str) -> bool:
        """감정 패턴 데이터 내보내기"""
        try:
            export_data = {
                "metadata": {
                    "version": self.version,
                    "export_time": datetime.now().isoformat(),
                    "total_analyses": self.analysis_count,
                },
                "emotion_history": self.emotion_history,
                "analysis_summary": self.get_analysis_summary(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 감정 패턴 데이터 내보내기 완료: {filepath}")
            return True

        except Exception as e:
            print(f"❌ 데이터 내보내기 실패: {e}")
            return False


def test_advanced_emotion_analyzer():
    """고도화 감정 분석기 테스트"""
    print("🧪 Advanced Emotion Analyzer 테스트 시작...")

    analyzer = AdvancedEmotionAnalyzer()

    test_cases = [
        {
            "text": "와! 정말 너무 행복해요!! 🎉✨ 오늘 완전 최고의 하루였어요!",
            "description": "고강도 기쁨 + 이모지",
        },
        {
            "text": "요즘 계속 우울하고... 힘들어요. 언제까지 이럴까요?",
            "description": "지속적 슬픔 + 불확실성",
        },
        {
            "text": "갑자기 화가 나네요!! 진짜 열받아요!",
            "description": "급작스러운 분노",
        },
        {
            "text": "그냥 평범한 하루였어요. 특별한 일은 없었고요.",
            "description": "중립적 상태",
        },
        {
            "text": "친구와 함께 있을 때는 좋은데, 혼자 있으면 외로워져요.",
            "description": "상황 의존적 감정",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n🔍 테스트 {i}: {case['description']}")
        print(f"📝 입력: '{case['text']}'")

        result = analyzer.analyze_emotion_advanced(case["text"])

        print(f"🎯 주요 감정: {result['primary']}")
        print(f"💪 강도: {result['intensity']:.3f}")
        print(f"⚖️ 안정성: {result['stability']:.3f}")
        print(f"🌍 상황 의존성: {result['context_dependency']:.3f}")
        print(f"⏰ 시간적 감쇠: {result['temporal_decay']:.3f}")
        print(f"🧩 복잡도: {result['complexity']:.3f}")
        print(f"⏱️ 처리 시간: {result['meta']['processing_time']:.4f}초")

    # 분석 요약
    summary = analyzer.get_analysis_summary()
    print(f"\n📊 분석 요약:")
    print(f"   총 분석 횟수: {summary['total_analyses']}")
    print(f"   히스토리 크기: {summary['history_size']}")

    print("\n🎉 Advanced Emotion Analyzer 테스트 완료!")


if __name__ == "__main__":
    test_advanced_emotion_analyzer()
