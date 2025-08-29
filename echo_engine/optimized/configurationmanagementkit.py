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