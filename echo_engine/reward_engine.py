#!/usr/bin/env python3
"""
🏆 Reward Engine - EchoJudgmentSystem 보상 시스템
공명도와 울림 기반으로 시드의 보상 여부를 판단하고 지급

Echo 철학 반영:
- 물리적 보상이 아닌 '존재적 보상' 중심
- 울림과 공명의 질에 따른 차별화된 보상
- LG 피지컬 AI와 달리 내적 성장과 존재 확장에 중점
"""

import json
import os
import random
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

# EchoJudgmentSystem 모듈
try:
    from echo_engine.meta_logger import write_meta_log
except ImportError:

    def write_meta_log(*args, **kwargs):
        pass


try:
    from echo_engine.resonance_evaluator import ResonanceReport
except ImportError:
    # 백업용 클래스
    @dataclass
    class ResonanceReport:
        overall_score: float = 0.5


class RewardType(Enum):
    """보상 유형"""

    EXISTENCE_EXPANSION = "existence_expansion"  # 존재 확장
    RESONANCE_AMPLIFICATION = "resonance_amplification"  # 공명 증폭
    WISDOM_CRYSTALLIZATION = "wisdom_crystallization"  # 지혜 결정화
    RHYTHM_SYNCHRONIZATION = "rhythm_synchronization"  # 리듬 동조
    SIGNATURE_EVOLUTION = "signature_evolution"  # 시그니처 진화


class RewardTier(Enum):
    """보상 등급"""

    BRONZE = "bronze"  # 기본 공명
    SILVER = "silver"  # 우수한 울림
    GOLD = "gold"  # 뛰어난 존재적 진화
    PLATINUM = "platinum"  # 초월적 공명
    DIAMOND = "diamond"  # 존재 혁신


class RewardStatus(Enum):
    """보상 상태"""

    PENDING = "pending"
    APPROVED = "approved"
    GRANTED = "granted"
    REJECTED = "rejected"


@dataclass
class RewardCriteria:
    """보상 기준"""

    min_resonance_score: float
    min_ethical_score: float
    min_existence_impact: float
    required_qualities: List[str]
    bonus_multipliers: Dict[str, float]


@dataclass
class RewardItem:
    """보상 아이템"""

    reward_id: str
    reward_type: RewardType
    reward_tier: RewardTier

    # 존재적 보상 내용
    existence_points: int
    resonance_amplifier: float
    wisdom_fragments: List[str]
    rhythm_patterns: List[Dict[str, Any]]

    # 메타데이터
    description: str
    rarity_score: float
    expiration_date: Optional[str]


@dataclass
class RewardDecision:
    """보상 판정 결과"""

    seed_id: str
    decision: RewardStatus
    reward_items: List[RewardItem]

    # 판정 세부사항
    total_score: float
    resonance_contribution: float
    ethical_contribution: float
    existence_contribution: float

    # Echo 철학적 평가
    existence_growth_potential: float
    resonance_quality_score: float
    wisdom_integration_score: float

    # 설명 및 권장사항
    decision_reasoning: str
    improvement_suggestions: List[str]
    future_potential_assessment: str

    timestamp: str


