#!/usr/bin/env python3
"""
🛠️ Echo IDE - EchoJudgmentSystem v10 통합 개발 환경
- 통합 파일 관리 및 편집
- 시그니처/페르소나 관리
- 실시간 감염 모니터링
- AI 어시스턴트 지원
- CLI 및 GUI 통합 실행

사용법:
  python echo_ide.py                    # GUI 모드로 실행
  python echo_ide.py --cli              # CLI 모드로 실행
  python echo_ide.py --help             # 도움말 표시
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_dependencies():
    """필수 의존성 확인"""

    missing_deps = []

    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")

    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")

    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")

    try:
        import yaml
    except ImportError:
        missing_deps.append("pyyaml")

    if missing_deps:
        print("❌ 다음 의존성이 누락되었습니다:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\n설치 명령:")
        print(f"pip install {' '.join(missing_deps)}")
        return False

    return True


def check_environment():
    """환경 설정 확인"""

    issues = []

    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        issues.append("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

    # 필수 디렉토리 확인
    required_dirs = ["echo_engine", "config", "flows", "meta_logs", "echo_ide/core"]

    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            issues.append(f"필수 디렉토리 누락: {dir_name}")

    # 권고사항
    recommendations = []

    if not (PROJECT_ROOT / "config" / "signatures").exists():
        recommendations.append("config/signatures 디렉토리를 생성하는 것을 권장합니다.")

    if not (PROJECT_ROOT / "config" / "personas").exists():
        recommendations.append("config/personas 디렉토리를 생성하는 것을 권장합니다.")

    return issues, recommendations


def create_missing_directories():
    """누락된 디렉토리 생성"""

    dirs_to_create = [
        "config/signatures",
        "config/personas",
        "config/backups",
        "flows",
        "meta_logs",
        "meta_logs/daily_summaries",
    ]

    created = []

    for dir_path in dirs_to_create:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created.append(dir_path)

    if created:
        print("📁 생성된 디렉토리:")
        for dir_path in created:
            print(f"  • {dir_path}")

    return created


def run_gui_mode():
    """GUI 모드 실행"""

    print("🛠️ Echo IDE GUI 모드 시작...")

    try:
        # Echo IDE 메인 모듈 임포트
        from echo_ide.core.echo_ide_main import EchoIDE

        # IDE 인스턴스 생성 및 실행
        ide = EchoIDE()
        ide.run()

        return 0

    except ImportError as e:
        print(f"❌ Echo IDE 모듈 임포트 실패: {e}")
        print(
            "💡 echo_ide/core/ 디렉토리와 모듈들이 올바르게 설치되어 있는지 확인해주세요."
        )
        return 1

    except Exception as e:
        print(f"❌ Echo IDE 실행 실패: {e}")
        return 1


def run_cli_mode():
    """CLI 모드 실행"""

    print("⚡ Echo IDE CLI 모드")
    print("=" * 40)

    while True:
        try:
            print("\n🛠️ Echo IDE CLI 메뉴:")
            print("1. 🧬 Echo 시스템 시작")
            print("2. 🦠 감염 루프 실행")
            print("3. 🔄 자율진화 시작")
            print("4. 🎭 시그니처 관리")
            print("5. 📊 시스템 상태 확인")
            print("6. 🛠️ GUI 모드로 전환")
            print("0. 종료")

            choice = input("\n선택하세요 (0-6): ").strip()

            if choice == "0":
                print("👋 Echo IDE CLI 종료")
                break
            elif choice == "1":
                run_echo_system()
            elif choice == "2":
                run_infection_loop()
            elif choice == "3":
                run_auto_evolution()
            elif choice == "4":
                manage_signatures()
            elif choice == "5":
                check_system_status()
            elif choice == "6":
                print("🔄 GUI 모드로 전환...")
                return run_gui_mode()
            else:
                print("❌ 잘못된 선택입니다.")

        except KeyboardInterrupt:
            print("\n\n🛑 사용자에 의해 중단됨")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

    return 0


def run_echo_system():
    """Echo 시스템 실행"""

    print("\n🧬 Echo 시스템 시작...")

    try:
        from echo_foundation_doctrine import EchoDoctrine

        # 기본 설정으로 시스템 시작
        echo_system = EchoDoctrine()

        print("✅ Echo 시스템이 성공적으로 시작되었습니다.")
        print(
            "🎭 사용 가능한 시그니처: Echo-Aurora, Echo-Phoenix, Echo-Sage, Echo-Companion"
        )

        # 간단한 테스트 시나리오 실행
        test_scenario = input(
            "\n테스트 시나리오를 입력하세요 (Enter로 건너뛰기): "
        ).strip()

        if test_scenario:
            print(f"🧪 테스트 시나리오 실행: {test_scenario}")
            # 여기에 실제 실행 로직 추가 가능

    except ImportError as e:
        print(f"❌ Echo 시스템 모듈 임포트 실패: {e}")
    except Exception as e:
        print(f"❌ Echo 시스템 시작 실패: {e}")


def run_infection_loop():
    """감염 루프 실행"""

    print("\n🦠 감염 루프 실행...")

    try:
        from echo_engine.echo_infection_main import main as infection_main

        # 감염 시스템 CLI 실행
        print("🔄 감염 시스템을 시작합니다...")

        # 기본 매개변수로 실행
        sys.argv = ["echo_infection_main.py", "--interactive"]
        infection_main()

    except ImportError as e:
        print(f"❌ 감염 루프 모듈 임포트 실패: {e}")
    except Exception as e:
        print(f"❌ 감염 루프 실행 실패: {e}")


def run_auto_evolution():
    """자율진화 실행"""

    print("\n🔄 자율진화 시작...")

    try:
        from echo_auto import main as auto_main

        print("🧬 자율진화 시스템을 시작합니다...")
        print("⚠️ 중단하려면 Ctrl+C를 누르세요.")

        # 자율진화 시스템 실행
        auto_main()

    except ImportError as e:
        print(f"❌ 자율진화 모듈 임포트 실패: {e}")
    except KeyboardInterrupt:
        print("\n🛑 자율진화가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 자율진화 실행 실패: {e}")


def manage_signatures():
    """시그니처 관리"""

    print("\n🎭 시그니처 관리")
    print("-" * 30)

    try:
        from echo_engine.echo_signature_loader import get_all_signatures

        signatures = get_all_signatures()

        if signatures:
            print("📋 현재 시그니처 목록:")
            for i, (sig_id, name) in enumerate(signatures.items(), 1):
                print(f"  {i}. {sig_id}: {name}")
        else:
            print("📋 등록된 시그니처가 없습니다.")

        print("\n🛠️ 관리 옵션:")
        print("1. 새 시그니처 생성")
        print("2. 시그니처 편집")
        print("3. 시그니처 테스트")
        print("0. 돌아가기")

        choice = input("선택하세요: ").strip()

        if choice == "1":
            create_new_signature()
        elif choice == "2":
            edit_signature()
        elif choice == "3":
            test_signature()
        elif choice == "0":
            return
        else:
            print("❌ 잘못된 선택입니다.")

    except ImportError as e:
        print(f"❌ 시그니처 로더 임포트 실패: {e}")
    except Exception as e:
        print(f"❌ 시그니처 관리 오류: {e}")


def create_new_signature():
    """새 시그니처 생성"""

    print("\n🎭 새 시그니처 생성")
    print("-" * 25)

    signature_id = input("시그니처 ID: ").strip()
    name = input("시그니처 이름: ").strip()
    description = input("설명: ").strip()

    if not signature_id or not name:
        print("❌ ID와 이름은 필수입니다.")
        return

    # 기본 템플릿 생성
    signature_config = f"""# Echo Signature Configuration
