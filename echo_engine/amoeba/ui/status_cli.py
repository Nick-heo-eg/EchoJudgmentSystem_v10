"""
🌌 CLI Status Display for Amoeba v0.2
명령줄 인터페이스 상태 출력
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager


def render_status(manager: AmoebaManager) -> str:
    """Amoeba 시스템 상태를 문자열로 렌더링"""

    output_lines = []

    # 헤더
    output_lines.append("=" * 50)
    output_lines.append("🌌 Amoeba v0.2 Status")
    output_lines.append("=" * 50)

    # 환경 정보
    env_info = manager.env_info
    adapter_name = manager.adapter.name if manager.adapter else "none"

    output_lines.append(
        f" Environment : {env_info.get('os', {}).get('system', 'Unknown')} ({env_info.get('python', {}).get('version', 'Unknown')})"
    )
    output_lines.append(f" Adapter     : {adapter_name}")

    # WSL/Docker 정보
    runtime_info = []
    if env_info.get("runtime", {}).get("is_wsl"):
        runtime_info.append("WSL")
    if env_info.get("runtime", {}).get("is_docker"):
        runtime_info.append("Docker")
    if env_info.get("runtime", {}).get("is_cloud"):
        cloud_provider = env_info["runtime"].get("provider", "Unknown")
        runtime_info.append(f"Cloud({cloud_provider.upper()})")

    if runtime_info:
        output_lines.append(f" Runtime     : {', '.join(runtime_info)}")

    # 링커 상태
    linker_status = manager.linker.get_status()
    fs_map = (
        "ON"
        if linker_status.get("wsl_enabled") or linker_status.get("docker_enabled")
        else "OFF"
    )
    docker_bridge = "ON" if linker_status.get("docker_enabled") else "OFF"

    output_lines.append(
        f" Linked      : fs_map={fs_map}, docker_bridge={docker_bridge}"
    )
    output_lines.append(f" Services    : {linker_status.get('services', 0)} registered")

    # 플러그인 상태
    if hasattr(manager, "plugins") and manager.plugins:
        plugin_status = manager.plugins.get_status()
        active_plugins = plugin_status.get("active_count", 0)
        failed_plugins = plugin_status.get("failed_count", 0)

        output_lines.append(
            f" Plugins     : {active_plugins} active, {failed_plugins} failed"
        )

        # 활성 플러그인 목록
        active_list = plugin_status.get("plugins", {}).get("active", {})
        if active_list:
            plugin_details = []
            for name, info in active_list.items():
                version = info.get("version", "0.1")
                status = "RUNNING" if info.get("started") else "LOADED"
                plugin_details.append(f"{name}({version}, {status})")

            # 한 줄에 출력하되, 너무 길면 줄바꿈
            plugins_str = ", ".join(plugin_details)
            if len(plugins_str) > 60:
                output_lines.append(" Plugin List :")
                for detail in plugin_details:
                    output_lines.append(f"             {detail}")
            else:
                output_lines.append(f" Plugin List : {plugins_str}")
    else:
        output_lines.append(" Plugins     : 0 active, 0 failed")

    # 텔레메트리 상태
    if hasattr(manager, "telemetry") and manager.telemetry:
        telemetry_enabled = manager.telemetry.collector.enabled
        telemetry_sink = manager.telemetry.collector.sink
        telemetry_path = (
            str(manager.telemetry.collector.log_path)
            if telemetry_sink == "file"
            else "N/A"
        )

        output_lines.append(
            f" Telemetry   : {'enabled' if telemetry_enabled else 'disabled'} ({telemetry_sink})"
        )
        if telemetry_sink == "file" and len(telemetry_path) < 50:
            output_lines.append(f" Log Path    : {telemetry_path}")
    else:
        output_lines.append(" Telemetry   : disabled")

    # 최적화 상태
    optimizer_report = manager.optimizer.get_optimization_report()
    optimizations = optimizer_report.get("optimizations_applied", [])
    optimization_count = len(optimizations)

    output_lines.append(f" Optimization: {optimization_count} applied")

    # 성능 메트릭 (있다면)
    metrics = optimizer_report.get("performance_metrics", {})
    if metrics:
        if "cpu_benchmark_ms" in metrics:
            cpu_bench = metrics["cpu_benchmark_ms"]
            output_lines.append(f" Performance : CPU={cpu_bench:.1f}ms")

        if "memory_percent" in metrics:
            mem_percent = metrics["memory_percent"]
            output_lines.append(f" Memory Usage: {mem_percent:.1f}%")

    # 상태 요약
    health_status = "OK"
    if failed_plugins > 0:
        health_status = "WARNING"
    if not manager.adapter:
        health_status = "ERROR"

    output_lines.append(f" Health      : {health_status}")

    # 타임스탬프
    output_lines.append("")
    output_lines.append(
        f" Generated   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    output_lines.append("=" * 50)

    return "\n".join(output_lines)


def print_status(manager: AmoebaManager):
    """상태를 콘솔에 출력"""
    status_text = render_status(manager)
    print(status_text)


def render_compact_status(manager: AmoebaManager) -> str:
    """간단한 한 줄 상태"""
    env_info = manager.env_info
    adapter_name = manager.adapter.name if manager.adapter else "none"

    # 기본 정보
    os_name = env_info.get("os", {}).get("system", "Unknown")
    python_version = env_info.get("python", {}).get("version", "Unknown")

    # 런타임 정보
    runtime_tags = []
    runtime = env_info.get("runtime", {})
    if runtime.get("is_wsl"):
        runtime_tags.append("WSL")
    if runtime.get("is_docker"):
        runtime_tags.append("Docker")
    if runtime.get("is_cloud"):
        runtime_tags.append(runtime.get("provider", "Cloud").upper())

    runtime_str = f"[{','.join(runtime_tags)}]" if runtime_tags else ""

    # 플러그인 수
    plugin_count = 0
    if hasattr(manager, "plugins") and manager.plugins:
        plugin_count = manager.plugins.get_status().get("active_count", 0)

    # 상태 구성
    status_parts = [
        f"Amoeba v0.2",
        f"{adapter_name}@{os_name}",
        f"Python{python_version}",
        runtime_str,
        f"{plugin_count}plugins",
    ]

    # 빈 부분 제거
    status_parts = [part for part in status_parts if part and part != "[]"]

    return " | ".join(status_parts)


def print_compact_status(manager: AmoebaManager):
    """간단한 상태를 콘솔에 출력"""
    compact_status = render_compact_status(manager)
    print(f"🌌 {compact_status}")


def main():
    """CLI 진입점"""
    # 이 함수는 실제로는 main.py에서 --amoeba-status로 호출됨
    print("Use 'python main.py --amoeba-status' to view status")


if __name__ == "__main__":
    main()
