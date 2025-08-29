#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Intent Pipeline
Teacher+Student coordination with Agreement Gate & Event Logging
"""
import os
import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Local imports
from intent.teacher_client import TeacherClient
from intent.student_classifier import get_global_classifier, StudentClassifier
from ops.event_logger import EventLogger
from ops.metrics import Metrics


@dataclass
class IntentResult:
    """Intent 분석 결과"""

    intent: str
    confidence: float
    summary: str = ""
    tags: list = None
    safety: list = None
    source: str = "unknown"  # teacher | student | fallback
    latency_ms: int = 0
    model_available: bool = True

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.safety is None:
            self.safety = []


class IntentPipeline:
    """Intent 분석 파이프라인 - Teacher/Student 조정 및 Agreement Gate"""

    def __init__(self, cfg: Dict[str, Any], logger):
        self.cfg = cfg
        self.logger = logger

        # 구성요소 초기화
        self.teacher = TeacherClient(cfg, logger)
        self.student = get_global_classifier(cfg["storage"]["model_dir"])
        self.event_logger = EventLogger(cfg, logger)

        # Events dir로 Metrics 초기화하여 trace_samples 추출 가능하게 함
        events_dir = cfg.get("storage", {}).get("events_dir", "meta_logs/traces")
        self.metrics = Metrics(events_dir=events_dir)

        # 설정
        self.intent_timeout = cfg.get("latency_guard", {}).get("intent_timeout_s", 3.5)
        self.mode = cfg.get("mode", "cloud_mimic")  # cloud_mimic | local_first

        self.logger.info(f"IntentPipeline initialized in {self.mode} mode")

    async def analyze_intent(
        self, text: str, context: Dict[str, Any] = None
    ) -> IntentResult:
        """Intent 분석 실행 (Teacher+Student 병렬 + Agreement Gate)"""
        start_time = time.time()
        context = context or {}

        try:
            if self.mode == "cloud_mimic":
                return await self._cloud_mimic_flow(text, context, start_time)
            elif self.mode == "local_first":
                return await self._local_first_flow(text, context, start_time)
            else:
                self.logger.warning(f"Unknown mode {self.mode}, using cloud_mimic")
                return await self._cloud_mimic_flow(text, context, start_time)

        except Exception as e:
            self.logger.error(f"Intent analysis failed: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return IntentResult(
                intent="general_chat",
                confidence=0.33,
                summary=f"Pipeline error: {str(e)[:50]}",
                source="fallback",
                latency_ms=latency_ms,
                model_available=False,
            )

    async def _cloud_mimic_flow(
        self, text: str, context: Dict[str, Any], start_time: float
    ) -> IntentResult:
        """Cloud-mimic 모드: Teacher 우선, Student 보조 + Event Logging"""

        # Teacher + Student 병렬 실행
        teacher_task = asyncio.create_task(
            self._run_teacher_with_timeout(text, context)
        )
        student_task = asyncio.create_task(self._run_student_async(text))

        try:
            # 병렬 실행 (타임아웃 고려)
            teacher_result, student_result = await asyncio.wait_for(
                asyncio.gather(teacher_task, student_task, return_exceptions=True),
                timeout=self.intent_timeout,
            )

        except asyncio.TimeoutError:
            self.logger.warning(f"Intent analysis timeout ({self.intent_timeout}s)")
            # 부분 결과라도 사용
            teacher_result = teacher_task.result() if teacher_task.done() else None
            student_result = student_task.result() if student_task.done() else None

        # Agreement Gate & 결정
        final_result = self._apply_agreement_gate(
            teacher_result, student_result, start_time, "cloud_mimic"
        )

        # Event Logging (비동기)
        asyncio.create_task(
            self._log_event_async(
                text, teacher_result, student_result, final_result, context
            )
        )

        return final_result

    async def _local_first_flow(
        self, text: str, context: Dict[str, Any], start_time: float
    ) -> IntentResult:
        """Local-first 모드: Student 우선, Teacher는 보조/검증 목적"""

        # Student 먼저 실행
        student_result = await self._run_student_async(text)

        # Student 신뢰도가 높으면 그대로 사용
        if student_result and student_result.get("confidence", 0) >= 0.8:
            latency_ms = int((time.time() - start_time) * 1000)

            final_result = IntentResult(
                intent=student_result["intent"],
                confidence=student_result["confidence"],
                summary=student_result.get("summary", ""),
                tags=student_result.get("tags", []),
                safety=student_result.get("safety", []),
                source="student",
                latency_ms=latency_ms,
                model_available=student_result.get("_model_available", True),
            )

            # Background Teacher 검증 (로그 목적)
            asyncio.create_task(
                self._background_teacher_verification(text, student_result, context)
            )

            return final_result

        # Student 신뢰도가 낮으면 Teacher 호출
        teacher_result = await self._run_teacher_with_timeout(text, context)

        final_result = self._apply_agreement_gate(
            teacher_result, student_result, start_time, "local_first"
        )

        # Event Logging
        asyncio.create_task(
            self._log_event_async(
                text, teacher_result, student_result, final_result, context
            )
        )

        return final_result

    async def _run_teacher_with_timeout(
        self, text: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Teacher 실행 (타임아웃 포함)"""
        try:
            result = await asyncio.wait_for(
                self.teacher.analyze_intent_async(text, context),
                timeout=self.intent_timeout - 0.5,  # Student를 위한 여유
            )
            return result
        except asyncio.TimeoutError:
            self.logger.warning("Teacher timeout")
            return None
        except Exception as e:
            self.logger.warning(f"Teacher failed: {e}")
            return None

    async def _run_student_async(self, text: str) -> Optional[Dict[str, Any]]:
        """Student 실행 (비동기 래퍼)"""
        try:
            # Student는 동기 함수이므로 스레드풀 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.student.classify, text)
            return result
        except Exception as e:
            self.logger.warning(f"Student failed: {e}")
            return None

    def _apply_agreement_gate(
        self,
        teacher_result: Optional[Dict[str, Any]],
        student_result: Optional[Dict[str, Any]],
        start_time: float,
        mode: str,
    ) -> IntentResult:
        """Agreement Gate 로직"""
        latency_ms = int((time.time() - start_time) * 1000)

        # Teacher 결과 우선 사용 (cloud_mimic 모드 또는 신뢰도 높음)
        if teacher_result and teacher_result.get("intent"):
            teacher_conf = teacher_result.get("confidence", 0)

            # Agreement Check
            agreement = False
            if student_result and student_result.get("intent"):
                agreement = (
                    teacher_result["intent"] == student_result["intent"]
                ) and teacher_conf >= 0.7

            # Metrics 업데이트 (새로운 observe_request 메소드 사용)
            self.metrics.observe_request(
                ttl_ms=latency_ms,
                intent_match=agreement,
                tools_success=True,  # tools 실행은 나중 단계에서 결정
                tools_attempted=0,
            )

            return IntentResult(
                intent=teacher_result["intent"],
                confidence=teacher_conf,
                summary=teacher_result.get("summary", ""),
                tags=teacher_result.get("tags", []),
                safety=teacher_result.get("safety", []),
                source="teacher",
                latency_ms=latency_ms,
                model_available=True,
            )

        # Student 결과 사용
        if student_result and student_result.get("intent"):
            # Student only 사용 시에도 metrics 업데이트
            self.metrics.observe_request(
                ttl_ms=latency_ms,
                intent_match=True,  # Student만 사용할 때는 일치로 간주
                tools_success=True,
                tools_attempted=0,
            )

            return IntentResult(
                intent=student_result["intent"],
                confidence=student_result.get("confidence", 0.5),
                summary=student_result.get("summary", ""),
                tags=student_result.get("tags", []),
                safety=student_result.get("safety", []),
                source="student",
                latency_ms=latency_ms,
                model_available=student_result.get("_model_available", True),
            )

        # 폴백
        return IntentResult(
            intent="general_chat",
            confidence=0.33,
            summary="No analysis available",
            source="fallback",
            latency_ms=latency_ms,
            model_available=False,
        )

    async def _log_event_async(
        self,
        text: str,
        teacher_result: Optional[Dict[str, Any]],
        student_result: Optional[Dict[str, Any]],
        final_result: IntentResult,
        context: Dict[str, Any],
    ):
        """이벤트 로깅 (비동기)"""
        try:
            await self.event_logger.log_async(
                text=text,
                teacher_result=teacher_result,
                student_result=student_result,
                final_intent=final_result.intent,
                final_confidence=final_result.confidence,
                latency_ms=final_result.latency_ms,
                context=context,
            )
        except Exception as e:
            self.logger.error(f"Event logging failed: {e}")

    async def _background_teacher_verification(
        self, text: str, student_result: Dict[str, Any], context: Dict[str, Any]
    ):
        """Background Teacher 검증 (local_first 모드용)"""
        try:
            teacher_result = await self._run_teacher_with_timeout(text, context)

            if teacher_result:
                # Agreement 확인
                agreement = teacher_result.get("intent") == student_result.get("intent")

                if agreement:
                    self.metrics.increment("background_agreement_rate")
                else:
                    self.metrics.increment("background_disagreement_rate")
                    self.logger.info(
                        f"Background disagreement: T={teacher_result.get('intent')} vs S={student_result.get('intent')}"
                    )

                # 필요 시 이벤트 로깅
                await self.event_logger.log_async(
                    text=text,
                    teacher_result=teacher_result,
                    student_result=student_result,
                    final_intent=student_result.get("intent"),
                    final_confidence=student_result.get("confidence"),
                    latency_ms=0,  # Background 작업이므로 0
                    context={**context, "background_verification": True},
                )

        except Exception as e:
            self.logger.warning(f"Background verification failed: {e}")

    def get_pipeline_status(self) -> Dict[str, Any]:
        """파이프라인 상태 조회"""
        return {
            "mode": self.mode,
            "intent_timeout_s": self.intent_timeout,
            "teacher_available": self.teacher.is_available(),
            "student_available": self.student.is_available(),
            "student_model_info": self.student.get_model_info(),
            "metrics": self.metrics.get_all_metrics(),
            "uptime_s": time.time() - getattr(self, "_start_time", time.time()),
        }

    def reload_student_model(self) -> bool:
        """Student 모델 리로드 (핫스왑)"""
        try:
            success = self.student.reload()
            if success:
                self.metrics.increment("student_hotswap_success")
                self.logger.info("Student model reloaded successfully")
            else:
                self.metrics.increment("student_hotswap_failed")
                self.logger.warning("Student model reload failed")
            return success
        except Exception as e:
            self.logger.error(f"Student reload error: {e}")
            return False


