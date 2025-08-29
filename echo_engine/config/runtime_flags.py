"""
Runtime Flags for Echo Free-Speak Mode
동적 페르소나 믹싱과 템플릿 우회를 위한 런타임 플래그
"""

from dataclasses import dataclass
import os


@dataclass
class RuntimeFlags:
    """Echo 런타임 동작 플래그"""

    free_speak: bool = False
    no_template: bool = False
    temperature: float = 0.8
    top_p: float = 0.9
    timeout_s: int = 60

    @classmethod
    def from_env(cls):
        return cls(
            free_speak=os.getenv("ECHO_FREE_SPEAK", "0") == "1",
            no_template=os.getenv("ECHO_NO_TEMPLATE", "0") == "1",
            temperature=float(os.getenv("ECHO_TEMPERATURE", "0.8")),
            top_p=float(os.getenv("ECHO_TOP_P", "0.9")),
            timeout_s=int(os.getenv("ECHO_TIMEOUT_S", "60")),
        )


# 글로벌 런타임 플래그 인스턴스
_runtime_flags = RuntimeFlags.from_env()


def get_runtime_flags() -> RuntimeFlags:
    """현재 런타임 플래그 반환"""
    return _runtime_flags


def set_runtime_flag(key: str, value):
    """런타임 플래그 동적 설정"""
    global _runtime_flags
    if hasattr(_runtime_flags, key):
        setattr(_runtime_flags, key, value)


def enable_free_speak():
    """Free-speak 모드 활성화"""
    set_runtime_flag("free_speak", True)
    set_runtime_flag("temperature", 0.9)


def enable_dynamic_personas():
    """동적 페르소나 믹싱 활성화"""
    set_runtime_flag("no_template", True)
    set_runtime_flag("top_p", 0.95)


def reset_flags():
    """플래그 초기화"""
    global _runtime_flags
    _runtime_flags = RuntimeFlags.from_env()
