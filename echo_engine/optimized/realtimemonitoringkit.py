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