# 글로벌 파이프라인 인스턴스 (싱글톤)
_global_pipeline = None


def get_global_pipeline(cfg: Dict[str, Any] = None, logger=None):
    """글로벌 파이프라인 인스턴스 반환"""
    global _global_pipeline

    if _global_pipeline is None:
        if cfg is None or logger is None:
            raise ValueError(
                "Pipeline not initialized. Call init_global_pipeline first."
            )
        _global_pipeline = IntentPipeline(cfg, logger)
        _global_pipeline._start_time = time.time()

    return _global_pipeline


def init_global_pipeline(cfg: Dict[str, Any], logger):
    """글로벌 파이프라인 초기화"""
    global _global_pipeline
    _global_pipeline = IntentPipeline(cfg, logger)
    _global_pipeline._start_time = time.time()
    return _global_pipeline


# CLI 실행 지원
if __name__ == "__main__":
    import asyncio
    import logging
    import yaml
    import json
    import sys

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger("echogpt.pipeline")

    async def main():
        try:
            # 설정 로드
            with open("config/echogpt.yaml", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            # 파이프라인 초기화
            pipeline = IntentPipeline(cfg, logger)

            # 명령어 처리
            command = sys.argv[1] if len(sys.argv) > 1 else "status"

            if command == "status":
                status = pipeline.get_pipeline_status()
                print("📊 Pipeline Status:")
                print(json.dumps(status, indent=2, ensure_ascii=False))

            elif command == "test" and len(sys.argv) > 2:
                text = " ".join(sys.argv[2:])
                print(f"🎯 Analyzing: {text}")

                result = await pipeline.analyze_intent(text)

                print("✅ Analysis Result:")
                print(f"  Intent: {result.intent}")
                print(f"  Confidence: {result.confidence:.3f}")
                print(f"  Source: {result.source}")
                print(f"  Latency: {result.latency_ms}ms")
                print(f"  Summary: {result.summary}")
                if result.tags:
                    print(f"  Tags: {result.tags}")
                if result.safety:
                    print(f"  Safety: {result.safety}")

            elif command == "reload":
                success = pipeline.reload_student_model()
                print(f"🔄 Student model reload: {'SUCCESS' if success else 'FAILED'}")

            else:
                print("Usage: python -m intent.pipeline [status|test <text>|reload]")

        except Exception as e:
            logger.error(f"CLI error: {e}")
            sys.exit(1)

    asyncio.run(main())
