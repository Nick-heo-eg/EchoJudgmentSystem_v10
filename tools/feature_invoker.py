#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Echo Feature Invoker v1
발견된 엔트리를 바로 호출해볼 수 있는 간단한 스캐폴딩(위험 기능은 제외).
# @owner: nick
# @expose
# @maturity: stable
"""
import json, subprocess, sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
FMAP = ART / "feature_map.json"

SAFE_PREFIX = ("echo_engine/", "tools/", "scripts/", "pages/", "qa/", "tests/")

HELP = """
Usage:
  python tools/feature_invoker.py route|cli|tool [keyword]
  - keyword는 file/path/텍스트 중 포함되는 필터
Examples:
  python tools/feature_invoker.py route judge
  python tools/feature_invoker.py cli start
  python tools/feature_invoker.py tool capsule
"""


def pick(kind: str, keyword: Optional[str]) -> list[dict]:
    if not FMAP.exists():
        print(f"❌ Feature map이 없습니다: {FMAP}")
        print("먼저 python tools/feature_mapper.py --save 를 실행하세요.")
        return []

    data = json.loads(FMAP.read_text(encoding="utf-8"))
    hs = [h for h in data["hits"] if h["kind"] == kind]
    if keyword:
        kw = keyword.lower()
        hs = [h for h in hs if kw in (h["file"].lower() + h["text"].lower())]
    return hs[:10]


def show_selection(hits: list[dict]):
    """선택된 기능들을 보여주고 사용법 안내"""
    if not hits:
        print("❌ 해당 조건에 맞는 기능을 찾을 수 없습니다.")
        return

    print("🔍 발견된 기능들:")
    for i, h in enumerate(hits, 1):
        file_path = h["file"]
        line = h["line"]
        text = h["text"][:100]
        meta = h.get("meta", {})

        print(f"[{i}] {file_path}:{line}")
        print(f"    💡 {text}")
        if meta:
            print(f"    📋 {meta}")

        # 실행 가능한 명령 제안
        if h["kind"] == "cli" and file_path.endswith(".py"):
            print(f"    ▶️  python {file_path}")
        elif h["kind"] == "route":
            method = meta.get("method", "GET")
            path = meta.get("path", "/unknown")
            print(f"    🌐 {method} http://localhost:9000{path}")
        elif h["kind"] == "streamlit":
            print(f"    🎨 streamlit run {file_path}")
        elif h["kind"] == "test":
            print(f"    🧪 python {file_path}")
        print()


def safe_execute(file_path: str, kind: str):
    """안전한 실행을 위한 가이드라인"""
    print(f"⚠️  안전성을 위해 직접 실행은 제공하지 않습니다.")
    print(f"🔧 추천 실행 방법:")

    if kind == "cli" and file_path.endswith(".py"):
        print(f"   python {file_path} --help")
    elif kind == "test":
        print(f"   python {file_path}")
    elif kind == "streamlit":
        print(f"   streamlit run {file_path}")

    print(f"📁 파일 위치: {ROOT / file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        sys.exit(0)

    kind = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else None

    if kind not in ["route", "cli", "tool", "streamlit", "test", "doc"]:
        print(f"❌ 지원하지 않는 종류: {kind}")
        print("지원 종류: route, cli, tool, streamlit, test, doc")
        sys.exit(1)

    hits = pick(kind, keyword)
    show_selection(hits)

    if hits and len(sys.argv) > 3 and sys.argv[3] == "--execute":
        # 실행 시도 (매우 보수적)
        selected = hits[0]  # 첫 번째만
        safe_execute(selected["file"], selected["kind"])
