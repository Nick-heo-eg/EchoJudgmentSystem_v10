#!/usr/bin/env python3
"""
🎯 EchoJudgmentSystem v10.5 - Q-Table Strategy Selector
Q-Table 기반 행동 선택 및 학습 시스템

Q-Table은 다음 기능을 제공합니다:
- 상황-행동 조합에 대한 Q-값 학습
- 판단 결과 피드백 기반 강화학습
- 전략 선택 최적화
- 경험 리플레이 및 탐험/활용 균형
"""

import json
import time
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import os

# 수학 연산용
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class ActionType(Enum):
    """행동 유형"""

    JUDGMENT = "judgment"
    STRATEGY = "strategy"
    EMOTION_RESPONSE = "emotion_response"
    META_REFLECTION = "meta_reflection"
    LEARNING = "learning"


class ExplorationStrategy(Enum):
    """탐험 전략"""

    EPSILON_GREEDY = "epsilon_greedy"
    UCB = "ucb"  # Upper Confidence Bound
    THOMPSON_SAMPLING = "thompson_sampling"
    SOFTMAX = "softmax"


@dataclass
class QState:
    """Q-Table 상태 표현"""

    emotion: str
    emotion_intensity: str  # minimal, low, moderate, high, intense
    context_type: str
    urgency: str
    energy_level: str  # low, medium, high
    recent_success: str  # low, medium, high

    def to_key(self) -> str:
        """상태를 키 문자열로 변환"""
        return f"{self.emotion}_{self.emotion_intensity}_{self.context_type}_{self.urgency}_{self.energy_level}_{self.recent_success}"

    @classmethod
    def from_context(cls, context: Dict[str, Any]) -> "QState":
        """컨텍스트로부터 상태 생성"""
        return cls(
            emotion=context.get("emotion", "neutral"),
            emotion_intensity=cls._categorize_intensity(
                context.get("emotion_intensity", 0.5)
            ),
            context_type=context.get("context_type", "general"),
            urgency=context.get("urgency", "normal"),
            energy_level=cls._categorize_energy(context.get("energy_level", 0.7)),
            recent_success=cls._categorize_success(
                context.get("recent_success_rate", 0.5)
            ),
        )

    @staticmethod
    def _categorize_intensity(intensity: float) -> str:
        """감정 강도 분류"""
        if intensity <= 0.2:
            return "minimal"
        elif intensity <= 0.4:
            return "low"
        elif intensity <= 0.6:
            return "moderate"
        elif intensity <= 0.8:
            return "high"
        else:
            return "intense"

    @staticmethod
    def _categorize_energy(energy: float) -> str:
        """에너지 수준 분류"""
        if energy <= 0.3:
            return "low"
        elif energy <= 0.7:
            return "medium"
        else:
            return "high"

    @staticmethod
    def _categorize_success(success_rate: float) -> str:
        """성공률 분류"""
        if success_rate <= 0.3:
            return "low"
        elif success_rate <= 0.7:
            return "medium"
        else:
            return "high"


@dataclass
class QAction:
    """Q-Table 행동 표현"""

    action_type: ActionType
    strategy: str
    intensity: float = 0.5
    meta_params: Dict[str, Any] = field(default_factory=dict)

    def to_key(self) -> str:
        """행동을 키 문자열로 변환"""
        intensity_cat = (
            "low"
            if self.intensity < 0.3
            else "high" if self.intensity > 0.7 else "medium"
        )
        return f"{self.action_type.value}_{self.strategy}_{intensity_cat}"


@dataclass
class QExperience:
    """Q-Learning 경험"""

    state: QState
    action: QAction
    reward: float
    next_state: QState
    done: bool
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "state_key": self.state.to_key(),
            "action_key": self.action.to_key(),
            "reward": self.reward,
            "next_state_key": self.next_state.to_key(),
            "done": self.done,
            "timestamp": self.timestamp.isoformat(),
        }


