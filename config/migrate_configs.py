#!/usr/bin/env python3
"""
🔄 Configuration Migration Script
기존 설정 파일들을 새로운 통합 설정으로 마이그레이션하는 스크립트
"""

import os
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class ConfigMigrator:
    """설정 파일 마이그레이션 도구"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "config" / "backup"
        self.migration_log = []

        # 마이그레이션 대상 파일들
        self.source_configs = {
            "llm_config": self.project_root / "config" / "llm_config.yaml",
            "judge_config": self.project_root
            / "echo_engine"
            / "llm_free"
            / "judge_config.yaml",
        }

        self.target_config = self.project_root / "config" / "echo_system_config.yaml"

    def backup_existing_configs(self):
        """기존 설정 파일들 백업"""
        print("📦 기존 설정 파일 백업 중...")

        # 백업 디렉토리 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"migration_backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)

        backed_up_files = []

        for config_name, config_path in self.source_configs.items():
            if config_path.exists():
                backup_file = backup_path / f"{config_name}.yaml"
                shutil.copy2(config_path, backup_file)
                backed_up_files.append(str(backup_file))
                print(f"   ✅ {config_path} → {backup_file}")

        # 백업 정보 저장
        backup_info = {
            "timestamp": timestamp,
            "backed_up_files": backed_up_files,
            "migration_reason": "Config unification migration",
        }

        with open(backup_path / "backup_info.json", "w", encoding="utf-8") as f:
            json.dump(backup_info, f, ensure_ascii=False, indent=2)

        self.migration_log.append(f"백업 완료: {backup_path}")
        return backup_path

    def analyze_existing_configs(self) -> Dict[str, Any]:
        """기존 설정 파일 분석"""
        print("🔍 기존 설정 파일 분석 중...")

        analysis = {
            "found_configs": {},
            "merged_settings": {},
            "conflicts": [],
            "migration_notes": [],
        }

        for config_name, config_path in self.source_configs.items():
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    analysis["found_configs"][config_name] = {
                        "path": str(config_path),
                        "size": config_path.stat().st_size,
                        "sections": list(config_data.keys()) if config_data else [],
                        "data": config_data,
                    }

                    print(f"   ✅ {config_name}: {len(config_data.keys())}개 섹션 발견")

                except Exception as e:
                    print(f"   ❌ {config_name} 분석 실패: {e}")
                    analysis["migration_notes"].append(
                        f"{config_name} 파일 읽기 실패: {e}"
                    )
            else:
                print(f"   ⚠️ {config_name} 파일 없음: {config_path}")

        return analysis

    def merge_configs(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """설정 파일들을 통합 설정으로 병합"""
        print("🔗 설정 파일 병합 중...")

        # 새로운 통합 설정 템플릿 로드
        if self.target_config.exists():
            with open(self.target_config, "r", encoding="utf-8") as f:
                unified_config = yaml.safe_load(f)
        else:
            print("❌ 통합 설정 파일이 존재하지 않음")
            return {}

        found_configs = analysis["found_configs"]

        # LLM Config 병합
        if "llm_config" in found_configs:
            llm_data = found_configs["llm_config"]["data"]
            self._merge_llm_config(unified_config, llm_data)

        # Judge Config 병합
        if "judge_config" in found_configs:
            judge_data = found_configs["judge_config"]["data"]
            self._merge_judge_config(unified_config, judge_data)

        return unified_config

    def _merge_llm_config(self, unified: Dict[str, Any], llm_config: Dict[str, Any]):
        """LLM 설정 병합"""
        print("   🤖 LLM 설정 병합 중...")

        # 판단 모드 병합
        if "judge_mode" in llm_config:
            unified["judgment"]["mode"] = llm_config["judge_mode"]

        # 신뢰도 임계값 병합
        if "confidence_threshold" in llm_config:
            unified["judgment"]["confidence_threshold"] = llm_config[
                "confidence_threshold"
            ]

        # Claude 설정 병합
        if "claude_settings" in llm_config:
            claude_settings = llm_config["claude_settings"]
            unified["claude"].update(
                {
                    "api_mode": claude_settings.get("api_mode", "mock"),
                    "model": claude_settings.get("model", "claude-3-5-sonnet-20241022"),
                    "max_tokens": claude_settings.get("max_tokens", 1000),
                    "temperature": claude_settings.get("temperature", 0.3),
                    "timeout": claude_settings.get("timeout", 30),
                    "retry_count": claude_settings.get("retry_count", 3),
                }
            )

        # Fallback 설정 병합
        if "fallback_settings" in llm_config:
            fallback = llm_config["fallback_settings"]
            unified["llm_free"].update(
                {
                    "min_confidence": fallback.get("min_confidence", 0.3),
                    "performance": {
                        "max_processing_time": fallback.get("max_processing_time", 2.0)
                    },
                    "caching": {
                        "enabled": fallback.get("enable_caching", True),
                        "cache_size": fallback.get("cache_size", 100),
                        "cache_ttl": fallback.get("cache_ttl", 300),
                    },
                }
            )

        # 로깅 설정 병합
        if "logging" in llm_config:
            logging_config = llm_config["logging"]
            unified["logging"].update(
                {
                    "level": logging_config.get("level", "INFO"),
                    "file_path": logging_config.get(
                        "file_path", "logs/echo_system.log"
                    ),
                    "format": logging_config.get(
                        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    ),
                }
            )

            if "rotation" in logging_config:
                unified["logging"]["rotation"] = logging_config["rotation"]

        # 성능 설정 병합
        if "performance" in llm_config:
            perf_config = llm_config["performance"]
            unified["performance"].update(
                {
                    "max_concurrent_requests": perf_config.get(
                        "max_concurrent_requests", 10
                    ),
                    "request_queue_size": perf_config.get("request_queue_size", 100),
                    "request_timeout": perf_config.get("request_timeout", 30),
                }
            )

        # FIST 설정 병합 (새로 추가된 섹션인 경우)
        if "fist_templates" in llm_config:
            fist_config = llm_config["fist_templates"]
            if "structure_types" in fist_config:
                unified["fist_templates"]["structure_types"].update(
                    fist_config["structure_types"]
                )

    def _merge_judge_config(
        self, unified: Dict[str, Any], judge_config: Dict[str, Any]
    ):
        """Judge 설정 병합"""
        print("   ⚖️ Judge 설정 병합 중...")

        # 기본 판단 설정 병합
        if "judgment_settings" in judge_config:
            judgment = judge_config["judgment_settings"]

            unified["llm_free"].update(
                {
                    "judgment_mode": judgment.get("judgment_mode", "pattern_based"),
                    "confidence_threshold": judgment.get("confidence_threshold", 0.6),
                    "defaults": {
                        "emotion": judgment.get("default_emotion", "neutral"),
                        "strategy": judgment.get("default_strategy", "balanced"),
                        "context": judgment.get("default_context", "general"),
                        "reasoning_depth": judgment.get("reasoning_depth", 3),
                    },
                }
            )

        # 패턴 매칭 설정 병합
        if "pattern_matching" in judge_config:
            pattern = judge_config["pattern_matching"]
            unified["llm_free"]["pattern_matching"] = pattern

        # 감정 분석 설정 병합
        if "emotion_analysis" in judge_config:
            emotion = judge_config["emotion_analysis"]
            unified["llm_free"]["emotion_analysis"] = {
                "weights": emotion.get("emotion_weights", {}),
                "threshold": emotion.get("emotion_threshold", 0.6),
                "intensity_method": emotion.get("intensity_method", "frequency"),
                "handle_negation": emotion.get("handle_negation", True),
                "allow_mixed_emotions": emotion.get("allow_mixed_emotions", True),
            }

        # 전략 분석 설정 병합
        if "strategy_analysis" in judge_config:
            strategy = judge_config["strategy_analysis"]
            unified["llm_free"]["strategy_analysis"] = {
                "weights": strategy.get("strategy_weights", {}),
                "threshold": strategy.get("strategy_threshold", 0.5),
                "selection_method": strategy.get("selection_method", "highest_score"),
                "allow_combination": strategy.get("allow_strategy_combination", True),
            }

        # 성능 설정 병합
        if "performance" in judge_config:
            perf = judge_config["performance"]
            unified["llm_free"]["performance"] = {
                "max_processing_time": perf.get("max_processing_time", 5.0),
                "max_memory_usage": perf.get("max_memory_usage", 100),
                "enable_parallel_processing": perf.get(
                    "enable_parallel_processing", True
                ),
                "max_threads": perf.get("max_threads", 4),
                "batch_size": perf.get("batch_size", 10),
            }

    def create_import_migration_guide(self) -> str:
        """import 문 마이그레이션 가이드 생성"""
        guide_path = self.project_root / "config" / "MIGRATION_GUIDE.md"

        migration_guide = """# 🔄 Configuration Migration Guide

