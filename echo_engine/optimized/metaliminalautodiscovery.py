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