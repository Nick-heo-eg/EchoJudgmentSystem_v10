"""
Asset Value Judger - Data Schemas
=================================

자산 분석 결과의 데이터 구조 정의
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AssetStatus(str, Enum):
    """자산 상태 분류 - 실용적 관점"""

    ACTIVE = "active"  # 현재 활발히 사용중
    SLEEPING_VALUABLE = "sleeping_valuable"  # 미활용이지만 가치있음 (재활성화 권장)
    DORMANT = "dormant"  # 활용되지 않음 (검토 필요)
    DEPRECATED = "deprecated"  # 폐기 예정/정리 대상


@dataclass
class AssetMetrics:
    """파일별 수집된 메트릭"""

    # 기본 메타데이터
    loc: int  # Lines of Code
    complexity: int  # Cyclomatic Complexity
    deps_in: int  # 이 파일을 import하는 수
    deps_out: int  # 이 파일이 import하는 수
    last_modified_days: int  # 마지막 수정 후 경과 일수

    # 동적 분석
    covered: bool  # 테스트 커버리지 여부
    bridge_called: bool  # 브릿지에서 호출되는지 여부

    # Echo 시그니처 연계성
    has_signature_link: bool  # 시그니처 시스템과 연결
    has_judgment_link: bool  # 판단 엔진과 연결

    # 전략적 가치
    roadmap_matched: bool  # 로드맵 키워드 매칭
    roadmap_priority: str  # 매칭된 기능의 우선순위

    # 기술적 특성
    unique_patterns: int  # 고유한 패턴/알고리즘 수
    unused_functions: int  # 사용되지 않는 함수 수

    # 활용도 메트릭 (새로 추가)
    import_frequency: int = 0  # 다른 파일에서 import되는 빈도
    execution_frequency: int = 0  # 실제 실행되는 빈도
    recent_commits: int = 0  # 최근 3개월 커밋 수

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "loc": self.loc,
            "complexity": self.complexity,
            "deps_in": self.deps_in,
            "deps_out": self.deps_out,
            "last_modified_days": self.last_modified_days,
            "covered": self.covered,
            "bridge_called": self.bridge_called,
            "has_signature_link": self.has_signature_link,
            "has_judgment_link": self.has_judgment_link,
            "roadmap_matched": self.roadmap_matched,
            "roadmap_priority": self.roadmap_priority,
            "unique_patterns": self.unique_patterns,
            "unused_functions": self.unused_functions,
            "import_frequency": self.import_frequency,
            "execution_frequency": self.execution_frequency,
            "recent_commits": self.recent_commits,
        }


@dataclass
class AssetDecision:
    """자산 분류 결정"""

    status: AssetStatus  # dormant/pending/junk
    reason: str  # 분류 이유
    actions: List[str]  # 권장 액션

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "status": self.status.value,
            "reason": self.reason,
            "actions": self.actions,
        }


@dataclass
class AssetScores:
    """T/S/P 점수"""

    t_score: float  # Technical Value (0-100)
    s_score: float  # Strategic Value (0-100)
    p_score: float  # Potential Value (0-100)
    total: float  # 가중 평균 점수

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "t_score": round(self.t_score, 2),
            "s_score": round(self.s_score, 2),
            "p_score": round(self.p_score, 2),
            "total": round(self.total, 2),
        }


@dataclass
class AssetReport:
    """단일 파일의 완전한 분석 결과"""

    path: str  # 파일 경로
    owner: str  # 파일 소유자/팀
    metrics: AssetMetrics  # 수집된 메트릭
    scores: Dict[str, float]  # T/S/P 점수
    decision: AssetDecision  # 분류 결정
    timestamp: str  # 분석 시각

    def dict(self) -> Dict[str, Any]:
        """완전한 딕셔너리 변환 (JSON 직렬화용)"""
        return {
            "path": self.path,
            "owner": self.owner,
            "metrics": self.metrics.to_dict(),
            "scores": self.scores,
            "decision": self.decision.to_dict(),
            "timestamp": self.timestamp,
        }


@dataclass
class BatchAnalysisResult:
    """전체 분석 결과 요약"""

    total_files: int
    dormant_count: int
    pending_count: int
    junk_count: int
    top_dormant: List[AssetReport]
    junk_candidates: List[AssetReport]
    analysis_timestamp: str

    def summary_dict(self) -> Dict[str, Any]:
        """요약 딕셔너리"""
        return {
            "summary": {
                "total_files": self.total_files,
                "dormant_count": self.dormant_count,
                "pending_count": self.pending_count,
                "junk_count": self.junk_count,
            },
            "top_dormant": [asset.dict() for asset in self.top_dormant],
            "junk_candidates": [asset.dict() for asset in self.junk_candidates],
            "analysis_timestamp": self.analysis_timestamp,
        }


# 설정 스키마
@dataclass
class WeightsConfig:
    """가중치 설정"""

    total_weights: Dict[str, float]  # T/S/P 총합 가중치
    thresholds: Dict[str, float]  # dormant/pending 임계값
    t_weights: Dict[str, float]  # T 세부 가중치
    s_weights: Dict[str, float]  # S 세부 가중치
    p_weights: Dict[str, float]  # P 세부 가중치


@dataclass
class RegistryConfig:
    """자산 레지스트리 설정"""

    protected_patterns: List[str]  # 보호할 파일 패턴
    force_dormant: List[str]  # 강제 dormant 지정
    force_junk: List[str]  # 강제 junk 지정 (위험!)
    owners: Dict[str, str]  # 파일패턴 → 소유자 매핑


@dataclass
class RoadmapFeature:
    """로드맵 기능 정의"""

    name: str
    keywords: List[str]
    priority: str  # high/medium/low
    eta: str  # 예상 완료 시기
    description: Optional[str] = None


@dataclass
class RoadmapConfig:
    """로드맵 설정"""

    features: List[RoadmapFeature]


# 검증 함수들
def validate_asset_report(report_data: Dict[str, Any]) -> bool:
    """AssetReport 데이터 유효성 검증"""
    required_fields = ["path", "owner", "metrics", "scores", "decision", "timestamp"]

    if not all(field in report_data for field in required_fields):
        return False

    # 점수 범위 검증 (0-100)
    scores = report_data.get("scores", {})
    for score_name in ["t_score", "s_score", "p_score", "total"]:
        if score_name not in scores:
            return False
        score = scores[score_name]
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            return False

    # 상태 값 검증
    decision = report_data.get("decision", {})
    if decision.get("status") not in [status.value for status in AssetStatus]:
        return False

    return True


def create_asset_report_schema() -> Dict[str, Any]:
    """JSON Schema for AssetReport validation"""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["path", "owner", "metrics", "scores", "decision", "timestamp"],
        "properties": {
            "path": {"type": "string"},
            "owner": {"type": "string"},
            "metrics": {
                "type": "object",
                "required": ["loc", "complexity", "deps_in", "deps_out"],
                "properties": {
                    "loc": {"type": "integer", "minimum": 0},
                    "complexity": {"type": "integer", "minimum": 0},
                    "deps_in": {"type": "integer", "minimum": 0},
                    "deps_out": {"type": "integer", "minimum": 0},
                    "last_modified_days": {"type": "integer", "minimum": 0},
                    "covered": {"type": "boolean"},
                    "bridge_called": {"type": "boolean"},
                    "has_signature_link": {"type": "boolean"},
                    "has_judgment_link": {"type": "boolean"},
                    "roadmap_matched": {"type": "boolean"},
                    "roadmap_priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "unique_patterns": {"type": "integer", "minimum": 0},
                    "unused_functions": {"type": "integer", "minimum": 0},
                },
            },
            "scores": {
                "type": "object",
                "required": ["t_score", "s_score", "p_score", "total"],
                "properties": {
                    "t_score": {"type": "number", "minimum": 0, "maximum": 100},
                    "s_score": {"type": "number", "minimum": 0, "maximum": 100},
                    "p_score": {"type": "number", "minimum": 0, "maximum": 100},
                    "total": {"type": "number", "minimum": 0, "maximum": 100},
                },
            },
            "decision": {
                "type": "object",
                "required": ["status", "reason", "actions"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["dormant", "pending", "junk"],
                    },
                    "reason": {"type": "string"},
                    "actions": {"type": "array", "items": {"type": "string"}},
                },
            },
            "timestamp": {"type": "string", "format": "date-time"},
        },
    }
