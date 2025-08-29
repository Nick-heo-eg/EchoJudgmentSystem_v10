#!/usr/bin/env python3
"""
🎛️ EchoJudgmentSystem v10.5 Configuration Loader
통합 설정 파일 로딩 및 관리 시스템
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConfigEnvironment:
    """환경별 설정 정보"""

    name: str
    description: str = ""
    active: bool = False
    loaded_at: Optional[datetime] = None


@dataclass
class ConfigValidationResult:
    """설정 검증 결과"""

    is_valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    missing_keys: list = field(default_factory=list)
    deprecated_keys: list = field(default_factory=list)


class EchoConfigLoader:
    """통합 설정 로더"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.environment: Optional[str] = None
        self.loaded_at: Optional[datetime] = None
        self.validation_result: Optional[ConfigValidationResult] = None

        # 기본 설정 스키마
        self.required_sections = [
            "system",
            "judgment",
            "signatures",
            "claude",
            "llm_free",
            "fist_templates",
            "logging",
            "performance",
        ]

        # 환경별 설정
        self.environments = {
            "development": ConfigEnvironment("development", "개발 환경"),
            "testing": ConfigEnvironment("testing", "테스트 환경"),
            "production": ConfigEnvironment("production", "운영 환경"),
            "offline": ConfigEnvironment("offline", "오프라인 환경"),
        }

    def _get_default_config_path(self) -> str:
        """기본 설정 파일 경로 반환"""
        current_dir = Path(__file__).parent
        return str(current_dir / "echo_system_config.yaml")

    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            # 메인 설정 파일 로드
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

            # 환경 설정 적용
            if environment:
                self.apply_environment_overrides(environment)
            else:
                # 시스템 기본 환경 사용
                env = self.config.get("system", {}).get("environment", "development")
                self.apply_environment_overrides(env)

            # 환경 변수 오버라이드 적용
            self.apply_env_var_overrides()

            # 설정 검증
            self.validation_result = self.validate_config()

            self.loaded_at = datetime.now()
            print(f"✅ 설정 로드 완료: {self.config_path} (환경: {self.environment})")

            return self.config

        except FileNotFoundError:
            print(f"❌ 설정 파일을 찾을 수 없음: {self.config_path}")
            return self._get_fallback_config()

        except yaml.YAMLError as e:
            print(f"❌ YAML 파싱 오류: {e}")
            return self._get_fallback_config()

        except Exception as e:
            print(f"❌ 설정 로드 실패: {e}")
            return self._get_fallback_config()

    def apply_environment_overrides(self, environment: str):
        """환경별 설정 오버라이드 적용"""
        self.environment = environment

        if "environments" in self.config and environment in self.config["environments"]:
            env_config = self.config["environments"][environment]

            # 깊은 병합 수행
            self._deep_merge(self.config, env_config)

            # 환경 정보 업데이트
            if environment in self.environments:
                self.environments[environment].active = True
                self.environments[environment].loaded_at = datetime.now()

            print(f"🎛️ 환경별 설정 적용: {environment}")

    def apply_env_var_overrides(self):
        """환경 변수 기반 설정 오버라이드"""
        overrides = {}

        # 특정 환경 변수들을 설정에 매핑
        env_mappings = {
            "ECHO_DEBUG_MODE": "system.debug_mode",
            "ECHO_JUDGE_MODE": "judgment.mode",
            "ECHO_CLAUDE_API_MODE": "claude.api_mode",
            "ECHO_FIST_ENABLED": "fist_templates.enabled",
            "ECHO_LOG_LEVEL": "logging.level",
            "ECHO_ENVIRONMENT": "system.environment",
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # 값 타입 변환
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)

                self._set_nested_value(overrides, config_path, value)

        if overrides:
            self._deep_merge(self.config, overrides)
            print(f"🌍 환경 변수 오버라이드 적용: {len(overrides)}개 설정")

    def validate_config(self) -> ConfigValidationResult:
        """설정 검증"""
        result = ConfigValidationResult(is_valid=True)

        # 필수 섹션 확인
        for section in self.required_sections:
            if section not in self.config:
                result.errors.append(f"필수 섹션 누락: {section}")
                result.missing_keys.append(section)
                result.is_valid = False

        # 시스템 설정 검증
        if "system" in self.config:
            system_config = self.config["system"]

            # 필수 필드 확인
            required_fields = ["name", "version", "environment"]
            for field in required_fields:
                if field not in system_config:
                    result.errors.append(f"시스템 필수 필드 누락: {field}")
                    result.is_valid = False

        # 판단 시스템 설정 검증
        if "judgment" in self.config:
            judgment_config = self.config["judgment"]

            # 모드 검증
            valid_modes = ["claude", "llm_free", "hybrid", "fist_only"]
            mode = judgment_config.get("mode")
            if mode and mode not in valid_modes:
                result.warnings.append(f"알 수 없는 판단 모드: {mode}")

            # 신뢰도 임계값 검증
            confidence = judgment_config.get("confidence_threshold")
            if confidence and (confidence < 0 or confidence > 1):
                result.errors.append("신뢰도 임계값은 0-1 사이여야 합니다")
                result.is_valid = False

        # FIST 템플릿 설정 검증
        if "fist_templates" in self.config:
            fist_config = self.config["fist_templates"]

            # 템플릿 디렉토리 확인
            templates_dir = fist_config.get("templates_dir")
            if templates_dir and not Path(templates_dir).exists():
                result.warnings.append(
                    f"FIST 템플릿 디렉토리가 존재하지 않음: {templates_dir}"
                )

        # 성능 설정 검증
        if "performance" in self.config:
            perf_config = self.config["performance"]

            # 동시 요청 수 검증
            max_requests = perf_config.get("max_concurrent_requests")
            if max_requests and max_requests < 1:
                result.errors.append("최대 동시 요청 수는 1 이상이어야 합니다")
                result.is_valid = False

        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """중첩된 키 경로로 설정값 조회"""
        try:
            keys = key_path.split(".")
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """중첩된 키 경로로 설정값 수정"""
        self._set_nested_value(self.config, key_path, value)

    def get_signature_config(self, signature_name: str) -> Dict[str, Any]:
        """특정 시그니처 설정 조회"""
        signatures = self.get("signatures.available", {})

        # 시그니처 이름 정규화 (Echo-Aurora -> echo_aurora)
        normalized_name = signature_name.lower().replace("-", "_")

        return signatures.get(normalized_name, {})

    def get_fist_category_config(self, category: str) -> Dict[str, Any]:
        """FIST 카테고리별 설정 조회"""
        categories = self.get("fist_templates.categories", {})
        return categories.get(category, {})

    def get_environment_info(self) -> Dict[str, Any]:
        """현재 환경 정보 반환"""
        return {
            "current_environment": self.environment,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "config_path": self.config_path,
            "validation_passed": (
                self.validation_result.is_valid if self.validation_result else None
            ),
            "available_environments": list(self.environments.keys()),
        }

    def reload_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """설정 다시 로드"""
        print(f"🔄 설정 재로드 중...")
        return self.load_config(environment)

    def save_config(self, output_path: Optional[str] = None):
        """현재 설정을 파일로 저장"""
        save_path = output_path or self.config_path

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            print(f"✅ 설정 저장 완료: {save_path}")

        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")

    def export_config(
        self, format: str = "yaml", output_path: Optional[str] = None
    ) -> str:
        """설정을 다른 형식으로 내보내기"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"config_export_{timestamp}.{format}"

        try:
            if format.lower() == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2, default=str)
            elif format.lower() == "yaml":
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        self.config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )
            else:
                raise ValueError(f"지원하지 않는 형식: {format}")

            print(f"✅ 설정 내보내기 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ 설정 내보내기 실패: {e}")
            return ""

    def _deep_merge(self, target: Dict, source: Dict):
        """딕셔너리 깊은 병합"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _set_nested_value(self, target: Dict, key_path: str, value: Any):
        """중첩된 딕셔너리에 값 설정"""
        keys = key_path.split(".")
        current = target

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _get_fallback_config(self) -> Dict[str, Any]:
        """폴백 설정 반환"""
        return {
            "system": {
                "name": "EchoJudgmentSystem",
                "version": "v10.5",
                "environment": "fallback",
                "debug_mode": True,
            },
            "judgment": {
                "mode": "llm_free",
                "confidence_threshold": 0.6,
                "fallback_chain": ["llm_free"],
            },
            "signatures": {
                "default": "Echo-Aurora",
                "available": {
                    "echo_aurora": {
                        "name": "Echo-Aurora",
                        "emotion_sensitivity": 0.8,
                        "response_tone": "inspiring",
                    }
                },
            },
            "claude": {"api_mode": "mock", "timeout": 30},
            "llm_free": {"enabled": True, "confidence_threshold": 0.6},
            "fist_templates": {"enabled": False},
            "logging": {"level": "INFO"},
            "performance": {"max_concurrent_requests": 5},
        }


