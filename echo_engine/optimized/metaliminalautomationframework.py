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