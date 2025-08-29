#!/usr/bin/env python3
"""
⚙️ EchoJudgmentSystem v10 - Config Manager
Mistral 통합 및 Fusion Judgment을 위한 설정 관리 시스템

기능:
- YAML 설정 파일 로딩
- 환경변수 오버라이드 지원
- 런타임 설정 업데이트
- 설정 검증 및 기본값 적용
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class MistralConfig:
    """Mistral 설정"""

    enabled: bool = True
    mode: str = "local"  # local, api, hybrid
    model_path: str = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    device: str = "auto"
    temperature: float = 0.7
    max_tokens: int = 512
    api_key: Optional[str] = None


@dataclass
class FusionConfig:
    """Fusion Judgment 설정"""

    default_providers: List[str] = field(
        default_factory=lambda: ["mistral", "echo_internal"]
    )
    default_strategy: str = "weighted_average"
    timeout: float = 30.0
    parallel_execution: bool = True
    provider_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class EchoConfig:
    """전체 Echo 시스템 설정"""

    mistral: MistralConfig = field(default_factory=MistralConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    development: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """⚙️ 설정 관리자"""

    def __init__(self, config_path: Union[str, Path] = None):
        self.config_path = (
            Path(config_path) if config_path else self._find_config_file()
        )
        self._config = {}
        self._last_modified = None

        # 환경변수 매핑
        self.env_mappings = {
            "MISTRAL_API_KEY": "mistral.api.api_key",
            "ANTHROPIC_API_KEY": "llm_providers.claude.api_key",
            "OPENAI_API_KEY": "llm_providers.gpt.api_key",
            "PERPLEXITY_API_KEY": "llm_providers.perplexity.api_key",
            "ECHO_DEBUG": "development.debug_mode",
            "ECHO_VERBOSE": "development.verbose_logging",
        }

        self.load_config()
        logger.info(f"⚙️ ConfigManager 초기화: {self.config_path}")

    def _find_config_file(self) -> Path:
        """설정 파일 자동 검색"""

        possible_paths = [
            Path("config/mistral_config.yaml"),
            Path("../config/mistral_config.yaml"),
            Path("echo_engine/config/mistral_config.yaml"),
            Path("./mistral_config.yaml"),
        ]

        for path in possible_paths:
            if path.exists():
                return path.resolve()

        # 기본 설정 파일 생성
        default_path = Path("config/mistral_config.yaml")
        default_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_default_config(default_path)
        return default_path

    def _create_default_config(self, path: Path):
        """기본 설정 파일 생성"""
        default_config = {
            "mistral": {
                "enabled": True,
                "mode": "local",
                "local": {
                    "model_path": "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                    "device": "auto",
                },
                "judgment": {"temperature": 0.7, "max_tokens": 512},
            },
            "fusion": {
                "default_providers": ["mistral", "echo_internal"],
                "default_strategy": "weighted_average",
                "timeout": 30.0,
            },
            "development": {"debug_mode": False, "verbose_logging": False},
        }

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"✅ 기본 설정 파일 생성: {path}")

    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로딩"""

        try:
            if not self.config_path.exists():
                logger.warning(f"⚠️ 설정 파일 없음: {self.config_path}")
                self._config = self._get_default_config()
                return self._config

            # 파일 수정 시간 확인
            current_modified = self.config_path.stat().st_mtime
            if self._last_modified and current_modified == self._last_modified:
                return self._config  # 변경 없음

            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

            self._last_modified = current_modified

            # 환경변수 오버라이드 적용
            self._apply_environment_overrides()

            # 설정 검증 및 기본값 적용
            self._validate_and_apply_defaults()

            logger.info(f"✅ 설정 로딩 완료: {self.config_path}")
            return self._config

        except Exception as e:
            logger.error(f"❌ 설정 로딩 실패: {e}")
            self._config = self._get_default_config()
            return self._config

    def _apply_environment_overrides(self):
        """환경변수 기반 설정 오버라이드"""

        for env_var, config_path in self.env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(self._config, config_path, env_value)
                logger.debug(f"환경변수 오버라이드: {env_var} -> {config_path}")

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any):
        """중첩 딕셔너리에 값 설정"""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # 타입 변환
        if isinstance(value, str):
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)

        current[keys[-1]] = value

    def _validate_and_apply_defaults(self):
        """설정 검증 및 기본값 적용"""

        # Mistral 기본값
        mistral_defaults = {
            "enabled": True,
            "mode": "local",
            "judgment": {
                "temperature": 0.7,
                "max_tokens": 512,
                "top_p": 0.9,
                "do_sample": True,
            },
        }

        self._config.setdefault("mistral", {})
        self._apply_defaults(self._config["mistral"], mistral_defaults)

        # Fusion 기본값
        fusion_defaults = {
            "default_providers": ["mistral", "echo_internal"],
            "default_strategy": "weighted_average",
            "timeout": 30.0,
            "parallel_execution": True,
            "provider_weights": {
                "mistral": 0.4,
                "claude": 0.3,
                "echo_internal": 0.2,
                "gpt": 0.25,
                "perplexity": 0.2,
            },
        }

        self._config.setdefault("fusion", {})
        self._apply_defaults(self._config["fusion"], fusion_defaults)

        # Development 기본값
        dev_defaults = {
            "debug_mode": False,
            "verbose_logging": False,
            "mock_mode": False,
        }

        self._config.setdefault("development", {})
        self._apply_defaults(self._config["development"], dev_defaults)

    def _apply_defaults(self, config: Dict[str, Any], defaults: Dict[str, Any]):
        """기본값 적용 (재귀적)"""
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                self._apply_defaults(config[key], value)

    def _get_default_config(self) -> Dict[str, Any]:
        """최소 기본 설정 반환"""
        return {
            "mistral": {
                "enabled": True,
                "mode": "local",
                "judgment": {"temperature": 0.7, "max_tokens": 512},
            },
            "fusion": {
                "default_providers": ["echo_internal"],
                "default_strategy": "weighted_average",
            },
            "development": {"debug_mode": False},
        }

    def get_config(self, path: str = None) -> Union[Dict[str, Any], Any]:
        """설정값 조회"""

        if path is None:
            return self._config

        keys = path.split(".")
        current = self._config

        try:
            for key in keys:
                current = current[key]
            return current
        except KeyError:
            logger.warning(f"⚠️ 설정 경로 없음: {path}")
            return None

    def set_config(self, path: str, value: Any):
        """설정값 변경"""
        self._set_nested_value(self._config, path, value)
        logger.info(f"설정 변경: {path} = {value}")

    def get_mistral_config(self) -> MistralConfig:
        """Mistral 설정 객체 반환"""
        mistral_config = self.get_config("mistral") or {}

        return MistralConfig(
            enabled=mistral_config.get("enabled", True),
            mode=mistral_config.get("mode", "local"),
            model_path=mistral_config.get("local", {}).get(
                "model_path", "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
            ),
            device=mistral_config.get("local", {}).get("device", "auto"),
            temperature=mistral_config.get("judgment", {}).get("temperature", 0.7),
            max_tokens=mistral_config.get("judgment", {}).get("max_tokens", 512),
            api_key=mistral_config.get("api", {}).get("api_key"),
        )

    def get_fusion_config(self) -> FusionConfig:
        """Fusion 설정 객체 반환"""
        fusion_config = self.get_config("fusion") or {}

        return FusionConfig(
            default_providers=fusion_config.get(
                "default_providers", ["mistral", "echo_internal"]
            ),
            default_strategy=fusion_config.get("default_strategy", "weighted_average"),
            timeout=fusion_config.get("timeout", 30.0),
            parallel_execution=fusion_config.get("parallel_execution", True),
            provider_weights=fusion_config.get("provider_weights", {}),
        )

    def is_provider_enabled(self, provider: str) -> bool:
        """LLM 제공자 활성화 상태 확인"""

        if provider == "mistral":
            return self.get_config("mistral.enabled") == True
        elif provider == "echo_internal":
            return True  # 항상 사용 가능
        else:
            return self.get_config(f"llm_providers.{provider}.enabled") == True

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """제공자별 설정 반환"""

        if provider == "mistral":
            return self.get_config("mistral") or {}
        elif provider == "echo_internal":
            return self.get_config("llm_providers.echo_internal") or {"enabled": True}
        else:
            return self.get_config(f"llm_providers.{provider}") or {}

    def get_signature_config(self, signature: str) -> Dict[str, Any]:
        """시그니처별 설정 반환"""
        return self.get_config(f"mistral.signatures.{signature}") or {}

    def reload_config(self):
        """설정 파일 다시 로딩"""
        self._last_modified = None  # 강제 리로드
        return self.load_config()

    def save_config(self, backup: bool = True):
        """현재 설정을 파일에 저장"""

        try:
            if backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix(
                    f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
                )
                import shutil

                shutil.copy2(self.config_path, backup_path)
                logger.info(f"설정 백업 생성: {backup_path}")

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"✅ 설정 저장 완료: {self.config_path}")

        except Exception as e:
            logger.error(f"❌ 설정 저장 실패: {e}")
            raise

    def validate_config(self) -> List[str]:
        """설정 유효성 검사"""
        errors = []

        # Mistral 설정 검증
        mistral_config = self.get_config("mistral")
        if mistral_config and mistral_config.get("enabled"):
            mode = mistral_config.get("mode", "local")

            if mode == "local":
                model_path = mistral_config.get("local", {}).get("model_path")
                if model_path and not Path(model_path).exists():
                    errors.append(f"Mistral 로컬 모델 파일 없음: {model_path}")

            elif mode == "api":
                api_key = mistral_config.get("api", {}).get("api_key")
                if not api_key and not os.getenv("MISTRAL_API_KEY"):
                    errors.append("Mistral API 키가 설정되지 않음")

        # Fusion 설정 검증
        fusion_config = self.get_config("fusion")
        if fusion_config:
            providers = fusion_config.get("default_providers", [])
            if not providers:
                errors.append("기본 LLM 제공자가 설정되지 않음")

            strategy = fusion_config.get("default_strategy")
            valid_strategies = [
                "weighted_average",
                "confidence_based",
                "majority_vote",
                "signature_optimized",
            ]
            if strategy not in valid_strategies:
                errors.append(f"유효하지 않은 융합 전략: {strategy}")

        return errors

    def get_debug_info(self) -> Dict[str, Any]:
        """디버그 정보 반환"""
        return {
            "config_path": str(self.config_path),
            "config_exists": self.config_path.exists(),
            "last_modified": self._last_modified,
            "environment_overrides": {
                env_var: os.getenv(env_var) is not None
                for env_var in self.env_mappings.keys()
            },
            "validation_errors": self.validate_config(),
            "mistral_enabled": self.is_provider_enabled("mistral"),
            "providers_enabled": {
                provider: self.is_provider_enabled(provider)
                for provider in [
                    "mistral",
                    "claude",
                    "gpt",
                    "perplexity",
                    "echo_internal",
                ]
            },
        }


# 전역 설정 관리자 인스턴스
_config_manager = None


def get_config_manager(config_path: Union[str, Path] = None) -> ConfigManager:
    """설정 관리자 싱글톤 인스턴스"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(path: str = None) -> Union[Dict[str, Any], Any]:
    """설정값 빠른 조회"""
    return get_config_manager().get_config(path)


def is_debug_mode() -> bool:
    """디버그 모드 확인"""
    return get_config("development.debug_mode") == True
