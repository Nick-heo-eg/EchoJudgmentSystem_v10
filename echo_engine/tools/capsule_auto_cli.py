"""
🎯 Capsule Auto CLI
검색 없는 즉시 캡슐 라우팅 CLI - "상황만 말하면 바로 추천"
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import track

from .capsule_auto_router import CapsuleAutoRouter
from .capsule_models import ExecutionContext

app = typer.Typer(name="auto", help="🎯 자동 캐슐 라우팅 CLI")
console = Console()

# 전역 라우터 인스턴스 (지연 초기화)
router = None


def get_router():
    """라우터 지연 초기화"""
    global router
    if router is None:
        router = CapsuleAutoRouter()
    return router


@app.command()
def route(
    situation: str = typer.Argument(help="현재 상황 (자유롭게 설명)"),
    emotion: Optional[str] = typer.Option(None, help="감정 상태"),
    intensity: float = typer.Option(0.6, help="강도 (0.0-1.0)"),
    auto_run: bool = typer.Option(False, "--run", help="자동 선택된 캡슐 즉시 실행"),
):
    """상황 기반 캡슐 자동 추천"""

    console.print(f"🎯 [yellow]상황 분석 중...[/yellow] '{situation}'")

    # 컨텍스트 생성
    context = ExecutionContext(text=situation, emotion=emotion, intensity=intensity)

    # 자동 라우팅
    recommendation = get_router().auto_route(context, limit=3)

    if not recommendation.capsule_names:
        console.print("[red]❌ 적합한 캡슐을 찾을 수 없습니다.[/red]")
        console.print("[cyan]💡 'capsule list'로 사용 가능한 캡슐을 확인하세요.[/cyan]")
        return

    # 추천 결과 표시
    console.print(
        Panel(
            f"""
🎯 [bold]자동 라우팅 결과[/bold]

[yellow]추천 이유:[/yellow] {recommendation.reasoning}
[yellow]신뢰도:[/yellow] {recommendation.confidence_score:.3f}

[yellow]추천 캡슐 ({len(recommendation.capsule_names)}개):[/yellow]
{chr(10).join(f"  {i+1}. {name}" + (" 🎯 [자동선택]" if i == 0 and recommendation.auto_selected else "")
              for i, name in enumerate(recommendation.capsule_names))}
    """,
            title="캡슐 자동 추천",
            border_style="green",
        )
    )

    # 자동 실행 여부
    if recommendation.auto_selected and auto_run:
        console.print(
            f"🚀 [green]자동 선택된 '{recommendation.capsule_names[0]}' 즉시 실행![/green]"
        )
        _execute_capsule(recommendation.capsule_names[0], context, record_success=True)
        return

    # 사용자 선택
    if len(recommendation.capsule_names) == 1:
        selected = recommendation.capsule_names[0]
    elif recommendation.auto_selected:
        # 높은 신뢰도면 자동 선택 제안
        if Confirm.ask(f"'{recommendation.capsule_names[0]}' 캡슐을 실행하시겠습니까?"):
            selected = recommendation.capsule_names[0]
        else:
            selected = _prompt_capsule_selection(recommendation.capsule_names)
    else:
        selected = _prompt_capsule_selection(recommendation.capsule_names)

    if selected:
        console.print(f"🎭 [cyan]선택된 캡슐: {selected}[/cyan]")
        _execute_capsule(selected, context, record_success=True)
    else:
        console.print("[yellow]취소되었습니다.[/yellow]")


@app.command()
def suggest(
    keywords: str = typer.Argument(help="키워드들 (공백으로 구분)"),
    limit: int = typer.Option(5, help="추천 개수"),
):
    """키워드 기반 빠른 추천"""

    keyword_list = keywords.split()
    console.print(f"🔍 키워드: {', '.join(keyword_list)}")

    # 간단한 컨텍스트로 라우팅
    context = ExecutionContext(text=" ".join(keyword_list), intensity=0.5)
    recommendation = get_router().auto_route(context, limit=limit)

    if not recommendation.capsule_names:
        console.print("[red]❌ 매칭되는 캡슐이 없습니다.[/red]")
        return

    table = Table(title="키워드 기반 캡슐 추천")
    table.add_column("순위", style="cyan")
    table.add_column("캡슐", style="green")
    table.add_column("매치점수", style="yellow")
    table.add_column("설명", style="blue")

    capsule_engine = get_router().engine
    for i, capsule_name in enumerate(recommendation.capsule_names):
        capsule = capsule_engine.registry.get_capsule(capsule_name)
        description = capsule.description if capsule else "N/A"

        table.add_row(
            str(i + 1),
            capsule_name,
            f"{recommendation.context_match_score:.3f}",
            description[:50] + "..." if len(description) > 50 else description,
        )

    console.print(table)


@app.command()
def hotlist(limit: int = typer.Option(10, help="표시할 인기 캡슐 수")):
    """인기 캡슐 핫리스트 (즐겨찾기)"""

    hot_capsules = get_router().get_hotlist(limit)

    if not hot_capsules:
        console.print("[yellow]아직 사용 기록이 없습니다.[/yellow]")
        console.print("[cyan]💡 캡슐을 몇 번 사용하면 인기 목록이 생성됩니다.[/cyan]")
        return

    console.print("🔥 [bold red]인기 캡슐 핫리스트[/bold red]")

    table = Table(title=f"Top {len(hot_capsules)} 인기 캡슐")
    table.add_column("순위", style="cyan")
    table.add_column("캡슐", style="green")
    table.add_column("인기도", style="red")
    table.add_column("타입", style="blue")

    capsule_engine = get_router().engine
    for i, (capsule_name, popularity) in enumerate(hot_capsules):
        capsule = capsule_engine.registry.get_capsule(capsule_name)
        capsule_type = capsule.type.value if capsule else "N/A"

        # 인기도를 별표로 시각화
        stars = "★" * int(popularity * 5)

        table.add_row(
            str(i + 1), capsule_name, f"{popularity:.3f} {stars}", capsule_type
        )

    console.print(table)


@app.command()
def smart(
    situation: str = typer.Argument(help="상황 설명"),
    dry_run: bool = typer.Option(False, help="실제 실행 없이 추천만"),
):
    """스마트 모드 - 분석→추천→실행을 한 번에"""

    console.print("🧠 [bold blue]스마트 모드 활성화[/bold blue]")
    console.print(f"📝 상황: {situation}")

    # 1단계: 상황 분석
    console.print("\n[yellow]1단계: 상황 분석 중...[/yellow]")
    context = ExecutionContext(text=situation, intensity=0.7)

    # 컨텍스트 신호 추출 (내부 분석기 직접 호출)
    signal = get_router().analyzer.analyze_context(situation)

    console.print(
        Panel(
            f"""
