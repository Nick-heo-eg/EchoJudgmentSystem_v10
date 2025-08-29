# strategic_predictor.py

from .emotion_infer import EmotionInferenceResult


def predict_strategy(emotion_input) -> str:
    """
    감정 추론 결과를 기반으로 전략 시그니처 추론
    emotion_input: EmotionInferenceResult 또는 str
    """
    # 호환성을 위한 처리
    if isinstance(emotion_input, str):
        emotion = emotion_input
        intensity = 0.5  # medium intensity as float
        next_emotion = "neutral"
    else:
        # EmotionInferenceResult 객체인 경우
        emotion = emotion_input.primary_emotion
        intensity = emotion_input.emotional_intensity
        next_emotion = (
            emotion_input.predicted_next_emotions[0]
            if emotion_input.predicted_next_emotions
            else "neutral"
        )

    # 감정 + 강도 기반 전략 매핑
    strategy_matrix = {
        "joy": {"low": "소통 관망", "medium": "긍정적 확장", "high": "관계 몰입"},
        "sadness": {"low": "내면 성찰", "medium": "감정 보존", "high": "회피 및 차단"},
        "anger": {"low": "문제 제기", "medium": "직면 및 요구", "high": "공격적 투사"},
        "fear": {"low": "신중한 관찰", "medium": "위험 회피", "high": "도피 및 회피"},
        "surprise": {
            "low": "무시 또는 관망",
            "medium": "호기심 기반 탐색",
            "high": "직관적 반응",
        },
        "neutral": {"low": "상황 유지", "medium": "정보 수집", "high": "관망 후 대응"},
    }

    # 강도 구간화
    if intensity < 0.4:
        level = "low"
    elif intensity < 0.7:
        level = "medium"
    else:
        level = "high"

    return strategy_matrix.get(emotion, {}).get(level, "관망")
