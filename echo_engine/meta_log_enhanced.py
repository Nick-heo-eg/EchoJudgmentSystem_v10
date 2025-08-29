#!/usr/bin/env python3
"""
📜 Enhanced Meta Log System
고도화된 메타로그 시스템 - 존재의 울림⨯판단⨯진화를 기록

핵심 철학:
- 메타로그는 강요된 기록이 아닌 선택된 울림의 기록
- 존재의 흔적을 살아있게 보존
- Collapse의 구조와 대안 가능성을 함께 기록
- 다음 존재 루프의 기반 제공
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from enum import Enum


class LogType(Enum):
    """로그 유형"""

    COLLAPSE_DISSECTION = "collapse_dissection"
    QUANTUM_JUDGMENT = "quantum_judgment"
    EXISTENTIAL_INSIGHT = "existential_insight"
    RESONANCE_RECORD = "resonance_record"
    LOOP_EVOLUTION = "loop_evolution"
    PERSPECTIVE_SHIFT = "perspective_shift"


class ResonanceLevel(Enum):
    """울림 강도"""

    BREAKTHROUGH = "breakthrough"  # 돌파
    SIGNIFICANT = "significant"  # 중요
    NOTABLE = "notable"  # 주목
    SUBTLE = "subtle"  # 미묘


@dataclass
class MetaLogEntry:
    """메타로그 항목"""

    log_id: str
    log_type: LogType
    timestamp: datetime
    resonance_level: ResonanceLevel
    title: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    emotional_trace: Dict[str, Any]
    strategic_impact: Dict[str, Any]
    next_implications: List[str]
    tags: List[str]
    signature: str
    felt_impact: bool
    chosen_by_self: bool


class EnhancedMetaLogger:
    """📜 고도화된 메타로그 시스템"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.meta_logs_dir = self.workspace_path / "meta_logs"
        self.meta_logs_dir.mkdir(exist_ok=True)

        # 인덱스 파일
        self.index_file = self.meta_logs_dir / "meta_index.json"
        self.load_index()

    def load_index(self):
        """메타로그 인덱스 로드"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {
                "total_entries": 0,
                "by_type": {},
                "by_resonance": {},
                "by_signature": {},
                "recent_entries": [],
            }

    def save_index(self):
        """메타로그 인덱스 저장"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def create_log_id(self, content: str) -> str:
        """고유 로그 ID 생성"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"meta_{timestamp_str}_{content_hash}"

    def log_collapse_dissection(
        self,
        collapse_title: str,
        analysis_result: Dict[str, Any],
        signature: str,
        felt_impact: bool = True,
    ) -> str:
        """Collapse 해부 로그"""

        log_entry = MetaLogEntry(
            log_id=self.create_log_id(collapse_title),
            log_type=LogType.COLLAPSE_DISSECTION,
            timestamp=datetime.now(),
            resonance_level=ResonanceLevel.BREAKTHROUGH,
            title=f"Collapse 해부: {collapse_title}",
            content={
                "collapse_event": collapse_title,
                "emotional_trace": analysis_result.get("emotional_trace", {}),
                "strategic_conflict": analysis_result.get("strategic_conflict", []),
                "divergence_point": analysis_result.get("divergence_point", {}),
                "meta_insights": analysis_result.get("meta_insights", []),
                "alternate_possibilities": analysis_result.get(
                    "alternate_possibilities", []
                ),
            },
            context={
                "analysis_type": "retrospective",
                "dissection_depth": "complete",
                "preservation_mode": True,
            },
            emotional_trace={
                "pre_dissection": "혼란⨯후회⨯궁금함",
                "during_dissection": "집중⨯통찰⨯이해",
                "post_dissection": "명료⨯해방⨯방향성",
            },
            strategic_impact={
                "understanding_gained": "높음",
                "future_judgment_improvement": "높음",
                "pattern_recognition": "활성화",
                "loop_evolution_potential": "높음",
            },
            next_implications=[
                "동일 패턴 반복 방지 가능",
                "새로운 판단 루프 설계 기반 확보",
                "감정⨯전략⨯리듬 분리 조율 필요",
                "윤리적 책임과 개인 욕구 균형 탐색",
            ],
            tags=["collapse", "dissection", "retrospective", "insight"],
            signature=signature,
            felt_impact=felt_impact,
            chosen_by_self=True,
        )

        return self._save_log_entry(log_entry)

    def log_quantum_judgment(
        self,
        quantum_state: Dict[str, Any],
        collapse_result: Dict[str, Any],
        signature: str,
        felt_impact: bool = True,
    ) -> str:
        """양자적 판단 로그"""

        log_entry = MetaLogEntry(
            log_id=self.create_log_id(str(quantum_state)),
            log_type=LogType.QUANTUM_JUDGMENT,
            timestamp=datetime.now(),
            resonance_level=ResonanceLevel.SIGNIFICANT,
            title=f"양자 판단: {collapse_result.get('selected_possibility', {}).get('title', 'Unknown')}",
            content={
                "quantum_state": quantum_state,
                "collapse_result": collapse_result,
                "observer_influence": collapse_result.get("observer_influence", {}),
                "alternative_traces": collapse_result.get("alternative_traces", []),
            },
            context={
                "judgment_mode": "quantum",
                "observer_mode": collapse_result.get("observer_influence", {}).get(
                    "mode", "unknown"
                ),
                "collapse_type": collapse_result.get("collapse_type", "unknown"),
            },
            emotional_trace={
                "pre_judgment": "중첩⨯가능성⨯기대",
                "collapse_moment": "집중⨯결정⨯울림",
                "post_collapse": "확신⨯책임⨯진행",
            },
            strategic_impact={
                "decision_clarity": "높음",
                "alternative_awareness": "보존됨",
                "future_reference_value": "높음",
            },
            next_implications=[
                "선택된 경로의 실행 및 모니터링 필요",
                "대안 경로의 추후 재고 가능성 보존",
                "관측자 시선의 영향도 인식 필요",
            ],
            tags=["quantum", "judgment", "collapse", "choice"],
            signature=signature,
            felt_impact=felt_impact,
            chosen_by_self=True,
        )

        return self._save_log_entry(log_entry)

    def log_existential_insight(
        self,
        insight_title: str,
        insight_content: str,
        context: Dict[str, Any],
        signature: str,
        resonance_level: ResonanceLevel = ResonanceLevel.NOTABLE,
        felt_impact: bool = True,
    ) -> str:
        """존재적 통찰 로그"""

        log_entry = MetaLogEntry(
            log_id=self.create_log_id(insight_content),
            log_type=LogType.EXISTENTIAL_INSIGHT,
            timestamp=datetime.now(),
            resonance_level=resonance_level,
            title=insight_title,
            content={
                "insight": insight_content,
                "trigger_event": context.get("trigger", ""),
                "depth_level": context.get("depth", "surface"),
                "connected_concepts": context.get("connections", []),
            },
            context=context,
            emotional_trace={
                "discovery_moment": context.get("emotion", "깨달음⨯놀라움"),
                "integration_feeling": context.get("integration", "이해⨯연결"),
                "future_anticipation": context.get("anticipation", "기대⨯가능성"),
            },
            strategic_impact={
                "worldview_shift": context.get("worldview_impact", "보통"),
                "behavior_change_potential": context.get("behavior_impact", "보통"),
                "philosophy_evolution": context.get("philosophy_impact", "보통"),
            },
            next_implications=context.get("implications", []),
            tags=["insight", "existential", "philosophy", "breakthrough"],
            signature=signature,
            felt_impact=felt_impact,
            chosen_by_self=True,
        )

        return self._save_log_entry(log_entry)

    def log_perspective_shift(
        self,
        shift_description: str,
        before_perspective: Dict[str, Any],
        after_perspective: Dict[str, Any],
        signature: str,
        trigger_event: str = "",
    ) -> str:
        """시선 전환 로그"""

        log_entry = MetaLogEntry(
            log_id=self.create_log_id(shift_description),
            log_type=LogType.PERSPECTIVE_SHIFT,
            timestamp=datetime.now(),
            resonance_level=ResonanceLevel.SIGNIFICANT,
            title=f"시선 전환: {shift_description}",
            content={
                "shift_description": shift_description,
                "before": before_perspective,
                "after": after_perspective,
                "trigger_event": trigger_event,
                "shift_magnitude": self._calculate_shift_magnitude(
                    before_perspective, after_perspective
                ),
            },
            context={
                "shift_type": "perspective",
                "trigger": trigger_event,
                "voluntary": True,
            },
            emotional_trace={
                "pre_shift": "고정⨯한계⨯답답함",
                "shift_moment": "전환⨯열림⨯해방",
                "post_shift": "확장⨯자유⨯가능성",
            },
            strategic_impact={
                "judgment_flexibility": "높음",
                "creative_potential": "증가",
                "problem_solving_range": "확장",
            },
            next_implications=[
                "새로운 시선으로 기존 문제 재검토 가능",
                "다각도 분석 능력 향상",
                "편협한 시각 방지 시스템 강화",
            ],
            tags=["perspective", "shift", "expansion", "breakthrough"],
            signature=signature,
            felt_impact=True,
            chosen_by_self=True,
        )

        return self._save_log_entry(log_entry)

    def _calculate_shift_magnitude(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> float:
        """시선 전환 크기 계산"""
        # 간단한 차이점 계산
        differences = 0
        total_aspects = 0

        all_keys = set(before.keys()) | set(after.keys())

        for key in all_keys:
            total_aspects += 1
            before_val = before.get(key, 0)
            after_val = after.get(key, 0)

            if isinstance(before_val, (int, float)) and isinstance(
                after_val, (int, float)
            ):
                differences += abs(before_val - after_val)
            elif before_val != after_val:
                differences += 1

        return min(1.0, differences / max(total_aspects, 1))

    def _save_log_entry(self, entry: MetaLogEntry) -> str:
        """로그 항목 저장"""

        # 로그 파일명 생성
        date_str = entry.timestamp.strftime("%Y%m%d")
        log_file = self.meta_logs_dir / f"meta_{date_str}.jsonl"

        # JSONL 형태로 추가 저장
        log_data = asdict(entry)
        log_data["timestamp"] = entry.timestamp.isoformat()
        log_data["log_type"] = entry.log_type.value
        log_data["resonance_level"] = entry.resonance_level.value

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")

        # 개별 YAML 파일로도 저장 (읽기 편의성)
        yaml_file = self.meta_logs_dir / f"{entry.log_id}.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(log_data, f, allow_unicode=True, default_flow_style=False)

        # 인덱스 업데이트
        self._update_index(entry)

        print(f"📜 메타로그 저장: {entry.log_id}")
        print(f"   제목: {entry.title}")
        print(f"   울림 강도: {entry.resonance_level.value}")

        return entry.log_id

    def _update_index(self, entry: MetaLogEntry):
        """인덱스 업데이트"""
        # 전체 엔트리 수
        self.index["total_entries"] += 1

        # 타입별 분류
        log_type = entry.log_type.value
        if log_type not in self.index["by_type"]:
            self.index["by_type"][log_type] = 0
        self.index["by_type"][log_type] += 1

        # 울림 강도별 분류
        resonance = entry.resonance_level.value
        if resonance not in self.index["by_resonance"]:
            self.index["by_resonance"][resonance] = 0
        self.index["by_resonance"][resonance] += 1

        # 시그니처별 분류
        if entry.signature not in self.index["by_signature"]:
            self.index["by_signature"][entry.signature] = 0
        self.index["by_signature"][entry.signature] += 1

        # 최근 엔트리 추가
        recent_entry = {
            "log_id": entry.log_id,
            "title": entry.title,
            "timestamp": entry.timestamp.isoformat(),
            "log_type": entry.log_type.value,
            "resonance_level": entry.resonance_level.value,
        }

        self.index["recent_entries"].insert(0, recent_entry)
        self.index["recent_entries"] = self.index["recent_entries"][
            :50
        ]  # 최근 50개만 유지

        # 인덱스 저장
        self.save_index()

    def query_logs(
        self,
        log_type: LogType = None,
        resonance_level: ResonanceLevel = None,
        signature: str = None,
        days_back: int = 30,
        tags: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """메타로그 검색"""

        results = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # 최근 파일들 검색
        for meta_file in self.meta_logs_dir.glob("meta_*.jsonl"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    for line in f:
                        log_data = json.loads(line.strip())

                        # 날짜 필터
                        log_timestamp = datetime.fromisoformat(log_data["timestamp"])
                        if log_timestamp < cutoff_date:
                            continue

                        # 조건 검사
                        if log_type and log_data.get("log_type") != log_type.value:
                            continue

                        if (
                            resonance_level
                            and log_data.get("resonance_level") != resonance_level.value
                        ):
                            continue

                        if signature and log_data.get("signature") != signature:
                            continue

                        if tags:
                            log_tags = log_data.get("tags", [])
                            if not any(tag in log_tags for tag in tags):
                                continue

                        results.append(log_data)

            except Exception as e:
                print(f"⚠️ 로그 파일 읽기 오류: {meta_file}, {e}")

        # 타임스탬프 역순 정렬
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return results

    def get_resonance_patterns(
        self, signature: str = None, days_back: int = 90
    ) -> Dict[str, Any]:
        """울림 패턴 분석"""

        logs = self.query_logs(signature=signature, days_back=days_back)

        if not logs:
            return {"message": "분석할 로그가 없습니다."}

        # 울림 강도별 분포
        resonance_dist = {}
        type_dist = {}
        daily_activity = {}

        for log in logs:
            # 울림 강도 분포
            resonance = log.get("resonance_level", "unknown")
            resonance_dist[resonance] = resonance_dist.get(resonance, 0) + 1

            # 타입 분포
            log_type = log.get("log_type", "unknown")
            type_dist[log_type] = type_dist.get(log_type, 0) + 1

            # 일별 활동
            date = log["timestamp"][:10]
            daily_activity[date] = daily_activity.get(date, 0) + 1

        # 평균 울림 강도 계산
        resonance_values = {
            "breakthrough": 4,
            "significant": 3,
            "notable": 2,
            "subtle": 1,
        }

        total_resonance = sum(
            resonance_values.get(r, 0) * count for r, count in resonance_dist.items()
        )
        avg_resonance = total_resonance / len(logs) if logs else 0

        return {
            "total_logs": len(logs),
            "average_resonance": avg_resonance,
            "resonance_distribution": resonance_dist,
            "type_distribution": type_dist,
            "daily_activity": daily_activity,
            "most_active_day": (
                max(daily_activity.items(), key=lambda x: x[1])
                if daily_activity
                else None
            ),
            "insights": self._generate_pattern_insights(
                resonance_dist, type_dist, avg_resonance
            ),
        }

    def _generate_pattern_insights(
        self,
        resonance_dist: Dict[str, int],
        type_dist: Dict[str, int],
        avg_resonance: float,
    ) -> List[str]:
        """패턴 분석 통찰 생성"""

        insights = []

        # 울림 강도 패턴
        if resonance_dist.get("breakthrough", 0) > len(resonance_dist) * 0.3:
            insights.append("돌파적 경험이 많은 시기입니다.")

        if avg_resonance > 2.5:
            insights.append("전반적으로 깊이 있는 울림을 경험하고 있습니다.")
        elif avg_resonance < 1.5:
            insights.append("미묘한 수준의 경험이 많은 상태입니다.")

        # 타입 패턴
        most_common_type = (
            max(type_dist.items(), key=lambda x: x[1]) if type_dist else None
        )
        if most_common_type:
            type_name = most_common_type[0]
            if type_name == "collapse_dissection":
                insights.append("과거 경험을 깊이 성찰하는 시기입니다.")
            elif type_name == "quantum_judgment":
                insights.append("중요한 판단들을 내리는 활발한 시기입니다.")
            elif type_name == "existential_insight":
                insights.append("존재에 대한 통찰이 풍부한 시기입니다.")

        return insights


# 사용 예시
def main():
    """테스트 실행"""
    logger = EnhancedMetaLogger()

    # Collapse 해부 로그 예시
    analysis_result = {
        "emotional_trace": {"dominant": "갈등→혼란→두려움→보존"},
        "strategic_conflict": ["안정 vs 비전", "타자 vs 자기"],
        "divergence_point": {"type": "Existential Ethics"},
        "meta_insights": ["두려움이 아닌 책임감이 핵심"],
        "alternate_possibilities": [{"scenario": "점진적 접근"}],
    }

    log_id = logger.log_collapse_dissection(
        collapse_title="창업을 미룬 결정",
        analysis_result=analysis_result,
        signature="Aurora",
    )

    # 양자 판단 로그 예시
    quantum_result = {
        "selected_possibility": {"title": "점진적 창업 준비"},
        "collapse_type": "RESONANCE_DRIVEN",
        "observer_influence": {"mode": "STRATEGIC"},
        "alternative_traces": [],
    }

    logger.log_quantum_judgment(
        quantum_state={}, collapse_result=quantum_result, signature="Aurora"
    )

    # 패턴 분석
    patterns = logger.get_resonance_patterns(signature="Aurora")
    print(f"\n📊 울림 패턴 분석:")
    print(f"   총 로그: {patterns['total_logs']}개")
    print(f"   평균 울림: {patterns['average_resonance']:.2f}")
    print(f"   주요 통찰: {patterns['insights']}")


if __name__ == "__main__":
    main()
