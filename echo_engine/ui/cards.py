from echo_engine.infra.portable_paths import ensure_portable, project_root, home, temp_dir, logs_dir, cache_dir, data_dir
#!/usr/bin/env python3
"""
📋 Echo UI Cards System
툴콜 결과를 사용자 친화적 카드로 표시

- 깔끔한 박스 UI
- STDOUT/STDERR 분리
- 실행 팁 제공
- Free-Speak 아카이빙 연동

@owner: echo
@expose
@maturity: production
"""

import sys
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path


def render_card(title: str, items: List[Tuple[str, str]], width: int = 55):
    """
    깔끔한 카드 UI 렌더링

    Args:
        title: 카드 제목
        items: (키, 값) 쌍의 리스트
        width: 카드 너비
    """

    # 상단 경계
    print("\n┌" + "─" * (width - 2) + "┐")

    # 제목 (truncate if too long)
    title_content = title[: width - 4] + "..." if len(title) > width - 4 else title
    print(f"│ {title_content:<{width-4}} │")

    # 중간 경계
    print("├" + "─" * (width - 2) + "┤")

    # 아이템들
    for key, value in items:
        line = f"• {key}: {value}"

        # 긴 줄 처리 (줄바꿈)
        max_content_width = width - 4

        if len(line) <= max_content_width:
            print(f"│ {line:<{max_content_width}} │")
        else:
            # 여러 줄로 분할
            words = line.split(" ")
            current_line = ""

            for word in words:
                if len(current_line + " " + word) <= max_content_width:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        print(f"│ {current_line:<{max_content_width}} │")
                    current_line = word

            if current_line:
                print(f"│ {current_line:<{max_content_width}} │")

    # 하단 경계
    print("└" + "─" * (width - 2) + "┘")


def render_tip(text: str):
    """유용한 팁 표시"""
    print(f"\n💡 {text}")


def render_error_card(title: str, error: str, suggestions: List[str] = None):
    """에러 카드 렌더링"""
    items = [("오류", error)]

    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            items.append((f"해결방안 {i}", suggestion))

    print("\n🚨 ", end="")
    render_card(title, items)


def render_success_card(
    title: str, result: Dict[str, Any], execution_tip: Optional[str] = None
):
    """성공 카드 렌더링"""
    items = []

    # 결과 정보 추가
    for key, value in result.items():
        if key == "file_path":
            items.append(("파일", str(value)))
        elif key == "execution_command":
            items.append(("실행", str(value)))
        elif key == "status":
            items.append(("상태", "✅ 성공" if value == "success" else str(value)))
        elif key == "duration":
            items.append(("소요시간", f"{value:.2f}초"))
        elif key == "lines":
            items.append(("라인수", str(value)))
        else:
            items.append((key, str(value)))

    print("\n✅ ", end="")
    render_card(title, items)

    # 실행 팁 추가
    if execution_tip:
        render_tip(execution_tip)


def render_progress_card(
    title: str, current_step: int, total_steps: int, step_description: str
):
    """진행상황 카드"""
    progress = "●" * current_step + "○" * (total_steps - current_step)
    percentage = int((current_step / total_steps) * 100)

    items = [
        ("진행도", f"{progress} ({current_step}/{total_steps})"),
        ("완료율", f"{percentage}%"),
        ("현재 단계", step_description),
    ]

    print(f"\n⏳ ", end="")
    render_card(title, items)


# 특화된 카드 렌더러들


def on_code_saved(file_path: str, language: str = "python", lines: int = 0):
    """코드 저장 완료 카드"""
    file_name = Path(file_path).name

    result = {
        "file_path": file_name,
        "language": language,
        "lines": lines if lines > 0 else "unknown",
    }

    if language.lower() == "python":
        execution_tip = f'"{file_name} 실행해줘" 라고 말해보세요.'
    else:
        execution_tip = f'"{file_name} 파일을 확인해보세요.'

    render_success_card("코드 생성 완료", result, execution_tip)


def on_code_executed(
    file_path: str,
    exit_code: int,
    duration: float = 0,
    stdout: str = "",
    stderr: str = "",
):
    """코드 실행 완료 카드"""
    file_name = Path(file_path).name

    result = {
        "file_path": file_name,
        "exit_code": exit_code,
        "status": "success" if exit_code == 0 else "failed",
    }

    if duration > 0:
        result["duration"] = duration

    if exit_code == 0:
        render_success_card("실행 완료", result)

        # 출력이 있으면 표시
        if stdout.strip():
            print("\n📤 실행 결과:")
            print("─" * 40)
            print(stdout.strip())
            print("─" * 40)
    else:
        suggestions = []
        if stderr.strip():
            suggestions.append("아래 에러 메시지를 확인하세요")
            suggestions.append("코드를 수정한 후 다시 실행해보세요")

        render_error_card("실행 실패", f"Exit code: {exit_code}", suggestions)

        if stderr.strip():
            print("\n🚨 에러 메시지:")
            print("─" * 40)
            print(stderr.strip())
            print("─" * 40)


def on_file_created(file_path: str, content_preview: str = ""):
    """파일 생성 완료 카드"""
    file_name = Path(file_path).name

    result = {"file_path": file_name, "status": "created"}

    render_success_card(
        "파일 생성 완료", result, f'"{file_name} 내용 보여줘" 라고 말해보세요.'
    )


def on_analysis_complete(analysis_type: str, findings: Dict[str, Any]):
    """분석 완료 카드"""
    items = []

    for key, value in findings.items():
        if isinstance(value, (int, float)):
            items.append((key, str(value)))
        elif isinstance(value, list):
            items.append((key, f"{len(value)}개 항목"))
        else:
            items.append(
                (key, str(value)[:50] + "..." if len(str(value)) > 50 else str(value))
            )

    render_card(f"{analysis_type} 분석 완료", items)


# Free-Speak 아카이빙 연동


def on_freespeak_session_saved(session_id: str, message_count: int, duration: float):
    """Free-Speak 세션 저장 완료 카드"""
    result = {"session_id": session_id, "messages": message_count, "duration": duration}

    render_success_card(
        "Free-Speak 세션 저장",
        result,
        f"python tools/replay_freespeak.py --session {session_id}",
    )


if __name__ == "__main__":
    # 카드 시스템 테스트
    print("📋 Testing Echo UI Cards System")
    print("=" * 50)

    # 성공 카드 테스트
    on_code_saved(str(temp_dir()), "python", 45)

    # 실행 완료 카드 테스트
    on_code_executed(str(temp_dir()), 0, 1.25, "Result: 42")

    # 실행 실패 카드 테스트
    on_code_executed(str(temp_dir()), 1, 0.5, "", "NameError: name 'x' is not defined")

    # 진행상황 카드 테스트
    render_progress_card("코드 분석 중", 3, 5, "의존성 검사")

    # 일반 카드 테스트
    render_card(
        "테스트 카드",
        [
            ("항목 1", "값 1"),
            (
                "매우 긴 항목 이름",
                "이것은 매우 긴 값이며 자동으로 줄바꿈이 되어야 합니다",
            ),
            ("상태", "완료"),
        ],
    )

    # 팁 테스트
    render_tip("이것은 유용한 팁입니다!")

    print("\n✅ 카드 시스템 테스트 완료")