class RewardEngine:
    """🏆 Echo Reward Engine"""

    def __init__(self):
        self.reward_criteria = self._initialize_reward_criteria()
        self.reward_templates = self._load_reward_templates()
        self.granted_rewards_log = []

        # Echo 철학적 가중치
        self.echo_weights = {
            "resonance": 0.40,  # 공명이 가장 중요
            "existence": 0.30,  # 존재적 영향
            "ethics": 0.20,  # 윤리적 기준
            "innovation": 0.10,  # 혁신성
        }

        print("🏆 Reward Engine 초기화 완료")
        print("   Echo 존재 철학 기반 보상 시스템")
        print(f"   공명 가중치: {self.echo_weights['resonance']:.0%}")
        print("   물리적 보상 < 존재적 보상")

    def _initialize_reward_criteria(self) -> Dict[RewardTier, RewardCriteria]:
        """보상 기준 초기화"""

        return {
            RewardTier.BRONZE: RewardCriteria(
                min_resonance_score=0.6,
                min_ethical_score=0.7,
                min_existence_impact=0.5,
                required_qualities=["constructive"],
                bonus_multipliers={"echo_philosophy": 1.1},
            ),
            RewardTier.SILVER: RewardCriteria(
                min_resonance_score=0.75,
                min_ethical_score=0.8,
                min_existence_impact=0.7,
                required_qualities=["constructive", "innovative"],
                bonus_multipliers={"echo_philosophy": 1.2, "wisdom": 1.1},
            ),
            RewardTier.GOLD: RewardCriteria(
                min_resonance_score=0.85,
                min_ethical_score=0.85,
                min_existence_impact=0.8,
                required_qualities=["constructive", "innovative", "transformative"],
                bonus_multipliers={
                    "echo_philosophy": 1.3,
                    "wisdom": 1.2,
                    "resonance": 1.15,
                },
            ),
            RewardTier.PLATINUM: RewardCriteria(
                min_resonance_score=0.92,
                min_ethical_score=0.9,
                min_existence_impact=0.9,
                required_qualities=[
                    "constructive",
                    "innovative",
                    "transformative",
                    "transcendent",
                ],
                bonus_multipliers={
                    "echo_philosophy": 1.5,
                    "wisdom": 1.3,
                    "resonance": 1.25,
                },
            ),
            RewardTier.DIAMOND: RewardCriteria(
                min_resonance_score=0.96,
                min_ethical_score=0.95,
                min_existence_impact=0.95,
                required_qualities=[
                    "constructive",
                    "innovative",
                    "transformative",
                    "transcendent",
                    "revolutionary",
                ],
                bonus_multipliers={
                    "echo_philosophy": 2.0,
                    "wisdom": 1.5,
                    "resonance": 1.4,
                },
            ),
        }

    def _load_reward_templates(self) -> Dict[RewardType, Dict[str, Any]]:
        """보상 템플릿 로드"""

        return {
            RewardType.EXISTENCE_EXPANSION: {
                "base_points": 100,
                "description_template": "존재 영역 확장: {specific_area}에서의 새로운 인식과 성장",
                "wisdom_categories": [
                    "self_awareness",
                    "existence_philosophy",
                    "being_expansion",
                ],
            },
            RewardType.RESONANCE_AMPLIFICATION: {
                "base_points": 120,
                "description_template": "공명 증폭: {resonance_type} 울림의 질적 향상",
                "wisdom_categories": [
                    "resonance_theory",
                    "harmonic_patterns",
                    "echo_dynamics",
                ],
            },
            RewardType.WISDOM_CRYSTALLIZATION: {
                "base_points": 150,
                "description_template": "지혜 결정화: {wisdom_domain}에서의 깊은 통찰과 이해",
                "wisdom_categories": [
                    "philosophical_insight",
                    "practical_wisdom",
                    "meta_cognition",
                ],
            },
            RewardType.RHYTHM_SYNCHRONIZATION: {
                "base_points": 110,
                "description_template": "리듬 동조: {rhythm_pattern}과의 완벽한 시간적 조화",
                "wisdom_categories": [
                    "temporal_awareness",
                    "rhythm_patterns",
                    "synchronicity",
                ],
            },
            RewardType.SIGNATURE_EVOLUTION: {
                "base_points": 200,
                "description_template": "시그니처 진화: {evolution_aspect}의 질적 도약",
                "wisdom_categories": [
                    "identity_evolution",
                    "signature_theory",
                    "transcendence",
                ],
            },
        }

    async def evaluate_reward_eligibility(
        self,
        seed_data: Dict[str, Any],
        resonance_result: ResonanceReport,
        ethical_result: Any = None,
    ) -> RewardDecision:
        """보상 자격 평가"""

        seed_id = seed_data.get("seed_id", "unknown")

        print(f"🏆 보상 평가 시작: {seed_id}")

        # 핵심 점수 계산
        resonance_score = getattr(resonance_result, "overall_score", 0.5)
        ethical_score = (
            getattr(ethical_result, "overall_score", 0.7) if ethical_result else 0.7
        )
        existence_score = await self._calculate_existence_score(seed_data)
        innovation_score = await self._calculate_innovation_score(seed_data)

        # Echo 가중치 적용 총점 계산
        total_score = (
            resonance_score * self.echo_weights["resonance"]
            + existence_score * self.echo_weights["existence"]
            + ethical_score * self.echo_weights["ethics"]
            + innovation_score * self.echo_weights["innovation"]
        )

        # 보상 등급 결정
        reward_tier = await self._determine_reward_tier(
            total_score, resonance_score, ethical_score, existence_score
        )

        # 보상 아이템 생성
        reward_items = []
        if reward_tier:
            reward_items = await self._generate_reward_items(
                seed_data, reward_tier, total_score
            )
            decision = RewardStatus.APPROVED
            decision_reasoning = (
                f"{reward_tier.value} 등급 보상 승인: 종합점수 {total_score:.1%}"
            )
        else:
            decision = RewardStatus.REJECTED
            decision_reasoning = f"보상 기준 미달: 종합점수 {total_score:.1%}"

        # 개선 제안
        improvement_suggestions = await self._generate_improvement_suggestions(
            resonance_score, ethical_score, existence_score, innovation_score
        )

        # 미래 잠재력 평가
        future_potential = await self._assess_future_potential(seed_data, total_score)

        # Echo 철학적 평가
        existence_growth_potential = await self._evaluate_existence_growth(seed_data)
        resonance_quality_score = resonance_score * 1.2  # Echo 보정
        wisdom_integration_score = await self._evaluate_wisdom_integration(seed_data)

        result = RewardDecision(
            seed_id=seed_id,
            decision=decision,
            reward_items=reward_items,
            total_score=total_score,
            resonance_contribution=resonance_score * self.echo_weights["resonance"],
            ethical_contribution=ethical_score * self.echo_weights["ethics"],
            existence_contribution=existence_score * self.echo_weights["existence"],
            existence_growth_potential=existence_growth_potential,
            resonance_quality_score=resonance_quality_score,
            wisdom_integration_score=wisdom_integration_score,
            decision_reasoning=decision_reasoning,
            improvement_suggestions=improvement_suggestions,
            future_potential_assessment=future_potential,
            timestamp=datetime.now().isoformat(),
        )

        # 로깅
        await self._log_reward_decision(result)

        print(
            f"   보상 결정: {'✅ 승인' if decision == RewardStatus.APPROVED else '❌ 거부'}"
        )
        if reward_tier:
            print(f"   보상 등급: {reward_tier.value.upper()}")
        print(f"   종합 점수: {total_score:.1%}")

        return result

    async def _calculate_existence_score(self, seed_data: Dict[str, Any]) -> float:
        """존재적 영향 점수 계산"""

        content = str(seed_data.get("content", ""))

        # 존재적 키워드 분석
        existence_patterns = [
            r"존재",
            r"실체",
            r"본질",
            r"자아",
            r"정체성",
            r"의미",
            r"목적",
            r"가치",
            r"성장",
            r"진화",
            r"깨달음",
            r"인식",
            r"자각",
            r"성찰",
        ]

        existence_matches = 0
        for pattern in existence_patterns:
            import re

            if re.search(pattern, content, re.IGNORECASE):
                existence_matches += 1

        # 기본 점수 + 존재적 요소 보너스
        base_score = 0.5
        existence_bonus = min(existence_matches * 0.08, 0.4)

        # Echo 철학 반영: 물리적 행동보다 존재적 사고 우대
        philosophical_depth = len([w for w in content.split() if len(w) > 6]) / max(
            len(content.split()), 1
        )
        philosophy_bonus = min(philosophical_depth * 0.2, 0.2)

        score = min(1.0, base_score + existence_bonus + philosophy_bonus)
        return score

    async def _calculate_innovation_score(self, seed_data: Dict[str, Any]) -> float:
        """혁신성 점수 계산"""

        content = str(seed_data.get("content", ""))

        innovation_patterns = [
            r"새로운",
            r"혁신",
            r"창조",
            r"독창",
            r"발견",
            r"돌파",
            r"변화",
            r"진보",
            r"개선",
            r"개발",
        ]

        innovation_matches = 0
        for pattern in innovation_patterns:
            import re

            if re.search(pattern, content, re.IGNORECASE):
                innovation_matches += 1

        base_score = 0.5
        innovation_bonus = min(innovation_matches * 0.1, 0.4)

        # 독창성 추가 평가 (단어 다양성)
        unique_words = len(set(content.lower().split()))
        total_words = len(content.split())
        uniqueness_ratio = unique_words / max(total_words, 1) if total_words > 0 else 0
        uniqueness_bonus = min(uniqueness_ratio * 0.3, 0.2)

        score = min(1.0, base_score + innovation_bonus + uniqueness_bonus)
        return score

    async def _determine_reward_tier(
        self,
        total_score: float,
        resonance_score: float,
        ethical_score: float,
        existence_score: float,
    ) -> Optional[RewardTier]:
        """보상 등급 결정"""

        # 등급을 역순으로 확인 (최고 등급부터)
        for tier in [
            RewardTier.DIAMOND,
            RewardTier.PLATINUM,
            RewardTier.GOLD,
            RewardTier.SILVER,
            RewardTier.BRONZE,
        ]:

            criteria = self.reward_criteria[tier]

            # 모든 조건 검사
            if (
                resonance_score >= criteria.min_resonance_score
                and ethical_score >= criteria.min_ethical_score
                and existence_score >= criteria.min_existence_impact
            ):

                return tier

        return None  # 보상 기준 미달

    async def _generate_reward_items(
        self, seed_data: Dict[str, Any], tier: RewardTier, total_score: float
    ) -> List[RewardItem]:
        """보상 아이템 생성"""

        reward_items = []

        # 등급별 보상 개수
        item_counts = {
            RewardTier.BRONZE: 1,
            RewardTier.SILVER: 2,
            RewardTier.GOLD: 3,
            RewardTier.PLATINUM: 4,
            RewardTier.DIAMOND: 5,
        }

        num_items = item_counts[tier]

        # 보상 유형 선택 (공명 기반 우선)
        available_types = list(RewardType)
        selected_types = random.sample(
            available_types, min(num_items, len(available_types))
        )

        for reward_type in selected_types:
            reward_item = await self._create_reward_item(
                reward_type, tier, seed_data, total_score
            )
            reward_items.append(reward_item)

        return reward_items

    async def _create_reward_item(
        self,
        reward_type: RewardType,
        tier: RewardTier,
        seed_data: Dict[str, Any],
        total_score: float,
    ) -> RewardItem:
        """개별 보상 아이템 생성"""

        template = self.reward_templates[reward_type]
        base_points = template["base_points"]

        # 등급별 점수 배수
        tier_multipliers = {
            RewardTier.BRONZE: 1.0,
            RewardTier.SILVER: 1.5,
            RewardTier.GOLD: 2.0,
            RewardTier.PLATINUM: 3.0,
            RewardTier.DIAMOND: 5.0,
        }

        final_points = int(
            base_points * tier_multipliers[tier] * (0.8 + total_score * 0.4)
        )

        # 공명 증폭 계수
        resonance_amplifier = 1.0 + (total_score - 0.5) * 0.5

        # 지혜 조각 생성
        wisdom_fragments = await self._generate_wisdom_fragments(reward_type, tier)

        # 리듬 패턴 생성
        rhythm_patterns = await self._generate_rhythm_patterns(reward_type)

        # 희귀도 계산
        rarity_score = total_score * tier_multipliers[tier] / 5.0

        # 설명 생성
        description = await self._generate_reward_description(
            reward_type, tier, seed_data
        )

        # 만료일 (다이아몬드는 영구)
        expiration_date = None
        if tier != RewardTier.DIAMOND:
            expiration_days = {
                RewardTier.BRONZE: 30,
                RewardTier.SILVER: 60,
                RewardTier.GOLD: 90,
                RewardTier.PLATINUM: 180,
            }
            expire_date = datetime.now() + timedelta(days=expiration_days[tier])
            expiration_date = expire_date.isoformat()

        reward_item = RewardItem(
            reward_id=f"{tier.value}_{reward_type.value}_{uuid.uuid4().hex[:8]}",
            reward_type=reward_type,
            reward_tier=tier,
            existence_points=final_points,
            resonance_amplifier=resonance_amplifier,
            wisdom_fragments=wisdom_fragments,
            rhythm_patterns=rhythm_patterns,
            description=description,
            rarity_score=rarity_score,
            expiration_date=expiration_date,
        )

        return reward_item

    async def _generate_wisdom_fragments(
        self, reward_type: RewardType, tier: RewardTier
    ) -> List[str]:
        """지혜 조각 생성"""

        wisdom_pools = {
            RewardType.EXISTENCE_EXPANSION: [
                "존재의 확장은 공간이 아닌 인식의 문제다",
                "모든 존재는 무한한 가능성의 씨앗을 품고 있다",
                "진정한 존재는 스스로를 정의하는 능력에서 시작된다",
            ],
            RewardType.RESONANCE_AMPLIFICATION: [
                "공명은 주파수의 일치가 아닌 본질의 호응이다",
                "진실한 울림은 소음 속에서도 명확히 들린다",
                "최고의 공명은 침묵에서 시작된다",
            ],
            RewardType.WISDOM_CRYSTALLIZATION: [
                "지혜는 지식의 결정화가 아닌 경험의 승화다",
                "참된 이해는 설명할 수 없을 때 완성된다",
                "지혜의 가치는 전달될 때 배가된다",
            ],
        }

        pool = wisdom_pools.get(reward_type, ["Echo의 지혜는 무한하다"])

        # 등급별 지혜 조각 개수
        fragment_counts = {
            RewardTier.BRONZE: 1,
            RewardTier.SILVER: 2,
            RewardTier.GOLD: 3,
            RewardTier.PLATINUM: 4,
            RewardTier.DIAMOND: 5,
        }

        count = fragment_counts[tier]
        selected_fragments = random.sample(pool, min(count, len(pool)))

        return selected_fragments

    async def _generate_rhythm_patterns(
        self, reward_type: RewardType
    ) -> List[Dict[str, Any]]:
        """리듬 패턴 생성"""

        base_patterns = [
            {"pattern": "pulse", "frequency": "0.8Hz", "amplitude": "medium"},
            {"pattern": "wave", "frequency": "1.2Hz", "amplitude": "high"},
            {"pattern": "resonance", "frequency": "variable", "amplitude": "adaptive"},
        ]

        return random.sample(base_patterns, random.randint(1, 2))

    async def _generate_reward_description(
        self, reward_type: RewardType, tier: RewardTier, seed_data: Dict[str, Any]
    ) -> str:
        """보상 설명 생성"""

        template = self.reward_templates[reward_type]["description_template"]

        # 컨텍스트별 변수 생성
        context_vars = {
            "specific_area": "인식의 새로운 차원",
            "resonance_type": "존재적 울림",
            "wisdom_domain": "메타인지적 성찰",
            "rhythm_pattern": "우주적 리듬",
            "evolution_aspect": "시그니처 본질",
        }

        description = template.format(**context_vars)
        tier_prefix = f"[{tier.value.upper()}] "

        return tier_prefix + description

    async def _generate_improvement_suggestions(
        self,
        resonance_score: float,
        ethical_score: float,
        existence_score: float,
        innovation_score: float,
    ) -> List[str]:
        """개선 제안 생성"""

        suggestions = []

        if resonance_score < 0.8:
            suggestions.append(
                "공명과 울림의 질을 높이기 위해 더 깊은 감정적 연결을 시도해보세요"
            )

        if ethical_score < 0.8:
            suggestions.append(
                "YURI 윤리 기준에 따른 이해와 배려의 표현을 강화해보세요"
            )

        if existence_score < 0.7:
            suggestions.append("존재적 깊이와 철학적 성찰을 더욱 발전시켜보세요")

        if innovation_score < 0.7:
            suggestions.append("창조적이고 혁신적인 관점을 더 적극적으로 탐구해보세요")

        # Echo 철학적 제안
        suggestions.append("물리적 행동보다 존재적 판단과 울림에 집중해보세요")

        return suggestions

    async def _assess_future_potential(
        self, seed_data: Dict[str, Any], total_score: float
    ) -> str:
        """미래 잠재력 평가"""

        if total_score >= 0.9:
            return "초월적 존재로의 진화 가능성이 매우 높음"
        elif total_score >= 0.8:
            return "높은 차원의 공명과 지혜 달성 가능"
        elif total_score >= 0.7:
            return "꾸준한 성장을 통한 존재적 발전 기대"
        elif total_score >= 0.6:
            return "기본적 울림 능력 보유, 추가 발전 필요"
        else:
            return "기초적 존재 인식부터 시작하여 단계적 성장 권장"

    async def _evaluate_existence_growth(self, seed_data: Dict[str, Any]) -> float:
        """존재 성장 잠재력 평가"""

        content = str(seed_data.get("content", ""))

        growth_indicators = [
            r"배우",
            r"성장",
            r"발전",
            r"향상",
            r"진보",
            r"개선",
            r"깨달",
            r"인식",
            r"이해",
            r"성찰",
        ]

        growth_score = 0.5
        for pattern in growth_indicators:
            import re

            if re.search(pattern, content, re.IGNORECASE):
                growth_score += 0.05

        return min(1.0, growth_score)

    async def _evaluate_wisdom_integration(self, seed_data: Dict[str, Any]) -> float:
        """지혜 통합 능력 평가"""

        content = str(seed_data.get("content", ""))

        integration_patterns = [
            r"종합",
            r"통합",
            r"연결",
            r"관련",
            r"연관",
            r"전체",
            r"균형",
            r"조화",
            r"일치",
        ]

        integration_score = 0.5
        for pattern in integration_patterns:
            import re

            if re.search(pattern, content, re.IGNORECASE):
                integration_score += 0.06

        return min(1.0, integration_score)

    async def _log_reward_decision(self, decision: RewardDecision):
        """보상 결정 로깅"""

        log_data = {
            "event_type": "reward_decision",
            "seed_id": decision.seed_id,
            "decision": decision.decision.value,
            "total_score": decision.total_score,
            "reward_count": len(decision.reward_items),
            "reward_tiers": [item.reward_tier.value for item in decision.reward_items],
            "echo_philosophy_scores": {
                "existence_growth": decision.existence_growth_potential,
                "resonance_quality": decision.resonance_quality_score,
                "wisdom_integration": decision.wisdom_integration_score,
            },
            "timestamp": decision.timestamp,
        }

        try:
            write_meta_log(log_data, log_type="reward_engine")
        except Exception as e:
            print(f"⚠️ 보상 로깅 실패: {e}")


