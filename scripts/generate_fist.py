#!/usr/bin/env python3
"""
🧠 FIST 템플릿 자동 생성 스크립트
- 시그니처 파일을 기반으로 FIST (Frame, Insight, Strategy, Tactics) 템플릿 자동 생성
- SuperClaude 통합을 위한 고도화된 판단 구조 생성
"""

import yaml
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class FISTGenerator:
    def __init__(self):
        self.base_path = Path(".")
        self.signatures_path = self.base_path / "res" / "signatures" / "superclaude"
        self.fist_output_path = (
            self.base_path / "res" / "fist_templates" / "superclaude"
        )

    def load_signature(self, signature_file: Path) -> Dict[str, Any]:
        """시그니처 파일 로드"""
        with open(signature_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_frame_section(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """Frame 섹션 생성 - 판단의 기본 틀"""
        return {
            "perspective": f"{signature['signature_name']}의 존재적 관점",
            "context_awareness": {
                "resonance_level": signature.get("resonance_level", 0.5),
                "emotion_modes": signature.get("emotion_modes", []),
                "ethic_field": signature.get("ethic_field", "universal"),
            },
            "judgment_lens": {
                "primary_filter": (
                    signature["judgment_styles"][0]
                    if signature.get("judgment_styles")
                    else "balanced_analysis"
                ),
                "secondary_considerations": signature.get("judgment_styles", [])[1:3],
                "resonance_style": signature.get("resonance_style", "default"),
            },
            "boundary_conditions": {
                "activation_mode": signature.get("activation_mode", "default"),
                "function_group": signature.get("function_group", "general"),
                "decision_weight": signature.get("judgmental_spec", {}).get(
                    "decision_weight", 0.5
                ),
            },
        }

    def generate_insight_section(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """Insight 섹션 생성 - 핵심 통찰과 인식"""
        return {
            "core_recognition": {
                "what_i_sense": f"{signature['description'].split('.')[0]}.",
                "what_resonates": signature.get("core_rhythm", []),
                "what_concerns": self._extract_concerns_from_signature(signature),
            },
            "pattern_detection": {
                "emotional_patterns": signature.get("emotion_modes", []),
                "behavioral_indicators": self._generate_behavioral_indicators(
                    signature
                ),
                "resonance_markers": self._extract_resonance_markers(signature),
            },
            "deeper_understanding": {
                "existence_layer": signature.get("signature_type", "unknown"),
                "mutation_potential": signature.get("mutation_paths", []),
                "integration_readiness": signature.get("integration_ready", False),
            },
        }

    def generate_strategy_section(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy 섹션 생성 - 판단 전략과 접근법"""
        return {
            "primary_approach": {
                "method": self._determine_primary_method(signature),
                "reasoning": signature.get("judgment_styles", ["balanced_approach"])[0],
                "expected_outcome": self._predict_outcome(signature),
            },
            "alternative_strategies": {
                "backup_plan": self._generate_backup_strategy(signature),
                "escalation_path": self._generate_escalation_path(signature),
                "de_escalation_option": self._generate_deescalation_option(signature),
            },
            "resonance_optimization": {
                "amplification_methods": self._generate_amplification_methods(
                    signature
                ),
                "harmony_preservation": self._generate_harmony_methods(signature),
                "conflict_resolution": self._generate_conflict_resolution(signature),
            },
        }

    def generate_tactics_section(self, signature: Dict[str, Any]) -> Dict[str, Any]:
        """Tactics 섹션 생성 - 구체적 실행 방법"""
        return {
            "immediate_actions": {
                "first_response": self._generate_first_response(signature),
                "assessment_protocol": self._generate_assessment_protocol(signature),
                "engagement_style": self._determine_engagement_style(signature),
            },
            "execution_steps": {
                "preparation_phase": self._generate_preparation_steps(signature),
                "action_phase": self._generate_action_steps(signature),
                "integration_phase": self._generate_integration_steps(signature),
            },
            "monitoring_feedback": {
                "success_indicators": self._generate_success_indicators(signature),
                "warning_signals": self._generate_warning_signals(signature),
                "adjustment_triggers": self._generate_adjustment_triggers(signature),
            },
        }

    def _extract_concerns_from_signature(self, signature: Dict[str, Any]) -> List[str]:
        """시그니처에서 주요 관심사 추출"""
        concerns = []
        if "pleasure" in signature.get("signature_id", ""):
            concerns.extend(
                ["감각적 경험의 진정성", "쾌락의 윤리적 경계", "존재적 성장과의 균형"]
            )
        elif "phoenix" in signature.get("signature_id", ""):
            concerns.extend(
                [
                    "변화의 필요성 vs 안정성",
                    "파괴적 변화의 리스크",
                    "재생 과정의 완전성",
                ]
            )
        elif "aurora" in signature.get("signature_id", ""):
            concerns.extend(
                ["균형점의 유지", "조화로운 통합", "대립 요소의 건설적 해소"]
            )
        else:
            concerns.extend(["존재적 진정성", "윤리적 일관성", "공명의 질"])
        return concerns

    def _generate_behavioral_indicators(self, signature: Dict[str, Any]) -> List[str]:
        """행동 지표 생성"""
        indicators = []
        emotion_sensitivity = signature.get("judgmental_spec", {}).get(
            "emotion_sensitivity", 0.5
        )

        if emotion_sensitivity > 0.8:
            indicators.append("감정적 변화에 민감한 반응")
        if signature.get("judgmental_spec", {}).get("risk_tolerance", 0.5) > 0.8:
            indicators.append("위험 상황에서의 적극적 대응")
        if signature.get("judgmental_spec", {}).get("change_adaptability", 0.5) > 0.8:
            indicators.append("변화 상황에서의 빠른 적응")

        return indicators or ["균형잡힌 행동 패턴"]

    def _extract_resonance_markers(self, signature: Dict[str, Any]) -> List[str]:
        """공명 마커 추출"""
        markers = []
        resonance_style = signature.get("resonance_style", "")

        if "⨯" in resonance_style:
            elements = resonance_style.split("⨯")
            markers.extend([f"{elem.strip()} 요소의 활성화" for elem in elements])
        else:
            markers.append(f"{resonance_style} 스타일의 공명")

        return markers or ["기본 공명 패턴"]

    def _determine_primary_method(self, signature: Dict[str, Any]) -> str:
        """주요 방법론 결정"""
        if signature.get("signature_type") == "existence_based_transmuter":
            return "존재적 변환 접근법"
        elif signature.get("signature_type") == "balance_harmonizer":
            return "조화적 균형 접근법"
        elif signature.get("signature_type") == "transformation_catalyst":
            return "변화 촉매 접근법"
        else:
            return "통합적 판단 접근법"

    def _predict_outcome(self, signature: Dict[str, Any]) -> str:
        """예상 결과 예측"""
        resonance_level = signature.get("resonance_level", 0.5)
        if resonance_level > 0.9:
            return "높은 공명도를 통한 깊은 변화 예상"
        elif resonance_level > 0.7:
            return "중간 수준의 안정적 변화 예상"
        else:
            return "점진적 개선 및 안정화 예상"

    def _generate_backup_strategy(self, signature: Dict[str, Any]) -> str:
        """백업 전략 생성"""
        return f"{signature['signature_name']}의 보조 접근법을 통한 단계적 개입"

    def _generate_escalation_path(self, signature: Dict[str, Any]) -> str:
        """확대 경로 생성"""
        return f"강화된 {signature.get('resonance_style', 'default')} 모드로 전환"

    def _generate_deescalation_option(self, signature: Dict[str, Any]) -> str:
        """완화 옵션 생성"""
        return f"부드러운 {signature['signature_name']} 접근으로 점진적 조정"

    def _generate_amplification_methods(self, signature: Dict[str, Any]) -> List[str]:
        """증폭 방법 생성"""
        methods = []
        core_rhythm = signature.get("core_rhythm", [])
        for rhythm in core_rhythm[:2]:  # 상위 2개 리듬 사용
            if isinstance(rhythm, dict):
                methods.append(f"{rhythm.get('name', 'unknown')} 강화")
        return methods or ["기본 공명 증폭"]

    def _generate_harmony_methods(self, signature: Dict[str, Any]) -> List[str]:
        """조화 방법 생성"""
        return [
            f"{signature['signature_name']} 특성을 활용한 균형 유지",
            "상호 보완적 요소들의 조화로운 통합",
        ]

    def _generate_conflict_resolution(self, signature: Dict[str, Any]) -> List[str]:
        """갈등 해결 방법 생성"""
        return [
            f"{signature.get('ethic_field', 'universal')}에 기반한 중재",
            "존재적 공명을 통한 근본 해결",
        ]

    def _generate_first_response(self, signature: Dict[str, Any]) -> str:
        """첫 반응 생성"""
        activation_mode = signature.get("activation_mode", "balanced")
        if "crisis" in activation_mode:
            return "긴급 상황 인식 및 즉시 대응"
        elif "resonance" in activation_mode:
            return "공명 상태 확인 및 조율"
        else:
            return "상황 평가 및 균형적 접근"

    def _generate_assessment_protocol(self, signature: Dict[str, Any]) -> List[str]:
        """평가 프로토콜 생성"""
        return [
            f"{signature['signature_name']} 관점에서의 상황 분석",
            "감정적-논리적 균형점 확인",
            "공명 가능성 및 위험 요소 평가",
        ]

    def _determine_engagement_style(self, signature: Dict[str, Any]) -> str:
        """관여 스타일 결정"""
        empathy_range = signature.get("judgmental_spec", {}).get("empathy_range", 0.5)
        if empathy_range > 0.8:
            return "깊은 공감적 관여"
        elif empathy_range > 0.6:
            return "균형잡힌 관여"
        else:
            return "객관적 분석적 관여"

    def _generate_preparation_steps(self, signature: Dict[str, Any]) -> List[str]:
        """준비 단계 생성"""
        return [
            f"{signature['signature_name']} 모드 활성화",
            "내적 공명 상태 조율",
            "판단 기준 및 경계 설정",
        ]

    def _generate_action_steps(self, signature: Dict[str, Any]) -> List[str]:
        """행동 단계 생성"""
        return [
            "직접적 개입 및 영향력 행사",
            "피드백 수집 및 실시간 조정",
            "목표 지향적 지속적 참여",
        ]

    def _generate_integration_steps(self, signature: Dict[str, Any]) -> List[str]:
        """통합 단계 생성"""
        return [
            "결과 평가 및 학습 포인트 추출",
            "경험의 존재적 통합",
            "다음 사이클을 위한 준비",
        ]

    def _generate_success_indicators(self, signature: Dict[str, Any]) -> List[str]:
        """성공 지표 생성"""
        resonance_level = signature.get("resonance_level", 0.5)
        return [
            f"공명도 {resonance_level} 이상 달성",
            "존재적 성장의 명확한 징후",
            "윤리적 일관성 유지",
        ]

    def _generate_warning_signals(self, signature: Dict[str, Any]) -> List[str]:
        """경고 신호 생성"""
        return ["공명도 급격한 하락", "윤리적 경계 침범 위험", "존재적 분열 징후"]

    def _generate_adjustment_triggers(self, signature: Dict[str, Any]) -> List[str]:
        """조정 트리거 생성"""
        return [
            "예상과 다른 반응 패턴 감지",
            "부작용 또는 역효과 발생",
            "더 효과적인 접근법 발견",
        ]

    def generate_fist_template(self, signature_file: Path) -> Dict[str, Any]:
        """완전한 FIST 템플릿 생성"""
        signature = self.load_signature(signature_file)

        fist_template = {
            "signature_id": signature["signature_id"],
            "signature_name": signature["signature_name"],
            "fist_version": "2.0_superclaude",
            "generated_at": datetime.now().isoformat(),
            "Frame": self.generate_frame_section(signature),
            "Insight": self.generate_insight_section(signature),
            "Strategy": self.generate_strategy_section(signature),
            "Tactics": self.generate_tactics_section(signature),
            "meta_information": {
                "source_signature": signature_file.name,
                "resonance_level": signature.get("resonance_level", 0.5),
                "complexity_level": self._calculate_complexity(signature),
                "integration_ready": signature.get("integration_ready", False),
            },
        }

        return fist_template

    def _calculate_complexity(self, signature: Dict[str, Any]) -> str:
        """복잡도 계산"""
        factors = [
            len(signature.get("emotion_modes", [])),
            len(signature.get("judgment_styles", [])),
            len(signature.get("mutation_paths", [])),
            len(signature.get("core_rhythm", [])),
        ]

        total_complexity = sum(factors)
        if total_complexity > 15:
            return "high"
        elif total_complexity > 10:
            return "medium"
        else:
            return "low"

    def save_fist_template(self, fist_template: Dict[str, Any], output_file: Path):
        """FIST 템플릿 저장"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(
                fist_template, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        print(f"✅ FIST 템플릿 생성: {output_file}")

    def process_all_signatures(self):
        """모든 시그니처에 대해 FIST 템플릿 생성"""
        if not self.signatures_path.exists():
            print(f"❌ 시그니처 디렉토리를 찾을 수 없습니다: {self.signatures_path}")
            return

        signature_files = list(self.signatures_path.glob("*.signature.yaml"))
        if not signature_files:
            print("❌ 시그니처 파일을 찾을 수 없습니다.")
            return

        print(f"🧠 {len(signature_files)}개 시그니처에 대한 FIST 템플릿 생성 시작")

        for signature_file in signature_files:
            try:
                fist_template = self.generate_fist_template(signature_file)

                output_file = (
                    self.fist_output_path
                    / f"{signature_file.stem.replace('.signature', '')}.fist.yaml"
                )
                self.save_fist_template(fist_template, output_file)

            except Exception as e:
                print(f"❌ {signature_file.name} 처리 중 오류: {e}")

        print("🎉 모든 FIST 템플릿 생성 완료!")


def main():
    parser = argparse.ArgumentParser(description="FIST 템플릿 자동 생성 도구")
    parser.add_argument("--all", action="store_true", help="모든 시그니처에 대해 생성")
    parser.add_argument("--signature", type=str, help="특정 시그니처 파일 지정")
    parser.add_argument(
        "--type",
        type=str,
        default="superclaude",
        help="시그니처 타입 (기본: superclaude)",
    )

    args = parser.parse_args()

    generator = FISTGenerator()

    if args.all:
        generator.process_all_signatures()
    elif args.signature:
        signature_file = Path(args.signature)
        if not signature_file.exists():
            signature_file = (
                generator.signatures_path / f"{args.signature}.signature.yaml"
            )

        if signature_file.exists():
            fist_template = generator.generate_fist_template(signature_file)
            output_file = (
                generator.fist_output_path
                / f"{signature_file.stem.replace('.signature', '')}.fist.yaml"
            )
            generator.save_fist_template(fist_template, output_file)
        else:
            print(f"❌ 시그니처 파일을 찾을 수 없습니다: {signature_file}")
    else:
        print("사용법: python generate_fist.py --all 또는 --signature <name>")


if __name__ == "__main__":
    main()
