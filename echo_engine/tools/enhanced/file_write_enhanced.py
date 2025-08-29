# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class FileWriteTool:
    name = "file_write"
    description = "Write text content to a file. Creates parent dirs."
    schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or project-relative file path",
            },
            "content": {"type": "string", "description": "Text content to write"},
            "append": {
                "type": "boolean",
                "description": "Append instead of overwrite",
                "default": False,
            },
            "mkdirs": {
                "type": "boolean",
                "description": "Create parent dirs if missing",
                "default": True,
            },
            "encoding": {"type": "string", "default": "utf-8"},
        },
        "required": ["path", "content"],
    }

    def run(self, path, content, append=False, mkdirs=True, encoding="utf-8", **_):
        p = Path(path)
        if mkdirs:
            p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with p.open(mode, encoding=encoding, newline="\n") as f:
            f.write(content)
        return {"ok": True, "path": str(p), "bytes": len(content)}


async def run(
    path: str,
    content: str,
    append: bool = False,
    mkdirs: bool = True,
    encoding: str = "utf-8",
    **kwargs,
) -> Dict[str, Any]:
    """Enhanced File Write Tool"""

    # 🚀 Enhanced File Write 결과
    tool = FileWriteTool()
    result = tool.run(
        path=path, content=content, append=append, mkdirs=mkdirs, encoding=encoding
    )

    # Enhanced 결과 구조
    enhanced_result = {
        "ok": result["ok"],
        "module": "file_write_enhanced",
        "mode": "enhanced_file_operations",
        "version": "1.0.0-enhanced",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        # 파일 작업 결과
        "file_operation": {
            "path": result["path"],
            "size_bytes": result["bytes"],
            "operation": "append" if append else "write",
            "encoding": encoding,
            "parent_dirs_created": mkdirs,
        },
        # 메타데이터
        "metadata": {
            "absolute_path": str(Path(path).resolve()),
            "file_exists": Path(path).exists(),
            "is_text_file": True,
            "creation_time": datetime.utcnow().isoformat() + "Z",
        },
    }

    return enhanced_result
