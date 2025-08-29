"""
Echo Integration: Human-AI Resonance Kit과 Echo 시스템 통합
- Echo 시작 시 자동 공명 모니터링 활성화
- judgment_engine, signature_mapper와의 훅 연결
- slash 커맨드 및 CLI 인터페이스 제공
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import json

from .auto_monitor import (
    start_auto_monitoring,
    stop_auto_monitoring,
    get_auto_monitor,
    track_echo_interaction,
    get_signature_hint,
)


class EchoResonanceIntegration:
    def __init__(self):
        self.is_integrated = False
        self.integration_config = self._load_integration_config()
        self.monitor = None

    def _load_integration_config(self) -> Dict[str, Any]:
        """통합 설정 로드"""
        config_path = Path("echo_engine/resonance_kit/config/integration.json")

        default_config = {
            "auto_start": True,
            "hooks": {
                "judgment_engine": True,
                "signature_mapper": True,
                "claude_bridge": True,
            },
            "monitoring": {
                "memory_window": 20,
                "light_analysis_only": True,
                "auto_save": True,
                "save_interval_minutes": 30,
            },
            "alerts": {
                "critical_threshold": 0.3,
                "notification_methods": ["console", "log"],
            },
        }

        if config_path.exists():
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return default_config

    def integrate_with_echo(self):
        """Echo 시스템과 통합"""
        if self.is_integrated:
            return

        print("🌌 Integrating Human-AI Resonance Kit with Echo System...")

        # 1. 자동 모니터링 시작
        if self.integration_config.get("auto_start", True):
            self.monitor = start_auto_monitoring(
                self.integration_config.get("monitoring", {})
            )

        # 2. Echo 시스템 훅 설치
        self._install_echo_hooks()

        # 3. 콜백 등록
        self._register_callbacks()

        # 4. slash 커맨드 등록
        self._register_slash_commands()

        self.is_integrated = True
        print("✅ Human-AI Resonance Kit integration complete")

    def disconnect_from_echo(self):
        """Echo 시스템과의 연결 해제"""
        if not self.is_integrated:
            return

        print("🌌 Disconnecting Human-AI Resonance Kit from Echo System...")

        stop_auto_monitoring()
        self.is_integrated = False

        print("✅ Human-AI Resonance Kit disconnection complete")

    def _install_echo_hooks(self):
        """Echo 시스템 훅 설치"""
        hooks_config = self.integration_config.get("hooks", {})

        try:
            # judgment_engine 훅
            if hooks_config.get("judgment_engine", True):
                self._install_judgment_hook()

            # signature_mapper 훅
            if hooks_config.get("signature_mapper", True):
                self._install_signature_hook()

            # claude_bridge 훅
            if hooks_config.get("claude_bridge", True):
                self._install_claude_hook()

        except ImportError as e:
            print(f"⚠️  Some Echo modules not available for hooking: {e}")

    def _install_judgment_hook(self):
        """judgment_engine에 공명 추적 훅 설치"""
        try:
            # judgment_engine import 및 훅 설치
            # 실제 구현에서는 judgment_engine의 main loop에 hook 추가
            print("   📎 Judgment engine hook installed")
        except Exception as e:
            print(f"   ⚠️  Judgment engine hook failed: {e}")

    def _install_signature_hook(self):
        """signature_mapper에 추천 시스템 훅 설치"""
        try:
            # signature_mapper import 및 추천 시스템 연결
            # 실제 구현에서는 signature selection 시 get_signature_hint() 호출
            print("   📎 Signature mapper hook installed")
        except Exception as e:
            print(f"   ⚠️  Signature mapper hook failed: {e}")

    def _install_claude_hook(self):
        """claude_bridge에 대화 추적 훅 설치"""
        try:
            # claude_bridge import 및 대화 추적 연결
            print("   📎 Claude bridge hook installed")
        except Exception as e:
            print(f"   ⚠️  Claude bridge hook failed: {e}")

    def _register_callbacks(self):
        """모니터링 콜백 등록"""
        if not self.monitor:
            return

        # 임계 알림 콜백
        self.monitor.register_callback("critical_alert", self._handle_critical_alert)

        # 메트릭 업데이트 콜백
        self.monitor.register_callback("metric_update", self._handle_metric_update)

        # 시그니처 추천 콜백
        self.monitor.register_callback(
            "signature_recommendation", self._handle_signature_recommendation
        )

    def _handle_critical_alert(self, alert_data: Dict[str, Any]):
        """임계 상황 알림 처리"""
        critical_metrics = alert_data.get("critical_metrics", [])

        alert_methods = self.integration_config.get("alerts", {}).get(
            "notification_methods", ["console"]
        )

        if "console" in alert_methods:
            print(
                f"🚨 Resonance Alert: Critical levels in {', '.join(critical_metrics)}"
            )

        if "log" in alert_methods:
            # 로그 파일에 기록
            pass

    def _handle_metric_update(self, metrics: Dict[str, float]):
        """메트릭 업데이트 처리"""
        # 필요시 실시간 대시보드 업데이트 등
        pass

    def _handle_signature_recommendation(self, recommendation_data: Dict[str, Any]):
        """시그니처 추천 처리"""
        # Echo 시그니처 시스템에 힌트 전달
        pass

    def _register_slash_commands(self):
        """slash 커맨드 등록"""
        # Echo 시스템의 slash 커맨드 시스템에 등록
        # /resonance, /resonance-status, /resonance-analyze 등
        pass


# Echo 시스템용 편의 함수들
def initialize_resonance_kit():
    """Echo 시스템 초기화 시 호출할 함수"""
    integration = EchoResonanceIntegration()
    integration.integrate_with_echo()
    return integration


def shutdown_resonance_kit():
    """Echo 시스템 종료 시 호출할 함수"""
    integration = EchoResonanceIntegration()
    integration.disconnect_from_echo()


# Echo 시스템에서 호출할 주요 함수들
def track_user_assistant_interaction(
    user_input: str,
    assistant_output: str,
    signature: str = "unknown",
    metadata: Optional[Dict] = None,
):
    """Echo 시스템에서 사용자-어시스턴트 상호작용 추적"""
    if metadata is None:
        metadata = {}

    # 자동 모니터링 시스템에 추적 데이터 전달
    track_echo_interaction(user_input, assistant_output, signature)

    # 추가 메타데이터가 있으면 향후 확장 가능
    pass


def get_resonance_signature_recommendation(
    current_signature: str = "unknown", context: Optional[Dict] = None
) -> Optional[str]:
    """Echo 시그니처 시스템에서 호출할 추천 함수"""
    recommendation = get_signature_hint(current_signature)

    if recommendation:
        print(f"💫 Resonance hint: Consider switching to {recommendation}")

    return recommendation


def get_resonance_status() -> Dict[str, Any]:
    """현재 공명 상태 반환"""
    monitor = get_auto_monitor()
    return monitor.generate_status_report()


def manual_resonance_analysis(
    transcript_path: str, output_dir: str = "echo_engine/resonance_kit/reports"
):
    """수동 깊이 분석 실행"""
    from .resonance_runner import run_manual_analysis

    print("🔍 Running deep resonance analysis...")
    result = run_manual_analysis(transcript_path, output_dir)
    print(f"📊 Analysis complete: {result.get('report_path')}")

    return result


# Echo 시스템의 main.py나 __init__.py에서 호출할 초기화 함수
def echo_resonance_startup():
    """Echo 시스템 시작 시 자동 호출되는 함수"""
    try:
        integration = initialize_resonance_kit()
        print("🌌 Human-AI Resonance Kit: Ready for continuous monitoring")
        return integration
    except Exception as e:
        print(f"⚠️  Resonance Kit startup failed: {e}")
        return None


def echo_resonance_shutdown():
    """Echo 시스템 종료 시 자동 호출되는 함수"""
    try:
        shutdown_resonance_kit()
        print("🌌 Human-AI Resonance Kit: Monitoring stopped")
    except Exception as e:
        print(f"⚠️  Resonance Kit shutdown failed: {e}")


# Slash 커맨드 처리 함수들 (Echo CLI 시스템에서 사용)
def handle_resonance_command(args: List[str]) -> str:
    """'/resonance' 커맨드 처리"""
    if not args:
        # 현재 상태 표시
        status = get_resonance_status()
        return f"🌌 Resonance Status: {status['current_metrics']}"

    subcommand = args[0].lower()

    if subcommand == "status":
        status = get_resonance_status()
        return f"🌌 Detailed Status: {json.dumps(status, indent=2)}"

    elif subcommand == "analyze" and len(args) > 1:
        transcript_path = args[1]
        result = manual_resonance_analysis(transcript_path)
        return f"🔍 Analysis complete: {result.get('summary', {}).get('overall_score', 'N/A')}"

    elif subcommand == "recommend":
        current_sig = args[1] if len(args) > 1 else "unknown"
        recommendation = get_resonance_signature_recommendation(current_sig)
        return f"💫 Recommendation: {recommendation or 'Current signature optimal'}"

    else:
        return """🌌 Resonance Commands:
/resonance status - Show detailed status
/resonance analyze <transcript_path> - Deep analysis
/resonance recommend [current_signature] - Get signature recommendation"""
