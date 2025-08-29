#!/usr/bin/env python3
"""
Import Migration Script for EchoJudgmentSystem v10

Automatically updates import paths from old structure to new modular structure.
Handles the migration from echo_engine to the new src/ modular architecture.

Usage:
    python scripts/dev/migrate_imports.py --dry-run    # Preview changes
    python scripts/dev/migrate_imports.py --apply      # Apply changes
    python scripts/dev/migrate_imports.py --backup     # Create backups
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json


class ImportMigrator:
    """Handles automated import path migration"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / ".migration_backup"

        # Import mapping from old to new structure
        self.import_mappings = {
            # Foundation mappings
            "from src.echo_foundation.doctrine": "from src.echo_foundation.doctrine",
            "import src.echo_foundation.doctrine": "import src.echo_foundation.doctrine",
            # Core engine mappings
            "from echo_engine.judgment_engine": "from echo_engine.judgment_engine",
            "from echo_engine.persona_core": "from echo_engine.persona_core",
            "from echo_engine.reasoning": "from echo_engine.reasoning",
            "from echo_engine.emotion_infer": "from echo_engine.emotion_infer",
            "from echo_engine.strategic_predictor": "from echo_engine.strategic_predictor",
            "from echo_engine.loop_orchestrator": "from echo_engine.loop_orchestrator",
            # FIST templates
            "from echo_engine.fist_templates": "from echo_engine.fist_templates",
            "from echo_engine.fist_templates.fist_core": "from echo_engine.fist_templates.fist_core",
            "from echo_engine.fist_templates.template_engine": "from echo_engine.fist_templates.template_engine",
            # Learning system mappings
            "from echo_engine.reinforcement_engine": "from echo_engine.reinforcement_engine",
            "from echo_engine.qtable_rl": "from echo_engine.qtable_rl",
            "from echo_engine.adaptive_learning_engine": "from echo_engine.adaptive_learning_engine",
            "from echo_engine.replay_learning": "from echo_engine.replay_learning",
            "from echo_engine.weight_optimizer": "from echo_engine.weight_optimizer",
            # Memory system mappings
            "from echo_engine.echo_hippocampus": "from echo_engine.echo_hippocampus",
            "from echo_engine.seed_kernel": "from echo_engine.seed_kernel",
            "from echo_engine.phantom_pain_detector": "from echo_engine.phantom_pain_detector",
            # LLM-free mappings
            "from echo_engine.llm_free": "from echo_engine.llm_free",
            # Meta-cognition mappings
            "from echo_engine.echo_audit_system": "from echo_engine.echo_audit_system",
            "from echo_engine.signature_performance_reporter": "from echo_engine.signature_performance_reporter",
            "from echo_engine.temporal_echo_tracker": "from echo_engine.temporal_echo_tracker",
            "from echo_engine.evolution.meta_evolution_orchestrator": "from echo_engine.evolution.meta_evolution_orchestrator",
            "from echo_engine.logging.meta_log_enhanced": "from echo_engine.logging.meta_log_enhanced",
            "from echo_engine.flow_visualizer": "from echo_engine.flow_visualizer",
            # Services mappings
            "from echo_engine.claude_bridge": "from echo_engine.claude_bridge",
            "from echo_engine.echo_network": "from echo_engine.echo_network",
            "from api.echo_agent_api": "from api.echo_agent_api",
            # Configuration mappings
            "from src.echo_foundation.config.loader": "from src.echo_foundation.config.loader",
        }

        # Files to exclude from migration
        self.exclude_patterns = [
            "*.pyc",
            "__pycache__",
            ".git",
            "venv",
            "echo_venv",
            "echo_test_venv",
            "echo_dashboard_env",
            "node_modules",
            ".migration_backup",
        ]

        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "imports_updated": 0,
            "errors": [],
        }

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from migration"""
        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return True
        return False

    def create_backup(self, file_path: Path):
        """Create backup of file before modification"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)

        relative_path = file_path.relative_to(self.root_path)
        backup_path = self.backup_dir / relative_path

        # Ensure backup directory exists
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to backup
        shutil.copy2(file_path, backup_path)

    def migrate_file_imports(
        self, file_path: Path, dry_run: bool = False
    ) -> List[Tuple[str, str]]:
        """Migrate imports in a single file"""
        changes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply import mappings
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    changes.append((old_import, new_import))

            # Additional pattern-based replacements
            content = self.apply_pattern_replacements(content, changes)

            # Write changes if not dry run
            if not dry_run and content != original_content:
                self.create_backup(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stats["files_modified"] += 1

            if changes:
                self.stats["imports_updated"] += len(changes)

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.stats["errors"].append(error_msg)
            print(f"❌ {error_msg}")

        return changes

    def apply_pattern_replacements(
        self, content: str, changes: List[Tuple[str, str]]
    ) -> str:
        """Apply regex-based pattern replacements"""

        # Handle generic echo_engine imports
        pattern = r"from echo_engine\.([a-zA-Z_][a-zA-Z0-9_]*)"

        def replace_generic(match):
            module_name = match.group(1)

            # Map to appropriate new location based on module name
            if module_name in [
                "judgment_engine",
                "reasoning",
                "quantum_judgment_engine",
            ]:
                return f"from echo_engine.{module_name}"
            elif module_name in [
                "persona_core",
                "emotion_infer",
                "strategic_predictor",
            ]:
                return f"from echo_engine.{module_name}"
            elif (
                module_name.startswith("fist_")
                or module_name.startswith("rise_")
                or module_name.startswith("dir_")
            ):
                return f"from echo_engine.fist_templates.{module_name}"
            elif module_name in [
                "loop_orchestrator",
                "flow_writer",
                "integrated_judgment_flow",
            ]:
                return f"from echo_engine.{module_name}"
            elif module_name in ["reinforcement_engine", "qtable_rl", "reward_engine"]:
                return f"from echo_engine.{module_name}"
            elif module_name in [
                "adaptive_learning_engine",
                "replay_learning",
                "weight_optimizer",
            ]:
                return f"from echo_engine.{module_name}"
            elif (
                module_name.startswith("hippocampus")
                or module_name.startswith("seed")
                or module_name.startswith("phantom")
            ):
                return f"from echo_engine.{module_name}"
            elif module_name.startswith("llm_free"):
                return f"from echo_engine.llm_free.{module_name}"
            elif (
                module_name.startswith("meta_")
                or module_name.startswith("audit")
                or module_name.startswith("signature_")
            ):
                if "evolution" in module_name:
                    return f"from echo_engine.evolution.{module_name}"
                elif any(x in module_name for x in ["log", "logger"]):
                    return f"from echo_engine.logging.{module_name}"
                elif (
                    "performance" in module_name
                    or "temporal" in module_name
                    or "audit" in module_name
                ):
                    return f"from echo_engine.{module_name}"
                else:
                    return f"from echo_engine.{module_name}"
            elif (
                module_name.startswith("flow_")
                or module_name.startswith("quantum_")
                or module_name.startswith("manifest")
            ):
                return f"from echo_engine.{module_name}"
            elif (
                "claude" in module_name
                or "bridge" in module_name
                or "network" in module_name
            ):
                return f"from echo_engine.{module_name}"
            elif "api" in module_name:
                return f"from api.{module_name}"
            else:
                # Default to core if uncertain
                return f"from echo_engine.{module_name}"

        new_content = re.sub(pattern, replace_generic, content)

        # Track changes
        if new_content != content:
            changes.append(("generic echo_engine pattern", "modular structure"))

        return new_content

    def find_python_files(self) -> List[Path]:
        """Find all Python files to process"""
        python_files = []

        for file_path in self.root_path.rglob("*.py"):
            if not self.should_exclude_file(file_path):
                python_files.append(file_path)

        return python_files

    def migrate_all_files(self, dry_run: bool = False) -> Dict:
        """Migrate imports in all Python files"""
        python_files = self.find_python_files()

        print(f"🔍 Found {len(python_files)} Python files to process")

        if dry_run:
            print("🧪 DRY RUN - No changes will be applied")

        results = {}

        for file_path in python_files:
            self.stats["files_processed"] += 1
            changes = self.migrate_file_imports(file_path, dry_run)

            if changes:
                results[str(file_path)] = changes
                print(f"📝 {file_path}: {len(changes)} imports updated")
                if dry_run:
                    for old, new in changes[:3]:  # Show first 3 changes
                        print(f"  • {old[:60]}... → {new[:60]}...")
                    if len(changes) > 3:
                        print(f"  • ... and {len(changes) - 3} more")

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate migration report"""
        timestamp = datetime.now().isoformat()

        report = {
            "migration_timestamp": timestamp,
            "statistics": self.stats,
            "files_changed": list(results.keys()),
            "import_mappings_used": self.import_mappings,
            "errors": self.stats["errors"],
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def save_report(self, results: Dict):
        """Save migration report to file"""
        report_content = self.generate_report(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.root_path / f"migration_report_{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"📊 Migration report saved: {report_path}")

    def print_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 60)
        print("📈 MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"Imports updated: {self.stats['imports_updated']}")

        if self.stats["errors"]:
            print(f"Errors encountered: {len(self.stats['errors'])}")
            print("\nErrors:")
            for error in self.stats["errors"][:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(self.stats["errors"]) > 5:
                print(f"  • ... and {len(self.stats['errors']) - 5} more")
        else:
            print("✅ No errors encountered")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate import paths in EchoJudgmentSystem v10"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying them"
    )

    parser.add_argument("--apply", action="store_true", help="Apply import migrations")

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backups of all files (implied with --apply)",
    )

    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Root directory to process (default: current directory)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not (args.dry_run or args.apply):
        print("❌ Must specify either --dry-run or --apply")
        parser.print_help()
        sys.exit(1)

    # Initialize migrator
    migrator = ImportMigrator(args.root)

    print("🚀 EchoJudgmentSystem v10 Import Migration")
    print(f"📁 Root directory: {migrator.root_path.absolute()}")

    if args.backup or args.apply:
        print(f"💾 Backup directory: {migrator.backup_dir}")

    # Run migration
    try:
        results = migrator.migrate_all_files(dry_run=args.dry_run)

        # Save report
        migrator.save_report(results)

        # Print summary
        migrator.print_summary()

        if args.dry_run and results:
            print("\n💡 Run with --apply to make these changes permanent")
        elif args.apply:
            print("\n✅ Migration completed successfully!")

    except KeyboardInterrupt:
        print("\n⏹️ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
