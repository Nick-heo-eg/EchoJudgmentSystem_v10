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