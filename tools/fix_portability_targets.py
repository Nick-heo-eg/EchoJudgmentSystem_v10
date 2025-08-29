#!/usr/bin/env python3
"""
Portability 정밀 봉합 도구 - 21곳만 노린 정확 타격
패턴은 "명백한 절대경로 상수"만 겨냥합니다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "echo_engine"

# (1) 명백한 절대경로 리터럴만: /mnt/<drive>/..., C:\..., /Users/...
PATTERNS = [
    (re.compile(r'Path\("(/mnt/[a-z]/[^"]+)"\)'), r'ensure_portable("\1")'),
    (re.compile(r'"([A-Za-z]:\\\\[^"]+)"'), r'ensure_portable("\1")'),
    (re.compile(r'Path\("(/Users/[^"]+)"\)'), r'ensure_portable("\1")'),
    # v2 패턴 - 추가 경로들
    # /tmp → temp_dir()
    (re.compile(r'"(/tmp/[^"]*)"'), r"str(temp_dir())"),
    (re.compile(r"Path\('/tmp/([^']*)'\)"), r'Path(temp_dir()) / "\1"'),
    # 사용자 홈 하드코딩 → home()
    (re.compile(r'"(/home/[A-Za-z0-9_\-./]+)"'), r"str(home())"),
    # Windows Program Files 류 → ensure_portable
    (re.compile(r'"([A-Za-z]:\\\\Program Files[^"]*)"'), r'ensure_portable("\1")'),
    # /var/log/* → logs_dir()
    (re.compile(r'"(/var/log/[^"]*)"'), r"str(logs_dir())"),
    # /etc/* → project_root()/etc (기본값) - 쓰기 필요 없는 읽기용만 대상
    (re.compile(r'"(/etc/[^"]*)"'), r'str(project_root() / "etc")'),
    # sys.path.append('/mnt/...') → project_root()
    (
        re.compile(r"sys\.path\.append\(['\"](/mnt/[a-z]/[^'\"]+)['\"]\)"),
        r"sys.path.append(str(project_root()))",
    ),
    # open('/var/log/xxx.log', ...) → logs_dir()/xxx.log
    (
        re.compile(r"open\(['\"](/var/log/([^'\"]+))['\"],"),
        r"open(str(logs_dir() / '\2'),",
    ),
    # v4 패턴 추가
    # sys.path.insert(0, '/mnt/...') → project_root()
    (
        re.compile(
            r"sys\.path\.insert\(\s*0\s*,\s*['\"](/mnt/[a-z]/[^'\"]+)['\"]\s*\)"
        ),
        r"sys.path.insert(0, str(project_root()))",
    ),
    # os.path.join('/etc/xxx', ...) → project_root()/etc/xxx
    (
        re.compile(r"os\.path\.join\(\s*['\"](/etc/[^'\"]+)['\"]"),
        r"os.path.join(str(project_root() / 'etc')",
    ),
]

TARGETS_HINT = [
    "cosmos_wsl_bridge_guardian.py",
    "echo_claude_cli_demo.py",
    "amoeba/adapters/local_adapter.py",
    "amoeba/adapters/wsl_adapter.py",
    "amoeba/adapters/cloud_adapter.py",
]

HEADER = (
    "from echo_engine.infra.portable_paths import "
    "ensure_portable, project_root, home, temp_dir, logs_dir, cache_dir, data_dir\n"
)


def patch_file(fp: Path, dry=True) -> bool:
    """파일 패치 수행"""
    text = fp.read_text(encoding="utf-8", errors="ignore")
    orig = text
    changed = False

    if "ensure_portable(" not in text and any(p.search(text) for p, _ in PATTERNS):
        # 헤더 주입(중복 방지)
        if "portable_paths import" not in text:
            text = HEADER + text

        for rx, rep in PATTERNS:
            text, n = rx.subn(rep, text)
            if n:
                changed = True

    if changed and not dry:
        fp.write_text(text, encoding="utf-8")

    return orig != text


def main(dry=True):
    """메인 실행 함수"""
    hit = 0
    print(f"{'DRY-RUN' if dry else 'APPLY'} 모드로 스캔 중...")

    for rel in TARGETS_HINT:
        fp = SRC / rel
        if fp.exists():
            if patch_file(fp, dry=dry):
                print(f"  📝 {'예상' if dry else '적용'}: {rel}")
                hit += 1
        else:
            print(f"  ❌ 파일 없음: {rel}")

    # 추가로 루트 레벨 및 전체 프로젝트 스캔
    for pattern in ["cosmos*.py", "echo*.py", "fix*.py", "test*.py", "execute*.py"]:
        for fp in ROOT.glob(pattern):
            if (
                fp.is_file()
                and "portable_paths" not in fp.name
                and "fix_portability" not in fp.name
            ):
                if patch_file(fp, dry=dry):
                    print(f"  📝 {'예상' if dry else '적용'}: {fp.relative_to(ROOT)}")
                    hit += 1

    # echo_engine 하위 전체 스캔
    for fp in SRC.rglob("*.py"):
        if fp.is_file() and "portable_paths" not in fp.name:
            if patch_file(fp, dry=dry):
                print(f"  📝 {'예상' if dry else '적용'}: {fp.relative_to(ROOT)}")
                hit += 1

    print(f"{('DRY-RUN' if dry else 'APPLY')} 완료 - 변경: {hit}개")
    return hit


if __name__ == "__main__":
    import sys

    dry = True
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        dry = False
    main(dry=dry)
