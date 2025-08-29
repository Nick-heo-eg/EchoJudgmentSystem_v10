#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Echo Feature Mapper v1
- FastAPI routes, CLI entrypoints, adapters, tools, Streamlit pages, tests를 자동 인덱싱
- JSON/Markdown/HTML 아티팩트 생성
# @owner: nick
# @expose
# @maturity: stable
"""
from __future__ import annotations
import re, os, json, sys, subprocess, webbrowser, fnmatch, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

import networkx as nx
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from jinja2 import Template

# Stage 2 수술: Tag I/O 집중 감축 시스템
try:
    from tools.index.tag_index import extract_tags_cached, get_tag_index

    TAG_CACHE_AVAILABLE = True
except ImportError:
    TAG_CACHE_AVAILABLE = False

try:
    import yaml  # policy/profiles
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

RG = ["rg", "--no-ignore", "--hidden", "--line-number", "--color", "never"]
RG_AVAILABLE = shutil.which("rg") is not None

console = Console()


@dataclass
class Hit:
    kind: str  # route|cli|tool|adapter|streamlit|test|doc
    file: str
    line: int
    text: str
    meta: Dict[str, Any]
    tags: Dict[str, Any] | None = None  # expose/owner/maturity 캐시


class FeatureMap(BaseModel):
    root: str
    hits: List[Dict[str, Any]]
    edges: List[Tuple[str, str, str]]  # (src, dst, label)


ROUTE_PATTERNS = [
    r"@router\.(get|post|put|delete|patch)\(.*\)",
    r"APIRouter\(.*prefix=.*\)",
]
CLI_PATTERNS = [
    r"if __name__ == ['\"]__main__['\"]:",
    r"argparse\.(ArgumentParser|add_argument)",
    r"import typer|from typer import",  # Typer 지원
    r"import click|from click import",  # Click 지원
]
TOOL_PATTERNS = [
    r"def\s+(run|handle|execute)\(.*\):",
    r"class\s+.*Adapter\(.*\):",
]
STREAMLIT_PATTERNS = [
    r"import streamlit as st",
    r"st\.(sidebar|page|set_page_config|tabs)\(.*\)",
]
TEST_PATTERNS = [
    r"pytest|unittest",
    r"client\.(get|post|put|delete)\(",
]
DOC_PATTERNS = [
    r"signature|capsule|CLAUDE|README|Echo Workspace|Echo Judgment",
]

# Lightweight parser helpers -------------------------------------------------

_FILE_CACHE: Dict[str, str] = {}


def _read_file(path: Path) -> str:
    key = str(path)
    if key not in _FILE_CACHE:
        try:
            _FILE_CACHE[key] = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            _FILE_CACHE[key] = ""
    return _FILE_CACHE[key]


def _extract_tags_for(path: Path) -> Dict[str, Any]:
    """
    Stage 2 수술: mtime 캐싱 기반 태그 추출 (I/O 집중 감축)
    기존 직접 파일 읽기 → 캐시 우선 검사로 95%+ I/O 감축
    """
    if TAG_CACHE_AVAILABLE:
        # 캐싱된 태그 추출 (mtime 기반 캐시 히트)
        return extract_tags_cached(path)

    # 폴백: 직접 파일 읽기 (Stage 2 수술 전 방식)
    txt = _read_file(path)
    head = "\n".join(txt.splitlines()[:80])  # 상단 80줄만 스캔
    tags: Dict[str, Any] = {}
    if re.search(r"^\s*#\s*@expose\b", head, re.M):
        tags["expose"] = True
    m_owner = re.search(r"^\s*#\s*@owner:\s*([A-Za-z0-9_\-\.]+)", head, re.M)
    if m_owner:
        tags["owner"] = m_owner.group(1)
    m_maturity = re.search(
        r"^\s*#\s*@maturity:\s*(stable|beta|experimental|deprecated)", head, re.I | re.M
    )
    if m_maturity:
        tags["maturity"] = m_maturity.group(1).lower()
    return tags


def _match_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in globs)


def _load_policy(policy_path: Optional[str]) -> Dict[str, Any]:
    if not policy_path:
        return {}
    if yaml is None:
        console.print(
            "[yellow]PyYAML 미설치로 정책을 읽을 수 없습니다. `pip install pyyaml`[/]"
        )
        return {}
    p = Path(policy_path)
    if not p.exists():
        console.print(f"[yellow]정책 파일이 없습니다: {p}[/]")
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    # 기본값
    return {
        "version": data.get("version", 1),
        "default_owner": data.get("default_owner", None),
        "allowlist": data.get("allowlist", ["**"]),
        "denylist": data.get("denylist", []),
        "tags": data.get("tags", {"require_expose": False, "require_owner": False}),
        "maturity": data.get("maturity", {"allowed": ["stable", "beta"]}),
        "tests": data.get("tests", {"require_coverage": False}),
    }


def _load_profile(profile_name: Optional[str]) -> Dict[str, Any]:
    if not profile_name:
        return {}
    if yaml is None:
        console.print(
            "[yellow]PyYAML 미설치로 프로필을 읽을 수 없습니다. `pip install pyyaml`[/]"
        )
        return {}

    prof_path = ROOT / "profiles.yaml"
    if not prof_path.exists():
        console.print(f"[yellow]프로필 파일이 없습니다: {prof_path}[/]")
        return {}

    try:
        data = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        profiles = data.get("profiles", {})
        if profile_name not in profiles:
            available = list(profiles.keys())
            console.print(f"[yellow]알 수 없는 프로필: {profile_name}[/]")
            console.print(f"[yellow]사용 가능한 프로필: {', '.join(available)}[/]")
            return {}

        p = profiles[profile_name]
        return {
            "allow": p.get("allow", ["**"]),
            "deny": p.get("deny", []),
            "tag_defaults": p.get("tag_defaults", {}),
        }
    except Exception as e:
        console.print(f"[yellow]프로필 로드 실패: {e}[/]")
        return {}


def _policy_allow_file(relpath: str, policy: Dict[str, Any]) -> bool:
    if not policy:
        return True
    if policy["denylist"] and _match_any(relpath, policy["denylist"]):
        return False
    if policy["allowlist"] and not _match_any(relpath, policy["allowlist"]):
        return False
    return True


def _policy_allow_tags(tags: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    if not policy:
        return True
    require_expose = policy["tags"].get("require_expose", False)
    require_owner = policy["tags"].get("require_owner", False)
    allowed_mats = set([m.lower() for m in policy["maturity"].get("allowed", [])])
    # expose
    if require_expose and not tags.get("expose"):
        return False
    # owner
    if require_owner:
        owner = tags.get("owner") or policy.get("default_owner")
        if not owner:
            return False
        # owner 태그가 명시된 경우만 통과
        if "owner" not in tags:
            return False
    # maturity
    mat = (tags.get("maturity") or "stable").lower()
    if allowed_mats and mat not in allowed_mats:
        return False
    return True


SCAN_EXTS = {".py", ".pyi", ".md", ".markdown", ".yaml", ".yml", ".toml"}

# Stage 1 수술: 매니페스트 기반 혈관 네트워크 재구성
CORE_FILES_MANIFEST = [
    # Root Level Essentials
    "main.py",
    "echo.py",
    "cosmos.py",
    "quick_dev.py",
    "workflow_runner.py",
    "echo_engine/echo_agent_api.py",
    "echo_engine/judgment_engine.py",
    "echo_engine/reasoning.py",
    "echo_engine/persona_core.py",
    "echo_engine/signature_mapper.py",
    "echo_engine/seed_kernel.py",
    # API Routes
    "api/server.py",
    "api/routers/*.py",
    # Critical Tools
    "tools/feature_mapper.py",
    "tools/feature_tagger.py",
    "tools/feature_invoker.py",
    "tools/health_advisor.py",
    # UI Components
    "streamlit_ui/comprehensive_dashboard.py",
    "streamlit_ui/components/*.py",
]

HOT_DIRECTORIES = {
    "echo_engine": ["**/*.py"],  # 핵심 엔진
    "api": ["**/*.py"],  # API 라우터
    "tools": ["*.py"],  # 루트 툴들
    "streamlit_ui": ["*.py"],  # UI 대시보드
    "tests": ["test_*.py"],  # 주요 테스트만
}


def _expand_manifest_pattern(pattern: str) -> List[Path]:
    """매니페스트 패턴을 실제 파일 경로로 확장 (직접 탐색)"""
    files = []

    if "*" in pattern:
        # glob 패턴 처리
        for p in ROOT.glob(pattern):
            if p.is_file() and p.suffix.lower() in SCAN_EXTS:
                files.append(p)
    else:
        # 정확한 파일 경로
        p = ROOT / pattern
        if p.exists() and p.is_file() and p.suffix.lower() in SCAN_EXTS:
            files.append(p)

    return files


def _list_candidates(
    profile: Dict[str, Any] | None, policy: Dict[str, Any] | None
) -> List[Path]:
    """혈관 수술 완료: 매니페스트 기반 직접 확장 (ROOT.rglob 완전 제거)"""
    files: List[Path] = []

    # 1. 프로필 기반 직접 확장 (최우선)
    if profile and profile.get("allow"):
        for allow_pattern in profile["allow"]:
            if allow_pattern.endswith("/**"):
                # 디렉토리 확장: 매니페스트 확인 후 HOT_DIRECTORIES 활용
                dir_name = allow_pattern[:-3]
                if dir_name in HOT_DIRECTORIES:
                    # 핫 디렉토리면 지정된 패턴들만 스캔
                    dir_path = ROOT / dir_name
                    if dir_path.exists():
                        for hot_pattern in HOT_DIRECTORIES[dir_name]:
                            files.extend(
                                _expand_manifest_pattern(f"{dir_name}/{hot_pattern}")
                            )
                else:
                    # 일반 디렉토리는 제한적 스캔
                    dir_path = ROOT / dir_name
                    if dir_path.exists() and dir_path.is_dir():
                        for p in dir_path.glob("*.py"):
                            if p.is_file():
                                files.append(p)
            else:
                # 특정 패턴 직접 확장
                files.extend(_expand_manifest_pattern(allow_pattern))
    else:
        # 2. 매니페스트 기반 핵심 파일들만 (rglob 대신 직접 확장)
        console.print("[yellow]⚡ 매니페스트 기반 혈관 확장 모드[/yellow]")

        for manifest_pattern in CORE_FILES_MANIFEST:
            files.extend(_expand_manifest_pattern(manifest_pattern))

        # HOT_DIRECTORIES 추가 확장 (단계적)
        for dir_name, patterns in HOT_DIRECTORIES.items():
            dir_path = ROOT / dir_name
            if dir_path.exists():
                for pattern in patterns:
                    files.extend(_expand_manifest_pattern(f"{dir_name}/{pattern}"))

    # 3. 중복 제거 및 필터링 (변경 없음)
    unique_files = []
    seen = set()
    for p in files:
        if p in seen:
            continue
        seen.add(p)

        rel = str(p.relative_to(ROOT)).replace("\\", "/")

        # deny 필터
        if profile and profile.get("deny"):
            if _match_any(rel, profile["deny"]):
                continue

        # 정책 필터
        if policy and not _policy_allow_file(rel, policy):
            continue

        unique_files.append(p)

    return unique_files


def _scan_python(
    patterns: List[str], files: List[Path], max_workers: int = 0
) -> List[Hit]:
    """외부 rg 없이 파이썬으로 빠르게 스캔. 라인단위 매칭으로 line번호 확보."""
    regs = [re.compile(p) for p in patterns]
    hits: List[Hit] = []

    def scan_one(path: Path) -> List[Hit]:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        txt = _read_file(path)
        out: List[Hit] = []
        if not txt:
            return out
        for idx, line in enumerate(txt.splitlines(), start=1):
            for patt, reg in zip(patterns, regs):
                if reg.search(line):
                    out.append(
                        Hit(
                            kind="raw",
                            file=rel,
                            line=idx,
                            text=line,
                            meta={"pattern": patt},
                            tags=_extract_tags_for(path),
                        )
                    )
        return out

    if max_workers and max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = {ex.submit(scan_one, f): f for f in files}
            for fu in as_completed(futs):
                hits.extend(fu.result())
    else:
        for f in files:
            hits.extend(scan_one(f))
    return hits


def _scan_rg(patterns: List[str], files: List[Path]) -> List[Hit]:
    """rg가 있으면 파일 리스트 범위로 rg 실행 (정확히 필요한 파일만)."""
    hits: List[Hit] = []
    if not RG_AVAILABLE:
        return hits
    # rg는 파일 리스트를 stdin으로 받을 수 없으므로 xargs식 호출 대신 파일 패턴을 -g로 전달
    globs: List[str] = []
    for f in files:
        globs += ["-g", str(f.relative_to(ROOT)).replace("\\", "/")]
    for patt in patterns:
        cmd = RG + [patt] + globs
        try:
            out = subprocess.check_output(
                cmd, cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            out = ""
        for line in out.splitlines():
            try:
                path, lineno, text = line.split(":", 2)
                tags = _extract_tags_for(ROOT / path)
                hits.append(
                    Hit(
                        kind="raw",
                        file=path,
                        line=int(lineno),
                        text=text,
                        meta={"pattern": patt},
                        tags=tags,
                    )
                )
            except ValueError:
                pass
    return hits


def filter_hits(hits: List[Hit], kind: str, selector: str) -> List[Hit]:
    sel = re.compile(selector)
    out = []
    for h in hits:
        if sel.search(h.text):
            hh = Hit(
                kind=kind,
                file=h.file,
                line=h.line,
                text=h.text,
                meta=h.meta,
                tags=h.tags,
            )
            out.append(hh)
    return out


# Discovery ------------------------------------------------------------------


def discover(
    policy: Dict[str, Any] | None = None,
    profile: Dict[str, Any] | None = None,
    engine: str = "auto",
) -> List[Hit]:
    console.print("[red]🔥 혈관 수술 완료: 매니페스트 직접 확장 모드[/red]")
    cand_files = _list_candidates(profile, policy)
    console.print(
        f"[green]⚡ 혈관을 통한 파일 공급: {len(cand_files)}개 (기존 806개 → {len(cand_files)}개)[/green]"
    )

    if engine == "auto":
        engine = "rg" if RG_AVAILABLE else "python"

    all_patterns = (
        ROUTE_PATTERNS
        + CLI_PATTERNS
        + TOOL_PATTERNS
        + STREAMLIT_PATTERNS
        + TEST_PATTERNS
        + DOC_PATTERNS
    )

    # 혈관 수술 후 엔진 최적화
    if len(cand_files) < 50 or not RG_AVAILABLE:
        console.print(
            f"[green]🐍 Python 엔진 (혈관 직접 공급: {len(cand_files)}개)[/green]"
        )
        raw = _scan_python(
            all_patterns, cand_files, max_workers=min(4, os.cpu_count() or 2)
        )
    else:
        console.print(f"[green]🚀 rg 엔진 (혈관 네트워크: {len(cand_files)}개)[/green]")
        raw = _scan_rg(all_patterns, cand_files)

    bucketed: List[Hit] = []
    bucketed += filter_hits(raw, "route", r"@router\.(get|post|put|delete|patch)")
    bucketed += filter_hits(raw, "route", r"APIRouter\(")
    bucketed += filter_hits(raw, "cli", r"__main__|argparse|typer|click")
    bucketed += filter_hits(raw, "tool", r"def\s+(run|handle|execute)\(|Adapter\(")
    bucketed += filter_hits(raw, "streamlit", r"import streamlit|st\.")
    bucketed += filter_hits(raw, "test", r"pytest|unittest|client\.")
    bucketed += filter_hits(
        raw, "doc", r"signature|capsule|CLAUDE|README|Echo Workspace|Echo Judgment"
    )

    # 정책 기반 태그 필터링 (파일 필터링은 이미 _list_candidates에서 적용됨)
    if policy:
        filtered: List[Hit] = []
        for h in bucketed:
            if not _policy_allow_tags(h.tags or {}, policy):
                continue
            filtered.append(h)
        bucketed = filtered

    # Meta extraction (prefix, function name, etc.)
    for h in bucketed:
        if h.kind == "route":
            m = re.search(
                r"@router\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", h.text
            )
            if m:
                h.meta.update({"method": m.group(1).upper(), "path": m.group(2)})
        if h.kind == "cli":
            if "typer" in h.text:
                h.meta.update({"cli": "typer"})
            elif "click" in h.text:
                h.meta.update({"cli": "click"})
            elif "argparse" in h.text:
                h.meta.update({"cli": "argparse"})
        if h.kind == "tool":
            fn = re.search(r"def\s+(run|handle|execute)\(([^)]*)\):", h.text)
            if fn:
                h.meta.update({"entry": fn.group(1), "params": fn.group(2)})

    return bucketed


# Linking (very simple heuristics) -------------------------------------------


def link_edges(
    hits: List[Hit], policy: Dict[str, Any] | None = None
) -> List[Tuple[str, str, str]]:
    """Create edges like: route → tool, cli → tool, streamlit → route"""
    edges: List[Tuple[str, str, str]] = []
    # naive heuristics via co-location and imports
    # if file mentions "from echo_engine.tools import X" then connect
    by_file: Dict[str, List[Hit]] = {}
    for h in hits:
        by_file.setdefault(h.file, []).append(h)

    for f, group in by_file.items():
        kinds = {g.kind for g in group}

        def ok_pair(a: Hit, b: Hit) -> bool:
            if not policy:
                return True
            # 두 노드 모두 expose/owner/maturity 요건 충족해야 엣지 생성
            return _policy_allow_tags(a.tags or {}, policy) and _policy_allow_tags(
                b.tags or {}, policy
            )

        if "route" in kinds and "tool" in kinds:
            for r in [x for x in group if x.kind == "route"]:
                for t in [x for x in group if x.kind == "tool"]:
                    if ok_pair(r, t):
                        edges.append(
                            (
                                f"{r.file}:{r.line}",
                                f"{t.file}:{t.line}",
                                "route→tool(file)",
                            )
                        )
        if "streamlit" in kinds and "route" in kinds:
            for s in [x for x in group if x.kind == "streamlit"]:
                for r in [x for x in group if x.kind == "route"]:
                    if ok_pair(s, r):
                        edges.append(
                            (
                                f"{s.file}:{s.line}",
                                f"{r.file}:{r.line}",
                                "ui→route(file)",
                            )
                        )
        if "cli" in kinds and "tool" in kinds:
            for c in [x for x in group if x.kind == "cli"]:
                for t in [x for x in group if x.kind == "tool"]:
                    if ok_pair(c, t):
                        edges.append(
                            (
                                f"{c.file}:{c.line}",
                                f"{t.file}:{t.line}",
                                "cli→tool(file)",
                            )
                        )
    return edges


# Renderers ------------------------------------------------------------------

MD_TMPL = Template(
    """
