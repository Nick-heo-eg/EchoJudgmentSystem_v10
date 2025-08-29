#!/usr/bin/env python3
"""
🔁 EchoJudgmentSystem v10.6 - Replay Learning Engine
과거 판단⨯결정⨯피드백 로그를 활용한 시뮬레이션 학습 모듈

TT.006: "과거는 미래의 교사이다. 모든 실수와 성공은 다음 지혜의 씨앗이 된다."

주요 기능:
- 과거 세션 데이터 로드 및 분석
- 결정 시퀀스 재구성 및 시뮬레이션
- 가상 시나리오 학습
- 패턴 발견 및 전략 최적화
- 메타인지 루프와 통합된 학습
"""

import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Iterator
from dataclasses import dataclass, asdict
from pathlib import Path
import re

# EchoJudgmentSystem 모듈
try:
    from echo_engine.meta_logger import log_evolution_event, get_meta_log_writer
except ImportError:
    log_evolution_event = None
    get_meta_log_writer = None

try:
    from echo_engine.persona_meta_logger import get_persona_meta_logger
except ImportError:
    get_persona_meta_logger = None

try:
    from feedback_system import FeedbackSystem
except ImportError:
    FeedbackSystem = None

try:
    from echo_engine.reinforcement_engine import get_reinforcement_engine
except ImportError:
    get_reinforcement_engine = None


@dataclass
class DecisionStep:
    """개별 결정 단계 정의"""

    timestamp: str
    step_id: str
    input_text: str
    context: Dict[str, Any]
    emotion_detected: str
    strategy_selected: str
    confidence: float
    reasoning: str
    response_generated: str
    user_feedback: Optional[Dict[str, Any]] = None
    success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplaySession:
    """리플레이 세션 정의"""

    session_id: str
    start_time: str
    end_time: str
    total_steps: int
    success_rate: float
    average_confidence: float
    dominant_emotions: List[str]
    strategies_used: List[str]
    decision_sequence: List[DecisionStep]
    meta_insights: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "decision_sequence": [step.to_dict() for step in self.decision_sequence],
        }