🔍 [bold]분석 결과[/bold]

[yellow]감지된 감정:[/yellow] {', '.join(signal.emotions) if signal.emotions else '없음'}
[yellow]캡슐 힌트:[/yellow] {', '.join(signal.capsule_hints[:3]) if signal.capsule_hints else '없음'}
[yellow]긴급도:[/yellow] {signal.urgency:.1f}/1.0
[yellow]복잡도:[/yellow] {signal.complexity:.1f}/1.0
[yellow]주요 키워드:[/yellow] {', '.join(signal.keywords[:5]) if signal.keywords else '없음'}
    """,
            title="상황 분석",
            border_style="blue",
        )
    )

    # 2단계: 캡슐 추천
    console.print("\n[yellow]2단계: 최적 캡슐 추천...[/yellow]")
    recommendation = get_router().auto_route(context, limit=1)

    if not recommendation.capsule_names:
        console.print("[red]❌ 적합한 캡슐을 찾을 수 없습니다.[/red]")
        return

    selected_capsule = recommendation.capsule_names[0]
    console.print(f"🎯 [green]선택된 캡슐: {selected_capsule}[/green]")
    console.print(f"🎲 신뢰도: {recommendation.confidence_score:.3f}")
    console.print(f"🧠 추천 이유: {recommendation.reasoning}")

    if dry_run:
        console.print("\n[cyan]🔍 드라이런 모드: 실제 실행하지 않음[/cyan]")
        return

    # 3단계: 자동 실행
    console.print(f"\n[yellow]3단계: '{selected_capsule}' 실행 중...[/yellow]")
    _execute_capsule(selected_capsule, context, record_success=True)


@app.command()
def warmup():
    """캐시 웜업 - 초기 인기도 설정"""

    console.print("🔥 [yellow]캐시 웜업 중...[/yellow]")
    get_router().warm_up_cache()

    hotlist = get_router().get_hotlist(5)
    console.print("[green]✅ 캐시 웜업 완료![/green]")

    if hotlist:
        console.print("\n📊 초기 인기도 설정 결과:")
        for i, (name, score) in enumerate(hotlist):
            console.print(f"  {i+1}. {name}: {score:.3f}")


@app.command()
def learn(
    capsule_name: str = typer.Argument(help="학습할 캡슐"),
    situation: str = typer.Argument(help="상황"),
    success: bool = typer.Option(True, help="성공 여부"),
):
    """수동 학습 - 캡슐과 상황 연관성 학습"""

    context = ExecutionContext(text=situation)
    get_router().record_selection(capsule_name, context, success)

    status = "성공" if success else "실패"
    console.print(
        f"📚 [green]학습 완료![/green] '{capsule_name}' ← '{situation}' ({status})"
    )

    # 업데이트된 인기도 표시
    popularity = get_router().cache.get_popularity_score(capsule_name)
    console.print(f"📈 '{capsule_name}' 인기도: {popularity:.3f}")


@app.command()
def analyze(text: str = typer.Argument(help="분석할 텍스트")):
    """상황 분석기 테스트"""

    signal = get_router().analyzer.analyze_context(text)

    console.print(
        Panel(
            f"""
