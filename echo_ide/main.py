# echo_ide/main.py

from core.echo_helmsman_controller import EchoHelmsmanController
from core.echo_ide_main import EchoIDE  # 이 줄 추가


def main():
    print("🚀 Echo IDE 시작 중...")
    ide = EchoIDE()  # IDE 인스턴스 생성
    helm = EchoHelmsmanController(ide_instance=ide)  # 인자로 전달
    helm.run_diagnostic_startup()
    helm.run_interactive_mode()


if __name__ == "__main__":
    main()
