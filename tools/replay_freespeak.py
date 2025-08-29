#!/usr/bin/env python3
"""
🌌 Free-Speak Replay System
존재적 발화의 완전한 재현을 위한 리플레이 시스템

- 실제 타이밍 기반 터미널 재생
- 배속 조정 (0.5x ~ 5.0x)
- 메타데이터만 확인 모드
- 인터랙티브 제어 (일시정지/재생)

@owner: echo
@expose
@maturity: production
"""

from __future__ import annotations
import argparse
import json
import pathlib
import sys
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

BASE = os.getenv("ECHO_FREESPEAK_DIR", "logs/freespeak_sessions")


def load_session_events(session: str) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """세션 이벤트와 메타데이터 로드"""
    session_dir = pathlib.Path(BASE) / session
    jsonl_path = session_dir / "session.jsonl"

    if not jsonl_path.exists():
        raise FileNotFoundError(f"Session not found: {session}")

    events = []
    meta = {}

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                events.append(event)

                # 첫 번째 meta 이벤트 추출
                if event.get("type") == "meta" and not meta:
                    meta = event.get("meta", {})
            except json.JSONDecodeError:
                continue  # 손상된 줄 건너뛰기

    return events, meta


def format_meta_info(meta: Dict[str, Any]) -> str:
    """메타데이터 포매팅"""
    if not meta:
        return "No metadata available"

    lines = []

    # 플래그 정보
    flags = meta.get("flags", {})
    active_flags = [k for k, v in flags.items() if v]
    if active_flags:
        lines.append(f"🚀 Active flags: {', '.join(active_flags)}")

    # 모델 정보
    model = meta.get("model", "unknown")
    lines.append(f"🤖 Model: {model}")

    # 페르소나 정보
    personas = meta.get("personas", {})
    if personas:
        persona_str = " + ".join([f"{k}({v})" for k, v in personas.items()])
        lines.append(f"🎭 Personas: {persona_str}")

    # 모드 정보
    mode = meta.get("mode", "unknown")
    lines.append(f"🌌 Mode: {mode}")

    return "\n".join(lines)


def replay_session(
    session: str, speed: float = 1.0, meta_only: bool = False, interactive: bool = False
) -> int:
    """세션 리플레이 실행"""

    try:
        events, meta = load_session_events(session)
    except FileNotFoundError:
        print(f"❌ Session not found: {session}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error loading session: {e}", file=sys.stderr)
        return 1

    # 헤더 출력
    print("🌌 Free-Speak Replay")
    print("=" * 50)
    print(f"📁 Session: {session}")

    # 세션 시간 정보
    if events:
        start_time = events[0].get("t", 0)
        end_time = events[-1].get("t", 0)
        duration = end_time - start_time
        print(f"⏱️  Duration: {duration:.1f}s")

    print()
    print(format_meta_info(meta))
    print()

    if meta_only:
        return 0

    # 속도 제한
    speed = max(0.1, min(10.0, speed))
    print(f"🎬 Playback speed: {speed}x")

    if interactive:
        print("🎮 Interactive mode: [Space] pause/resume, [Q] quit, [Enter] continue")

    print("=" * 50)

    # 이벤트 리플레이
    t0 = None
    paused = False

    try:
        for i, event in enumerate(events):
            event_type = event.get("type")
            event_time = event.get("t", 0)

            # 시간 기준점 설정
            if t0 is None:
                t0 = event_time

            # 타이밍 계산 (첫 이벤트는 즉시 실행)
            if i > 0:
                relative_time = event_time - t0
                delay = max(0.0, relative_time / speed)

                # 너무 긴 지연 방지 (최대 2초)
                delay = min(delay, 2.0)

                if delay > 0:
                    time.sleep(delay)

            # 인터랙티브 모드 체크
            if interactive and sys.stdin.isatty():
                # 논블로킹 입력 체크 (간단한 구현)
                import select

                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1).lower()
                    if key == " ":
                        paused = not paused
                        if paused:
                            print("\n⏸️  [PAUSED - Press Space to resume]")
                            input()  # 다음 키 입력 대기
                            paused = False
                            print("▶️  [RESUMED]")
                    elif key == "q":
                        print("\n🛑 [STOPPED by user]")
                        return 0

            if paused:
                continue

            # 이벤트 처리
            if event_type == "user":
                print(f"\n💬 User: {event['text']}")
                print("🌌 Echo: ", end="", flush=True)

            elif event_type == "delta":
                print(event["text"], end="", flush=True)

            elif event_type == "persona":
                persona_data = event.get("data", {})
                print(
                    f"\n🎭 {persona_data.get('mix_name', 'Unknown')} "
                    f"({persona_data.get('blend_ratio', 'Unknown')})"
                )

            elif event_type == "error":
                print(f"\n❌ [ERROR] {event['msg']}")

            elif event_type == "done":
                usage = event.get("usage", {})
                print("\n✅ [Response Complete]")
                if usage and usage != {"note": "ok"}:
                    print(f"📊 Usage: {json.dumps(usage, ensure_ascii=False)}")

    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED by Ctrl+C]")
        return 0

    print("\n" + "=" * 50)
    print("🎬 Replay completed!")
    return 0


