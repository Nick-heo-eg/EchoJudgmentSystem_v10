import shutil, subprocess
from echo_engine.health.registry import MetricResult

MAX_SCORE = 10.0


def _run(cmd: list) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False


def run_style(
    black_args=".", isort_args=".", flake8_args=".", mypy_args="."
) -> MetricResult:
    tools = {
        "black": black_args,
        "isort": isort_args,
        "flake8": flake8_args,
        "mypy": mypy_args,
    }
    available = {t: bool(shutil.which(t)) for t in tools}
    ok = 0
    ran = 0
    for t, args in tools.items():
        if not available[t]:
            continue
        ran += 1
        if t in ("black", "isort"):
            ok += 1 if _run([t, args]) else 0
        elif t == "flake8":
            ok += 1 if _run([t, args]) else 0
        elif t == "mypy":
            ok += 1 if _run([t, args]) else 0
    # 도구 모두 설치/정상: 10점, 일부만: 비례
    score = 0.0 if ran == 0 else (ok / ran) * MAX_SCORE
    return MetricResult(
        key="style",
        score=round(score, 2),
        max_score=MAX_SCORE,
        summary=f"tools={ran}, pass={ok}",
    )


def register(registry, cfg: dict, weight: float):
    from echo_engine.health.registry import MetricSpec

    style = cfg.get("options", {}).get("style", {})
    registry.register(
        MetricSpec(
            key="style",
            weight=weight,
            runner=lambda: run_style(
                style.get("black_args", "."),
                style.get("isort_args", "."),
                style.get("flake8_args", "."),
                style.get("mypy_args", "."),
            ),
        )
    )