## 개요
EchoJudgmentSystem v10.5에서 모든 설정 파일이 통합되었습니다.

## 변경사항

### 이전 (분산된 설정)
```python
# 이전 방식 - 여러 파일에서 설정 로드
import yaml

with open('config/llm_config.yaml') as f:
    llm_config = yaml.safe_load(f)

with open('echo_engine/llm_free/judge_config.yaml') as f:
    judge_config = yaml.safe_load(f)

# 설정 사용
judge_mode = llm_config['judge_mode']
confidence = llm_config['confidence_threshold']
```

### 이후 (통합 설정)
```python
# 새로운 방식 - 통합 설정 로더 사용
from src.echo_foundation.config.loader import get_config, get_config_loader

# 간단한 설정 조회
judge_mode = get_config('judgment.mode')
confidence = get_config('judgment.confidence_threshold')

# 복잡한 설정 조회
loader = get_config_loader()
signature_config = loader.get_signature_config('Echo-Aurora')
fist_config = loader.get_fist_category_config('decision')
```

## 마이그레이션 체크리스트

### 1. Import 문 업데이트
- [ ] `config/llm_config.yaml` 직접 로드하는 코드 제거
- [ ] `echo_engine/llm_free/judge_config.yaml` 직접 로드하는 코드 제거
- [ ] `from src.echo_foundation.config.loader import get_config` 추가

