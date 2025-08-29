import os, re, subprocess, shutil
from echo_engine.health.registry import MetricResult

MAX_SCORE = 10.0
PATTERN = re.compile(r"(TODO|FIXME|HACK)\b[: ]?(.*)")


def scan_debt(root: str, max_files: int = 800):
    findings = []
    file_count = 0
    EXCLUDE_DIRS = (
        "venv",
        ".git",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        "data",
        "logs",
        "health_reports",
        ".vscode",
        ".idea",
    )

    for dirpath, dirs, files in os.walk(root):
        if any(h in dirpath for h in EXCLUDE_DIRS):
            continue
        # Prune directories
        dirs[:] = [d for d in dirs if not any(h in d for h in EXCLUDE_DIRS)]

        for f in files:
            if file_count >= max_files:
                break
            if not f.endswith(
                (".py", ".md", ".yaml", ".yml", ".json", ".ini", ".toml")
            ):
                continue
            file_count += 1
            p = os.path.join(dirpath, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    if len(content) > 100000:  # Skip very large files
                        continue
                    for i, line in enumerate(content.split("\n"), start=1):
                        m = PATTERN.search(line)
                        if m:
                            findings.append((p, i, m.group(1), m.group(2).strip()))
                            if (
                                len(findings) >= 200
                            ):  # Limit findings to prevent excessive processing
                                return findings
            except Exception:
                pass
        if file_count >= max_files:
            break
    return findings


def write_md(findings, out_file="health_reports/health_issues.md"):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# Health Issues (TODO/FIXME/HACK)\n\n")
        for p, i, tag, msg in findings:
            f.write(f"- [{tag}] {p}:{i} — {msg}\n")


def create_github_issues(findings):
    gh = shutil.which("gh")
    if not gh:
        return False
    # 간단하게 상위 20개만 등록
    for p, i, tag, msg in findings[:20]:
        title = f"[{tag}] {os.path.basename(p)}:{i} — {msg[:60]}"
        body = f"Auto-filed by Echo Health v2.5\n\nFile: {p}\nLine: {i}\nTag: {tag}\nMsg: {msg}"
        try:
            subprocess.run(
                ["gh", "issue", "create", "-t", title, "-b", body], check=False
            )
        except Exception:
            pass
    return True


def run_debt(root: str, auto_issue=False) -> MetricResult:
    findings = scan_debt(root)
    write_md(findings)
    # 점수: 항목이 적을수록↑
    penalty = min(len(findings) * 0.15, 9.0)
    score = max(0.0, MAX_SCORE - penalty)
    if auto_issue and findings:
        create_github_issues(findings)
    return MetricResult(
        key="debt",
        score=round(score, 2),
        max_score=MAX_SCORE,
        summary=f"found={len(findings)}",
        details={"file": "health_reports/health_issues.md"},
    )


def register(registry, root: str, weight: float, auto_issue: bool = False):
    from echo_engine.health.registry import MetricSpec

    registry.register(
        MetricSpec(key="debt", weight=weight, runner=lambda: run_debt(root, auto_issue))
    )
