#!/usr/bin/env python3
"""
🧠 Memory Manager - 최적화된 메모리 관리 시스템
효율적인 상호작용 기억 및 패턴 학습
"""

import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Deque

@dataclass 
class OptimizedPersonaMemory:
    """최적화된 페르소나 메모리"""
    
    # 고정 크기 큐로 메모리 효율성 확보
    recent_interactions: Deque = field(default_factory=lambda: deque(maxlen=20))
    emotional_patterns: Dict[str, Deque] = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=10)))
    strategy_success_counts: Dict[str, int] = field(default_factory=dict)
    strategy_effectiveness: Dict[str, Deque] = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=10)))
    
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """상호작용 기록 (O(1) 복잡도)"""
        interaction["timestamp"] = time.time()  # float가 datetime보다 빠름
        self.recent_interactions.append(interaction)
    
    def track_emotion(self, emotion: str, intensity: float) -> None:
        """감정 패턴 추적 (O(1) 복잡도)"""
        self.emotional_patterns[emotion].append(intensity)
    
    def update_strategy_success(self, strategy: str, success: bool) -> None:
        """전략 성공률 업데이트 (O(1) 복잡도)"""
        if strategy not in self.strategy_success_counts:
            self.strategy_success_counts[strategy] = 0
            
        if success:
            self.strategy_success_counts[strategy] += 1
        else:
            self.strategy_success_counts[strategy] = max(0, self.strategy_success_counts[strategy] - 1)
    
    def add_strategy_feedback(self, strategy: str, effectiveness: float) -> None:
        """전략 효과성 피드백 (O(1) 복잡도)"""
        self.strategy_effectiveness[strategy].append(effectiveness)
    
    def get_strategy_effectiveness(self, strategy: str) -> float:
        """전략 효과성 평균 (캐시됨)"""
        effectiveness_scores = self.strategy_effectiveness.get(strategy)
        if effectiveness_scores:
            return sum(effectiveness_scores) / len(effectiveness_scores)
        return 0.5
    
    def get_emotion_average(self, emotion: str) -> float:
        """감정 평균 강도"""
        pattern = self.emotional_patterns.get(emotion)
        if pattern:
            return sum(pattern) / len(pattern)
        return 0.0
    
    def get_recent_emotions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """최근 감정 패턴"""
        emotions = []
        for interaction in list(self.recent_interactions)[-limit:]:
            if "emotion_detected" in interaction:
                emotions.append({
                    "emotion": interaction["emotion_detected"],
                    "intensity": interaction.get("emotion_intensity", 0.0),
                    "timestamp": interaction.get("timestamp", 0)
                })
        return emotions
    
    def get_best_strategies(self, top_k: int = 3) -> List[tuple]:
        """가장 성공적인 전략들"""
        return sorted(
            self.strategy_success_counts.items(),
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
    
    def cleanup_old_data(self, max_age_seconds: int = 86400) -> None:
        """오래된 데이터 정리 (24시간 이상)"""
        current_time = time.time()
        cutoff_time = current_time - max_age_seconds
        
        # 오래된 상호작용 제거  
        while (self.recent_interactions and 
               self.recent_interactions[0].get("timestamp", 0) < cutoff_time):
            self.recent_interactions.popleft()

class OptimizedMemoryManager:
    """최적화된 메모리 관리자"""
    
    def __init__(self):
        self.memory = OptimizedPersonaMemory()
        self._last_cleanup = time.time()
        
    def record_interaction(self, emotion: str, intensity: float, strategy: str,
                          success: bool, effectiveness: float = None) -> None:
        """상호작용 종합 기록"""
        # 모든 업데이트를 한 번에 처리 (효율성)
        interaction = {
            "emotion": emotion,
            "intensity": intensity,
            "strategy": strategy,
            "success": success,
            "effectiveness": effectiveness or (1.0 if success else 0.0)
        }
        
        self.memory.add_interaction(interaction)
        self.memory.track_emotion(emotion, intensity)
        self.memory.update_strategy_success(strategy, success)
        
        if effectiveness:
            self.memory.add_strategy_feedback(strategy, effectiveness)
            
        # 주기적 청소 (1시간마다)
        if time.time() - self._last_cleanup > 3600:
            self.memory.cleanup_old_data()
            self._last_cleanup = time.time()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """학습 인사이트 생성"""
        return {
            "best_strategies": self.memory.get_best_strategies(),
            "recent_emotions": self.memory.get_recent_emotions(),
            "interaction_count": len(self.memory.recent_interactions),
            "emotional_stability": self._calculate_emotional_stability(),
            "strategy_diversity": len(self.memory.strategy_success_counts)
        }
    
    def _calculate_emotional_stability(self) -> float:
        """감정 안정성 계산"""
        recent_emotions = self.memory.get_recent_emotions()
        if len(recent_emotions) < 2:
            return 0.5
            
        intensities = [e["intensity"] for e in recent_emotions]
        variance = sum((x - sum(intensities)/len(intensities))**2 for x in intensities) / len(intensities)
        
        # 낮은 분산 = 높은 안정성
        return max(0.0, min(1.0, 1.0 - variance))

# 전역 인스턴스
_memory_manager = OptimizedMemoryManager()

def record_interaction_fast(emotion: str, intensity: float, strategy: str,
                           success: bool, effectiveness: float = None) -> None:
    """빠른 상호작용 기록 (외부 인터페이스)"""
    _memory_manager.record_interaction(emotion, intensity, strategy, success, effectiveness)

def get_learning_insights_fast() -> Dict[str, Any]:
    """빠른 학습 인사이트 (외부 인터페이스)"""
    return _memory_manager.get_learning_insights()