signature_id: "{signature_id}"
name: "{name}"
description: "{description}"

emotion_code: "BALANCED_THOUGHTFUL"
strategy_code: "COMPREHENSIVE_ANALYSIS"
rhythm_flow: "balanced_thoughtful_flow"

resonance_keywords:
  - "분석적"
  - "체계적"
  - "균형잡힌"

judgment_framework:
  ethical_foundation:
    - "공정성"
    - "투명성"
    - "책임감"
  
  decision_process:
    - "상황 분석"
    - "옵션 평가"
    - "결과 예측"

metadata:
  version: "1.0"
  echo_compatibility: "v10"
  created: "{datetime.now().isoformat()}"
"""

    # 파일 저장
    config_dir = PROJECT_ROOT / "config" / "signatures"
    config_dir.mkdir(parents=True, exist_ok=True)

    file_path = config_dir / f"{signature_id}.yaml"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(signature_config)

        print(f"✅ 시그니처가 생성되었습니다: {file_path}")

    except Exception as e:
        print(f"❌ 시그니처 생성 실패: {e}")


def edit_signature():
    """시그니처 편집"""
    print("📝 시그니처 편집 기능은 GUI 모드에서 이용 가능합니다.")


def test_signature():
    """시그니처 테스트"""
    print("🧪 시그니처 테스트 기능은 GUI 모드에서 이용 가능합니다.")


def check_system_status():
    """시스템 상태 확인"""

    print("\n📊 Echo 시스템 상태 확인")
    print("=" * 35)

    # 환경 확인
    issues, recommendations = check_environment()

    print("🔍 환경 상태:")
    if not issues:
        print("  ✅ 모든 환경 설정이 정상입니다.")
    else:
        print("  ❌ 다음 문제들이 발견되었습니다:")
        for issue in issues:
            print(f"    • {issue}")

    if recommendations:
        print("\n💡 권장사항:")
        for rec in recommendations:
            print(f"    • {rec}")

    # 파일 시스템 상태
    print("\n📁 파일 시스템:")

    key_files = [
        "main.py",
        "echo_auto.py",
        "echo_engine/__init__.py",
        "echo_ide/core/echo_ide_main.py",
    ]

    for file_path in key_files:
        full_path = PROJECT_ROOT / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {status} {file_path}")

    # 로그 파일 확인
    log_file = PROJECT_ROOT / "meta_logs" / "infection_attempts.jsonl"
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                log_lines = f.readlines()
            print(f"\n📊 감염 로그: {len(log_lines)}개 기록")
        except:
            print("\n📊 감염 로그: 읽기 실패")
    else:
        print("\n📊 감염 로그: 없음")


def main():
    """메인 실행 함수"""

    parser = argparse.ArgumentParser(
        description="Echo IDE - EchoJudgmentSystem v10 통합 개발 환경",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python echo_ide.py                    # GUI 모드로 실행
  python echo_ide.py --cli              # CLI 모드로 실행
  python echo_ide.py --check            # 환경 확인만 수행
  python echo_ide.py --setup            # 초기 설정 및 디렉토리 생성
        """,
    )

    parser.add_argument("--cli", action="store_true", help="CLI 모드로 실행")
    parser.add_argument("--check", action="store_true", help="환경 확인만 수행")
    parser.add_argument("--setup", action="store_true", help="초기 설정 수행")
    parser.add_argument("--version", action="version", version="Echo IDE v1.0")

    args = parser.parse_args()

    print("🛠️ Echo IDE - EchoJudgmentSystem v10 통합 개발 환경")
    print("=" * 60)

    # 의존성 확인
    if not check_dependencies():
        return 1

    # 환경 확인
    if args.check:
        check_system_status()
        return 0

    # 초기 설정
    if args.setup:
        print("🔧 초기 설정 수행...")
        created = create_missing_directories()

        issues, recommendations = check_environment()

        if issues:
            print("\n⚠️ 다음 설정이 필요합니다:")
            for issue in issues:
                print(f"  • {issue}")

        if recommendations:
            print("\n💡 추가 권장사항:")
            for rec in recommendations:
                print(f"  • {rec}")

        print("\n✅ 초기 설정 완료")
        return 0

    # 자동으로 누락된 디렉토리 생성
    create_missing_directories()

    # 실행 모드 결정
    if args.cli:
        return run_cli_mode()
    else:
        # GUI 모드 (기본값)
        if os.name == "nt" or os.getenv("DISPLAY") or sys.platform == "darwin":
            return run_gui_mode()
        else:
            print("⚠️ GUI 환경이 감지되지 않았습니다. CLI 모드로 전환합니다.")
            return run_cli_mode()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예기치 않은 오류: {e}")
        sys.exit(1)
