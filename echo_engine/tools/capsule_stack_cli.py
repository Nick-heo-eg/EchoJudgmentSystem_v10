"""
🧬 Capsule Stack CLI
캡슐 스택 관리 CLI 도구
"""

import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

from .capsule_stack import CapsuleStackEngine, CapsuleStackResult
from .capsule_models import ExecutionContext

app = typer.Typer(name="stack", help="🧬 캡슐 스택 관리 CLI")
console = Console()

stack_engine = CapsuleStackEngine()


@app.command()
def create(
    name: str = typer.Argument(help="스택 이름"),
    capsules: str = typer.Argument(help="캡슐들 (쉼표로 구분)"),
):
    """캡슐 스택 생성"""
    capsule_list = [c.strip() for c in capsules.split(",")]

    try:
        stack_engine.create_stack(name, capsule_list)
        console.print(f"[green]✅ 스택 '{name}' 생성 완료![/green]")

        # 스택 정보 표시
        info = stack_engine.get_stack_info(name)
        console.print(
            Panel(
                f"""
🧬 [bold]스택 구성[/bold]

[yellow]캡슐 수:[/yellow] {info['total_capsules']}개
[yellow]총 규칙 수:[/yellow] {info['stack_composition']['total_rules']}개
[yellow]타입 분포:[/yellow] {info['stack_composition']['type_distribution']}
[yellow]다양성 점수:[/yellow] {info['stack_composition']['diversity_score']:.3f}

[yellow]포함된 캡슐:[/yellow]
{chr(10).join(f"  • {c['name']} ({c['type']}) - {c['rules_count']}개 규칙" for c in info['capsules'])}
        """,
                title=f"스택 '{name}'",
                border_style="blue",
            )
        )

        # 보완 캡슐 추천
        suggestions = stack_engine.suggest_complementary_capsules(capsule_list)
        if suggestions:
            console.print(f"[cyan]💡 보완 추천 캡슐: {', '.join(suggestions)}[/cyan]")

    except ValueError as e:
        console.print(f"[red]❌ 스택 생성 실패: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def execute(
    name: str = typer.Argument(help="실행할 스택 이름"),
    text: Optional[str] = typer.Option(None, help="입력 텍스트"),
    emotion: Optional[str] = typer.Option(None, help="감정 상태"),
    intensity: float = typer.Option(0.5, help="감정 강도"),
):
    """캡슐 스택 실행"""
    try:
        context = ExecutionContext(text=text, emotion=emotion, intensity=intensity)

        console.print(f"🧬 스택 '{name}' 실행 중...")
        result = stack_engine.execute_stack(name, context)

        # 실행 결과 출력
        console.print(
            Panel(
                f"""
🎯 [bold]스택 실행 결과[/bold]

[yellow]트리거된 캡슐:[/yellow] {result.capsules_triggered}/{len(result.capsule_results)}개

[yellow]통합 액션 ({len(result.combined_actions)}개):[/yellow]
{chr(10).join(f"  • {action}" for action in result.combined_actions)}

[yellow]통합 감정 상태:[/yellow]
{chr(10).join(f"  • {emotion}: {value:.3f}" for emotion, value in result.combined_emotional_state.items())}

[yellow]성능 메트릭:[/yellow]
  • 총 실행 시간: {result.total_execution_time_ms:.2f}ms
  • 스택 신뢰도: {result.stack_confidence:.3f}
  • 시너지 점수: {result.synergy_score:.3f}
        """,
                title=f"'{name}' 실행 결과",
                border_style="green",
            )
        )

        # 개별 캡슐 결과 요약
        if len(result.capsule_results) > 1:
            table = Table(title="개별 캡슐 결과")
            table.add_column("캡슐", style="cyan")
            table.add_column("트리거된 규칙", style="yellow")
            table.add_column("액션", style="green")
            table.add_column("신뢰도", style="blue")

            for capsule_result in result.capsule_results:
                table.add_row(
                    capsule_result.capsule_name,
                    str(len(capsule_result.triggered_rules)),
                    str(len(capsule_result.output_actions)),
                    f"{capsule_result.confidence_score:.3f}",
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ 스택 실행 실패: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list():
    """생성된 스택 목록"""
    stacks = stack_engine.list_stacks()

    if not stacks:
        console.print("[yellow]생성된 스택이 없습니다.[/yellow]")
        return

    table = Table(title=f"캡슐 스택 목록 ({len(stacks)}개)")
    table.add_column("스택 이름", style="cyan")
    table.add_column("캡슐 수", style="green")
    table.add_column("총 규칙", style="yellow")
    table.add_column("다양성", style="blue")
    table.add_column("구성", style="magenta")

    for stack_name in stacks:
        info = stack_engine.get_stack_info(stack_name)
        composition = info["stack_composition"]

        table.add_row(
            stack_name,
            str(info["total_capsules"]),
            str(composition["total_rules"]),
            f"{composition['diversity_score']:.2f}",
            ", ".join(f"{k}({v})" for k, v in composition["type_distribution"].items()),
        )

    console.print(table)


@app.command()
def info(name: str):
    """스택 상세 정보"""
    info = stack_engine.get_stack_info(name)

    if not info:
        console.print(f"[red]스택 '{name}'을 찾을 수 없습니다.[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"""
[bold cyan]{info['stack_name']}[/bold cyan] 스택

[yellow]구성 정보:[/yellow]
• 캡슐 수: {info['total_capsules']}개
• 총 규칙 수: {info['stack_composition']['total_rules']}개
• 평균 규칙/캡슐: {info['stack_composition']['avg_rules_per_capsule']:.1f}개
• 다양성 점수: {info['stack_composition']['diversity_score']:.3f}

[yellow]타입 분포:[/yellow]
{chr(10).join(f"• {k}: {v}개" for k, v in info['stack_composition']['type_distribution'].items())}

[yellow]포함된 캡슐들:[/yellow]
{chr(10).join(f"• {c['name']} ({c['type']}) - {c['description'][:50]}..." for c in info['capsules'])}
    """,
            title="스택 상세 정보",
            border_style="blue",
        )
    )


@app.command()
def optimize(name: str):
    """스택 실행 순서 최적화"""
    if name not in stack_engine.stacks:
        console.print(f"[red]스택 '{name}'을 찾을 수 없습니다.[/red]")
        raise typer.Exit(1)

    original_order = stack_engine.stacks[name]
    optimized_order = stack_engine.optimize_stack_order(original_order)

    console.print(f"[yellow]🔧 스택 '{name}' 최적화 결과:[/yellow]")

    table = Table(title="실행 순서 비교")
    table.add_column("순서", style="cyan")
    table.add_column("기존", style="red")
    table.add_column("최적화", style="green")

    max_len = max(len(original_order), len(optimized_order))
    for i in range(max_len):
        original = original_order[i] if i < len(original_order) else ""
        optimized = optimized_order[i] if i < len(optimized_order) else ""
        table.add_row(str(i + 1), original, optimized)

    console.print(table)

    # 최적화 적용 여부 확인
    if typer.confirm("최적화된 순서를 적용하시겠습니까?"):
        stack_engine.stacks[name] = optimized_order
        stack_engine._save_stacks()
        console.print("[green]✅ 최적화 순서가 적용되었습니다![/green]")


@app.command()
def suggest(capsules: str):
    """보완 캡슐 추천"""
    capsule_list = [c.strip() for c in capsules.split(",")]
    suggestions = stack_engine.suggest_complementary_capsules(capsule_list)

    console.print(
        Panel(
            f"""
[yellow]기존 캡슐:[/yellow] {', '.join(capsule_list)}

[yellow]추천 보완 캡슐:[/yellow]
{chr(10).join(f"• {suggestion}" for suggestion in suggestions) if suggestions else "• 모든 타입이 이미 포함되어 있습니다"}

[cyan]💡 다양한 타입의 캡슐을 조합하면 더 높은 시너지 효과를 얻을 수 있습니다![/cyan]
    """,
            title="캡슐 추천",
            border_style="magenta",
        )
    )


@app.command()
def remove(name: str):
    """스택 제거"""
    if stack_engine.remove_stack(name):
        console.print(f"[green]✅ 스택 '{name}'이 제거되었습니다.[/green]")
    else:
        console.print(f"[red]❌ 스택 '{name}'을 찾을 수 없습니다.[/red]")


@app.command()
def benchmark(
    name: str,
    iterations: int = typer.Option(10, help="반복 횟수"),
    text: str = typer.Option("benchmark test", help="테스트 텍스트"),
):
    """스택 성능 벤치마크"""
    context = ExecutionContext(text=text, intensity=0.6)
    results = []

    console.print(f"🧬 스택 '{name}' 벤치마크 실행 중...")

    for i in track(range(iterations), description="벤치마킹..."):
        try:
            result = stack_engine.execute_stack(name, context)
            results.append(result)
        except Exception as e:
            console.print(f"[red]반복 {i+1} 실패: {e}[/red]")

    if not results:
        console.print("[red]❌ 모든 벤치마크가 실패했습니다.[/red]")
        return

    # 통계 계산
    avg_time = sum(r.total_execution_time_ms for r in results) / len(results)
    avg_confidence = sum(r.stack_confidence for r in results) / len(results)
    avg_synergy = sum(r.synergy_score for r in results) / len(results)
    avg_actions = sum(len(r.combined_actions) for r in results) / len(results)

    console.print(
        Panel(
            f"""
📊 [bold]벤치마크 결과[/bold] ({len(results)}/{iterations} 성공)

[yellow]평균 성능:[/yellow]
• 실행 시간: {avg_time:.2f}ms
• 스택 신뢰도: {avg_confidence:.3f}
• 시너지 점수: {avg_synergy:.3f}
• 평균 액션 수: {avg_actions:.1f}개

[yellow]범위:[/yellow]
• 최소 시간: {min(r.total_execution_time_ms for r in results):.2f}ms
• 최대 시간: {max(r.total_execution_time_ms for r in results):.2f}ms
• 최고 시너지: {max(r.synergy_score for r in results):.3f}
    """,
            title=f"'{name}' 벤치마크",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