# 전역 설정 로더 인스턴스
_config_loader = None


def get_config_loader() -> EchoConfigLoader:
    """전역 설정 로더 인스턴스 반환"""
    global _config_loader
    if _config_loader is None:
        _config_loader = EchoConfigLoader()
        _config_loader.load_config()
    return _config_loader


def load_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """설정 로드 (편의 함수)"""
    loader = get_config_loader()
    return loader.load_config(environment)


def get_config(key_path: str, default: Any = None) -> Any:
    """설정값 조회 (편의 함수)"""
    loader = get_config_loader()
    return loader.get(key_path, default)


def get_signature_config(signature_name: str) -> Dict[str, Any]:
    """시그니처 설정 조회 (편의 함수)"""
    loader = get_config_loader()
    return loader.get_signature_config(signature_name)


def get_fist_category_config(category: str) -> Dict[str, Any]:
    """FIST 카테고리 설정 조회 (편의 함수)"""
    loader = get_config_loader()
    return loader.get_fist_category_config(category)


if __name__ == "__main__":
    # 테스트 실행
    print("🧪 EchoConfigLoader 테스트")
    print("=" * 50)

    loader = EchoConfigLoader()
    config = loader.load_config("development")

    print(f"시스템 이름: {loader.get('system.name')}")
    print(f"판단 모드: {loader.get('judgment.mode')}")
    print(f"FIST 활성화: {loader.get('fist_templates.enabled')}")
    print(f"환경 정보: {loader.get_environment_info()}")

    if loader.validation_result:
        print(
            f"검증 결과: {'✅ 통과' if loader.validation_result.is_valid else '❌ 실패'}"
        )
        if loader.validation_result.errors:
            print(f"오류: {loader.validation_result.errors}")
        if loader.validation_result.warnings:
            print(f"경고: {loader.validation_result.warnings}")
