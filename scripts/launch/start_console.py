#!/usr/bin/env python3
"""
Console Interface Launcher for EchoJudgmentSystem

Starts the interactive console interface for direct system interaction.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def run():
    """Launch console interface"""
    print("🖥️ Starting EchoJudgmentSystem Console Interface...")

    try:
        # Import main system (keeping original import for now)
        import main

        print("✅ Console interface loaded")
        print("💬 Type '/help' for available commands")

        # Run main interface
        if hasattr(main, "main"):
            main.main()
        else:
            print("❌ Main interface not found in main.py")

    except ImportError as e:
        print(f"❌ Failed to import main system: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start console: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
