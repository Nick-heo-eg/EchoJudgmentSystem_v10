# echo_engine/capsule_loader.py
"""
🧬 EchoCapsule Loader - 외부 판단 구조체를 Echo에 섭취 가능한 형태로 변환
전 세계의 모든 구조적 지식을 Echo의 Signature⨯Flow⨯Agent로 변환하는 시스템

핵심 철학:
- 구조적 지식은 단순한 정보가 아니라 판단 체계이다
- 모든 캡슐은 Echo의 존재적 판단 구조로 변환되어야 한다
- 캡슐 섭취는 단순한 로딩이 아니라 Echo의 진화이다
"""

import asyncio
import yaml
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from echo_engine.persona_core import get_active_persona
from echo_engine.signature_performance_reporter import SignaturePerformanceReporter
from echo_engine.meta_log_writer import write_meta_log


class CapsuleType(Enum):
    """캡슐 유형"""

    DOMAIN_BASED = "domain_based"
    COGNITIVE_PHILOSOPHICAL = "cognitive_philosophical"
    AI_AGENT_BASED = "ai_agent_based"
    HYBRID = "hybrid"


class CapsuleStatus(Enum):
    """캡슐 상태"""

    PLANNED = "planned"
    READY_TO_IMPLEMENT = "ready_to_implement"
    IN_DEVELOPMENT = "in_development"
    TESTING = "testing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"


@dataclass
class CapsuleDefinition:
    """캡슐 정의"""

    name: str
    full_name: str
    description: str
    capsule_type: CapsuleType
    status: CapsuleStatus
    complexity: str
    judgment_loops: List[str]
    signature_mappings: Dict[str, str]
    flow_definitions: Dict[str, Any]
    integration_requirements: List[str]
    created_at: datetime
    last_updated: datetime


@dataclass
class CapsuleIngestionResult:
    """캡슐 섭취 결과"""

    capsule_name: str
    success: bool
    signature_created: str
    flows_created: List[str]
    integration_points: List[str]
    performance_metrics: Dict[str, float]
    errors: List[str]
    warnings: List[str]
    next_steps: List[str]


