#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Configuration Loader
YAML-based configuration management
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(path: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = Path(path)

    if not config_path.is_absolute():
        # 상대 경로인 경우 echogpt 디렉토리 기준으로 처리
        base_dir = Path(__file__).parent.parent
        config_path = base_dir / path

    try:
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 환경 변수 치환
        config = _substitute_env_vars(config)

        return config

    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML configuration: {e}")


def _substitute_env_vars(config: Any) -> Any:
    """환경 변수 치환 (${VAR_NAME} 형식)"""
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # ${VAR_NAME} 형식의 환경 변수 치환
        import re

        def replace_env(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # 없으면 원본 반환

        return re.sub(r"\$\{([^}]+)\}", replace_env, config)
    else:
        return config


def get_default_config() -> Dict[str, Any]:
    """기본 설정 반환"""
    return {
        "name": "EchoGPT",
        "mode": "local_first",
        "latency_guard": {"intent_timeout_s": 3.5, "tool_timeout_ms": 2500},
        "teacher": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.0,
            "max_tokens": 300,
        },
        "distill": {"enabled": False, "agree_min_conf": 0.75},
        "privacy": {"redact_rules": []},
        "storage": {
            "events_dir": "meta_logs/traces",
            "model_dir": "models/intent_student",
        },
        "tools": {
            "web_search": {"enabled": True},
            "calc": {"enabled": True},
            "file_reader": {"enabled": True},
        },
    }
