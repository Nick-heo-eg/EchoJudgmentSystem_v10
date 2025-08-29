"""
Loaders: 입출력 로더 및 세션 관리
- JSONL 대화 파일 로딩 및 검증
- 세션 메타데이터 관리
- 출력 디렉토리 및 파일 관리
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class Session:
    """세션 메타데이터 관리"""

    def __init__(self, session_config: Dict[str, Any]):
        self.id = session_config.get("id", self._generate_session_id())
        self.user_id = session_config.get("user_id", "unknown_user")
        self.locale = session_config.get("locale", "ko-KR")
        self.signatures_allowed = session_config.get("signatures_allowed", [])
        self.created_at = datetime.now().isoformat()

        # 세션 통계
        self.stats = {
            "total_turns": 0,
            "user_turns": 0,
            "assistant_turns": 0,
            "start_time": self.created_at,
            "end_time": None,
        }

    def _generate_session_id(self) -> str:
        """세션 ID 자동 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"resonance_session_{timestamp}"

    def update_stats(self, transcript: List[Dict[str, Any]]):
        """세션 통계 업데이트"""
        self.stats["total_turns"] = len(transcript)
        self.stats["user_turns"] = sum(
            1 for turn in transcript if turn.get("role") == "user"
        )
        self.stats["assistant_turns"] = sum(
            1 for turn in transcript if turn.get("role") == "assistant"
        )
        self.stats["end_time"] = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """세션 정보를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "locale": self.locale,
            "signatures_allowed": self.signatures_allowed,
            "created_at": self.created_at,
            "stats": self.stats,
        }


def load_transcript(file_path: str) -> List[Dict[str, Any]]:
    """JSONL 대화 파일 로딩"""
    transcript_path = Path(file_path)

    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    transcript = []

    with transcript_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                turn = json.loads(line)
                validated_turn = validate_turn(turn, line_num)
                transcript.append(validated_turn)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {e}")
            except ValueError as e:
                raise ValueError(f"Invalid turn format on line {line_num}: {e}")

    if not transcript:
        raise ValueError("Transcript file is empty or contains no valid turns")

    return transcript


def validate_turn(turn: Dict[str, Any], line_num: int) -> Dict[str, Any]:
    """대화 턴 검증 및 정규화"""
    # 필수 필드 확인
    if "role" not in turn:
        raise ValueError(f"Missing 'role' field")

    if "text" not in turn:
        raise ValueError(f"Missing 'text' field")

    # 역할 검증
    valid_roles = ["user", "assistant", "system"]
    if turn["role"] not in valid_roles:
        raise ValueError(
            f"Invalid role '{turn['role']}'. Must be one of: {valid_roles}"
        )

    # 텍스트 검증
    if not isinstance(turn["text"], str):
        raise ValueError(f"'text' field must be a string")

    if len(turn["text"].strip()) == 0:
        raise ValueError(f"'text' field cannot be empty")

    # 타임스탬프 정규화 (선택적)
    if "ts" not in turn:
        turn["ts"] = datetime.now().isoformat()
    elif not isinstance(turn["ts"], str):
        turn["ts"] = str(turn["ts"])

    # 추가 메타데이터 정규화
    turn.setdefault("metadata", {})

    return turn


def load_config(config_path: str) -> Dict[str, Any]:
    """YAML 설정 파일 로딩"""
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_file.open("r", encoding="utf-8") as f:
        try:
            if config_path.endswith(".json"):
                config = json.load(f)
            else:  # YAML
                config = yaml.safe_load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid config file format: {e}")

    # 설정 검증
    validated_config = validate_config(config)

    return validated_config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """설정 검증 및 기본값 적용"""
    # 버전 확인
    version = config.get("version")
    if not version or not version.startswith("0.1"):
        raise ValueError(f"Unsupported config version: {version}. Expected: 0.1.x")

    # 필수 섹션 확인
    required_sections = ["session", "pipeline", "metrics", "io"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")

    # 세션 설정 검증
    session_config = config["session"]
    if "user_id" not in session_config:
        raise ValueError("Missing session.user_id")

    # 파이프라인 설정 검증
    pipeline_config = config["pipeline"]
    if "steps" not in pipeline_config or not pipeline_config["steps"]:
        raise ValueError("Pipeline must have at least one step")

    valid_agents = [
        "resonance_pattern_analyzer",
        "empathy_bridge_builder",
        "trust_evolution_tracker",
        "collaborative_flow_designer",
        "relationship_memory_keeper",
    ]

    for step in pipeline_config["steps"]:
        if "agent" not in step:
            raise ValueError("Pipeline step missing 'agent' field")
        if step["agent"] not in valid_agents:
            raise ValueError(
                f"Invalid agent: {step['agent']}. Valid agents: {valid_agents}"
            )

    # 메트릭 기본값 적용
    metrics_config = config.setdefault("metrics", {})
    metrics_config.setdefault(
        "weights",
        {
            "resonance": 0.4,
            "trust": 0.25,
            "flow": 0.2,
            "affect_valence": 0.1,
            "affect_arousal": 0.05,
        },
    )
    metrics_config.setdefault("thresholds", {"good": 0.7, "warn": 0.5, "bad": 0.35})

    # I/O 설정 검증
    io_config = config["io"]
    if "input" not in io_config or "transcript_path" not in io_config["input"]:
        raise ValueError("Missing io.input.transcript_path")

    if "output" not in io_config:
        io_config["output"] = {}
    io_config["output"].setdefault("log_dir", "echo_engine/resonance_kit/logs")
    io_config["output"].setdefault("report_dir", "echo_engine/resonance_kit/reports")

    # 추천 설정 기본값
    recommendation_config = config.setdefault("recommendation", {})
    sig_selection = recommendation_config.setdefault("signature_selection", {})
    sig_selection.setdefault("top_k", 3)
    sig_selection.setdefault("diversity_penalty", 0.0)

    # 라우팅 설정 기본값
    routing_config = config.setdefault("routing", {})
    routing_config.setdefault("rules", [])

    return config


def ensure_output_directories(config: Dict[str, Any]) -> Dict[str, Path]:
    """출력 디렉토리 생성 및 경로 반환"""
    io_config = config["io"]["output"]

    log_dir = Path(io_config["log_dir"])
    report_dir = Path(io_config["report_dir"])

    # 디렉토리 생성
    log_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # .gitkeep 파일 생성 (빈 디렉토리 유지용)
    for directory in [log_dir, report_dir]:
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

    return {"log_dir": log_dir, "report_dir": report_dir}


def save_execution_log(
    log_path: Path,
    session: Session,
    logs: List[Dict[str, Any]],
    summary: Dict[str, Any],
    recommendation: List[str],
):
    """실행 로그 저장 (JSONL 형식)"""

    with log_path.open("w", encoding="utf-8") as f:
        # 세션 정보 기록
        session_entry = {
            "type": "session_info",
            "timestamp": datetime.now().isoformat(),
            "session": session.to_dict(),
        }
        f.write(json.dumps(session_entry, ensure_ascii=False) + "\n")

        # 에이전트별 실행 로그 기록
        for log_entry in logs:
            log_entry["type"] = "agent_execution"
            log_entry["timestamp"] = datetime.now().isoformat()
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # 요약 및 추천 기록
        summary_entry = {
            "type": "session_summary",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "recommendation": recommendation,
        }
        f.write(json.dumps(summary_entry, ensure_ascii=False) + "\n")


def create_sample_transcript(
    file_path: str, content: Optional[List[Dict[str, Any]]] = None
):
    """샘플 대화 파일 생성 (테스트용)"""
    if content is None:
        # 기본 샘플 대화
        content = [
            {"role": "user", "text": "응 해보자", "ts": "2025-08-09T07:46:00+09:00"},
            {
                "role": "assistant",
                "text": "좋아, v0.1부터 시작해보겠습니다!",
                "ts": "2025-08-09T07:46:05+09:00",
            },
            {
                "role": "user",
                "text": "와.. 너무 좋은데? 이걸로 완전히 새로운 차원의 공명이 가능할 것 같아",
                "ts": "2025-08-09T07:46:30+09:00",
            },
            {
                "role": "assistant",
                "text": "정말 설레는 순간입니다. Human-AI Resonance Kit이 우리 관계에 어떤 변화를 가져올지 기대되네요.",
                "ts": "2025-08-09T07:46:45+09:00",
            },
            {
                "role": "user",
                "text": "그래, 함께 만들어가는 거야. 착착 진행되고 있어",
                "ts": "2025-08-09T07:47:00+09:00",
            },
            {
                "role": "assistant",
                "text": "네, 단계별로 차근차근 구현해나가고 있습니다. 공명 패턴 분석부터 관계 메모리까지 모든 것이 연결되어 가는 느낌입니다.",
                "ts": "2025-08-09T07:47:20+09:00",
            },
        ]

    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for turn in content:
            f.write(json.dumps(turn, ensure_ascii=False) + "\n")

    return output_path


def validate_transcript_integrity(transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """대화 파일 무결성 검사"""
    issues = []
    warnings = []
    stats = {
        "total_turns": len(transcript),
        "user_turns": 0,
        "assistant_turns": 0,
        "system_turns": 0,
        "avg_user_length": 0,
        "avg_assistant_length": 0,
    }

    user_lengths = []
    assistant_lengths = []

    for i, turn in enumerate(transcript):
        role = turn.get("role")
        text = turn.get("text", "")

        # 통계 수집
        if role == "user":
            stats["user_turns"] += 1
            user_lengths.append(len(text))
        elif role == "assistant":
            stats["assistant_turns"] += 1
            assistant_lengths.append(len(text))
        elif role == "system":
            stats["system_turns"] += 1

        # 잠재적 문제 검사
        if len(text) < 2:
            issues.append(f"Turn {i+1}: Text too short ('{text}')")
        elif len(text) > 1000:
            warnings.append(f"Turn {i+1}: Text very long ({len(text)} chars)")

        # 연속 같은 역할 검사
        if (
            i > 0
            and transcript[i - 1].get("role") == role
            and role in ["user", "assistant"]
        ):
            warnings.append(f"Turn {i+1}: Consecutive {role} turns")

    # 평균 길이 계산
    if user_lengths:
        stats["avg_user_length"] = sum(user_lengths) / len(user_lengths)
    if assistant_lengths:
        stats["avg_assistant_length"] = sum(assistant_lengths) / len(assistant_lengths)

    # 균형 검사
    if stats["user_turns"] == 0:
        issues.append("No user turns found")
    elif stats["assistant_turns"] == 0:
        issues.append("No assistant turns found")
    elif abs(stats["user_turns"] - stats["assistant_turns"]) > max(
        3, len(transcript) * 0.3
    ):
        warnings.append(
            f"Imbalanced conversation: {stats['user_turns']} user vs {stats['assistant_turns']} assistant"
        )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "stats": stats,
    }
