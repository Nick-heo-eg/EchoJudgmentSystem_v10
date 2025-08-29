#!/usr/bin/env python3
"""
🎯 Strategy Selector - 최적화된 전략 선택 시스템
상황별 최적 전략을 O(1)로 선택하는 룩업 테이블 기반 시스템
"""

from typing import Dict, List, Any
from functools import lru_cache

class OptimizedStrategySelector:
    """최적화된 전략 선택기"""
    
    def __init__(self):
        self.strategy_lookup = self._build_strategy_lookup()
        self.persona_strategies = self._build_persona_strategies()
        
    @lru_cache(maxsize=200)
    def select_strategy(self, emotion: str, intensity: float, persona_type: str,
                       intent: str = None) -> Dict[str, Any]:
        """
        빠른 전략 선택 (O(1) 룩업)
        
        Args:
            emotion: 감정 유형
            intensity: 감정 강도
            persona_type: 페르소나 타입
            intent: 사용자 의도 (선택사항)
            
        Returns:
            선택된 전략 정보
        """
        # 기본 전략 룩업
        base_strategy = self.strategy_lookup.get(emotion, "balanced")
        
        # 페르소나 특성 적용
        persona_strategies = self.persona_strategies.get(persona_type, [])
        
        # 고강도일 때 페르소나 전략 우선
        if intensity > 0.6 and persona_strategies:
            primary_strategy = persona_strategies[0]
        else:
            primary_strategy = base_strategy
            
        # 전략 신뢰도 계산
        confidence = self._calculate_confidence(emotion, intensity, persona_type)
        
        return {
            "primary_strategy": primary_strategy,
            "base_strategy": base_strategy, 
            "persona_influence": primary_strategy in persona_strategies,
            "confidence": confidence,
            "alternatives": self._get_alternative_strategies(emotion, persona_type),
            "intensity_adjusted": intensity > 0.6
        }
    
    def _build_strategy_lookup(self) -> Dict[str, str]:
        """감정-전략 룩업 테이블 구축"""
        return {
            "joy": "empathetic",
            "sadness": "supportive", 
            "anger": "cautious",
            "fear": "reassuring",
            "surprise": "exploratory",
            "neutral": "balanced"
        }
    
    def _build_persona_strategies(self) -> Dict[str, List[str]]:
        """페르소나별 전략 테이블"""
        return {
            "Echo-Aurora": ["empathetic", "nurturing", "optimistic"],
            "Echo-Phoenix": ["transformative", "resilient", "adaptive"],
            "Echo-Sage": ["analytical", "logical", "systematic"],
            "Echo-Companion": ["supportive", "loyal", "reliable"]
        }
    
    @lru_cache(maxsize=50)
    def _calculate_confidence(self, emotion: str, intensity: float, persona_type: str) -> float:
        """전략 선택 신뢰도 계산"""
        base_confidence = 0.7
        
        # 강도 기반 보정
        intensity_bonus = min(intensity * 0.3, 0.25)
        
        # 페르소나 매칭 보정
        persona_bonus = 0.1 if persona_type in self.persona_strategies else 0
        
        return min(base_confidence + intensity_bonus + persona_bonus, 1.0)
    
    def _get_alternative_strategies(self, emotion: str, persona_type: str) -> List[str]:
        """대안 전략 제안"""
        alternatives = []
        persona_strats = self.persona_strategies.get(persona_type, [])
        
        # 페르소나 전략 중 기본 전략이 아닌 것들
        base = self.strategy_lookup.get(emotion, "balanced")
        for strategy in persona_strats:
            if strategy != base:
                alternatives.append(strategy)
                
        return alternatives[:2]  # 상위 2개만

# 전역 인스턴스
_strategy_selector = OptimizedStrategySelector()

def select_strategy_fast(emotion: str, intensity: float, persona_type: str, 
                        intent: str = None) -> Dict[str, Any]:
    """빠른 전략 선택 (외부 인터페이스)"""
    return _strategy_selector.select_strategy(emotion, intensity, persona_type, intent)
