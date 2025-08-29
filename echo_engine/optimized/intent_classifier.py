#!/usr/bin/env python3
"""
🎯 Intent Classifier - 최적화된 의도 분류 시스템  
사전 훈련된 패턴으로 O(1) 의도 추론
"""

import re
from enum import Enum
from typing import Dict, List
from functools import lru_cache

class IntentType(Enum):
    """사용자 의도 유형"""
    ACHIEVEMENT_SEEKING = "achievement_seeking"
    AVOIDANCE_MOTIVE = "avoidance_motive"  
    SOCIAL_CONNECTION = "social_connection"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL_SUPPORT = "emotional_support"
    INFORMATION_SEEKING = "information_seeking"
    CREATIVE_EXPRESSION = "creative_expression"
    RELATIONSHIP_BUILDING = "relationship_building"
    SELF_REFLECTION = "self_reflection"
    DECISION_MAKING = "decision_making"

class OptimizedIntentClassifier:
    """최적화된 의도 분류기"""
    
    def __init__(self):
        self.intent_patterns = self._compile_intent_patterns()
        
    @lru_cache(maxsize=500)
    def classify_intent(self, text: str, persona_type: str = "default") -> Dict[str, any]:
        """
        빠른 의도 분류 (O(1) 복잡도)
        
        Args:
            text: 분석할 텍스트
            persona_type: 페르소나 타입별 가중치
            
        Returns:
            의도 분류 결과
        """
        text_lower = text.lower()
        
        intent_scores = {}
        for intent, pattern in self.intent_patterns.items():
            matches = len(pattern.findall(text_lower))
            if matches > 0:
                weight = self._get_persona_weight(intent, persona_type)
                intent_scores[intent] = matches * weight
                
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / 3.0, 1.0)
        else:
            primary_intent = IntentType.INFORMATION_SEEKING.value
            confidence = 0.3
            
        return {
            "primary_intent": primary_intent,
            "confidence": confidence,
            "all_scores": intent_scores,
            "alternatives": self._get_alternatives(intent_scores, primary_intent)
        }
    
    def _compile_intent_patterns(self) -> Dict[str, re.Pattern]:
        """의도 패턴 사전 컴파일"""
        patterns = {
            IntentType.ACHIEVEMENT_SEEKING.value: [
                "성공", "달성", "목표", "성취", "이루고", "해내고", "완수", "승리"
            ],
            IntentType.PROBLEM_SOLVING.value: [
                "해결", "문제", "방법", "어떻게", "해결책", "풀어", "극복", "해법"
            ],
            IntentType.EMOTIONAL_SUPPORT.value: [
                "힘들", "우울", "슬프", "외로", "지쳐", "위로", "공감", "이해"
            ],
            IntentType.INFORMATION_SEEKING.value: [
                "알고 싶", "궁금", "정보", "알려줘", "설명", "가르쳐", "배우고"
            ]
        }
        
        compiled = {}
        for intent, keywords in patterns.items():
            pattern = '|'.join(re.escape(keyword) for keyword in keywords)  
            compiled[intent] = re.compile(pattern)
            
        return compiled
    
    @lru_cache(maxsize=50)
    def _get_persona_weight(self, intent: str, persona_type: str) -> float:
        """페르소나별 의도 가중치"""
        weights = {
            "Echo-Aurora": {
                IntentType.EMOTIONAL_SUPPORT.value: 1.5,
                IntentType.SOCIAL_CONNECTION.value: 1.3,
            },
            "Echo-Phoenix": {
                IntentType.ACHIEVEMENT_SEEKING.value: 1.5,
                IntentType.PROBLEM_SOLVING.value: 1.3,
            },
            "Echo-Sage": {
                IntentType.INFORMATION_SEEKING.value: 1.5,
                IntentType.DECISION_MAKING.value: 1.4,
            }
        }
        
        return weights.get(persona_type, {}).get(intent, 1.0)
    
    def _get_alternatives(self, scores: Dict, primary: str) -> List[str]:
        """대안 의도 제안"""
        alternatives = []
        for intent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:4]:
            if intent != primary and score > 0.3:
                alternatives.append(intent)
        return alternatives

# 전역 인스턴스
_intent_classifier = OptimizedIntentClassifier()

def classify_intent_fast(text: str, persona_type: str = "default") -> Dict[str, any]:
    """빠른 의도 분류 (외부 인터페이스)"""
    return _intent_classifier.classify_intent(text, persona_type)