class QTableStrategySelector:
    """Q-Table 기반 전략 선택기"""

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.1,
        exploration_decay: float = 0.995,
        min_exploration_rate: float = 0.01,
        exploration_strategy: ExplorationStrategy = ExplorationStrategy.EPSILON_GREEDY,
    ):
        """
        Q-Table 전략 선택기 초기화

        Args:
            learning_rate: 학습률 (α)
            discount_factor: 할인 인수 (γ)
            exploration_rate: 탐험율 (ε)
            exploration_decay: 탐험율 감소율
            min_exploration_rate: 최소 탐험율
            exploration_strategy: 탐험 전략
        """
        # Q-Learning 파라미터
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        self.exploration_strategy = exploration_strategy

        # Q-Table 및 데이터 구조
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.state_visit_count: Dict[str, int] = defaultdict(int)
        self.action_count: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # 경험 리플레이
        self.experience_buffer = deque(maxlen=10000)
        self.batch_size = 32

        # 성능 통계
        self.total_actions = 0
        self.successful_actions = 0
        self.total_rewards = 0.0
        self.episode_count = 0

        # 가능한 행동들 초기화
        self.available_actions = self._initialize_actions()

        # 온라인 학습 설정
        self.online_learning = True
        self.update_frequency = 10

        print(f"🎯 Q-Table 전략 선택기 초기화 완료")
        print(f"   학습률: {learning_rate}, 할인인수: {discount_factor}")
        print(f"   탐험율: {exploration_rate}, 탐험 전략: {exploration_strategy.value}")

    def _initialize_actions(self) -> List[QAction]:
        """가능한 행동들 초기화"""
        actions = []

        # 기본 전략들
        base_strategies = [
            "empathetic",
            "analytical",
            "supportive",
            "cautious",
            "creative",
            "balanced",
            "assertive",
            "collaborative",
        ]

        # 각 전략에 대해 다양한 강도로 행동 생성
        for strategy in base_strategies:
            for intensity in [0.3, 0.5, 0.8]:
                # 판단 행동
                actions.append(
                    QAction(
                        action_type=ActionType.JUDGMENT,
                        strategy=strategy,
                        intensity=intensity,
                    )
                )

                # 전략 행동
                actions.append(
                    QAction(
                        action_type=ActionType.STRATEGY,
                        strategy=strategy,
                        intensity=intensity,
                    )
                )

        # 특수 행동들
        special_actions = [
            QAction(ActionType.META_REFLECTION, "self_analysis", 0.7),
            QAction(ActionType.META_REFLECTION, "pattern_recognition", 0.6),
            QAction(ActionType.LEARNING, "experience_consolidation", 0.5),
            QAction(ActionType.LEARNING, "strategy_adaptation", 0.8),
        ]

        actions.extend(special_actions)

        print(f"🎯 가능한 행동 {len(actions)}개 초기화 완료")
        return actions

    def select_action(
        self, state: QState, available_strategies: List[str] = None
    ) -> QAction:
        """
        현재 상태에서 최적 행동 선택

        Args:
            state: 현재 상태
            available_strategies: 사용 가능한 전략 목록

        Returns:
            선택된 행동
        """
        state_key = state.to_key()
        self.state_visit_count[state_key] += 1

        # 사용 가능한 행동 필터링
        if available_strategies:
            filtered_actions = [
                action
                for action in self.available_actions
                if action.strategy in available_strategies
                or action.action_type
                in [ActionType.META_REFLECTION, ActionType.LEARNING]
            ]
        else:
            filtered_actions = self.available_actions

        # 탐험 vs 활용 결정
        if self._should_explore():
            action = self._explore_action(state, filtered_actions)
        else:
            action = self._exploit_action(state, filtered_actions)

        # 행동 카운트 업데이트
        action_key = action.to_key()
        self.action_count[state_key][action_key] += 1
        self.total_actions += 1

        return action

    def _should_explore(self) -> bool:
        """탐험 여부 결정"""
        if self.exploration_strategy == ExplorationStrategy.EPSILON_GREEDY:
            return random.random() < self.exploration_rate
        elif self.exploration_strategy == ExplorationStrategy.UCB:
            return False  # UCB는 자체적으로 탐험/활용 균형
        else:
            return random.random() < self.exploration_rate

    def _explore_action(self, state: QState, actions: List[QAction]) -> QAction:
        """탐험적 행동 선택"""
        if self.exploration_strategy == ExplorationStrategy.EPSILON_GREEDY:
            return random.choice(actions)
        elif self.exploration_strategy == ExplorationStrategy.SOFTMAX:
            return self._softmax_selection(state, actions)
        else:
            return random.choice(actions)

    def _exploit_action(self, state: QState, actions: List[QAction]) -> QAction:
        """활용적 행동 선택 (Q값이 최대인 행동)"""
        state_key = state.to_key()

        if self.exploration_strategy == ExplorationStrategy.UCB:
            return self._ucb_selection(state, actions)

        best_action = None
        best_q_value = float("-inf")

        for action in actions:
            action_key = action.to_key()
            q_value = self.q_table[state_key][action_key]

            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action

        # 모든 Q값이 동일하면 랜덤 선택
        if best_action is None or best_q_value == 0:
            best_action = random.choice(actions)

        return best_action

    def _ucb_selection(self, state: QState, actions: List[QAction]) -> QAction:
        """Upper Confidence Bound 선택"""
        state_key = state.to_key()
        total_visits = self.state_visit_count[state_key]

        if total_visits == 0:
            return random.choice(actions)

        best_action = None
        best_ucb_value = float("-inf")

        for action in actions:
            action_key = action.to_key()
            q_value = self.q_table[state_key][action_key]
            action_visits = self.action_count[state_key][action_key]

            if action_visits == 0:
                ucb_value = float("inf")  # 한 번도 시도하지 않은 행동 우선
            else:
                if NUMPY_AVAILABLE:
                    confidence = np.sqrt(2 * np.log(total_visits) / action_visits)
                else:
                    confidence = math.sqrt(2 * math.log(total_visits) / action_visits)
                ucb_value = q_value + confidence

            if ucb_value > best_ucb_value:
                best_ucb_value = ucb_value
                best_action = action

        return best_action or random.choice(actions)

    def _softmax_selection(
        self, state: QState, actions: List[QAction], temperature: float = 1.0
    ) -> QAction:
        """Softmax 확률적 선택"""
        state_key = state.to_key()
        q_values = []

        for action in actions:
            action_key = action.to_key()
            q_value = self.q_table[state_key][action_key]
            q_values.append(q_value / temperature)

        if NUMPY_AVAILABLE:
            # 수치적 안정성을 위한 정규화
            q_values = np.array(q_values)
            q_values = q_values - np.max(q_values)
            probabilities = np.exp(q_values) / np.sum(np.exp(q_values))

            # 확률적 선택
            chosen_idx = np.random.choice(len(actions), p=probabilities)
            return actions[chosen_idx]
        else:
            # numpy 없이 간단한 softmax
            max_q = max(q_values)
            if NUMPY_AVAILABLE:
                exp_values = [np.exp(q - max_q) for q in q_values]
            else:
                exp_values = [math.exp(q - max_q) for q in q_values]
            sum_exp = sum(exp_values)
            probabilities = [exp_val / sum_exp for exp_val in exp_values]

            # 확률적 선택 (단순 구현)
            rand_val = random.random()
            cumulative = 0.0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if rand_val <= cumulative:
                    return actions[i]

            return actions[-1]  # 폴백

    def update_q_value(
        self,
        state: QState,
        action: QAction,
        reward: float,
        next_state: QState,
        done: bool = False,
    ):
        """
        Q-값 업데이트 (Q-Learning)

        Args:
            state: 현재 상태
            action: 수행한 행동
            reward: 받은 보상
            next_state: 다음 상태
            done: 에피소드 종료 여부
        """
        state_key = state.to_key()
        action_key = action.to_key()
        next_state_key = next_state.to_key()

        # 현재 Q값
        current_q = self.q_table[state_key][action_key]

        # 다음 상태에서의 최대 Q값
        if done:
            max_next_q = 0.0
        else:
            next_q_values = self.q_table[next_state_key]
            max_next_q = max(next_q_values.values()) if next_q_values else 0.0

        # Q-Learning 업데이트 공식
        # Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        td_target = reward + self.discount_factor * max_next_q
        td_error = td_target - current_q
        new_q_value = current_q + self.learning_rate * td_error

        # Q값 업데이트
        self.q_table[state_key][action_key] = new_q_value

        # 경험 저장
        experience = QExperience(state, action, reward, next_state, done)
        self.experience_buffer.append(experience)

        # 통계 업데이트
        self.total_rewards += reward
        if reward > 0:
            self.successful_actions += 1

        # 주기적 배치 학습
        if self.online_learning and len(self.experience_buffer) >= self.batch_size:
            if self.total_actions % self.update_frequency == 0:
                self._replay_experience()

        # 탐험율 감소
        self._decay_exploration_rate()

    def _replay_experience(self):
        """경험 리플레이 학습"""
        if len(self.experience_buffer) < self.batch_size:
            return

        # 랜덤 배치 샘플링
        batch = random.sample(list(self.experience_buffer), self.batch_size)

        for experience in batch:
            # 기존 Q-Learning 업데이트와 동일하지만 더 작은 학습률 사용
            state_key = experience.state.to_key()
            action_key = experience.action.to_key()

            current_q = self.q_table[state_key][action_key]

            if experience.done:
                max_next_q = 0.0
            else:
                next_state_key = experience.next_state.to_key()
                next_q_values = self.q_table[next_state_key]
                max_next_q = max(next_q_values.values()) if next_q_values else 0.0

            td_target = experience.reward + self.discount_factor * max_next_q
            td_error = td_target - current_q

            # 리플레이에서는 더 작은 학습률 사용
            replay_learning_rate = self.learning_rate * 0.5
            new_q_value = current_q + replay_learning_rate * td_error

            self.q_table[state_key][action_key] = new_q_value

    def _decay_exploration_rate(self):
        """탐험율 감소"""
        self.exploration_rate = max(
            self.min_exploration_rate, self.exploration_rate * self.exploration_decay
        )

    def calculate_reward(
        self, judgment_result: Dict[str, Any], context: Dict[str, Any] = None
    ) -> float:
        """
        판단 결과로부터 보상 계산

        Args:
            judgment_result: 판단 결과
            context: 추가 컨텍스트

        Returns:
            계산된 보상값 (-1.0 ~ 1.0)
        """
        reward = 0.0

        # 기본 성공/실패 보상
        if judgment_result.get("error_occurred", False):
            reward -= 0.5
        else:
            reward += 0.2

        # 신뢰도 기반 보상
        confidence = judgment_result.get("confidence", 0.5)
        reward += (confidence - 0.5) * 0.6  # -0.3 ~ +0.3

        # 처리 시간 기반 페널티
        processing_time = judgment_result.get("processing_time", 0.0)
        if processing_time > 5.0:  # 5초 이상이면 페널티
            reward -= 0.2
        elif processing_time < 1.0:  # 1초 미만이면 보너스
            reward += 0.1

        # 감정 적절성 보상
        emotion_detected = judgment_result.get("emotion_detected", "neutral")
        if context:
            expected_emotion = context.get("expected_emotion")
            if expected_emotion and emotion_detected == expected_emotion:
                reward += 0.3

        # 전략 일관성 보상
        strategy_suggested = judgment_result.get("strategy_suggested", "balanced")
        if context:
            preferred_strategy = context.get("preferred_strategy")
            if preferred_strategy and strategy_suggested == preferred_strategy:
                reward += 0.2

        # 사용자 피드백 (만약 있다면)
        user_satisfaction = judgment_result.get("user_satisfaction")
        if user_satisfaction is not None:
            reward += (user_satisfaction - 0.5) * 1.0  # 가장 중요한 요소

        # 보상 범위 정규화 (-1.0 ~ 1.0)
        reward = max(-1.0, min(1.0, reward))

        return reward

    def get_best_actions(
        self, state: QState, top_k: int = 3
    ) -> List[Tuple[QAction, float]]:
        """
        주어진 상태에서 최고 Q값을 가진 행동들 반환

        Args:
            state: 상태
            top_k: 반환할 상위 행동 수

        Returns:
            (행동, Q값) 튜플 리스트
        """
        state_key = state.to_key()
        state_q_values = self.q_table[state_key]

        if not state_q_values:
            # Q값이 없으면 기본 행동들 반환
            default_actions = [
                QAction(ActionType.JUDGMENT, "balanced", 0.5),
                QAction(ActionType.STRATEGY, "empathetic", 0.5),
                QAction(ActionType.META_REFLECTION, "self_analysis", 0.5),
            ]
            return [(action, 0.0) for action in default_actions[:top_k]]

        # Q값 기준으로 정렬
        sorted_actions = sorted(
            state_q_values.items(), key=lambda x: x[1], reverse=True
        )

        result = []
        for action_key, q_value in sorted_actions[:top_k]:
            # 행동 키로부터 행동 객체 재구성
            action = self._reconstruct_action_from_key(action_key)
            if action:
                result.append((action, q_value))

        return result

    def _reconstruct_action_from_key(self, action_key: str) -> Optional[QAction]:
        """행동 키로부터 행동 객체 재구성"""
        try:
            parts = action_key.split("_")
            if len(parts) >= 3:
                action_type = ActionType(parts[0])
                strategy = parts[1]
                intensity_str = parts[2]

                intensity_map = {"low": 0.3, "medium": 0.5, "high": 0.8}
                intensity = intensity_map.get(intensity_str, 0.5)

                return QAction(action_type, strategy, intensity)
        except:
            pass
        return None

    def get_strategy_recommendations(
        self, state: QState, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        상태에 기반한 전략 추천

        Args:
            state: 현재 상태
            context: 추가 컨텍스트

        Returns:
            전략 추천 정보
        """
        # 최고 행동들 가져오기
        best_actions = self.get_best_actions(state, top_k=5)

        # 전략별 Q값 집계
        strategy_scores = defaultdict(list)
        for action, q_value in best_actions:
            if action.action_type in [ActionType.JUDGMENT, ActionType.STRATEGY]:
                strategy_scores[action.strategy].append(q_value)

        # 전략별 평균 점수 계산
        strategy_recommendations = {}
        for strategy, scores in strategy_scores.items():
            avg_score = sum(scores) / len(scores)
            strategy_recommendations[strategy] = {
                "score": avg_score,
                "confidence": len(scores) / 5.0,  # 0-1 범위
                "action_count": len(scores),
            }

        # 상위 전략 선택
        sorted_strategies = sorted(
            strategy_recommendations.items(), key=lambda x: x[1]["score"], reverse=True
        )

        return {
            "primary_strategy": (
                sorted_strategies[0][0] if sorted_strategies else "balanced"
            ),
            "alternative_strategies": [s[0] for s in sorted_strategies[1:3]],
            "strategy_scores": dict(strategy_recommendations),
            "state_exploration_level": self.state_visit_count[state.to_key()],
            "total_q_learning_episodes": self.episode_count,
        }

    def end_episode(self, final_reward: float = 0.0):
        """에피소드 종료 처리"""
        self.episode_count += 1
        self.total_rewards += final_reward

        # 주기적 통계 출력
        if self.episode_count % 100 == 0:
            self._print_learning_stats()

    def _print_learning_stats(self):
        """학습 통계 출력"""
        success_rate = (self.successful_actions / max(self.total_actions, 1)) * 100
        avg_reward = self.total_rewards / max(self.episode_count, 1)

        print(f"🎯 Q-Learning 통계 (에피소드 {self.episode_count})")
        print(f"   성공률: {success_rate:.1f}%")
        print(f"   평균 보상: {avg_reward:.3f}")
        print(f"   탐험율: {self.exploration_rate:.3f}")
        print(f"   총 상태 수: {len(self.q_table)}")
        print(f"   경험 버퍼: {len(self.experience_buffer)}")

    def save_q_table(self, file_path: str):
        """Q-Table 저장"""
        data = {
            "q_table": dict(self.q_table),
            "state_visit_count": dict(self.state_visit_count),
            "action_count": dict(self.action_count),
            "parameters": {
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "exploration_rate": self.exploration_rate,
                "exploration_decay": self.exploration_decay,
                "min_exploration_rate": self.min_exploration_rate,
                "exploration_strategy": self.exploration_strategy.value,
            },
            "statistics": {
                "total_actions": self.total_actions,
                "successful_actions": self.successful_actions,
                "total_rewards": self.total_rewards,
                "episode_count": self.episode_count,
            },
            "timestamp": datetime.now().isoformat(),
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Q-Table 저장 완료: {file_path}")

    def load_q_table(self, file_path: str) -> bool:
        """Q-Table 로드"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Q-Table 복원
            self.q_table = defaultdict(lambda: defaultdict(float))
            for state_key, actions in data["q_table"].items():
                for action_key, q_value in actions.items():
                    self.q_table[state_key][action_key] = q_value

            # 기타 데이터 복원
            self.state_visit_count = defaultdict(int)
            self.state_visit_count.update(data["state_visit_count"])

            self.action_count = defaultdict(lambda: defaultdict(int))
            for state_key, actions in data["action_count"].items():
                for action_key, count in actions.items():
                    self.action_count[state_key][action_key] = count

            # 통계 복원
            stats = data.get("statistics", {})
            self.total_actions = stats.get("total_actions", 0)
            self.successful_actions = stats.get("successful_actions", 0)
            self.total_rewards = stats.get("total_rewards", 0.0)
            self.episode_count = stats.get("episode_count", 0)

            print(f"📁 Q-Table 로드 완료: {file_path}")
            print(f"   상태 수: {len(self.q_table)}")
            print(f"   총 에피소드: {self.episode_count}")

            return True

        except Exception as e:
            print(f"❌ Q-Table 로드 실패: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """전체 통계 반환"""
        return {
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "success_rate": (self.successful_actions / max(self.total_actions, 1))
            * 100,
            "total_rewards": self.total_rewards,
            "average_reward": self.total_rewards / max(self.episode_count, 1),
            "episode_count": self.episode_count,
            "exploration_rate": self.exploration_rate,
            "q_table_size": len(self.q_table),
            "total_state_actions": sum(
                len(actions) for actions in self.q_table.values()
            ),
            "experience_buffer_size": len(self.experience_buffer),
            "learning_parameters": {
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "exploration_strategy": self.exploration_strategy.value,
            },
        }


# 편의 함수들
def create_q_state_from_judgment_context(
    emotion: str,
    emotion_intensity: float,
    context_type: str = "general",
    urgency: str = "normal",
    energy_level: float = 0.7,
    recent_success_rate: float = 0.5,
) -> QState:
    """판단 컨텍스트로부터 Q상태 생성"""
    context = {
        "emotion": emotion,
        "emotion_intensity": emotion_intensity,
        "context_type": context_type,
        "urgency": urgency,
        "energy_level": energy_level,
        "recent_success_rate": recent_success_rate,
    }
    return QState.from_context(context)


if __name__ == "__main__":
    # 테스트 코드
    print("🎯 Q-Table 전략 선택기 테스트")
    print("=" * 50)

    # Q-Table 생성
    q_selector = QTableStrategySelector(
        learning_rate=0.1,
        exploration_rate=0.3,
        exploration_strategy=ExplorationStrategy.EPSILON_GREEDY,
    )

    # 테스트 시나리오
    test_scenarios = [
        {
            "name": "긍정적 상황",
            "state": create_q_state_from_judgment_context(
                "joy", 0.8, "personal", "normal", 0.9, 0.8
            ),
            "expected_reward": 0.7,
        },
        {
            "name": "부정적 상황",
            "state": create_q_state_from_judgment_context(
                "sadness", 0.6, "personal", "high", 0.4, 0.3
            ),
            "expected_reward": 0.3,
        },
        {
            "name": "업무 스트레스",
            "state": create_q_state_from_judgment_context(
                "anger", 0.7, "work", "high", 0.5, 0.4
            ),
            "expected_reward": 0.2,
        },
        {
            "name": "중성 상황",
            "state": create_q_state_from_judgment_context(
                "neutral", 0.3, "general", "normal", 0.7, 0.6
            ),
            "expected_reward": 0.5,
        },
    ]

    # 학습 시뮬레이션
    for episode in range(5):
        print(f"\n=== 에피소드 {episode + 1} ===")

        for scenario in test_scenarios:
            print(f"\n📋 {scenario['name']}")

            state = scenario["state"]

            # 행동 선택
            action = q_selector.select_action(state)
            print(
                f"   선택된 행동: {action.action_type.value} - {action.strategy} (강도: {action.intensity:.1f})"
            )

            # 가상의 다음 상태 (단순화)
            # 현재 상태의 문자열 값들을 숫자로 변환
            current_intensity = 0.5  # 기본값
            if state.emotion_intensity == "minimal":
                current_intensity = 0.1
            elif state.emotion_intensity == "low":
                current_intensity = 0.3
            elif state.emotion_intensity == "moderate":
                current_intensity = 0.5
            elif state.emotion_intensity == "high":
                current_intensity = 0.7
            elif state.emotion_intensity == "intense":
                current_intensity = 0.9

            current_energy = 0.7  # 기본값
            if state.energy_level == "low":
                current_energy = 0.3
            elif state.energy_level == "medium":
                current_energy = 0.7
            elif state.energy_level == "high":
                current_energy = 0.9

            next_state = create_q_state_from_judgment_context(
                state.emotion,
                (
                    max(0.1, current_intensity - 0.1)
                    if "sad" in state.emotion
                    else current_intensity
                ),
                state.context_type,
                state.urgency,
                min(1.0, current_energy + 0.1) if state.energy_level != "high" else 1.0,
                scenario["expected_reward"],
            )

            # 모의 판단 결과
            judgment_result = {
                "confidence": 0.6 + random.random() * 0.3,
                "processing_time": 0.5 + random.random() * 2.0,
                "error_occurred": random.random() < 0.1,
                "emotion_detected": state.emotion,
                "strategy_suggested": action.strategy,
            }

            # 보상 계산 및 Q값 업데이트
            reward = q_selector.calculate_reward(judgment_result)
            q_selector.update_q_value(state, action, reward, next_state)

            print(f"   보상: {reward:.3f}")

        # 에피소드 종료
        q_selector.end_episode()

    # 최종 통계
    print(f"\n📊 최종 Q-Learning 통계:")
    stats = q_selector.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

    # 전략 추천 테스트
    print(f"\n💡 전략 추천 테스트:")
    test_state = create_q_state_from_judgment_context(
        "fear", 0.6, "work", "high", 0.4, 0.3
    )
    recommendations = q_selector.get_strategy_recommendations(test_state)

    print(f"  주요 전략: {recommendations['primary_strategy']}")
    print(f"  대안 전략: {recommendations['alternative_strategies']}")
    print(f"  상태 탐험 수준: {recommendations['state_exploration_level']}")
