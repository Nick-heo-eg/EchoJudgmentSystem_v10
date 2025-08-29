from __future__ import annotations
import logging
import os
import platform
from typing import TYPE_CHECKING
from echo_engine.amoeba.env_detect import detect_cloud
from echo_engine.base import BaseAdapter

try:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager
except ImportError as e:
    print(f"⚠️ Amoeba Manager 로드 실패: {e}")

"""
🌌 Cloud Adapter for Amoeba v0.2
클라우드 환경 (AWS/Azure/GCP) 특화 어댑터
"""





if TYPE_CHECKING:
    pass  # Type checking 전용 임포트가 있을 경우 여기에 추가

log = logging.getLogger("amoeba.cloud_adapter")


class CloudAdapter(BaseAdapter):
    """클라우드 환경 특화 어댑터"""

    name = "cloud"
    priority = 7  # 높은 우선순위

    def detect(self) -> bool:
        """클라우드 환경 감지"""
        cloud_info = detect_cloud()
        is_cloud = cloud_info.get("is_cloud", False)

        if is_cloud:
            provider = cloud_info.get("provider", "unknown")
            log.info(f"☁️ 클라우드 환경 감지: {provider.upper()}")

            if cloud_info.get("instance_type"):
                log.info(f"🏗️ 인스턴스 타입: {cloud_info['instance_type']}")

        return is_cloud

    def prelink(self, mgr: AmoebaManager) -> None:
        """클라우드 연결 전 준비"""
        log.info("🔧 클라우드 환경 준비 중...")

        cloud_info = detect_cloud()
        provider = cloud_info.get("provider", "unknown")

        # 클라우드 공통 설정
        os.environ["CLOUD_PROVIDER"] = provider.upper()
        os.environ["CLOUD_INSTANCE"] = "1"

        if provider == "aws":
            self._prepare_aws(mgr)
        elif provider == "azure":
            self._prepare_azure(mgr)
        elif provider == "gcp":
            self._prepare_gcp(mgr)

        # 클라우드 공통 경로 매핑
        cloud_paths = {
            "/mnt/cloud": "/opt/cloud",
            "/cloud-storage": "/mnt/storage",
            "/logs": os.path.join(
                os.path.expanduser("~"), ".cache", "echo", "logs", r"cloud"
            ),
        }

        mgr.linker.path_mapper.mappings.update(cloud_paths)

    def _prepare_aws(self, mgr: AmoebaManager) -> None:
        """AWS 환경 준비"""
        log.info("🚀 AWS 환경 설정")

        # AWS 메타데이터 서비스 설정
        os.environ["AWS_METADATA_SERVICE_TIMEOUT"] = "5"
        os.environ["AWS_METADATA_SERVICE_NUM_ATTEMPTS"] = "2"

        # ECS 태스크인지 확인
        if os.getenv("AWS_EXECUTION_ROLE_ARN"):
            os.environ["AWS_ECS_TASK"] = "1"
            log.info("📦 ECS 태스크 환경 감지")

        # Lambda 환경인지 확인
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            os.environ["AWS_LAMBDA"] = "1"
            log.info("⚡ Lambda 환경 감지")

    def _prepare_azure(self, mgr: AmoebaManager) -> None:
        """Azure 환경 준비"""
        log.info("🔷 Azure 환경 설정")

        # Azure 메타데이터 설정
        os.environ["AZURE_METADATA_TIMEOUT"] = "5"

        # App Service인지 확인
        if os.getenv("WEBSITE_SITE_NAME"):
            os.environ["AZURE_APP_SERVICE"] = "1"
            log.info("🌐 App Service 환경 감지")

    def _prepare_gcp(self, mgr: AmoebaManager) -> None:
        """GCP 환경 준비"""
        log.info("🌈 GCP 환경 설정")

        # GCP 메타데이터 설정
        os.environ["GCE_METADATA_TIMEOUT"] = "5"

        # Cloud Run인지 확인
        if os.getenv("K_SERVICE"):
            os.environ["GCP_CLOUD_RUN"] = "1"
            log.info("🏃 Cloud Run 환경 감지")

    def link(self, mgr: AmoebaManager) -> None:
        """클라우드 시스템 연결"""
        log.info("🔗 클라우드 시스템 연결 중...")

        cloud_info = detect_cloud()
        provider = cloud_info.get("provider", "unknown")

        # 클라우드 서비스 등록
        mgr.linker.register_service(
            "cloud_provider",
            {
                "provider": provider,
                "instance_type": cloud_info.get("instance_type"),
                "region": self._detect_region(provider),
                "availability_zone": self._detect_az(provider),
            },
        )

        # 클라우드 스토리지 서비스
        mgr.linker.register_service(
            "cloud_storage", {"provider": provider, "available": True}
        )

        # 로그 수집 서비스
        mgr.linker.register_service(
            "cloud_logging", {"provider": provider, "centralized": True}
        )

        # 메트릭 수집 서비스
        mgr.linker.register_service(
            "cloud_metrics", {"provider": provider, "enabled": True}
        )

        log.info("✅ 클라우드 연결 완료")

    def _detect_region(self, provider: str) -> str:
        """클라우드 리전 감지"""
        if provider == "aws":
            return os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "unknown"))
        elif provider == "azure":
            return os.getenv("AZURE_REGION", "unknown")
        elif provider == "gcp":
            return os.getenv("GOOGLE_CLOUD_REGION", "unknown")
        return "unknown"

    def _detect_az(self, provider: str) -> str:
        """가용 영역 감지"""
        # 실제로는 메타데이터 API를 통해 가져와야 하지만,
        # 여기서는 환경변수 기반으로 간단히 처리
        if provider == "aws":
            return os.getenv("AWS_AVAILABILITY_ZONE", "unknown")
        return "unknown"

    def optimize(self, mgr: AmoebaManager) -> None:
        """클라우드 환경 최적화"""
        log.info("⚡ 클라우드 환경 최적화 시작...")

        # 클라우드 공통 최적화
        mgr.optimizer.apply_cloud_optimizations()

        # 메모리 최적화 (클라우드는 보통 메모리 제한)
        mgr.optimizer.optimize_memory()

        # 네트워크 최적화
        self._optimize_network(mgr)

        # 로깅 최적화 (클라우드 로그 수집)
        self._optimize_logging(mgr)

        # 메트릭 최적화
        self._optimize_metrics(mgr)

        cloud_info = detect_cloud()
        provider = cloud_info.get("provider", "unknown")

        if provider == "aws":
            self._optimize_aws(mgr)
        elif provider == "azure":
            self._optimize_azure(mgr)
        elif provider == "gcp":
            self._optimize_gcp(mgr)

        log.info("✅ 클라우드 최적화 완료")

    def _optimize_network(self, mgr: AmoebaManager) -> None:
        """네트워크 최적화"""
        # 클라우드 환경에서 네트워크 지연 최적화
        os.environ["REQUESTS_TIMEOUT"] = "30"
        os.environ["HTTPX_TIMEOUT"] = "30"

        mgr.optimizer.optimizations_applied.append("cloud_network_optimization")

    def _optimize_logging(self, mgr: AmoebaManager) -> None:
        """로깅 최적화"""
        # 구조화된 로깅 활성화
        os.environ["LOG_FORMAT"] = "json"
        os.environ["LOG_LEVEL"] = "INFO"

        mgr.optimizer.optimizations_applied.append("cloud_logging_optimization")

    def _optimize_metrics(self, mgr: AmoebaManager) -> None:
        """메트릭 최적화"""
        # 메트릭 수집 활성화
        os.environ["METRICS_ENABLED"] = "1"
        os.environ["TELEMETRY_ENABLED"] = "1"

        mgr.optimizer.optimizations_applied.append("cloud_metrics_optimization")

    def _optimize_aws(self, mgr: AmoebaManager) -> None:
        """AWS 특화 최적화"""
        # X-Ray 트레이싱
        if not os.getenv("_X_AMZN_TRACE_ID"):
            os.environ["AWS_XRAY_TRACING_NAME"] = "echo-amoeba"

        # CloudWatch 로그
        os.environ["AWS_CLOUDWATCH_ENABLED"] = "1"

        mgr.optimizer.optimizations_applied.append("aws_optimization")

    def _optimize_azure(self, mgr: AmoebaManager) -> None:
        """Azure 특화 최적화"""
        # Application Insights
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = os.getenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
        )

        mgr.optimizer.optimizations_applied.append("azure_optimization")

    def _optimize_gcp(self, mgr: AmoebaManager) -> None:
        """GCP 특화 최적화"""
        # Cloud Logging
        os.environ["GOOGLE_CLOUD_LOGGING_ENABLED"] = "1"

        # Cloud Monitoring
        os.environ["GOOGLE_CLOUD_MONITORING_ENABLED"] = "1"

        mgr.optimizer.optimizations_applied.append("gcp_optimization")
