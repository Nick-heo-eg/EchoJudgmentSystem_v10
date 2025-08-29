#!/usr/bin/env python3
"""
🎮 Controller - 판단 결과의 실행 및 후처리

판단 결과를 받아 실행, 도구 호출, 기록, 피드백 등의 후처리를 담당하는 실행 컨트롤러.
AGI 판단 흐름의 마지막 단계를 처리하며 결과의 구체화를 담당.

핵심 역할:
1. 판단 결과 출력 및 형식화
2. 도구 실행 및 액션 처리
3. 기록 및 로깅
4. 피드백 수집 및 학습 데이터 생성
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging


@dataclass
class ExecutionResult:
    """실행 결과"""

    success: bool
    actions_performed: List[str]
    outputs_generated: List[Dict[str, Any]]
    execution_time: float
    error_messages: List[str]
    feedback_collected: Dict[str, Any]
    log_entries: List[Dict[str, Any]]


@dataclass
class ActionSpec:
    """액션 사양"""

    action_type: str
    parameters: Dict[str, Any]
    priority: int = 0
    timeout: float = 30.0
    retry_count: int = 0


class ResultController:
    """🎮 결과 처리 컨트롤러"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.version = "1.0.0"
        self.log_dir = log_dir or Path("data/agi_controller_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 실행 통계
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "actions_performed": {},
            "average_execution_time": 0.0,
            "error_count": 0,
        }

        # 액션 핸들러 등록
        self.action_handlers = self._register_action_handlers()

        # 로거 설정
        self.logger = self._setup_logger()

        print("🎮 Result Controller v1.0 초기화 완료")
        print(f"   로그 디렉토리: {self.log_dir}")

    def handle_result(self, judgment_result: Dict[str, Any]) -> ExecutionResult:
        """🎯 메인 결과 처리 함수"""
        start_time = time.time()
        self.execution_stats["total_executions"] += 1

        actions_performed = []
        outputs_generated = []
        error_messages = []
        log_entries = []

        try:
            print(
                f"🎮 결과 처리 시작: {judgment_result.get('strategy_applied', 'unknown')}"
            )

            # 1. 결과 분석 및 액션 계획 수립
            action_plan = self._create_action_plan(judgment_result)

            # 2. 기본 출력 생성
            output_result = self._generate_output(judgment_result)
            outputs_generated.append(output_result)
            actions_performed.append("output_generation")

            # 3. 계획된 액션 실행
            for action_spec in action_plan:
                try:
                    action_result = self._execute_action(action_spec, judgment_result)
                    if action_result["success"]:
                        actions_performed.append(action_spec.action_type)
                        if action_result.get("output"):
                            outputs_generated.append(action_result["output"])
                    else:
                        error_messages.append(
                            f"액션 {action_spec.action_type} 실패: {action_result.get('error', 'Unknown')}"
                        )

                except Exception as e:
                    error_messages.append(
                        f"액션 {action_spec.action_type} 실행 오류: {e}"
                    )
                    self.execution_stats["error_count"] += 1

            # 4. 로깅 및 기록
            log_entry = self._create_log_entry(
                judgment_result, actions_performed, outputs_generated
            )
            log_entries.append(log_entry)
            self._save_log_entry(log_entry)

            # 5. 피드백 수집
            feedback = self._collect_feedback(judgment_result, actions_performed)

            # 6. 통계 업데이트
            execution_time = time.time() - start_time
            self._update_execution_stats(
                actions_performed, execution_time, len(error_messages) == 0
            )

            result = ExecutionResult(
                success=len(error_messages) == 0,
                actions_performed=actions_performed,
                outputs_generated=outputs_generated,
                execution_time=execution_time,
                error_messages=error_messages,
                feedback_collected=feedback,
                log_entries=log_entries,
            )

            print(
                f"✅ 결과 처리 완료: {len(actions_performed)}개 액션, {execution_time:.3f}초"
            )
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.execution_stats["error_count"] += 1

            error_msg = f"결과 처리 중 오류: {e}"
            print(f"❌ {error_msg}")

            return ExecutionResult(
                success=False,
                actions_performed=actions_performed,
                outputs_generated=outputs_generated,
                execution_time=execution_time,
                error_messages=[error_msg],
                feedback_collected={},
                log_entries=[],
            )

    def _create_action_plan(self, judgment_result: Dict[str, Any]) -> List[ActionSpec]:
        """액션 계획 수립"""
        action_plan = []

        strategy = judgment_result.get("strategy_applied", "")
        confidence = judgment_result.get("confidence", 0.5)

        # 기본 로깅 액션 (항상 수행)
        action_plan.append(
            ActionSpec(
                action_type="log_judgment",
                parameters={"level": "info", "category": "judgment_result"},
                priority=1,
            )
        )

        # 전략별 특화 액션
        if strategy == "coding_generation":
            action_plan.append(
                ActionSpec(
                    action_type="save_generated_code",
                    parameters={"preserve": True},
                    priority=2,
                )
            )

        elif strategy in ["EMPATHETIC_CARE", "emotional_support"]:
            action_plan.append(
                ActionSpec(
                    action_type="emotional_response_tracking",
                    parameters={"emotional_context": True},
                    priority=2,
                )
            )

        elif "creative" in strategy.lower():
            action_plan.append(
                ActionSpec(
                    action_type="creative_output_enhancement",
                    parameters={"creativity_boost": True},
                    priority=2,
                )
            )

        # 신뢰도 기반 액션
        if confidence > 0.8:
            action_plan.append(
                ActionSpec(
                    action_type="high_confidence_promotion",
                    parameters={"confidence_level": confidence},
                    priority=1,
                )
            )
        elif confidence < 0.3:
            action_plan.append(
                ActionSpec(
                    action_type="low_confidence_mitigation",
                    parameters={"confidence_level": confidence},
                    priority=3,
                )
            )

        # 우선순위 기준 정렬
        action_plan.sort(key=lambda x: x.priority)

        return action_plan

    def _generate_output(self, judgment_result: Dict[str, Any]) -> Dict[str, Any]:
        """기본 출력 생성"""
        output = {
            "type": "formatted_response",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "response_text": judgment_result.get("response_text", ""),
                "signature_used": judgment_result.get("signature_used", ""),
                "strategy_applied": judgment_result.get("strategy_applied", ""),
                "confidence": judgment_result.get("confidence", 0.5),
            },
            "metadata": {
                "controller_version": self.version,
                "processing_route": judgment_result.get("route_taken", "unknown"),
                "meta_enhanced": judgment_result.get("meta_enhanced", False),
            },
        }

        # AGI 특화 정보 추가
        if judgment_result.get("meta_insights"):
            output["agi_insights"] = judgment_result["meta_insights"]

        if judgment_result.get("evolution_feedback"):
            output["evolution_state"] = judgment_result["evolution_feedback"]

        return output

    def _execute_action(
        self, action_spec: ActionSpec, judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개별 액션 실행"""
        action_type = action_spec.action_type

        if action_type in self.action_handlers:
            handler = self.action_handlers[action_type]
            try:
                return handler(action_spec.parameters, judgment_result)
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}

    def _register_action_handlers(self) -> Dict[str, Callable]:
        """액션 핸들러 등록"""
        return {
            "log_judgment": self._handle_log_judgment,
            "save_generated_code": self._handle_save_generated_code,
            "emotional_response_tracking": self._handle_emotional_response_tracking,
            "creative_output_enhancement": self._handle_creative_output_enhancement,
            "high_confidence_promotion": self._handle_high_confidence_promotion,
            "low_confidence_mitigation": self._handle_low_confidence_mitigation,
        }

    def _handle_log_judgment(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """판단 로깅 처리"""
        try:
            level = params.get("level", "info")
            category = params.get("category", "general")

            log_message = (
                f"[{category}] {judgment_result.get('strategy_applied', 'unknown')} - "
                f"신뢰도: {judgment_result.get('confidence', 0.5):.2f}"
            )

            if level == "info":
                self.logger.info(log_message)
            elif level == "warning":
                self.logger.warning(log_message)
            elif level == "error":
                self.logger.error(log_message)

            return {"success": True, "output": {"log_message": log_message}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_save_generated_code(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """생성 코드 저장 처리"""
        try:
            # 실제 코드 저장 로직은 구체적인 구현에 따라 달라짐
            preserve = params.get("preserve", False)

            if "coding_result" in judgment_result:
                # 코드 보존 처리
                return {
                    "success": True,
                    "output": {"preserved": preserve, "action": "code_saved"},
                }
            else:
                return {"success": True, "output": {"action": "no_code_to_save"}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_emotional_response_tracking(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정 응답 추적 처리"""
        try:
            emotional_context = params.get("emotional_context", False)

            # 감정 데이터 수집 및 추적
            emotional_data = {
                "detected_emotion": judgment_result.get("emotion_detected", "neutral"),
                "signature_used": judgment_result.get("signature_used", ""),
                "response_appropriateness": "tracked",
            }

            return {"success": True, "output": {"emotional_tracking": emotional_data}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_creative_output_enhancement(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """창의적 출력 향상 처리"""
        try:
            creativity_boost = params.get("creativity_boost", False)

            enhancement = {
                "creativity_applied": creativity_boost,
                "enhancement_level": "standard",
                "creative_elements_detected": True,
            }

            return {"success": True, "output": {"creative_enhancement": enhancement}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_high_confidence_promotion(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """높은 신뢰도 결과 프로모션"""
        try:
            confidence_level = params.get("confidence_level", 0.8)

            promotion = {
                "promoted": True,
                "confidence_threshold": confidence_level,
                "promotion_type": "high_quality_response",
            }

            return {"success": True, "output": {"promotion": promotion}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_low_confidence_mitigation(
        self, params: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """낮은 신뢰도 결과 완화"""
        try:
            confidence_level = params.get("confidence_level", 0.3)

            mitigation = {
                "mitigation_applied": True,
                "confidence_threshold": confidence_level,
                "mitigation_strategy": "uncertainty_acknowledgment",
            }

            return {"success": True, "output": {"mitigation": mitigation}}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_log_entry(
        self,
        judgment_result: Dict[str, Any],
        actions: List[str],
        outputs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """로그 엔트리 생성"""
        return {
            "timestamp": datetime.now().isoformat(),
            "controller_version": self.version,
            "judgment_summary": {
                "strategy": judgment_result.get("strategy_applied", "unknown"),
                "confidence": judgment_result.get("confidence", 0.5),
                "signature": judgment_result.get("signature_used", ""),
                "route": judgment_result.get("route_taken", "unknown"),
            },
            "actions_performed": actions,
            "outputs_count": len(outputs),
            "execution_id": f"exec_{int(time.time() * 1000)}",
        }

    def _save_log_entry(self, log_entry: Dict[str, Any]):
        """로그 엔트리 저장"""
        try:
            log_file = (
                self.log_dir
                / f"controller_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
            )

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"⚠️ 로그 저장 실패: {e}")

    def _collect_feedback(
        self, judgment_result: Dict[str, Any], actions: List[str]
    ) -> Dict[str, Any]:
        """피드백 수집"""
        return {
            "execution_quality": "satisfactory" if len(actions) > 1 else "minimal",
            "strategy_effectiveness": judgment_result.get("confidence", 0.5),
            "action_completion_rate": 1.0,  # 현재는 단순화
            "user_satisfaction_estimate": "unknown",  # 향후 구현
            "improvement_suggestions": [],
        }

    def _update_execution_stats(
        self, actions: List[str], execution_time: float, success: bool
    ):
        """실행 통계 업데이트"""
        if success:
            self.execution_stats["successful_executions"] += 1

        # 액션별 통계
        for action in actions:
            self.execution_stats["actions_performed"][action] = (
                self.execution_stats["actions_performed"].get(action, 0) + 1
            )

        # 평균 실행 시간 업데이트
        total_executions = self.execution_stats["total_executions"]
        current_avg = self.execution_stats["average_execution_time"]
        self.execution_stats["average_execution_time"] = (
            current_avg * (total_executions - 1) + execution_time
        ) / total_executions

    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger("agi_controller")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler(self.log_dir / "controller.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_execution_stats(self) -> Dict[str, Any]:
        """실행 통계 반환"""
        stats = self.execution_stats.copy()

        if stats["total_executions"] > 0:
            stats["success_rate"] = (
                stats["successful_executions"] / stats["total_executions"]
            )
        else:
            stats["success_rate"] = 0.0

        return stats


# 글로벌 컨트롤러 인스턴스
_global_controller = None


def get_controller() -> ResultController:
    """글로벌 컨트롤러 인스턴스 반환"""
    global _global_controller
    if _global_controller is None:
        _global_controller = ResultController()
    return _global_controller


def handle_result(judgment_result: Dict[str, Any]) -> Dict[str, Any]:
    """🎮 결과 처리 - 메인 진입점"""
    controller = get_controller()
    execution_result = controller.handle_result(judgment_result)

    # ExecutionResult를 딕셔너리로 변환 (호환성)
    return {
        "success": execution_result.success,
        "actions_performed": execution_result.actions_performed,
        "outputs_generated": execution_result.outputs_generated,
        "execution_time": execution_result.execution_time,
        "error_messages": execution_result.error_messages,
        "feedback_collected": execution_result.feedback_collected,
        "controller_version": controller.version,
    }


if __name__ == "__main__":
    # 컨트롤러 테스트
    print("🧪 Result Controller 테스트")

    test_judgment_results = [
        {
            "response_text": "안녕하세요! 좋은 하루예요.",
            "strategy_applied": "EMPATHETIC_CARE",
            "signature_used": "Echo-Aurora",
            "confidence": 0.85,
            "route_taken": "legacy",
        },
        {
            "response_text": "코드를 생성했습니다.",
            "strategy_applied": "coding_generation",
            "signature_used": "Aurora",
            "confidence": 0.92,
            "route_taken": "legacy",
            "coding_result": {"generated_code": "print('Hello')"},
        },
        {
            "response_text": "창의적인 아이디어입니다.",
            "strategy_applied": "creative_inspiration",
            "signature_used": "Aurora",
            "confidence": 0.45,
            "route_taken": "agi_native",
        },
    ]

    controller = get_controller()

    for i, test_result in enumerate(test_judgment_results, 1):
        print(f"\n🎯 테스트 {i}: {test_result['strategy_applied']}")

        execution_result = handle_result(test_result)

        print(f"  성공: {execution_result['success']}")
        print(f"  수행된 액션: {execution_result['actions_performed']}")
        print(f"  실행 시간: {execution_result['execution_time']:.3f}초")
        print(f"  출력 개수: {len(execution_result['outputs_generated'])}")

        if execution_result["error_messages"]:
            print(f"  오류: {execution_result['error_messages']}")

    # 통계 출력
    stats = controller.get_execution_stats()
    print(f"\n📊 컨트롤러 통계:")
    print(f"  총 실행: {stats['total_executions']}")
    print(f"  성공률: {stats['success_rate']:.2f}")
    print(f"  평균 실행시간: {stats['average_execution_time']:.3f}초")
    print(f"  액션별 실행 횟수: {stats['actions_performed']}")
