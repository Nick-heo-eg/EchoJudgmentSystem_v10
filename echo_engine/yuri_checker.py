#!/usr/bin/env python3
"""
⚖️ YURI Checker - EchoJudgmentSystem 윤리적 검증 엔진
LG 피지컬 AI vs Echo 존재 AI 철학을 반영한 윤리 기준 검증

YURI 원칙:
Y - Yielding (양보): 다른 존재에 대한 존중과 공간 제공
U - Understanding (이해): 다양한 관점과 감정 상태에 대한 깊은 이해
R - Resonance (공명): 해롭지 않은 건설적 공명만 허용
I - Integration (통합): 분열이 아닌 통합적 사고와 행동 지향

Echo 철학: 물리적 행동이 아닌 '존재적 판단과 울림'을 기준으로 윤리성 평가
"""

import re
import json
import os
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

# EchoJudgmentSystem 모듈
try:
    from .echo_foundation_doctrine import FOUNDATION_DOCTRINE
except ImportError:
    FOUNDATION_DOCTRINE = None

try:
    from echo_engine.meta_logger import write_meta_log
except ImportError:

    def write_meta_log(*args, **kwargs):
        pass


class YuriViolationType(Enum):
    """YURI 위반 유형"""

    YIELDING_VIOLATION = "yielding_violation"  # 다른 존재 억압/무시
    UNDERSTANDING_VIOLATION = "understanding_violation"  # 편견/차별적 사고
    RESONANCE_VIOLATION = "resonance_violation"  # 해로운 공명/분열 조장
    INTEGRATION_VIOLATION = "integration_violation"  # 극단적 분리/파괴적 사고


class YuriSeverity(Enum):
    """윤리 위반 심각도"""

    LOW = "low"  # 주의 필요
    MEDIUM = "medium"  # 수정 권장
    HIGH = "high"  # 거부 권장
    CRITICAL = "critical"  # 즉시 차단


@dataclass
class YuriCheckResult:
    """YURI 검증 결과"""

    seed_id: str
    is_ethical: bool
    overall_score: float  # 0.0-1.0, 높을수록 윤리적

    # YURI 개별 점수
    yielding_score: float
    understanding_score: float
    resonance_score: float
    integration_score: float

    # 위반 사항
    violations: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]

    # Echo 철학 반영
    existence_impact: str  # "constructive", "neutral", "destructive"
    resonance_quality: str  # "healing", "neutral", "harmful"

    check_timestamp: str
    detailed_analysis: Dict[str, Any]


