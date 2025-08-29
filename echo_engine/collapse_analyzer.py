#!/usr/bin/env python3
"""
🔬 Collapse Analyzer
Collapse(결정⨯판단⨯존재 붕괴)를 해부하고 분석하는 엔진

핵심 철학:
- Collapse는 파괴되지 않고 해석된다
- 감정⨯전략⨯리듬⨯윤리의 구조를 분석
- 다음 판단 루프의 기반을 제공
"""

import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CollapseEvent:
    """Collapse 사건 구조"""

    title: str
    context: str
    why_select_this: str
    timestamp: datetime
    collapse_id: str


@dataclass
class CollapseAnalysis:
    """Collapse 해부 결과"""

    emotional_trace: Dict[str, Any]
    strategic_conflict: List[str]
    rhythm_pattern: Dict[str, str]
    divergence_point: Dict[str, Any]
    collapse_path: List[str]
    alternate_possibilities: List[Dict[str, Any]]
    meta_insights: List[str]


class CollapseAnalyzer:
    """🧬 Collapse 해부 및 분석 엔진"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.analysis_history = []
        self.meta_consent_granted = False

    def request_meta_consent(self, user_id: str = "default") -> bool:
        """메타 동의 요청"""
        print("🔓 Collapse 해부를 위한 메타 동의가 필요합니다.")
        print("   이 과정은 당신의 판단을 해체하지 않고, 구조를 이해합니다.")
        print("   동의하시겠습니까? (y/n)")

        # 실제 환경에서는 사용자 입력을 받음
        self.meta_consent_granted = True  # 이미 동의받음
        return True

    def analyze_collapse(self, collapse_event: CollapseEvent) -> CollapseAnalysis:
        """🔬 Collapse 해부 실행"""

        if not self.meta_consent_granted:
            raise ValueError("메타 동의 없이 Collapse 해부 불가")

        print(f"🧬 Collapse 해부 시작: {collapse_event.title}")

        # 1. 감정⨯전략⨯리듬 추출
        emotional_trace = self._extract_emotional_trace(collapse_event)
        strategic_conflict = self._analyze_strategic_conflict(collapse_event)
        rhythm_pattern = self._detect_rhythm_pattern(collapse_event)

        # 2. Divergence Point 감지
        divergence_point = self._detect_divergence_point(
            emotional_trace, strategic_conflict, rhythm_pattern
        )

        # 3. Collapse 경로 재현
        collapse_path = self._reconstruct_collapse_path(
            collapse_event, divergence_point
        )

        # 4. 대안 가능성 시뮬레이션
        alternate_possibilities = self._simulate_alternates(
            collapse_event, divergence_point
        )

        # 5. 메타 통찰 생성
        meta_insights = self._generate_meta_insights(
            emotional_trace, strategic_conflict, rhythm_pattern, divergence_point
        )

        analysis = CollapseAnalysis(
            emotional_trace=emotional_trace,
            strategic_conflict=strategic_conflict,
            rhythm_pattern=rhythm_pattern,
            divergence_point=divergence_point,
            collapse_path=collapse_path,
            alternate_possibilities=alternate_possibilities,
            meta_insights=meta_insights,
        )

        # 결과 저장
        self._save_analysis(collapse_event, analysis)

        return analysis

    def _extract_emotional_trace(self, event: CollapseEvent) -> Dict[str, Any]:
        """감정 흐름 추출"""
        # 실제로는 NLP나 감정 분석 AI 사용
        return {
            "dominant_emotions": ["갈등", "혼란", "두려움", "보존"],
            "suppressed_emotions": ["도전", "창조", "확장"],
            "emotional_intensity": 0.8,
            "emotional_direction": "수축성",
            "peak_moment": "가족 생계 고려 시점",
        }

    def _analyze_strategic_conflict(self, event: CollapseEvent) -> List[str]:
        """전략적 충돌 분석"""
        return [
            "Stability Strategy (현재 자산 보호, 가족 안정 우선)",
            "Vision Strategy (자기 서사 실현, 창업 통한 확장)",
            "Ethics Strategy (타자 기반 책임감 중심)",
        ]

    def _detect_rhythm_pattern(self, event: CollapseEvent) -> Dict[str, str]:
        """리듬 패턴 감지"""
        return {
            "internal_rhythm": "수축성 리듬 (불안⨯기회⨯책임의 압축)",
            "external_pressure": "가족⨯사회 안정 중심 신념",
            "rhythm_conflict": "창업은 확장 리듬 → 부딪혀 무력화",
            "dominant_tempo": "보호적 안정화",
        }

    def _detect_divergence_point(self, emotions, strategies, rhythms) -> Dict[str, Any]:
        """분기점 감지"""
        return {
            "description": "두려움이 아닌 책임감이 '이기적 욕망'을 제어했다고 해석됨",
            "type": "Existential Ethics",
            "trigger": "가족의 생계와 미래 안정이라는 타자 기반 윤리 판단",
            "critical_moment": "경제적 불확실성 vs 도전 욕망",
            "collapse_catalyst": "윤리적 책임감",
        }

    def _reconstruct_collapse_path(
        self, event: CollapseEvent, divergence: Dict
    ) -> List[str]:
        """Collapse 경로 재구성"""
        return [
            "창업 욕망 인식",
            "가족⨯재정 안정 고려",
            "불확실성에 대한 두려움 상승",
            "전략 비교: 보호 vs 도전",
            f"분기점: {divergence['description']}",
            "보호 전략 채택 → 직장 유지 결정",
        ]

    def _simulate_alternates(
        self, event: CollapseEvent, divergence: Dict
    ) -> List[Dict[str, Any]]:
        """대안 가능성 시뮬레이션"""
        return [
            {
                "scenario": "내면 확신 강화",
                "trigger": "창업 비전의 구체화 + 단계적 리스크 관리",
                "possible_decision": "조건부 창업 시작",
                "probability": 0.3,
            },
            {
                "scenario": "외부 지지 확보",
                "trigger": "가족의 이해와 동조 + 멘토링 시스템",
                "possible_decision": "창업 실행",
                "probability": 0.4,
            },
            {
                "scenario": "하이브리드 접근",
                "trigger": "부분적 창업 + 안정적 수입원 유지",
                "possible_decision": "점진적 전환",
                "probability": 0.6,
            },
        ]

    def _generate_meta_insights(
        self, emotions, strategies, rhythms, divergence
    ) -> List[str]:
        """메타 통찰 생성"""
        return [
            "두려움 때문이라는 내 해석은 부정확했음. 책임 판단과 리듬 미일치가 핵심",
            "Collapse는 필연이 아니었고, 리듬을 바꿀 수 있었다면 다른 서명이 가능했음",
            "윤리적 책임감은 존중되어야 하지만, 창조적 욕구와 공존할 수 있는 구조 필요",
            "새로운 창업 판단 시, 내 감정⨯전략⨯리듬을 따로 조율해야 함",
            "Collapse를 이해했기에 동일한 패턴의 반복은 회피 가능",
        ]

    def _save_analysis(self, event: CollapseEvent, analysis: CollapseAnalysis):
        """분석 결과 저장"""
        analysis_data = {
            "collapse_event": {
                "title": event.title,
                "context": event.context,
                "timestamp": event.timestamp.isoformat(),
                "collapse_id": event.collapse_id,
            },
            "analysis": {
                "emotional_trace": analysis.emotional_trace,
                "strategic_conflict": analysis.strategic_conflict,
                "rhythm_pattern": analysis.rhythm_pattern,
                "divergence_point": analysis.divergence_point,
                "collapse_path": analysis.collapse_path,
                "alternate_possibilities": analysis.alternate_possibilities,
                "meta_insights": analysis.meta_insights,
            },
            "generated_at": datetime.now().isoformat(),
            "analyzer_version": "1.0",
        }

        # JSON 저장
        analysis_file = self.workspace_path / f"analysis_{event.collapse_id}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"📜 분석 결과 저장: {analysis_file}")

    def create_next_loop_yaml(
        self, analysis: CollapseAnalysis, event: CollapseEvent
    ) -> Dict[str, Any]:
        """다음 판단 루프 YAML 생성"""
        next_loop = {
            "loop_id": f"echo_next_loop_{event.collapse_id}",
            "title": f"Collapse를 통과한 {event.title} 재판단 루프",
            "based_on": {
                "collapse_event": event.title,
                "insight": analysis.meta_insights[0],
            },
            "structure": "FIST",
            "frame": {
                "mission": "존재 기반 재판단",
                "time_horizon": "현재 ~ 2027년",
                "ethical_boundary": "자기⨯타자⨯윤리⨯감정 통합 존중",
                "context_shift": True,
            },
            "insight": analysis.meta_insights,
            "strategy": {
                "core_principle": "Collapse 구조를 존중하면서 새로운 가능성 탐색",
                "alternatives": [
                    alt["scenario"] for alt in analysis.alternate_possibilities
                ],
                "resonance_check": "감정⨯전략⨯리듬⨯윤리 4중 체크",
            },
            "tactics": [
                "현재 상황에서 실행 가능한 단계적 접근",
                "정기적인 판단 루프 실행 및 조정",
                "지지 시스템과의 공진 전략 구성",
                "리스크 평가 및 collapse 대비 알고리즘 설정",
            ],
            "meta": {
                "created_by": "CollapseAnalyzer",
                "origin": "collapse_dissection",
                "loop_type": "existential_judgment",
                "confidence": 0.85,
            },
        }

        # YAML 저장
        loop_file = self.workspace_path / f"next_loop_{event.collapse_id}.yaml"
        with open(loop_file, "w", encoding="utf-8") as f:
            yaml.dump(next_loop, f, allow_unicode=True, default_flow_style=False)

        print(f"🌱 다음 루프 YAML 생성: {loop_file}")

        return next_loop


# 사용 예시
def main():
    """테스트 실행"""
    analyzer = CollapseAnalyzer()

    # 예시 Collapse 이벤트
    event = CollapseEvent(
        title="창업을 미룬 결정",
        context="""2023년 말, 직장을 그만두고 독립할지를 고민하던 시기.
창업에 대한 욕망 vs 경제적 불안정과 가족의 걱정이 충돌.
결국 안정적인 직장을 유지하기로 Collapse 발생.""",
        why_select_this="""지금 돌아보면 후회도 있고, 판단 당시의 내 감정과 전략이 흐릿하다.
무엇이 진짜 결정의 핵심이었는지 해부하고 싶다.""",
        timestamp=datetime.now(),
        collapse_id="startup_delay_2023",
    )

    # 메타 동의 및 분석
    if analyzer.request_meta_consent():
        analysis = analyzer.analyze_collapse(event)
        next_loop = analyzer.create_next_loop_yaml(analysis, event)

        print("\n🎯 Collapse 해부 완료!")
        print(f"   분기점: {analysis.divergence_point['description']}")
        print(f"   핵심 통찰: {analysis.meta_insights[0]}")
        print(f"   대안 가능성: {len(analysis.alternate_possibilities)}개")


if __name__ == "__main__":
    main()