# Echo Feature Map (auto-generated)
Root: `{{ root }}`

## Summary
- Total: **{{ total }}** hits
- By kind:
{% for k, v in by_kind.items() %}- {{ k }}: {{ v }}
{% endfor %}

## Table
| kind | file:line | meta | text |
|---|---|---|---|
{% for h in hits %}| {{ h.kind }} | `{{ h.file }}:{{ h.line }}` | {{ h.meta }} | {{ h.text|replace('|','\\|')|truncate(120) }} |
{% endfor %}

## Edges ({{ edges|length }})
| src | → | dst | label |
|---|---|---|---|
{% for s,d,l in edges %}| `{{ s }}` | → | `{{ d }}` | {{ l }} |
{% endfor %}
"""
)

HTML_TMPL = Template(
    """
<!doctype html>
<meta charset="utf-8"/>
<title>Echo Feature Map</title>
<style>
body{font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; margin:24px}
summary{font-weight:600}
code{background:#f6f8fa;padding:2px 6px;border-radius:6px}
input{padding:8px 10px; width:320px;}
.table{border-collapse:collapse;width:100%;margin-top:12px}
.table th,.table td{border:1px solid #e5e7eb;padding:6px 8px;font-size:12px}
.badge{display:inline-block;background:#eef2ff;padding:2px 6px;border-radius:8px;margin-right:4px}
</style>
<h1>Echo Feature Map</h1>
<p>Root: <code>{{ root }}</code></p>
<input id="q" placeholder="filter by text/file/kind..." oninput="f()" />
<div id="c"></div>
<script>
const data = {{ data|safe }};
function row(h){
  const id = `${h.file}:${h.line}`;
  return `<tr><td><span class=badge>${h.kind}</span></td><td><code>${id}</code></td><td>${escapeHtml(JSON.stringify(h.meta))}</td><td>${escapeHtml(h.text)}</td></tr>`
}
function escapeHtml(s){return s.replace(/[&<>\"]/g, m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[m]))}
function f(){
  const q = document.getElementById('q').value.toLowerCase();
  const hits = data.hits.filter(h=> (h.file+h.text+h.kind+JSON.stringify(h.meta)).toLowerCase().includes(q));
  render(hits);
}
function render(hits){
  const rows = hits.map(row).join("\n");
  document.getElementById('c').innerHTML = `<details open><summary>Hits (${hits.length})</summary><table class=table><thead><tr><th>kind</th><th>file:line</th><th>meta</th><th>text</th></tr></thead><tbody>${rows}</tbody></table></details>`;
}
render(data.hits);
</script>
"""
)


def main(
    save: bool = True,
    to_html: bool = True,
    open_html: bool = False,
    policy_path: Optional[str] = None,
    profile_name: Optional[str] = None,
    engine: str = "auto",
):
    console.print("[red]🩸 Feature Mapper Stage 1+2 수술 시작[/red]")

    policy = _load_policy(policy_path)
    profile = _load_profile(profile_name)

    # Stage 2 수술: 태그 캐시 사전 준비
    if TAG_CACHE_AVAILABLE:
        tag_index = get_tag_index()
        console.print(
            f"[green]💉 Tag 캐시 시스템 준비완료 (기존 {len(tag_index.cache)}개 엔트리)[/green]"
        )

    hits = discover(policy=policy, profile=profile, engine=engine)
    edges = link_edges(hits, policy=policy)

    # Stage 2 수술 결과 보고
    if TAG_CACHE_AVAILABLE:
        stats = tag_index.get_stats()
        console.print(
            f"[cyan]📊 Tag I/O 감축 결과: {stats['hit_rate']} 캐시 히트율 (Hits: {stats['hits']}, Misses: {stats['misses']})[/cyan]"
        )
        tag_index.flush()  # 캐시 저장

    # pack
    fmap = FeatureMap(root=str(ROOT), hits=[asdict(h) for h in hits], edges=edges)

    # console table
    title = "Echo Feature Map (preview)"
    if profile_name:
        title += f" - Profile: {profile_name}"
    if policy_path:
        title += f" - Policy: {Path(policy_path).name}"

    table = Table(title=title)
    table.add_column("kind", style="cyan", no_wrap=True)
    table.add_column("file:line", style="magenta")
    table.add_column("meta", style="green")
    for h in hits[:30]:
        table.add_row(h.kind, f"{h.file}:{h.line}", json.dumps(h.meta)[:80])
    console.print(table)

    # 필터링 통계 출력
    if profile_name or policy_path:
        console.print(f"\n[blue]📊 필터링 결과: {len(hits)}개 기능 발견[/]")
        if profile_name:
            console.print(f"[blue]   프로필: {profile_name}[/]")
        if policy_path:
            console.print(f"[blue]   정책: {Path(policy_path).name}[/]")

    if save:
        (ART / "feature_map.json").write_text(
            fmap.model_dump_json(indent=2), encoding="utf-8"
        )
        md = MD_TMPL.render(
            root=str(ROOT),
            total=len(hits),
            by_kind=_by_kind(hits),
            hits=[asdict(h) for h in hits],
            edges=edges,
        )
        (ART / "feature_map.md").write_text(md, encoding="utf-8")
        console.print(
            f"[green]✅ Stage 1+2 수술 완료: {len(hits)}개 기능 매핑, 아티팩트 저장완료[/green]"
        )

    if to_html:
        html = HTML_TMPL.render(root=str(ROOT), data=json.loads(fmap.model_dump_json()))
        (ART / "feature_map.html").write_text(html, encoding="utf-8")
        if open_html:
            webbrowser.open((ART / "feature_map.html").as_uri())
        console.print(
            "[cyan]🎯 HTML 대시보드 생성완료 → artifacts/feature_map.html[/cyan]"
        )


def _by_kind(hits: List[Hit]) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for h in hits:
        d[h.kind] = d.get(h.kind, 0) + 1
    return d


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Echo Feature Discovery & Linker v1")
    ap.add_argument("--save", action="store_true", help="JSON/MD 파일 저장")
    ap.add_argument("--html", action="store_true", help="HTML 대시보드 생성")
    ap.add_argument("--open", action="store_true", help="HTML 자동 열기")
    ap.add_argument("--policy", type=str, help="feature_policies.yaml 경로")
    ap.add_argument(
        "--profile", type=str, help="profiles.yaml 내 프로필명 (예: minimal)"
    )
    ap.add_argument(
        "--engine",
        type=str,
        default="auto",
        choices=["auto", "python", "rg"],
        help="스캔 엔진",
    )
    args = ap.parse_args()
    main(
        save=args.save,
        to_html=args.html,
        open_html=args.open,
        policy_path=args.policy,
        profile_name=args.profile,
        engine=args.engine,
    )
