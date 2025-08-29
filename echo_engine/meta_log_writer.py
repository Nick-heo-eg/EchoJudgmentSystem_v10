#!/usr/bin/env python3
"""
📝 Meta Log Writer - 누락된 모듈

다른 모듈들이 참조하는 meta_log_writer 모듈
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class MetaLogWriter:
    """메타 로그 작성기"""

    def __init__(self, log_file: str = "meta_logs/default.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def write_log(self, event_type: str, data: Dict[str, Any]) -> bool:
        """로그를 작성합니다."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data,
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            return True
        except Exception as e:
            print(f"⚠️ Meta log write failed: {e}")
            return False


# 글로벌 인스턴스
_default_writer = None


def get_meta_log_writer(log_file: str = None) -> MetaLogWriter:
    """메타 로그 작성기 인스턴스를 반환합니다."""
    global _default_writer
    if _default_writer is None or log_file:
        _default_writer = MetaLogWriter(log_file or "meta_logs/default.jsonl")
    return _default_writer


def write_meta_log(event_type: str, data: Dict[str, Any]) -> bool:
    """메타 로그를 작성하는 편의 함수"""
    writer = get_meta_log_writer()
    return writer.write_log(event_type, data)
