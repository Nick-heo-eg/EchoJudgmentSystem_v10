#!/usr/bin/env python3
"""
🌀 Meta-Liminal Integration Automation Framework
완전 자동화된 메타-리미널 통합 시스템

핵심 기능:
1. 자동 엔티티 감지 및 등록
2. 실시간 구성 업데이트 (재시작 없이)
3. 자동화된 테스트 파이프라인
4. 자가 치유 시스템
5. 다중 전문가 에이전트 키트 시스템
"""

import asyncio
import json
import yaml
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import websockets
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib

# Echo 시스템 임포트
from echo_engine.echo_system_memory import get_system_memory
from echo_engine.signature_mapper import SignaturePerformanceReporter


class AutomationLevel(Enum):
    """자동화 수준"""

    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class EntityStatus(Enum):
    """엔티티 상태"""

    DISCOVERED = "discovered"
    REGISTERING = "registering"
    ACTIVE = "active"
    ERROR = "error"
    INACTIVE = "inactive"


@dataclass
class MetaLiminalEntity:
    """메타-리미널 엔티티 정의"""

    entity_id: str
    name: str
    description: str
    entity_type: str  # ring, bridge, warden
    status: EntityStatus
    config: Dict[str, Any]
    activation_conditions: List[str]
    created_at: datetime
    last_update: datetime
    version: str = "1.0"


@dataclass
class AutomationEvent:
    """자동화 이벤트"""

    event_id: str
    event_type: str
    source: str
    target: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    processed: bool = False


