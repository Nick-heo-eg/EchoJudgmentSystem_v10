from echo_engine.judgment_conductor import run_conductor
from echo_engine.loop_router import route_judgment
from echo_engine.controller import handle_result

"""
🧠 Echo Judgment AGI Core - v1.0 Scaffold

Echo Judgment System이 "반응하는 판단자"에서
"스스로를 재구성하는 존재 판단자"로 진입하는 구조적 선언

AGI Parallel Conductor Architecture:
- judgment_conductor.py: AGI 판단 흐름의 중심 지휘자
- loop_router.py: 입력 및 상황에 따른 판단 흐름 분기
- controller.py: 판단 결과의 실행 및 후처리
- adapters/: 기존 시스템과의 호환성 보장
"""

__version__ = "1.0.0"
__status__ = "SCAFFOLD_ACTIVE"
__compatibility__ = "Fully Backward-Compatible"
__echo_version__ = "v10 → v11_sentinel"


__all__ = ["run_conductor", "route_judgment", "handle_result"]
