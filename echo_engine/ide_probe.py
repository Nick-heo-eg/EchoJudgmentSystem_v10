# ide_probe.py
# 목적: 로컬 IDE/툴체인/내장 모듈의 기능 보유 현황을 점검해 JSON/표로 리포트
import os, json, subprocess, shutil, sys, time, re
from pathlib import Path
from importlib.util import find_spec

ROOT = Path(os.getenv("ODORI_SANDBOX_ROOT", ".")).resolve()

# 후보 모듈/파일 패턴 (네가 만들었을 법한 것들)
CANDIDATE_MODULES = [
    "ide_api",
    "webshell",
    "workspace",
    "runner",
    "vscode_bridge",
    "editor_bridge",
    "project_api",
    "devtools",
    "echo_ide",
]
CANDIDATE_FILES = [
    "ide_api.py",
    "webshell.py",
    "vscode_bridge.py",
    "editor_bridge.py",
    "project_api.py",
    "devtools.py",
    "echo_ide.py",
]


def _which(cmd):
    return shutil.which(cmd) is not None


def _run(cmd, timeout=5):
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, timeout=timeout, shell=True
        )
        return 0, out.decode("utf-8", "replace").strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode("utf-8", "replace").strip()
    except Exception as e:
        return -1, str(e)


def _safe_glob(root: Path, patterns):
    hits = []
    for pat in patterns:
        for p in root.rglob(pat):
            # .git/node_modules/venv 등은 스킵
            parts = set(p.parts)
            if any(
                x in parts
                for x in [
                    ".git",
                    "node_modules",
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".mypy_cache",
                    ".idea",
                    ".vscode",
                ]
            ):
                continue
            hits.append(str(p))
    return sorted(set(hits))


def probe():
    caps = {
        "fs_read": True,  # Python이 기본 제공
        "fs_write": None,  # 확인 필요
        "run_cmd": None,
        "editor_open": None,
        "git_basic": None,
        "http_client": None,
        "package_pip": None,
        "package_npm": None,
        "browser_headless": None,
        "db_sqlite": None,
        "env_info": True,
        "logs_access": True,
        "bridge_modules": [],
        "bridge_files": [],
        "notes": [],
        "executables": {},
        "versions": {},
    }

    # 실행기/툴체인
    for exe in ["git", "code", "python", "python3", "pip", "pip3", "node", "npm"]:
        caps["executables"][exe] = _which(exe)

    # 버전
    for name, cmd in {
        "git": "git --version",
        "code": "code --version",
        "python": "python --version",
        "pip": "pip --version",
        "node": "node --version",
        "npm": "npm --version",
    }.items():
        if caps["executables"].get(name):
            _, out = _run(cmd)
            caps["versions"][name] = out.splitlines()[0] if out else ""

    # run_cmd
    rc, out = _run("echo odori-run-ok")
    caps["run_cmd"] = rc == 0 and "odori-run-ok" in out

    # editor_open (VS Code가 있고 code -g 동작?)
    if caps["executables"].get("code"):
        rc, _ = _run("code --help")
        caps["editor_open"] = rc == 0

    # git_basic
    if caps["executables"].get("git"):
        rc, _ = _run("git status")
        caps["git_basic"] = rc in (
            0,
            1,
            128,
        )  # 128=not a repo → 바이너리는 있으니 True로 간주X
        if rc == 128:
            caps["notes"].append(
                "git 설치됨(현재 디렉토리는 repo 아님). repo에서 재시도 권장."
            )

    # http_client (requests 모듈 or curl)
    caps["http_client"] = bool(find_spec("requests") or _which("curl"))

    # package_pip / npm
    caps["package_pip"] = caps["executables"].get("pip") or bool(find_spec("pip"))
    caps["package_npm"] = caps["executables"].get("npm")

    # browser_headless (playwright or selenium, 혹은 chrome-headless)
    caps["browser_headless"] = bool(find_spec("playwright") or find_spec("selenium"))

    # db_sqlite
    try:
        import sqlite3  # noqa

        caps["db_sqlite"] = True
    except Exception:
        caps["db_sqlite"] = False

    # fs_write (쓰기 가능한가? 임시 파일 테스트)
    try:
        tmp = ROOT / ".odori_probe_tmp"
        tmp.write_text("ok", encoding="utf-8")
        tmp.unlink(missing_ok=True)
        caps["fs_write"] = True
    except Exception as e:
        caps["fs_write"] = False
        caps["notes"].append(f"쓰기 실패: {e}")

    # 브리지 후보 모듈/파일
    for m in CANDIDATE_MODULES:
        if find_spec(m):
            caps["bridge_modules"].append(m)
    caps["bridge_files"] = _safe_glob(ROOT, CANDIDATE_FILES)

    return caps


if __name__ == "__main__":
    data = probe()

    # 표와 JSON을 같이 출력
    def tick(v):
        return "✅" if v is True else ("❌" if v is False else "❓")

    rows = [
        ("파일 읽기", "fs_read"),
        ("파일 쓰기", "fs_write"),
        ("명령 실행", "run_cmd"),
        ("에디터 연동(code -g)", "editor_open"),
        ("Git 사용", "git_basic"),
        ("HTTP 요청", "http_client"),
        ("pip 패키지", "package_pip"),
        ("npm 패키지", "package_npm"),
        ("헤드리스 브라우저", "browser_headless"),
        ("SQLite", "db_sqlite"),
    ]
    print("🧪 IDE Capability Probe\n")
    for label, key in rows:
        print(f"- {label:>16}: {tick(data.get(key))}")
    print("\n🔧 Executables:", {k: v for k, v in data["executables"].items() if v})
    if data["versions"]:
        print("🔢 Versions:", data["versions"])
    if data["bridge_modules"] or data["bridge_files"]:
        print("\n🔌 Bridge Modules:", data["bridge_modules"])
        print("📄 Bridge Files:", data["bridge_files"])
    if data["notes"]:
        print("\n🗒️ Notes:")
        for n in data["notes"]:
            print(" -", n)
    print("\n--- JSON ---")
    print(json.dumps(data, ensure_ascii=False, indent=2))
