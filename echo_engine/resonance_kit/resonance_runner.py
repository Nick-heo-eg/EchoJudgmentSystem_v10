"""
Resonance Runner: Human-AI Resonance Kit 메인 실행기
- CLI 모드: 깊이 분석을 위한 수동 실행
- API 모드: 다른 시스템에서 호출 가능
- Echo 통합 모드: Echo 시스템과 완전 통합
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from .loaders import (
    Session,
    load_transcript,
    load_config,
    ensure_output_directories,
    save_execution_log,
)
from .metrics import MetricBook
from .rules import Router
from .report import write_report
from .agents.resonance_pattern_analyzer import ResonancePatternAnalyzer
from .agents.empathy_bridge_builder import EmpathyBridgeBuilder
from .agents.trust_evolution_tracker import TrustEvolutionTracker
from .agents.collaborative_flow_designer import CollaborativeFlowDesigner
from .agents.relationship_memory_keeper import RelationshipMemoryKeeper

# 에이전트 레지스트리
AGENTS = {
    "resonance_pattern_analyzer": ResonancePatternAnalyzer,
    "empathy_bridge_builder": EmpathyBridgeBuilder,
    "trust_evolution_tracker": TrustEvolutionTracker,
    "collaborative_flow_designer": CollaborativeFlowDesigner,
    "relationship_memory_keeper": RelationshipMemoryKeeper,
}


class ResonanceRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = Session(config["session"])
        self.metrics = MetricBook(config["metrics"])
        self.router = Router(config.get("routing", {}))

        # 출력 디렉토리 확인
        self.output_dirs = ensure_output_directories(config)

        # 실행 로그
        self.execution_logs = []

    def run_full_pipeline(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        print(f"🌌 Starting Resonance Analysis for session: {self.session.id}")

        # 세션 통계 업데이트
        self.session.update_stats(transcript)

        # 파이프라인 단계별 실행
        for step_config in self.config["pipeline"]["steps"]:
            if not step_config.get("enabled", True):
                continue

            agent_name = step_config["agent"]
            self._run_agent_step(agent_name, step_config, transcript)

        # 최종 요약 및 추천 생성
        summary = self.metrics.summarize()
        recommendations = self.metrics.recommend_signatures(
            allowed=self.session.signatures_allowed,
            top_k=self.config["recommendation"]["signature_selection"]["top_k"],
            diversity_penalty=self.config["recommendation"]["signature_selection"][
                "diversity_penalty"
            ],
        )

        # 추천 근거 생성
        recommendation_rationale = self.metrics.get_detailed_recommendation_rationale(
            recommendations
        )

        # 실행 로그 저장
        log_path = self.output_dirs["log_dir"] / f"{self.session.id}.jsonl"
        save_execution_log(
            log_path, self.session, self.execution_logs, summary, recommendations
        )

        # 보고서 생성
        report_path = self.output_dirs["report_dir"] / f"{self.session.id}.md"
        write_report(
            report_path,
            self.session,
            summary,
            recommendations,
            self.execution_logs,
            recommendation_rationale,
        )

        return {
            "session_id": self.session.id,
            "summary": summary,
            "recommendations": recommendations,
            "recommendation_rationale": recommendation_rationale,
            "log_path": str(log_path),
            "report_path": str(report_path),
            "execution_logs": self.execution_logs,
        }

    def _run_agent_step(
        self,
        agent_name: str,
        step_config: Dict[str, Any],
        transcript: List[Dict[str, Any]],
    ):
        """개별 에이전트 단계 실행"""
        print(f"   🔄 Running {agent_name}...")

        if agent_name not in AGENTS:
            print(f"   ❌ Unknown agent: {agent_name}")
            return

        # 에이전트 인스턴스 생성 및 실행
        agent_class = AGENTS[agent_name]
        agent_config = step_config.get("config", {})

        agent = agent_class(agent_config, self.session, self.metrics)
        result = agent.run(transcript)

        # 실행 로그에 추가
        log_entry = {
            "step": agent_name,
            "timestamp": datetime.now().isoformat(),
            "config": agent_config,
            **result,
        }
        self.execution_logs.append(log_entry)

        # 라우팅 결정 확인
        current_metrics = self.metrics.get_current_values()
        routing_decision = self.router.decide(current_metrics)

        if routing_decision:
            print(f"   📍 Routing decision: {routing_decision['action']}")
            self._handle_routing_decision(routing_decision, transcript, agent_name)

    def _handle_routing_decision(
        self,
        decision: Dict[str, Any],
        transcript: List[Dict[str, Any]],
        current_agent: str,
    ):
        """라우팅 결정 처리"""
        action = decision["action"]
        params = decision.get("params", {})

        if action == "repeat_agent":
            target_agent = params.get("agent", current_agent)
            max_repeats = params.get("max_repeats", 2)

            print(f"   🔁 Repeating {target_agent} (max {max_repeats} times)")

            # 반복 실행 (개선이 있을 때까지 또는 최대 횟수까지)
            for repeat_num in range(max_repeats):
                if target_agent in AGENTS:
                    agent_class = AGENTS[target_agent]
                    agent = agent_class(params, self.session, self.metrics)
                    result = agent.run(transcript)

                    repeat_log = {
                        "step": f"{target_agent}#repeat_{repeat_num + 1}",
                        "timestamp": datetime.now().isoformat(),
                        "routing_trigger": decision["routing_context"],
                        **result,
                    }
                    self.execution_logs.append(repeat_log)

                    # 개선도 체크 (간단한 버전)
                    if result.get("metrics", {}).get("resonance", 0) > 0.6:
                        print(f"   ✅ Improvement detected, stopping repeats")
                        break

        elif action == "escalate_signature_rewrite":
            style = params.get("style", "supportive-adjust")
            intensity = params.get("intensity", "medium")

            escalation_log = {
                "step": "signature_style_escalation",
                "timestamp": datetime.now().isoformat(),
                "style": style,
                "intensity": intensity,
                "routing_context": decision["routing_context"],
                "recommendation": f"Switch response style to {style} with {intensity} intensity",
            }
            self.execution_logs.append(escalation_log)
            print(f"   📤 Escalating to {style} style ({intensity} intensity)")

        elif action == "suggest_signature_switch":
            preferred_category = params.get("preferred_category", "empathetic")
            reason = params.get("reason", "metrics below threshold")
            confidence = params.get("switch_confidence", 0.5)

            switch_log = {
                "step": "signature_switch_suggestion",
                "timestamp": datetime.now().isoformat(),
                "preferred_category": preferred_category,
                "reason": reason,
                "confidence": confidence,
                "routing_context": decision["routing_context"],
            }
            self.execution_logs.append(switch_log)
            print(
                f"   💡 Suggesting signature switch to {preferred_category} category ({reason})"
            )


def run_cli_mode():
    """CLI 모드 실행"""
    parser = argparse.ArgumentParser(description="Human-AI Resonance Kit v0.1")
    parser.add_argument(
        "--config", required=True, help="Configuration file path (YAML/JSON)"
    )
    parser.add_argument("--transcript", help="Override transcript path")
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument("--session-id", help="Custom session ID")
    parser.add_argument(
        "--quiet", action="store_true", help="Quiet mode (minimal output)"
    )
    parser.add_argument(
        "--json-output", action="store_true", help="Output results as JSON"
    )

    args = parser.parse_args()

    try:
        # 설정 로드
        config = load_config(args.config)

        # CLI 인자로 덮어쓰기
        if args.transcript:
            config["io"]["input"]["transcript_path"] = args.transcript
        if args.output_dir:
            config["io"]["output"]["log_dir"] = f"{args.output_dir}/logs"
            config["io"]["output"]["report_dir"] = f"{args.output_dir}/reports"
        if args.session_id:
            config["session"]["id"] = args.session_id

        # 대화 로드
        transcript = load_transcript(config["io"]["input"]["transcript_path"])

        if not args.quiet:
            print(f"📖 Loaded {len(transcript)} conversation turns")

        # 실행기 생성 및 실행
        runner = ResonanceRunner(config)
        result = runner.run_full_pipeline(transcript)

        # 결과 출력
        if args.json_output:
            print(
                json.dumps(
                    {
                        "summary": result["summary"],
                        "recommendations": result["recommendations"],
                        "log_path": result["log_path"],
                        "report_path": result["report_path"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            if not args.quiet:
                print(f"\n✅ Analysis Complete!")
                print(f"📊 Overall Score: {result['summary']['overall_score']}")
                print(f"🏷️  Quality Level: {result['summary']['quality_label']}")
                print(
                    f"💫 Recommended Signatures: {', '.join(result['recommendations'])}"
                )
                print(f"📄 Report: {result['report_path']}")

        return result

    except Exception as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


def run_manual_analysis(
    transcript_path: str,
    output_dir: str = "echo_engine/resonance_kit/reports",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """수동 분석 실행 (Echo 시스템에서 호출)"""

    # 기본 설정 생성
    config = {
        "version": "0.1",
        "session": {
            "id": session_id
            or f"manual_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": "echo_user",
            "locale": "ko-KR",
            "signatures_allowed": [
                "Selene",
                "Heo",
                "Aurora",
                "Lune",
                "Companion",
                "Phoenix",
                "Sage",
            ],
        },
        "pipeline": {
            "steps": [
                {
                    "agent": "resonance_pattern_analyzer",
                    "enabled": True,
                    "config": {"window_turns": 6},
                },
                {
                    "agent": "empathy_bridge_builder",
                    "enabled": True,
                    "config": {"mirroring_strength": 0.6},
                },
                {
                    "agent": "trust_evolution_tracker",
                    "enabled": True,
                    "config": {"decay": 0.02},
                },
                {
                    "agent": "collaborative_flow_designer",
                    "enabled": True,
                    "config": {"prompt_clarity_boost": 0.5},
                },
                {
                    "agent": "relationship_memory_keeper",
                    "enabled": True,
                    "config": {"memory_window": 30},
                },
            ]
        },
        "routing": {"rules": []},
        "metrics": {
            "weights": {
                "resonance": 0.4,
                "trust": 0.25,
                "flow": 0.2,
                "affect_valence": 0.1,
                "affect_arousal": 0.05,
            },
            "thresholds": {"good": 0.7, "warn": 0.5, "bad": 0.35},
        },
        "io": {
            "input": {"transcript_path": transcript_path},
            "output": {
                "log_dir": f"{output_dir}/logs",
                "report_dir": f"{output_dir}/reports",
            },
        },
        "recommendation": {
            "signature_selection": {"top_k": 3, "diversity_penalty": 0.15}
        },
    }

    # 대화 로드
    transcript = load_transcript(transcript_path)

    # 실행기 생성 및 실행
    runner = ResonanceRunner(config)
    result = runner.run_full_pipeline(transcript)

    return result


if __name__ == "__main__":
    run_cli_mode()
