#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Tagger v1
- feature_map.json + profiles.yaml을 읽어 '선택된 파일'에만
  # @owner: nick / # @expose / # @maturity: stable  태그를 보증.
- shebang/encoding 라인은 보존하며 그 아래에 주석 태그 삽입.
# @owner: nick
# @expose
# @maturity: stable
"""
from __future__ import annotations
import json, sys, re, fnmatch, argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
FMAP = ART / "feature_map.json"
PROF = ROOT / "profiles.yaml"

try:
    import yaml
except Exception:
    print("❌ pip install pyyaml")
    sys.exit(1)

console = Console()

TAG_OWNER_RE = re.compile(r"^\s*#\s*@owner:\s*(\S+)", re.M)
TAG_EXPOSE_RE = re.compile(r"^\s*#\s*@expose\b", re.M)
TAG_MAT_RE = re.compile(
    r"^\s*#\s*@maturity:\s*(stable|beta|experimental|deprecated)", re.I | re.M
)


def match_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in globs)


def load_profile(name: str):
    if not PROF.exists():
        console.print(f"[red]❌ {PROF} 파일이 없습니다.[/]")
        sys.exit(1)

    profs = yaml.safe_load(PROF.read_text(encoding="utf-8"))
    if name not in profs.get("profiles", {}):
        available = list(profs.get("profiles", {}).keys())
        console.print(f"[red]❌ 알 수 없는 프로필: {name}[/]")
        console.print(f"[yellow]사용 가능한 프로필: {', '.join(available)}[/]")
        sys.exit(1)

    p = profs["profiles"][name]
    return {
        "allow": p.get("allow", ["**"]),
        "deny": p.get("deny", []),
        "tag_defaults": p.get("tag_defaults", {"owner": "nick", "maturity": "stable"}),
    }


def pick_files(profile: dict, all_files: list[str]) -> list[str]:
    out = []
    for f in all_files:
        # 먼저 deny 체크 (우선순위)
        if profile["deny"]:
            denied = False
            for deny_pattern in profile["deny"]:
                if match_any(f, [deny_pattern]):
                    denied = True
                    break
            if denied:
                continue

        # 그 다음 allow 체크
        if profile["allow"]:
            allowed = False
            for allow_pattern in profile["allow"]:
                if match_any(f, [allow_pattern]):
                    allowed = True
                    break
            if not allowed:
                continue

        out.append(f)
    return sorted(set(out))


def ensure_tags(text: str, owner: str, maturity: str) -> tuple[str, bool]:
    changed = False
    have_owner = TAG_OWNER_RE.search(text) is not None
    have_expose = TAG_EXPOSE_RE.search(text) is not None
    have_maturity = TAG_MAT_RE.search(text) is not None

    if have_owner and have_expose and have_maturity:
        return text, False

    # shebang/encoding 줄을 건너뛰고 그 아래에 삽입
    lines = text.splitlines(keepends=False)  # keepends=False for easier handling
    insert_at = 0

    # shebang 라인 확인
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    # encoding 라인 확인
    if insert_at < len(lines) and re.match(
        r"^#.*coding[:=]", lines[insert_at] if insert_at < len(lines) else ""
    ):
        insert_at += 1

    # 기존 docstring 위치 확인 - """ 위에 태그 삽입
    if insert_at < len(lines):
        for i in range(insert_at, min(insert_at + 10, len(lines))):
            if '"""' in lines[i]:
                insert_at = i
                break

    tags_to_add = []
    if not have_owner:
        tags_to_add.append(f"# @owner: {owner}")
    if not have_expose:
        tags_to_add.append("# @expose")
    if not have_maturity:
        tags_to_add.append(f"# @maturity: {maturity}")

    if tags_to_add:
        # 빈 줄이 없으면 하나 추가
        if insert_at > 0 and insert_at < len(lines) and lines[insert_at - 1].strip():
            tags_to_add.insert(0, "")

        lines[insert_at:insert_at] = tags_to_add

        # 태그 뒤에 빈 줄이 없으면 추가
        new_insert = insert_at + len(tags_to_add)
        if new_insert < len(lines) and lines[new_insert].strip():
            lines.insert(new_insert, "")

        changed = True

    # 원래 파일이 \n으로 끝났는지 확인
    ends_with_newline = text.endswith("\n")
    result = "\n".join(lines)
    if ends_with_newline:
        result += "\n"

    return result, changed


def main(profile_name: str, dry_run: bool):
    # feature map 로드
    if not FMAP.exists():
        console.print(f"[red]❌ {FMAP} 파일이 없습니다.[/]")
        console.print(
            "[yellow]먼저 python tools/feature_mapper.py --save 를 실행하세요.[/]"
        )
        sys.exit(1)

    fmap = json.loads(FMAP.read_text(encoding="utf-8"))
    files = sorted(set(h["file"] for h in fmap["hits"]))

    # 프로필 로드
    prof = load_profile(profile_name)
    targets = pick_files(prof, files)

    owner = prof["tag_defaults"].get("owner", "nick")
    maturity = prof["tag_defaults"].get("maturity", "stable")

    console.print(f"[cyan]🔖 Feature Tagger v1[/]")
    console.print(f"[blue]프로필: {profile_name}[/]")
    console.print(f"[blue]전체 파일: {len(files)}개 → 선택된 파일: {len(targets)}개[/]")
    console.print(f"[blue]태그 기본값: owner={owner}, maturity={maturity}[/]")

    if dry_run:
        console.print("[yellow]🧪 DRY RUN 모드 - 실제 파일은 수정하지 않습니다.[/]")

    touched = []
    skipped = []

    for rel in targets:
        path = ROOT / rel
        try:
            if not path.exists():
                skipped.append(f"{rel} (파일 없음)")
                continue

            txt = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            skipped.append(f"{rel} (읽기 실패: {e})")
            continue

        new_txt, changed = ensure_tags(txt, owner, maturity)
        if changed:
            touched.append(rel)
            if not dry_run:
                try:
                    path.write_text(new_txt, encoding="utf-8")
                except Exception as e:
                    skipped.append(f"{rel} (쓰기 실패: {e})")
                    touched.remove(rel)

    # 결과 테이블
    table = Table(title=f"Tagging Results - {profile_name}")
    table.add_column("상태", style="green")
    table.add_column("수량", justify="right")
    table.add_row("✅ 선택된 파일", str(len(targets)))
    table.add_row("🏷️  태그 추가됨", str(len(touched)))
    table.add_row("⚠️  건너뜀", str(len(skipped)))

    console.print(table)

    if touched:
        console.print(f"\n[green]✅ 태그가 추가된 파일들 (처음 20개):[/]")
        for i, f in enumerate(touched[:20], 1):
            console.print(f"  {i:2d}. {f}")
        if len(touched) > 20:
            console.print(f"     ... 그리고 {len(touched)-20}개 더")

    if skipped:
        console.print(f"\n[yellow]⚠️  건너뛴 파일들 (처음 10개):[/]")
        for i, reason in enumerate(skipped[:10], 1):
            console.print(f"  {i:2d}. {reason}")
        if len(skipped) > 10:
            console.print(f"     ... 그리고 {len(skipped)-10}개 더")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Profile-based feature tagging tool")
    ap.add_argument(
        "--profile", default="minimal", help="프로필 선택 (default: minimal)"
    )
    ap.add_argument("--dry-run", action="store_true", help="실제 수정 없이 미리보기만")
    args = ap.parse_args()
    main(args.profile, args.dry_run)
