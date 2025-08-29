from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import yaml
from echo_engine.amoeba.amoeba_manager import AmoebaManager

"""
🌌 Amoeba Loader v0.2
Echo Judgment System의 Amoeba 시스템 로더
임포트 시 부수효과 제거 - 함수 호출 시에만 AmoebaManager 생성
"""




# AmoebaManager는 함수 내부에서 지연 임포트
LOGGER = logging.getLogger("amoeba")


def load_amoeba(
    config_path: str | Path = "echo_engine/amoeba/templates/amoeba_config.yaml",
    autostart_telemetry: bool = True,
) -> Tuple[bool, Optional[Any]]:
    """
    앱 부팅 시 1회 호출. 안전모드로 실패해도 앱은 계속 올라가게 설계.

    Args:
        config_path: Amoeba 설정 파일 경로
        autostart_telemetry: 텔레메트리 자동 시작 여부

    Returns:
        Tuple[bool, Optional[AmoebaManager]]: (성공 여부, AmoebaManager 인스턴스)
    """
    try:
        # 지연 임포트: 함수 호출 시에만 AmoebaManager 로드

        # 1) 설정 로드
        cfg_p = Path(config_path)
        cfg = {}

        if cfg_p.exists():
            cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8")) or {}
            LOGGER.info("🟪 Amoeba config loaded: %s", cfg_p)
        else:
            LOGGER.info("🟪 Amoeba config not found, using defaults: %s", cfg_p)
            cfg = _get_default_config()

        # 텔레메트리 자동 시작 제어
        if not autostart_telemetry:
            if "telemetry" not in cfg:
                cfg["telemetry"] = {}
            cfg["telemetry"]["auto_monitor"] = False

        # 2) 매니저 생성
        manager = AmoebaManager(cfg)
        LOGGER.info("✅ AmoebaManager 생성 완료")

        # 3) 단계 실행 (감지 → 연결 → 최적화)
        manager.detect_environment()
        LOGGER.info("✅ 환경 감지 완료")

        manager.attach()
        LOGGER.info("✅ 시스템 연결 완료")

        result = manager.optimize()
        if isinstance(result, dict) and result.get("status") == "completed":
            LOGGER.info("✅ 시스템 최적화 완료")
        else:
            LOGGER.warning("⚠️ 시스템 최적화 부분 실패 또는 스킵")

        return True, manager

    except Exception as e:
        LOGGER.error("❌ Amoeba 초기화 실패: %s", e)
        # 실패해도 앱은 계속 돌아가게 False/None 반환
        return False, None


def _get_default_config() -> Dict[str, Any]:
    """기본 Amoeba 설정 반환"""
    return {
        "amoeba": {
            "version": "0.1.0",
            "log_level": "info",
            "auto_attach": True,
            "auto_optimize": True,
            "fallback_mode": "safe",
        },
        "environment": {
            "detect_wsl": True,
            "detect_docker": True,
            "detect_virtual_env": True,
        },
        "optimization": {
            "memory_check": True,
            "disk_check": True,
            "module_check": True,
        },
    }


# 편의 래퍼
def quick_load() -> Tuple[bool, Optional[AmoebaManager]]:
    """빠른 Amoeba 로드 (기본 설정 사용)"""
    return load_amoeba()


def load_with_dict(config_dict: Dict[str, Any]) -> Tuple[bool, Optional[Any]]:
    """딕셔너리 설정으로 Amoeba 로드"""
    try:
        # 지연 임포트: 함수 호출 시에만 AmoebaManager 로드

        manager = AmoebaManager(config_dict)
        manager.detect_environment()
        manager.attach()
        manager.optimize()
        return True, manager
    except Exception as e:
        LOGGER.error("❌ 설정 기반 로드 실패: %s", e)
        return False, None
