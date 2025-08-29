#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 3 수술: Health 흐름 통합 시스템
health 체크 + advisor 제안을 단일 실행으로 통합 (중복 실행 제거)
# @owner: nick
# @expose
# @maturity: stable
"""
import re
import sys
import subprocess
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
ROOT = Path(__file__).resolve().parents[1]


def run_health_check(
    fast: bool = True, max_seconds: int = 20, limit: int = 800
) -> tuple[float, dict]:
    """통합 헬스 체크 실행 (단일 실행)"""
    console.print(
        f"[blue]🏥 통합 헬스 체크 시작 ({'FAST' if fast else 'FULL'} 모드)[/blue]"
    )

    cmd = [
        sys.executable,
        "-m",
        "echo_engine.evolve_min",
        "--health",
        "--limit",
        str(limit),
        "--max-seconds",
        str(max_seconds),
    ]
    if fast:
        cmd.insert(3, "--fast")

    try:
        console.print(f"[dim]실행 명령어: {' '.join(cmd)}[/dim]")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=max_seconds + 30, cwd=ROOT
        )

        if result.returncode == 0:
            output = result.stdout
            console.print(output)  # 실시간 출력

            # 점수 추출
            match = re.search(r"Echo 시스템 건강도:\s*(\d+\.?\d*)/100", output)
            health_score = float(match.group(1)) if match else 50.0

            # 이슈 분석
            issues = {"total": 0}
            total_match = re.search(r"발견된 이슈:\s*(\d+)개", output)
            if total_match:
                issues["total"] = int(total_match.group(1))

            # 카테고리별 이슈 파싱
            category_pattern = r"•\s*(\w+):\s*(\d+)개"
            for match in re.finditer(category_pattern, output):
                category, count = match.groups()
                issues[category] = int(count)

            return health_score, issues

        else:
            console.print(f"[red]❌ Health 체크 실패: {result.stderr}[/red]")
            return 50.0, {"total": 0}

    except subprocess.TimeoutExpired:
        console.print(f"[red]❌ Health 체크 타임아웃 ({max_seconds}초)[/red]")
        return 50.0, {"total": 0}
    except Exception as e:
        console.print(f"[red]❌ Health 체크 오류: {e}[/red]")
        return 50.0, {"total": 0}


def generate_advisor_recommendations(health_score: float, issues: dict):
    """개선 제안 생성 (기존 health_advisor.py 로직 통합 + Advanced Audit 연동)"""

    console.print("\n" + "=" * 60)
    console.print("🏥 Health Advisor - 자동 개선 제안 (+ Advanced Audit)")
    console.print("=" * 60)

    # Advanced Audit 사용 가능성 체크
    advanced_audit_available = (ROOT / "advanced_whitehack_audit.py").exists()
    if advanced_audit_available:
        console.print(
            "[cyan]🔍 Advanced Audit 시스템 발견 - 고급 보안 감사 가능[/cyan]"
        )

    # Health Score별 평가
    if health_score >= 65:
        status_color = "green"
        status_emoji = "🟢"
        status_text = "우수"
    elif health_score >= 45:
        status_color = "yellow"
        status_emoji = "🟡"
        status_text = "보통"
    else:
        status_color = "red"
        status_emoji = "🔴"
        status_text = "개선 필요"

    console.print(
        f"\n📊 현재 상태: [{status_color}]{status_emoji} {health_score:.1f}/100 ({status_text})[/{status_color}]"
    )

    if issues.get("total", 0) > 0:
        console.print(f"⚠️  총 {issues['total']}개 이슈 발견")

    # 제안 테이블
    table = Table(title="🎯 추천 개선 작업", show_header=True, header_style="bold blue")
    table.add_column("우선순위", style="cyan", width=8)
    table.add_column("작업", style="white", width=35)
    table.add_column("명령어", style="green", width=35)

    suggestions = []

    # Health Score별 제안
    if health_score < 45:
        suggestions.append(("🔥 High", "Import 문제 자동 수정", "make imports-fix"))
        suggestions.append(
            (
                "🔥 High",
                "큰 파일들 태깅 (리팩터링 대상)",
                "python tools/feature_tagger.py --profile development",
            )
        )
        suggestions.append(("🔴 High", "문제 파일들 상세 분석", "make imports-analyze"))

    elif health_score < 65:
        suggestions.append(
            ("🟡 Mid", "Import 분석 및 선택적 수정", "make imports-analyze")
        )
        suggestions.append(
            (
                "🟡 Mid",
                "안정적인 기능만 태깅",
                "python tools/feature_tagger.py --profile minimal",
            )
        )
        suggestions.append(("🟢 Low", "포팅성 문제 체크", "make portability-dry"))

    else:
        suggestions.append(
            (
                "🟢 Low",
                "새 기능 개발 준비",
                'python quick_dev.py plan "새 기능 아이디어"',
            )
        )
        suggestions.append(
            (
                "🟢 Low",
                "전체 시스템 기능 매핑",
                "python tools/feature_mapper.py --save --html --profile development",
            )
        )
        suggestions.append(
            (
                "🌟 Opt",
                "고급 개발 워크플로우",
                'python workflow_runner.py full "프로젝트" 이름',
            )
        )

    # 이슈별 특화 제안
    if issues.get("import", 0) >= 5:
        suggestions.insert(
            0, ("🔥 Urgent", "Import 문제 집중 해결", "make imports-fix")
        )

    if issues.get("size", 0) >= 3:
        suggestions.append(
            (
                "🟡 Mid",
                "대형 파일 분석",
                "python tools/feature_mapper.py --profile development | grep 'size'",
            )
        )

    if issues.get("complexity", 0) >= 3:
        suggestions.append(
            (
                "🟡 Mid",
                "복잡도 높은 파일 리팩터링 준비",
                "python tools/feature_tagger.py --profile minimal --dry-run",
            )
        )

    # 테이블에 추가
    for priority, task, command in suggestions[:6]:  # 최대 6개만 표시
        table.add_row(priority, task, command)

    console.print(table)

    # Meta 기능 연결 안내 (확장됨)
    console.print(f"\n🎯 [bold blue]Meta 기능 활용:[/bold blue]")
    console.print(f"   • 캡슐에서 /find cli health → 헬스 관련 도구 검색")
    console.print(f"   • 캡슐에서 /find tool fix → 자동 수정 도구 검색")
    console.print(f"   • python echo_capsule_chat_safe.py → 자연어 기능 접근")

    # 새롭게 발곴된 기능들
    console.print(f"\n[bold green]🔍 새롭게 발곴된 고급 도구들:[/bold green]")
    if advanced_audit_available:
        console.print(
            f"   • python advanced_whitehack_audit.py → 토탈 보안 감사 (실제 인스톨/동작 검증)"
        )
    console.print(f"   • python auto_launcher.py --echo → 전체 시스템 자동 시작")
    console.print(
        f"   • python agent_orchestra_runner.py → YAML 기반 멀티 에이전트 시스템"
    )

    # 다음 단계 안내
    if health_score < 45:
        console.print(f"\n[red]🚨 권장 워크플로우:[/red]")
        console.print(f"   1. make imports-fix")
        console.print(f"   2. make compile && make smoke")
        console.print(f"   3. make health (재확인)")
        console.print(f"   4. python tools/feature_tagger.py --profile minimal")
    else:
        console.print(
            f"\n[green]✨ 시스템이 안정적입니다! 새로운 개발을 시작하기 좋은 상태입니다.[/green]"
        )
        console.print(f"   추천: python cosmos_auto_init.py 로 개발 도구 메뉴 확인")

        # 안정적인 시스템에서 추가 연결 제안
        if advanced_audit_available:
            console.print(f"\n[blue]🛡️ 고급 보안 감사 추천:[/blue]")
            console.print(
                f"   python advanced_whitehack_audit.py 로 전체 시스템 보안 점검"
            )

    console.print("\n" + "=" * 60 + "\n")


def main():
    """Stage 3 수술: 통합 Health 시스템 메인"""
    parser = argparse.ArgumentParser(
        description="Stage 3 수술: Health 흐름 통합 시스템"
    )
    parser.add_argument("--fast", action="store_true", help="빠른 헬스 체크 모드")
    parser.add_argument("--max-seconds", type=int, default=20, help="최대 실행 시간")
    parser.add_argument("--limit", type=int, default=800, help="스캔 제한")

    args = parser.parse_args()

    try:
        console.print(
            Panel(
                """
🩸 [bold]Stage 3 수술: Health 흐름 통합[/bold]

기존: health 체크 → advisor 제안 (2번 실행)
수술: health + advisor 단일 통합 실행 (1번 실행)

⚡ 예상 효과: 30-50% 시간 단축
        """,
                title="🏥 Health 수술",
                border_style="red",
            )
        )

        # 단일 통합 실행
        health_score, issues = run_health_check(
            fast=args.fast, max_seconds=args.max_seconds, limit=args.limit
        )

        # 즉시 제안 생성 (추가 실행 없음)
        generate_advisor_recommendations(health_score, issues)

        console.print(
            "[green]✅ Stage 3 수술 완료: Health + Advisor 단일 통합 실행[/green]"
        )

        # 고급 감사 후속 작업 제안
        if health_score >= 65:
            advanced_audit_available = (
                Path(__file__).parent.parent / "advanced_whitehack_audit.py"
            ).exists()
            if advanced_audit_available:
                console.print(
                    "[cyan]🔍 시스템이 안정적이니 고급 보안 감사를 고려해보세요: python advanced_whitehack_audit.py[/cyan]"
                )

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Health 통합 시스템 종료[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Health 통합 시스템 실행 실패: {e}[/red]")


if __name__ == "__main__":
    main()