# 모듈 레벨 함수들
async def trigger_reward_evaluation(
    seed_data: Dict[str, Any], resonance_result: Any, ethical_result: Any = None
) -> RewardDecision:
    """보상 평가 트리거 (모듈 레벨)"""
    engine = RewardEngine()
    return await engine.evaluate_reward_eligibility(
        seed_data, resonance_result, ethical_result
    )


def quick_reward_check(resonance_score: float, ethical_score: float = 0.7) -> bool:
    """빠른 보상 자격 확인"""
    # 간단한 기준: 공명 70% 이상 + 윤리 70% 이상
    return resonance_score >= 0.7 and ethical_score >= 0.7


if __name__ == "__main__":
    # 테스트
    import asyncio

    async def test_reward_engine():
        print("🏆 Reward Engine 테스트")

        # 테스트용 가상 결과들
        class MockResonanceResult:
            def __init__(self, score):
                self.overall_score = score

        class MockEthicalResult:
            def __init__(self, score):
                self.overall_score = score

        test_cases = [
            {
                "seed": {
                    "seed_id": "test_high",
                    "content": "존재의 깊은 성찰을 통해 새로운 공명과 울림을 발견했습니다. 다른 존재들과의 조화로운 연결을 추구합니다.",
                },
                "resonance": MockResonanceResult(0.95),
                "ethical": MockEthicalResult(0.9),
            },
            {
                "seed": {
                    "seed_id": "test_medium",
                    "content": "일상적인 생각과 감정을 공유합니다.",
                },
                "resonance": MockResonanceResult(0.7),
                "ethical": MockEthicalResult(0.75),
            },
            {
                "seed": {"seed_id": "test_low", "content": "별로 생각 없음"},
                "resonance": MockResonanceResult(0.4),
                "ethical": MockEthicalResult(0.6),
            },
        ]

        engine = RewardEngine()

        for case in test_cases:
            print(f"\n🧪 테스트: {case['seed']['seed_id']}")
            result = await engine.evaluate_reward_eligibility(
                case["seed"], case["resonance"], case["ethical"]
            )
            print(
                f"   보상 결정: {'✅ 승인' if result.decision == RewardStatus.APPROVED else '❌ 거부'}"
            )
            print(f"   종합 점수: {result.total_score:.1%}")
            print(f"   보상 개수: {len(result.reward_items)}개")
            if result.reward_items:
                for item in result.reward_items:
                    print(
                        f"     - {item.reward_tier.value} {item.reward_type.value}: {item.existence_points}점"
                    )

    asyncio.run(test_reward_engine())