class ReplayLearner:
    """
    EchoJudgmentSystem 리플레이 학습기

    과거의 판단 세션들을 재현하고 분석하여
    시스템의 의사결정 능력을 향상시킵니다.
    """

    def __init__(self, log_directory: str = "meta_logs"):
        """
        리플레이 학습기 초기화

        Args:
            log_directory: 로그 파일들이 저장된 디렉토리
        """
        self.log_directory = Path(log_directory)
        self.history: List[ReplaySession] = []
        self.learned_patterns: Dict[str, Any] = {}
        self.simulation_results: List[Dict[str, Any]] = []

        # 학습 설정
        self.replay_batch_size = 5
        self.pattern_threshold = 0.7
        self.max_simulations = 100

        # 통계
        self.total_replays = 0
        self.successful_replays = 0
        self.patterns_discovered = 0

        # 초기화
        self.load_learned_patterns()

        print("🔁 ReplayLearner 초기화 완료")

    def load_session(self, session_id: str) -> Optional[ReplaySession]:
        """
        특정 세션 데이터를 로드하고 파싱

        Args:
            session_id: 로드할 세션 ID

        Returns:
            파싱된 ReplaySession 객체 또는 None
        """
        try:
            # 세션 로그 파일 찾기
            session_files = list(self.log_directory.glob(f"*{session_id}*"))

            if not session_files:
                print(f"⚠️ 세션 {session_id} 로그 파일을 찾을 수 없음")
                return None

            session_file = session_files[0]

            # JSONL 파일 읽기
            decision_steps = []
            session_meta = {}

            with open(session_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    try:
                        data = json.loads(line.strip())

                        if data.get("event_type") == "session_start":
                            session_meta["start_time"] = data.get("timestamp")
                        elif data.get("event_type") == "session_end":
                            session_meta["end_time"] = data.get("timestamp")
                        elif data.get("event_type") == "persona_interaction":
                            # 개별 결정 단계로 변환
                            step = self._convert_to_decision_step(data, line_num)
                            if step:
                                decision_steps.append(step)

                    except json.JSONDecodeError:
                        continue

            if not decision_steps:
                print(f"⚠️ 세션 {session_id}에서 유효한 결정 단계를 찾을 수 없음")
                return None

            # ReplaySession 생성
            replay_session = self._create_replay_session(
                session_id, session_meta, decision_steps
            )

            print(f"📁 세션 로드 완료: {session_id} ({len(decision_steps)}개 단계)")
            return replay_session

        except Exception as e:
            print(f"❌ 세션 로드 실패 {session_id}: {e}")
            return None

    def reconstruct_decision_sequence(
        self, session_data: ReplaySession
    ) -> List[Dict[str, Any]]:
        """
        결정 시퀀스를 재구성하고 시뮬레이션

        Args:
            session_data: 재구성할 세션 데이터

        Returns:
            시뮬레이션 결과 리스트
        """
        try:
            simulation_results = []

            print(f"🎭 결정 시퀀스 재구성 시작: {session_data.session_id}")

            # 각 결정 단계를 순차적으로 시뮬레이션
            for i, step in enumerate(session_data.decision_sequence):
                print(
                    f"   단계 {i+1}/{len(session_data.decision_sequence)}: {step.strategy_selected}"
                )

                # 현재 단계 시뮬레이션
                sim_result = self._simulate_decision_step(step, i, session_data)
                simulation_results.append(sim_result)

                # 패턴 학습
                self._learn_from_step(step, sim_result)

                # 진행 상황 표시
                if (i + 1) % 5 == 0:
                    success_rate = sum(
                        1 for r in simulation_results if r["simulation_success"]
                    ) / len(simulation_results)
                    print(
                        f"   진행률: {i+1}/{len(session_data.decision_sequence)} (성공률: {success_rate:.2f})"
                    )

            # 전체 시퀀스 분석
            sequence_analysis = self._analyze_decision_sequence(
                simulation_results, session_data
            )

            # 학습 결과 저장
            self.simulation_results.extend(simulation_results)
            self.total_replays += 1

            overall_success = sequence_analysis["overall_success_rate"] > 0.6
            if overall_success:
                self.successful_replays += 1

            # 메타 로깅
            self._log_replay_event(session_data, sequence_analysis)

            print(f"✅ 시퀀스 재구성 완료: {len(simulation_results)}개 단계 시뮬레이션")
            return simulation_results

        except Exception as e:
            print(f"❌ 결정 시퀀스 재구성 실패: {e}")
            return []

    def replay_multiple_sessions(
        self, session_ids: List[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        여러 세션을 일괄 리플레이하여 패턴 학습

        Args:
            session_ids: 특정 세션 ID 리스트 (None이면 자동 발견)
            limit: 최대 리플레이할 세션 수

        Returns:
            종합 학습 결과
        """
        try:
            if session_ids is None:
                session_ids = self._discover_session_ids(limit)

            print(f"🔄 다중 세션 리플레이 시작: {len(session_ids)}개 세션")

            all_results = []
            successful_sessions = 0

            for i, session_id in enumerate(session_ids[:limit]):
                print(f"\n📂 세션 {i+1}/{len(session_ids[:limit])}: {session_id}")

                # 세션 로드
                session = self.load_session(session_id)
                if not session:
                    continue

                # 결정 시퀀스 재구성
                results = self.reconstruct_decision_sequence(session)

                if results:
                    all_results.extend(results)
                    successful_sessions += 1

                    # 중간 패턴 분석
                    if (i + 1) % 3 == 0:
                        self._update_learned_patterns()

            # 최종 패턴 업데이트
            self._update_learned_patterns()

            # 종합 분석
            comprehensive_analysis = self._perform_comprehensive_analysis(all_results)

            # 학습 결과 저장
            self.save_learned_patterns()

            print(f"\n✅ 다중 세션 리플레이 완료:")
            print(f"   처리된 세션: {successful_sessions}/{len(session_ids[:limit])}")
            print(f"   총 결정 단계: {len(all_results)}")
            print(f"   발견된 패턴: {self.patterns_discovered}")

            return comprehensive_analysis

        except Exception as e:
            print(f"❌ 다중 세션 리플레이 실패: {e}")
            return {}

    def generate_synthetic_scenarios(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        학습된 패턴을 기반으로 가상 시나리오 생성

        Args:
            count: 생성할 시나리오 수

        Returns:
            생성된 시나리오 리스트
        """
        try:
            scenarios = []

            print(f"🎲 가상 시나리오 생성: {count}개")

            for i in range(count):
                scenario = self._create_synthetic_scenario(i)

                if scenario:
                    scenarios.append(scenario)
                    print(
                        f"   시나리오 {i+1}: {scenario['context_type']} / {scenario['emotion_pattern']}"
                    )

            print(f"✅ 가상 시나리오 생성 완료: {len(scenarios)}개")
            return scenarios

        except Exception as e:
            print(f"❌ 가상 시나리오 생성 실패: {e}")
            return []

    def _convert_to_decision_step(
        self, log_data: Dict[str, Any], step_id: int
    ) -> Optional[DecisionStep]:
        """로그 데이터를 DecisionStep으로 변환"""
        try:
            return DecisionStep(
                timestamp=log_data.get("timestamp", datetime.now().isoformat()),
                step_id=f"step_{step_id}",
                input_text=log_data.get("input_text", ""),
                context=log_data.get("context", {}),
                emotion_detected=log_data.get("emotion_detected", "neutral"),
                strategy_selected=log_data.get("strategy_selected", "balanced"),
                confidence=log_data.get("strategy_confidence", 0.5),
                reasoning=log_data.get("reasoning", ""),
                response_generated=log_data.get("response_generated", ""),
                user_feedback=log_data.get("user_feedback"),
                success=log_data.get("strategy_effectiveness", 0.5) > 0.6,
            )
        except Exception:
            return None

    def _create_replay_session(
        self, session_id: str, meta: Dict[str, Any], steps: List[DecisionStep]
    ) -> ReplaySession:
        """DecisionStep 리스트로부터 ReplaySession 생성"""
        successful_steps = sum(1 for step in steps if step.success)
        success_rate = successful_steps / len(steps) if steps else 0.0

        confidences = [step.confidence for step in steps if step.confidence > 0]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        emotions = [step.emotion_detected for step in steps]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        dominant_emotions = sorted(
            emotion_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]
        dominant_emotions = [emotion for emotion, count in dominant_emotions]

        strategies = list(set(step.strategy_selected for step in steps))

        return ReplaySession(
            session_id=session_id,
            start_time=meta.get("start_time", ""),
            end_time=meta.get("end_time", ""),
            total_steps=len(steps),
            success_rate=success_rate,
            average_confidence=average_confidence,
            dominant_emotions=dominant_emotions,
            strategies_used=strategies,
            decision_sequence=steps,
            meta_insights={},
        )

    def _simulate_decision_step(
        self, step: DecisionStep, step_index: int, session: ReplaySession
    ) -> Dict[str, Any]:
        """개별 결정 단계 시뮬레이션"""
        simulation_start = time.time()

        # 현재 컨텍스트에서 최적 전략 예측
        predicted_strategy = self._predict_optimal_strategy(step, session)

        # 실제 선택과 예측 비교
        strategy_match = predicted_strategy == step.strategy_selected

        # 결과 효과성 예측
        predicted_success = self._predict_step_success(step, predicted_strategy)

        # 시뮬레이션 성공 여부 (예측 정확도 기반)
        simulation_success = strategy_match and (predicted_success == step.success)

        simulation_time = time.time() - simulation_start

        return {
            "step_index": step_index,
            "original_strategy": step.strategy_selected,
            "predicted_strategy": predicted_strategy,
            "strategy_match": strategy_match,
            "original_success": step.success,
            "predicted_success": predicted_success,
            "simulation_success": simulation_success,
            "confidence_delta": abs(
                step.confidence - self._calculate_predicted_confidence(step)
            ),
            "simulation_time": simulation_time,
            "learning_insights": self._extract_step_insights(step, predicted_strategy),
        }

    def _predict_optimal_strategy(
        self, step: DecisionStep, session: ReplaySession
    ) -> str:
        """현재 상황에서 최적 전략 예측"""
        # 학습된 패턴 기반 예측
        context_key = (
            f"{step.context.get('context_type', 'general')}:{step.emotion_detected}"
        )

        if context_key in self.learned_patterns:
            pattern = self.learned_patterns[context_key]
            best_strategies = pattern.get("best_strategies", [])
            if best_strategies:
                return best_strategies[0]

        # 세션 내 성공 패턴 기반 예측
        successful_strategies = [
            s.strategy_selected
            for s in session.decision_sequence
            if s.success and s.emotion_detected == step.emotion_detected
        ]

        if successful_strategies:
            strategy_counts = {}
            for strategy in successful_strategies:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            return max(strategy_counts.items(), key=lambda x: x[1])[0]

        # 기본값
        return "balanced"

    def _predict_step_success(self, step: DecisionStep, strategy: str) -> bool:
        """단계 성공 여부 예측"""
        # 전략별 성공률 기반 예측
        context_key = f"{step.context.get('context_type', 'general')}:{step.emotion_detected}:{strategy}"

        if context_key in self.learned_patterns:
            success_rate = self.learned_patterns[context_key].get("success_rate", 0.5)
            return success_rate > 0.6

        # 신뢰도 기반 예측
        return step.confidence > 0.7

    def _calculate_predicted_confidence(self, step: DecisionStep) -> float:
        """예측 신뢰도 계산"""
        base_confidence = 0.5

        # 감정 안정성 가중치
        emotion_weights = {
            "joy": 0.8,
            "neutral": 0.7,
            "curiosity": 0.75,
            "sadness": 0.4,
            "anger": 0.3,
            "fear": 0.2,
        }
        emotion_weight = emotion_weights.get(step.emotion_detected, 0.5)

        # 컨텍스트 복잡도 가중치
        context_complexity = len(step.context)
        complexity_weight = max(0.3, 1.0 - context_complexity * 0.1)

        return min(1.0, base_confidence * emotion_weight * complexity_weight)

    def _extract_step_insights(
        self, step: DecisionStep, predicted_strategy: str
    ) -> List[str]:
        """단계별 학습 인사이트 추출"""
        insights = []

        if step.success:
            insights.append(
                f"Successful pattern: {step.emotion_detected} + {step.strategy_selected}"
            )

        if predicted_strategy != step.strategy_selected:
            insights.append(
                f"Strategy mismatch: predicted {predicted_strategy}, used {step.strategy_selected}"
            )

        if step.confidence < 0.5:
            insights.append("Low confidence decision - needs pattern reinforcement")

        return insights

    def _learn_from_step(self, step: DecisionStep, sim_result: Dict[str, Any]):
        """개별 단계에서 패턴 학습"""
        context_key = (
            f"{step.context.get('context_type', 'general')}:{step.emotion_detected}"
        )
        strategy_key = f"{context_key}:{step.strategy_selected}"

        # 컨텍스트-감정 패턴 학습
        if context_key not in self.learned_patterns:
            self.learned_patterns[context_key] = {
                "occurrences": 0,
                "successful_strategies": [],
                "best_strategies": [],
                "average_confidence": 0.0,
                "confidence_variance": 0.0,
            }

        pattern = self.learned_patterns[context_key]
        pattern["occurrences"] += 1

        if step.success:
            pattern["successful_strategies"].append(step.strategy_selected)

        # 전략별 세부 패턴 학습
        if strategy_key not in self.learned_patterns:
            self.learned_patterns[strategy_key] = {
                "uses": 0,
                "successes": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0,
                "contexts": [],
            }

        strategy_pattern = self.learned_patterns[strategy_key]
        strategy_pattern["uses"] += 1
        if step.success:
            strategy_pattern["successes"] += 1
        strategy_pattern["success_rate"] = (
            strategy_pattern["successes"] / strategy_pattern["uses"]
        )
        strategy_pattern["contexts"].append(step.context)

    def _analyze_decision_sequence(
        self, sim_results: List[Dict[str, Any]], session: ReplaySession
    ) -> Dict[str, Any]:
        """전체 결정 시퀀스 분석"""
        total_steps = len(sim_results)
        successful_sims = sum(1 for r in sim_results if r["simulation_success"])
        strategy_matches = sum(1 for r in sim_results if r["strategy_match"])

        return {
            "session_id": session.session_id,
            "total_simulation_steps": total_steps,
            "successful_simulations": successful_sims,
            "overall_success_rate": (
                successful_sims / total_steps if total_steps > 0 else 0
            ),
            "strategy_prediction_accuracy": (
                strategy_matches / total_steps if total_steps > 0 else 0
            ),
            "average_confidence_delta": (
                sum(r["confidence_delta"] for r in sim_results) / total_steps
                if total_steps > 0
                else 0
            ),
            "total_simulation_time": sum(r["simulation_time"] for r in sim_results),
            "learning_insights_count": sum(
                len(r["learning_insights"]) for r in sim_results
            ),
            "pattern_quality_score": self._calculate_pattern_quality_score(sim_results),
        }

    def _calculate_pattern_quality_score(
        self, sim_results: List[Dict[str, Any]]
    ) -> float:
        """패턴 학습 품질 점수 계산"""
        if not sim_results:
            return 0.0

        accuracy = sum(1 for r in sim_results if r["simulation_success"]) / len(
            sim_results
        )
        consistency = 1.0 - (
            sum(r["confidence_delta"] for r in sim_results) / len(sim_results)
        )

        return accuracy * 0.7 + consistency * 0.3

    def _update_learned_patterns(self):
        """학습된 패턴 업데이트 및 정제"""
        updated_patterns = 0

        for key, pattern in self.learned_patterns.items():
            if (
                "successful_strategies" in pattern
                and len(pattern["successful_strategies"]) > 2
            ):
                # 최고 성과 전략들 업데이트
                strategy_counts = {}
                for strategy in pattern["successful_strategies"]:
                    strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

                sorted_strategies = sorted(
                    strategy_counts.items(), key=lambda x: x[1], reverse=True
                )
                pattern["best_strategies"] = [
                    strategy for strategy, count in sorted_strategies[:3]
                ]
                updated_patterns += 1

        self.patterns_discovered = updated_patterns
        print(f"🧠 패턴 업데이트: {updated_patterns}개 컨텍스트")

    def _perform_comprehensive_analysis(
        self, all_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """종합 분석 수행"""
        if not all_results:
            return {}

        total_steps = len(all_results)
        successful_sims = sum(1 for r in all_results if r["simulation_success"])

        # 전략별 성과 분석
        strategy_performance = {}
        for result in all_results:
            strategy = result["predicted_strategy"]
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {"uses": 0, "successes": 0}

            strategy_performance[strategy]["uses"] += 1
            if result["simulation_success"]:
                strategy_performance[strategy]["successes"] += 1

        # 성과 계산
        for strategy in strategy_performance:
            perf = strategy_performance[strategy]
            perf["success_rate"] = (
                perf["successes"] / perf["uses"] if perf["uses"] > 0 else 0
            )

        return {
            "total_replayed_steps": total_steps,
            "overall_simulation_success_rate": successful_sims / total_steps,
            "strategy_performance": strategy_performance,
            "patterns_learned": len(self.learned_patterns),
            "replay_sessions": self.total_replays,
            "successful_replays": self.successful_replays,
            "replay_success_rate": self.successful_replays / max(1, self.total_replays),
            "learning_quality_score": self._calculate_overall_quality_score(
                all_results
            ),
        }

    def _calculate_overall_quality_score(self, results: List[Dict[str, Any]]) -> float:
        """전체 학습 품질 점수 계산"""
        if not results:
            return 0.0

        simulation_accuracy = sum(1 for r in results if r["simulation_success"]) / len(
            results
        )
        pattern_coverage = min(
            1.0, len(self.learned_patterns) / 20
        )  # 20개 패턴을 기준으로
        learning_depth = min(1.0, self.total_replays / 10)  # 10개 세션을 기준으로

        return simulation_accuracy * 0.5 + pattern_coverage * 0.3 + learning_depth * 0.2

    def _discover_session_ids(self, limit: int) -> List[str]:
        """로그 디렉토리에서 세션 ID들 자동 발견"""
        session_ids = []

        try:
            for log_file in self.log_directory.glob("*.jsonl"):
                # 파일명에서 세션 ID 추출 시도
                filename = log_file.name

                # persona_session_YYYYMMDD_HHMMSS_UUID.jsonl 패턴
                session_match = re.search(r"session_(\d{8}_\d{6}_[a-f0-9]+)", filename)
                if session_match:
                    session_ids.append(session_match.group(1))
                    continue

                # 기타 패턴들
                meta_match = re.search(r"meta_session_(\d+)", filename)
                if meta_match:
                    session_ids.append(meta_match.group(1))

            # 중복 제거 및 정렬
            session_ids = sorted(list(set(session_ids)))[:limit]

        except Exception as e:
            print(f"⚠️ 세션 ID 자동 발견 실패: {e}")

        return session_ids

    def _create_synthetic_scenario(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """가상 시나리오 생성"""
        try:
            # 학습된 패턴에서 랜덤 선택
            if not self.learned_patterns:
                return None

            context_patterns = [
                k
                for k in self.learned_patterns.keys()
                if ":" in k and len(k.split(":")) == 2
            ]
            if not context_patterns:
                return None

            pattern_key = random.choice(context_patterns)
            context_type, emotion = pattern_key.split(":")

            pattern = self.learned_patterns[pattern_key]
            best_strategies = pattern.get("best_strategies", ["balanced"])

            return {
                "scenario_id": f"synthetic_{scenario_id}",
                "context_type": context_type,
                "emotion_pattern": emotion,
                "recommended_strategies": best_strategies,
                "expected_success_rate": pattern.get("success_rate", 0.5),
                "confidence_baseline": pattern.get("average_confidence", 0.5),
                "learning_source": "replay_learning",
                "created_at": datetime.now().isoformat(),
            }

        except Exception:
            return None

    def _log_replay_event(self, session: ReplaySession, analysis: Dict[str, Any]):
        """리플레이 학습 이벤트 로깅"""
        try:
            if log_evolution_event:
                event_data = {
                    "event": "Replay Learning Session",
                    "tag": ["replay_learning", "pattern_discovery", "simulation"],
                    "cause": [
                        f"session_{session.session_id}",
                        f"steps_{session.total_steps}",
                    ],
                    "effect": [
                        f"patterns_learned",
                        f"simulation_accuracy_{analysis.get('overall_success_rate', 0):.2f}",
                    ],
                    "resolution": "learning_patterns_updated",
                    "insight": f"Replay learning from {session.total_steps} decision steps",
                    "adaptation_strength": analysis.get("pattern_quality_score", 0.5),
                    "coherence_improvement": analysis.get("overall_success_rate", 0.5),
                    "reflection_depth": 2,
                }
                log_evolution_event(event_data, f"replay_{session.session_id}")

        except Exception as e:
            print(f"⚠️ 리플레이 이벤트 로깅 실패: {e}")

    def get_replay_statistics(self) -> Dict[str, Any]:
        """리플레이 학습 통계 반환"""
        return {
            "total_replays": self.total_replays,
            "successful_replays": self.successful_replays,
            "replay_success_rate": self.successful_replays / max(1, self.total_replays),
            "patterns_discovered": self.patterns_discovered,
            "learned_patterns_count": len(self.learned_patterns),
            "simulation_results_count": len(self.simulation_results),
            "avg_pattern_quality": self._calculate_average_pattern_quality(),
        }

    def _calculate_average_pattern_quality(self) -> float:
        """평균 패턴 품질 계산"""
        if not self.learned_patterns:
            return 0.0

        quality_scores = []
        for pattern in self.learned_patterns.values():
            if "success_rate" in pattern:
                quality_scores.append(pattern["success_rate"])

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

    def save_learned_patterns(
        self, filepath: str = "data/replay_learned_patterns.json"
    ):
        """학습된 패턴 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            save_data = {
                "learned_patterns": self.learned_patterns,
                "statistics": self.get_replay_statistics(),
                "last_updated": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"💾 학습 패턴 저장 완료: {filepath}")

        except Exception as e:
            print(f"❌ 학습 패턴 저장 실패: {e}")

    def load_learned_patterns(
        self, filepath: str = "data/replay_learned_patterns.json"
    ):
        """학습된 패턴 로드"""
        try:
            if not os.path.exists(filepath):
                print(f"📁 학습 패턴 파일 없음, 새로 시작: {filepath}")
                return

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.learned_patterns = data.get("learned_patterns", {})

            stats = data.get("statistics", {})
            self.total_replays = stats.get("total_replays", 0)
            self.successful_replays = stats.get("successful_replays", 0)
            self.patterns_discovered = stats.get("patterns_discovered", 0)

            print(f"📂 학습 패턴 로드 완료: {len(self.learned_patterns)}개 패턴")

        except Exception as e:
            print(f"❌ 학습 패턴 로드 실패: {e}")


# 글로벌 인스턴스
_replay_learner = None


def get_replay_learner() -> ReplayLearner:
    """글로벌 리플레이 학습기 인스턴스 반환"""
    global _replay_learner
    if _replay_learner is None:
        _replay_learner = ReplayLearner()
    return _replay_learner


def replay_session(session_id: str) -> Dict[str, Any]:
    """편의 함수: 세션 리플레이"""
    learner = get_replay_learner()
    session = learner.load_session(session_id)
    if session:
        return learner.reconstruct_decision_sequence(session)
    return {}


def batch_replay_learning(session_limit: int = 5) -> Dict[str, Any]:
    """편의 함수: 일괄 리플레이 학습"""
    learner = get_replay_learner()
    return learner.replay_multiple_sessions(limit=session_limit)
