#!/usr/bin/env python3
"""
Dashboard Launcher for EchoJudgmentSystem

Starts the Streamlit dashboard for web-based monitoring and control.
"""

import sys
import subprocess
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def run():
    """Launch dashboard"""
    print("📊 Starting EchoJudgmentSystem Dashboard...")

    try:
        # Load configuration
        from echo_foundation.config import load_system_config

        config = load_system_config()

        dashboard_config = config.get("dashboard", {})
        host = dashboard_config.get("host", "0.0.0.0")
        port = dashboard_config.get("port", 8501)

        print(f"🌐 Dashboard will run on http://{host}:{port}")

        # Find dashboard file
        dashboard_path = Path("streamlit_ui/comprehensive_dashboard.py")
        if not dashboard_path.exists():
            dashboard_path = Path("src/echo_services/web/dashboard/main.py")

        if not dashboard_path.exists():
            print("❌ Dashboard file not found")
            sys.exit(1)

        # Launch Streamlit
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path),
            "--server.address",
            host,
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ]

        print(f"🚀 Launching: {' '.join(cmd)}")
        subprocess.run(cmd)

    except ImportError as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
