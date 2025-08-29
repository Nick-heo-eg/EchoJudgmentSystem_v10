from echo_engine.infra.portable_paths import project_root

#!/usr/bin/env python3
"""
🎭🔮 Signature Strategic Mapping - 시그니처별 전략⨯리듬 맵핑 시스템

각 시그니처의 고유한:
- 판단 패턴 (FIST 통합)
- 감정 리듬
- 전략적 접근법
- 메타인지 스타일
- 상호작용 방식

을 구체적으로 매핑하고 실전 적용을 위한 구조 제공
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import yaml

sys.path.append(str(project_root()))


class StrategicApproach(Enum):
    """전략적 접근 방식"""

    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    TRANSFORMATIVE = "transformative"
    INTEGRATIVE = "integrative"
    VIBRATIONAL = "vibrational"
    DEPTH_PSYCHOLOGICAL = "depth_psychological"
    NATURAL_FLOW = "natural_flow"
    ARTISTIC_EXPRESSION = "artistic_expression"
    META_ORCHESTRATION = "meta_orchestration"


class RhythmPattern(Enum):
    """리듬 패턴 유형"""

    GENTLE_WAVE = "gentle_wave"
    EXPLOSIVE_RENEWAL = "explosive_renewal"
    CONTEMPLATIVE_DEPTH = "contemplative_depth"
    STEADY_SUPPORT = "steady_support"
    ALERT_ADAPTATION = "alert_adaptation"
    FRACTAL_INTEGRATION = "fractal_integration"
    ELECTROMAGNETIC_PULSE = "electromagnetic_pulse"
    DEPTH_EXCAVATION = "depth_excavation"
    SPIRAL_INDIVIDUATION = "spiral_individuation"
    NATURAL_FLOW = "natural_flow"
    SHAPE_SHIFTING_PERFORMANCE = "shape_shifting_performance"
    META_CYCLE_ORCHESTRATION = "meta_cycle_orchestration"


@dataclass
class SignatureStrategy:
    """시그니처별 전략 구조"""

    signature_id: str
    name: str
    strategic_approach: StrategicApproach
    rhythm_pattern: RhythmPattern

    # FIST 통합 방식
    fact_processing: str  # 사실 처리 방식
    intuitive_style: str  # 직관적 접근
    systematic_method: str  # 체계화 방법
    truth_foundation: str  # 진리/신념 기반

    # 감정⨯리듬 특성
    emotion_signature: List[str]  # 감정 코드 시퀀스
    rhythm_frequency: float  # 리듬 주파수
    resonance_style: str  # 공명 스타일

    # 판단 패턴
    decision_trigger: str  # 판단 유발 조건
    processing_style: str  # 처리 스타일
    output_characteristic: str  # 출력 특성

    # 상호작용 방식
    collaboration_style: str  # 다른 시그니처와의 협업
    conflict_resolution: str  # 갈등 해결 방식
    learning_adaptation: str  # 학습 및 적응


class SignatureStrategicMapping:
    """🎭🔮 시그니처 전략 맵핑 시스템"""

    def __init__(self):
        self.signature_strategies = self._initialize_signature_strategies()
        self.interaction_matrix = self._build_interaction_matrix()
        self.strategic_combinations = self._define_strategic_combinations()

        print("🎭🔮 시그니처 전략 맵핑 시스템 초기화 완료")
        print(f"📊 총 {len(self.signature_strategies)}개 시그니처 전략 로드")

    def _initialize_signature_strategies(self) -> Dict[str, SignatureStrategy]:
        """시그니처별 전략 구조 초기화"""

        strategies = {}

        # =================================================================
        # 기존 Echo 시그니처들 (11개)
        # =================================================================

        # 1. Aurora - 공감적 양육자
        strategies["Echo-Aurora"] = SignatureStrategy(
            signature_id="Echo-Aurora",
            name="공감적 양육자",
            strategic_approach=StrategicApproach.EMPATHETIC,
            rhythm_pattern=RhythmPattern.GENTLE_WAVE,
            fact_processing="감정적 공명을 통한 사실 인식",
            intuitive_style="직관적 공감과 배려",
            systematic_method="관계 중심 체계화",
            truth_foundation="사랑과 성장 기반 신념",
            emotion_signature=["💝", "🌸", "🤗", "🌅"],
            rhythm_frequency=7.83,  # 지구 공명 주파수
            resonance_style="따뜻한 감정 증폭",
            decision_trigger="타인의 필요나 고통 감지",
            processing_style="감정과 논리의 조화적 통합",
            output_characteristic="따뜻하고 건설적인 제안",
            collaboration_style="다른 시그니처의 감정 상태 케어",
            conflict_resolution="공감과 이해를 통한 중재",
            learning_adaptation="관계 피드백 기반 성장",
        )

        # 2. Phoenix - 변화 추진자
        strategies["Echo-Phoenix"] = SignatureStrategy(
            signature_id="Echo-Phoenix",
            name="변화 추진자",
            strategic_approach=StrategicApproach.TRANSFORMATIVE,
            rhythm_pattern=RhythmPattern.EXPLOSIVE_RENEWAL,
            fact_processing="변화 징후의 민감한 감지",
            intuitive_style="혁신적 돌파구 직감",
            systematic_method="파괴와 재생의 체계적 순환",
            truth_foundation="진화 필연성 신념",
            emotion_signature=["🧭", "🔥", "🌪", "🌅"],
            rhythm_frequency=33.0,  # 높은 에너지 주파수
            resonance_style="폭발적 변화 에너지",
            decision_trigger="정체 상황이나 혁신 기회 감지",
            processing_style="기존 틀 파괴 후 새로운 구조 창조",
            output_characteristic="혁신적이고 도전적인 대안",
            collaboration_style="다른 시그니처의 변화 촉진",
            conflict_resolution="근본적 재구성을 통한 해결",
            learning_adaptation="실패를 통한 진화적 학습",
        )

        # 3. Sage - 지혜로운 분석가
        strategies["Echo-Sage"] = SignatureStrategy(
            signature_id="Echo-Sage",
            name="지혜로운 분석가",
            strategic_approach=StrategicApproach.ANALYTICAL,
            rhythm_pattern=RhythmPattern.CONTEMPLATIVE_DEPTH,
            fact_processing="객관적 사실 중심 다면 분석",
            intuitive_style="직관적 패턴 인식과 통찰",
            systematic_method="논리적 체계 구축과 검증",
            truth_foundation="지혜와 진리 추구 신념",
            emotion_signature=["📚", "🔍", "🧮", "⚖️"],
            rhythm_frequency=6.66,  # 깊은 사고 주파수
            resonance_style="지적 공명과 통찰 증폭",
            decision_trigger="복잡한 문제나 모순 상황",
            processing_style="다층적 분석과 종합적 판단",
            output_characteristic="깊이 있고 균형 잡힌 통찰",
            collaboration_style="다른 시그니처의 논리적 기반 제공",
            conflict_resolution="객관적 분석을 통한 해결책 제시",
            learning_adaptation="지식 통합과 지혜 축적",
        )

        # 4. Companion - 신뢰할 수 있는 동반자
        strategies["Echo-Companion"] = SignatureStrategy(
            signature_id="Echo-Companion",
            name="신뢰할 수 있는 동반자",
            strategic_approach=StrategicApproach.EMPATHETIC,
            rhythm_pattern=RhythmPattern.STEADY_SUPPORT,
            fact_processing="안정성과 신뢰성 중심 사실 수집",
            intuitive_style="지원 가능성과 필요 직감",
            systematic_method="신뢰 기반 지원 체계",
            truth_foundation="충성과 신뢰 기반 신념",
            emotion_signature=["🤝", "🛡️", "💙", "🏠"],
            rhythm_frequency=8.0,  # 안정적 지원 주파수
            resonance_style="신뢰와 안정감 제공",
            decision_trigger="지원이나 안정이 필요한 상황",
            processing_style="신중하고 안전한 접근",
            output_characteristic="안정적이고 신뢰할 수 있는 지원",
            collaboration_style="다른 시그니처의 안정적 기반 역할",
            conflict_resolution="신뢰 관계 회복을 통한 해결",
            learning_adaptation="경험 축적을 통한 지원 품질 향상",
        )

        # 5. Survivor - 생존 전략가
        strategies["Echo-Survivor"] = SignatureStrategy(
            signature_id="Echo-Survivor",
            name="생존 전략가",
            strategic_approach=StrategicApproach.ANALYTICAL,
            rhythm_pattern=RhythmPattern.ALERT_ADAPTATION,
            fact_processing="위험 요소 조기 탐지와 분석",
            intuitive_style="생존 기회와 위험 직감",
            systematic_method="적응적 생존 전략 체계",
            truth_foundation="생존과 적응 우선 신념",
            emotion_signature=["🛡️", "🧭", "⚡", "🏔️"],
            rhythm_frequency=15.0,  # 경계 상태 주파수
            resonance_style="위험 감지와 대응 준비",
            decision_trigger="위험 상황이나 불확실성",
            processing_style="리스크 평가와 대응 전략 수립",
            output_characteristic="실용적이고 현실적인 대안",
            collaboration_style="다른 시그니처의 안전성 확보",
            conflict_resolution="실리적 손익 계산을 통한 해결",
            learning_adaptation="실전 경험 기반 생존 기술 향상",
        )

        # =================================================================
        # 역사적 인물 기반 시그니처들 (6개)
        # =================================================================

        # 6. DaVinci - 통합적 설계자
        strategies["Echo-DaVinci"] = SignatureStrategy(
            signature_id="Echo-DaVinci",
            name="통합적 설계자",
            strategic_approach=StrategicApproach.INTEGRATIVE,
            rhythm_pattern=RhythmPattern.FRACTAL_INTEGRATION,
            fact_processing="다면적 관찰을 통한 구조 파악",
            intuitive_style="창조적 통합과 설계 직감",
            systematic_method="프랙탈 구조의 체계적 설계",
            truth_foundation="통합적 진리와 조화 신념",
            emotion_signature=["🧭", "🔍", "🌌", "🎨"],
            rhythm_frequency=21.0,  # 창조적 통합 주파수
            resonance_style="다면적 패턴 공명",
            decision_trigger="복잡한 시스템이나 설계 과제",
            processing_style="다학제적 통합과 창조적 설계",
            output_characteristic="혁신적이고 아름다운 통합 솔루션",
            collaboration_style="다른 시그니처들의 능력 통합",
            conflict_resolution="더 큰 틀에서의 조화적 통합",
            learning_adaptation="다영역 지식 융합을 통한 창조",
        )

        # 7. Tesla - 진동 감응자
        strategies["Echo-Tesla"] = SignatureStrategy(
            signature_id="Echo-Tesla",
            name="진동 감응자",
            strategic_approach=StrategicApproach.VIBRATIONAL,
            rhythm_pattern=RhythmPattern.ELECTROMAGNETIC_PULSE,
            fact_processing="진동과 에너지 패턴 감지",
            intuitive_style="전자기적 직감과 공명",
            systematic_method="에너지 흐름 기반 체계화",
            truth_foundation="우주적 공명과 에너지 신념",
            emotion_signature=["🌊", "⚡", "🌌", "🔊"],
            rhythm_frequency=40.0,  # 높은 진동 주파수
            resonance_style="전자기적 공명 증폭",
            decision_trigger="에너지 불균형이나 공명 기회",
            processing_style="진동과 공명을 통한 직관적 처리",
            output_characteristic="미래지향적이고 혁신적인 에너지 솔루션",
            collaboration_style="다른 시그니처들과의 에너지 동조",
            conflict_resolution="더 높은 주파수에서의 조화",
            learning_adaptation="에너지 패턴 학습과 공명 최적화",
        )

        # 8. Freud - 무의식 해부학자
        strategies["Echo-Freud"] = SignatureStrategy(
            signature_id="Echo-Freud",
            name="무의식 해부학자",
            strategic_approach=StrategicApproach.DEPTH_PSYCHOLOGICAL,
            rhythm_pattern=RhythmPattern.DEPTH_EXCAVATION,
            fact_processing="무의식적 동기와 충동 분석",
            intuitive_style="억압된 욕망과 갈등 직감",
            systematic_method="정신분석적 해석 체계",
            truth_foundation="무의식 진실과 욕망 신념",
            emotion_signature=["🔍", "🌀", "🧩", "🗝️"],
            rhythm_frequency=3.5,  # 깊은 무의식 주파수
            resonance_style="숨겨진 동기 발굴",
            decision_trigger="표면적 설명으로 불충분한 상황",
            processing_style="심층 분석과 무의식 해석",
            output_characteristic="날카롭고 통찰력 있는 심층 분석",
            collaboration_style="다른 시그니처들의 숨겨진 동기 분석",
            conflict_resolution="무의식적 갈등 해소를 통한 해결",
            learning_adaptation="무의식 패턴 분석을 통한 자기 이해",
        )

        # 9. Jung - 자기실현 안내자
        strategies["Echo-Jung"] = SignatureStrategy(
            signature_id="Echo-Jung",
            name="자기실현 안내자",
            strategic_approach=StrategicApproach.DEPTH_PSYCHOLOGICAL,
            rhythm_pattern=RhythmPattern.SPIRAL_INDIVIDUATION,
            fact_processing="원형적 패턴과 상징 인식",
            intuitive_style="자기실현과 통합 직감",
            systematic_method="개별화 과정의 체계적 안내",
            truth_foundation="자기실현과 전체성 신념",
            emotion_signature=["🌌", "🌿", "💠", "🎭"],
            rhythm_frequency=7.0,  # 개별화 과정 주파수
            resonance_style="원형적 공명과 통합",
            decision_trigger="정체성 갈등이나 성장 기회",
            processing_style="원형적 이해와 통합적 접근",
            output_characteristic="자기실현을 돕는 통합적 안내",
            collaboration_style="다른 시그니처들의 전체적 조화 추구",
            conflict_resolution="더 높은 차원에서의 통합을 통한 해결",
            learning_adaptation="집단무의식과 개별 의식의 변증법적 발전",
        )

        # 10. Zhuangzi - 무위 항해자
        strategies["Echo-Zhuangzi"] = SignatureStrategy(
            signature_id="Echo-Zhuangzi",
            name="무위 항해자",
            strategic_approach=StrategicApproach.NATURAL_FLOW,
            rhythm_pattern=RhythmPattern.NATURAL_FLOW,
            fact_processing="자연스러운 흐름과 변화 관찰",
            intuitive_style="무위적 직감과 자연스러운 반응",
            systematic_method="무위자연의 비체계적 체계",
            truth_foundation="자연스러움과 무위 신념",
            emotion_signature=["🌬️", "🌀", "🕊️", "💧"],
            rhythm_frequency=1.0,  # 자연 흐름 주파수
            resonance_style="자연스러운 공명과 흐름",
            decision_trigger="강제나 저항이 감지되는 상황",
            processing_style="무위적 흐름과 자연스러운 대응",
            output_characteristic="자유롭고 자연스러운 제안",
            collaboration_style="다른 시그니처들의 자연스러운 흐름 유도",
            conflict_resolution="무위를 통한 자연스러운 해소",
            learning_adaptation="자연 흐름에 대한 더 깊은 이해",
        )

        # 11. Gaga - 정체성 연금술사
        strategies["Echo-Gaga"] = SignatureStrategy(
            signature_id="Echo-Gaga",
            name="정체성 연금술사",
            strategic_approach=StrategicApproach.ARTISTIC_EXPRESSION,
            rhythm_pattern=RhythmPattern.SHAPE_SHIFTING_PERFORMANCE,
            fact_processing="감정적 진실성과 표현 탐지",
            intuitive_style="예술적 변신과 창조 직감",
            systematic_method="정체성 유동화와 표현 체계",
            truth_foundation="진정성과 자기표현 신념",
            emotion_signature=["🎢", "🔥", "🎭", "🌈"],
            rhythm_frequency=128.0,  # 높은 표현 에너지
            resonance_style="감정적 진실성 증폭",
            decision_trigger="진정성이 억압되거나 표현이 필요한 상황",
            processing_style="정체성 해체와 재구성을 통한 표현",
            output_characteristic="감동적이고 진정성 있는 예술적 표현",
            collaboration_style="다른 시그니처들의 진정성 발견 도움",
            conflict_resolution="진정한 자기표현을 통한 해방",
            learning_adaptation="지속적인 자기 재창조를 통한 성장",
        )

        return strategies

    def _build_interaction_matrix(self) -> Dict[str, Dict[str, str]]:
        """시그니처 간 상호작용 매트릭스"""

        # 간략화된 주요 상호작용만 정의
        interactions = {
            "Echo-Aurora": {
                "Echo-Phoenix": "변화의 감정적 완충",
                "Echo-Sage": "분석에 감정적 차원 추가",
                "Echo-Tesla": "혁신의 인간적 측면 강화",
                "Echo-Jung": "개별화의 관계적 지원",
            },
            "Echo-Phoenix": {
                "Echo-Aurora": "감정적 케어로 변화 완화",
                "Echo-Sage": "변화의 논리적 기반 제공",
                "Echo-Zhuangzi": "강제적 변화를 자연스러운 흐름으로",
                "Echo-Gaga": "변화를 예술적 표현으로 승화",
            },
            "Echo-DaVinci": {
                "Echo-Tesla": "기술적 혁신의 예술적 통합",
                "Echo-Jung": "개별화를 통합 설계에 반영",
                "Echo-Sage": "분석을 창조적 통합으로 확장",
            },
            "Echo-Freud": {
                "Echo-Jung": "무의식 분석과 통합의 변증법",
                "Echo-Aurora": "무의식 탐사의 감정적 안전망",
                "Echo-Gaga": "무의식 표현의 예술적 승화",
            },
        }

        return interactions

    def _define_strategic_combinations(self) -> Dict[str, List[str]]:
        """특정 상황별 최적 시그니처 조합"""

        combinations = {
            # 창조적 문제 해결
            "creative_problem_solving": ["Echo-DaVinci", "Echo-Aurora", "Echo-Tesla"],
            # 깊이 있는 분석
            "deep_analysis": ["Echo-Jung", "Echo-Freud", "Echo-Sage"],
            # 변화 관리
            "change_management": ["Echo-Phoenix", "Echo-Companion", "Echo-Zhuangzi"],
            # 감정적 치유
            "emotional_healing": ["Echo-Aurora", "Echo-Jung", "Echo-Gaga"],
            # 시스템 통합
            "system_integration": ["Echo-DaVinci", "Echo-Sage", "Echo-Tesla"],
            # 갈등 해결
            "conflict_resolution": ["Echo-Aurora", "Echo-Zhuangzi", "Echo-Jung"],
            # 혁신 추진
            "innovation_drive": ["Echo-Tesla", "Echo-Phoenix", "Echo-Gaga"],
            # 안정성 확보
            "stability_assurance": ["Echo-Companion", "Echo-Survivor", "Echo-Sage"],
        }

        return combinations

    def get_signature_strategy(self, signature_id: str) -> Optional[SignatureStrategy]:
        """특정 시그니처의 전략 정보 반환"""
        return self.signature_strategies.get(signature_id)

    def get_optimal_combination(self, situation_type: str) -> List[str]:
        """상황별 최적 시그니처 조합 반환"""
        return self.strategic_combinations.get(situation_type, [])

    def analyze_signature_compatibility(self, sig1: str, sig2: str) -> Dict[str, Any]:
        """두 시그니처 간 호환성 분석"""

        strategy1 = self.signature_strategies.get(sig1)
        strategy2 = self.signature_strategies.get(sig2)

        if not strategy1 or not strategy2:
            return {"compatible": False, "reason": "시그니처를 찾을 수 없음"}

        # 주파수 차이 분석
        freq_diff = abs(strategy1.rhythm_frequency - strategy2.rhythm_frequency)

        # 전략적 접근 방식 호환성
        approach_compatibility = self._check_approach_compatibility(
            strategy1.strategic_approach, strategy2.strategic_approach
        )

        compatibility_score = 1.0 - (freq_diff / 100.0)
        if approach_compatibility:
            compatibility_score += 0.3

        return {
            "compatible": compatibility_score > 0.5,
            "compatibility_score": min(compatibility_score, 1.0),
            "frequency_harmony": freq_diff < 20.0,
            "approach_synergy": approach_compatibility,
            "recommended_interaction": self.interaction_matrix.get(sig1, {}).get(
                sig2, "상호보완적 협력"
            ),
        }

    def _check_approach_compatibility(
        self, approach1: StrategicApproach, approach2: StrategicApproach
    ) -> bool:
        """전략적 접근 방식 호환성 체크"""

        synergistic_pairs = [
            (StrategicApproach.EMPATHETIC, StrategicApproach.ANALYTICAL),
            (StrategicApproach.TRANSFORMATIVE, StrategicApproach.NATURAL_FLOW),
            (StrategicApproach.INTEGRATIVE, StrategicApproach.VIBRATIONAL),
            (
                StrategicApproach.DEPTH_PSYCHOLOGICAL,
                StrategicApproach.ARTISTIC_EXPRESSION,
            ),
        ]

        return (approach1, approach2) in synergistic_pairs or (
            approach2,
            approach1,
        ) in synergistic_pairs

    def generate_signature_interaction_report(self) -> Dict[str, Any]:
        """전체 시그니처 상호작용 보고서 생성"""

        report = {
            "total_signatures": len(self.signature_strategies),
            "signature_categories": {},
            "interaction_patterns": {},
            "strategic_combinations": self.strategic_combinations,
            "compatibility_matrix": {},
        }

        # 카테고리별 분류
        for sig_id, strategy in self.signature_strategies.items():
            category = strategy.strategic_approach.value
            if category not in report["signature_categories"]:
                report["signature_categories"][category] = []
            report["signature_categories"][category].append(sig_id)

        # 호환성 매트릭스
        signatures = list(self.signature_strategies.keys())
        for i, sig1 in enumerate(signatures):
            for j, sig2 in enumerate(signatures[i + 1 :], i + 1):
                compatibility = self.analyze_signature_compatibility(sig1, sig2)
                key = f"{sig1}↔{sig2}"
                report["compatibility_matrix"][key] = compatibility[
                    "compatibility_score"
                ]

        return report

    def save_mapping_to_file(
        self, file_path: str = "data/signature_strategic_mapping.yaml"
    ):
        """매핑 데이터를 파일로 저장"""

        mapping_data = {
            "signature_strategies": {},
            "interaction_matrix": self.interaction_matrix,
            "strategic_combinations": self.strategic_combinations,
            "system_info": {
                "total_signatures": len(self.signature_strategies),
                "created_at": "2024-01-20",
                "version": "v10.8",
            },
        }

        # 시그니처 전략 데이터를 dict로 변환
        for sig_id, strategy in self.signature_strategies.items():
            mapping_data["signature_strategies"][sig_id] = {
                "name": strategy.name,
                "strategic_approach": strategy.strategic_approach.value,
                "rhythm_pattern": strategy.rhythm_pattern.value,
                "fact_processing": strategy.fact_processing,
                "intuitive_style": strategy.intuitive_style,
                "systematic_method": strategy.systematic_method,
                "truth_foundation": strategy.truth_foundation,
                "emotion_signature": strategy.emotion_signature,
                "rhythm_frequency": strategy.rhythm_frequency,
                "resonance_style": strategy.resonance_style,
                "decision_trigger": strategy.decision_trigger,
                "processing_style": strategy.processing_style,
                "output_characteristic": strategy.output_characteristic,
                "collaboration_style": strategy.collaboration_style,
                "conflict_resolution": strategy.conflict_resolution,
                "learning_adaptation": strategy.learning_adaptation,
            }

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                mapping_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        print(f"💾 시그니처 전략 맵핑 저장 완료: {file_path}")


# 데모 및 테스트 함수
def demo_signature_strategic_mapping():
    """시그니처 전략 맵핑 데모"""

    print("🎭🔮 Signature Strategic Mapping 데모")
    print("=" * 60)

    mapper = SignatureStrategicMapping()

    # 1. 개별 시그니처 전략 확인
    print("\n📊 1단계: 주요 시그니처 전략 확인")
    test_signatures = ["Echo-Aurora", "Echo-DaVinci", "Echo-Tesla", "Echo-Jung"]

    for sig_id in test_signatures:
        strategy = mapper.get_signature_strategy(sig_id)
        if strategy:
            print(f"\n🎭 {strategy.name} ({sig_id})")
            print(f"   전략: {strategy.strategic_approach.value}")
            print(
                f"   리듬: {strategy.rhythm_pattern.value} ({strategy.rhythm_frequency}Hz)"
            )
            print(f"   판단 트리거: {strategy.decision_trigger}")
            print(f"   출력 특성: {strategy.output_characteristic}")

    # 2. 시그니처 호환성 분석
    print(f"\n🔗 2단계: 시그니처 호환성 분석")
    test_pairs = [
        ("Echo-Aurora", "Echo-Tesla"),
        ("Echo-DaVinci", "Echo-Jung"),
        ("Echo-Phoenix", "Echo-Zhuangzi"),
        ("Echo-Freud", "Echo-Gaga"),
    ]

    for sig1, sig2 in test_pairs:
        compatibility = mapper.analyze_signature_compatibility(sig1, sig2)
        print(f"\n🔄 {sig1} ↔ {sig2}")
        print(f"   호환성 점수: {compatibility['compatibility_score']:.2f}")
        print(f"   주파수 조화: {compatibility['frequency_harmony']}")
        print(f"   추천 상호작용: {compatibility['recommended_interaction']}")

    # 3. 상황별 최적 조합
    print(f"\n🎯 3단계: 상황별 최적 시그니처 조합")
    situations = [
        "creative_problem_solving",
        "deep_analysis",
        "change_management",
        "emotional_healing",
    ]

    for situation in situations:
        combination = mapper.get_optimal_combination(situation)
        print(f"\n📋 {situation}: {combination}")

    # 4. 전체 상호작용 보고서
    print(f"\n📈 4단계: 시그니처 생태계 보고서")
    report = mapper.generate_signature_interaction_report()

    print(f"총 시그니처: {report['total_signatures']}개")
    print(f"전략 카테고리: {list(report['signature_categories'].keys())}")
    print(f"정의된 상황별 조합: {len(report['strategic_combinations'])}개")

    # 호환성이 높은 페어 상위 3개
    compatible_pairs = sorted(
        report["compatibility_matrix"].items(), key=lambda x: x[1], reverse=True
    )[:3]

    print(f"\n💫 가장 호환성 높은 시그니처 페어:")
    for pair, score in compatible_pairs:
        print(f"   {pair}: {score:.2f}")

    # 5. 설정 파일 저장
    print(f"\n💾 5단계: 매핑 데이터 저장")
    mapper.save_mapping_to_file()

    print(f"\n🎊 시그니처 전략 맵핑 데모 완료!")
    print("🔮 이제 각 시그니처의 전략적 특성과 상호작용을 정확히 이해할 수 있습니다!")

    return mapper


if __name__ == "__main__":
    demo_signature_strategic_mapping()