### 2. 설정 키 경로 업데이트
| 이전 | 이후 |
|------|------|
| `llm_config['judge_mode']` | `get_config('judgment.mode')` |
| `llm_config['confidence_threshold']` | `get_config('judgment.confidence_threshold')` |
| `llm_config['claude_settings']['model']` | `get_config('claude.model')` |
| `judge_config['judgment_settings']['reasoning_depth']` | `get_config('llm_free.defaults.reasoning_depth')` |

### 3. 환경별 설정 활용
```python
# 환경별 설정 로드
loader = get_config_loader()
config = loader.load_config('production')  # 또는 'development', 'testing'

# 환경 정보 확인
env_info = loader.get_environment_info()
```

### 4. 동적 설정 변경
```python
# 런타임에 설정 변경
loader = get_config_loader()
loader.set('judgment.mode', 'hybrid')
loader.set('fist_templates.enabled', True)
```

## 주요 변경점

### 설정 구조 변화
- **judgment**: 판단 시스템 통합 설정
- **signatures**: 시그니처 시스템 설정  
- **claude**: Claude API 설정
- **llm_free**: LLM-Free 시스템 설정
- **fist_templates**: FIST 템플릿 시스템 설정
- **meta_cognition**: 메타인지 반성 루프 설정

### 새로운 기능
- 환경별 설정 오버라이드 (`environments` 섹션)
- 환경 변수 기반 설정 (`ECHO_*` 환경 변수)
- 설정 검증 및 validation
- 실시간 설정 재로드
- 설정 내보내기/가져오기

## 호환성 보장

기존 코드가 즉시 중단되지 않도록 다음과 같은 방법을 권장합니다:

1. **점진적 마이그레이션**: 모듈별로 하나씩 새로운 설정 시스템으로 전환
2. **폴백 지원**: 기존 설정 파일이 존재하는 경우 임시로 로드
3. **로깅**: 마이그레이션 진행 상황 추적

## 문제 해결

### 설정을 찾을 수 없는 경우
```python
# 안전한 설정 조회 (기본값 포함)
mode = get_config('judgment.mode', 'llm_free')  # 기본값: 'llm_free'
```

### 환경별 설정 문제
```python
# 현재 환경 확인
loader = get_config_loader()
print(f"현재 환경: {loader.environment}")

# 환경 강제 변경
loader.load_config('development')
```