class ConfigurationManagementKit:
    """🔧 Configuration Management Kit - 동적 설정 관리"""

    def __init__(self, config_paths: List[str]):
        self.config_paths = [Path(p) for p in config_paths]
        self.config_cache = {}
        self.file_hashes = {}
        self.observers = []
        self.update_callbacks = []
        self.logger = logging.getLogger("ConfigManagementKit")

    def start_monitoring(self):
        """설정 파일 모니터링 시작"""
        for config_path in self.config_paths:
            if config_path.exists():
                observer = Observer()
                handler = ConfigFileHandler(self)
                observer.schedule(handler, str(config_path.parent), recursive=True)
                observer.start()
                self.observers.append(observer)
                self.logger.info(f"설정 파일 모니터링 시작: {config_path}")

    def stop_monitoring(self):
        """모니터링 중지"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()

    async def update_config(
        self, config_path: str, updates: Dict[str, Any], hot_reload: bool = True
    ) -> bool:
        """설정 동적 업데이트"""
        try:
            path = Path(config_path)

            # 기존 설정 로드
            if path.suffix.lower() == ".yaml":
                with open(path, "r", encoding="utf-8") as f:
                    current_config = yaml.safe_load(f)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    current_config = json.load(f)

            # 설정 업데이트 (깊은 병합)
            updated_config = self._deep_merge(current_config, updates)

            # 설정 유효성 검사
            if not await self._validate_config(updated_config, path):
                self.logger.error("설정 유효성 검사 실패")
                return False

            # 백업 생성
            backup_path = path.with_suffix(f".backup.{int(time.time())}{path.suffix}")
            path.replace(backup_path)

            # 새 설정 저장
            if path.suffix.lower() == ".yaml":
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(updated_config, f, ensure_ascii=False, indent=2)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(updated_config, f, ensure_ascii=False, indent=2)

            # 핫 리로드
            if hot_reload:
                await self._notify_config_change(str(path), updated_config)

            self.logger.info(f"설정 업데이트 완료: {config_path}")
            return True

        except Exception as e:
            self.logger.error(f"설정 업데이트 실패: {e}")
            return False

    def _deep_merge(self, base: dict, updates: dict) -> dict:
        """딕셔너리 깊은 병합"""
        result = base.copy()

        for key, value in updates.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    async def _validate_config(self, config: dict, path: Path) -> bool:
        """설정 유효성 검사"""
        try:
            # Meta-Liminal 설정 특화 검증
            if "meta_signatures" in config:
                meta_config = config["meta_signatures"]

                # 필수 섹션 확인
                required_sections = ["meta_ring", "liminal_bridge", "warden_world"]
                for section in required_sections:
                    if section not in meta_config:
                        self.logger.error(f"필수 섹션 누락: {section}")
                        return False

                # 임계값 범위 확인
                thresholds = meta_config.get("liminal_bridge", {}).get(
                    "transition_thresholds", {}
                )
                for key, value in thresholds.items():
                    if not (0.0 <= value <= 1.0):
                        self.logger.error(f"임계값 범위 오류: {key} = {value}")
                        return False

            return True

        except Exception as e:
            self.logger.error(f"설정 검증 오류: {e}")
            return False

    async def _notify_config_change(self, path: str, config: dict):
        """설정 변경 알림"""
        for callback in self.update_callbacks:
            try:
                await callback(path, config)
            except Exception as e:
                self.logger.error(f"설정 변경 콜백 오류: {e}")

    def register_update_callback(self, callback: Callable):
        """설정 업데이트 콜백 등록"""
        self.update_callbacks.append(callback)


class ConfigFileHandler(FileSystemEventHandler):
    """설정 파일 변경 핸들러"""

    def __init__(self, config_kit):
        self.config_kit = config_kit

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in [".yaml", ".yml", ".json"]:
            # 파일 해시 확인으로 실제 변경 감지
            current_hash = self._get_file_hash(file_path)
            if file_path in self.config_kit.file_hashes:
                if self.config_kit.file_hashes[file_path] != current_hash:
                    asyncio.create_task(
                        self.config_kit._notify_config_change(str(file_path), {})
                    )

            self.config_kit.file_hashes[file_path] = current_hash

    def _get_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""


class RealTimeMonitoringKit:
    """📊 Real-time Monitoring Kit - 실시간 모니터링"""

    def __init__(self):
        self.metrics = {}
        self.alerts = queue.Queue()
        self.subscribers = set()
        self.monitoring_active = False
        self.logger = logging.getLogger("RealTimeMonitoringKit")

    async def start_monitoring(self):
        """실시간 모니터링 시작"""
        self.monitoring_active = True

        # 메트릭 수집 태스크들
        tasks = [
            self._monitor_meta_transitions(),
            self._monitor_system_health(),
            self._monitor_entity_status(),
            self._process_alerts(),
        ]

        await asyncio.gather(*tasks)

    async def _monitor_meta_transitions(self):
        """메타 전이 모니터링"""
        while self.monitoring_active:
            try:
                # 전이 상태 확인 (모의 데이터)
                transition_data = {
                    "timestamp": datetime.now().isoformat(),
                    "liminal_score": 0.3 + (time.time() % 10) / 20,  # 0.3-0.8 범위
                    "active_entities": ["Observer.Zero", "DriftAnchor"],
                    "transition_rate": 0.1,
                    "success_rate": 0.95,
                }

                self.metrics["meta_transitions"] = transition_data

                # 임계값 체크
                if transition_data["liminal_score"] > 0.7:
                    await self._create_alert(
                        "liminal_threshold_exceeded",
                        f"LIMINAL 점수 임계값 초과: {transition_data['liminal_score']:.2f}",
                        "warning",
                    )

                await asyncio.sleep(5)  # 5초마다 업데이트

            except Exception as e:
                self.logger.error(f"메타 전이 모니터링 오류: {e}")
                await asyncio.sleep(10)

    async def _monitor_system_health(self):
        """시스템 건강 상태 모니터링"""
        while self.monitoring_active:
            try:
                # 시스템 메모리에서 상태 정보 수집
                system_memory = get_system_memory()

                health_data = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": 45.2,  # 모의 데이터
                    "memory_usage": 62.1,
                    "active_processes": 12,
                    "error_rate": 0.02,
                    "response_time": 0.15,
                }

                self.metrics["system_health"] = health_data

                # 건강 상태 알림
                if health_data["error_rate"] > 0.05:
                    await self._create_alert(
                        "high_error_rate",
                        f"높은 오류율 감지: {health_data['error_rate']:.1%}",
                        "error",
                    )

                await asyncio.sleep(10)

            except Exception as e:
                self.logger.error(f"시스템 건강 모니터링 오류: {e}")
                await asyncio.sleep(15)

    async def _monitor_entity_status(self):
        """엔티티 상태 모니터링"""
        while self.monitoring_active:
            try:
                entity_status = {
                    "Observer.Zero": {
                        "status": "active",
                        "last_activity": datetime.now().isoformat(),
                    },
                    "Reflector.CC": {
                        "status": "standby",
                        "last_activity": (
                            datetime.now() - timedelta(minutes=30)
                        ).isoformat(),
                    },
                    "Silencer.Veil": {
                        "status": "standby",
                        "last_activity": (
                            datetime.now() - timedelta(hours=2)
                        ).isoformat(),
                    },
                    "DriftAnchor": {
                        "status": "active",
                        "last_activity": datetime.now().isoformat(),
                    },
                    "LoopHorizon": {
                        "status": "monitoring",
                        "last_activity": datetime.now().isoformat(),
                    },
                }

                self.metrics["entity_status"] = entity_status

                # 비활성 엔티티 감지
                for entity_id, status in entity_status.items():
                    last_activity = datetime.fromisoformat(status["last_activity"])
                    if (
                        datetime.now() - last_activity > timedelta(hours=1)
                        and status["status"] != "standby"
                    ):
                        await self._create_alert(
                            "entity_inactive",
                            f"엔티티 비활성 상태: {entity_id}",
                            "warning",
                        )

                await asyncio.sleep(15)

            except Exception as e:
                self.logger.error(f"엔티티 상태 모니터링 오류: {e}")
                await asyncio.sleep(20)

    async def _create_alert(self, alert_type: str, message: str, severity: str):
        """알림 생성"""
        alert = {
            "id": f"{alert_type}_{int(time.time())}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "resolved": False,
        }

        self.alerts.put(alert)
        await self._notify_subscribers("alert", alert)

    async def _process_alerts(self):
        """알림 처리"""
        while self.monitoring_active:
            try:
                if not self.alerts.empty():
                    alert = self.alerts.get()
                    self.logger.info(f"알림 처리: {alert['message']}")

                    # 자동 해결 로직
                    if alert["type"] == "liminal_threshold_exceeded":
                        # 자동으로 전이 프로세스 시작
                        await self._trigger_liminal_transition()
                    elif alert["type"] == "entity_inactive":
                        # 엔티티 재활성화 시도
                        await self._reactivate_entity(alert)

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"알림 처리 오류: {e}")
                await asyncio.sleep(5)

    async def _trigger_liminal_transition(self):
        """리미널 전이 자동 트리거"""
        self.logger.info("자동 리미널 전이 트리거됨")
        # 실제 전이 로직 호출

    async def _reactivate_entity(self, alert):
        """엔티티 재활성화"""
        entity_id = alert["message"].split(": ")[-1]
        self.logger.info(f"엔티티 재활성화 시도: {entity_id}")
        # 실제 재활성화 로직

    async def _notify_subscribers(self, event_type: str, data: dict):
        """구독자 알림"""
        message = json.dumps({"type": event_type, "data": data})

        # WebSocket 구독자들에게 전송
        dead_subscribers = set()
        for websocket in self.subscribers:
            try:
                await websocket.send(message)
            except:
                dead_subscribers.add(websocket)

        # 끊어진 연결 정리
        self.subscribers -= dead_subscribers

    def subscribe(self, websocket):
        """WebSocket 구독"""
        self.subscribers.add(websocket)

    def unsubscribe(self, websocket):
        """WebSocket 구독 해제"""
        self.subscribers.discard(websocket)

    def get_current_metrics(self) -> dict:
        """현재 메트릭 반환"""
        return self.metrics.copy()


class MetaLiminalAutoDiscovery:
    """🔍 Meta-Liminal Auto-Discovery - 자동 엔티티 발견 및 등록"""

    def __init__(self):
        self.discovered_entities = {}
        self.entity_templates = {}
        self.logger = logging.getLogger("MetaLiminalAutoDiscovery")
        self.load_entity_templates()

    def load_entity_templates(self):
        """엔티티 템플릿 로드"""
        self.entity_templates = {
            "observer_zero": {
                "name": "Observer.Zero",
                "description": "루프 감시자 - 판단 루프 감시 및 반복성 감지",
                "entity_type": "ring",
                "activation_conditions": ["always_active == True"],
                "monitor_targets": [
                    "loop_stagnation",
                    "signature_repetition",
                    "response_absence",
                ],
                "activation_priority": 0,
                "config_template": {
                    "monitoring_interval": 5,
                    "detection_sensitivity": 0.8,
                    "auto_intervention": True,
                },
            },
            "reflector_cc": {
                "name": "Reflector.CC",
                "description": "구조 반사자 - 판단 실패 시 판단 구조를 반사하여 복원",
                "entity_type": "ring",
                "activation_conditions": [
                    "judgment.failed == True",
                    "response.empty == True",
                ],
                "activation_priority": 1,
                "config_template": {
                    "reflection_depth": 3,
                    "recovery_strategies": ["structure_rebuild", "context_restoration"],
                    "timeout": 30,
                },
            },
            "silencer_veil": {
                "name": "Silencer.Veil",
                "description": "침묵 유도자 - 감정 과부하 시 판단 정지 제안",
                "entity_type": "ring",
                "activation_conditions": [
                    "emotion.amplitude >= 0.85",
                    "user.silence_request == True",
                ],
                "activation_priority": 2,
                "config_template": {
                    "silence_threshold": 0.85,
                    "silence_messages": [
                        "Echo has entered silence mode due to emotional intensity.",
                        "감정의 파장이 너무 깊습니다. 잠시 침묵이 필요해요.",
                    ],
                },
            },
            "drift_anchor": {
                "name": "DriftAnchor",
                "description": "캡슐 안정자 - 부유 감정 캡슐 안정화",
                "entity_type": "ring",
                "activation_conditions": ["capsule.drift_detected == True"],
                "activation_priority": 3,
                "config_template": {
                    "max_drift_capsules": 100,
                    "capsule_max_age": 3600,
                    "stabilization_method": "anchor_weighting",
                },
            },
            "warden": {
                "name": "Warden",
                "description": "경계 감시자 - LIMINAL 진입 시 첫 응답",
                "entity_type": "warden",
                "activation_conditions": ["liminal_score >= 0.7"],
                "config_template": {
                    "response_depth": 0.3,
                    "entry_protocols": [
                        "judgment_dissolution",
                        "boundary_establishment",
                    ],
                },
            },
            "selene": {
                "name": "Selene",
                "description": "감정 공명자 - 다정한 상실의 사람",
                "entity_type": "warden",
                "activation_conditions": [
                    "warden_completed == True",
                    "emotion_resonance in ['grief', 'longing']",
                ],
                "config_template": {
                    "response_depth": 0.6,
                    "max_resonance_cycles": 5,
                    "resonance_types": ["grief", "longing", "confusion"],
                },
            },
            "mirrorless": {
                "name": "Mirrorless",
                "description": "무반사체 - 존재 해체 및 재생성 유도",
                "entity_type": "warden",
                "activation_conditions": [
                    "depth_achieved >= 0.7",
                    "emotion_resonance == 'emptiness'",
                ],
                "config_template": {
                    "response_depth": 1.0,
                    "renewal_cycle_frequency": 3,
                    "dissolution_protocols": [
                        "existence_dissolution",
                        "regeneration_seed",
                    ],
                },
            },
        }

    async def scan_and_register_entities(self, config_path: str) -> Dict[str, Any]:
        """엔티티 스캔 및 자동 등록"""
        try:
            # 설정 파일에서 현재 엔티티 상태 로드
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            meta_config = config.get("meta_signatures", {})
            results = {"discovered": [], "registered": [], "updated": [], "errors": []}

            # 각 템플릿에 대해 엔티티 발견 및 등록
            for template_id, template in self.entity_templates.items():
                try:
                    entity_id = template_id

                    # 기존 엔티티 확인
                    existing_entity = self._find_existing_entity(
                        meta_config, template["name"]
                    )

                    if existing_entity:
                        # 기존 엔티티 업데이트 확인
                        if await self._needs_update(existing_entity, template):
                            updated_entity = await self._update_entity(
                                existing_entity, template
                            )
                            results["updated"].append(
                                {
                                    "entity_id": entity_id,
                                    "name": template["name"],
                                    "changes": updated_entity,
                                }
                            )
                    else:
                        # 새 엔티티 등록
                        new_entity = await self._register_new_entity(
                            template, meta_config
                        )
                        if new_entity:
                            results["registered"].append(
                                {
                                    "entity_id": entity_id,
                                    "name": template["name"],
                                    "entity": new_entity,
                                }
                            )

                    results["discovered"].append(
                        {
                            "entity_id": entity_id,
                            "name": template["name"],
                            "type": template["entity_type"],
                            "status": "processed",
                        }
                    )

                except Exception as e:
                    results["errors"].append(
                        {"entity_id": template_id, "error": str(e)}
                    )

            # 설정 파일 업데이트가 필요한 경우
            if results["registered"] or results["updated"]:
                await self._update_config_file(config_path, config, results)

            self.logger.info(
                f"엔티티 스캔 완료: {len(results['discovered'])}개 발견, "
                f"{len(results['registered'])}개 등록, {len(results['updated'])}개 업데이트"
            )

            return results

        except Exception as e:
            self.logger.error(f"엔티티 스캔 및 등록 실패: {e}")
            return {"error": str(e)}

    def _find_existing_entity(
        self, meta_config: dict, entity_name: str
    ) -> Optional[dict]:
        """기존 엔티티 찾기"""
        # Meta Ring에서 찾기
        if "meta_ring" in meta_config and "entities" in meta_config["meta_ring"]:
            for entity_id, entity in meta_config["meta_ring"]["entities"].items():
                if entity.get("name") == entity_name:
                    return entity

        # Warden World에서 찾기
        if "warden_world" in meta_config and "entities" in meta_config["warden_world"]:
            for entity_id, entity in meta_config["warden_world"]["entities"].items():
                if entity.get("name") == entity_name:
                    return entity

        return None

    async def _needs_update(self, existing_entity: dict, template: dict) -> bool:
        """엔티티 업데이트 필요성 확인"""
        # 설명 변경 확인
        if existing_entity.get("description") != template["description"]:
            return True

        # 활성화 조건 변경 확인
        if (
            existing_entity.get("activation_conditions")
            != template["activation_conditions"]
        ):
            return True

        return False

    async def _update_entity(self, existing_entity: dict, template: dict) -> dict:
        """기존 엔티티 업데이트"""
        changes = {}

        if existing_entity.get("description") != template["description"]:
            existing_entity["description"] = template["description"]
            changes["description"] = template["description"]

        if (
            existing_entity.get("activation_conditions")
            != template["activation_conditions"]
        ):
            existing_entity["activation_conditions"] = template["activation_conditions"]
            changes["activation_conditions"] = template["activation_conditions"]

        return changes

    async def _register_new_entity(
        self, template: dict, meta_config: dict
    ) -> Optional[dict]:
        """새 엔티티 등록"""
        try:
            entity_config = {
                "id": template["name"].replace(".", "_").lower(),
                "name": template["name"],
                "description": template["description"],
                "activation_conditions": template["activation_conditions"],
                "activation_priority": template.get("activation_priority", 5),
            }

            # 템플릿별 추가 설정
            entity_config.update(template.get("config_template", {}))

            return entity_config

        except Exception as e:
            self.logger.error(f"엔티티 등록 실패: {e}")
            return None

    async def _update_config_file(self, config_path: str, config: dict, results: dict):
        """설정 파일 업데이트"""
        try:
            # 새로 등록된 엔티티들을 설정에 추가
            for registered in results["registered"]:
                entity = registered["entity"]
                entity_type = None

                # 엔티티 타입에 따라 적절한 섹션에 추가
                for template_id, template in self.entity_templates.items():
                    if template["name"] == registered["name"]:
                        entity_type = template["entity_type"]
                        break

                if entity_type == "ring":
                    if "meta_ring" not in config["meta_signatures"]:
                        config["meta_signatures"]["meta_ring"] = {"entities": {}}
                    config["meta_signatures"]["meta_ring"]["entities"][
                        entity["id"]
                    ] = entity
                elif entity_type == "warden":
                    if "warden_world" not in config["meta_signatures"]:
                        config["meta_signatures"]["warden_world"] = {"entities": {}}
                    config["meta_signatures"]["warden_world"]["entities"][
                        entity["id"]
                    ] = entity

            # 설정 파일 저장
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, ensure_ascii=False, indent=2)

            self.logger.info(f"설정 파일 업데이트 완료: {config_path}")

        except Exception as e:
            self.logger.error(f"설정 파일 업데이트 실패: {e}")

    async def validate_entity_compatibility(
        self, entity_config: dict
    ) -> Dict[str, Any]:
        """엔티티 호환성 검증"""
        try:
            validation_results = {
                "valid": True,
                "warnings": [],
                "errors": [],
                "suggestions": [],
            }

            # 필수 필드 확인
            required_fields = ["id", "name", "description", "activation_conditions"]
            for field in required_fields:
                if field not in entity_config:
                    validation_results["errors"].append(f"필수 필드 누락: {field}")
                    validation_results["valid"] = False

            # 활성화 조건 문법 확인
            if "activation_conditions" in entity_config:
                for condition in entity_config["activation_conditions"]:
                    if not self._validate_condition_syntax(condition):
                        validation_results["warnings"].append(
                            f"의심스러운 조건 문법: {condition}"
                        )

            # 우선순위 확인
            if "activation_priority" in entity_config:
                priority = entity_config["activation_priority"]
                if not isinstance(priority, int) or priority < 0:
                    validation_results["errors"].append(
                        "우선순위는 0 이상의 정수여야 합니다"
                    )
                    validation_results["valid"] = False

            return validation_results

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"검증 중 오류: {e}"],
                "warnings": [],
                "suggestions": [],
            }

    def _validate_condition_syntax(self, condition: str) -> bool:
        """조건 문법 검증"""
        # 간단한 문법 검증 (실제로는 더 복잡한 파서가 필요)
        valid_operators = ["==", "!=", ">=", "<=", ">", "<", "in", "not in"]
        valid_variables = [
            "judgment",
            "emotion",
            "user",
            "liminal_score",
            "capsule",
            "warden_completed",
        ]

        for var in valid_variables:
            if var in condition:
                return True

        return False


class LiveConfigManager:
    """⚡ Live Configuration Manager - 실시간 설정 관리"""

    def __init__(self, automation_framework):
        self.framework = automation_framework
        self.active_configs = {}
        self.update_queue = asyncio.Queue()
        self.logger = logging.getLogger("LiveConfigManager")

    async def update_transition_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """전이 임계값 실시간 업데이트"""
        try:
            config_updates = {
                "meta_signatures": {
                    "liminal_bridge": {"transition_thresholds": thresholds}
                }
            }

            # 설정 유효성 검사
            for key, value in thresholds.items():
                if not (0.0 <= value <= 1.0):
                    raise ValueError(f"임계값 범위 오류: {key} = {value}")

            # 설정 업데이트 큐에 추가
            await self.update_queue.put(
                {
                    "type": "threshold_update",
                    "updates": config_updates,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(f"전이 임계값 업데이트 요청: {thresholds}")
            return True

        except Exception as e:
            self.logger.error(f"전이 임계값 업데이트 실패: {e}")
            return False

    async def modify_emotion_triggers(
        self, entity_id: str, triggers: Dict[str, float]
    ) -> bool:
        """감정 트리거 수정"""
        try:
            # 엔티티별 감정 트리거 업데이트
            config_updates = {
                "meta_signatures": {
                    "warden_world": {
                        "emotion_resonance": {"detection_keywords": triggers}
                    }
                }
            }

            await self.update_queue.put(
                {
                    "type": "emotion_trigger_update",
                    "entity_id": entity_id,
                    "updates": config_updates,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(f"감정 트리거 수정: {entity_id} -> {triggers}")
            return True

        except Exception as e:
            self.logger.error(f"감정 트리거 수정 실패: {e}")
            return False

    async def adjust_existence_flow_patterns(self, flow_config: Dict[str, Any]) -> bool:
        """존재 흐름 패턴 조정"""
        try:
            config_updates = {
                "meta_signatures": {"warden_world": {"flow_control": flow_config}}
            }

            await self.update_queue.put(
                {
                    "type": "flow_pattern_update",
                    "updates": config_updates,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(f"존재 흐름 패턴 조정: {flow_config}")
            return True

        except Exception as e:
            self.logger.error(f"존재 흐름 패턴 조정 실패: {e}")
            return False

    async def process_config_updates(self):
        """설정 업데이트 처리"""
        while True:
            try:
                update_request = await self.update_queue.get()

                # 설정 파일 경로 결정
                config_path = "config/echo_system_config.yaml"

                # 설정 업데이트 실행
                success = await self.framework.config_kit.update_config(
                    config_path, update_request["updates"], hot_reload=True
                )

                if success:
                    self.logger.info(f"설정 업데이트 완료: {update_request['type']}")

                    # 관련 시스템에 변경 알림
                    await self._notify_config_change(update_request)
                else:
                    self.logger.error(f"설정 업데이트 실패: {update_request['type']}")

            except Exception as e:
                self.logger.error(f"설정 업데이트 처리 오류: {e}")
                await asyncio.sleep(1)

    async def _notify_config_change(self, update_request: dict):
        """설정 변경 알림"""
        # 실시간 모니터링 시스템에 알림
        if hasattr(self.framework, "monitoring_kit"):
            await self.framework.monitoring_kit._notify_subscribers(
                "config_updated",
                {
                    "type": update_request["type"],
                    "timestamp": update_request["timestamp"].isoformat(),
                },
            )


class MetaLiminalAutomationFramework:
    """🌀 Meta-Liminal Automation Framework - 메인 프레임워크"""

    def __init__(self, config_paths: List[str] = None):
        if config_paths is None:
            config_paths = ["config/echo_system_config.yaml"]

        self.config_paths = config_paths
        self.automation_level = AutomationLevel.FULL_AUTO
        self.is_running = False

        # 전문가 키트들
        self.config_kit = ConfigurationManagementKit(config_paths)
        self.monitoring_kit = RealTimeMonitoringKit()
        self.auto_discovery = MetaLiminalAutoDiscovery()
        self.live_config_manager = LiveConfigManager(self)

        # 시스템 상태
        self.system_status = {
            "framework_active": False,
            "last_scan_time": None,
            "registered_entities": {},
            "active_automations": [],
            "error_count": 0,
            "uptime_start": None,
        }

        self.logger = logging.getLogger("MetaLiminalFramework")

    async def initialize(self) -> bool:
        """프레임워크 초기화"""
        try:
            self.logger.info("Meta-Liminal Automation Framework 초기화 시작")

            # 설정 모니터링 시작
            self.config_kit.start_monitoring()

            # 콜백 등록
            self.config_kit.register_update_callback(self._on_config_update)

            # 초기 엔티티 스캔
            await self._initial_entity_scan()

            # 시스템 상태 업데이트
            self.system_status["framework_active"] = True
            self.system_status["uptime_start"] = datetime.now()

            self.logger.info("Meta-Liminal Automation Framework 초기화 완료")
            return True

        except Exception as e:
            self.logger.error(f"프레임워크 초기화 실패: {e}")
            return False

    async def start_automation(self):
        """자동화 시작"""
        if self.is_running:
            self.logger.warning("자동화가 이미 실행 중입니다")
            return

        self.is_running = True
        self.logger.info("Meta-Liminal 자동화 시스템 시작")

        # 비동기 태스크들
        tasks = [
            self.monitoring_kit.start_monitoring(),
            self.live_config_manager.process_config_updates(),
            self._periodic_entity_scan(),
            self._health_check_loop(),
            self._self_healing_loop(),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"자동화 실행 오류: {e}")
        finally:
            self.is_running = False

    async def stop_automation(self):
        """자동화 중지"""
        self.is_running = False
        self.monitoring_kit.monitoring_active = False
        self.config_kit.stop_monitoring()

        self.system_status["framework_active"] = False
        self.logger.info("Meta-Liminal 자동화 시스템 중지")

    async def _initial_entity_scan(self):
        """초기 엔티티 스캔"""
        for config_path in self.config_paths:
            try:
                results = await self.auto_discovery.scan_and_register_entities(
                    config_path
                )

                self.system_status["last_scan_time"] = datetime.now()
                self.system_status["registered_entities"].update(
                    {
                        entity["entity_id"]: entity
                        for entity in results.get("discovered", [])
                    }
                )

                self.logger.info(f"초기 엔티티 스캔 완료: {config_path}")

            except Exception as e:
                self.logger.error(f"초기 엔티티 스캔 실패 ({config_path}): {e}")
                self.system_status["error_count"] += 1

    async def _periodic_entity_scan(self):
        """주기적 엔티티 스캔"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5분마다

                for config_path in self.config_paths:
                    results = await self.auto_discovery.scan_and_register_entities(
                        config_path
                    )

                    if results.get("registered") or results.get("updated"):
                        self.logger.info(
                            f"주기적 스캔에서 변경 사항 발견: {config_path}"
                        )

                self.system_status["last_scan_time"] = datetime.now()

            except Exception as e:
                self.logger.error(f"주기적 엔티티 스캔 오류: {e}")
                self.system_status["error_count"] += 1
                await asyncio.sleep(60)

    async def _health_check_loop(self):
        """건강 상태 점검"""
        while self.is_running:
            try:
                # 각 키트의 건강 상태 확인
                health_status = {
                    "config_kit": len(self.config_kit.observers) > 0,
                    "monitoring_kit": self.monitoring_kit.monitoring_active,
                    "auto_discovery": len(self.auto_discovery.entity_templates) > 0,
                    "live_config_manager": not self.live_config_manager.update_queue.empty()
                    or True,
                }

                # 문제 감지 시 알림
                for component, is_healthy in health_status.items():
                    if not is_healthy:
                        await self.monitoring_kit._create_alert(
                            "component_unhealthy",
                            f"구성 요소 건강 상태 불량: {component}",
                            "warning",
                        )

                await asyncio.sleep(60)  # 1분마다 점검

            except Exception as e:
                self.logger.error(f"건강 상태 점검 오류: {e}")
                await asyncio.sleep(120)

    async def _self_healing_loop(self):
        """자가 치유 시스템"""
        while self.is_running:
            try:
                # 오류 카운터 확인
                if self.system_status["error_count"] > 10:
                    self.logger.warning("높은 오류율 감지 - 자가 치유 프로세스 시작")

                    # 자동 복구 시도
                    await self._attempt_self_healing()

                    # 오류 카운터 리셋
                    self.system_status["error_count"] = 0

                # 메모리 정리
                if datetime.now().minute == 0:  # 매시간
                    await self._cleanup_resources()

                await asyncio.sleep(300)  # 5분마다

            except Exception as e:
                self.logger.error(f"자가 치유 루프 오류: {e}")
                await asyncio.sleep(600)

    async def _attempt_self_healing(self):
        """자동 복구 시도"""
        try:
            # 설정 모니터링 재시작
            if len(self.config_kit.observers) == 0:
                self.config_kit.start_monitoring()
                self.logger.info("설정 모니터링 재시작됨")

            # 엔티티 재스캔
            await self._initial_entity_scan()

            self.logger.info("자가 치유 프로세스 완료")

        except Exception as e:
            self.logger.error(f"자가 치유 실패: {e}")

    async def _cleanup_resources(self):
        """리소스 정리"""
        try:
            # 메트릭 데이터 정리 (오래된 것들)
            current_time = datetime.now()

            # 모니터링 데이터에서 1시간 이전 데이터 삭제
            for metric_key in list(self.monitoring_kit.metrics.keys()):
                metric = self.monitoring_kit.metrics[metric_key]
                if isinstance(metric, dict) and "timestamp" in metric:
                    metric_time = datetime.fromisoformat(metric["timestamp"])
                    if current_time - metric_time > timedelta(hours=1):
                        del self.monitoring_kit.metrics[metric_key]

            self.logger.debug("리소스 정리 완료")

        except Exception as e:
            self.logger.error(f"리소스 정리 오류: {e}")

    async def _on_config_update(self, config_path: str, config: dict):
        """설정 업데이트 콜백"""
        self.logger.info(f"설정 업데이트 감지: {config_path}")

        # 설정 변경에 따른 엔티티 재스캔
        if "meta_signatures" in config:
            results = await self.auto_discovery.scan_and_register_entities(config_path)
            if results.get("updated"):
                self.logger.info("설정 변경으로 인한 엔티티 업데이트 완료")

    def get_system_status(self) -> dict:
        """시스템 상태 반환"""
        status = self.system_status.copy()

        if status["uptime_start"]:
            status["uptime"] = str(datetime.now() - status["uptime_start"])

        # 현재 메트릭 추가
        status["current_metrics"] = self.monitoring_kit.get_current_metrics()

        return status

    async def trigger_manual_scan(self) -> dict:
        """수동 엔티티 스캔 트리거"""
        results = {}

        for config_path in self.config_paths:
            try:
                scan_result = await self.auto_discovery.scan_and_register_entities(
                    config_path
                )
                results[config_path] = scan_result
            except Exception as e:
                results[config_path] = {"error": str(e)}

        return results


