"""
🌌 Environment Detection for Amoeba v0.2
환경별 세부 감지 및 특성 분석
"""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


def detect_wsl() -> Dict[str, Any]:
    """WSL 환경 감지"""
    info = {"is_wsl": False, "version": None, "distro": None}

    try:
        # Method 1: /proc/version check
        if Path("/proc/version").exists():
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info:
                    info["is_wsl"] = True
                    if "wsl2" in version_info:
                        info["version"] = "2"
                    else:
                        info["version"] = "1"

        # Method 2: WSL environment variables
        if os.getenv("WSL_DISTRO_NAME"):
            info["is_wsl"] = True
            info["distro"] = os.getenv("WSL_DISTRO_NAME")

        # Method 3: uname check
        if not info["is_wsl"] and platform.system() == "Linux":
            try:
                uname = subprocess.check_output(["uname", "-r"], text=True).lower()
                if "microsoft" in uname:
                    info["is_wsl"] = True
            except subprocess.SubprocessError:
                pass

    except Exception:
        pass

    return info


def detect_docker() -> Dict[str, Any]:
    """Docker 환경 감지"""
    info = {"is_docker": False, "container_id": None, "runtime": None}

    try:
        # Method 1: /.dockerenv file
        if Path("/.dockerenv").exists():
            info["is_docker"] = True

        # Method 2: cgroup check
        if Path("/proc/1/cgroup").exists():
            with open("/proc/1/cgroup", "r") as f:
                cgroup_info = f.read()
                if "docker" in cgroup_info or "containerd" in cgroup_info:
                    info["is_docker"] = True
                    # Extract container ID if possible
                    for line in cgroup_info.split("\n"):
                        if "docker" in line:
                            parts = line.split("/")
                            if len(parts) > 1:
                                info["container_id"] = parts[-1][:12]  # First 12 chars
                            break

        # Method 3: Docker runtime detection
        if info["is_docker"]:
            runtime_path = Path("/proc/1/environ")
            if runtime_path.exists():
                with open(runtime_path, "rb") as f:
                    environ = f.read().decode("utf-8", errors="ignore")
                    if "DOCKER" in environ:
                        info["runtime"] = "docker"
                    elif "containerd" in environ:
                        info["runtime"] = "containerd"

    except Exception:
        pass

    return info


def detect_cloud() -> Dict[str, Any]:
    """클라우드 환경 감지"""
    info = {"is_cloud": False, "provider": None, "instance_type": None}

    try:
        # AWS detection
        if Path("/sys/hypervisor/uuid").exists():
            with open("/sys/hypervisor/uuid", "r") as f:
                uuid = f.read().strip()
                if uuid.startswith("ec2"):
                    info["is_cloud"] = True
                    info["provider"] = "aws"

        # Azure detection
        if Path("/sys/class/dmi/id/sys_vendor").exists():
            with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                vendor = f.read().strip().lower()
                if "microsoft corporation" in vendor:
                    info["is_cloud"] = True
                    info["provider"] = "azure"

        # GCP detection
        try:
            result = subprocess.check_output(
                [
                    "curl",
                    "-s",
                    "-H",
                    "Metadata-Flavor: Google",
                    "http://metadata.google.internal/computeMetadata/v1/instance/machine-type",
                ],
                timeout=2,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if result:
                info["is_cloud"] = True
                info["provider"] = "gcp"
                info["instance_type"] = result.split("/")[-1]
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass

    except Exception:
        pass

    return info


def detect_gpu() -> Dict[str, Any]:
    """GPU 감지"""
    info = {"has_gpu": False, "gpus": [], "cuda_version": None}

    try:
        # NVIDIA GPU detection
        try:
            result = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if result.strip():
                info["has_gpu"] = True
                for line in result.strip().split("\n"):
                    name, memory = line.split(", ")
                    info["gpus"].append(
                        {"name": name.strip(), "memory_mb": int(memory)}
                    )

                # Get CUDA version
                cuda_result = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=driver_version",
                        "--format=csv,noheader",
                    ],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                if cuda_result.strip():
                    info["cuda_version"] = cuda_result.strip()

        except subprocess.SubprocessError:
            pass

        # AMD GPU detection (basic)
        if not info["has_gpu"]:
            try:
                result = subprocess.check_output(
                    ["lspci"], stderr=subprocess.DEVNULL, text=True
                )
                for line in result.split("\n"):
                    if "VGA compatible controller" in line and (
                        "AMD" in line or "ATI" in line
                    ):
                        info["has_gpu"] = True
                        info["gpus"].append(
                            {"name": line.split(": ")[-1], "type": "amd"}
                        )
            except subprocess.SubprocessError:
                pass

    except Exception:
        pass

    return info


def detect_comprehensive_environment() -> Dict[str, Any]:
    """종합적 환경 감지"""
    env_info = {
        "timestamp": platform.node(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": os.path.realpath(os.__file__).split("lib")[0],
        },
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "runtime": {},
        "capabilities": {},
    }

    # 각 환경 감지
    wsl_info = detect_wsl()
    docker_info = detect_docker()
    cloud_info = detect_cloud()
    gpu_info = detect_gpu()

    # 통합
    env_info["runtime"].update(wsl_info)
    env_info["runtime"].update(docker_info)
    env_info["runtime"].update(cloud_info)
    env_info["capabilities"].update(gpu_info)

    # 기본 파일시스템 정보
    env_info["filesystem"] = {
        "cwd": os.getcwd(),
        "home": os.path.expanduser("~"),
        "tmp": os.path.abspath(
            os.path.expandvars("$TMPDIR")
            if os.getenv("TMPDIR")
            else os.path.join(tempfile.gettempdir())
        ),
    }

    return env_info
