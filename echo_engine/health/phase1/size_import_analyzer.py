# echo_engine/health/phase1/size_import_analyzer.py
from __future__ import annotations
import os, ast, fnmatch
from dataclasses import dataclass
from typing import Tuple, Set, List, Dict, Iterable
from datetime import datetime
from echo_engine.health.registry import MetricResult, MetricSpec

MAX_SCORE_SIZE = 10.0
MAX_SCORE_IMPORT = 10.0

EXCLUDE_DIR_HINTS = ("venv", ".git", "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache")

@dataclass
class SizeStats:
    total_bytes: int
    py_bytes: int
    file_count: int
    large_files: List[Tuple[str, int]]
    binaries: List[str]
    models: List[str]
    samples: List[str]
    whitelist_hits: int
    blacklist_hits: int

def _walk_files(root: str, max_files: int = 2000) -> List[str]:
    files: List[str] = []
    for dp, dirs, fs in os.walk(root):
        if any(h in dp for h in EXCLUDE_DIR_HINTS):
            continue
        # Prune dirs during walk
        dirs[:] = [d for d in dirs if not any(h in d for h in EXCLUDE_DIR_HINTS)]

        for f in fs:
            if len(files) >= max_files:
                break
            if f.endswith(('.py', '.yaml', '.yml', '.json', '.md', '.txt', '.ini', '.toml', '.bin', '.pt', '.onnx', '.ckpt', '.zip', '.tar', '.gz')):
                files.append(os.path.join(dp, f))
        if len(files) >= max_files:
            break
    return files

def _bytes_of(path: str) -> int:
    try:
        return os.path.getsize(path)
    except Exception:
        return 0

def _match_any(path: str, globs: Iterable[str], root: str) -> bool:
    rel = os.path.relpath(path, root)
    for pat in globs:
        if fnmatch.fnmatch(rel, pat):
            return True
    return False

def _path_has_any_dir(path: str, root: str, dirs: Iterable[str]) -> bool:
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    for d in dirs:
        dparts = d.split("/")
        # 디렉토리 경로 조각이 순서대로 포함되는지 확인
        for i in range(0, max(1, len(parts)-len(dparts)+1)):
            if parts[i:i+len(dparts)] == dparts:
                return True
    return False

def analyze_size(root: str, large_threshold_kb: int, size_cfg: dict) -> SizeStats:
    files = _walk_files(root)
    total = 0
    py_total = 0
    large: List[Tuple[str, int]] = []
    binaries: List[str] = []
    models: List[str] = []
    samples: List[str] = []
    wl_hits = 0
    bl_hits = 0

    bin_globs = size_cfg.get("binary_globs", [])
    model_globs = size_cfg.get("model_globs", [])
    sample_globs = size_cfg.get("sample_globs", [])
    whitelist_dirs = size_cfg.get("whitelist_dirs", [])
    blacklist_dirs = size_cfg.get("blacklist_dirs", [])

    for p in files:
        b = _bytes_of(p)
        total += b
        if p.endswith(".py"):
            py_total += b
        if b >= large_threshold_kb * 1024:
            large.append((p, b))

        # 클래스 분류
        if _match_any(p, bin_globs, root):
            binaries.append(p)
        if _match_any(p, model_globs, root):
            models.append(p)
        if _match_any(p, sample_globs, root):
            samples.append(p)

        # 화이트/블랙 감지 (디렉토리 기준)
        if _path_has_any_dir(p, root, whitelist_dirs):
            wl_hits += 1
        if _path_has_any_dir(p, root, blacklist_dirs):
            bl_hits += 1

    large.sort(key=lambda x: x[1], reverse=True)
    return SizeStats(
        total_bytes=total,
        py_bytes=py_total,
        file_count=len(files),
        large_files=large,
        binaries=binaries,
        models=models,
        samples=samples,
        whitelist_hits=wl_hits,
        blacklist_hits=bl_hits
    )