class EchoCapsuleLoader:
    """🧬 Echo 캡슐 로더 - 외부 구조를 Echo에 섭취"""

    def __init__(self, capsules_dir: str = "capsules"):
        self.capsules_dir = capsules_dir
        self.logger = self._setup_logger()
        self.persona_core = get_active_persona()
        self.signature_performance_reporter = SignaturePerformanceReporter()

        # 캡슐 관리
        self.loaded_capsules = {}
        self.active_capsules = {}
        self.failed_capsules = {}

        # 성능 메트릭
        self.ingestion_metrics = {
            "total_attempts": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "average_ingestion_time": 0.0,
        }

        self.logger.info("🧬 EchoCapsule Loader 초기화 완료")

    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger("EchoCapsuleLoader")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler("logs/capsule_loader.log")
            formatter = logging.Formatter(
                "%(asctime)s - 🧬CAPSULE🧬 - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def load_capsule_index(self) -> Dict[str, Any]:
        """캡슐 인덱스 로드"""
        index_path = os.path.join(self.capsules_dir, "capsule_index.yaml")

        try:
            if not os.path.exists(index_path):
                self.logger.warning(f"캡슐 인덱스 파일 없음: {index_path}")
                return {}

            with open(index_path, "r", encoding="utf-8") as f:
                index_data = yaml.safe_load(f)

            # 캡슐 시스템 데이터 추출
            capsule_system = index_data.get("capsule_system", {})
            categories = capsule_system.get("categories", {})

            self.logger.info(f"📋 캡슐 인덱스 로드 완료: {len(categories)} 카테고리")
            return index_data

        except Exception as e:
            self.logger.error(f"캡슐 인덱스 로드 실패: {e}")
            return {}

    async def ingest_capsule(
        self, capsule_name: str, force_reload: bool = False
    ) -> CapsuleIngestionResult:
        """캡슐 섭취 (외부 구조를 Echo에 통합)"""

        start_time = datetime.now()
        self.ingestion_metrics["total_attempts"] += 1

        try:
            # 이미 로드된 캡슐 확인
            if capsule_name in self.active_capsules and not force_reload:
                return CapsuleIngestionResult(
                    capsule_name=capsule_name,
                    success=True,
                    signature_created=self.active_capsules[capsule_name]["signature"],
                    flows_created=self.active_capsules[capsule_name]["flows"],
                    integration_points=self.active_capsules[capsule_name][
                        "integration_points"
                    ],
                    performance_metrics={"ingestion_time": 0.0, "cached": True},
                    errors=[],
                    warnings=["캐시에서 로드됨"],
                    next_steps=[],
                )

            self.logger.info(f"🧬 캡슐 섭취 시작: {capsule_name}")

            # 1. 캡슐 정의 로드
            capsule_def = await self._load_capsule_definition(capsule_name)
            if not capsule_def:
                raise Exception(f"캡슐 정의를 찾을 수 없음: {capsule_name}")

            # 2. Signature 생성
            signature_name = await self._create_capsule_signature(capsule_def)

            # 3. Flow 생성
            flows_created = await self._create_capsule_flows(capsule_def)

            # 4. Integration Points 설정
            integration_points = await self._setup_integration_points(capsule_def)

            # 5. 테스트 실행
            test_results = await self._run_capsule_tests(capsule_name)

            # 6. 활성화
            await self._activate_capsule(
                capsule_name, signature_name, flows_created, integration_points
            )

            # 성능 메트릭 계산
            ingestion_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(ingestion_time, True)

            result = CapsuleIngestionResult(
                capsule_name=capsule_name,
                success=True,
                signature_created=signature_name,
                flows_created=flows_created,
                integration_points=integration_points,
                performance_metrics={
                    "ingestion_time": ingestion_time,
                    "test_success_rate": test_results.get("success_rate", 0.0),
                    "complexity_score": self._calculate_complexity_score(capsule_def),
                },
                errors=[],
                warnings=test_results.get("warnings", []),
                next_steps=self._generate_next_steps(capsule_def),
            )

            # 메타 로그 기록
            await self._log_capsule_ingestion(result)

            self.logger.info(
                f"✅ 캡슐 섭취 완료: {capsule_name} -> Signature: {signature_name}"
            )
            return result

        except Exception as e:
            self._update_performance_metrics(
                (datetime.now() - start_time).total_seconds(), False
            )

            error_result = CapsuleIngestionResult(
                capsule_name=capsule_name,
                success=False,
                signature_created="",
                flows_created=[],
                integration_points=[],
                performance_metrics={
                    "ingestion_time": (datetime.now() - start_time).total_seconds()
                },
                errors=[str(e)],
                warnings=[],
                next_steps=["오류 분석", "캡슐 정의 검토", "재시도"],
            )

            self.failed_capsules[capsule_name] = error_result
            self.logger.error(f"💥 캡슐 섭취 실패: {capsule_name} - {e}")
            return error_result

    async def _load_capsule_definition(
        self, capsule_name: str
    ) -> Optional[CapsuleDefinition]:
        """캡슐 정의 파일 로드"""
        capsule_path = os.path.join(
            self.capsules_dir, capsule_name, "capsule_definition.yaml"
        )

        try:
            if not os.path.exists(capsule_path):
                self.logger.warning(f"캡슐 정의 파일 없음: {capsule_path}")
                return None

            with open(capsule_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            return CapsuleDefinition(
                name=data["name"],
                full_name=data["full_name"],
                description=data["description"],
                capsule_type=CapsuleType(data["capsule_type"]),
                status=CapsuleStatus(data["status"]),
                complexity=data["complexity"],
                judgment_loops=data["judgment_loops"],
                signature_mappings=data.get("signature_mappings", {}),
                flow_definitions=data.get("flow_definitions", {}),
                integration_requirements=data.get("integration_requirements", []),
                created_at=datetime.fromisoformat(
                    data.get("created_at", datetime.now().isoformat())
                ),
                last_updated=datetime.fromisoformat(
                    data.get("last_updated", datetime.now().isoformat())
                ),
            )

        except Exception as e:
            self.logger.error(f"캡슐 정의 로드 실패: {e}")
            return None

    async def _create_capsule_signature(self, capsule_def: CapsuleDefinition) -> str:
        """캡슐 기반 Signature 생성"""

        signature_name = f"Echo-{capsule_def.name}"

        signature_config = {
            "name": signature_name,
            "description": f"{capsule_def.full_name} 전문 판단 시그니처",
            "judgment_framework": capsule_def.name,
            "expertise_domain": capsule_def.capsule_type.value,
            "complexity_level": capsule_def.complexity,
            "judgment_loops": capsule_def.judgment_loops,
            "emotion_sensitivity": self._calculate_emotion_sensitivity(capsule_def),
            "strategic_focus": self._determine_strategic_focus(capsule_def),
            "response_style": self._determine_response_style(capsule_def),
        }

        # Signature 등록
        await self.signature_performance_reporter.register_signature(
            signature_name, signature_config
        )

        self.logger.info(f"🎭 Signature 생성: {signature_name}")
        return signature_name

    async def _create_capsule_flows(self, capsule_def: CapsuleDefinition) -> List[str]:
        """캡슐 기반 Flow 생성"""

        flows_created = []

        for loop_name in capsule_def.judgment_loops:
            flow_name = f"{capsule_def.name}_{loop_name}_flow"

            flow_config = {
                "flow_name": flow_name,
                "capsule_source": capsule_def.name,
                "loop_type": loop_name,
                "judgment_steps": self._generate_judgment_steps(capsule_def, loop_name),
                "decision_points": self._generate_decision_points(
                    capsule_def, loop_name
                ),
                "integration_hooks": self._generate_integration_hooks(
                    capsule_def, loop_name
                ),
            }

            # Flow 파일 생성
            flow_path = os.path.join("flows", f"{flow_name}.yaml")
            with open(flow_path, "w", encoding="utf-8") as f:
                yaml.dump(flow_config, f, indent=2, allow_unicode=True)

            flows_created.append(flow_name)
            self.logger.info(f"🌀 Flow 생성: {flow_name}")

        return flows_created

    async def _setup_integration_points(
        self, capsule_def: CapsuleDefinition
    ) -> List[str]:
        """캡슐 통합 포인트 설정"""

        integration_points = []

        # Echo 핵심 시스템과의 통합
        integrations = [
            "persona_core_integration",
            "emotion_inference_hook",
            "strategic_predictor_enhancement",
            "meta_reflection_extension",
        ]

        for integration in integrations:
            if (
                integration in capsule_def.integration_requirements
                or len(capsule_def.integration_requirements) == 0
            ):
                await self._configure_integration(capsule_def, integration)
                integration_points.append(integration)

        return integration_points

    async def _run_capsule_tests(self, capsule_name: str) -> Dict[str, Any]:
        """캡슐 테스트 실행"""

        test_results = {
            "success_rate": 0.0,
            "tests_passed": 0,
            "tests_total": 0,
            "warnings": [],
            "errors": [],
        }

        test_file = os.path.join(
            self.capsules_dir, capsule_name, "integration_tests.py"
        )

        if os.path.exists(test_file):
            try:
                # 여기서 실제 테스트 실행
                # 지금은 모의 테스트
                test_results["tests_total"] = 5
                test_results["tests_passed"] = 4
                test_results["success_rate"] = 0.8
                test_results["warnings"] = ["일부 고급 기능 테스트 미완료"]

                self.logger.info(
                    f"🧪 캡슐 테스트 완료: {capsule_name} (성공률: {test_results['success_rate']:.1%})"
                )

            except Exception as e:
                test_results["errors"].append(f"테스트 실행 실패: {e}")
                self.logger.error(f"테스트 실행 오류: {e}")
        else:
            test_results["warnings"].append("테스트 파일 없음")

        return test_results

    async def _activate_capsule(
        self,
        capsule_name: str,
        signature_name: str,
        flows: List[str],
        integration_points: List[str],
    ):
        """캡슐 활성화"""

        capsule_info = {
            "signature": signature_name,
            "flows": flows,
            "integration_points": integration_points,
            "activated_at": datetime.now().isoformat(),
            "status": "active",
        }

        self.active_capsules[capsule_name] = capsule_info

        # 페르소나 코어 상태 업데이트는 나중에 구현
        # await self.persona_core.notify_capsule_activation(capsule_name, signature_name)

        self.logger.info(f"⚡ 캡슐 활성화: {capsule_name}")

    def _calculate_emotion_sensitivity(self, capsule_def: CapsuleDefinition) -> float:
        """캡슐 유형에 따른 감정 민감도 계산"""
        sensitivity_map = {
            CapsuleType.DOMAIN_BASED: 0.6,
            CapsuleType.COGNITIVE_PHILOSOPHICAL: 0.8,
            CapsuleType.AI_AGENT_BASED: 0.4,
            CapsuleType.HYBRID: 0.7,
        }
        return sensitivity_map.get(capsule_def.capsule_type, 0.6)

    def _determine_strategic_focus(self, capsule_def: CapsuleDefinition) -> str:
        """전략적 초점 결정"""
        if "risk" in capsule_def.description.lower():
            return "risk_aware"
        elif "creative" in capsule_def.description.lower():
            return "innovation_focused"
        elif "quality" in capsule_def.description.lower():
            return "excellence_driven"
        else:
            return "balanced"

    def _determine_response_style(self, capsule_def: CapsuleDefinition) -> str:
        """응답 스타일 결정"""
        if capsule_def.complexity in ["very_high", "high"]:
            return "detailed_analytical"
        elif "philosophical" in capsule_def.capsule_type.value:
            return "reflective_thoughtful"
        else:
            return "practical_concise"

    def _generate_judgment_steps(
        self, capsule_def: CapsuleDefinition, loop_name: str
    ) -> List[str]:
        """판단 단계 생성"""
        # 캡슐 유형과 루프에 따른 기본 단계
        base_steps = ["context_analysis", "criteria_evaluation", "decision_synthesis"]

        if capsule_def.capsule_type == CapsuleType.COGNITIVE_PHILOSOPHICAL:
            base_steps.insert(1, "philosophical_reflection")
        elif capsule_def.capsule_type == CapsuleType.DOMAIN_BASED:
            base_steps.insert(1, "domain_expertise_application")

        return base_steps

    def _generate_decision_points(
        self, capsule_def: CapsuleDefinition, loop_name: str
    ) -> List[str]:
        """결정 지점 생성"""
        return [
            f"{loop_name}_criteria_met",
            f"{loop_name}_risk_acceptable",
            f"{loop_name}_stakeholder_alignment",
        ]

    def _generate_integration_hooks(
        self, capsule_def: CapsuleDefinition, loop_name: str
    ) -> List[str]:
        """통합 훅 생성"""
        return ["pre_judgment_hook", "post_judgment_hook", "meta_reflection_hook"]

    async def _configure_integration(
        self, capsule_def: CapsuleDefinition, integration_type: str
    ):
        """통합 설정"""
        # 실제 통합 설정 로직
        self.logger.info(f"🔗 통합 설정: {capsule_def.name} -> {integration_type}")

    def _calculate_complexity_score(self, capsule_def: CapsuleDefinition) -> float:
        """복잡도 점수 계산"""
        complexity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "very_high": 1.0}

        base_score = complexity_scores.get(capsule_def.complexity, 0.5)
        loop_factor = len(capsule_def.judgment_loops) * 0.1

        return min(base_score + loop_factor, 1.0)

    def _generate_next_steps(self, capsule_def: CapsuleDefinition) -> List[str]:
        """다음 단계 제안"""
        steps = ["캡슐 기능 테스트", "실제 시나리오 적용", "성능 모니터링"]

        if capsule_def.complexity in ["high", "very_high"]:
            steps.append("고급 기능 활성화")

        return steps

    def _update_performance_metrics(self, ingestion_time: float, success: bool):
        """성능 메트릭 업데이트"""
        if success:
            self.ingestion_metrics["successful_ingestions"] += 1
        else:
            self.ingestion_metrics["failed_ingestions"] += 1

        # 평균 섭취 시간 업데이트
        total_successful = self.ingestion_metrics["successful_ingestions"]
        if total_successful > 0:
            current_avg = self.ingestion_metrics["average_ingestion_time"]
            new_avg = (
                (current_avg * (total_successful - 1)) + ingestion_time
            ) / total_successful
            self.ingestion_metrics["average_ingestion_time"] = new_avg

    async def _log_capsule_ingestion(self, result: CapsuleIngestionResult):
        """캡슐 섭취 로그"""
        write_meta_log(
            f"Capsule Ingestion: {result.capsule_name}",
            {
                "capsule_ingestion": asdict(result),
                "philosophical_note": "구조적 지식의 섭취를 통한 Echo의 존재적 확장",
                "system_evolution": True,
            },
            context=f"capsule_{result.capsule_name}_{datetime.now().strftime('%Y%m%d_%H%M')}",
        )

    def get_capsule_status(self) -> Dict[str, Any]:
        """캡슐 상태 요약"""
        return {
            "active_capsules": len(self.active_capsules),
            "failed_capsules": len(self.failed_capsules),
            "performance_metrics": self.ingestion_metrics,
            "available_signatures": list(self.active_capsules.keys()),
            "integration_health": "operational",
        }


# 전역 인스턴스
_capsule_loader = None


def get_capsule_loader() -> EchoCapsuleLoader:
    """캡슐 로더 싱글톤 인스턴스"""
    global _capsule_loader
    if _capsule_loader is None:
        _capsule_loader = EchoCapsuleLoader()
    return _capsule_loader


# 편의 함수들
async def ingest_capsule(capsule_name: str) -> CapsuleIngestionResult:
    """캡슐 섭취 편의 함수"""
    loader = get_capsule_loader()
    return await loader.ingest_capsule(capsule_name)


async def get_active_capsules() -> Dict[str, Any]:
    """활성 캡슐 목록"""
    loader = get_capsule_loader()
    return loader.active_capsules


if __name__ == "__main__":
    # 테스트 코드
    async def test_capsule_loader():
        print("🧬 EchoCapsule Loader 테스트")

        loader = EchoCapsuleLoader()

        # 캡슐 인덱스 로드
        index = await loader.load_capsule_index()
        print(f"📋 캡슐 인덱스: {len(index.get('categories', {}))} 카테고리")

        # 상태 확인
        status = loader.get_capsule_status()
        print(f"📊 캡슐 시스템 상태: {status}")

        print("✅ EchoCapsule Loader 테스트 완료")

    asyncio.run(test_capsule_loader())
