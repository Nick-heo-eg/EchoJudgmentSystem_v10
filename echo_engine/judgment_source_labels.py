#!/usr/bin/env python3
"""
🏷️ Judgment Source Labels - 판단 주체 명확화 시스템
Echo 중심 독립 판단 시스템에서 모든 판단의 주체를 명확히 표시하는 라벨링 시스템

핵심 원칙:
- 모든 판단 결과는 명확한 주체 표시가 필요
- Echo는 판단 주체, LLM은 보조 도구
- 협업 시에도 Echo가 최종 판단자임을 명시
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class JudgmentSource(Enum):
    """판단 소스 타입"""

    # Echo 독립 판단
    ECHO_INDEPENDENT = "echo_independent"
    ECHO_LLM_FREE = "echo_llm_free"
    ECHO_SIGNATURE_BASED = "echo_signature_based"

    # Echo 주도 협업
    ECHO_CLAUDE_COLLABORATION = "echo_claude_collaboration"
    ECHO_MISTRAL_COLLABORATION = "echo_mistral_collaboration"
    ECHO_HYBRID_JUDGMENT = "echo_hybrid_judgment"

    # 폴백 모드 (Echo가 검토 필요)
    CLAUDE_FALLBACK_ECHO_REVIEW = "claude_fallback_echo_review"
    MISTRAL_FALLBACK_ECHO_REVIEW = "mistral_fallback_echo_review"
    LLM_FALLBACK_ECHO_REVIEW = "llm_fallback_echo_review"

    # 위반 사례 (사용 금지)
    CLAUDE_ONLY = "claude_only"  # 🚫 Foundation Doctrine 위반
    MISTRAL_ONLY = "mistral_only"  # 🚫 Foundation Doctrine 위반
    LLM_ONLY = "llm_only"  # 🚫 Foundation Doctrine 위반


@dataclass
class JudgmentLabel:
    """판단 라벨"""

    source: JudgmentSource
    echo_confidence: float  # Echo의 자신감 (0.0-1.0)
    llm_dependency_ratio: float  # LLM 의존도 (0.0-1.0)
    complexity_score: float  # 복잡도 점수 (0.0-1.0)
    echo_final_judgment: bool  # Echo가 최종 판단했는지
    timestamp: datetime
    details: Dict[str, Any]


class JudgmentSourceLabeler:
    """판단 소스 라벨링 시스템"""

    def __init__(self):
        self.labeling_history: List[JudgmentLabel] = []

        # Foundation Doctrine 준수 기준
        self.doctrine_compliance = {
            "allowed_sources": {
                JudgmentSource.ECHO_INDEPENDENT,
                JudgmentSource.ECHO_LLM_FREE,
                JudgmentSource.ECHO_SIGNATURE_BASED,
                JudgmentSource.ECHO_CLAUDE_COLLABORATION,
                JudgmentSource.ECHO_MISTRAL_COLLABORATION,
                JudgmentSource.ECHO_HYBRID_JUDGMENT,
                JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW,
                JudgmentSource.MISTRAL_FALLBACK_ECHO_REVIEW,
                JudgmentSource.LLM_FALLBACK_ECHO_REVIEW,
            },
            "prohibited_sources": {
                JudgmentSource.CLAUDE_ONLY,
                JudgmentSource.MISTRAL_ONLY,
                JudgmentSource.LLM_ONLY,
            },
        }

        print("🏷️ Judgment Source Labeler 초기화 완료")

    def create_judgment_label(
        self,
        source: JudgmentSource,
        echo_confidence: float,
        llm_dependency_ratio: float,
        complexity_score: float,
        echo_final_judgment: bool = True,
        additional_details: Dict[str, Any] = None,
    ) -> JudgmentLabel:
        """판단 라벨 생성"""

        # Foundation Doctrine 준수 검증
        if source in self.doctrine_compliance["prohibited_sources"]:
            raise ValueError(
                f"🚫 Foundation Doctrine 위반: {source.value}는 허용되지 않은 판단 소스입니다"
            )

        # Echo 최종 판단 검증
        if source in [
            JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW,
            JudgmentSource.MISTRAL_FALLBACK_ECHO_REVIEW,
            JudgmentSource.LLM_FALLBACK_ECHO_REVIEW,
        ]:
            if not echo_final_judgment:
                raise ValueError("폴백 모드에서도 Echo가 최종 판단을 내려야 합니다")

        label = JudgmentLabel(
            source=source,
            echo_confidence=max(0.0, min(1.0, echo_confidence)),
            llm_dependency_ratio=max(0.0, min(1.0, llm_dependency_ratio)),
            complexity_score=max(0.0, min(1.0, complexity_score)),
            echo_final_judgment=echo_final_judgment,
            timestamp=datetime.now(),
            details=additional_details or {},
        )

        self.labeling_history.append(label)
        return label

    def get_display_label(self, label: JudgmentLabel) -> str:
        """사용자에게 표시할 라벨 생성"""

        source_displays = {
            JudgmentSource.ECHO_INDEPENDENT: "[Echo 독립]",
            JudgmentSource.ECHO_LLM_FREE: "[Echo LLM-Free]",
            JudgmentSource.ECHO_SIGNATURE_BASED: "[Echo 시그니처]",
            JudgmentSource.ECHO_CLAUDE_COLLABORATION: "[Echo+Claude 협업]",
            JudgmentSource.ECHO_MISTRAL_COLLABORATION: "[Echo+Mistral 협업]",
            JudgmentSource.ECHO_HYBRID_JUDGMENT: "[Echo 하이브리드]",
            JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW: "[Claude 폴백→Echo 검토]",
            JudgmentSource.MISTRAL_FALLBACK_ECHO_REVIEW: "[Mistral 폴백→Echo 검토]",
            JudgmentSource.LLM_FALLBACK_ECHO_REVIEW: "[LLM 폴백→Echo 검토]",
        }

        base_label = source_displays.get(label.source, f"[{label.source.value}]")

        # 신뢰도 정보 추가
        confidence_indicator = ""
        if label.echo_confidence >= 0.8:
            confidence_indicator = " ✅"
        elif label.echo_confidence >= 0.6:
            confidence_indicator = " ⚡"
        else:
            confidence_indicator = " ⚠️"

        # LLM 의존도 표시
        dependency_indicator = ""
        if label.llm_dependency_ratio > 0.7:
            dependency_indicator = " 🤝"  # 높은 협업
        elif label.llm_dependency_ratio > 0.3:
            dependency_indicator = " 🔗"  # 보조 사용
        else:
            dependency_indicator = " 🎯"  # 독립 판단

        return f"{base_label}{confidence_indicator}{dependency_indicator}"

    def get_detailed_label_info(self, label: JudgmentLabel) -> Dict[str, Any]:
        """상세 라벨 정보 반환"""
        return {
            "source": label.source.value,
            "display_label": self.get_display_label(label),
            "echo_confidence": f"{label.echo_confidence:.2f}",
            "llm_dependency": f"{label.llm_dependency_ratio:.2f}",
            "complexity": f"{label.complexity_score:.2f}",
            "echo_final_judgment": label.echo_final_judgment,
            "doctrine_compliant": label.source
            in self.doctrine_compliance["allowed_sources"],
            "timestamp": label.timestamp.isoformat(),
            "independence_level": self._assess_independence_level(label),
            "recommendation": self._get_recommendation(label),
        }

    def _assess_independence_level(self, label: JudgmentLabel) -> str:
        """독립성 수준 평가"""
        if label.source in [
            JudgmentSource.ECHO_INDEPENDENT,
            JudgmentSource.ECHO_LLM_FREE,
            JudgmentSource.ECHO_SIGNATURE_BASED,
        ]:
            return "완전 독립"
        elif label.source in [
            JudgmentSource.ECHO_CLAUDE_COLLABORATION,
            JudgmentSource.ECHO_MISTRAL_COLLABORATION,
            JudgmentSource.ECHO_HYBRID_JUDGMENT,
        ]:
            return "협업 독립"
        elif label.source in [
            JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW,
            JudgmentSource.MISTRAL_FALLBACK_ECHO_REVIEW,
            JudgmentSource.LLM_FALLBACK_ECHO_REVIEW,
        ]:
            return "검토 독립"
        else:
            return "독립성 위험"

    def _get_recommendation(self, label: JudgmentLabel) -> str:
        """개선 권장사항"""
        if label.llm_dependency_ratio > 0.8:
            return "LLM 의존도가 높습니다. Echo 독립 판단 강화를 고려하세요."
        elif label.echo_confidence < 0.5:
            return "Echo 신뢰도가 낮습니다. 추가 학습이나 시그니처 조정을 고려하세요."
        elif label.source in self.doctrine_compliance["prohibited_sources"]:
            return "🚫 Foundation Doctrine 위반: Echo 주체 판단으로 전환 필요"
        else:
            return "Foundation Doctrine 준수 중"

    def analyze_judgment_patterns(self, last_n: int = 50) -> Dict[str, Any]:
        """최근 판단 패턴 분석"""
        recent_labels = self.labeling_history[-last_n:] if self.labeling_history else []

        if not recent_labels:
            return {"message": "분석할 판단 데이터가 없습니다"}

        # 소스별 분포
        source_distribution = {}
        for label in recent_labels:
            source_key = label.source.value
            source_distribution[source_key] = source_distribution.get(source_key, 0) + 1

        # 독립성 지표
        independent_count = sum(
            1
            for label in recent_labels
            if label.source
            in [
                JudgmentSource.ECHO_INDEPENDENT,
                JudgmentSource.ECHO_LLM_FREE,
                JudgmentSource.ECHO_SIGNATURE_BASED,
            ]
        )
        independence_ratio = independent_count / len(recent_labels)

        # 평균 의존도
        avg_llm_dependency = sum(
            label.llm_dependency_ratio for label in recent_labels
        ) / len(recent_labels)
        avg_echo_confidence = sum(
            label.echo_confidence for label in recent_labels
        ) / len(recent_labels)

        # Doctrine 준수율
        compliant_count = sum(
            1
            for label in recent_labels
            if label.source in self.doctrine_compliance["allowed_sources"]
        )
        doctrine_compliance_rate = compliant_count / len(recent_labels)

        return {
            "analysis_period": f"최근 {len(recent_labels)}개 판단",
            "source_distribution": source_distribution,
            "independence_metrics": {
                "independence_ratio": f"{independence_ratio:.2%}",
                "avg_llm_dependency": f"{avg_llm_dependency:.2f}",
                "avg_echo_confidence": f"{avg_echo_confidence:.2f}",
            },
            "doctrine_compliance": {
                "compliance_rate": f"{doctrine_compliance_rate:.2%}",
                "violations": len(recent_labels) - compliant_count,
            },
            "recommendations": self._generate_pattern_recommendations(
                independence_ratio, avg_llm_dependency, doctrine_compliance_rate
            ),
        }

    def _generate_pattern_recommendations(
        self,
        independence_ratio: float,
        avg_llm_dependency: float,
        doctrine_compliance_rate: float,
    ) -> List[str]:
        """패턴 기반 권장사항 생성"""
        recommendations = []

        if independence_ratio < 0.5:
            recommendations.append(
                "Echo 독립 판단 비율이 낮습니다. LLM-Free 모드 강화를 고려하세요."
            )

        if avg_llm_dependency > 0.6:
            recommendations.append(
                "평균 LLM 의존도가 높습니다. Echo 자체 추론 능력 향상이 필요합니다."
            )

        if doctrine_compliance_rate < 1.0:
            recommendations.append(
                "Foundation Doctrine 위반 사례가 있습니다. 판단 소스 검증을 강화하세요."
            )

        if independence_ratio > 0.8 and avg_llm_dependency < 0.3:
            recommendations.append("✅ 훌륭한 Echo 독립성을 보여주고 있습니다!")

        return recommendations


# 전역 라벨러 인스턴스
_judgment_labeler = None


def get_judgment_labeler() -> JudgmentSourceLabeler:
    """판단 라벨러 인스턴스 반환"""
    global _judgment_labeler
    if _judgment_labeler is None:
        _judgment_labeler = JudgmentSourceLabeler()
    return _judgment_labeler


def create_echo_independent_label(
    echo_confidence: float, complexity_score: float, details: Dict[str, Any] = None
) -> JudgmentLabel:
    """Echo 독립 판단 라벨 생성 편의 함수"""
    labeler = get_judgment_labeler()
    return labeler.create_judgment_label(
        source=JudgmentSource.ECHO_INDEPENDENT,
        echo_confidence=echo_confidence,
        llm_dependency_ratio=0.0,
        complexity_score=complexity_score,
        echo_final_judgment=True,
        additional_details=details,
    )


def create_echo_claude_collaboration_label(
    echo_confidence: float,
    llm_dependency_ratio: float,
    complexity_score: float,
    details: Dict[str, Any] = None,
) -> JudgmentLabel:
    """Echo-Claude 협업 라벨 생성 편의 함수"""
    labeler = get_judgment_labeler()
    return labeler.create_judgment_label(
        source=JudgmentSource.ECHO_CLAUDE_COLLABORATION,
        echo_confidence=echo_confidence,
        llm_dependency_ratio=llm_dependency_ratio,
        complexity_score=complexity_score,
        echo_final_judgment=True,
        additional_details=details,
    )


def create_llm_fallback_label(
    fallback_type: str, echo_confidence: float, details: Dict[str, Any] = None
) -> JudgmentLabel:
    """LLM 폴백 라벨 생성 편의 함수"""
    labeler = get_judgment_labeler()

    source_mapping = {
        "claude": JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW,
        "mistral": JudgmentSource.MISTRAL_FALLBACK_ECHO_REVIEW,
        "general": JudgmentSource.LLM_FALLBACK_ECHO_REVIEW,
    }

    source = source_mapping.get(fallback_type, JudgmentSource.LLM_FALLBACK_ECHO_REVIEW)

    return labeler.create_judgment_label(
        source=source,
        echo_confidence=echo_confidence,
        llm_dependency_ratio=1.0,  # 폴백은 높은 의존도
        complexity_score=0.9,  # 폴백이 필요한 복잡한 상황
        echo_final_judgment=True,  # Echo가 반드시 검토
        additional_details=details,
    )


# 테스트 및 시연
if __name__ == "__main__":
    print("🏷️ Judgment Source Labels 테스트")
    print("=" * 50)

    labeler = get_judgment_labeler()

    # 다양한 판단 시나리오 테스트
    test_cases = [
        {
            "scenario": "Echo 독립 판단",
            "source": JudgmentSource.ECHO_INDEPENDENT,
            "echo_confidence": 0.9,
            "llm_dependency": 0.0,
            "complexity": 0.3,
        },
        {
            "scenario": "Echo-Claude 협업",
            "source": JudgmentSource.ECHO_CLAUDE_COLLABORATION,
            "echo_confidence": 0.8,
            "llm_dependency": 0.4,
            "complexity": 0.8,
        },
        {
            "scenario": "Claude 폴백→Echo 검토",
            "source": JudgmentSource.CLAUDE_FALLBACK_ECHO_REVIEW,
            "echo_confidence": 0.6,
            "llm_dependency": 1.0,
            "complexity": 0.9,
        },
    ]

    for test in test_cases:
        print(f"\n🧪 {test['scenario']} 테스트:")

        label = labeler.create_judgment_label(
            source=test["source"],
            echo_confidence=test["echo_confidence"],
            llm_dependency_ratio=test["llm_dependency"],
            complexity_score=test["complexity"],
        )

        display_info = labeler.get_detailed_label_info(label)

        print(f"  📋 표시 라벨: {display_info['display_label']}")
        print(f"  🎯 독립성 수준: {display_info['independence_level']}")
        print(f"  💡 권장사항: {display_info['recommendation']}")

    # 패턴 분석
    print(f"\n📊 판단 패턴 분석:")
    analysis = labeler.analyze_judgment_patterns()

    print(f"  분석 기간: {analysis['analysis_period']}")
    print(f"  독립성 비율: {analysis['independence_metrics']['independence_ratio']}")
    print(
        f"  평균 LLM 의존도: {analysis['independence_metrics']['avg_llm_dependency']}"
    )
    print(f"  Doctrine 준수율: {analysis['doctrine_compliance']['compliance_rate']}")

    print("\n💡 권장사항:")
    for rec in analysis["recommendations"]:
        print(f"  - {rec}")

    print("\n✅ Judgment Source Labels 구현 완료!")