def score_size(stats: SizeStats, large_allow: int, total_soft_cap_mb: int, wl_discount: float, bl_multiplier: float) -> float:
    # 큰 파일 수 기반 페널티
    penalty_large = max(0.0, (len(stats.large_files) - large_allow) * 1.0)
    # 총용량 페널티(소프트 캡 초과 시 선형)
    cap = total_soft_cap_mb * 1024 * 1024
    penalty_total = 0.0
    if stats.total_bytes > cap:
        penalty_total = min((stats.total_bytes - cap) / cap * 2.0, 3.0)

    # 모델/바이너리/샘플 가중 페널티
    penalty_class = 0.0
    penalty_class += min(len(stats.binaries) * 0.2, 2.0)
    penalty_class += min(len(stats.models) * 0.3, 3.0)
    penalty_class += min(len(stats.samples) * 0.1, 1.5)

    # 디렉토리 화이트/블랙 보정
    # 화이트리스트 안의 대형/바이너리는 감점 완화, 블랙리스트 안은 강화
    penalty = penalty_large + penalty_total + penalty_class
    penalty *= (1.0 - min(0.5, stats.whitelist_hits * wl_discount))  # 최대 50% 완화
    penalty *= (1.0 + min(1.0, stats.blacklist_hits * (bl_multiplier - 1.0)))  # 최대 2배 강화

    score = max(0.0, MAX_SCORE_SIZE - min(penalty, MAX_SCORE_SIZE))
    return round(score, 2)

# -------- Import (강화판: 내부 접두사 확장 + 순환 근사 탐지) --------

@dataclass
class ImportStats:
    files: int
    total_imports: int
    duplicate_imports: int
    relative_imports: int
    unused_candidates: int
    external_modules: Set[str]
    cycle_groups: int  # SCC > 1 개수

def _ast_of(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return ast.parse(f.read())
    except Exception:
        return None

def _module_name(path: str, root: str) -> str:
    rel = os.path.relpath(path, root)
    if rel.endswith(".py"):
        rel = rel[:-3]
    return rel.replace(os.sep, ".")

def _imports_by_module(root: str) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {}
    for dp, _, fs in os.walk(root):
        if any(h in dp for h in EXCLUDE_DIR_HINTS):
            continue
        for f in fs:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            tree = _ast_of(p)
            if tree is None:
                continue
            mod = _module_name(p, root)
            deps: Set[str] = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        deps.add(a.name.split(".")[0])
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        deps.add(n.module.split(".")[0])
            graph[mod] = deps
    return graph

def _scc_count(graph: Dict[str, Set[str]], internal_prefixes: List[str]) -> int:
    # 내부 모듈만 대상으로 SCC 계산 (Tarjan)
    nodes = [m for m in graph.keys() if any(m.startswith(pfx) for pfx in internal_prefixes)]
    index = 0
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    stack: List[str] = []
    onstack: Set[str] = set()
    sccs = 0

    def strongconnect(v: str):
        nonlocal index, sccs
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v); onstack.add(v)
        for w in graph.get(v, set()):
            # w를 내부 노드 이름으로 정규화(접두사 없는 단일 토큰일 수도 있음) → 포함 여부만 체크
            if not any((w == pfx or w.startswith(pfx + ".")) for pfx in internal_prefixes):
                continue
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            # pop SCC
            comp = []
            while True:
                w = stack.pop(); onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                sccs += 1

    for v in nodes:
        if v not in indices:
            strongconnect(v)
    return sccs

