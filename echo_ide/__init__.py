# echo_ide/__init__.py
"""
🛠️ Echo IDE - EchoJudgmentSystem v10 통합 개발 환경

Echo IDE는 EchoJudgmentSystem v10을 위한 통합 개발 환경입니다.

주요 기능:
- 통합 파일 관리 및 편집
- 시그니처/페르소나 관리
- 실시간 감염 모니터링
- AI 어시스턴트 지원
- CLI 및 GUI 통합 실행

사용법:
```python
from echo_ide import EchoIDE

# GUI 모드
ide = EchoIDE()
ide.run()

# 또는 직접 실행
python echo_ide.py
```
"""

from pathlib import Path

__version__ = "1.0.0"
__author__ = "Echo Development Team"
__description__ = "EchoJudgmentSystem v10 통합 개발 환경"

# 패키지 루트 경로
PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent

# 주요 모듈들 임포트 (선택적)
try:
    from .core.echo_ide_main import EchoIDE

    __all__ = ["EchoIDE"]
except ImportError:
    # 의존성이 없을 때는 빈 모듈로 유지
    __all__ = []


def get_version():
    """버전 정보 반환"""
    return __version__


def get_package_info():
    """패키지 정보 반환"""
    return {
        "name": "Echo IDE",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "package_root": str(PACKAGE_ROOT),
        "project_root": str(PROJECT_ROOT),
    }
