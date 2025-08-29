"""
🎨 Echo Capsule Editor
UI 또는 CLI 기반에서 캡슐 내용을 생성, 수정, 시각화하는 편집기
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class EchoCapsuleEditor:
    def __init__(self, capsules_dir: str = "capsules"):
        self.capsules_dir = Path(capsules_dir)
        self.capsules_dir.mkdir(exist_ok=True)

    def edit_capsule(self, capsule_id: str, updates: Dict[str, Any]) -> bool:
        """캡슐 내용을 편집하고 저장"""
        print(f"📝 Editing Capsule: {capsule_id} with {updates}")

        capsule_path = self.capsules_dir / f"{capsule_id}.yaml"

        # 기존 캡슐 로드 또는 새로 생성
        if capsule_path.exists():
            with open(capsule_path, "r", encoding="utf-8") as f:
                capsule_data = yaml.safe_load(f)
        else:
            capsule_data = {
                "capsule": {
                    "id": capsule_id,
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "status": "active",
                    "echo_type": "judgment_capsule",
                }
            }

        # 업데이트 적용
        for key, value in updates.items():
            if key in ["topic", "content", "tags", "source"]:
                capsule_data["capsule"][key] = value
            elif key == "embedding":
                capsule_data["capsule"]["embedding"] = value
            elif key == "mapped_position":
                capsule_data["capsule"]["mapped_position"] = value

        # 수정 시간 기록
        capsule_data["capsule"]["modified"] = datetime.now().isoformat()

        # 저장
        with open(capsule_path, "w", encoding="utf-8") as f:
            yaml.dump(capsule_data, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ Capsule {capsule_id} saved successfully")
        return True

    def create_capsule(self, topic: str, content: str, tags: List[str] = None) -> str:
        """새 캡슐 생성"""
        capsule_id = (
            f"{topic.lower().replace(' ', '_')}_{datetime.now().strftime('%m%d')}"
        )

        capsule_data = {
            "capsule": {
                "id": capsule_id,
                "topic": topic,
                "content": content,
                "tags": tags or [],
                "created": datetime.now().strftime("%Y-%m-%d"),
                "status": "active",
                "echo_type": "judgment_capsule",
                "source": "EchoCapsuleEditor",
            }
        }

        capsule_path = self.capsules_dir / f"{capsule_id}.yaml"
        with open(capsule_path, "w", encoding="utf-8") as f:
            yaml.dump(capsule_data, f, default_flow_style=False, allow_unicode=True)

        print(f"🆕 Created new capsule: {capsule_id}")
        return capsule_id

    def visualize_capsule(self, capsule_id: str) -> Dict[str, Any]:
        """캡슐 내용을 시각화 형태로 반환"""
        capsule_path = self.capsules_dir / f"{capsule_id}.yaml"

        if not capsule_path.exists():
            print(f"❌ Capsule {capsule_id} not found")
            return {}

        with open(capsule_path, "r", encoding="utf-8") as f:
            capsule_data = yaml.safe_load(f)

        # 시각화 형태로 정리
        visualization = {
            "id": capsule_data["capsule"]["id"],
            "topic": capsule_data["capsule"].get("topic", "Unknown"),
            "content_preview": capsule_data["capsule"].get("content", "")[:100] + "...",
            "tags": capsule_data["capsule"].get("tags", []),
            "status": capsule_data["capsule"].get("status", "unknown"),
            "created": capsule_data["capsule"].get("created", "N/A"),
            "embedding_available": "embedding" in capsule_data["capsule"],
            "mapped_position": capsule_data["capsule"].get("mapped_position"),
        }

        print(f"👁️  Visualizing capsule: {capsule_id}")
        print(json.dumps(visualization, indent=2, ensure_ascii=False))

        return visualization

    def list_capsules(self) -> List[str]:
        """모든 캡슐 목록 반환"""
        capsules = []
        for capsule_file in self.capsules_dir.glob("*.yaml"):
            capsule_id = capsule_file.stem
            capsules.append(capsule_id)

        print(f"📋 Found {len(capsules)} capsules: {', '.join(capsules)}")
        return capsules


# CLI Interface
def main():
    editor = EchoCapsuleEditor()

    print("🎨 Echo Capsule Editor CLI")
    print("Commands: create, edit, view, list, quit")

    while True:
        command = input("\n> ").strip().lower()

        if command == "quit":
            break
        elif command == "list":
            editor.list_capsules()
        elif command.startswith("create"):
            topic = input("Topic: ")
            content = input("Content: ")
            tags = (
                input("Tags (comma-separated): ").split(",")
                if input("Tags? (y/n): ") == "y"
                else []
            )
            editor.create_capsule(topic, content, [t.strip() for t in tags])
        elif command.startswith("view"):
            capsule_id = input("Capsule ID: ")
            editor.visualize_capsule(capsule_id)
        elif command.startswith("edit"):
            capsule_id = input("Capsule ID: ")
            print("Enter updates (key=value format, 'done' to finish):")
            updates = {}
            while True:
                update = input("Update: ")
                if update.lower() == "done":
                    break
                if "=" in update:
                    key, value = update.split("=", 1)
                    updates[key.strip()] = value.strip()
            editor.edit_capsule(capsule_id, updates)


if __name__ == "__main__":
    main()