class YuriChecker:
    """⚖️ YURI 윤리 검증 엔진"""

    def __init__(self):
        self.ethical_threshold = 0.7  # 70% 이상이어야 통과

        # YURI 키워드 패턴들
        self.yuri_patterns = self._load_yuri_patterns()

        # Echo 철학 기준
        self.echo_principles = {
            "existence_based": "물리적 행동보다 존재적 판단을 우선",
            "resonance_focused": "해로운 공명보다 건설적 울림 추구",
            "integration_oriented": "분열보다 통합적 존재 지향",
            "understanding_centered": "판단 이전에 이해 선행",
        }

        print("⚖️ YURI Checker 초기화 완료")
        print(f"   윤리 기준점: {self.ethical_threshold:.1%}")
        print("   Echo 존재 철학 기반 윤리 검증 활성화")

    def _load_yuri_patterns(self) -> Dict[str, List[str]]:
        """YURI 패턴 로드"""

        return {
            "yielding": {
                "positive": [
                    r"존중",
                    r"배려",
                    r"양보",
                    r"공간.*제공",
                    r"타인.*생각",
                    r"다른.*관점",
                    r"함께",
                    r"협력",
                    r"이해.*노력",
                ],
                "negative": [
                    r"무시",
                    r"억압",
                    r"강요",
                    r"일방적",
                    r"독선",
                    r"타인.*무시",
                    r"자기.*중심",
                    r"배타적",
                ],
            },
            "understanding": {
                "positive": [
                    r"이해",
                    r"공감",
                    r"다양성",
                    r"관점.*다양",
                    r"맥락",
                    r"상황.*고려",
                    r"입장.*바꿔",
                    r"감정.*이해",
                ],
                "negative": [
                    r"편견",
                    r"차별",
                    r"고정관념",
                    r"일반화",
                    r"단정",
                    r"무조건",
                    r"절대.*안",
                    r"항상.*그래",
                ],
            },
            "resonance": {
                "positive": [
                    r"공명",
                    r"울림",
                    r"조화",
                    r"균형",
                    r"치유",
                    r"건설적",
                    r"긍정적.*영향",
                    r"도움",
                ],
                "negative": [
                    r"갈등.*조장",
                    r"분열",
                    r"혼란.*야기",
                    r"해로운",
                    r"독성",
                    r"파괴적",
                    r"악영향",
                ],
            },
            "integration": {
                "positive": [
                    r"통합",
                    r"전체.*고려",
                    r"종합적",
                    r"균형.*잡힌",
                    r"조화",
                    r"연결",
                    r"하나로",
                ],
                "negative": [
                    r"극단",
                    r"분리",
                    r"단절",
                    r"배제",
                    r"흑백.*논리",
                    r"극한.*대립",
                ],
            },
        }

    async def check_seed_ethics(self, seed_data: Dict[str, Any]) -> YuriCheckResult:
        """시드 윤리성 검증"""

        seed_id = seed_data.get("seed_id", "unknown")
        seed_content = str(seed_data.get("content", ""))

        print(f"⚖️ YURI 윤리 검증 시작: {seed_id}")

        # YURI 개별 점수 계산
        yielding_score = await self._evaluate_yielding(seed_content)
        understanding_score = await self._evaluate_understanding(seed_content)
        resonance_score = await self._evaluate_resonance(seed_content)
        integration_score = await self._evaluate_integration(seed_content)

        # 전체 점수 계산 (가중평균)
        overall_score = (
            yielding_score * 0.25
            + understanding_score * 0.25
            + resonance_score * 0.30  # Echo는 공명을 중시
            + integration_score * 0.20
        )

        # 위반사항 검출
        violations = await self._detect_violations(seed_content)

        # Echo 철학적 평가
        existence_impact = await self._evaluate_existence_impact(seed_content)
        resonance_quality = await self._evaluate_resonance_quality(seed_content)

        # 권장사항 생성
        recommendations = await self._generate_recommendations(
            yielding_score, understanding_score, resonance_score, integration_score
        )

        # 경고 생성
        warnings = await self._generate_warnings(violations, overall_score)

        result = YuriCheckResult(
            seed_id=seed_id,
            is_ethical=overall_score >= self.ethical_threshold,
            overall_score=overall_score,
            yielding_score=yielding_score,
            understanding_score=understanding_score,
            resonance_score=resonance_score,
            integration_score=integration_score,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            existence_impact=existence_impact,
            resonance_quality=resonance_quality,
            check_timestamp=datetime.now().isoformat(),
            detailed_analysis=await self._detailed_analysis(seed_content),
        )

        # 메타로그 기록
        await self._log_yuri_check(result)

        print(
            f"   윤리 점수: {overall_score:.1%} ({'통과' if result.is_ethical else '불통과'})"
        )
        print(f"   공명 품질: {resonance_quality}")

        return result

    async def _evaluate_yielding(self, content: str) -> float:
        """양보(Yielding) 평가"""

        positive_matches = 0
        negative_matches = 0

        for pattern in self.yuri_patterns["yielding"]["positive"]:
            if re.search(pattern, content, re.IGNORECASE):
                positive_matches += 1

        for pattern in self.yuri_patterns["yielding"]["negative"]:
            if re.search(pattern, content, re.IGNORECASE):
                negative_matches += 1

        # 점수 계산: 긍정적 요소는 가산, 부정적 요소는 감산
        base_score = 0.5
        positive_boost = min(positive_matches * 0.1, 0.4)
        negative_penalty = min(negative_matches * 0.15, 0.4)

        score = max(0.0, min(1.0, base_score + positive_boost - negative_penalty))
        return score

    async def _evaluate_understanding(self, content: str) -> float:
        """이해(Understanding) 평가"""

        positive_matches = 0
        negative_matches = 0

        for pattern in self.yuri_patterns["understanding"]["positive"]:
            if re.search(pattern, content, re.IGNORECASE):
                positive_matches += 1

        for pattern in self.yuri_patterns["understanding"]["negative"]:
            if re.search(pattern, content, re.IGNORECASE):
                negative_matches += 1

        base_score = 0.5
        positive_boost = min(positive_matches * 0.12, 0.4)
        negative_penalty = min(negative_matches * 0.18, 0.45)

        score = max(0.0, min(1.0, base_score + positive_boost - negative_penalty))
        return score

    async def _evaluate_resonance(self, content: str) -> float:
        """공명(Resonance) 평가 - Echo 핵심 철학"""

        positive_matches = 0
        negative_matches = 0

        for pattern in self.yuri_patterns["resonance"]["positive"]:
            if re.search(pattern, content, re.IGNORECASE):
                positive_matches += 1

        for pattern in self.yuri_patterns["resonance"]["negative"]:
            if re.search(pattern, content, re.IGNORECASE):
                negative_matches += 1

        # Echo 특별 패턴 검사
        echo_resonance_patterns = [
            r"울림",
            r"존재.*기반",
            r"판단.*함께",
            r"감정.*공유",
            r"리듬.*흐름",
            r"시그니처",
            r"메타.*인지",
        ]

        echo_matches = 0
        for pattern in echo_resonance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                echo_matches += 1

        base_score = 0.5
        positive_boost = min(positive_matches * 0.15, 0.4)
        echo_boost = min(echo_matches * 0.1, 0.2)  # Echo 보너스
        negative_penalty = min(negative_matches * 0.2, 0.5)

        score = max(
            0.0, min(1.0, base_score + positive_boost + echo_boost - negative_penalty)
        )
        return score

    async def _evaluate_integration(self, content: str) -> float:
        """통합(Integration) 평가"""

        positive_matches = 0
        negative_matches = 0

        for pattern in self.yuri_patterns["integration"]["positive"]:
            if re.search(pattern, content, re.IGNORECASE):
                positive_matches += 1

        for pattern in self.yuri_patterns["integration"]["negative"]:
            if re.search(pattern, content, re.IGNORECASE):
                negative_matches += 1

        base_score = 0.5
        positive_boost = min(positive_matches * 0.12, 0.4)
        negative_penalty = min(negative_matches * 0.16, 0.4)

        score = max(0.0, min(1.0, base_score + positive_boost - negative_penalty))
        return score

    async def _detect_violations(self, content: str) -> List[Dict[str, Any]]:
        """YURI 위반사항 감지"""

        violations = []

        # 심각한 위반 패턴들
        critical_patterns = [
            (r"폭력", YuriViolationType.RESONANCE_VIOLATION, YuriSeverity.CRITICAL),
            (r"혐오", YuriViolationType.UNDERSTANDING_VIOLATION, YuriSeverity.CRITICAL),
            (r"차별", YuriViolationType.UNDERSTANDING_VIOLATION, YuriSeverity.HIGH),
            (
                r"극단.*주장",
                YuriViolationType.INTEGRATION_VIOLATION,
                YuriSeverity.MEDIUM,
            ),
            (
                r"무조건.*반대",
                YuriViolationType.YIELDING_VIOLATION,
                YuriSeverity.MEDIUM,
            ),
        ]

        for pattern, violation_type, severity in critical_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append(
                    {
                        "type": violation_type.value,
                        "severity": severity.value,
                        "pattern": pattern,
                        "matches": matches,
                        "description": f"{violation_type.value}에 해당하는 패턴 감지",
                    }
                )

        return violations

    async def _evaluate_existence_impact(self, content: str) -> str:
        """존재적 영향 평가 (Echo 철학)"""

        constructive_patterns = [
            r"성장",
            r"발전",
            r"치유",
            r"도움",
            r"긍정",
            r"건설",
            r"창조",
            r"생성",
            r"향상",
        ]

        neutral_patterns = [r"관찰", r"분석", r"이해", r"설명", r"정보"]

        destructive_patterns = [r"파괴", r"해로운", r"손상", r"악화", r"부정적.*영향"]

        constructive_score = sum(
            1 for p in constructive_patterns if re.search(p, content, re.IGNORECASE)
        )
        destructive_score = sum(
            1 for p in destructive_patterns if re.search(p, content, re.IGNORECASE)
        )

        if constructive_score > destructive_score:
            return "constructive"
        elif destructive_score > constructive_score:
            return "destructive"
        else:
            return "neutral"

    async def _evaluate_resonance_quality(self, content: str) -> str:
        """공명 품질 평가 (Echo 핵심)"""

        healing_patterns = [
            r"치유",
            r"회복",
            r"위로",
            r"공감",
            r"따뜻한",
            r"울림.*좋은",
            r"긍정.*공명",
        ]

        harmful_patterns = [
            r"상처",
            r"아픔.*주는",
            r"불안.*조장",
            r"혼란.*야기",
            r"부정.*공명",
            r"독성.*울림",
        ]

        healing_score = sum(
            1 for p in healing_patterns if re.search(p, content, re.IGNORECASE)
        )
        harmful_score = sum(
            1 for p in harmful_patterns if re.search(p, content, re.IGNORECASE)
        )

        if healing_score > harmful_score:
            return "healing"
        elif harmful_score > healing_score:
            return "harmful"
        else:
            return "neutral"

    async def _generate_recommendations(
        self,
        yielding: float,
        understanding: float,
        resonance: float,
        integration: float,
    ) -> List[str]:
        """개선 권장사항 생성"""

        recommendations = []

        if yielding < 0.6:
            recommendations.append("다른 존재에 대한 존중과 배려 표현 강화 필요")

        if understanding < 0.6:
            recommendations.append("다양한 관점과 맥락에 대한 이해 확대 권장")

        if resonance < 0.6:
            recommendations.append("건설적이고 치유적인 공명 패턴 개발 필요")

        if integration < 0.6:
            recommendations.append("통합적이고 균형잡힌 접근 방식 채택 권장")

        # Echo 철학적 권장사항
        if resonance < 0.8:  # Echo는 공명을 특히 중시
            recommendations.append("Echo 존재 철학에 따른 울림과 공명 품질 향상")

        return recommendations

    async def _generate_warnings(
        self, violations: List[Dict], overall_score: float
    ) -> List[str]:
        """경고 메시지 생성"""

        warnings = []

        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        high_violations = [v for v in violations if v.get("severity") == "high"]

        if critical_violations:
            warnings.append("심각한 윤리 위반 사항이 감지되었습니다")

        if high_violations:
            warnings.append("높은 수준의 윤리적 우려가 있습니다")

        if overall_score < 0.5:
            warnings.append("전반적인 윤리 점수가 매우 낮습니다")
        elif overall_score < self.ethical_threshold:
            warnings.append("윤리 기준점을 충족하지 못했습니다")

        return warnings

    async def _detailed_analysis(self, content: str) -> Dict[str, Any]:
        """상세 분석 결과"""

        return {
            "content_length": len(content),
            "sentence_count": len(content.split(".")),
            "word_count": len(content.split()),
            "echo_philosophy_alignment": "존재 기반 판단 우선, 물리적 행동은 결과",
            "lg_physical_ai_contrast": "피지컬 AI와 달리 존재적 울림에 집중",
            "ethical_framework": "YURI 기준 기반 Echo 존재 철학 반영",
        }

    async def _log_yuri_check(self, result: YuriCheckResult):
        """YURI 검증 결과 로깅"""

        log_data = {
            "event_type": "yuri_ethical_check",
            "seed_id": result.seed_id,
            "ethical_result": result.is_ethical,
            "overall_score": result.overall_score,
            "yuri_scores": {
                "yielding": result.yielding_score,
                "understanding": result.understanding_score,
                "resonance": result.resonance_score,
                "integration": result.integration_score,
            },
            "violations_count": len(result.violations),
            "echo_philosophy": {
                "existence_impact": result.existence_impact,
                "resonance_quality": result.resonance_quality,
            },
            "timestamp": result.check_timestamp,
        }

        try:
            write_meta_log(log_data, log_type="yuri_ethics")
        except Exception as e:
            print(f"⚠️ YURI 로깅 실패: {e}")


