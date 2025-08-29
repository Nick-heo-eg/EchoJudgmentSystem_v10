#!/usr/bin/env python3
"""
🧠 EchoJudgmentSystem v10.6 - Reinforcement Engine
판단⨯행동 결과에 대한 보상 기반 학습 모듈

TT.005: "모든 판단은 경험이 되고, 경험은 다음 판단의 지혜가 된다."

주요 기능:
- Q-table 기반 강화학습
- 판단 결과에 대한 보상/처벌 적용
- 전략 효과성 학습 및 업데이트
- 메타인지 피드백 루프 통합
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# EchoJudgmentSystem 모듈
try:
    from echo_engine.qtable_rl import QTableRL
except ImportError:
    QTableRL = None

try:
    from echo_engine.meta_logger import log_evolution_event
except ImportError:
    log_evolution_event = None

try:
    from echo_engine.persona_meta_logger import get_persona_meta_logger
except ImportError:
    get_persona_meta_logger = None


@dataclass
class ReinforcementAction:
    """강화학습 액션 정의"""

    strategy: str
    context_type: str
    emotion_state: str
    confidence: float
    timestamp: str

    def to_key(self) -> str:
        """Q-table 키 생성"""
        return f"{self.context_type}:{self.emotion_state}:{self.strategy}"


@dataclass
class ReinforcementFeedback:
    """강화학습 피드백 정의"""

    action_key: str
    reward: float
    success: bool
    user_satisfaction: float
    response_time: float
    learning_insight: str
    meta_reflection: Dict[str, Any]


class ReinforcementEngine:
    """
    EchoJudgmentSystem 강화학습 엔진

    판단 결과에 대한 보상 기반 학습을 통해
    시스템의 전략 선택 능력을 지속적으로 향상시킵니다.
    """

    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.9):
        """
        강화학습 엔진 초기화

        Args:
            learning_rate: 학습률 (0.0-1.0)
            discount_factor: 할인 인수 (0.0-1.0)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # Q-table 초기화
        self.q_table: Dict[str, float] = {}
        self.action_counts: Dict[str, int] = {}
        self.last_rewards: Dict[str, float] = {}

        # 학습 통계
        self.total_actions = 0
        self.successful_actions = 0
        self.learning_episodes = 0

        # 전략별 성과 추적
        self.strategy_performance: Dict[str, Dict[str, Any]] = {}

        # 설정 로드
        self.load_q_table()

        print("🧠 ReinforcementEngine 초기화 완료")

    def apply_reward(
        self, judgment_result: Dict[str, Any], feedback: Dict[str, Any]
    ) -> float:
        """
        판단 결과에 대한 보상 적용

        Args:
            judgment_result: 판단 결과 데이터
            feedback: 사용자/시스템 피드백

        Returns:
            적용된 보상 값
        """
        try:
            # 액션 정보 추출
            action = self._extract_action(judgment_result)

            # 보상 계산
            reward = self._calculate_reward(feedback)

            # Q-value 업데이트
            action_key = action.to_key()
            current_q = self.q_table.get(action_key, 0.0)

            # Q-learning 업데이트 공식: Q(s,a) = Q(s,a) + α[r + γmax(Q(s',a')) - Q(s,a)]
            new_q = current_q + self.learning_rate * (reward - current_q)
            self.q_table[action_key] = new_q

            # 통계 업데이트
            self.action_counts[action_key] = self.action_counts.get(action_key, 0) + 1
            self.last_rewards[action_key] = reward
            self.total_actions += 1

            if reward > 0:
                self.successful_actions += 1

            # 전략 성과 업데이트
            self._update_strategy_performance(action, reward, feedback)

            # 메타 로깅
            self._log_reinforcement_event(action, reward, feedback)

            # 주기적 Q-table 저장
            if self.total_actions % 10 == 0:
                self.save_q_table()

            print(f"🎯 보상 적용: {action_key} → {reward:.3f} (Q: {new_q:.3f})")
            return reward

        except Exception as e:
            print(f"❌ 보상 적용 실패: {e}")
            return 0.0

    def get_updated_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        학습된 Q-table을 기반으로 최적 전략 추천

        Args:
            context: 현재 상황 컨텍스트

        Returns:
            추천 전략 정보
        """
        try:
            context_type = context.get("context_type", "general")
            emotion_state = context.get("emotion_detected", "neutral")

            # 현재 상황에 적용 가능한 전략들 찾기
            available_strategies = self._get_available_strategies(
                context_type, emotion_state
            )

            if not available_strategies:
                # 기본 전략 반환
                return {
                    "strategy": "balanced",
                    "confidence": 0.5,
                    "reason": "No learned strategies available",
                    "q_value": 0.0,
                    "exploration": True,
                }

            # Q-value 기반 전략 선택 (ε-greedy)
            best_strategy = self._select_strategy_epsilon_greedy(
                available_strategies, context_type, emotion_state
            )

            action_key = f"{context_type}:{emotion_state}:{best_strategy}"
            q_value = self.q_table.get(action_key, 0.0)
            confidence = min(
                1.0, max(0.0, (q_value + 1.0) / 2.0)
            )  # Q-value를 confidence로 변환

            # 전략 성과 정보 추가
            performance_info = self.strategy_performance.get(best_strategy, {})

            return {
                "strategy": best_strategy,
                "confidence": confidence,
                "reason": f"Q-learning 기반 선택 (Q={q_value:.3f})",
                "q_value": q_value,
                "exploration": False,
                "action_count": self.action_counts.get(action_key, 0),
                "last_reward": self.last_rewards.get(action_key, 0.0),
                "performance_info": performance_info,
            }

        except Exception as e:
            print(f"❌ 전략 업데이트 실패: {e}")
            return {
                "strategy": "balanced",
                "confidence": 0.3,
                "reason": f"Error in strategy selection: {e}",
                "q_value": 0.0,
                "exploration": True,
            }

    def _extract_action(self, judgment_result: Dict[str, Any]) -> ReinforcementAction:
        """판단 결과에서 액션 정보 추출"""
        return ReinforcementAction(
            strategy=judgment_result.get("strategy_selected", "balanced"),
            context_type=judgment_result.get("context_type", "general"),
            emotion_state=judgment_result.get("emotion_detected", "neutral"),
            confidence=judgment_result.get("confidence", 0.5),
            timestamp=datetime.now().isoformat(),
        )

    def _calculate_reward(self, feedback: Dict[str, Any]) -> float:
        """피드백을 기반으로 보상 계산"""
        reward = 0.0

        # 성공/실패 기본 보상
        if feedback.get("success", False):
            reward += 0.5
        else:
            reward -= 0.3

        # 사용자 만족도 보상
        user_satisfaction = feedback.get("user_satisfaction", 0.5)
        reward += (user_satisfaction - 0.5) * 0.4

        # 효과성 점수 보상
        effectiveness = feedback.get("effectiveness_score", 0.5)
        reward += (effectiveness - 0.5) * 0.3

        # 응답 시간 보상 (빠를수록 좋음)
        response_time = feedback.get("response_time", 1.0)
        if response_time < 0.5:
            reward += 0.1
        elif response_time > 2.0:
            reward -= 0.1

        # 메타인지 품질 보상
        meta_quality = feedback.get("meta_quality", 0.5)
        reward += (meta_quality - 0.5) * 0.2

        return max(-1.0, min(1.0, reward))  # -1.0 ~ 1.0 범위로 제한

    def _get_available_strategies(
        self, context_type: str, emotion_state: str
    ) -> List[str]:
        """현재 상황에서 사용 가능한 전략 목록 반환"""
        # 기본 전략 목록
        base_strategies = [
            "empathetic",
            "analytical",
            "creative",
            "supportive",
            "logical",
            "intuitive",
            "collaborative",
            "adaptive",
        ]

        # 컨텍스트별 특화 전략
        context_strategies = {
            "emotional": ["empathetic", "supportive", "intuitive"],
            "analytical": ["logical", "analytical", "systematic"],
            "creative": ["creative", "intuitive", "adaptive"],
            "collaborative": ["collaborative", "supportive", "empathetic"],
            "crisis": ["adaptive", "logical", "supportive"],
        }

        # 감정별 적합 전략
        emotion_strategies = {
            "joy": ["empathetic", "creative", "collaborative"],
            "sadness": ["supportive", "empathetic", "intuitive"],
            "anger": ["analytical", "logical", "adaptive"],
            "fear": ["supportive", "logical", "empathetic"],
            "neutral": base_strategies,
        }

        # 상황에 맞는 전략 조합
        available = set(base_strategies)

        if context_type in context_strategies:
            available.update(context_strategies[context_type])

        if emotion_state in emotion_strategies:
            available.update(emotion_strategies[emotion_state])

        return list(available)

    def _select_strategy_epsilon_greedy(
        self,
        strategies: List[str],
        context_type: str,
        emotion_state: str,
        epsilon: float = 0.1,
    ) -> str:
        """ε-greedy 알고리즘으로 전략 선택"""
        # Exploration vs Exploitation
        if np.random.random() < epsilon:
            # 탐험: 랜덤 선택
            return np.random.choice(strategies)
        else:
            # 활용: Q-value가 가장 높은 전략 선택
            best_strategy = strategies[0]
            best_q_value = float("-inf")

            for strategy in strategies:
                action_key = f"{context_type}:{emotion_state}:{strategy}"
                q_value = self.q_table.get(action_key, 0.0)

                if q_value > best_q_value:
                    best_q_value = q_value
                    best_strategy = strategy

            return best_strategy

    def _update_strategy_performance(
        self, action: ReinforcementAction, reward: float, feedback: Dict[str, Any]
    ):
        """전략별 성과 통계 업데이트"""
        strategy = action.strategy

        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {
                "total_uses": 0,
                "successful_uses": 0,
                "total_reward": 0.0,
                "average_reward": 0.0,
                "best_reward": float("-inf"),
                "worst_reward": float("inf"),
                "last_used": None,
                "contexts": set(),
                "emotions": set(),
            }

        perf = self.strategy_performance[strategy]
        perf["total_uses"] += 1
        perf["total_reward"] += reward
        perf["average_reward"] = perf["total_reward"] / perf["total_uses"]
        perf["last_used"] = action.timestamp
        perf["contexts"].add(action.context_type)
        perf["emotions"].add(action.emotion_state)

        if reward > 0:
            perf["successful_uses"] += 1

        if reward > perf["best_reward"]:
            perf["best_reward"] = reward

        if reward < perf["worst_reward"]:
            perf["worst_reward"] = reward

    def _log_reinforcement_event(
        self, action: ReinforcementAction, reward: float, feedback: Dict[str, Any]
    ):
        """강화학습 이벤트 로깅"""
        try:
            # 진화 이벤트 로깅
            if log_evolution_event:
                event_data = {
                    "event": "Reinforcement Learning Update",
                    "tag": ["reinforcement", "q_learning", "strategy_optimization"],
                    "cause": [
                        f"action_{action.strategy}",
                        f"context_{action.context_type}",
                    ],
                    "effect": [f"reward_{reward:.3f}", "q_table_update"],
                    "resolution": f"strategy_confidence_updated",
                    "insight": f"Q-learning adaptation for {action.strategy}",
                    "adaptation_strength": abs(reward),
                    "coherence_improvement": max(0, reward),
                    "reflection_depth": 1,
                }
                log_evolution_event(event_data, f"reinforcement_{action.strategy}")

            # 페르소나 메타 로거 연동
            if get_persona_meta_logger:
                meta_logger = get_persona_meta_logger()
                meta_logger.log_flow_transition(
                    {
                        "event_type": "reinforcement_learning",
                        "action": asdict(action),
                        "reward": reward,
                        "feedback": feedback,
                        "q_table_size": len(self.q_table),
                        "learning_stats": {
                            "total_actions": self.total_actions,
                            "success_rate": self.successful_actions
                            / max(1, self.total_actions),
                        },
                    }
                )

        except Exception as e:
            print(f"⚠️ 강화학습 이벤트 로깅 실패: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 반환"""
        success_rate = self.successful_actions / max(1, self.total_actions)

        # Q-table 통계
        q_values = list(self.q_table.values())
        avg_q = np.mean(q_values) if q_values else 0.0
        max_q = np.max(q_values) if q_values else 0.0
        min_q = np.min(q_values) if q_values else 0.0

        # 최고 성과 전략들
        top_strategies = sorted(
            self.strategy_performance.items(),
            key=lambda x: x[1]["average_reward"],
            reverse=True,
        )[:5]

        return {
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "success_rate": success_rate,
            "q_table_size": len(self.q_table),
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "q_statistics": {
                "average": avg_q,
                "maximum": max_q,
                "minimum": min_q,
                "std_dev": np.std(q_values) if q_values else 0.0,
            },
            "top_strategies": [
                {
                    "strategy": name,
                    "average_reward": perf["average_reward"],
                    "success_rate": perf["successful_uses"]
                    / max(1, perf["total_uses"]),
                    "total_uses": perf["total_uses"],
                }
                for name, perf in top_strategies
            ],
        }

    def save_q_table(self, filepath: str = "data/reinforcement_q_table.json"):
        """Q-table 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            save_data = {
                "q_table": self.q_table,
                "action_counts": self.action_counts,
                "last_rewards": self.last_rewards,
                "learning_stats": {
                    "total_actions": self.total_actions,
                    "successful_actions": self.successful_actions,
                    "learning_rate": self.learning_rate,
                    "discount_factor": self.discount_factor,
                },
                "strategy_performance": {
                    k: {
                        **v,
                        "contexts": list(v["contexts"]),
                        "emotions": list(v["emotions"]),
                    }
                    for k, v in self.strategy_performance.items()
                },
                "last_updated": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Q-table 저장 완료: {filepath}")

        except Exception as e:
            print(f"❌ Q-table 저장 실패: {e}")

    def load_q_table(self, filepath: str = "data/reinforcement_q_table.json"):
        """Q-table 로드"""
        try:
            if not os.path.exists(filepath):
                print(f"📁 Q-table 파일 없음, 새로 시작: {filepath}")
                return

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.q_table = data.get("q_table", {})
            self.action_counts = data.get("action_counts", {})
            self.last_rewards = data.get("last_rewards", {})

            stats = data.get("learning_stats", {})
            self.total_actions = stats.get("total_actions", 0)
            self.successful_actions = stats.get("successful_actions", 0)

            # 전략 성과 데이터 로드 (set 복원)
            perf_data = data.get("strategy_performance", {})
            for strategy, perf in perf_data.items():
                perf["contexts"] = set(perf.get("contexts", []))
                perf["emotions"] = set(perf.get("emotions", []))
            self.strategy_performance = perf_data

            print(f"📂 Q-table 로드 완료: {len(self.q_table)}개 상태-액션 쌍")

        except Exception as e:
            print(f"❌ Q-table 로드 실패: {e}")

    def reset_learning(self):
        """학습 데이터 초기화"""
        self.q_table.clear()
        self.action_counts.clear()
        self.last_rewards.clear()
        self.strategy_performance.clear()
        self.total_actions = 0
        self.successful_actions = 0
        self.learning_episodes = 0

        print("🔄 강화학습 데이터 초기화 완료")


# 글로벌 인스턴스
_reinforcement_engine = None


def get_reinforcement_engine() -> ReinforcementEngine:
    """글로벌 강화학습 엔진 인스턴스 반환"""
    global _reinforcement_engine
    if _reinforcement_engine is None:
        _reinforcement_engine = ReinforcementEngine()
    return _reinforcement_engine


def apply_judgment_reward(
    judgment_result: Dict[str, Any], feedback: Dict[str, Any]
) -> float:
    """편의 함수: 판단 결과에 보상 적용"""
    engine = get_reinforcement_engine()
    return engine.apply_reward(judgment_result, feedback)


def get_optimal_strategy(context: Dict[str, Any]) -> Dict[str, Any]:
    """편의 함수: 최적 전략 추천"""
    engine = get_reinforcement_engine()
    return engine.get_updated_strategy(context)
