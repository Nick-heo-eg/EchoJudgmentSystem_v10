# echo_ide/core/__init__.py
"""
Echo IDE 코어 모듈

Echo IDE의 핵심 기능들을 제공하는 모듈 패키지입니다.

모듈 구성:
- echo_ide_main: 메인 IDE 인터페이스
- echo_file_manager: 파일 관리 시스템
- echo_signature_manager: 시그니처/페르소나 관리
- echo_monitor_dashboard: 실시간 모니터링 대시보드
- echo_ai_assistant: AI 어시스턴트
"""

from pathlib import Path

__version__ = "1.0.0"

# 코어 모듈 루트
CORE_ROOT = Path(__file__).parent

# 모듈별 임포트 (선택적)
try:
    from .echo_ide_main import EchoIDE
    from .echo_file_manager import EchoFileManager, create_file_manager_ui
    from .echo_signature_manager import (
        EchoSignatureManager,
        create_signature_manager_ui,
    )
    from .echo_monitor_dashboard import (
        EchoMonitorDashboard,
        create_monitor_dashboard_ui,
    )
    from .echo_ai_assistant import EchoAIAssistant, create_ai_assistant_ui
    from .echo_natural_processor import EchoNaturalProcessor

    __all__ = [
        "EchoIDE",
        "EchoFileManager",
        "create_file_manager_ui",
        "EchoSignatureManager",
        "create_signature_manager_ui",
        "EchoMonitorDashboard",
        "create_monitor_dashboard_ui",
        "EchoAIAssistant",
        "create_ai_assistant_ui",
        "EchoNaturalProcessor",
    ]

except ImportError as e:
    # 의존성 문제시 경고만 출력
    print(f"⚠️ Echo IDE 코어 모듈 임포트 오류: {e}")
    __all__ = []


def get_core_modules():
    """사용 가능한 코어 모듈 목록 반환"""

    available_modules = []

    # 각 모듈의 가용성 확인
    module_files = [
        "echo_ide_main.py",
        "echo_file_manager.py",
        "echo_signature_manager.py",
        "echo_monitor_dashboard.py",
        "echo_ai_assistant.py",
        "echo_natural_processor.py",
    ]

    for module_file in module_files:
        if (CORE_ROOT / module_file).exists():
            module_name = module_file.replace(".py", "")
            available_modules.append(module_name)

    return available_modules


def check_dependencies():
    """Echo IDE 실행에 필요한 의존성 확인"""

    dependencies = {
        "tkinter": False,
        "matplotlib": False,
        "psutil": False,
        "yaml": False,
        "numpy": False,
    }

    # 각 의존성 확인
    try:
        import tkinter

        dependencies["tkinter"] = True
    except ImportError:
        pass

    try:
        import matplotlib

        dependencies["matplotlib"] = True
    except ImportError:
        pass

    try:
        import psutil

        dependencies["psutil"] = True
    except ImportError:
        pass

    try:
        import yaml

        dependencies["yaml"] = True
    except ImportError:
        pass

    try:
        import numpy

        dependencies["numpy"] = True
    except ImportError:
        pass

    return dependencies