### 검증 오류
```python
# 설정 검증 결과 확인
loader = get_config_loader()
if loader.validation_result:
    if not loader.validation_result.is_valid:
        print("설정 오류:", loader.validation_result.errors)
```
"""

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(migration_guide)

        return str(guide_path)

    def update_imports_in_files(self):
        """프로젝트 파일들의 import 문 업데이트"""
        print("📝 Import 문 업데이트 중...")

        # 업데이트할 파일 패턴들
        python_files = list(self.project_root.rglob("*.py"))

        updated_files = []
        update_patterns = [
            # 기존 설정 파일 로드 패턴들
            (
                "with open('config/llm_config.yaml')",
                "from src.echo_foundation.config.loader import get_config",
            ),
            ("yaml.safe_load", "# Migrated to unified config"),
            ("llm_config['judge_mode']", "get_config('judgment.mode')"),
            (
                "llm_config['confidence_threshold']",
                "get_config('judgment.confidence_threshold')",
            ),
        ]

        for file_path in python_files:
            # venv, __pycache__ 등 제외
            if any(
                exclude in str(file_path) for exclude in ["venv", "__pycache__", ".git"]
            ):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # 패턴 기반 치환 (주석으로만 표시, 실제 변경은 수동으로)
                for old_pattern, new_pattern in update_patterns:
                    if old_pattern in content:
                        # 실제 변경 대신 주석으로 마이그레이션 힌트 추가
                        content = content.replace(
                            old_pattern,
                            f"{old_pattern}  # TODO: Migrate to {new_pattern}",
                        )

                # 파일이 변경된 경우에만 저장 (실제로는 주석 추가만)
                if content != original_content:
                    updated_files.append(str(file_path))

            except Exception as e:
                print(f"   ⚠️ {file_path} 업데이트 실패: {e}")

        print(f"   📋 업데이트 대상 파일: {len(updated_files)}개")
        return updated_files

    def run_migration(self) -> Dict[str, Any]:
        """전체 마이그레이션 실행"""
        print("🚀 설정 파일 마이그레이션 시작")
        print("=" * 60)

        migration_result = {
            "success": False,
            "backup_path": None,
            "analysis": {},
            "unified_config_path": None,
            "migration_guide_path": None,
            "updated_files": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 1. 기존 설정 백업
            backup_path = self.backup_existing_configs()
            migration_result["backup_path"] = str(backup_path)

            # 2. 기존 설정 분석
            analysis = self.analyze_existing_configs()
            migration_result["analysis"] = analysis

            # 3. 설정 병합 (통합 설정이 이미 존재하므로 검증만)
            if self.target_config.exists():
                print(f"✅ 통합 설정 파일 존재: {self.target_config}")
                migration_result["unified_config_path"] = str(self.target_config)
            else:
                print(f"❌ 통합 설정 파일 없음: {self.target_config}")
                migration_result["errors"].append("통합 설정 파일이 존재하지 않습니다")

            # 4. 마이그레이션 가이드 생성
            guide_path = self.create_import_migration_guide()
            migration_result["migration_guide_path"] = guide_path
            print(f"📖 마이그레이션 가이드 생성: {guide_path}")

            # 5. Import 문 분석 (실제 변경은 하지 않음)
            updated_files = self.update_imports_in_files()
            migration_result["updated_files"] = updated_files

            migration_result["success"] = True
            print("\n✅ 마이그레이션 완료!")

        except Exception as e:
            print(f"\n❌ 마이그레이션 실패: {e}")
            migration_result["errors"].append(str(e))

        return migration_result


def main():
    """메인 실행 함수"""
    migrator = ConfigMigrator()
    result = migrator.run_migration()

    print("\n" + "=" * 60)
    print("📊 마이그레이션 결과 요약")
    print("=" * 60)

    if result["success"]:
        print("🎉 마이그레이션 성공!")
        print(f"   📦 백업 위치: {result['backup_path']}")
        print(f"   📋 통합 설정: {result['unified_config_path']}")
        print(f"   📖 가이드: {result['migration_guide_path']}")
        print(f"   📝 업데이트 대상: {len(result['updated_files'])}개 파일")

        print("\n🔄 다음 단계:")
        print("1. 마이그레이션 가이드 확인")
        print("2. 점진적으로 코드 업데이트")
        print("3. 새로운 설정 시스템 테스트")
        print("4. 기존 설정 파일 제거 (백업 후)")
    else:
        print("❌ 마이그레이션 실패")
        for error in result["errors"]:
            print(f"   - {error}")

    return result


if __name__ == "__main__":
    main()