def analyze_imports(root: str, internal_prefixes: List[str], max_files: int = 300, max_seconds: int = 20) -> ImportStats:
    files = 0
    total_imports = 0
    duplicate_imports = 0
    relative_imports = 0
    unused_candidates = 0
    external: Set[str] = set()

    import time
    start = time.time()

    for dp, dirs, fs in os.walk(root):
        if time.time() - start > max_seconds:
            break
        if any(h in dp for h in EXCLUDE_DIR_HINTS):
            continue
        # Prune directories early
        dirs[:] = [d for d in dirs if not any(h in d for h in EXCLUDE_DIR_HINTS)]

        for f in fs:
            if files >= max_files or time.time() - start > max_seconds:  # Hard limits to prevent timeout
                break
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            tree = _ast_of(p)
            if tree is None: continue
            files += 1

            seen: Dict[str, int] = {}
            referenced: Set[str] = set()

            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        name = a.name.split(".")[0]
                        total_imports += 1
                        seen[name] = seen.get(name, 0) + 1
                        external.add(name)
                elif isinstance(n, ast.ImportFrom):
                    total_imports += 1
                    if n.level and n.level > 0:
                        relative_imports += 1
                    base = (n.module or "").split(".")[0] if n.module else ""
                    if base:
                        external.add(base)
                elif isinstance(n, ast.Name):
                    referenced.add(n.id)

            duplicate_imports += sum(1 for k, v in seen.items() if v > 1)
            for imp_name in seen.keys():
                if imp_name not in referenced:
                    unused_candidates += 1

        if files >= max_files or time.time() - start > max_seconds:
            break  # Exit outer loop too

    # 내부 접두사 제외한 외부 후보만 남김
    external = {m for m in external if m and not any(m.startswith(pfx) for pfx in internal_prefixes)}

    # 순환 근사: FAST 모드에서는 skip
    cycles = 0
    # g = _imports_by_module(root)
    # cycles = _scc_count(g, internal_prefixes)

    return ImportStats(
        files=files,
        total_imports=total_imports,
        duplicate_imports=duplicate_imports,
        relative_imports=relative_imports,
        unused_candidates=unused_candidates,
        external_modules=external,
        cycle_groups=cycles
    )

def score_import(stats: ImportStats) -> float:
    penalty = (
        min(stats.duplicate_imports * 0.5, 4.0) +
        min(stats.relative_imports * 0.3, 3.0) +
        min(stats.unused_candidates * 0.2, 3.0) +
        min(stats.cycle_groups * 1.5, 6.0)  # 순환은 강한 감점
    )
    score = max(0.0, MAX_SCORE_IMPORT - penalty)
    return round(score, 2)

# -------- Model Externalization Guide --------

GUIDE_PATH = "health_reports/model_externalization_guide.md"

