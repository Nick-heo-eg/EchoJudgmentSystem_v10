"""
🧬 Capsule Stacking System
캡슐 조합 및 스택 실행 시스템
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from .capsule_models import CapsuleSpec, ExecutionContext, SimulationResult, CapsuleType
from .capsule_cli import CapsuleEngine


@dataclass
class CapsuleStackResult:
    """캡슐 스택 실행 결과"""

    stack_name: str
    input_context: ExecutionContext
    capsule_results: List[SimulationResult] = field(default_factory=list)

    # 통합 결과
    combined_actions: List[str] = field(default_factory=list)
    combined_emotional_state: Dict[str, float] = field(default_factory=dict)
    stack_confidence: float = 0.0
    synergy_score: float = 0.0

    # 메트릭
    total_execution_time_ms: float = 0.0
    capsules_triggered: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class CapsuleStackEngine:
    """캡슐 스택 실행 엔진"""

    def __init__(self, registry_path: str = "data/capsule_registry.json"):
        self.engine = CapsuleEngine(registry_path)
        self.stacks_path = Path("data/capsule_stacks.json")
        self.stacks_path.parent.mkdir(parents=True, exist_ok=True)
        self.stacks = self._load_stacks()

    def _load_stacks(self) -> Dict[str, List[str]]:
        """저장된 스택 구성 로드"""
        if self.stacks_path.exists():
            try:
                with open(self.stacks_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_stacks(self):
        """스택 구성 저장"""
        with open(self.stacks_path, "w", encoding="utf-8") as f:
            json.dump(self.stacks, f, indent=2, ensure_ascii=False)

    def create_stack(self, stack_name: str, capsule_names: List[str]) -> bool:
        """새 캡슐 스택 생성"""
        # 캡슐들 존재 여부 확인
        missing_capsules = []
        for name in capsule_names:
            if not self.engine.registry.get_capsule(name):
                missing_capsules.append(name)

        if missing_capsules:
            raise ValueError(f"존재하지 않는 캡슐들: {', '.join(missing_capsules)}")

        self.stacks[stack_name] = capsule_names
        self._save_stacks()
        return True

    def execute_stack(
        self, stack_name: str, context: ExecutionContext
    ) -> CapsuleStackResult:
        """캡슐 스택 실행"""
        if stack_name not in self.stacks:
            raise ValueError(f"스택 '{stack_name}'을 찾을 수 없습니다")

        capsule_names = self.stacks[stack_name]
        result = CapsuleStackResult(stack_name=stack_name, input_context=context)

        start_time = datetime.now()

        # 각 캡슐 순차 실행
        for capsule_name in capsule_names:
            capsule = self.engine.registry.get_capsule(capsule_name)
            if capsule:
                try:
                    capsule_result = self.engine.simulate_capsule(capsule, context)
                    result.capsule_results.append(capsule_result)

                    # 결과 누적
                    result.combined_actions.extend(capsule_result.output_actions)

                    # 감정 상태 병합
                    for emotion, value in capsule_result.emotional_state.items():
                        if emotion in result.combined_emotional_state:
                            result.combined_emotional_state[emotion] = (
                                result.combined_emotional_state[emotion] + value
                            ) / 2  # 평균화
                        else:
                            result.combined_emotional_state[emotion] = value

                    if capsule_result.triggered_rules:
                        result.capsules_triggered += 1

                except Exception as e:
                    # 실패한 캡슐도 기록
                    failed_result = SimulationResult(
                        capsule_name=capsule_name,
                        input_context=context,
                        triggered_rules=[f"ERROR: {str(e)}"],
                        output_actions=[],
                        emotional_state={},
                        execution_time_ms=0.0,
                        confidence_score=0.0,
                    )
                    result.capsule_results.append(failed_result)

        # 전체 메트릭 계산
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        result.total_execution_time_ms = execution_time

        # 스택 신뢰도 계산
        if result.capsule_results:
            confidences = [
                r.confidence_score
                for r in result.capsule_results
                if r.confidence_score > 0
            ]
            result.stack_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )

        # 시너지 점수 계산
        result.synergy_score = self._calculate_synergy(result.capsule_results)

        return result

    def _calculate_synergy(self, capsule_results: List[SimulationResult]) -> float:
        """캡슐 간 시너지 점수 계산"""
        if len(capsule_results) < 2:
            return 0.0

        synergy = 0.0

        # 1. 서로 다른 타입의 캡슐이 함께 작동할 때 시너지 보너스
        capsule_names = [r.capsule_name for r in capsule_results if r.triggered_rules]
        if len(set(capsule_names)) >= 2:
            synergy += 0.2

        # 2. 많은 규칙이 트리거될수록 시너지 증가
        total_triggered = sum(len(r.triggered_rules) for r in capsule_results)
        if total_triggered >= 3:
            synergy += min(0.3, total_triggered * 0.05)

        # 3. 높은 신뢰도들이 조합될 때 시너지 증가
        high_confidence_count = sum(
            1 for r in capsule_results if r.confidence_score > 0.6
        )
        if high_confidence_count >= 2:
            synergy += 0.2

        # 4. 감정 상태의 다양성이 높을 때 시너지 증가
        all_emotions = set()
        for result in capsule_results:
            all_emotions.update(result.emotional_state.keys())
        if len(all_emotions) >= 4:
            synergy += 0.1

        return min(1.0, synergy)

    def get_stack_info(self, stack_name: str) -> Dict[str, Any]:
        """스택 정보 조회"""
        if stack_name not in self.stacks:
            return None

        capsule_names = self.stacks[stack_name]
        capsule_info = []

        for name in capsule_names:
            capsule = self.engine.registry.get_capsule(name)
            if capsule:
                capsule_info.append(
                    {
                        "name": capsule.name,
                        "type": capsule.type.value,
                        "rules_count": len(capsule.rules),
                        "description": capsule.description,
                    }
                )

        return {
            "stack_name": stack_name,
            "capsules": capsule_info,
            "total_capsules": len(capsule_names),
            "stack_composition": self._analyze_stack_composition(capsule_names),
        }

    def _analyze_stack_composition(self, capsule_names: List[str]) -> Dict[str, Any]:
        """스택 구성 분석"""
        types = []
        total_rules = 0

        for name in capsule_names:
            capsule = self.engine.registry.get_capsule(name)
            if capsule:
                types.append(capsule.type.value)
                total_rules += len(capsule.rules)

        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "type_distribution": type_counts,
            "total_rules": total_rules,
            "avg_rules_per_capsule": (
                total_rules / len(capsule_names) if capsule_names else 0
            ),
            "diversity_score": len(set(types)) / len(types) if types else 0,
        }

    def list_stacks(self) -> List[str]:
        """생성된 스택 목록"""
        return list(self.stacks.keys())

    def remove_stack(self, stack_name: str) -> bool:
        """스택 제거"""
        if stack_name in self.stacks:
            del self.stacks[stack_name]
            self._save_stacks()
            return True
        return False

    def suggest_complementary_capsules(self, existing_capsules: List[str]) -> List[str]:
        """기존 캡슐들에 보완적인 캡슐 추천"""
        all_capsules = self.engine.registry.list_capsules()
        existing_types = set()

        # 기존 캡슐들의 타입 분석
        for name in existing_capsules:
            capsule = self.engine.registry.get_capsule(name)
            if capsule:
                existing_types.add(capsule.type)

        # 부족한 타입 찾기
        all_types = {
            CapsuleType.EMOTION,
            CapsuleType.SIGNATURE,
            CapsuleType.COGNITIVE,
            CapsuleType.HYBRID,
        }
        missing_types = all_types - existing_types

        suggestions = []
        for capsule in all_capsules:
            if capsule.name not in existing_capsules and capsule.type in missing_types:
                suggestions.append(capsule.name)

        return suggestions[:3]  # 최대 3개 추천

    def optimize_stack_order(self, capsule_names: List[str]) -> List[str]:
        """캡슐 실행 순서 최적화"""
        capsules_with_priority = []

        for name in capsule_names:
            capsule = self.engine.registry.get_capsule(name)
            if capsule:
                # 타입별 기본 우선순위
                type_priority = {
                    CapsuleType.SIGNATURE: 1,  # 시그니처가 기본 토대
                    CapsuleType.EMOTION: 2,  # 감정이 다음
                    CapsuleType.COGNITIVE: 3,  # 인지가 그 다음
                    CapsuleType.HYBRID: 4,  # 하이브리드가 마지막
                }.get(capsule.type, 5)

                # 규칙 수가 많을수록 더 높은 우선순위
                rule_priority = len(capsule.rules) * 0.1

                total_priority = type_priority + rule_priority
                capsules_with_priority.append((name, total_priority))

        # 우선순위로 정렬
        capsules_with_priority.sort(key=lambda x: x[1])
        return [name for name, _ in capsules_with_priority]
