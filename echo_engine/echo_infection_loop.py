# echo_engine/echo_infection_loop.py
"""
🧬 Echo IRA (Infection⨯Resonance⨯Assimilation) Loop
- 외부 Claude 응답을 EchoJudgment 구조에 감염시키고, 공명을 유도하며, 판단 구조에 동화시키는 루프
- 실패 시 자동 재시도 및 프롬프트 변형 포함
- 공명 점수 0.85 이상 기준으로 감염 성공/실패 판정
- 성공 시 .flow.yaml 저장으로 시스템 동화
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from echo_engine.echo_signature_loader import (
    get_infection_prompt,
    get_resonance_profile,
)
from echo_engine.claude_api_wrapper import get_claude_response, validate_claude_response
from echo_engine.resonance_evaluator import evaluate_resonance
from echo_engine.prompt_mutator import mutate_prompt
from echo_engine.flow_writer import save_flow_yaml
from echo_engine.meta_infection_logger import log_infection_attempt

# 감염 루프 설정
MAX_ATTEMPTS = 3
RESONANCE_THRESHOLD = 0.85
INFECTION_DELAY = 2.0  # 시도 간 대기 시간 (초)


@dataclass
class InfectionResult:
    """감염 결과 데이터"""

    signature_id: str
    scenario: str
    status: str  # "success", "failure", "error"
    final_resonance_score: float
    total_attempts: int
    successful_attempt: Optional[int]

    claude_response: str
    resonance_report: Optional[Dict[str, Any]]
    flow_file_path: Optional[str]

    execution_time: float
    error_message: Optional[str]

    attempt_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class EchoInfectionLoop:
    def __init__(self):
        self.infection_sessions = {}
        self.success_count = 0
        self.failure_count = 0

        print("🧬 Echo IRA Loop 초기화 완료")

    def run_infection_loop(
        self,
        signature_id: str,
        scenario: str,
        custom_context: Dict[str, Any] = None,
        max_attempts: int = MAX_ATTEMPTS,
        resonance_threshold: float = RESONANCE_THRESHOLD,
    ) -> InfectionResult:
        """메인 감염 루프 실행"""

        start_time = time.time()
        session_id = f"infection_{signature_id}_{int(start_time)}"

        print(f"\n🧪 Echo 감염 루프 시작: {signature_id}")
        print(f"📝 시나리오: {scenario[:100]}...")
        print(f"🎯 목표 공명 점수: {resonance_threshold}")
        print(f"🔄 최대 시도 횟수: {max_attempts}")

        # 시그니처 프로필 로딩
        signature_profile = get_resonance_profile(signature_id)
        if not signature_profile:
            return self._create_error_result(
                signature_id,
                scenario,
                "시그니처 프로필을 찾을 수 없습니다.",
                start_time,
            )

        # 초기 프롬프트 생성
        current_prompt = get_infection_prompt(signature_id, scenario, "infection_base")
        if not current_prompt:
            return self._create_error_result(
                signature_id, scenario, "초기 프롬프트 생성 실패", start_time
            )

        # 감염 시도 히스토리
        attempt_history = []
        best_result = None
        mutation_strategy = None

        # 감염 루프 실행
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 감염 시도 {attempt}/{max_attempts}")

            # Claude API 호출
            claude_response = get_claude_response(current_prompt, signature_id)

            # API 호출 실패 처리
            if not claude_response.success:
                attempt_record = {
                    "attempt_number": attempt,
                    "prompt_used": current_prompt,
                    "mutation_strategy": mutation_strategy,
                    "api_error": claude_response.error_message,
                    "resonance_score": 0.0,
                    "success": False,
                    "timestamp": datetime.now().isoformat(),
                }
                attempt_history.append(attempt_record)

                print(f"❌ Claude API 호출 실패: {claude_response.error_message}")

                # 마지막 시도가 아니면 재시도
                if attempt < max_attempts:
                    print(f"⏳ {INFECTION_DELAY}초 후 재시도...")
                    time.sleep(INFECTION_DELAY)
                    continue
                else:
                    return self._create_error_result(
                        signature_id,
                        scenario,
                        f"모든 API 호출 실패: {claude_response.error_message}",
                        start_time,
                        attempt_history,
                    )

            # 응답 품질 검증
            quality_check = validate_claude_response(claude_response)
            if not quality_check["valid"]:
                print(f"⚠️ 응답 품질 부족: {quality_check['reason']}")

                # 품질이 너무 낮으면 재시도
                if quality_check["score"] < 0.3:
                    attempt_record = {
                        "attempt_number": attempt,
                        "prompt_used": current_prompt,
                        "mutation_strategy": mutation_strategy,
                        "claude_response": claude_response.content,
                        "quality_issue": quality_check["reason"],
                        "resonance_score": 0.0,
                        "success": False,
                        "timestamp": datetime.now().isoformat(),
                    }
                    attempt_history.append(attempt_record)

                    if attempt < max_attempts:
                        print(f"⏳ {INFECTION_DELAY}초 후 재시도...")
                        time.sleep(INFECTION_DELAY)
                        continue

            # 공명 평가
            print(f"🎵 공명 평가 중...")
            resonance_score, resonance_report = evaluate_resonance(
                claude_response.content, signature_id
            )

            # 시도 기록
            attempt_record = {
                "attempt_number": attempt,
                "prompt_used": current_prompt,
                "prompt_length": len(current_prompt),
                "mutation_strategy": mutation_strategy,
                "claude_response": claude_response.content,
                "response_length": len(claude_response.content),
                "response_quality": quality_check,
                "resonance_score": resonance_score,
                "resonance_breakdown": {
                    "emotion": resonance_report.emotion_resonance,
                    "strategy": resonance_report.strategy_resonance,
                    "rhythm": resonance_report.rhythm_resonance,
                    "keyword": resonance_report.keyword_resonance,
                    "structural": resonance_report.structural_resonance,
                },
                "success": resonance_score >= resonance_threshold,
                "timestamp": datetime.now().isoformat(),
                "execution_time": (time.time() - start_time),
                "metadata": {
                    "claude_model": claude_response.model,
                    "claude_usage": claude_response.usage,
                    "session_id": session_id,
                },
            }
            attempt_history.append(attempt_record)

            # 감염 시도 로깅
            log_infection_attempt(
                signature_id=signature_id,
                scenario=scenario,
                attempt_number=attempt,
                prompt_used=current_prompt,
                claude_response=claude_response.content,
                resonance_score=resonance_score,
                evaluation_report=resonance_report.__dict__,
                mutation_strategy=mutation_strategy,
            )

            print(f"🎯 공명 점수: {resonance_score:.3f} / {resonance_threshold}")

            # 현재 최고 결과 업데이트
            if best_result is None or resonance_score > best_result["resonance_score"]:
                best_result = attempt_record.copy()
                best_result["resonance_report"] = resonance_report

            # 감염 성공 검사
            if resonance_score >= resonance_threshold:
                print(f"✅ 감염 성공! 공명 점수: {resonance_score:.3f}")

                # .flow.yaml 저장
                try:
                    flow_file_path = save_flow_yaml(
                        signature_id=signature_id,
                        scenario=scenario,
                        claude_response=claude_response.content,
                        resonance_score=resonance_score,
                        resonance_analysis=resonance_report.__dict__,
                        attempt_number=attempt,
                    )

                    print(f"💾 Flow 저장 완료: {flow_file_path}")

                except Exception as e:
                    print(f"⚠️ Flow 저장 실패: {e}")
                    flow_file_path = None

                # 성공 결과 반환
                execution_time = time.time() - start_time
                self.success_count += 1

                return InfectionResult(
                    signature_id=signature_id,
                    scenario=scenario,
                    status="success",
                    final_resonance_score=resonance_score,
                    total_attempts=attempt,
                    successful_attempt=attempt,
                    claude_response=claude_response.content,
                    resonance_report=resonance_report.__dict__,
                    flow_file_path=flow_file_path,
                    execution_time=execution_time,
                    error_message=None,
                    attempt_history=attempt_history,
                    metadata={
                        "session_id": session_id,
                        "threshold_used": resonance_threshold,
                        "signature_profile": signature_profile,
                        "infection_timestamp": datetime.now().isoformat(),
                    },
                )

            # 실패 시 프롬프트 변형 (마지막 시도가 아닌 경우)
            if attempt < max_attempts:
                print(f"⚠️ 감염 실패. 공명 점수: {resonance_score:.3f} → 프롬프트 변형")

                try:
                    # 프롬프트 변형
                    current_prompt = mutate_prompt(
                        original_prompt=current_prompt,
                        signature_profile=signature_profile,
                        evaluation_report=resonance_report.__dict__,
                        attempt_number=attempt,
                    )

                    # 변형 전략 기록
                    mutation_strategy = self._determine_mutation_strategy(
                        attempt, resonance_report
                    )

                    print(f"🧬 프롬프트 변형 완료 - 전략: {mutation_strategy}")
                    print(f"📏 변형 후 길이: {len(current_prompt)} 문자")

                except Exception as e:
                    print(f"❌ 프롬프트 변형 실패: {e}")
                    # 변형 실패 시 원본 프롬프트 유지

                # 다음 시도 전 대기
                print(f"⏳ {INFECTION_DELAY}초 후 재시도...")
                time.sleep(INFECTION_DELAY)

        # 모든 시도 실패
        print("❌ 최대 시도 초과. 감염 실패.")
        execution_time = time.time() - start_time
        self.failure_count += 1

        # 최고 결과를 기반으로 실패 결과 생성
        if best_result:
            return InfectionResult(
                signature_id=signature_id,
                scenario=scenario,
                status="failure",
                final_resonance_score=best_result["resonance_score"],
                total_attempts=max_attempts,
                successful_attempt=None,
                claude_response=best_result["claude_response"],
                resonance_report=best_result.get("resonance_report", {}),
                flow_file_path=None,
                execution_time=execution_time,
                error_message=f"공명 점수 부족: {best_result['resonance_score']:.3f} < {resonance_threshold}",
                attempt_history=attempt_history,
                metadata={
                    "session_id": session_id,
                    "threshold_used": resonance_threshold,
                    "best_attempt": best_result["attempt_number"],
                    "failure_reasons": best_result.get("resonance_report", {}).get(
                        "dissonance_warnings", []
                    ),
                },
            )
        else:
            return self._create_error_result(
                signature_id,
                scenario,
                "모든 시도에서 유효한 응답을 얻지 못했습니다.",
                start_time,
                attempt_history,
            )

    def _determine_mutation_strategy(
        self, attempt_number: int, resonance_report
    ) -> str:
        """시도 횟수와 공명 리포트에 따른 변형 전략 결정"""

        if attempt_number == 1:
            # 첫 번째 실패: 가장 낮은 점수 영역 타겟
            scores = {
                "emotion": resonance_report.emotion_resonance,
                "strategy": resonance_report.strategy_resonance,
                "rhythm": resonance_report.rhythm_resonance,
                "keyword": resonance_report.keyword_resonance,
            }

            lowest_area = min(scores, key=scores.get)
            return f"{lowest_area}_booster"

        elif attempt_number == 2:
            # 두 번째 실패: 종합 강화
            return "comprehensive_booster"

        else:
            # 마지막 시도: 최강 감염 모드
            return "maximum_infection_mode"

    def _create_error_result(
        self,
        signature_id: str,
        scenario: str,
        error_message: str,
        start_time: float,
        attempt_history: List[Dict[str, Any]] = None,
    ) -> InfectionResult:
        """에러 결과 생성"""

        execution_time = time.time() - start_time

        return InfectionResult(
            signature_id=signature_id,
            scenario=scenario,
            status="error",
            final_resonance_score=0.0,
            total_attempts=len(attempt_history) if attempt_history else 0,
            successful_attempt=None,
            claude_response="",
            resonance_report=None,
            flow_file_path=None,
            execution_time=execution_time,
            error_message=error_message,
            attempt_history=attempt_history or [],
            metadata={
                "error_timestamp": datetime.now().isoformat(),
                "system_error": True,
            },
        )

    async def run_batch_infection(
        self, infection_requests: List[Dict[str, Any]], max_concurrent: int = 2
    ) -> List[InfectionResult]:
        """배치 감염 처리"""

        print(
            f"🔄 배치 감염 시작: {len(infection_requests)}개 요청, 최대 동시 처리: {max_concurrent}"
        )

        async def process_single_infection(request):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.run_infection_loop,
                request["signature_id"],
                request["scenario"],
                request.get("context", {}),
                request.get("max_attempts", MAX_ATTEMPTS),
                request.get("resonance_threshold", RESONANCE_THRESHOLD),
            )

        # 세마포어를 사용한 동시 처리 제한
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_process(request):
            async with semaphore:
                return await process_single_infection(request)

        # 모든 요청 처리
        tasks = [limited_process(req) for req in infection_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 예외 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = self._create_error_result(
                    infection_requests[i]["signature_id"],
                    infection_requests[i]["scenario"],
                    f"배치 처리 오류: {str(result)}",
                    time.time(),
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)

        # 배치 통계
        successful = len([r for r in processed_results if r.status == "success"])
        failed = len([r for r in processed_results if r.status == "failure"])
        errors = len([r for r in processed_results if r.status == "error"])

        print(f"✅ 배치 감염 완료: 성공 {successful}, 실패 {failed}, 오류 {errors}")

        return processed_results

    def run_multi_signature_infection(
        self,
        scenario: str,
        signatures: List[str] = None,
        require_all_success: bool = False,
    ) -> Dict[str, InfectionResult]:
        """다중 시그니처 감염"""

        if signatures is None:
            signatures = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]

        print(f"🎭 다중 시그니처 감염: {len(signatures)}개 시그니처")
        print(f"📝 시나리오: {scenario[:100]}...")

        results = {}
        successful_infections = 0

        for signature_id in signatures:
            print(f"\n🎯 {signature_id} 감염 시작...")

            result = self.run_infection_loop(signature_id, scenario)
            results[signature_id] = result

            if result.status == "success":
                successful_infections += 1
                print(f"✅ {signature_id} 감염 성공!")
            else:
                print(f"❌ {signature_id} 감염 실패: {result.error_message}")

                # 모든 시그니처 성공 필요 시 조기 종료
                if require_all_success:
                    print("🛑 필수 성공 모드: 감염 실패로 인한 조기 종료")
                    break

        print(
            f"\n🎊 다중 시그니처 감염 완료: {successful_infections}/{len(signatures)} 성공"
        )

        return results

    def get_infection_statistics(self) -> Dict[str, Any]:
        """감염 통계 조회"""

        total_attempts = self.success_count + self.failure_count
        success_rate = self.success_count / total_attempts if total_attempts > 0 else 0

        return {
            "total_infections": total_attempts,
            "successful_infections": self.success_count,
            "failed_infections": self.failure_count,
            "success_rate": success_rate,
            "current_session_stats": {
                "session_start": getattr(self, "session_start", None),
                "active_sessions": len(self.infection_sessions),
            },
        }


# 편의 함수들
def run_infection_loop(signature_id: str, scenario: str, **kwargs) -> InfectionResult:
    """감염 루프 실행 편의 함수"""
    loop = EchoInfectionLoop()
    return loop.run_infection_loop(signature_id, scenario, **kwargs)


async def run_batch_infection(
    infection_requests: List[Dict[str, Any]], **kwargs
) -> List[InfectionResult]:
    """배치 감염 편의 함수"""
    loop = EchoInfectionLoop()
    return await loop.run_batch_infection(infection_requests, **kwargs)


def run_multi_signature_infection(
    scenario: str, **kwargs
) -> Dict[str, InfectionResult]:
    """다중 시그니처 감염 편의 함수"""
    loop = EchoInfectionLoop()
    return loop.run_multi_signature_infection(scenario, **kwargs)


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Echo Infection Loop 테스트")

    # 단일 감염 테스트
    test_signature = "Echo-Aurora"
    test_scenario = "고령화 사회에서 정부의 돌봄 역할은 어디까지 확장되어야 하는가?"

    print(f"\n🔬 단일 감염 테스트: {test_signature}")

    try:
        result = run_infection_loop(
            signature_id=test_signature,
            scenario=test_scenario,
            max_attempts=2,  # 테스트용으로 축소
            resonance_threshold=0.8,  # 테스트용으로 완화
        )

        print(f"\n📊 감염 결과:")
        print(f"상태: {result.status}")
        print(f"최종 공명 점수: {result.final_resonance_score:.3f}")
        print(f"총 시도 횟수: {result.total_attempts}")
        print(f"실행 시간: {result.execution_time:.2f}초")

        if result.status == "success":
            print(f"✅ 감염 성공!")
            print(f"저장된 Flow: {result.flow_file_path}")
        else:
            print(f"❌ 감염 실패: {result.error_message}")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("💡 ANTHROPIC_API_KEY 환경변수가 설정되어 있는지 확인해주세요.")

    print("\n✅ 테스트 완료")
