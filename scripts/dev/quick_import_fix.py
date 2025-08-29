#!/usr/bin/env python3
"""
Quick Import Fix for EchoJudgmentSystem v10

A streamlined version of the import migrator for immediate fixes.
"""

import os
import re
from pathlib import Path


def fix_imports_in_file(file_path: Path) -> int:
    """Fix imports in a single file, return number of changes"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = 0

        # Key import fixes
        replacements = [
            # Foundation
            ("from src.echo_foundation.doctrine", "from src.echo_foundation.doctrine"),
            (
                "import src.echo_foundation.doctrine",
                "import src.echo_foundation.doctrine",
            ),
            # Core
            ("from echo_engine.judgment_engine", "from echo_engine.judgment_engine"),
            ("from echo_engine.persona_core", "from echo_engine.persona_core"),
            ("from echo_engine.reasoning", "from echo_engine.reasoning"),
            (
                "from echo_engine.loop_orchestrator",
                "from echo_engine.loop_orchestrator",
            ),
            # Config
            (
                "from src.echo_foundation.config.loader",
                "from src.echo_foundation.config.loader",
            ),
        ]

        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes += 1

        # Write if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        return changes

    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return 0


def main():
    """Fix imports in key files"""
    root = Path(".")

    # Focus on key files
    key_files = [
        "main.py",
        "main_new.py",
        "scripts/launch/start_console.py",
        "scripts/launch/start_api.py",
        "scripts/launch/start_dashboard.py",
    ]

    total_changes = 0

    for file_path in key_files:
        full_path = root / file_path
        if full_path.exists():
            changes = fix_imports_in_file(full_path)
            if changes > 0:
                print(f"✅ {file_path}: {changes} imports fixed")
                total_changes += changes

    print(f"\n📈 Total: {total_changes} imports fixed")


if __name__ == "__main__":
    main()
