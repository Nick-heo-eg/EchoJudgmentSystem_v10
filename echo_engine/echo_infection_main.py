# echo_engine/echo_infection_main.py
"""
🚀 Echo Infection System - Main Integration Module
- Claude API 감염 루프 시스템의 통합 실행기
- 모든 감염 모듈을 통합하여 완전한 Echo IRA 루프 제공
- CLI 및 프로그래밍 인터페이스 지원
- 실시간 감염 모니터링 및 결과 분석
"""

import os
import sys
import argparse
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# Echo Infection 모듈들 임포트
from echo_engine.echo_signature_loader import get_signature_loader, get_all_signatures
from echo_engine.claude_api_wrapper import get_claude_wrapper
from echo_engine.resonance_evaluator import ResonanceEvaluator
from echo_engine.echo_infection_loop import (
    EchoInfectionLoop,
    run_infection_loop,
    run_multi_signature_infection,
)
from echo_engine.flow_writer import FlowWriter
from echo_engine.meta_infection_logger import MetaInfectionLogger


class EchoInfectionSystem:
    """Echo 감염 시스템 통합 클래스"""

    def __init__(self):
        self.signature_loader = get_signature_loader()
        self.claude_wrapper = get_claude_wrapper()
        self.resonance_evaluator = ResonanceEvaluator()
        self.infection_loop = EchoInfectionLoop()
        self.flow_writer = FlowWriter()
        self.logger = MetaInfectionLogger()

        print("🧬 Echo Infection System 초기화 완료")
        print(
            f"🎭 로딩된 시그니처: {len(self.signature_loader.get_all_signatures())}개"
        )

    def run_single_infection(
        self,
        signature_id: str,
        scenario: str,
        max_attempts: int = 3,
        threshold: float = 0.85,
    ) -> Dict[str, Any]:
        """단일 시그니처 감염 실행"""

        print(f"\n🎯 단일 감염 실행: {signature_id}")
        print(f"📝 시나리오: {scenario}")

        result = run_infection_loop(
            signature_id=signature_id,
            scenario=scenario,
            max_attempts=max_attempts,
            resonance_threshold=threshold,
        )

        return self._format_result(result)

    def run_signature_comparison(
        self, scenario: str, signatures: List[str] = None, threshold: float = 0.85
    ) -> Dict[str, Any]:
        """시그니처 비교 감염"""

        if signatures is None:
            signatures = list(self.signature_loader.get_all_signatures().keys())

        print(f"\n🎭 시그니처 비교 감염: {len(signatures)}개")
        print(f"📝 시나리오: {scenario}")

        results = run_multi_signature_infection(
            scenario=scenario, signatures=signatures, require_all_success=False
        )

        # 결과 포맷팅 및 비교 분석
        comparison_data = {
            "scenario": scenario,
            "signatures_tested": len(signatures),
            "total_attempts": sum(r.total_attempts for r in results.values()),
            "successful_infections": len(
                [r for r in results.values() if r.status == "success"]
            ),
            "results": {},
            "analysis": self._analyze_signature_comparison(results),
            "ranking": self._rank_signatures(results),
        }

        for sig_id, result in results.items():
            comparison_data["results"][sig_id] = self._format_result(result)

        return comparison_data

    async def run_batch_scenarios(
        self,
        scenarios: List[str],
        signature_id: str = "Echo-Aurora",
        max_concurrent: int = 2,
    ) -> Dict[str, Any]:
        """배치 시나리오 감염"""

        print(f"\n📦 배치 시나리오 감염: {len(scenarios)}개 시나리오")
        print(f"🎭 시그니처: {signature_id}")

        # 요청 구성
        infection_requests = [
            {
                "signature_id": signature_id,
                "scenario": scenario,
                "max_attempts": 3,
                "resonance_threshold": 0.85,
            }
            for scenario in scenarios
        ]

        # 배치 실행
        results = await self.infection_loop.run_batch_infection(
            infection_requests, max_concurrent=max_concurrent
        )

        # 배치 결과 분석
        batch_data = {
            "signature_id": signature_id,
            "total_scenarios": len(scenarios),
            "successful_infections": len([r for r in results if r.status == "success"]),
            "total_attempts": sum(r.total_attempts for r in results),
            "average_resonance": sum(r.final_resonance_score for r in results)
            / len(results),
            "results": [self._format_result(r) for r in results],
            "performance_analysis": self._analyze_batch_performance(results),
        }

        return batch_data

    def run_interactive_session(self):
        """대화형 감염 세션"""

        print("\n🎮 Echo 감염 대화형 세션 시작")
        print("='=" * 30)

        # 사용 가능한 시그니처 표시
        signatures = self.signature_loader.get_all_signatures()
        print("\n🎭 사용 가능한 시그니처:")
        for i, (sig_id, name) in enumerate(signatures.items(), 1):
            print(f"  {i}. {sig_id}: {name}")

        while True:
            try:
                print("\n" + "=" * 50)

                # 시그니처 선택
                sig_choice = input(
                    "\n시그니처 번호를 선택하세요 (1-4, q=종료): "
                ).strip()

                if sig_choice.lower() == "q":
                    break

                try:
                    sig_index = int(sig_choice) - 1
                    signature_id = list(signatures.keys())[sig_index]
                except (ValueError, IndexError):
                    print("❌ 잘못된 선택입니다.")
                    continue

                # 시나리오 입력
                print(f"\n🎯 선택된 시그니처: {signature_id}")
                scenario = input("시나리오를 입력하세요: ").strip()

                if not scenario:
                    print("❌ 시나리오를 입력해주세요.")
                    continue

                # 옵션 설정
                try:
                    max_attempts = int(input("최대 시도 횟수 (기본 3): ") or "3")
                    threshold = float(input("공명 임계값 (기본 0.85): ") or "0.85")
                except ValueError:
                    max_attempts = 3
                    threshold = 0.85

                # 감염 실행
                print(f"\n🧬 감염 시작...")
                result_data = self.run_single_infection(
                    signature_id, scenario, max_attempts, threshold
                )

                # 결과 출력
                self._print_infection_result(result_data)

            except KeyboardInterrupt:
                print("\n\n🛑 세션 중단됨")
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")

        print("\n👋 Echo 감염 세션 종료")

    def _format_result(self, result) -> Dict[str, Any]:
        """결과 포맷팅"""

        return {
            "signature_id": result.signature_id,
            "scenario": (
                result.scenario[:100] + "..."
                if len(result.scenario) > 100
                else result.scenario
            ),
            "status": result.status,
            "final_resonance_score": result.final_resonance_score,
            "total_attempts": result.total_attempts,
            "successful_attempt": result.successful_attempt,
            "execution_time": result.execution_time,
            "error_message": result.error_message,
            "flow_file_path": result.flow_file_path,
            "resonance_breakdown": (
                result.resonance_report.get("detailed_analysis", {})
                if result.resonance_report
                else {}
            ),
            "success": result.status == "success",
        }

    def _analyze_signature_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """시그니처 비교 분석"""

        analysis = {
            "best_performer": None,
            "worst_performer": None,
            "average_resonance": 0.0,
            "success_rate": 0.0,
            "total_attempts": 0,
            "insights": [],
        }

        if not results:
            return analysis

        # 성공률 계산
        successful = [r for r in results.values() if r.status == "success"]
        analysis["success_rate"] = len(successful) / len(results)

        # 평균 공명 점수
        resonance_scores = [r.final_resonance_score for r in results.values()]
        analysis["average_resonance"] = sum(resonance_scores) / len(resonance_scores)

        # 총 시도 횟수
        analysis["total_attempts"] = sum(r.total_attempts for r in results.values())

        # 최고/최악 성능자
        if resonance_scores:
            best_signature = max(
                results.keys(), key=lambda k: results[k].final_resonance_score
            )
            worst_signature = min(
                results.keys(), key=lambda k: results[k].final_resonance_score
            )

            analysis["best_performer"] = {
                "signature_id": best_signature,
                "resonance_score": results[best_signature].final_resonance_score,
                "attempts": results[best_signature].total_attempts,
            }

            analysis["worst_performer"] = {
                "signature_id": worst_signature,
                "resonance_score": results[worst_signature].final_resonance_score,
                "attempts": results[worst_signature].total_attempts,
            }

        # 인사이트 생성
        if analysis["success_rate"] == 1.0:
            analysis["insights"].append("모든 시그니처가 성공적으로 감염됨")
        elif analysis["success_rate"] >= 0.75:
            analysis["insights"].append("대부분의 시그니처가 감염에 성공")
        elif analysis["success_rate"] >= 0.5:
            analysis["insights"].append("절반 정도의 시그니처가 감염 성공")
        else:
            analysis["insights"].append(
                "감염 성공률이 낮음 - 시나리오 또는 임계값 조정 필요"
            )

        if analysis["average_resonance"] >= 0.9:
            analysis["insights"].append("전체적으로 매우 높은 공명도 달성")
        elif analysis["average_resonance"] >= 0.8:
            analysis["insights"].append("양호한 수준의 공명도 달성")

        return analysis

    def _rank_signatures(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """시그니처 순위"""

        rankings = []

        for sig_id, result in results.items():
            score = result.final_resonance_score

            # 성공 보너스
            if result.status == "success":
                score += 0.1

            # 시도 횟수 패널티 (적은 시도로 성공할수록 높은 점수)
            efficiency_bonus = (4 - result.total_attempts) * 0.02
            score += efficiency_bonus

            rankings.append(
                {
                    "rank": 0,  # 나중에 설정
                    "signature_id": sig_id,
                    "score": score,
                    "resonance_score": result.final_resonance_score,
                    "status": result.status,
                    "attempts": result.total_attempts,
                    "efficiency": efficiency_bonus,
                }
            )

        # 순위 정렬
        rankings.sort(key=lambda x: x["score"], reverse=True)

        # 순위 번호 설정
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1

        return rankings

    def _analyze_batch_performance(self, results: List[Any]) -> Dict[str, Any]:
        """배치 성능 분석"""

        if not results:
            return {}

        successful = [r for r in results if r.status == "success"]
        failed = [r for r in results if r.status == "failure"]
        errors = [r for r in results if r.status == "error"]

        analysis = {
            "success_rate": len(successful) / len(results),
            "failure_rate": len(failed) / len(results),
            "error_rate": len(errors) / len(results),
            "average_attempts": sum(r.total_attempts for r in results) / len(results),
            "average_execution_time": sum(r.execution_time for r in results)
            / len(results),
            "resonance_distribution": {
                "high": len([r for r in results if r.final_resonance_score >= 0.9]),
                "medium": len(
                    [r for r in results if 0.7 <= r.final_resonance_score < 0.9]
                ),
                "low": len([r for r in results if r.final_resonance_score < 0.7]),
            },
        }

        return analysis

    def _print_infection_result(self, result_data: Dict[str, Any]):
        """감염 결과 출력"""

        print(f"\n📊 감염 결과:")
        print(f"{'='*50}")
        print(f"🎭 시그니처: {result_data['signature_id']}")
        print(f"📝 시나리오: {result_data['scenario']}")
        print(f"🎯 상태: {result_data['status']}")
        print(f"🎵 최종 공명 점수: {result_data['final_resonance_score']:.3f}")
        print(f"🔄 총 시도 횟수: {result_data['total_attempts']}")
        print(f"⏱️ 실행 시간: {result_data['execution_time']:.2f}초")

        if result_data["success"]:
            print(f"✅ 감염 성공!")
            if result_data["flow_file_path"]:
                print(f"💾 Flow 저장: {result_data['flow_file_path']}")
        else:
            print(f"❌ 감염 실패: {result_data['error_message']}")

        # 공명 분석 상세
        if "resonance_breakdown" in result_data and result_data["resonance_breakdown"]:
            print(f"\n🎵 공명 분석:")
            breakdown = result_data["resonance_breakdown"]
            if "emotion_analysis" in breakdown:
                print(f"  감정: {breakdown['emotion_analysis'].get('score', 0):.3f}")
            if "strategy_analysis" in breakdown:
                print(f"  전략: {breakdown['strategy_analysis'].get('score', 0):.3f}")
            if "rhythm_analysis" in breakdown:
                print(f"  리듬: {breakdown['rhythm_analysis'].get('score', 0):.3f}")

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""

        return {
            "signatures_loaded": len(self.signature_loader.get_all_signatures()),
            "claude_api_status": "available" if self.claude_wrapper else "unavailable",
            "infection_statistics": self.infection_loop.get_infection_statistics(),
            "flow_statistics": self.flow_writer.get_infection_statistics(),
            "system_ready": True,
        }


def main():
    """CLI 메인 함수"""

    parser = argparse.ArgumentParser(description="Echo Infection System")
    parser.add_argument("--signature", "-s", help="시그니처 ID")
    parser.add_argument("--scenario", "-c", help="감염 시나리오")
    parser.add_argument(
        "--compare", "-m", action="store_true", help="모든 시그니처 비교"
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="대화형 모드")
    parser.add_argument("--attempts", "-a", type=int, default=3, help="최대 시도 횟수")
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.85, help="공명 임계값"
    )
    parser.add_argument("--status", action="store_true", help="시스템 상태 확인")

    args = parser.parse_args()

    # Echo Infection System 초기화
    try:
        system = EchoInfectionSystem()
    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {e}")
        print("💡 ANTHROPIC_API_KEY 환경변수가 설정되어 있는지 확인해주세요.")
        return 1

    # 시스템 상태 확인
    if args.status:
        status = system.get_system_status()
        print("🔍 Echo Infection System 상태:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return 0

    # 대화형 모드
    if args.interactive:
        system.run_interactive_session()
        return 0

    # 시나리오 필요
    if not args.scenario:
        print("❌ 시나리오가 필요합니다. --scenario 또는 -c 옵션을 사용하세요.")
        return 1

    # 시그니처 비교 모드
    if args.compare:
        print("🎭 모든 시그니처 비교 감염 실행...")
        result = system.run_signature_comparison(
            scenario=args.scenario, threshold=args.threshold
        )

        print(f"\n📊 비교 결과:")
        print(f"성공률: {result['analysis']['success_rate']:.1%}")
        print(f"평균 공명: {result['analysis']['average_resonance']:.3f}")

        print(f"\n🏆 순위:")
        for ranking in result["ranking"]:
            status_icon = "✅" if ranking["status"] == "success" else "❌"
            print(
                f"  {ranking['rank']}. {ranking['signature_id']}: {ranking['resonance_score']:.3f} {status_icon}"
            )

        return 0

    # 단일 시그니처 감염
    if not args.signature:
        print("❌ 시그니처가 필요합니다. --signature 또는 -s 옵션을 사용하세요.")
        return 1

    print(f"🧬 단일 감염 실행: {args.signature}")
    result = system.run_single_infection(
        signature_id=args.signature,
        scenario=args.scenario,
        max_attempts=args.attempts,
        threshold=args.threshold,
    )

    system._print_infection_result(result)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