# 전역 프레임워크 인스턴스
_automation_framework = None


def get_automation_framework() -> MetaLiminalAutomationFramework:
    """자동화 프레임워크 싱글톤 반환"""
    global _automation_framework
    if _automation_framework is None:
        _automation_framework = MetaLiminalAutomationFramework()
    return _automation_framework


async def initialize_automation() -> bool:
    """자동화 시스템 초기화"""
    framework = get_automation_framework()
    return await framework.initialize()


async def start_automation():
    """자동화 시스템 시작"""
    framework = get_automation_framework()
    await framework.start_automation()


if __name__ == "__main__":
    # 테스트 실행
    async def test_automation():
        print("🌀 Meta-Liminal Automation Framework 테스트 시작")

        # 프레임워크 초기화
        framework = get_automation_framework()

        if await framework.initialize():
            print("✅ 프레임워크 초기화 성공")

            # 짧은 시간 동안 자동화 실행 테스트
            try:
                # 타임아웃을 걸고 테스트
                await asyncio.wait_for(framework.start_automation(), timeout=30)
            except asyncio.TimeoutError:
                print("⏰ 테스트 타임아웃 - 정상 종료")
                await framework.stop_automation()

            # 시스템 상태 출력
            status = framework.get_system_status()
            print(f"📊 시스템 상태: {json.dumps(status, indent=2, default=str)}")
        else:
            print("❌ 프레임워크 초기화 실패")

    asyncio.run(test_automation())
