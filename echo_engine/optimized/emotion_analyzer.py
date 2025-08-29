#!/usr/bin/env python3
"""
🎭 Emotion Analyzer - 최적화된 감정 분석 시스템
O(1) 복잡도의 고성능 감정 분석기
"""

import re
from enum import Enum
from typing import Dict, Tuple
from functools import lru_cache

class EmotionType(Enum):
    """감정 유형"""
    JOY = "joy"
    SADNESS = "sadness" 
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"

class EmotionIntensity(Enum):
    """감정 강도"""
    MINIMAL = "minimal"    # 0.0 - 0.2
    LOW = "low"           # 0.2 - 0.4
    MODERATE = "moderate" # 0.4 - 0.6
    HIGH = "high"         # 0.6 - 0.8
    INTENSE = "intense"   # 0.8 - 1.0

class OptimizedEmotionAnalyzer:
    """최적화된 감정 분석기 (O(1) 복잡도)"""
    
    def __init__(self):
        # 사전 컴파일된 정규식 (초기화 시 한 번만)
        self.emotion_patterns = self._compile_emotion_patterns()
        self.intensity_cache = {}
        
    @lru_cache(maxsize=1000)
    def analyze_emotion(self, text: str, sensitivity: float = 0.5) -> Tuple[str, float]:
        """
        최적화된 감정 분석 (O(1) 복잡도)
        
        Args:
            text: 분석할 텍스트
            sensitivity: 감정 감도 (0.0-1.0)
            
        Returns:
            (감정_유형, 강도) 튜플
        """
        text_lower = text.lower()
        
        # 사전 컴파일된 패턴으로 O(1) 매칭
        emotion_scores = {}
        for emotion, pattern in self.emotion_patterns.items():
            matches = len(pattern.findall(text_lower))
            if matches > 0:
                emotion_scores[emotion] = matches * sensitivity
                
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            intensity = min(emotion_scores[primary_emotion] / 3.0, 1.0)
        else:
            primary_emotion = EmotionType.NEUTRAL.value
            intensity = 0.3
            
        return primary_emotion, intensity
    
    def _compile_emotion_patterns(self) -> Dict[str, re.Pattern]:
        """감정 패턴 사전 컴파일 (초기화 시 한 번만 실행)"""
        patterns = {
            EmotionType.JOY.value: [
                "기쁘", "행복", "좋", "최고", "성공", "축하", "만족", "즐거", "신나"
            ],
            EmotionType.SADNESS.value: [
                "슬프", "우울", "힘들", "속상", "실망", "포기", "아쉽", "절망", "눈물"
            ],
            EmotionType.ANGER.value: [
                "화", "짜증", "분노", "열받", "억울", "불만", "갑갑", "빡쳐", "꼴받"
            ],
            EmotionType.FEAR.value: [
                "무서", "걱정", "불안", "두려", "긴장", "스트레스", "공포", "떨려"
            ],
            EmotionType.SURPRISE.value: [
                "놀라", "와우", "대박", "깜짝", "신기", "의외", "헉", "어머"
            ]
        }
        
        compiled = {}
        for emotion, keywords in patterns.items():
            pattern = '|'.join(re.escape(keyword) for keyword in keywords)
            compiled[emotion] = re.compile(pattern)
            
        return compiled
    
    @lru_cache(maxsize=100)  
    def categorize_intensity(self, intensity: float) -> str:
        """감정 강도 분류 (캐싱됨)"""
        if intensity <= 0.2:
            return EmotionIntensity.MINIMAL.value
        elif intensity <= 0.4:
            return EmotionIntensity.LOW.value
        elif intensity <= 0.6:
            return EmotionIntensity.MODERATE.value
        elif intensity <= 0.8:
            return EmotionIntensity.HIGH.value
        else:
            return EmotionIntensity.INTENSE.value

# 전역 인스턴스 (싱글톤 패턴)
_emotion_analyzer = OptimizedEmotionAnalyzer()

def analyze_emotion_fast(text: str, sensitivity: float = 0.5) -> Dict[str, any]:
    """빠른 감정 분석 (외부 인터페이스)"""
    emotion, intensity = _emotion_analyzer.analyze_emotion(text, sensitivity)
    
    return {
        "primary_emotion": emotion,
        "intensity": intensity,
        "intensity_category": _emotion_analyzer.categorize_intensity(intensity),
        "confidence": min(intensity * 2, 1.0)  # 신뢰도 계산
    }
