"""
🎭 Capsule CLI Tool
실행 가능한 캡슐 시스템 CLI
"""

import typer
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from datetime import datetime

from .capsule_models import (
    CapsuleSpec,
    CapsuleRule,
    CapsuleTemplate,
    ExecutionContext,
    SimulationResult,
    CapsuleRegistry,
    CapsuleType,
)
from .capsule_auto_cli import app as auto_app

app = typer.Typer(name="capsule", help="🎭 Echo 캡슐 시스템 CLI")
console = Console()

# 자동 라우팅 서브커맨드 추가
app.add_typer(auto_app, name="auto")


class CapsuleEngine:
    """캡슐 실행 엔진"""

    def __init__(self, registry_path: str = "data/capsule_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> CapsuleRegistry:
        """레지스트리 로드"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return CapsuleRegistry(**data)
            except Exception as e:
                console.print(f"[red]레지스트리 로드 실패: {e}[/red]")

        return CapsuleRegistry()

    def _save_registry(self):
        """레지스트리 저장"""
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(
                self.registry.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )

    def validate_capsule_spec(self, capsule: CapsuleSpec) -> List[str]:
        """캡슐 사양 검증"""
        errors = []

        # 기본 검증
        if not capsule.name.strip():
            errors.append("캡슐 이름이 비어있습니다")

        if not capsule.description.strip():
            errors.append("캡슐 설명이 비어있습니다")

        # 규칙 검증
        for i, rule in enumerate(capsule.rules):
            if not rule.condition.strip():
                errors.append(f"규칙 {i+1}의 조건이 비어있습니다")
            if not rule.action.strip():
                errors.append(f"규칙 {i+1}의 액션이 비어있습니다")
            if rule.priority < 1 or rule.priority > 10:
                errors.append(f"규칙 {i+1}의 우선순위는 1-10 범위여야 합니다")

        return errors

    def simulate_capsule(
        self, capsule: CapsuleSpec, context: ExecutionContext
    ) -> SimulationResult:
        """캡슐 시뮬레이션 실행"""
        start_time = datetime.now()

        triggered_rules = []
        output_actions = []
        emotional_state = {"joy": 0.6, "excitement": 0.4, "confidence": 0.7}

        # 규칙 평가 및 실행
        for rule in sorted(capsule.rules, key=lambda r: r.priority, reverse=True):
            if self._evaluate_condition(rule.condition, context):
                triggered_rules.append(rule.condition)
                output_actions.append(rule.action)

                # 감정 상태 업데이트 (간단한 시뮬레이션)
                if "joy" in rule.action.lower():
                    emotional_state["joy"] = min(1.0, emotional_state["joy"] + 0.1)
                if "excite" in rule.action.lower():
                    emotional_state["excitement"] = min(
                        1.0, emotional_state["excitement"] + 0.1
                    )

        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        confidence = len(triggered_rules) / max(1, len(capsule.rules))

        return SimulationResult(
            capsule_name=capsule.name,
            input_context=context,
            triggered_rules=triggered_rules,
            output_actions=output_actions,
            emotional_state=emotional_state,
            execution_time_ms=execution_time,
            confidence_score=confidence,
        )

    def _evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
        """조건 평가 (간단한 구현)"""
        condition_lower = condition.lower()

        # 텍스트 기반 조건
        if "text:" in condition_lower:
            keyword = condition_lower.split("text:")[1].strip()
            return keyword in (context.text or "").lower()

        # 감정 기반 조건
        if "emotion:" in condition_lower:
            target_emotion = condition_lower.split("emotion:")[1].strip()
            return target_emotion == (context.emotion or "").lower()

        # 강도 기반 조건
        if "intensity>" in condition_lower:
            try:
                threshold = float(condition_lower.split("intensity>")[1].strip())
                return context.intensity > threshold
            except:
                pass

        # 기본: 항상 참
        return True


# CLI 인스턴스
engine = CapsuleEngine()


@app.command()
def init(
    name: str = typer.Option("sample-capsule", help="캡슐 이름"),
    type: str = typer.Option(
        "emotion", help="캡슐 타입 (emotion/signature/cognitive/hybrid)"
    ),
    output: str = typer.Option("examples/capsules", help="출력 디렉토리"),
):
    """샘플 캡슐 생성"""
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 샘플 캡슐 생성
    sample_rules = [
        CapsuleRule(
            condition="text:hello", action="respond_warmly", priority=5, weight=0.8
        ),
        CapsuleRule(
            condition="emotion:sad", action="provide_comfort", priority=7, weight=0.9
        ),
        CapsuleRule(
            condition="intensity>0.7", action="amplify_response", priority=3, weight=0.6
        ),
    ]

    capsule = CapsuleSpec(
        name=name,
        type=CapsuleType(type),
        description=f"샘플 {type} 캡슐",
        rules=sample_rules,
        parameters={"sensitivity": 0.7, "creativity": 0.6, "empathy": 0.8},
        tags=[type, "sample", "generated"],
    )

    # YAML 파일로 저장 (enum을 문자열로 변환)
    capsule_file = output_dir / f"{name}.yaml"
    capsule_dict = capsule.model_dump()
    capsule_dict["type"] = capsule_dict["type"]  # 이미 문자열로 변환됨
    with open(capsule_file, "w", encoding="utf-8") as f:
        yaml.dump(capsule_dict, f, default_flow_style=False, allow_unicode=True)

    console.print(f"✅ 샘플 캡슐 생성됨: [green]{capsule_file}[/green]")

    # 간단한 사용법 표시
    console.print(
        Panel(
            f"""
🎯 다음 명령어로 캡슐을 테스트해보세요:

[yellow]capsule validate {capsule_file}[/yellow]
[yellow]capsule simulate {capsule_file} --text "hello world"[/yellow]
[yellow]capsule register {capsule_file}[/yellow]
    """,
            title="사용법",
            border_style="blue",
        )
    )


@app.command()
def validate(file_path: str):
    """캡슐 YAML 파일 검증"""
    capsule_path = Path(file_path)

    if not capsule_path.exists():
        console.print(f"[red]파일을 찾을 수 없습니다: {file_path}[/red]")
        raise typer.Exit(1)

    try:
        with open(capsule_path, "r", encoding="utf-8") as f:
            capsule_data = yaml.safe_load(f)

        capsule = CapsuleSpec(**capsule_data)
        errors = engine.validate_capsule_spec(capsule)

        if errors:
            console.print("[red]❌ 검증 실패:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)
        else:
            console.print(f"[green]✅ 캡슐 '{capsule.name}' 검증 성공![/green]")

            # 캡슐 정보 표시
            table = Table(title="캡슐 정보")
            table.add_column("속성", style="cyan")
            table.add_column("값", style="green")

            table.add_row("이름", capsule.name)
            table.add_row("타입", capsule.type.value)
            table.add_row("버전", capsule.version)
            table.add_row("규칙 수", str(len(capsule.rules)))
            table.add_row("파라미터 수", str(len(capsule.parameters)))
            table.add_row("태그", ", ".join(capsule.tags))

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ 파일 로드 실패: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def simulate(
    file_path: str,
    text: Optional[str] = typer.Option(None, help="입력 텍스트"),
    emotion: Optional[str] = typer.Option(None, help="감정 상태"),
    intensity: float = typer.Option(0.5, help="감정 강도 (0.0-1.0)"),
):
    """캡슐 시뮬레이션 실행"""
    capsule_path = Path(file_path)

    if not capsule_path.exists():
        console.print(f"[red]파일을 찾을 수 없습니다: {file_path}[/red]")
        raise typer.Exit(1)

    try:
        with open(capsule_path, "r", encoding="utf-8") as f:
            capsule_data = yaml.safe_load(f)

        capsule = CapsuleSpec(**capsule_data)
        context = ExecutionContext(text=text, emotion=emotion, intensity=intensity)

        console.print(f"🎭 캡슐 '{capsule.name}' 시뮬레이션 실행 중...")

        with Progress() as progress:
            task = progress.add_task("[green]시뮬레이션...", total=100)
            progress.update(task, advance=50)

            result = engine.simulate_capsule(capsule, context)
            progress.update(task, advance=50)

        # 결과 출력
        console.print(
            Panel(
                f"""
🎯 [bold]시뮬레이션 결과[/bold]

[yellow]트리거된 규칙:[/yellow] {len(result.triggered_rules)}개
{chr(10).join(f"  • {rule}" for rule in result.triggered_rules)}

[yellow]실행된 액션:[/yellow] {len(result.output_actions)}개
{chr(10).join(f"  • {action}" for action in result.output_actions)}

[yellow]감정 상태:[/yellow]
{chr(10).join(f"  • {k}: {v:.3f}" for k, v in result.emotional_state.items())}

[yellow]성능:[/yellow]
  • 실행 시간: {result.execution_time_ms:.2f}ms
  • 신뢰도: {result.confidence_score:.3f}
        """,
                title=f"'{capsule.name}' 결과",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]❌ 시뮬레이션 실패: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def register(file_path: str):
    """캡슐을 레지스트리에 등록"""
    capsule_path = Path(file_path)

    if not capsule_path.exists():
        console.print(f"[red]파일을 찾을 수 없습니다: {file_path}[/red]")
        raise typer.Exit(1)

    try:
        with open(capsule_path, "r", encoding="utf-8") as f:
            capsule_data = yaml.safe_load(f)

        capsule = CapsuleSpec(**capsule_data)

        # 검증
        errors = engine.validate_capsule_spec(capsule)
        if errors:
            console.print("[red]❌ 검증 실패로 등록할 수 없습니다:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)

        # 등록
        engine.registry.register_capsule(capsule)
        engine._save_registry()

        console.print(f"[green]✅ 캡슐 '{capsule.name}' 등록 완료![/green]")
        console.print(f"레지스트리: {engine.registry_path}")

    except Exception as e:
        console.print(f"[red]❌ 등록 실패: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    type_filter: Optional[str] = typer.Option(
        None, help="타입 필터 (emotion/signature/cognitive/hybrid)"
    )
):
    """등록된 캡슐 목록 조회"""
    filter_type = CapsuleType(type_filter) if type_filter else None
    capsules = engine.registry.list_capsules(type_filter=filter_type)

    if not capsules:
        console.print("[yellow]등록된 캡슐이 없습니다.[/yellow]")
        return

    table = Table(title=f"등록된 캡슐 목록 ({len(capsules)}개)")
    table.add_column("이름", style="cyan")
    table.add_column("타입", style="green")
    table.add_column("버전", style="yellow")
    table.add_column("규칙 수", style="blue")
    table.add_column("생성일", style="magenta")

    for capsule in capsules:
        table.add_row(
            capsule.name,
            capsule.type.value,
            capsule.version,
            str(len(capsule.rules)),
            capsule.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@app.command()
def info(name: str):
    """캡슐 상세 정보 조회"""
    capsule = engine.registry.get_capsule(name)

    if not capsule:
        console.print(f"[red]캡슐 '{name}'을 찾을 수 없습니다.[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"""
[bold cyan]{capsule.name}[/bold cyan] v{capsule.version}

[yellow]설명:[/yellow] {capsule.description}
[yellow]타입:[/yellow] {capsule.type.value}
[yellow]작성자:[/yellow] {capsule.author}
[yellow]생성일:[/yellow] {capsule.created_at.strftime("%Y-%m-%d %H:%M:%S")}

[yellow]태그:[/yellow] {", ".join(capsule.tags)}

[yellow]규칙 ({len(capsule.rules)}개):[/yellow]
{chr(10).join(f"  {i+1}. {rule.condition} → {rule.action} (우선순위: {rule.priority})" for i, rule in enumerate(capsule.rules))}

[yellow]파라미터 ({len(capsule.parameters)}개):[/yellow]
{chr(10).join(f"  • {k}: {v}" for k, v in capsule.parameters.items())}
    """,
            title="캡슐 정보",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    app()
