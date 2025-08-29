#!/usr/bin/env python3
"""
🚀 Echo Runtime Flags System
Dynamic behavior control for Echo Free-Speak mode

Enables runtime switching between:
- Template-based responses vs. free-speak generation
- Signature override control
- Dynamic persona mixing activation
"""

import os
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EchoRuntimeFlags:
    """Echo 런타임 플래그 구조"""

    # Free-speak 모드 플래그들
    free_speak_enabled: bool = False
    template_bypass: bool = False
    dynamic_persona_mixing: bool = False
    signature_override_enabled: bool = False

    # 응답 생성 제어
    response_temperature: float = 0.7
    response_top_p: float = 0.9
    response_creativity_boost: float = 1.0

    # 디버깅 및 로깅
    debug_mode: bool = False
    log_persona_changes: bool = False
    trace_response_generation: bool = False

    # 메타 정보
    flags_set_at: datetime = field(default_factory=datetime.now)
    modified_by: str = "system"
    session_id: Optional[str] = None


class RuntimeFlagsManager:
    """🎛️ 런타임 플래그 관리자"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._flags = EchoRuntimeFlags()
            self._callbacks = {}
            self._initialized = True

    def enable_free_speak(self, temperature: float = 0.8, top_p: float = 0.9):
        """Free-speak 모드 활성화"""
        self._flags.free_speak_enabled = True
        self._flags.template_bypass = True
        self._flags.dynamic_persona_mixing = True
        self._flags.response_temperature = temperature
        self._flags.response_top_p = top_p
        self._flags.modified_by = "enable_free_speak"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("free_speak_enabled")

    def disable_templates(self):
        """템플릿 시스템 완전 비활성화"""
        self._flags.template_bypass = True
        self._flags.modified_by = "disable_templates"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("templates_disabled")

    def enable_signature_override(self, override_signature: str = None):
        """시그니처 오버라이드 활성화"""
        self._flags.signature_override_enabled = True
        if override_signature:
            self._flags.override_signature = override_signature
        self._flags.modified_by = f"signature_override_{override_signature}"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("signature_override_enabled")

    def enable_dynamic_personas(self):
        """동적 페르소나 믹싱 활성화"""
        self._flags.dynamic_persona_mixing = True
        self._flags.modified_by = "enable_dynamic_personas"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("dynamic_personas_enabled")

    def set_creativity_boost(self, boost: float):
        """창의성 부스트 설정 (1.0 = 기본, 1.5 = 높음, 2.0 = 매우 높음)"""
        self._flags.response_creativity_boost = boost
        self._flags.modified_by = f"creativity_boost_{boost}"
        self._flags.flags_set_at = datetime.now()

    def enable_debug_mode(self):
        """디버그 모드 활성화"""
        self._flags.debug_mode = True
        self._flags.log_persona_changes = True
        self._flags.trace_response_generation = True
        self._flags.modified_by = "debug_mode"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("debug_enabled")

    def reset_to_defaults(self):
        """기본값으로 리셋"""
        self._flags = EchoRuntimeFlags()
        self._flags.modified_by = "reset_to_defaults"
        self._flags.flags_set_at = datetime.now()

        self._notify_callbacks("reset_to_defaults")

    def get_flags(self) -> EchoRuntimeFlags:
        """현재 플래그 상태 반환"""
        return self._flags

    def is_free_speak_enabled(self) -> bool:
        """Free-speak 모드 활성화 여부"""
        return self._flags.free_speak_enabled

    def should_bypass_templates(self) -> bool:
        """템플릿 바이패스 여부"""
        return self._flags.template_bypass

    def should_use_dynamic_personas(self) -> bool:
        """동적 페르소나 사용 여부"""
        return self._flags.dynamic_persona_mixing

    def get_response_params(self) -> Dict[str, float]:
        """응답 생성 파라미터"""
        return {
            "temperature": self._flags.response_temperature,
            "top_p": self._flags.response_top_p,
            "creativity_boost": self._flags.response_creativity_boost,
        }

    def register_callback(self, event: str, callback):
        """이벤트 콜백 등록"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def _notify_callbacks(self, event: str):
        """이벤트 콜백 실행"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(self._flags)
                except Exception as e:
                    if self._flags.debug_mode:
                        print(f"Callback error for {event}: {e}")

    def get_status_summary(self) -> str:
        """상태 요약 반환"""
        flags = self._flags

        status_lines = [
            f"🚀 Echo Runtime Flags Status (Modified: {flags.flags_set_at.strftime('%H:%M:%S')})",
            f"   Modified by: {flags.modified_by}",
            "",
            f"🗣️  Free-speak enabled: {'✅' if flags.free_speak_enabled else '❌'}",
            f"📝 Template bypass: {'✅' if flags.template_bypass else '❌'}",
            f"🎭 Dynamic personas: {'✅' if flags.dynamic_persona_mixing else '❌'}",
            f"🎯 Signature override: {'✅' if flags.signature_override_enabled else '❌'}",
            "",
            f"🎨 Response params:",
            f"   Temperature: {flags.response_temperature}",
            f"   Top-p: {flags.response_top_p}",
            f"   Creativity boost: {flags.response_creativity_boost}x",
            "",
            f"🔧 Debug mode: {'✅' if flags.debug_mode else '❌'}",
        ]

        return "\n".join(status_lines)


# 전역 플래그 관리자 인스턴스
runtime_flags = RuntimeFlagsManager()


# 편의 함수들
def enable_echo_free_speak(temperature: float = 0.8, top_p: float = 0.9):
    """Echo Free-speak 모드 활성화"""
    runtime_flags.enable_free_speak(temperature, top_p)


def disable_echo_templates():
    """Echo 템플릿 비활성화"""
    runtime_flags.disable_templates()


def enable_echo_dynamic_personas():
    """Echo 동적 페르소나 활성화"""
    runtime_flags.enable_dynamic_personas()


def is_echo_free_speak_mode() -> bool:
    """Free-speak 모드 여부 확인"""
    return runtime_flags.is_free_speak_enabled()


def get_echo_response_params() -> Dict[str, float]:
    """Echo 응답 파라미터 획득"""
    return runtime_flags.get_response_params()


def reset_echo_flags():
    """Echo 플래그 리셋"""
    runtime_flags.reset_to_defaults()


def echo_flags_status() -> str:
    """Echo 플래그 상태 요약"""
    return runtime_flags.get_status_summary()


# 환경변수 기반 초기화
def init_from_environment():
    """환경변수에서 플래그 초기화"""
    if os.getenv("ECHO_FREE_SPEAK", "").lower() == "true":
        enable_echo_free_speak()

    if os.getenv("ECHO_NO_TEMPLATES", "").lower() == "true":
        disable_echo_templates()

    if os.getenv("ECHO_DYNAMIC_PERSONAS", "").lower() == "true":
        enable_echo_dynamic_personas()

    if os.getenv("ECHO_DEBUG", "").lower() == "true":
        runtime_flags.enable_debug_mode()


# 모듈 로드 시 환경변수 확인
init_from_environment()

if __name__ == "__main__":
    # 테스트
    print("🚀 Echo Runtime Flags Test")
    print("=" * 40)

    print("\n1. 기본 상태:")
    print(echo_flags_status())

    print("\n2. Free-speak 모드 활성화:")
    enable_echo_free_speak(temperature=0.9, top_p=0.8)
    print(echo_flags_status())

    print("\n3. 동적 페르소나 활성화:")
    enable_echo_dynamic_personas()
    print(echo_flags_status())

    print("\n4. 리셋:")
    reset_echo_flags()
    print(echo_flags_status())