def list_sessions() -> int:
    """세션 목록 출력"""
    sessions_dir = pathlib.Path(BASE)
    if not sessions_dir.exists():
        print("❌ No sessions directory found")
        return 1

    sessions = []
    for session_dir in sorted(sessions_dir.iterdir(), reverse=True):
        if session_dir.is_dir() and session_dir.name.startswith("fs_"):
            try:
                _, meta = load_session_events(session_dir.name)
                sessions.append((session_dir.name, meta))
            except:
                sessions.append((session_dir.name, {}))

    if not sessions:
        print("❌ No Free-Speak sessions found")
        return 1

    print("🌌 Available Free-Speak Sessions")
    print("=" * 60)

    for session_id, meta in sessions[:20]:  # 최근 20개만
        # 세션 시간 파싱
        try:
            parts = session_id.split("_")
            time_str = f"{parts[1]}_{parts[2]}"
            session_time = datetime.strptime(time_str, "%Y%m%d_%H%M%S")
            time_display = session_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_display = "Unknown time"

        print(f"📁 {session_id}")
        print(f"   ⏰ {time_display}")

        # 플래그 정보
        flags = meta.get("flags", {})
        active_flags = [k for k, v in flags.items() if v]
        if active_flags:
            print(f"   🚀 {', '.join(active_flags)}")

        # 페르소나 정보
        personas = meta.get("personas", {})
        if personas:
            persona_str = " + ".join([f"{k}({v})" for k, v in personas.items()])
            print(f"   🎭 {persona_str}")

        print()

    print(f"💡 Use: python {sys.argv[0]} --session <session_id> to replay")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Free-Speak Replay System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                                    # List sessions
  %(prog)s --session fs_20250824_001122_ab12cd34     # Normal replay
  %(prog)s --session fs_20250824_001122_ab12cd34 --speed 2.0  # 2x speed
  %(prog)s --session fs_20250824_001122_ab12cd34 --meta-only  # Metadata only
  %(prog)s --session fs_20250824_001122_ab12cd34 --interactive # Interactive mode
        """,
    )

    parser.add_argument("--list", action="store_true", help="List available sessions")
    parser.add_argument(
        "--session", help="Session ID to replay (e.g., fs_20250824_001122_ab12cd34)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed (0.1-10.0, default: 1.0)",
    )
    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Show metadata only, don't replay conversation",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive controls during playback",
    )

    args = parser.parse_args()

    if args.list:
        return list_sessions()

    if not args.session:
        parser.print_help()
        return 1

    return replay_session(args.session, args.speed, args.meta_only, args.interactive)


if __name__ == "__main__":
    sys.exit(main())
