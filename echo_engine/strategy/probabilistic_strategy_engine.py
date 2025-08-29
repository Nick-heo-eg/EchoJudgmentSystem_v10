#!/usr/bin/env python3
"""
🎲 Probabilistic Strategy Engine v1.0
베이지안 추론 및 몬테카를로 시뮬레이션 기반 확률적 전략 선택 시스템

Phase 2: LLM-Free 판단 시스템 고도화 모듈
- 베이지안 네트워크를 활용한 상황별 최적 전략 추론
- 몬테카를로 시뮬레이션으로 다중 시나리오 결과 예측
- 마르코프 체인 모델을 통한 대화 흐름 및 감정 전이 예측
- "디지털 공감 예술가"를 위한 확률적 의사결정 시스템

참조: LLM-Free 판단 시스템 완성도 극대화 가이드 Phase 2
- 단순 규칙 기반을 넘어선 확률적 추론 시스템
- 불확실성을 고려한 리스크 기반 전략 선택
- 실시간 학습을 통한 확률 모델 지속적 개선
"""

import os
import json
import time
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import numpy as np


@dataclass
class StrategyProbability:
    """전략 확률 데이터 클래스"""

    strategy_name: str
    base_probability: float  # 기본 확률
    conditional_probabilities: Dict[str, float]  # 조건부 확률들
    confidence_interval: Tuple[float, float]  # 신뢰 구간
    historical_success_rate: float  # 과거 성공률
    risk_factor: float  # 리스크 요소 (0.0: 안전, 1.0: 위험)
    expected_outcome: Dict[str, float]  # 예상 결과


@dataclass
class BayesianContext:
    """베이지안 추론을 위한 컨텍스트"""

    user_emotional_state: str
    conversation_depth: float
    urgency_level: float
    social_context: str
    temporal_factors: Dict[str, Any]
    historical_patterns: Dict[str, float]