🔍 [bold]상황 분석 결과[/bold]

[yellow]입력:[/yellow] "{text}"

[yellow]감지된 감정:[/yellow]
{chr(10).join(f"  • {emotion}" for emotion in signal.emotions) if signal.emotions else "  없음"}

[yellow]캡슐 힌트:[/yellow]
{chr(10).join(f"  • {hint}" for hint in signal.capsule_hints) if signal.capsule_hints else "  없음"}

[yellow]지표:[/yellow]
  • 긴급도: {signal.urgency:.3f}
  • 복잡도: {signal.complexity:.3f}

[yellow]키워드:[/yellow]
{", ".join(signal.keywords[:10]) if signal.keywords else "없음"}
    """,
            title="분석기 테스트",
            border_style="cyan",
        )
    )


def _prompt_capsule_selection(capsule_names: List[str]) -> Optional[str]:
    """캡슐 선택 프롬프트"""
    console.print("\n[yellow]캡슐을 선택하세요:[/yellow]")

    for i, name in enumerate(capsule_names):
        console.print(f"  {i+1}. {name}")

    console.print("  0. 취소")

    try:
        choice = typer.prompt("선택 (번호)", type=int)
        if 1 <= choice <= len(capsule_names):
            return capsule_names[choice - 1]
        elif choice == 0:
            return None
        else:
            console.print("[red]잘못된 번호입니다.[/red]")
            return None
    except Exception:
        console.print("[red]잘못된 입력입니다.[/red]")
        return None


def _execute_capsule(
    capsule_name: str, context: ExecutionContext, record_success: bool = True
):
    """캡슐 실행 및 결과 표시"""
    try:
        # 캡슐 엔진으로 시뮬레이션
        capsule_engine = get_router().engine
        capsule = capsule_engine.registry.get_capsule(capsule_name)

        if not capsule:
            console.print(f"[red]❌ 캡슐 '{capsule_name}'을 찾을 수 없습니다.[/red]")
            if record_success:
                get_router().record_selection(capsule_name, context, False)
            return

        result = capsule_engine.simulate_capsule(capsule, context)

        # 실행 결과 표시
        console.print(
            Panel(
                f"""
🎭 [bold]실행 결과[/bold]

[yellow]캡슐:[/yellow] {result.capsule_name}
[yellow]트리거된 규칙:[/yellow] {len(result.triggered_rules)}개
[yellow]실행된 액션:[/yellow] {len(result.output_actions)}개
[yellow]신뢰도:[/yellow] {result.confidence_score:.3f}
[yellow]실행시간:[/yellow] {result.execution_time_ms:.2f}ms

[yellow]액션 목록:[/yellow]
{chr(10).join(f"  • {action}" for action in result.output_actions)}

[yellow]감정 상태:[/yellow]
{chr(10).join(f"  • {k}: {v:.3f}" for k, v in result.emotional_state.items())}
        """,
                title=f"'{capsule_name}' 실행 완료",
                border_style="green",
            )
        )

        # 성공 기록
        if record_success:
            success = len(result.triggered_rules) > 0 and result.confidence_score > 0.3
            get_router().record_selection(capsule_name, context, success)

            if success:
                console.print("[dim green]📚 성공 케이스로 학습되었습니다.[/dim green]")

    except Exception as e:
        console.print(f"[red]❌ 실행 실패: {e}[/red]")
        if record_success:
            get_router().record_selection(capsule_name, context, False)


if __name__ == "__main__":
    app()
