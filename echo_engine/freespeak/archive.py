#!/usr/bin/env python3
"""
🌌 Free-Speak Archive System
존재적 발화의 완전한 기록과 재현을 위한 아카이빙 시스템

- JSONL (머신 리더블) + .log (원본 화면) 동시 저장
- 실시간 스트리밍 중 무음 백그라운드 저장
- 메타데이터: 플래그, 페르소나 비율, 모델명 등 완전 기록
- 리플레이 지원을 위한 타이밍 정보 포함

@owner: echo
@expose
@maturity: production
"""

from __future__ import annotations
import os
import sys
import json
import time
import uuid
import pathlib
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

DEFAULT_DIR = os.getenv("ECHO_FREESPEAK_DIR", "logs/freespeak_sessions")


def _now_ts() -> str:
    """현재 시간을 파일명 친화적 형태로 반환"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: str | pathlib.Path) -> pathlib.Path:
    """디렉토리 확실히 생성"""
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


class FreeSpeakArchiver:
    """
    🎯 Free-Speak 세션 아카이버

    ▶ 이중 기록 방식:
    - session.jsonl: 머신 리더블 (리플레이/분석용)
    - session.log: 원본 화면 텍스트 (인간 리더블)

    ▶ 세션 ID 형식: "fs_<timestamp>_<8charuuid>"

    ▶ 이벤트 타입:
    - meta: 세션 메타데이터 (플래그, 모델, 페르소나 등)
    - user: 사용자 입력
    - delta: 어시스턴트 출력 조각 (스트리밍)
    - done: 세션 완료
    - error: 오류 발생
    """

    def __init__(self, base_dir: str = DEFAULT_DIR, session_id: Optional[str] = None):
        self.base = ensure_dir(base_dir)
        self.session_id = session_id or f"fs_{_now_ts()}_{uuid.uuid4().hex[:8]}"
        self.dir = ensure_dir(self.base / self.session_id)

        # 이중 파일 오픈 (JSONL + RAW LOG)
        self.jsonl = open(
            self.dir / "session.jsonl", "a", encoding="utf-8", errors="replace"
        )
        self.raw = open(
            self.dir / "session.log", "a", encoding="utf-8", errors="replace"
        )
        self._opened = True

        # 세션 시작 로그
        self.raw.write(f"🌌 Free-Speak Session: {self.session_id}\n")
        self.raw.write(f"Started at: {datetime.now().isoformat()}\n")
        self.raw.write("=" * 60 + "\n")
        self.raw.flush()

    def close(self):
        """리소스 정리"""
        if self._opened:
            try:
                self.jsonl.close()
            finally:
                try:
                    self.raw.write("\n" + "=" * 60)
                    self.raw.write(
                        f"\nSession ended at: {datetime.now().isoformat()}\n"
                    )
                    self.raw.close()
                finally:
                    self._opened = False

    def _write_jsonl(self, obj: Dict[str, Any]):
        """JSONL 이벤트 기록 (타임스탬프 자동 추가)"""
        obj["t"] = time.time()
        obj["session_id"] = self.session_id
        self.jsonl.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.jsonl.flush()

    def write_meta(self, meta: Dict[str, Any]):
        """세션 메타데이터 기록"""
        self._write_jsonl({"type": "meta", "meta": meta})

        # Raw log에도 메타 정보 기록
        self.raw.write(f"📋 Session Meta:\n")
        for key, value in meta.items():
            self.raw.write(f"  {key}: {json.dumps(value, ensure_ascii=False)}\n")
        self.raw.write("-" * 40 + "\n")
        self.raw.flush()

    def write_user(self, text: str):
        """사용자 입력 기록"""
        self._write_jsonl({"type": "user", "text": text})
        self.raw.write(f"\n💬 User: {text}\n")
        self.raw.write("🌌 Echo: ")
        self.raw.flush()

    def write_delta(self, delta: str):
        """스트리밍 조각 기록 (어시스턴트 출력)"""
        self._write_jsonl({"type": "delta", "text": delta})
        self.raw.write(delta)
        self.raw.flush()

    def write_done(self, usage: Optional[Dict[str, Any]] = None):
        """세션 완료 기록"""
        self._write_jsonl({"type": "done", "usage": usage or {}})
        self.raw.write("\n✅ [Response Complete]\n")
        if usage:
            self.raw.write(f"📊 Usage: {json.dumps(usage, ensure_ascii=False)}\n")
        self.raw.flush()

    def write_error(self, msg: str):
        """오류 기록"""
        self._write_jsonl({"type": "error", "msg": msg})
        self.raw.write(f"\n❌ [ERROR] {msg}\n")
        self.raw.flush()

    def write_persona_info(
        self, persona_mix_name: str, blend_ratio: str, traits: Dict[str, float]
    ):
        """페르소나 믹스 정보 기록"""
        persona_data = {
            "mix_name": persona_mix_name,
            "blend_ratio": blend_ratio,
            "traits": traits,
        }
        self._write_jsonl({"type": "persona", "data": persona_data})

        self.raw.write(f"\n🎭 Persona Mix: {persona_mix_name} ({blend_ratio})\n")
        trait_str = " | ".join([f"{k}:{v:.1f}" for k, v in traits.items()])
        self.raw.write(f"💫 Traits: {trait_str}\n")
        self.raw.flush()

    # 컨텍스트 매니저 지원
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def find_sessions(base_dir: str = DEFAULT_DIR) -> Iterable[str]:
    """Free-Speak 세션 목록 조회"""
    p = pathlib.Path(base_dir)
    if not p.exists():
        return []

    sessions = []
    for d in sorted(p.iterdir(), key=lambda x: x.name, reverse=True):  # 최신순
        if d.is_dir() and d.name.startswith("fs_"):
            sessions.append(d.name)

    return sessions


def get_session_meta(
    session_id: str, base_dir: str = DEFAULT_DIR
) -> Optional[Dict[str, Any]]:
    """세션 메타데이터 추출"""
    session_path = pathlib.Path(base_dir) / session_id / "session.jsonl"
    if not session_path.exists():
        return None

    try:
        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                if event.get("type") == "meta":
                    return event.get("meta", {})
    except (json.JSONDecodeError, IOError):
        return None

    return {}


def list_recent_sessions(
    limit: int = 10, base_dir: str = DEFAULT_DIR
) -> List[Dict[str, Any]]:
    """최근 세션 목록 (메타데이터 포함)"""
    sessions = []
    for session_id in list(find_sessions(base_dir))[:limit]:
        meta = get_session_meta(session_id, base_dir) or {}

        # 세션 시작 시간 파싱
        try:
            time_part = session_id.split("_")[1] + "_" + session_id.split("_")[2]
            start_time = datetime.strptime(time_part, "%Y%m%d_%H%M%S")
        except:
            start_time = None

        sessions.append(
            {
                "session_id": session_id,
                "start_time": start_time.isoformat() if start_time else "unknown",
                "meta": meta,
            }
        )

    return sessions


if __name__ == "__main__":
    # 테스트 및 CLI 기능
    import argparse

    parser = argparse.ArgumentParser(description="Free-Speak Archive System")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--meta", help="Show metadata for session")
    parser.add_argument("--test", action="store_true", help="Run test archive")

    args = parser.parse_args()

    if args.list:
        print("🌌 Recent Free-Speak Sessions:")
        print("=" * 50)
        for session in list_recent_sessions():
            print(f"📁 {session['session_id']}")
            print(f"   ⏰ {session['start_time']}")
            if session["meta"]:
                flags = session["meta"].get("flags", {})
                mode_flags = [k for k, v in flags.items() if v]
                if mode_flags:
                    print(f"   🚀 {', '.join(mode_flags)}")
            print()

    elif args.meta:
        meta = get_session_meta(args.meta)
        if meta:
            print(f"📋 Session Meta: {args.meta}")
            print(json.dumps(meta, indent=2, ensure_ascii=False))
        else:
            print(f"❌ No metadata found for session: {args.meta}")

    elif args.test:
        print("🧪 Testing Free-Speak Archive System...")

        with FreeSpeakArchiver() as arc:
            print(f"🌌 Test session: {arc.session_id}")

            # 테스트 메타데이터
            arc.write_meta(
                {
                    "flags": {"free_speak": True, "dynamic_persona": True},
                    "model": "gpt-4-test",
                    "personas": {"Aurora": 0.7, "Companion": 0.3},
                    "mode": "test",
                }
            )

            # 테스트 대화
            arc.write_user("테스트 메시지입니다")
            arc.write_delta("안녕하세요! ")
            arc.write_delta("테스트 응답입니다.")
            arc.write_done({"tokens": 42})

        print("✅ Test completed!")

    else:
        parser.print_help()