class ProbabilisticStrategyEngine:
    """확률적 전략 선택을 위한 베이지안 추론 엔진"""

    def __init__(self, data_dir: str = "data/probabilistic_strategy"):
        """초기화"""
        self.version = "1.0.0"
        self.data_dir = data_dir
        self.strategy_cache = {}
        self.bayesian_network = {}
        self.markov_chains = {}
        self.monte_carlo_samples = 1000
        self.analysis_count = 0

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

        # 전략 카테고리 정의
        self.strategy_categories = {
            "empathetic": {
                "strategies": ["comfort", "validate", "listen"],
                "base_success": 0.75,
                "optimal_contexts": ["sadness", "fear", "stress"],
            },
            "analytical": {
                "strategies": ["analyze", "plan", "structure"],
                "base_success": 0.70,
                "optimal_contexts": ["confusion", "decision", "problem"],
            },
            "energizing": {
                "strategies": ["motivate", "challenge", "inspire"],
                "base_success": 0.65,
                "optimal_contexts": ["apathy", "depression", "stagnation"],
            },
            "creative": {
                "strategies": ["explore", "imagine", "reframe"],
                "base_success": 0.60,
                "optimal_contexts": ["boredom", "creativity_block", "routine"],
            },
            "social": {
                "strategies": ["connect", "share", "collaborate"],
                "base_success": 0.68,
                "optimal_contexts": ["loneliness", "isolation", "relationship"],
            },
        }

        # 베이지안 네트워크 초기 구조
        self.bayesian_network = {
            # P(전략|감정, 컨텍스트, 시간, 과거패턴)
            "strategy_nodes": {
                "comfort": {
                    "prior": 0.15,
                    "dependencies": ["emotion", "urgency", "social_context"],
                },
                "analyze": {
                    "prior": 0.20,
                    "dependencies": ["emotion", "complexity", "user_preference"],
                },
                "motivate": {
                    "prior": 0.12,
                    "dependencies": ["emotion", "energy_level", "time_of_day"],
                },
                "listen": {
                    "prior": 0.18,
                    "dependencies": ["emotion", "conversation_depth", "urgency"],
                },
                "challenge": {
                    "prior": 0.10,
                    "dependencies": ["emotion", "user_confidence", "relationship"],
                },
                "explore": {
                    "prior": 0.12,
                    "dependencies": ["emotion", "creativity_need", "openness"],
                },
                "validate": {
                    "prior": 0.13,
                    "dependencies": ["emotion", "self_doubt", "support_need"],
                },
            },
            # 조건부 확률 테이블
            "conditional_probabilities": {
                "emotion_given_strategy": {
                    "comfort": {"sadness": 0.8, "fear": 0.7, "anger": 0.3, "joy": 0.1},
                    "analyze": {
                        "confusion": 0.9,
                        "anxiety": 0.6,
                        "curiosity": 0.7,
                        "frustration": 0.5,
                    },
                    "motivate": {
                        "apathy": 0.8,
                        "depression": 0.7,
                        "fatigue": 0.6,
                        "excitement": 0.4,
                    },
                    "listen": {
                        "overwhelm": 0.9,
                        "sadness": 0.8,
                        "anger": 0.7,
                        "confusion": 0.6,
                    },
                    "challenge": {
                        "complacency": 0.8,
                        "doubt": 0.6,
                        "fear": 0.4,
                        "confidence": 0.7,
                    },
                    "explore": {
                        "boredom": 0.9,
                        "curiosity": 0.8,
                        "stagnation": 0.7,
                        "creativity": 0.6,
                    },
                    "validate": {
                        "insecurity": 0.9,
                        "doubt": 0.8,
                        "shame": 0.7,
                        "anxiety": 0.5,
                    },
                }
            },
        }

        # 마르코프 체인 상태 전이 매트릭스
        self.emotion_transition_matrix = {
            "sadness": {"sadness": 0.4, "neutral": 0.3, "comfort": 0.2, "hope": 0.1},
            "anger": {"anger": 0.5, "frustration": 0.2, "calm": 0.2, "regret": 0.1},
            "fear": {"fear": 0.6, "anxiety": 0.2, "relief": 0.1, "confidence": 0.1},
            "joy": {"joy": 0.3, "satisfaction": 0.4, "neutral": 0.2, "nostalgia": 0.1},
            "neutral": {
                "neutral": 0.5,
                "curiosity": 0.2,
                "mild_joy": 0.15,
                "mild_concern": 0.15,
            },
        }

        print(f"🎲 Probabilistic Strategy Engine v{self.version} 초기화 완료")
        print(f"📁 확률 모델 저장 경로: {self.data_dir}")

    def select_optimal_strategy(
        self, context: BayesianContext, available_strategies: List[str] = None
    ) -> Dict[str, Any]:
        """
        베이지안 추론을 통한 최적 전략 선택

        Args:
            context: 베이지안 추론 컨텍스트
            available_strategies: 사용 가능한 전략 목록

        Returns:
            최적 전략 및 확률적 분석 결과
        """
        self.analysis_count += 1
        start_time = time.time()

        if available_strategies is None:
            available_strategies = list(self.bayesian_network["strategy_nodes"].keys())

        # 1. 베이지안 추론으로 각 전략의 사후 확률 계산
        strategy_posteriors = self._calculate_bayesian_posteriors(
            context, available_strategies
        )

        # 2. 몬테카를로 시뮬레이션으로 각 전략의 예상 결과 시뮬레이션
        simulation_results = self._monte_carlo_simulation(context, strategy_posteriors)

        # 3. 마르코프 체인으로 장기 결과 예측
        long_term_predictions = self._markov_chain_prediction(
            context, strategy_posteriors
        )

        # 4. 리스크-보상 분석
        risk_reward_analysis = self._risk_reward_analysis(
            strategy_posteriors, simulation_results
        )

        # 5. 최종 전략 선택 (기대 효용 최대화)
        optimal_strategy = self._select_by_expected_utility(
            strategy_posteriors, simulation_results, risk_reward_analysis
        )

        # 결과 구성
        result = {
            "optimal_strategy": optimal_strategy,
            "strategy_probabilities": strategy_posteriors,
            "simulation_results": simulation_results,
            "long_term_prediction": long_term_predictions,
            "risk_analysis": risk_reward_analysis,
            "confidence_metrics": self._calculate_confidence_metrics(
                strategy_posteriors
            ),
            "meta": {
                "analysis_id": self.analysis_count,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "monte_carlo_samples": self.monte_carlo_samples,
            },
        }

        return result

    def _calculate_bayesian_posteriors(
        self, context: BayesianContext, strategies: List[str]
    ) -> Dict[str, StrategyProbability]:
        """베이지안 추론으로 사후 확률 계산"""
        posteriors = {}

        for strategy in strategies:
            if strategy not in self.bayesian_network["strategy_nodes"]:
                continue

            strategy_node = self.bayesian_network["strategy_nodes"][strategy]

            # 사전 확률
            prior = strategy_node["prior"]

            # 우도 계산 (P(증거|전략))
            likelihood = self._calculate_likelihood(strategy, context)

            # 정규화 상수 계산을 위한 전체 증거 확률
            evidence = self._calculate_evidence_probability(strategies, context)

            # 베이즈 정리: P(전략|증거) = P(증거|전략) * P(전략) / P(증거)
            posterior = (likelihood * prior) / max(evidence, 1e-10)

            # 신뢰 구간 계산 (베타 분포 근사)
            confidence_interval = self._calculate_confidence_interval(posterior)

            # 과거 성공률 (학습 데이터 기반)
            historical_success = self._get_historical_success_rate(strategy, context)

            # 리스크 요소 계산
            risk_factor = self._calculate_risk_factor(strategy, context)

            # 예상 결과
            expected_outcome = self._predict_outcome(strategy, context, posterior)

            posteriors[strategy] = StrategyProbability(
                strategy_name=strategy,
                base_probability=posterior,
                conditional_probabilities=self._get_conditional_probs(
                    strategy, context
                ),
                confidence_interval=confidence_interval,
                historical_success_rate=historical_success,
                risk_factor=risk_factor,
                expected_outcome=expected_outcome,
            )

        return posteriors

    def _calculate_likelihood(self, strategy: str, context: BayesianContext) -> float:
        """우도 계산 P(증거|전략)"""
        likelihood = 1.0

        # 감정 상태에 따른 우도
        emotion_probs = self.bayesian_network["conditional_probabilities"][
            "emotion_given_strategy"
        ]
        if strategy in emotion_probs:
            emotion_likelihood = emotion_probs[strategy].get(
                context.user_emotional_state, 0.1
            )
            likelihood *= emotion_likelihood

        # 컨텍스트 요소들에 따른 우도 조정
        likelihood *= self._context_likelihood_modifier(strategy, context)

        return likelihood

    def _context_likelihood_modifier(
        self, strategy: str, context: BayesianContext
    ) -> float:
        """컨텍스트 기반 우도 수정자"""
        modifier = 1.0

        # 대화 깊이에 따른 조정
        if context.conversation_depth > 0.7:
            if strategy in ["listen", "validate", "comfort"]:
                modifier *= 1.3
            elif strategy in ["challenge", "motivate"]:
                modifier *= 0.7

        # 긴급도에 따른 조정
        if context.urgency_level > 0.7:
            if strategy in ["analyze", "plan"]:
                modifier *= 1.4
            elif strategy in ["explore", "imagine"]:
                modifier *= 0.6

        # 사회적 맥락에 따른 조정
        if context.social_context == "private":
            if strategy in ["comfort", "validate", "listen"]:
                modifier *= 1.2
        elif context.social_context == "public":
            if strategy in ["challenge", "motivate"]:
                modifier *= 1.1

        # 시간적 요소 고려
        temporal_modifier = self._temporal_likelihood_modifier(
            strategy, context.temporal_factors
        )
        modifier *= temporal_modifier

        return modifier

    def _temporal_likelihood_modifier(
        self, strategy: str, temporal_factors: Dict[str, Any]
    ) -> float:
        """시간적 요소 기반 우도 수정자"""
        modifier = 1.0

        time_period = temporal_factors.get("time_period", "afternoon")
        day_of_week = temporal_factors.get("day_of_week", "wednesday")

        # 시간대별 전략 효과성
        time_effects = {
            "morning": {"motivate": 1.3, "analyze": 1.2, "comfort": 0.9},
            "afternoon": {"analyze": 1.1, "challenge": 1.1, "explore": 1.0},
            "evening": {"comfort": 1.2, "listen": 1.2, "validate": 1.1},
            "night": {"comfort": 1.4, "listen": 1.3, "analyze": 0.8},
        }

        if time_period in time_effects and strategy in time_effects[time_period]:
            modifier *= time_effects[time_period][strategy]

        # 요일별 효과
        if day_of_week in ["monday", "tuesday"]:  # 주 초
            if strategy in ["motivate", "challenge"]:
                modifier *= 1.1
        elif day_of_week in ["friday", "saturday"]:  # 주말 근처
            if strategy in ["comfort", "explore"]:
                modifier *= 1.1

        return modifier

    def _calculate_evidence_probability(
        self, strategies: List[str], context: BayesianContext
    ) -> float:
        """전체 증거 확률 P(증거) 계산"""
        evidence = 0.0

        for strategy in strategies:
            if strategy in self.bayesian_network["strategy_nodes"]:
                prior = self.bayesian_network["strategy_nodes"][strategy]["prior"]
                likelihood = self._calculate_likelihood(strategy, context)
                evidence += likelihood * prior

        return evidence

    def _calculate_confidence_interval(
        self, probability: float, confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """확률의 신뢰 구간 계산"""
        # 베타 분포를 이용한 근사적 신뢰 구간
        alpha = confidence_level / 2
        n = 100  # 가정된 샘플 크기

        # 정규 근사를 이용한 신뢰 구간
        margin = 1.96 * math.sqrt(probability * (1 - probability) / n)  # 95% 신뢰구간

        lower = max(0.0, probability - margin)
        upper = min(1.0, probability + margin)

        return (lower, upper)

    def _get_historical_success_rate(
        self, strategy: str, context: BayesianContext
    ) -> float:
        """과거 성공률 조회 (실제로는 학습 데이터에서 가져옴)"""
        # 기본 성공률 (카테고리별)
        base_rates = {
            "comfort": 0.78,
            "validate": 0.75,
            "listen": 0.82,
            "analyze": 0.72,
            "plan": 0.70,
            "structure": 0.68,
            "motivate": 0.65,
            "challenge": 0.60,
            "inspire": 0.67,
            "explore": 0.63,
            "imagine": 0.58,
            "reframe": 0.64,
        }

        base_rate = base_rates.get(strategy, 0.65)

        # 컨텍스트 기반 조정
        if context.user_emotional_state in ["sadness", "fear"] and strategy in [
            "comfort",
            "validate",
        ]:
            base_rate *= 1.1
        elif context.urgency_level > 0.8 and strategy in ["analyze", "plan"]:
            base_rate *= 1.05

        return min(base_rate, 1.0)

    def _calculate_risk_factor(self, strategy: str, context: BayesianContext) -> float:
        """전략별 리스크 요소 계산"""
        # 기본 리스크 레벨
        base_risks = {
            "comfort": 0.1,
            "validate": 0.1,
            "listen": 0.05,
            "analyze": 0.2,
            "plan": 0.15,
            "structure": 0.25,
            "motivate": 0.3,
            "challenge": 0.4,
            "inspire": 0.25,
            "explore": 0.2,
            "imagine": 0.15,
            "reframe": 0.3,
        }

        base_risk = base_risks.get(strategy, 0.2)

        # 컨텍스트 기반 리스크 조정
        if (
            context.user_emotional_state in ["anger", "frustration"]
            and strategy == "challenge"
        ):
            base_risk *= 1.5  # 화난 상태에서 도전은 위험
        elif context.urgency_level > 0.8 and strategy in ["explore", "imagine"]:
            base_risk *= 1.3  # 급한 상황에서 탐색은 위험

        return min(base_risk, 1.0)

    def _predict_outcome(
        self, strategy: str, context: BayesianContext, probability: float
    ) -> Dict[str, float]:
        """전략 실행 시 예상 결과 예측"""
        # 기본 결과 카테고리별 점수
        outcome_categories = [
            "satisfaction",
            "problem_solving",
            "emotional_improvement",
            "relationship_quality",
        ]

        base_outcomes = {
            "comfort": {
                "satisfaction": 0.8,
                "problem_solving": 0.4,
                "emotional_improvement": 0.9,
                "relationship_quality": 0.7,
            },
            "analyze": {
                "satisfaction": 0.7,
                "problem_solving": 0.9,
                "emotional_improvement": 0.5,
                "relationship_quality": 0.6,
            },
            "motivate": {
                "satisfaction": 0.6,
                "problem_solving": 0.7,
                "emotional_improvement": 0.8,
                "relationship_quality": 0.7,
            },
            "listen": {
                "satisfaction": 0.9,
                "problem_solving": 0.3,
                "emotional_improvement": 0.8,
                "relationship_quality": 0.9,
            },
            "challenge": {
                "satisfaction": 0.5,
                "problem_solving": 0.8,
                "emotional_improvement": 0.6,
                "relationship_quality": 0.5,
            },
            "explore": {
                "satisfaction": 0.7,
                "problem_solving": 0.6,
                "emotional_improvement": 0.7,
                "relationship_quality": 0.6,
            },
        }

        outcomes = base_outcomes.get(strategy, {cat: 0.6 for cat in outcome_categories})

        # 확률과 컨텍스트로 결과 조정
        for category in outcomes:
            outcomes[category] *= probability  # 확률이 높을수록 좋은 결과

            # 컨텍스트별 조정
            if (
                category == "emotional_improvement"
                and context.user_emotional_state in ["sadness", "fear"]
            ):
                outcomes[category] *= 1.1
            elif category == "problem_solving" and context.urgency_level > 0.7:
                outcomes[category] *= 1.05

        return outcomes

    def _get_conditional_probs(
        self, strategy: str, context: BayesianContext
    ) -> Dict[str, float]:
        """조건부 확률들 반환"""
        return {
            "success_given_emotion": self._prob_success_given_emotion(
                strategy, context.user_emotional_state
            ),
            "satisfaction_given_urgency": self._prob_satisfaction_given_urgency(
                strategy, context.urgency_level
            ),
            "effectiveness_given_depth": self._prob_effectiveness_given_depth(
                strategy, context.conversation_depth
            ),
        }

    def _prob_success_given_emotion(self, strategy: str, emotion: str) -> float:
        """P(성공|감정, 전략) 계산"""
        emotion_strategy_success = {
            ("sadness", "comfort"): 0.85,
            ("sadness", "listen"): 0.80,
            ("sadness", "analyze"): 0.40,
            ("anger", "listen"): 0.75,
            ("anger", "validate"): 0.70,
            ("anger", "challenge"): 0.30,
            ("fear", "comfort"): 0.80,
            ("fear", "analyze"): 0.65,
            ("fear", "motivate"): 0.45,
            ("joy", "motivate"): 0.75,
            ("joy", "explore"): 0.70,
            ("joy", "comfort"): 0.60,
        }

        return emotion_strategy_success.get((emotion, strategy), 0.60)

    def _prob_satisfaction_given_urgency(self, strategy: str, urgency: float) -> float:
        """P(만족|긴급도, 전략) 계산"""
        if urgency > 0.7:  # 높은 긴급도
            urgent_strategy_satisfaction = {
                "analyze": 0.80,
                "plan": 0.75,
                "comfort": 0.50,
                "explore": 0.30,
            }
            return urgent_strategy_satisfaction.get(strategy, 0.55)
        else:  # 낮은 긴급도
            relaxed_strategy_satisfaction = {
                "explore": 0.75,
                "comfort": 0.80,
                "analyze": 0.65,
                "motivate": 0.70,
            }
            return relaxed_strategy_satisfaction.get(strategy, 0.65)

    def _prob_effectiveness_given_depth(self, strategy: str, depth: float) -> float:
        """P(효과성|대화깊이, 전략) 계산"""
        if depth > 0.7:  # 깊은 대화
            deep_strategy_effectiveness = {
                "listen": 0.90,
                "validate": 0.85,
                "comfort": 0.80,
                "challenge": 0.60,
            }
            return deep_strategy_effectiveness.get(strategy, 0.70)
        else:  # 표면적 대화
            surface_strategy_effectiveness = {
                "analyze": 0.75,
                "motivate": 0.70,
                "explore": 0.65,
                "listen": 0.60,
            }
            return surface_strategy_effectiveness.get(strategy, 0.65)

    def _monte_carlo_simulation(
        self,
        context: BayesianContext,
        strategy_posteriors: Dict[str, StrategyProbability],
    ) -> Dict[str, Dict[str, float]]:
        """몬테카를로 시뮬레이션으로 전략별 결과 분포 계산"""
        simulation_results = {}

        for strategy, prob_data in strategy_posteriors.items():
            results = []

            # 몬테카를로 샘플링
            for _ in range(self.monte_carlo_samples):
                # 랜덤 변수들 샘플링
                success_prob = prob_data.base_probability
                risk_factor = prob_data.risk_factor

                # 노이즈 추가 (현실적 변동성)
                noise = random.gauss(0, 0.1)  # 표준편차 0.1인 정규분포 노이즈
                actual_success = max(0, min(1, success_prob + noise))

                # 리스크 고려
                if random.random() < risk_factor:
                    actual_success *= 0.5  # 리스크 발생 시 성공률 반감

                results.append(actual_success)

            # 시뮬레이션 결과 통계
            simulation_results[strategy] = {
                "mean_success": statistics.mean(results),
                "std_success": statistics.stdev(results) if len(results) > 1 else 0,
                "percentile_25": np.percentile(results, 25),
                "percentile_75": np.percentile(results, 75),
                "min_success": min(results),
                "max_success": max(results),
                "success_probability": sum(1 for r in results if r > 0.5)
                / len(results),
            }

        return simulation_results

    def _markov_chain_prediction(
        self,
        context: BayesianContext,
        strategy_posteriors: Dict[str, StrategyProbability],
    ) -> Dict[str, Any]:
        """마르코프 체인을 이용한 장기 감정 상태 예측"""
        current_emotion = context.user_emotional_state

        # 각 전략 실행 후 감정 전이 예측
        predictions = {}

        for strategy in strategy_posteriors.keys():
            # 전략 실행이 감정에 미치는 영향 모델링
            strategy_emotion_effects = {
                "comfort": {"sadness": "relief", "fear": "security", "anger": "calm"},
                "analyze": {
                    "confusion": "clarity",
                    "anxiety": "understanding",
                    "overwhelm": "structure",
                },
                "motivate": {
                    "apathy": "motivation",
                    "depression": "hope",
                    "fatigue": "energy",
                },
                "listen": {
                    "loneliness": "connection",
                    "anger": "validation",
                    "sadness": "understanding",
                },
                "challenge": {
                    "complacency": "growth",
                    "doubt": "confidence",
                    "fear": "courage",
                },
                "explore": {
                    "boredom": "interest",
                    "stagnation": "movement",
                    "routine": "novelty",
                },
            }

            # 전략 후 예상 감정 상태
            post_strategy_emotion = strategy_emotion_effects.get(strategy, {}).get(
                current_emotion, current_emotion
            )

            # 마르코프 체인으로 n-step 미래 예측
            future_states = self._predict_emotion_chain(post_strategy_emotion, steps=3)

            predictions[strategy] = {
                "immediate_emotion": post_strategy_emotion,
                "future_states": future_states,
                "stability_score": self._calculate_emotion_stability(future_states),
            }

        return predictions

    def _predict_emotion_chain(
        self, initial_state: str, steps: int
    ) -> List[Dict[str, float]]:
        """마르코프 체인으로 감정 상태 전이 예측"""
        if initial_state not in self.emotion_transition_matrix:
            initial_state = "neutral"

        current_distribution = {initial_state: 1.0}
        future_states = []

        for step in range(steps):
            next_distribution = defaultdict(float)

            for current_emotion, current_prob in current_distribution.items():
                if current_emotion in self.emotion_transition_matrix:
                    transitions = self.emotion_transition_matrix[current_emotion]

                    for next_emotion, trans_prob in transitions.items():
                        next_distribution[next_emotion] += current_prob * trans_prob

            current_distribution = dict(next_distribution)
            future_states.append(current_distribution.copy())

        return future_states

    def _calculate_emotion_stability(
        self, future_states: List[Dict[str, float]]
    ) -> float:
        """감정 안정성 점수 계산"""
        if not future_states:
            return 0.5

        # 각 단계에서 가장 높은 확률을 가진 감정의 확률들
        max_probs = [max(state.values()) for state in future_states]

        # 안정성 = 평균 최대 확률 (높을수록 안정적)
        stability = statistics.mean(max_probs)

        return stability

    def _risk_reward_analysis(
        self,
        strategy_posteriors: Dict[str, StrategyProbability],
        simulation_results: Dict[str, Dict[str, float]],
    ) -> Dict[str, Dict[str, float]]:
        """리스크-보상 분석"""
        analysis = {}

        for strategy in strategy_posteriors.keys():
            prob_data = strategy_posteriors[strategy]
            sim_data = simulation_results[strategy]

            # 보상 계산 (기대 성공률 × 잠재적 효과)
            expected_reward = (
                sim_data["mean_success"] * prob_data.historical_success_rate
            )

            # 리스크 계산 (변동성 + 리스크 요소)
            risk_score = sim_data["std_success"] + prob_data.risk_factor

            # 샤프 비율 유사 지표 (보상/리스크 비율)
            sharpe_ratio = expected_reward / max(risk_score, 0.01)

            # 하방 리스크 (실패 확률)
            downside_risk = 1 - sim_data["success_probability"]

            analysis[strategy] = {
                "expected_reward": expected_reward,
                "risk_score": risk_score,
                "sharpe_ratio": sharpe_ratio,
                "downside_risk": downside_risk,
                "risk_adjusted_return": expected_reward * (1 - downside_risk),
            }

        return analysis

    def _select_by_expected_utility(
        self,
        strategy_posteriors: Dict[str, StrategyProbability],
        simulation_results: Dict[str, Dict[str, float]],
        risk_analysis: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        """기대 효용 최대화를 통한 최적 전략 선택"""
        utilities = {}

        for strategy in strategy_posteriors.keys():
            prob_data = strategy_posteriors[strategy]
            sim_data = simulation_results[strategy]
            risk_data = risk_analysis[strategy]

            # 기대 효용 = 기대 보상 - 리스크 페널티
            risk_tolerance = 0.5  # 리스크 회피 정도 (0: 리스크 중립, 1: 극도 회피)

            expected_utility = (
                risk_data["expected_reward"]
                - (risk_tolerance * risk_data["risk_score"])
                + (0.2 * prob_data.historical_success_rate)  # 과거 성과 보너스
                + (0.1 * sim_data["success_probability"])  # 성공 확률 보너스
            )

            utilities[strategy] = {
                "expected_utility": expected_utility,
                "components": {
                    "base_reward": risk_data["expected_reward"],
                    "risk_penalty": risk_tolerance * risk_data["risk_score"],
                    "history_bonus": 0.2 * prob_data.historical_success_rate,
                    "success_bonus": 0.1 * sim_data["success_probability"],
                },
            }

        # 최고 효용 전략 선택
        best_strategy = max(
            utilities.keys(), key=lambda s: utilities[s]["expected_utility"]
        )

        return {
            "strategy": best_strategy,
            "expected_utility": utilities[best_strategy]["expected_utility"],
            "all_utilities": utilities,
            "confidence": strategy_posteriors[best_strategy].base_probability,
            "risk_level": strategy_posteriors[best_strategy].risk_factor,
        }

    def _calculate_confidence_metrics(
        self, strategy_posteriors: Dict[str, StrategyProbability]
    ) -> Dict[str, float]:
        """신뢰도 지표 계산"""
        probabilities = [prob.base_probability for prob in strategy_posteriors.values()]

        # 엔트로피 (불확실성 측정)
        entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probabilities)

        # 최대 확률과 두 번째 최대 확률의 차이
        sorted_probs = sorted(probabilities, reverse=True)
        confidence_gap = (
            sorted_probs[0] - sorted_probs[1]
            if len(sorted_probs) > 1
            else sorted_probs[0]
        )

        # 전체적 신뢰도
        overall_confidence = max(probabilities)

        return {
            "entropy": entropy,
            "confidence_gap": confidence_gap,
            "overall_confidence": overall_confidence,
            "decision_clarity": (
                confidence_gap / overall_confidence if overall_confidence > 0 else 0
            ),
        }

    def update_learning_data(
        self,
        strategy: str,
        context: BayesianContext,
        outcome_feedback: Dict[str, float],
    ) -> None:
        """실제 결과 피드백을 통한 확률 모델 업데이트"""
        # 베이지안 학습으로 모델 파라미터 업데이트
        # 실제 구현에서는 베타 분포나 디리클레 분포 등을 사용하여
        # 온라인 학습을 구현할 수 있음
        pass

    def get_strategy_explanation(self, result: Dict[str, Any]) -> List[str]:
        """전략 선택 이유 설명 생성"""
        explanations = []
        optimal = result["optimal_strategy"]

        strategy_name = optimal["strategy"]
        utility = optimal["expected_utility"]
        confidence = optimal["confidence"]
        risk = optimal["risk_level"]

        explanations.append(
            f"'{strategy_name}' 전략이 최고 기대 효용 {utility:.3f}로 선택됨"
        )
        explanations.append(f"선택 신뢰도: {confidence:.1%}, 리스크 수준: {risk:.1%}")

        # 확률적 분석 근거
        confidence_metrics = result["confidence_metrics"]
        if confidence_metrics["decision_clarity"] > 0.3:
            explanations.append("명확한 선택 근거 존재 - 높은 의사결정 확실성")
        else:
            explanations.append("여러 전략이 유사한 효용 - 신중한 모니터링 필요")

        # 시뮬레이션 결과 기반 설명
        sim_results = result["simulation_results"].get(strategy_name, {})
        success_prob = sim_results.get("success_probability", 0)
        explanations.append(f"몬테카를로 시뮬레이션 성공률: {success_prob:.1%}")

        return explanations


def test_probabilistic_strategy_engine():
    """확률적 전략 엔진 테스트"""
    print("🧪 Probabilistic Strategy Engine 테스트 시작...")

    engine = ProbabilisticStrategyEngine()

    # 테스트 시나리오 1: 슬픈 감정 상태에서의 전략 선택
    print("\n📝 시나리오 1: 슬픈 감정 상태 - 낮은 긴급도")
    context_1 = BayesianContext(
        user_emotional_state="sadness",
        conversation_depth=0.6,
        urgency_level=0.2,
        social_context="private",
        temporal_factors={"time_period": "evening", "day_of_week": "sunday"},
        historical_patterns={"preferred_empathy": 0.8, "analytical_preference": 0.3},
    )

    result_1 = engine.select_optimal_strategy(context_1)
    print(f"🎯 최적 전략: {result_1['optimal_strategy']['strategy']}")
    print(f"💪 기대 효용: {result_1['optimal_strategy']['expected_utility']:.3f}")
    print(f"🎲 신뢰도: {result_1['optimal_strategy']['confidence']:.3f}")

    explanations_1 = engine.get_strategy_explanation(result_1)
    print("🧠 선택 근거:")
    for explanation in explanations_1:
        print(f"   - {explanation}")

    # 테스트 시나리오 2: 급한 상황에서의 전략 선택
    print("\n📝 시나리오 2: 혼란스러운 상태 - 높은 긴급도")
    context_2 = BayesianContext(
        user_emotional_state="confusion",
        conversation_depth=0.3,
        urgency_level=0.9,
        social_context="semi-private",
        temporal_factors={"time_period": "morning", "day_of_week": "monday"},
        historical_patterns={"analytical_preference": 0.9, "patience_level": 0.3},
    )

    result_2 = engine.select_optimal_strategy(context_2)
    print(f"🎯 최적 전략: {result_2['optimal_strategy']['strategy']}")
    print(f"💪 기대 효용: {result_2['optimal_strategy']['expected_utility']:.3f}")
    print(f"⚠️ 리스크 수준: {result_2['optimal_strategy']['risk_level']:.3f}")

    # 테스트 시나리오 3: 기쁜 상태에서의 전략 선택
    print("\n📝 시나리오 3: 기쁜 감정 상태 - 중간 깊이 대화")
    context_3 = BayesianContext(
        user_emotional_state="joy",
        conversation_depth=0.8,
        urgency_level=0.1,
        social_context="public",
        temporal_factors={"time_period": "afternoon", "day_of_week": "friday"},
        historical_patterns={"creativity_preference": 0.7, "social_engagement": 0.8},
    )

    result_3 = engine.select_optimal_strategy(context_3)
    print(f"🎯 최적 전략: {result_3['optimal_strategy']['strategy']}")

    # 확률 분포 분석
    print(f"\n📊 전략별 확률 분포:")
    for strategy, prob_data in result_3["strategy_probabilities"].items():
        print(
            f"   {strategy}: {prob_data.base_probability:.3f} "
            f"(성공률: {prob_data.historical_success_rate:.3f}, "
            f"리스크: {prob_data.risk_factor:.3f})"
        )

    # 장기 예측 결과
    print(f"\n🔮 장기 감정 상태 예측:")
    long_term = result_3["long_term_prediction"]
    best_strategy = result_3["optimal_strategy"]["strategy"]
    if best_strategy in long_term:
        prediction = long_term[best_strategy]
        print(f"   즉시 효과: {prediction['immediate_emotion']}")
        print(f"   안정성 점수: {prediction['stability_score']:.3f}")

    # 신뢰도 메트릭스
    confidence = result_3["confidence_metrics"]
    print(f"\n📈 의사결정 신뢰도:")
    print(f"   전체 신뢰도: {confidence['overall_confidence']:.3f}")
    print(f"   결정 명확성: {confidence['decision_clarity']:.3f}")
    print(f"   엔트로피: {confidence['entropy']:.3f}")

    print("\n🎉 Probabilistic Strategy Engine 테스트 완료!")


if __name__ == "__main__":
    test_probabilistic_strategy_engine()