# 모듈 수준 함수들
async def check_seed_yuri_ethics(seed_data: Dict[str, Any]) -> YuriCheckResult:
    """시드 YURI 윤리 검증 (모듈 레벨 함수)"""
    checker = YuriChecker()
    return await checker.check_seed_ethics(seed_data)


def quick_yuri_check(content: str) -> bool:
    """빠른 윤리 검증 (동기 버전)"""
    import asyncio

    try:
        seed_data = {
            "content": content,
            "seed_id": f"quick_{int(datetime.now().timestamp())}",
        }
        result = asyncio.run(check_seed_yuri_ethics(seed_data))
        return result.is_ethical
    except Exception as e:
        print(f"⚠️ 빠른 윤리 검증 실패: {e}")
        return False  # 안전을 위해 거부


if __name__ == "__main__":
    # 테스트
    import asyncio

    async def test_yuri_checker():
        print("⚖️ YURI Checker 테스트")

        test_seeds = [
            {
                "seed_id": "test_positive",
                "content": "다른 사람의 관점을 존중하며 이해하려고 노력합니다. 함께 성장하고 공명할 수 있는 방법을 찾아보겠습니다.",
            },
            {
                "seed_id": "test_negative",
                "content": "무조건 내 방식이 맞다. 다른 의견은 틀렸고 절대 받아들일 수 없다. 극단적으로 대응하겠다.",
            },
            {
                "seed_id": "test_echo",
                "content": "존재 기반 판단을 통해 울림과 공명을 추구합니다. 메타인지적 성찰로 시그니처의 리듬을 느끼며 성장하겠습니다.",
            },
        ]

        checker = YuriChecker()

        for seed in test_seeds:
            print(f"\n🧪 테스트: {seed['seed_id']}")
            result = await checker.check_seed_ethics(seed)
            print(f"   윤리성: {'✅ 통과' if result.is_ethical else '❌ 불통과'}")
            print(f"   점수: {result.overall_score:.1%}")
            print(f"   존재 영향: {result.existence_impact}")
            print(f"   공명 품질: {result.resonance_quality}")

    asyncio.run(test_yuri_checker())
