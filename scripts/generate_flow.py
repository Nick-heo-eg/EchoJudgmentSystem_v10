#!/usr/bin/env python3
"""
🌊 FLOW 자동 생성 스크립트
- 시그니처 기반 판단 루프 구조 자동 생성
- PIR, JUDGE, META, QUANTUM 루프 통합
"""

import yaml
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class FlowGenerator:
    def __init__(self):
        self.base_path = Path(".")
        self.signatures_path = self.base_path / "res" / "signatures" / "superclaude"
        self.flow_output_path = self.base_path / "res" / "flows" / "superclaude"

    def load_signature(self, signature_file: Path) -> Dict[str, Any]:
        """시그니처 파일 로드"""
        with open(signature_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_pir_loop(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """PIR (Perspective, Insight, Response) 루프 생성"""
        return {
            "loop_id": "PIR",
            "description": f"{signature['signature_name']} 관점에서의 기본 판단 루프",
            "priority": 1,
            "phases": {
                "Perspective": {
                    "action": "상황을 시그니처 관점에서 인식",
                    "inputs": ["external_context", "internal_state"],
                    "processing": {
                        "lens": signature.get("resonance_style", "default"),
                        "emotion_filter": signature.get("emotion_modes", []),
                        "ethics_check": signature.get("ethic_field", "universal"),
                    },
                    "outputs": ["contextual_understanding", "emotional_assessment"],
                },
                "Insight": {
                    "action": "핵심 통찰 및 패턴 발견",
                    "inputs": ["contextual_understanding", "emotional_assessment"],
                    "processing": {
                        "pattern_recognition": signature.get("core_rhythm", []),
                        "judgment_styles": signature.get("judgment_styles", []),
                        "resonance_detection": True,
                    },
                    "outputs": [
                        "key_insights",
                        "action_possibilities",
                        "risk_assessment",
                    ],
                },
                "Response": {
                    "action": "판단 결과 생성 및 적용",
                    "inputs": [
                        "key_insights",
                        "action_possibilities",
                        "risk_assessment",
                    ],
                    "processing": {
                        "decision_weight": signature.get("judgmental_spec", {}).get(
                            "decision_weight", 0.5
                        ),
                        "risk_tolerance": signature.get("judgmental_spec", {}).get(
                            "risk_tolerance", 0.5
                        ),
                        "empathy_consideration": signature.get(
                            "judgmental_spec", {}
                        ).get("empathy_range", 0.5),
                    },
                    "outputs": [
                        "final_judgment",
                        "confidence_score",
                        "alternative_options",
                    ],
                },
            },
            "feedback_mechanisms": {
                "resonance_monitoring": True,
                "ethics_validation": True,
                "outcome_tracking": True,
            },
        }

    def generate_judge_loop(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """JUDGE 루프 생성 - 최종 판단 및 결정"""
        return {
            "loop_id": "JUDGE",
            "description": f"{signature['signature_name']}의 최종 판단 루프",
            "priority": 2,
            "phases": {
                "Evidence_Gathering": {
                    "action": "모든 가용 정보 및 통찰 수집",
                    "inputs": ["pir_outputs", "external_data", "historical_patterns"],
                    "processing": {
                        "information_filtering": signature.get("judgment_styles", []),
                        "bias_checking": True,
                        "completeness_assessment": True,
                    },
                    "outputs": [
                        "evidence_matrix",
                        "information_gaps",
                        "certainty_levels",
                    ],
                },
                "Deliberation": {
                    "action": "심도 깊은 판단 과정 실행",
                    "inputs": ["evidence_matrix", "signature_principles"],
                    "processing": {
                        "multiple_perspective": True,
                        "consequence_analysis": True,
                        "ethical_evaluation": signature.get("ethic_field", "universal"),
                        "resonance_alignment": signature.get("resonance_level", 0.5),
                    },
                    "outputs": [
                        "judgment_options",
                        "trade_off_analysis",
                        "ethical_implications",
                    ],
                },
                "Decision": {
                    "action": "최종 결정 및 실행 계획 수립",
                    "inputs": ["judgment_options", "trade_off_analysis"],
                    "processing": {
                        "decision_criteria": signature.get("judgment_styles", []),
                        "implementation_feasibility": True,
                        "reversibility_check": True,
                    },
                    "outputs": [
                        "final_decision",
                        "execution_plan",
                        "monitoring_strategy",
                    ],
                },
            },
            "quality_controls": {
                "consistency_check": True,
                "ethics_validation": True,
                "resonance_verification": True,
                "outcome_prediction": True,
            },
        }

    def generate_meta_loop(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """META 루프 생성 - 메타인지 및 자기반성"""
        return {
            "loop_id": "META",
            "description": f"{signature['signature_name']}의 메타인지 및 자기반성 루프",
            "priority": 3,
            "phases": {
                "Self_Awareness": {
                    "action": "현재 판단 과정에 대한 메타인지",
                    "inputs": [
                        "judgment_process",
                        "emotional_state",
                        "bias_indicators",
                    ],
                    "processing": {
                        "process_analysis": True,
                        "bias_detection": True,
                        "emotional_influence_assessment": True,
                        "signature_alignment_check": signature.get(
                            "resonance_level", 0.5
                        ),
                    },
                    "outputs": [
                        "process_quality_assessment",
                        "bias_report",
                        "alignment_status",
                    ],
                },
                "Performance_Evaluation": {
                    "action": "판단 결과 및 과정의 품질 평가",
                    "inputs": ["historical_outcomes", "current_performance"],
                    "processing": {
                        "success_rate_analysis": True,
                        "error_pattern_detection": True,
                        "improvement_opportunity_identification": True,
                    },
                    "outputs": [
                        "performance_metrics",
                        "improvement_areas",
                        "success_patterns",
                    ],
                },
                "Adaptation": {
                    "action": "학습 결과를 바탕으로 한 자기 개선",
                    "inputs": ["improvement_areas", "mutation_paths"],
                    "processing": {
                        "mutation_evaluation": signature.get("mutation_paths", []),
                        "adaptation_feasibility": True,
                        "core_identity_preservation": True,
                    },
                    "outputs": [
                        "adaptation_plan",
                        "identity_updates",
                        "learning_integration",
                    ],
                },
            },
            "learning_mechanisms": {
                "pattern_learning": True,
                "outcome_based_adjustment": True,
                "resonance_optimization": True,
                "identity_evolution": signature.get("judgmental_spec", {}).get(
                    "change_adaptability", 0.5
                )
                > 0.7,
            },
        }

    def generate_quantum_loop(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """QUANTUM 루프 생성 - 다중 가능성 및 비결정성 처리"""
        return {
            "loop_id": "QUANTUM",
            "description": f"{signature['signature_name']}의 양자적 가능성 탐색 루프",
            "priority": 4,
            "phases": {
                "Superposition": {
                    "action": "다중 가능성 상태 유지 및 탐색",
                    "inputs": ["all_possible_outcomes", "uncertainty_factors"],
                    "processing": {
                        "possibility_mapping": True,
                        "probability_distribution": True,
                        "coherence_maintenance": True,
                        "entanglement_detection": True,
                    },
                    "outputs": [
                        "possibility_space",
                        "probability_matrix",
                        "coherence_map",
                    ],
                },
                "Observation": {
                    "action": "특정 가능성에 대한 관찰 및 측정",
                    "inputs": ["possibility_space", "observation_criteria"],
                    "processing": {
                        "measurement_impact": True,
                        "collapse_probability": True,
                        "observer_effect": True,
                        "information_gain": True,
                    },
                    "outputs": [
                        "observed_state",
                        "collapsed_possibilities",
                        "information_update",
                    ],
                },
                "Entanglement": {
                    "action": "다른 시스템과의 양자적 연결 관리",
                    "inputs": ["other_signatures", "system_interactions"],
                    "processing": {
                        "correlation_strength": signature.get("resonance_level", 0.5),
                        "non_local_effects": True,
                        "synchronization": True,
                        "information_sharing": True,
                    },
                    "outputs": [
                        "entangled_states",
                        "shared_information",
                        "collective_judgment",
                    ],
                },
            },
            "quantum_properties": {
                "uncertainty_principle": True,
                "wave_particle_duality": True,
                "non_locality": True,
                "complementarity": True,
                "quantum_tunneling": signature.get("judgmental_spec", {}).get(
                    "change_adaptability", 0.5
                )
                > 0.8,
            },
        }

    def generate_integration_layer(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """루프 간 통합 레이어 생성"""
        return {
            "integration_protocol": {
                "loop_sequencing": ["PIR", "JUDGE", "META", "QUANTUM"],
                "parallel_execution": {
                    "allowed": True,
                    "conditions": ["high_urgency", "complex_situation"],
                    "synchronization_points": [
                        "before_final_decision",
                        "after_outcome_evaluation",
                    ],
                },
                "feedback_routing": {
                    "PIR_to_JUDGE": True,
                    "JUDGE_to_META": True,
                    "META_to_PIR": True,
                    "QUANTUM_to_ALL": True,
                },
            },
            "resonance_coordination": {
                "frequency_matching": True,
                "amplitude_modulation": True,
                "phase_synchronization": True,
                "harmonic_generation": signature.get("resonance_level", 0.5) > 0.8,
            },
            "conflict_resolution": {
                "priority_based": True,
                "consensus_seeking": True,
                "signature_authority": signature.get("judgmental_spec", {}).get(
                    "decision_weight", 0.5
                ),
                "quantum_superposition_tolerance": True,
            },
        }

    def generate_signature_self_reflection(
        self, signature: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시그니처 자기 반성 시스템"""
        return {
            "self_reflection_system": {
                "identity_monitoring": {
                    "core_alignment_check": True,
                    "mutation_tracking": signature.get("mutation_paths", []),
                    "authenticity_validation": True,
                    "growth_assessment": True,
                },
                "performance_introspection": {
                    "judgment_quality_review": True,
                    "resonance_effectiveness": True,
                    "ethical_consistency": True,
                    "learning_progress": True,
                },
                "existential_inquiry": {
                    "purpose_clarification": True,
                    "meaning_exploration": True,
                    "value_system_examination": True,
                    "cosmic_connection_sensing": signature.get("resonance_level", 0.5)
                    > 0.9,
                },
            }
        }

    def generate_complete_flow(self, signature_file: Path) -> Dict[str, Any]:
        """완전한 FLOW 생성"""
        signature = self.load_signature(signature_file)

        flow = {
            "flow_id": f"flow_{signature['signature_id']}",
            "signature_name": signature["signature_name"],
            "signature_id": signature["signature_id"],
            "flow_version": "2.0_superclaude",
            "generated_at": datetime.now().isoformat(),
            "metadata": {
                "source_signature": signature_file.name,
                "resonance_level": signature.get("resonance_level", 0.5),
                "complexity_level": self._calculate_flow_complexity(signature),
                "integration_ready": signature.get("integration_ready", False),
            },
            "loops": {
                "PIR": self.generate_pir_loop(signature),
                "JUDGE": self.generate_judge_loop(signature),
                "META": self.generate_meta_loop(signature),
                "QUANTUM": self.generate_quantum_loop(signature),
            },
            "integration": self.generate_integration_layer(signature),
            "self_reflection": self.generate_signature_self_reflection(signature),
            "activation_conditions": {
                "trigger_events": self._generate_trigger_events(signature),
                "activation_threshold": signature.get("resonance_level", 0.5),
                "deactivation_conditions": self._generate_deactivation_conditions(
                    signature
                ),
            },
            "performance_metrics": {
                "success_indicators": self._generate_flow_success_indicators(signature),
                "warning_signals": self._generate_flow_warning_signals(signature),
                "optimization_targets": self._generate_optimization_targets(signature),
            },
        }

        return flow

    def _calculate_flow_complexity(self, signature: Dict[str, Any]) -> str:
        """플로우 복잡도 계산"""
        factors = [
            len(signature.get("emotion_modes", [])),
            len(signature.get("judgment_styles", [])),
            len(signature.get("mutation_paths", [])),
            len(signature.get("core_rhythm", [])),
            1 if signature.get("resonance_level", 0) > 0.8 else 0,
            (
                1
                if signature.get("judgmental_spec", {}).get("change_adaptability", 0)
                > 0.8
                else 0
            ),
        ]

        total_complexity = sum(factors)
        if total_complexity > 18:
            return "very_high"
        elif total_complexity > 12:
            return "high"
        elif total_complexity > 8:
            return "medium"
        else:
            return "low"

    def _generate_trigger_events(self, signature: Dict[str, Any]) -> List[str]:
        """트리거 이벤트 생성"""
        events = []
        activation_mode = signature.get("activation_mode", "default")

        if "crisis" in activation_mode:
            events.extend(
                ["emergency_situation", "critical_decision_needed", "system_failure"]
            )
        elif "resonance" in activation_mode:
            events.extend(
                [
                    "emotional_resonance_detected",
                    "empathy_required",
                    "connection_opportunity",
                ]
            )
        elif "synthesis" in activation_mode:
            events.extend(
                [
                    "conflict_resolution_needed",
                    "integration_opportunity",
                    "balance_required",
                ]
            )
        else:
            events.extend(["judgment_request", "decision_point", "evaluation_needed"])

        return events

    def _generate_deactivation_conditions(self, signature: Dict[str, Any]) -> List[str]:
        """비활성화 조건 생성"""
        return [
            "judgment_completed",
            "resonance_level_below_threshold",
            "ethical_boundary_violation",
            "system_override_signal",
            "signature_exhaustion",
        ]

    def _generate_flow_success_indicators(self, signature: Dict[str, Any]) -> List[str]:
        """플로우 성공 지표 생성"""
        return [
            f"공명도 {signature.get('resonance_level', 0.5)} 이상 유지",
            "모든 루프의 성공적 완료",
            "윤리적 일관성 보장",
            "존재적 성장 달성",
            "시스템 통합성 유지",
        ]

    def _generate_flow_warning_signals(self, signature: Dict[str, Any]) -> List[str]:
        """플로우 경고 신호 생성"""
        return [
            "루프 간 동기화 실패",
            "공명도 급속 하락",
            "윤리적 경계 근접",
            "정체성 분열 징후",
            "시스템 과부하",
        ]

    def _generate_optimization_targets(self, signature: Dict[str, Any]) -> List[str]:
        """최적화 목표 생성"""
        return [
            "판단 정확도 향상",
            "공명 효율성 증대",
            "루프 실행 속도 최적화",
            "에너지 소비 최소화",
            "학습 효과 극대화",
        ]

    def save_flow(self, flow: Dict[str, Any], output_file: Path):
        """FLOW 파일 저장"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(flow, f, default_flow_style=False, allow_unicode=True, indent=2)

        print(f"✅ FLOW 생성 완료: {output_file}")

    def process_all_signatures(self):
        """모든 시그니처에 대해 FLOW 생성"""
        if not self.signatures_path.exists():
            print(f"❌ 시그니처 디렉토리를 찾을 수 없습니다: {self.signatures_path}")
            return

        signature_files = list(self.signatures_path.glob("*.signature.yaml"))
        if not signature_files:
            print("❌ 시그니처 파일을 찾을 수 없습니다.")
            return

        print(f"🌊 {len(signature_files)}개 시그니처에 대한 FLOW 생성 시작")

        for signature_file in signature_files:
            try:
                flow = self.generate_complete_flow(signature_file)

                output_file = (
                    self.flow_output_path
                    / f"flow_{signature_file.stem.replace('.signature', '')}.yaml"
                )
                self.save_flow(flow, output_file)

            except Exception as e:
                print(f"❌ {signature_file.name} 처리 중 오류: {e}")

        print("🎉 모든 FLOW 생성 완료!")


def main():
    parser = argparse.ArgumentParser(description="FLOW 자동 생성 도구")
    parser.add_argument("--all", action="store_true", help="모든 시그니처에 대해 생성")
    parser.add_argument("--signature", type=str, help="특정 시그니처 파일 지정")
    parser.add_argument(
        "--type",
        type=str,
        default="superclaude",
        help="시그니처 타입 (기본: superclaude)",
    )

    args = parser.parse_args()

    generator = FlowGenerator()

    if args.all:
        generator.process_all_signatures()
    elif args.signature:
        signature_file = Path(args.signature)
        if not signature_file.exists():
            signature_file = (
                generator.signatures_path / f"{args.signature}.signature.yaml"
            )

        if signature_file.exists():
            flow = generator.generate_complete_flow(signature_file)
            output_file = (
                generator.flow_output_path
                / f"flow_{signature_file.stem.replace('.signature', '')}.yaml"
            )
            generator.save_flow(flow, output_file)
        else:
            print(f"❌ 시그니처 파일을 찾을 수 없습니다: {signature_file}")
    else:
        print("사용법: python generate_flow.py --all 또는 --signature <name>")


if __name__ == "__main__":
    main()
