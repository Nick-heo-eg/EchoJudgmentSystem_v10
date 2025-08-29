#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Advisor - 헬스체크 후 자동 개선 제안 시스템
Health Score에 따라 적절한 도구와 명령어를 자동 제안
# @owner: nick
# @expose
# @maturity: stable
"""
import re
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def extract_health_score() -> float:
    """가장 최근 health 실행 결과에서 점수 추출"""
    try:
        # health 명령어 다시 실행해서 점수 가져오기
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "echo_engine.evolve_min",
                "--health",
                "--fast",
                "--max-seconds",
                "20",
                "--limit",
                "800",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            output = result.stdout
            # "Echo 시스템 건강도: XX.X/100" 패턴 찾기
            match = re.search(r"Echo 시스템 건강도:\s*(\d+\.?\d*)/100", output)
            if match:
                return float(match.group(1))
    except Exception as e:
        console.print(f"[yellow]⚠️ Health score 추출 실패: {e}[/yellow]")

    return 50.0  # 기본값


def count_issues() -> dict:
    """이슈 종류별 개수 파악"""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "echo_engine.evolve_min",
                "--health",
                "--fast",
                "--max-seconds",
                "10",
                "--limit",
                "200",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            output = result.stdout

            # "발견된 이슈: XX개" 패턴
            total_match = re.search(r"발견된 이슈:\s*(\d+)개", output)
            total_issues = int(total_match.group(1)) if total_match else 0

            # 카테고리별 이슈 파싱
            issues = {"total": total_issues}
            category_pattern = r"•\s*(\w+):\s*(\d+)개"
            for match in re.finditer(category_pattern, output):
                category, count = match.groups()
                issues[category] = int(count)

            return issues

    except Exception as e:
        console.print(f"[yellow]⚠️ 이슈 분석 실패: {e}[/yellow]")

    return {"total": 0}


def suggest_improvements(health_score: float, issues: dict):
    """Health Score와 이슈 상황에 맞는 개선 제안"""

    console.print("\n" + "=" * 60)
    console.print("🏥 Health Advisor - 자동 개선 제안")
    console.print("=" * 60)

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

    # Meta 기능 연결 안내
    console.print(f"\n🎯 [bold blue]Meta 기능 활용:[/bold blue]")
    console.print(f"   • 캡슐에서 /find cli health → 헬스 관련 도구 검색")
    console.print(f"   • 캡슐에서 /find tool fix → 자동 수정 도구 검색")
    console.print(f"   • python echo_capsule_chat_safe.py → 자연어 기능 접근")

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

    console.print("\n" + "=" * 60 + "\n")


def main():
    """메인 실행 함수"""
    try:
        health_score = extract_health_score()
        issues = count_issues()
        suggest_improvements(health_score, issues)

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Health Advisor 종료[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Health Advisor 실행 실패: {e}[/red]")


if __name__ == "__main__":
    main()
