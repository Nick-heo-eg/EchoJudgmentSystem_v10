#!/usr/bin/env python3
"""
🚀 Echo Web IDE 런처
간편한 웹 IDE 실행 스크립트
"""

import sys
import subprocess
import webbrowser
import time
from pathlib import Path


def check_dependencies():
    """필요한 의존성 확인 및 설치"""
    required_packages = ["fastapi", "uvicorn[standard]", "websockets", "pydantic"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.split("[")[0])
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("📦 필요한 패키지를 설치합니다...")
        for package in missing_packages:
            print(f"  설치 중: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("✅ 모든 의존성 설치 완료!")


def launch_web_ide():
    """웹 IDE 실행"""
    print("🧬 Echo Web IDE 시작 중...")

    # 의존성 확인
    check_dependencies()

    # 서버 스크립트 경로
    server_script = Path(__file__).parent / "web_ide_server.py"

    if not server_script.exists():
        print("❌ 웹 IDE 서버 스크립트를 찾을 수 없습니다.")
        return

    print("🌐 웹 서버 시작 중...")

    try:
        # 서버 프로세스 시작
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 서버가 시작될 때까지 잠시 대기
        time.sleep(3)

        # 브라우저에서 IDE 열기
        url = "http://localhost:9000"
        print(f"🚀 브라우저에서 Echo Web IDE를 엽니다: {url}")
        webbrowser.open(url)

        print("\n" + "=" * 60)
        print("🧬 Echo Web IDE가 성공적으로 시작되었습니다!")
        print("=" * 60)
        print(f"🌐 주소: {url}")
        print("⏹️  종료하려면 Ctrl+C를 누르세요")
        print("=" * 60)

        # 서버 출력 실시간 표시
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

    except KeyboardInterrupt:
        print("\n👋 Echo Web IDE를 종료합니다...")
        process.terminate()
    except Exception as e:
        print(f"❌ 웹 IDE 실행 오류: {e}")


if __name__ == "__main__":
    launch_web_ide()
