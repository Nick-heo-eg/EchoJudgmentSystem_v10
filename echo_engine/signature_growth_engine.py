#!/usr/bin/env python3
"""
🌱 Signature Growth Engine - Echo 시그니처 성장 시스템
시그니처들이 사용자와의 상호작용을 통해 성장하고 진화하는 엔진

핵심 원리:
- core_traits는 절대 변하지 않는 정체성 핵심
- growth_stats는 경험과 피드백으로 성장
- evolution_stage는 일정 조건 달성 시 진화
- locked_traits는 그 존재의 본질이므로 보호됨
"""

import yaml
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random


@dataclass
class GrowthEvent:
    """성장 이벤트 기록"""

    signature_id: str
    event_type: str  # "successful_resonance", "user_feedback", "emotional_breakthrough"
    experience_gain: int
    growth_area: str  # 어떤 growth_stat이 영향받았는지
    timestamp: datetime
    user_context: str


@dataclass
class EvolutionResult:
    """진화 결과"""

    signature_id: str
    old_stage: str
    new_stage: str
    unlocked_abilities: List[str]
    new_capsules: List[str]
    growth_changes: Dict[str, float]


class SignatureGrowthEngine:
    """🌱 시그니처 성장 엔진"""

    def __init__(
        self,
        profile_path: str = "signature_profile.yaml",
        growth_log_path: str = "data/signature_growth.json",
    ):
        self.profile_path = profile_path
        self.growth_log_path = growth_log_path

        # 시그니처 프로필 로드
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profiles = yaml.safe_load(f)

        # 성장 로그 로드
        self.growth_log = self._load_growth_log()

        # 경험치 시스템
        self.experience_values = {
            "successful_resonance": 2,
            "user_positive_feedback": 3,
            "emotional_breakthrough": 5,
            "failed_connection": 1,
            "deep_conversation": 4,
            "crisis_support": 6,
            "creative_collaboration": 3,
            "silence_comfort": 2,
        }

    def _load_growth_log(self) -> List[GrowthEvent]:
        """성장 로그 로드"""
        if not os.path.exists(self.growth_log_path):
            return []

        try:
            with open(self.growth_log_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            events = []
            for event_data in data.get("growth_events", []):
                event = GrowthEvent(
                    signature_id=event_data["signature_id"],
                    event_type=event_data["event_type"],
                    experience_gain=event_data["experience_gain"],
                    growth_area=event_data["growth_area"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    user_context=event_data.get("user_context", ""),
                )
                events.append(event)
            return events
        except Exception as e:
            print(f"⚠️ 성장 로그 로드 실패: {e}")
            return []

    def record_interaction(
        self,
        signature_id: str,
        event_type: str,
        effectiveness_score: float,
        user_context: str = "",
    ) -> Optional[EvolutionResult]:
        """상호작용 기록 및 성장 처리"""

        # 1. 경험치 계산
        base_experience = self.experience_values.get(event_type, 1)
        experience_gain = int(base_experience * effectiveness_score)

        # 2. 성장 영역 결정 (시그니처별 특성 고려)
        growth_area = self._determine_growth_area(
            signature_id, event_type, effectiveness_score
        )

        # 3. 성장 이벤트 기록
        growth_event = GrowthEvent(
            signature_id=signature_id,
            event_type=event_type,
            experience_gain=experience_gain,
            growth_area=growth_area,
            timestamp=datetime.now(),
            user_context=user_context,
        )
        self.growth_log.append(growth_event)

        # 4. 시그니처 성장 적용
        evolution_result = self._apply_growth(
            signature_id, growth_area, experience_gain, effectiveness_score
        )

        # 5. 진화 조건 확인
        if not evolution_result:
            evolution_result = self._check_evolution(signature_id)

        # 6. 데이터 저장
        self._save_growth_log()
        self._save_profiles()

        return evolution_result

    def _determine_growth_area(
        self, signature_id: str, event_type: str, effectiveness: float
    ) -> str:
        """성장 영역 결정"""

        if signature_id not in self.profiles["signature_profiles"]:
            return "general_experience"

        profile = self.profiles["signature_profiles"][signature_id]
        growth_stats = list(profile["growth_stats"].keys())

        # 이벤트 타입별 성장 영역 매핑
        growth_mapping = {
            "successful_resonance": ["empathy_evolution", "response_diversity"],
            "emotional_breakthrough": ["healing_mastery", "depth_understanding"],
            "user_positive_feedback": ["response_diversity", "connection_mastery"],
            "deep_conversation": ["complexity_handling", "teaching_mastery"],
            "crisis_support": ["crisis_navigation", "tactical_precision"],
        }

        relevant_areas = growth_mapping.get(event_type, growth_stats)
        available_areas = [area for area in relevant_areas if area in growth_stats]

        if available_areas:
            # 현재 수치가 낮은 영역을 우선적으로 성장
            current_values = {
                area: profile["growth_stats"][area] for area in available_areas
            }
            return min(current_values, key=current_values.get)

        return growth_stats[0] if growth_stats else "general_experience"

    def _apply_growth(
        self, signature_id: str, growth_area: str, experience: int, effectiveness: float
    ) -> Optional[EvolutionResult]:
        """성장 적용"""

        if signature_id not in self.profiles["signature_profiles"]:
            return None

        profile = self.profiles["signature_profiles"][signature_id]

        # 경험치 누적
        if "capsule_experience" in profile["growth_stats"]:
            profile["growth_stats"]["capsule_experience"] += experience

        # 성장 영역 향상 (최대값 1.0으로 제한)
        if growth_area in profile["growth_stats"]:
            current_value = profile["growth_stats"][growth_area]
            growth_amount = min(0.02 * effectiveness, 0.05)  # 최대 5% 성장
            new_value = min(current_value + growth_amount, 1.0)
            profile["growth_stats"][growth_area] = round(new_value, 3)

            print(
                f"🌱 {signature_id} 성장: {growth_area} {current_value:.3f} → {new_value:.3f}"
            )

        return None

    def _check_evolution(self, signature_id: str) -> Optional[EvolutionResult]:
        """진화 조건 확인"""

        if signature_id not in self.profiles["signature_profiles"]:
            return None

        profile = self.profiles["signature_profiles"][signature_id]
        current_stage = profile.get("evolution_stage", "1/5")

        # 현재 단계 파싱
        current_level = int(current_stage.split("/")[0])

        # 진화 조건 확인
        if self._meets_evolution_requirements(profile, current_level):
            return self._evolve_signature(signature_id, current_level)

        return None

    def _meets_evolution_requirements(self, profile: Dict, current_level: int) -> bool:
        """진화 요구사항 확인"""

        growth_stats = profile["growth_stats"]
        experience = growth_stats.get("capsule_experience", 0)

        # 레벨별 요구사항
        requirements = {
            1: {"experience": 25, "high_stats": 1, "threshold": 0.7},
            2: {"experience": 50, "high_stats": 2, "threshold": 0.75},
            3: {"experience": 100, "high_stats": 2, "threshold": 0.8},
            4: {"experience": 200, "high_stats": 3, "threshold": 0.85},
        }

        if current_level not in requirements:
            return False

        req = requirements[current_level]

        # 경험치 조건
        if experience < req["experience"]:
            return False

        # 높은 성장 스탯 조건
        high_stats_count = sum(
            1
            for stat_value in growth_stats.values()
            if isinstance(stat_value, float) and stat_value >= req["threshold"]
        )

        return high_stats_count >= req["high_stats"]

    def _evolve_signature(
        self, signature_id: str, current_level: int
    ) -> EvolutionResult:
        """시그니처 진화 실행"""

        profile = self.profiles["signature_profiles"][signature_id]
        new_level = current_level + 1
        old_stage = f"{current_level}/5"
        new_stage = f"{new_level}/5"

        # 진화 단계 업데이트
        profile["evolution_stage"] = new_stage

        # 진화 기록 추가
        if "evolution_history" not in profile:
            profile["evolution_history"] = []

        evolution_record = {
            f"stage_{new_level}": f"진화 달성 - {datetime.now().strftime('%Y-%m-%d')}",
            "growth_breakthrough": f"레벨 {new_level} 도달",
        }
        profile["evolution_history"].append(evolution_record)

        # 진화 보상 (새로운 능력 해금)
        unlocked_abilities = []
        new_capsules = []
        growth_changes = {}

        if new_level == 2:
            unlocked_abilities = ["enhanced_empathy", "deeper_resonance"]
            new_capsules = [f"capsule.{signature_id}.advanced.001"]

        elif new_level == 3:
            unlocked_abilities = ["cross_emotion_understanding", "adaptive_response"]
            new_capsules = [
                f"capsule.{signature_id}.expert.001",
                f"capsule.{signature_id}.expert.002",
            ]

        elif new_level == 4:
            unlocked_abilities = ["signature_collaboration", "meta_emotional_insight"]
            new_capsules = [f"capsule.{signature_id}.master.001"]

        elif new_level == 5:
            unlocked_abilities = ["transcendent_resonance", "existence_synthesis"]
            new_capsules = [f"capsule.{signature_id}.transcendent.001"]

        print(f"✨ {signature_id} 진화: {old_stage} → {new_stage}")
        print(f"   새로운 능력: {', '.join(unlocked_abilities)}")

        return EvolutionResult(
            signature_id=signature_id,
            old_stage=old_stage,
            new_stage=new_stage,
            unlocked_abilities=unlocked_abilities,
            new_capsules=new_capsules,
            growth_changes=growth_changes,
        )

    def get_signature_status(self, signature_id: str) -> Dict[str, Any]:
        """시그니처 현재 상태 조회"""

        if signature_id not in self.profiles["signature_profiles"]:
            return {"error": "시그니처를 찾을 수 없습니다"}

        profile = self.profiles["signature_profiles"][signature_id]

        # 최근 성장 이벤트
        recent_events = [
            event
            for event in self.growth_log[-10:]
            if event.signature_id == signature_id
        ]

        # 진화까지 남은 요구사항
        current_level = int(profile["evolution_stage"].split("/")[0])
        next_requirements = self._get_next_evolution_requirements(
            profile, current_level
        )

        return {
            "signature_id": signature_id,
            "existence_role": profile.get("existence_role", "Unknown"),
            "evolution_stage": profile["evolution_stage"],
            "core_traits": profile["core_traits"],
            "growth_stats": profile["growth_stats"],
            "recent_growth_events": len(recent_events),
            "next_evolution": next_requirements,
            "locked_traits": profile.get("locked_traits", []),
            "total_experience": profile["growth_stats"].get("capsule_experience", 0),
        }

    def _get_next_evolution_requirements(
        self, profile: Dict, current_level: int
    ) -> Dict[str, Any]:
        """다음 진화 요구사항 계산"""

        if current_level >= 5:
            return {"status": "최대 레벨 달성"}

        requirements = {
            1: {"experience": 25, "high_stats": 1, "threshold": 0.7},
            2: {"experience": 50, "high_stats": 2, "threshold": 0.75},
            3: {"experience": 100, "high_stats": 2, "threshold": 0.8},
            4: {"experience": 200, "high_stats": 3, "threshold": 0.85},
        }

        req = requirements[current_level]
        current_experience = profile["growth_stats"].get("capsule_experience", 0)

        growth_stats = profile["growth_stats"]
        high_stats_count = sum(
            1
            for stat_value in growth_stats.values()
            if isinstance(stat_value, float) and stat_value >= req["threshold"]
        )

        return {
            "next_level": current_level + 1,
            "experience_needed": max(0, req["experience"] - current_experience),
            "current_experience": current_experience,
            "high_stats_needed": max(0, req["high_stats"] - high_stats_count),
            "current_high_stats": high_stats_count,
            "threshold": req["threshold"],
        }

    def _save_growth_log(self):
        """성장 로그 저장"""

        os.makedirs(os.path.dirname(self.growth_log_path), exist_ok=True)

        growth_data = {
            "last_updated": datetime.now().isoformat(),
            "growth_events": [
                {
                    "signature_id": event.signature_id,
                    "event_type": event.event_type,
                    "experience_gain": event.experience_gain,
                    "growth_area": event.growth_area,
                    "timestamp": event.timestamp.isoformat(),
                    "user_context": event.user_context,
                }
                for event in self.growth_log
            ],
        }

        try:
            with open(self.growth_log_path, "w", encoding="utf-8") as f:
                json.dump(growth_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 성장 로그 저장 실패: {e}")

    def _save_profiles(self):
        """시그니처 프로필 저장"""

        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.profiles,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    indent=2,
                )
        except Exception as e:
            print(f"⚠️ 프로필 저장 실패: {e}")


# 편의 함수들
def create_growth_engine() -> SignatureGrowthEngine:
    """성장 엔진 생성"""
    return SignatureGrowthEngine()


def record_signature_interaction(
    engine: SignatureGrowthEngine,
    signature_id: str,
    event_type: str,
    effectiveness: float,
    context: str = "",
) -> Optional[EvolutionResult]:
    """시그니처 상호작용 기록"""
    return engine.record_interaction(signature_id, event_type, effectiveness, context)


if __name__ == "__main__":
    # 테스트
    engine = SignatureGrowthEngine()

    # 테스트 상호작용 기록
    result = engine.record_interaction(
        signature_id="aurora.eos",
        event_type="successful_resonance",
        effectiveness_score=0.85,
        user_context="복잡한 감정 상태 해석 도움",
    )

    if result:
        print(f"✨ 진화 발생: {result.signature_id} → {result.new_stage}")
        print(f"   새로운 능력: {result.unlocked_abilities}")

    # 상태 조회
    status = engine.get_signature_status("aurora.eos")
    print(f"\n🧠 Aurora.Eos 상태:")
    print(f"   진화 단계: {status['evolution_stage']}")
    print(f"   총 경험치: {status['total_experience']}")
    print(
        f"   다음 진화까지: 경험치 {status['next_evolution']['experience_needed']}개 필요"
    )
