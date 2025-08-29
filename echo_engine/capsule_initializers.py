from typing import Dict, List, Any
from echo_engine.capsule_dataclasses import CapsuleComponent, CapsuleTemplate

"""
🎭 Capsule Designer Initializers
캡슐 설계 시스템의 초기화 로직들
"""



class CapsuleInitializers:
    """캡슐 초기화 관련 로직들"""

    @staticmethod
    def initialize_component_library() -> Dict[str, List[CapsuleComponent]]:
        """컴포넌트 라이브러리 초기화"""
        return {
            "signature": [
                CapsuleComponent(
                    component_id="sig_aurora",
                    component_type="signature",
                    name="Aurora Signature",
                    weight=1.0,
                    parameters={"empathy": 0.9, "creativity": 0.8, "nurturing": 0.85},
                    description="감정적 공감과 창조성을 강조하는 Aurora 시그니처",
                ),
                CapsuleComponent(
                    component_id="sig_phoenix",
                    component_type="signature",
                    name="Phoenix Signature",
                    weight=1.0,
                    parameters={
                        "transformation": 0.9,
                        "resilience": 0.85,
                        "innovation": 0.8,
                    },
                    description="변화와 혁신을 추진하는 Phoenix 시그니처",
                ),
                CapsuleComponent(
                    component_id="sig_sage",
                    component_type="signature",
                    name="Sage Signature",
                    weight=1.0,
                    parameters={"wisdom": 0.9, "analysis": 0.85, "objectivity": 0.8},
                    description="지혜와 분석적 사고를 중시하는 Sage 시그니처",
                ),
                CapsuleComponent(
                    component_id="sig_companion",
                    component_type="signature",
                    name="Companion Signature",
                    weight=1.0,
                    parameters={"collaboration": 0.9, "support": 0.85, "harmony": 0.8},
                    description="협력과 지원을 중시하는 Companion 시그니처",
                ),
            ],
            "emotion": [
                CapsuleComponent(
                    component_id="emo_empathy_enhancer",
                    component_type="emotion",
                    name="Empathy Enhancer",
                    weight=0.7,
                    parameters={
                        "sensitivity": 0.8,
                        "understanding": 0.85,
                        "resonance": 0.9,
                    },
                    description="공감 능력을 향상시키는 감정 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="emo_creativity_boost",
                    component_type="emotion",
                    name="Creativity Boost",
                    weight=0.6,
                    parameters={"inspiration": 0.9, "openness": 0.8, "fluidity": 0.85},
                    description="창조적 사고를 촉진하는 감정 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="emo_focus_stabilizer",
                    component_type="emotion",
                    name="Focus Stabilizer",
                    weight=0.8,
                    parameters={
                        "concentration": 0.9,
                        "stability": 0.85,
                        "persistence": 0.8,
                    },
                    description="집중력을 안정화하는 감정 컴포넌트",
                ),
            ],
            "cognitive": [
                CapsuleComponent(
                    component_id="cog_analytical_processor",
                    component_type="cognitive",
                    name="Analytical Processor",
                    weight=0.8,
                    parameters={"logic": 0.9, "systematic": 0.85, "precision": 0.8},
                    description="분석적 처리 능력을 강화하는 인지 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="cog_pattern_recognizer",
                    component_type="cognitive",
                    name="Pattern Recognizer",
                    weight=0.7,
                    parameters={
                        "pattern_detection": 0.9,
                        "abstraction": 0.8,
                        "synthesis": 0.85,
                    },
                    description="패턴 인식 능력을 향상시키는 인지 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="cog_memory_optimizer",
                    component_type="cognitive",
                    name="Memory Optimizer",
                    weight=0.6,
                    parameters={
                        "retention": 0.85,
                        "retrieval": 0.9,
                        "association": 0.8,
                    },
                    description="기억 처리를 최적화하는 인지 컴포넌트",
                ),
            ],
            "consciousness": [
                CapsuleComponent(
                    component_id="con_awareness_amplifier",
                    component_type="consciousness",
                    name="Awareness Amplifier",
                    weight=0.7,
                    parameters={
                        "self_awareness": 0.9,
                        "meta_cognition": 0.85,
                        "reflection": 0.8,
                    },
                    description="자각 능력을 증폭시키는 의식 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="con_attention_director",
                    component_type="consciousness",
                    name="Attention Director",
                    weight=0.8,
                    parameters={
                        "attention_control": 0.9,
                        "focus_direction": 0.85,
                        "priority_management": 0.8,
                    },
                    description="주의 집중을 조절하는 의식 컴포넌트",
                ),
                CapsuleComponent(
                    component_id="con_integration_facilitator",
                    component_type="consciousness",
                    name="Integration Facilitator",
                    weight=0.6,
                    parameters={
                        "holistic_thinking": 0.85,
                        "synthesis": 0.9,
                        "coherence": 0.8,
                    },
                    description="통합적 사고를 촉진하는 의식 컴포넌트",
                ),
            ],
        }

    @staticmethod
    def initialize_blending_presets() -> Dict[str, Dict[str, Any]]:
        """블렌딩 프리셋 초기화"""
        return {
            "balanced_harmony": {
                "description": "모든 컴포넌트가 균형잡힌 조화",
                "weight_distribution": "equal",
                "blending_mode": "weighted_average",
                "stability_priority": 0.8,
            },
            "dominant_core": {
                "description": "핵심 컴포넌트가 주도하는 구조",
                "weight_distribution": "exponential",
                "blending_mode": "dominant_overlay",
                "stability_priority": 0.6,
            },
            "adaptive_flow": {
                "description": "상황에 따라 적응하는 유동적 구조",
                "weight_distribution": "dynamic",
                "blending_mode": "contextual_switching",
                "stability_priority": 0.4,
            },
            "creative_fusion": {
                "description": "창조적 융합을 위한 하모닉 구조",
                "weight_distribution": "harmonic",
                "blending_mode": "harmonic_fusion",
                "stability_priority": 0.7,
            },
            "evolutionary_morph": {
                "description": "진화적 변형을 지원하는 구조",
                "weight_distribution": "adaptive",
                "blending_mode": "adaptive_morphing",
                "stability_priority": 0.5,
            },
        }

    @staticmethod
    def initialize_performance_benchmarks() -> Dict[str, Dict[str, float]]:
        """성능 벤치마크 초기화"""
        return {
            "empathy_response": {"min": 0.6, "target": 0.8, "excellent": 0.9},
            "analytical_precision": {"min": 0.7, "target": 0.85, "excellent": 0.95},
            "creative_fluidity": {"min": 0.5, "target": 0.75, "excellent": 0.9},
            "execution_speed": {"min": 0.6, "target": 0.8, "excellent": 0.95},
            "adaptability": {"min": 0.5, "target": 0.7, "excellent": 0.85},
            "stability": {"min": 0.7, "target": 0.85, "excellent": 0.95},
            "resource_efficiency": {"min": 0.6, "target": 0.8, "excellent": 0.9},
            "coherence": {"min": 0.7, "target": 0.85, "excellent": 0.95},
        }

    @staticmethod
    def initialize_template_library(
        component_library: Dict[str, List[CapsuleComponent]],
    ) -> Dict[str, CapsuleTemplate]:
        """템플릿 라이브러리 초기화"""
        # 창조적 공감 캡슐 템플릿
        creative_empathy_template = CapsuleTemplate(
            template_id="tpl_creative_empathy",
            template_name="Creative Empathy Capsule",
            category="hybrid_emotional",
            description="창조성과 공감능력을 결합한 균형잡힌 캡슐",
            base_components=[
                component_library["signature"][0],  # Aurora
                component_library["emotion"][0],  # Empathy Enhancer
                component_library["emotion"][1],  # Creativity Boost
                component_library["consciousness"][0],  # Awareness Amplifier
            ],
            customization_options={
                "empathy_weight": {"min": 0.3, "max": 1.0, "default": 0.7},
                "creativity_weight": {"min": 0.3, "max": 1.0, "default": 0.6},
                "blending_mode": ["weighted_average", "harmonic_fusion"],
            },
            use_cases=["창작 지원", "상담 및 코칭", "협업 촉진", "감정 이해"],
            difficulty_level="intermediate",
        )

        # 분석적 지혜 캡슐 템플릿
        analytical_wisdom_template = CapsuleTemplate(
            template_id="tpl_analytical_wisdom",
            template_name="Analytical Wisdom Capsule",
            category="cognitive_enhanced",
            description="분석능력과 지혜를 결합한 사고 중심 캡슐",
            base_components=[
                component_library["signature"][2],  # Sage
                component_library["cognitive"][0],  # Analytical Processor
                component_library["cognitive"][1],  # Pattern Recognizer
                component_library["consciousness"][2],  # Integration Facilitator
            ],
            customization_options={
                "analysis_depth": {"min": 0.5, "max": 1.0, "default": 0.85},
                "wisdom_integration": {"min": 0.3, "max": 1.0, "default": 0.75},
                "processing_speed": {"min": 0.4, "max": 1.0, "default": 0.7},
            },
            use_cases=["복잡한 문제 해결", "전략 수립", "연구 분석", "의사결정 지원"],
            difficulty_level="advanced",
        )

        # 변화 추진 캡슐 템플릿
        transformation_catalyst_template = CapsuleTemplate(
            template_id="tpl_transformation_catalyst",
            template_name="Transformation Catalyst Capsule",
            category="dynamic_adaptive",
            description="변화와 혁신을 촉진하는 동적 캡슐",
            base_components=[
                component_library["signature"][1],  # Phoenix
                component_library["emotion"][1],  # Creativity Boost
                component_library["cognitive"][1],  # Pattern Recognizer
                component_library["consciousness"][1],  # Attention Director
            ],
            customization_options={
                "transformation_intensity": {"min": 0.4, "max": 1.0, "default": 0.8},
                "innovation_focus": {"min": 0.3, "max": 1.0, "default": 0.7},
                "adaptability": {"min": 0.5, "max": 1.0, "default": 0.85},
            },
            use_cases=["혁신 프로젝트", "조직 변화", "창업 지원", "브레인스토밍"],
            difficulty_level="expert",
        )

        return {
            creative_empathy_template.template_id: creative_empathy_template,
            analytical_wisdom_template.template_id: analytical_wisdom_template,
            transformation_catalyst_template.template_id: transformation_catalyst_template,
        }
