#!/usr/bin/env python3
"""
API Server Launcher for EchoJudgmentSystem

Starts the FastAPI server for REST API access.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def run():
    """Launch API server"""
    print("🚀 Starting EchoJudgmentSystem API Server...")

    try:
        # Load configuration
        from echo_foundation.config import load_system_config

        config = load_system_config()

        api_config = config.get("api", {})
        host = api_config.get("host", "0.0.0.0")
        port = api_config.get("port", 8000)

        print(f"📡 API Server will run on http://{host}:{port}")
        print("📚 API Documentation: http://localhost:9000/docs")

        # Import and run API server (keeping original import for now)
        import api_server

        if hasattr(api_server, "run_server"):
            api_server.run_server()
        else:
            print("❌ Server runner not found in api_server.py")

    except ImportError as e:
        print(f"❌ Failed to import API server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