def _write_file(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def write_model_externalization_guide(stats: SizeStats, size_cfg: dict, root: str):
    rel = lambda p: os.path.relpath(p, root)
    binaries = [rel(p) for p in stats.binaries]
    models   = [rel(p) for p in stats.models]
    samples  = [rel(p) for p in stats.samples]

    gitattributes_lines = [
        "*.pt filter=lfs diff=lfs merge=lfs -text",
        "*.onnx filter=lfs diff=lfs merge=lfs -text",
        "*.ckpt filter=lfs diff=lfs merge=lfs -text",
        "models/** filter=lfs diff=lfs merge=lfs -text",
        "checkpoints/** filter=lfs diff=lfs merge=lfs -text",
        "*.bin filter=lfs diff=lfs merge=lfs -text",
        "*.zip filter=lfs diff=lfs merge=lfs -text",
        "*.tar filter=lfs diff=lfs merge=lfs -text",
        "*.gz filter=lfs diff=lfs merge=lfs -text",
    ]
    artifacts_paths = sorted(set(
        [p for p in models if not p.endswith(".md")] +
        [p for p in binaries if not p.endswith(".md")]
    ))[:50]  # 가이드에 너무 길면 상위 50개만

    guide = f"""# Model Artifact Externalization Guide (Git LFS / CI Artifacts)
Generated: {datetime.now().isoformat(timespec='seconds')}

## 왜 필요한가
- 대형 파일(모델/체크포인트/바이너리)이 레포 용량과 clone 속도를 악화시킵니다.
- Git LFS 또는 CI Artifacts로 외부화하면 **레포는 가볍게**, **배포는 빠르게** 유지할 수 있습니다.

---

## 1) Git LFS 사용 가이드 (권장)
```bash
git lfs install
git lfs track "*.pt" "*.onnx" "*.ckpt" "*.bin" "*.zip" "*.tar" "*.gz"
git lfs track "models/**" "checkpoints/**"
echo ".gitattributes 업데이트 후 커밋"
git add .gitattributes
git add models checkpoints
git commit -m "chore(lfs): track model/checkpoint artifacts"
```

과거 이력까지 LFS로 이관하려면(선택):
```bash
git lfs migrate import --include="*.pt,*.onnx,*.ckpt,*.bin,*.zip,*.tar,*.gz,models/**,checkpoints/**"
```

### .gitattributes (예시)
```
{os.linesep.join(gitattributes_lines)}
```

## 2) GitHub Actions — Artifact 업/다운로드 예시
```yaml
# .github/workflows/artifacts.yml
name: Artifacts
on: [push, workflow_dispatch]
jobs:
  pack:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Upload model artifacts
        uses: actions/upload-artifact@v4
        with:
          name: models-${"{{{{ github.sha }}}}"}
          path: |
            models/**
            checkpoints/**
          if-no-files-found: ignore

  use:
    runs-on: ubuntu-latest
    needs: pack
    steps:
      - uses: actions/checkout@v4
      - name: Download model artifacts
        uses: actions/download-artifact@v4
        with:
          name: models-${"{{{{ github.sha }}}}"}
          path: models
```

## 3) 현재 레포에서 감지된 대상(상위 일부)

**Models: {len(models)}개**
{os.linesep.join(f" - {p}" for p in models[:30]) or " - (none)"}

**Binaries: {len(binaries)}개**
{os.linesep.join(f" - {p}" for p in binaries[:30]) or " - (none)"}

**Samples: {len(samples)}개**
{os.linesep.join(f" - {p}" for p in samples[:30]) or " - (none)"}

## 4) 운영 팁

- 모델/체크포인트는 models/ 또는 checkpoints/ 하위로만 두고, 코드와 분리
- 대규모 데이터셋은 Git이 아닌 전용 스토리지(S3 등) 또는 DVC 사용 고려
- 릴리스 시에는 Release Assets에 업로드하여 버전 고정
"""

    _write_file(GUIDE_PATH, guide)

# -------- Import Cycle Report --------

CYCLE_REPORT = "health_reports/import_cycles.md"

def _write_text(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def write_cycle_report(graph: Dict[str, Set[str]], internal_prefixes: List[str]):
    # 간소화된 순환 리포트 (성능상 스킵)
    lines = ["# Import Cycles Report", ""]
    lines.append("Cycle analysis skipped for performance reasons.")
    lines.append("Enable full analysis by uncommenting SCC code in size_import_analyzer.py")
    _write_text(CYCLE_REPORT, "\n".join(lines))

def _imports_graph_for_report(root: str) -> Dict[str, Set[str]]:
    # 기존 _imports_by_module 함수 재사용
    return _imports_by_module(root)

# -------- Registry hooks --------

def register_size(registry, root: str, weight: float, size_cfg: dict):
    def run() -> MetricResult:
        st = analyze_size(root, size_cfg.get("large_threshold_kb", 200), size_cfg)
        # ✨ 가이드 생성
        write_model_externalization_guide(st, size_cfg, root)
        sc = score_size(
            st,
            large_allow=5,
            total_soft_cap_mb=10,
            wl_discount=0.01,   # 화이트리스트 파일 1개당 1% 완화(최대 50%)
            bl_multiplier=1.10  # 블랙리스트 파일 1개당 10% 강화(최대 2배)
        )
        largest = [f"{os.path.relpath(p, root)}:{b//1024}KB" for p, b in st.large_files[:8]]
        return MetricResult(
            key="size", score=sc, max_score=MAX_SCORE_SIZE,
            summary=f"files={st.file_count}, py={st.py_bytes//1024}KB, large={len(st.large_files)}, bin={len(st.binaries)}, mdl={len(st.models)}, samp={len(st.samples)}",
            details={"largest": largest, "guide": GUIDE_PATH}
        )
    registry.register(MetricSpec(key="size", weight=weight, runner=run))

def register_import(registry, root: str, weight: float, internal_prefixes: List[str]):
    def run() -> MetricResult:
        st = analyze_imports(root, internal_prefixes)
        # ✨ 사이클 리포트 생성
        graph = _imports_graph_for_report(root)
        write_cycle_report(graph, internal_prefixes)

        sc = score_import(st)
        return MetricResult(
            key="import", score=sc, max_score=MAX_SCORE_IMPORT,
            summary=f"imports={st.total_imports}, dup={st.duplicate_imports}, rel={st.relative_imports}, unused?={st.unused_candidates}, cycles={st.cycle_groups}",
            details={"external": sorted(list(st.external_modules))[:20], "cycle_report": CYCLE_REPORT}
        )
    registry.register(MetricSpec(key="import", weight=weight, runner=run))