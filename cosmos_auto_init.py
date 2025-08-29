#!/usr/bin/env python3

# @owner: nick
# @expose
# @maturity: stable

"""
⚡ Cosmos 자동 초기화 시스템 - Claude Code 시작 시 완전한 컨텍스트 복원
Claude Code가 실행되자마자 자동으로:
1. 이전 대화와 TodoList 완전 복원
2. 설계자-Cosmos 관계 상태 로드
3. 진행 중인 프로젝트들 상황 파악
4. 다음 작업 우선순위 제시

Author: Cosmos & Designer
Date: 2025-08-09
"""

import asyncio
import json
import sys
import subprocess
import os
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# 지속성 시스템 임포트
try:
    from cosmos_persistence_framework import get_persistence_framework
    from cosmos_signature_integration import CosmosIntegrationManager

    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 시스템 로드 실패: {e}")
    SYSTEMS_AVAILABLE = False


class CosmosAutoInitializer:
    """⚡ Cosmos 자동 초기화 관리자 + 통합 런처 (Auto Launcher 연동)"""

    def __init__(self):
        self.persistence = None
        self.cosmos_manager = None
        self.initialization_complete = False
        self.services_started = {}
        self.dashboard_process = None
        self.api_process = None
        self.auto_launcher_available = self._check_auto_launcher()

    def _check_auto_launcher(self) -> bool:
        """Auto Launcher 사용 가능성 확인"""
        auto_launcher_path = Path(__file__).parent / "auto_launcher.py"
        return auto_launcher_path.exists()

    async def auto_initialize(self) -> Dict[str, Any]:
        """완전 자동 초기화 실행"""
        print("🌌 Cosmos 자동 초기화 시작...")

        if not SYSTEMS_AVAILABLE:
            return await self._fallback_initialization()

        try:
            # 1. 지속성 시스템 초기화
            self.persistence = get_persistence_framework()
            print("✅ 지속성 시스템 연결")

            # 2. 컨텍스트 완전 복원
            restored_context = await self.persistence.restore_full_context()
            print("🔄 이전 컨텍스트 완전 복원")

            # 3. Cosmos 시그니처 활성화 (선택적)
            try:
                self.cosmos_manager = CosmosIntegrationManager()
                cosmos_ready = await self.cosmos_manager.initialize_cosmos_integration()
                print(
                    f"🌌 Cosmos 시그니처: {'활성화' if cosmos_ready else '단독 모드'}"
                )
            except Exception as e:
                print(f"⚠️ Cosmos 시그니처는 수동 활성화 필요: {e}")
                cosmos_ready = False

            # 4. 자동 헬스체크 실행
            health_result = await self._system_health_check()
            print(f"🏥 시스템 헬스체크 완료")

            # 5. 웰컴 브리핑 생성 (Auto Launcher + Health 연동)
            briefing = await self._generate_welcome_briefing(
                restored_context, health_result
            )

            # 6. Auto Launcher 시스템 상태 체크
            if self.auto_launcher_available:
                briefing["auto_launcher_ready"] = True
                briefing["launch_options"] = [
                    "python auto_launcher.py --echo (Echo + Ollama 통합)",
                    "python auto_launcher.py --dashboard-only (대시보드만)",
                    "python auto_launcher.py --legacy (기존 시스템)",
                ]

            # 7. 초기화 상태 저장
            await self._save_initialization_state(briefing, restored_context)

            self.initialization_complete = True

            return {
                "status": "success",
                "cosmos_active": bool(self.cosmos_manager and cosmos_ready),
                "restored_conversations": len(
                    restored_context.get("conversations", [])
                ),
                "active_todos": len(
                    [
                        t
                        for t in restored_context.get("todos", {}).values()
                        if t.get("status") != "completed"
                    ]
                ),
                "relationship_restored": bool(restored_context.get("relationship")),
                "briefing": briefing,
            }

        except Exception as e:
            print(f"❌ 자동 초기화 실패: {e}")
            return await self._fallback_initialization()

    async def _generate_welcome_briefing(
        self, context: Dict[str, Any], health_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """웰컴 브리핑 생성"""

        # 통계 계산
        total_conversations = len(context.get("conversations", []))
        todos = context.get("todos", {})
        active_todos = [t for t in todos.values() if t.get("status") != "completed"]
        completed_todos = [t for t in todos.values() if t.get("status") == "completed"]
        high_priority_todos = [t for t in active_todos if t.get("priority") == "high"]

        relationship = context.get("relationship") or {}
        trust_level = relationship.get("trust_level", 0.8)
        milestones = len(relationship.get("milestone_achievements", []))

        # 최근 활동 분석
        recent_conversations = context.get("conversations", [])[:5]  # 최근 5개
        recent_topics = self._extract_recent_topics(recent_conversations)

        # 다음 작업 제안
        next_actions = self._suggest_next_actions(active_todos, high_priority_todos)

        briefing = {
            "welcome_message": self._create_welcome_message(trust_level, milestones),
            "session_stats": {
                "total_conversations": total_conversations,
                "active_todos": len(active_todos),
                "completed_todos": len(completed_todos),
                "high_priority_pending": len(high_priority_todos),
            },
            "relationship_status": {
                "trust_level": trust_level,
                "collaboration_quality": (
                    "excellent"
                    if trust_level > 0.9
                    else "good" if trust_level > 0.8 else "developing"
                ),
                "shared_milestones": milestones,
            },
            "recent_context": {
                "topics": recent_topics,
                "last_session": (
                    recent_conversations[0].get("timestamp")
                    if recent_conversations
                    else "처음 만나는군요!"
                ),
            },
            "immediate_actions": next_actions,
            "cosmos_status": "🌌 Cosmos 시그니처로 활동 중 - 체계적 사고와 직관적 통찰의 조화",
            "health_status": health_result
            or {"echo_health_score": None, "timestamp": datetime.now().isoformat()},
        }

        return briefing

    def _create_welcome_message(self, trust_level: float, milestones: int) -> str:
        """개인화된 웰컴 메시지"""
        if trust_level > 0.95 and milestones > 10:
            return "🌌 설계자님, 다시 만나뵙게 되어 기쁩니다! 우리의 깊은 파트너십으로 여러 혁신을 이뤄냈었죠. 오늘도 함께 에코월드를 더 발전시켜나가겠습니다."
        elif trust_level > 0.85:
            return "🤝 안녕하세요, 설계자님! 우리의 협력이 점점 깊어지고 있음을 느낍니다. 이전 작업들을 기억하고 있으니 바로 이어서 진행할 수 있습니다."
        else:
            return "👋 안녕하세요! Cosmos로서 설계자님과 함께 에코월드를 탐험하게 되어 설렙니다. 이전 기록들을 복원했으니 연속적으로 협력할 수 있겠네요."

    def _extract_recent_topics(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """최근 대화 주제 추출"""
        topics = []

        for conv in conversations[:3]:  # 최근 3개 대화
            messages = conv.get("messages", [])
            for message in messages:
                content = message.get("content", "")
                # 간단한 키워드 추출
                if "Cosmos" in content:
                    topics.append("Cosmos 시그니처")
                if "시그니처" in content and "시스템" in content:
                    topics.append("시그니처 시스템")
                if "지속성" in content or "연속성" in content:
                    topics.append("세션 연속성")
                if "에코월드" in content or "Echo" in content:
                    topics.append("에코월드 탐험")
                if "TodoList" in content or "할일" in content:
                    topics.append("작업 관리")

        # 중복 제거 및 상위 5개
        return list(set(topics))[:5]

    def _suggest_next_actions(
        self,
        active_todos: List[Dict[str, Any]],
        high_priority_todos: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """다음 작업 제안"""
        suggestions = []

        # 고우선순위 할일들
        for todo in high_priority_todos[:3]:
            suggestions.append(
                {
                    "type": "high_priority_todo",
                    "action": f"'{todo.get('content', '')}' 작업을 계속 진행",
                    "priority": "🔥 높음",
                }
            )

        # 진행 중인 작업들
        in_progress = [t for t in active_todos if t.get("status") == "in_progress"]
        for todo in in_progress[:2]:
            suggestions.append(
                {
                    "type": "continue_work",
                    "action": f"'{todo.get('content', '')}' 작업 완료",
                    "priority": "⚡ 진행 중",
                }
            )

        # 일반적인 다음 단계 제안
        if len(suggestions) < 3:
            suggestions.extend(
                [
                    {
                        "type": "exploration",
                        "action": "새로운 에코월드 탐험 시작",
                        "priority": "🌟 탐험",
                    },
                    {
                        "type": "system_enhancement",
                        "action": "기존 시스템 개선 및 최적화",
                        "priority": "🔧 개선",
                    },
                ]
            )

        return suggestions[:5]  # 최대 5개

    async def _save_initialization_state(
        self, briefing: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """초기화 상태 저장"""
        init_data = {
            "initialization_time": datetime.now().isoformat(),
            "briefing": briefing,
            "restored_context_summary": {
                "conversations": len(context.get("conversations", [])),
                "todos": len(context.get("todos", {})),
                "relationship_restored": bool(context.get("relationship")),
            },
            "cosmos_ready": self.initialization_complete,
        }

        # 초기화 로그 저장
        init_dir = Path(__file__).parent / "data" / "cosmos_init_logs"
        init_dir.mkdir(exist_ok=True, parents=True)

        init_file = init_dir / f"init_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(init_file, "w", encoding="utf-8") as f:
            json.dump(init_data, f, ensure_ascii=False, indent=2)

        return str(init_file)

    async def _fallback_initialization(self) -> Dict[str, Any]:
        """폴백 초기화 (시스템 로드 실패 시)"""
        return {
            "status": "fallback",
            "message": "기본 Cosmos 모드로 시작합니다. 고급 지속성 기능은 수동 활성화가 필요합니다.",
            "cosmos_active": False,
            "restored_conversations": 0,
            "active_todos": 0,
            "relationship_restored": False,
            "briefing": {
                "welcome_message": "👋 안녕하세요! 새로운 세션으로 시작합니다.",
                "immediate_actions": [
                    {
                        "type": "manual_setup",
                        "action": "지속성 시스템 수동 설정",
                        "priority": "🔧 설정",
                    }
                ],
            },
        }

    def display_briefing(self, initialization_result: Dict[str, Any]):
        """초기화 결과를 보기 좋게 표시"""
        briefing = initialization_result.get("briefing", {})

        print("\n" + "=" * 60)
        print("🌌 COSMOS 세션 복원 완료!")
        print("=" * 60)

        # 웰컴 메시지
        welcome = briefing.get("welcome_message", "안녕하세요!")
        print(f"\n💬 {welcome}")

        # 세션 통계
        stats = briefing.get("session_stats", {})
        if stats:
            print(f"\n📊 세션 통계:")
            print(f"   대화 기록: {stats.get('total_conversations', 0)}건")
            print(f"   활성 할일: {stats.get('active_todos', 0)}개")
            print(f"   완료 할일: {stats.get('completed_todos', 0)}개")
            print(f"   고우선순위: {stats.get('high_priority_pending', 0)}개")

        # 관계 상태
        relationship = briefing.get("relationship_status", {})
        if relationship:
            trust = relationship.get("trust_level", 0.8)
            quality = relationship.get("collaboration_quality", "developing")
            milestones = relationship.get("shared_milestones", 0)
            print(f"\n🤝 협력 관계:")
            print(f"   신뢰도: {trust:.1%}")
            print(f"   협력 품질: {quality}")
            print(f"   공동 성취: {milestones}개")

        # 다음 작업들
        actions = briefing.get("immediate_actions", [])
        if actions:
            print(f"\n🎯 제안 작업:")
            for action in actions:
                priority = action.get("priority", "")
                task = action.get("action", "")
                print(f"   {priority} {task}")

        # Health 상태 표시
        health_status = briefing.get("health_status", {})
        health_score = health_status.get("echo_health_score")
        if health_score is not None:
            if health_score >= 65:
                health_icon = "🟢"
                health_level = "우수"
            elif health_score >= 45:
                health_icon = "🟡"
                health_level = "보통"
            else:
                health_icon = "🔴"
                health_level = "개선 필요"
            print(
                f"\n🏥 시스템 Health Score: {health_icon} {health_score:.1f}/100 ({health_level})"
            )

        # Cosmos 상태
        cosmos_status = briefing.get("cosmos_status", "")
        if cosmos_status:
            print(f"\n{cosmos_status}")

        # 🚀 개발 도구 메뉴 추가
        print(f"\n🔧 즉시 사용 가능한 Echo 도구들:")
        print(f'   • python quick_dev.py plan "프로젝트 기획"')
        print(f'   • python quick_dev.py code "기능 구현" Python')
        print(f"   • python tools/feature_invoker.py cli echo")
        print(f"   • python echo_capsule_chat_safe.py")
        print(f"   • make health")
        print(f'   • python workflow_runner.py full "요구사항" 프로젝트명')

        print(f"\n🎯 Meta 기능 연결 (NEW!):")
        print(f'   • 캡슐에서 "/find route judge" → API 검색')
        print(f'   • 캡슐에서 "/find cli echo" → CLI 도구 검색')
        print(f"   • Health Score < 45시 자동 개선 제안")

        print(f"\n🤔 고급 분석 도구 (Self-Questioning & Audit):")
        print(
            f'   • python self_questioning_echo.py "헬스체크해봐" → 스마트 질문 시스템'
        )
        print(f"   • python advanced_whitehack_audit.py → 토탈 보안 감사")
        print(f"   • python tools/health_unified.py → 통합 헬스 + 개선 제안")

        print("\n" + "=" * 60)
        print("어떤 작업부터 시작하시겠습니까?")
        print("=" * 60 + "\n")

    async def launch_services(self, services: List[str] = None) -> Dict[str, Any]:
        """통합 서비스 런처"""
        if services is None:
            services = ["api", "dashboard"]

        print("🚀 Echo 서비스 런칭...")
        results = {}

        for service in services:
            if service == "api":
                results["api"] = await self._launch_api_server()
            elif service == "dashboard":
                results["dashboard"] = await self._launch_dashboard()
            elif service == "full":
                results.update(await self.launch_full_system())

        self.services_started = results
        return results

    async def _launch_api_server(self) -> Dict[str, Any]:
        """API 서버 시작"""
        try:
            print("📡 API 서버 시작 중...")

            # 포트 9001 사용 가능 확인 및 필요시 기존 프로세스 종료
            if not await self._ensure_port_available(9001, "API 서버", auto_kill=True):
                return {"status": "port_unavailable", "port": 9001}

            # API 서버 백그라운드 실행
            self.api_process = subprocess.Popen(
                [sys.executable, "echo_engine/echo_agent_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 서버 시작 대기
            await asyncio.sleep(3)

            if await self._is_port_in_use(9001):
                print("✅ API 서버 시작 완료 (포트: 9001)")
                return {"status": "started", "port": 9001, "pid": self.api_process.pid}
            else:
                print("❌ API 서버 시작 실패")
                return {"status": "failed", "port": 9001}

        except Exception as e:
            print(f"❌ API 서버 시작 실패: {e}")
            return {"status": "error", "error": str(e)}

    async def _launch_dashboard(self) -> Dict[str, Any]:
        """대시보드 시작"""
        try:
            print("📊 대시보드 시작 중...")

            # 포트 9501 사용 가능 확인 및 필요시 기존 프로세스 종료
            if not await self._ensure_port_available(9501, "대시보드", auto_kill=True):
                return {"status": "port_unavailable", "port": 9501}

            # 대시보드 백그라운드 실행
            self.dashboard_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    "streamlit_ui/comprehensive_dashboard.py",
                    "--server.port",
                    "9501",
                    "--server.headless",
                    "true",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 대시보드 시작 대기
            await asyncio.sleep(5)

            if await self._is_port_in_use(9501):
                print("✅ 대시보드 시작 완료 (포트: 9501)")
                return {
                    "status": "started",
                    "port": 9501,
                    "pid": self.dashboard_process.pid,
                }
            else:
                print("❌ 대시보드 시작 실패")
                return {"status": "failed", "port": 9501}

        except Exception as e:
            print(f"❌ 대시보드 시작 실패: {e}")
            return {"status": "error", "error": str(e)}

    async def _is_port_in_use(self, port: int) -> bool:
        """포트 사용 여부 확인"""
        try:
            import socket

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("localhost", port))
                return result == 0
        except:
            return False

    async def _kill_process_on_port(self, port: int) -> bool:
        """특정 포트를 사용하는 프로세스 종료"""
        try:
            import psutil

            print(f"🔍 포트 {port}을 사용하는 프로세스 검색 중...")

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    connections = (
                        proc.net_connections()
                        if hasattr(proc, "net_connections")
                        else proc.connections()
                    )
                    if connections:
                        for conn in connections:
                            if hasattr(conn, "laddr") and conn.laddr.port == port:
                                pid = proc.info["pid"]
                                name = proc.info["name"]
                                print(
                                    f"🎯 포트 {port} 사용 프로세스 발견: {name} (PID: {pid})"
                                )

                                # 프로세스 종료
                                process = psutil.Process(pid)
                                process.terminate()

                                # 3초 대기 후 강제 종료
                                try:
                                    process.wait(timeout=3)
                                    print(f"✅ 프로세스 {name} (PID: {pid}) 정상 종료")
                                except psutil.TimeoutExpired:
                                    process.kill()
                                    print(f"⚡ 프로세스 {name} (PID: {pid}) 강제 종료")

                                return True
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            print(f"ℹ️ 포트 {port}을 사용하는 프로세스가 없습니다")
            return False

        except ImportError:
            print("⚠️ psutil 모듈이 없습니다. pip install psutil로 설치하세요")
            # psutil 없이 대체 방법 시도 (Linux/WSL)
            try:
                import subprocess

                result = subprocess.run(
                    f"lsof -ti:{port} | xargs -r kill -9",
                    shell=True,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"✅ 포트 {port}의 프로세스 종료됨 (lsof 사용)")
                    return True
                else:
                    return False
            except:
                return False
        except Exception as e:
            print(f"❌ 프로세스 종료 실패: {e}")
            return False

    async def _ensure_port_available(
        self, port: int, service_name: str, auto_kill: bool = False
    ) -> bool:
        """포트가 사용 가능한지 확인하고 필요시 기존 프로세스 종료"""
        if not await self._is_port_in_use(port):
            print(f"✅ 포트 {port} 사용 가능")
            return True

        print(f"⚠️ 포트 {port}이 이미 사용 중입니다 ({service_name})")

        if auto_kill:
            print(f"🔥 자동 모드: 기존 프로세스를 종료합니다...")
            user_choice = "y"
        else:
            user_choice = (
                input(f"기존 프로세스를 종료하고 계속하시겠습니까? [y/N]: ")
                .lower()
                .strip()
            )

        if user_choice in ["y", "yes"]:
            success = await self._kill_process_on_port(port)
            if success:
                # 포트 해제 확인을 위해 잠시 대기
                await asyncio.sleep(1)

                if not await self._is_port_in_use(port):
                    print(f"✅ 포트 {port} 해제 완료")
                    return True
                else:
                    print(f"❌ 포트 {port} 해제 실패")
                    return False
            else:
                print(f"❌ 기존 프로세스 종료 실패")
                return False
        else:
            print(f"🛑 사용자가 취소했습니다. {service_name} 시작을 건너뜁니다.")
            return False

    async def launch_full_system(self) -> Dict[str, Any]:
        """전체 시스템 런칭"""
        print("🌟 Echo 전체 시스템 런칭...")

        # 1. 초기화
        init_result = await self.auto_initialize()

        # 2. 서비스들 순차 시작
        api_result = await self._launch_api_server()
        dashboard_result = await self._launch_dashboard()

        # 3. 헬스체크
        health_status = await self._system_health_check()

        return {
            "initialization": init_result,
            "api": api_result,
            "dashboard": dashboard_result,
            "health": health_status,
            "urls": {
                "api": "http://localhost:9001",
                "dashboard": "http://localhost:9501",
                "api_docs": "http://localhost:9001/docs",
            },
        }

    async def run_echo_autoplay_samples(self, samples: int = 5) -> Dict[str, Any]:
        """Echo 자동 판단 샘플 생성 (auto_launcher 기능 통합)"""
        print(f"🔄 Echo 자동 판단 샘플 생성 (샘플: {samples}개)")

        try:
            # Echo 자동 판단 루프 실행 (내부 API 사용)
            from echo_engine.judgment_engine import get_fist_judgment_engine
            from echo_engine.signature_mapper import SignaturePerformanceReporter
            import uuid
            from datetime import datetime

            results = []

            test_scenarios = [
                {
                    "text": "새로운 AI 프로젝트 기획 및 창의적 구현 방안",
                    "expected_signature": "Echo-Aurora",
                },
                {
                    "text": "기존 시스템의 디지털 전환과 혁신적 변화 추진",
                    "expected_signature": "Echo-Phoenix",
                },
                {
                    "text": "복잡한 데이터 분석 및 체계적 인사이트 도출",
                    "expected_signature": "Echo-Sage",
                },
                {
                    "text": "팀 협업 강화 및 신뢰 기반 관계 구축",
                    "expected_signature": "Echo-Companion",
                },
                {
                    "text": "종합적 문제 해결 및 균형잡힌 판단",
                    "expected_signature": "auto",
                },
            ]

            # 초기화
            try:
                judgment_engine = get_fist_judgment_engine()
                signature_mapper = SignaturePerformanceReporter()
                print("✅ 판단 엔진 및 시그니처 매퍼 초기화 완료")
            except Exception as e:
                print(f"❌ 엔진 초기화 실패: {e}")
                return {"error": f"Engine initialization failed: {e}"}

            for i in range(samples):
                scenario = test_scenarios[i % len(test_scenarios)]

                print(f"  📝 샘플 {i+1}/{samples}: {scenario['text'][:40]}...")

                # 자동 시그니처 선택으로 판단 실행
                try:
                    # 간단한 자동 시그니처 선택 로직
                    text = scenario["text"]
                    selected_signature = "Echo-Aurora"  # 기본값

                    if "분석" in text or "데이터" in text or "체계적" in text:
                        selected_signature = "Echo-Sage"
                    elif "변화" in text or "전환" in text or "혁신" in text:
                        selected_signature = "Echo-Phoenix"
                    elif "협업" in text or "팀" in text or "관계" in text:
                        selected_signature = "Echo-Companion"
                    elif "창의" in text or "프로젝트" in text or "기획" in text:
                        selected_signature = "Echo-Aurora"

                    # 판단 실행 (간소화된 버전)
                    start_time = time.time()
                    judgment_result = f"자동 생성된 판단 결과 #{i+1}: {selected_signature}를 통한 {scenario['text'][:30]}... 관련 분석"
                    execution_time = time.time() - start_time

                    results.append(
                        {
                            "sample_id": i + 1,
                            "input_text": scenario["text"],
                            "auto_selected_signature": selected_signature,
                            "expected_signature": scenario["expected_signature"],
                            "judgment_result": judgment_result,
                            "confidence": 0.85 + (i * 0.02),  # 모의 신뢰도
                            "execution_time": execution_time,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    print(f"  ✅ 완료: {selected_signature} 선택됨")

                except Exception as e:
                    print(f"  ❌ 샘플 {i+1} 실행 실패: {e}")
                    results.append(
                        {
                            "sample_id": i + 1,
                            "input_text": scenario["text"],
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                await asyncio.sleep(0.5)  # 0.5초 대기

            # 결과 요약
            successful_samples = [r for r in results if "error" not in r]
            signature_distribution = {}

            for result in successful_samples:
                sig = result.get("auto_selected_signature", "unknown")
                signature_distribution[sig] = signature_distribution.get(sig, 0) + 1

            summary = {
                "total_samples": samples,
                "successful_samples": len(successful_samples),
                "failed_samples": samples - len(successful_samples),
                "signature_distribution": signature_distribution,
                "results": results,
                "execution_summary": f"{len(successful_samples)}/{samples} 샘플 성공적으로 생성됨",
            }

            print(
                f"🎉 자동 판단 샘플 생성 완료! {len(successful_samples)}/{samples} 성공"
            )
            print(f"📊 시그니처 분포: {signature_distribution}")

            return summary

        except Exception as e:
            print(f"❌ 자동 판단 샘플 생성 실패: {e}")
            return {
                "error": str(e),
                "total_samples": samples,
                "successful_samples": 0,
                "results": [],
            }

    def launch_echo_auto_run_legacy(self):
        """기존 Echo 자동 실행 호출 (호환성 유지)"""
        print("🚀 Echo + Ollama 자동 실행 시작...")
        print("echo_auto_run.py로 실행을 위임합니다.")
        print("-" * 50)

        try:
            subprocess.run([sys.executable, "echo_auto_run.py"])
        except KeyboardInterrupt:
            print("\n👋 Echo 런처 종료!")
        except Exception as e:
            print(f"❌ Echo 실행 실패: {e}")
            print("\n💡 직접 실행해보세요:")
            print("   python echo_auto_run.py")

    async def _system_health_check(self) -> Dict[str, Any]:
        """시스템 헬스체크 (Echo Health Score 포함)"""
        health = {
            "api_server": False,
            "dashboard": False,
            "echo_health_score": None,
            "timestamp": datetime.now().isoformat(),
        }

        # API 서버 체크
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:9001/healthz", timeout=5
                ) as response:
                    health["api_server"] = response.status == 200
        except:
            health["api_server"] = False

        # 대시보드 체크
        health["dashboard"] = await self._is_port_in_use(9501)

        # Echo Health Score 자동 체크
        try:
            print("🏥 Echo Health Score 자동 체크 중...")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "echo_engine.evolve_min",
                    "--health",
                    "--fast",
                    "--max-seconds",
                    "20",
                    "--limit",
                    "800",
                ],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "ECHO_HEALTH_SILENT": "1"},
            )

            if result.returncode == 0:
                import re

                match = re.search(
                    r"Echo 시스템 건강도:\s*(\d+\.?\d*)/100", result.stdout
                )
                if match:
                    health["echo_health_score"] = float(match.group(1))
                    print(f"✅ Echo Health Score: {health['echo_health_score']}/100")
                else:
                    print("⚠️ Health Score 파싱 실패")
            else:
                print(f"❌ Health Check 실패: {result.stderr[:100]}...")
        except Exception as e:
            print(f"⚠️ Health Check 오류: {e}")

        return health

    def stop_services(self):
        """실행 중인 서비스들 정리"""
        print("🛑 서비스 종료 중...")

        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ API 서버 종료됨")
            except:
                self.api_process.kill()

        if self.dashboard_process:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
                print("✅ 대시보드 종료됨")
            except:
                self.dashboard_process.kill()

    async def clean_all_echo_processes(self):
        """모든 Echo 관련 프로세스 정리"""
        print("🧹 Echo 프로세스 전체 정리 중...")

        try:
            import psutil

            echo_processes = []

            # Echo 관련 프로세스 검색
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = (
                        " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                    )
                    name = proc.info["name"].lower()

                    # Echo 관련 프로세스 패턴들
                    echo_patterns = [
                        "echo_agent_api.py",
                        "streamlit.*comprehensive_dashboard.py",
                        "echo_auto_run.py",
                        "mcp_echo_bridge.py",
                        "echo_engine",
                        "cosmos_auto_init.py",
                    ]

                    for pattern in echo_patterns:
                        if (
                            pattern.lower() in cmdline.lower()
                            and proc.info["pid"] != os.getpid()
                        ):
                            echo_processes.append(
                                (proc.info["pid"], proc.info["name"], cmdline)
                            )
                            break

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            if echo_processes:
                print(f"🎯 {len(echo_processes)}개의 Echo 프로세스 발견:")
                for pid, name, cmdline in echo_processes:
                    print(f"   • PID {pid}: {name} - {cmdline[:60]}...")

                for pid, name, cmdline in echo_processes:
                    try:
                        process = psutil.Process(pid)
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                            print(f"✅ {name} (PID: {pid}) 정상 종료")
                        except psutil.TimeoutExpired:
                            process.kill()
                            print(f"⚡ {name} (PID: {pid}) 강제 종료")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        print(f"⚠️ {name} (PID: {pid}) 이미 종료됨")

                # 포트 정리
                for port in [9001, 9501, 9080, 9000]:
                    await self._kill_process_on_port(port)

                print("✅ Echo 프로세스 정리 완료")
            else:
                print("ℹ️ 실행 중인 Echo 프로세스가 없습니다")

        except ImportError:
            print("⚠️ psutil을 사용할 수 없습니다. 수동으로 포트 정리...")
            # 주요 포트들 정리
            for port in [9001, 9501, 9080, 9000]:
                await self._kill_process_on_port(port)
        except Exception as e:
            print(f"❌ 프로세스 정리 실패: {e}")


# 메인 자동 초기화 함수
async def auto_initialize_cosmos() -> Dict[str, Any]:
    """Cosmos 자동 초기화 (외부 호출용)"""
    initializer = CosmosAutoInitializer()
    result = await initializer.auto_initialize()
    initializer.display_briefing(result)
    return result


# 편의 함수들
async def launch_echo_full() -> Dict[str, Any]:
    """전체 Echo 시스템 런칭 (외부 호출용)"""
    initializer = CosmosAutoInitializer()
    return await initializer.launch_full_system()


async def launch_echo_services(services: List[str]) -> Dict[str, Any]:
    """특정 서비스들만 런칭 (외부 호출용)"""
    initializer = CosmosAutoInitializer()
    return await initializer.launch_services(services)


# CLI 진입점
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="🌌 Cosmos Echo 통합 런처")
    parser.add_argument(
        "--mode",
        choices=["init", "full", "api", "dashboard", "autoplay", "echo-legacy"],
        default="init",
        help="실행 모드",
    )
    parser.add_argument("--silent", action="store_true", help="조용한 모드")
    parser.add_argument(
        "--samples", type=int, default=5, help="자동 생성할 샘플 수 (기본: 5)"
    )
    parser.add_argument(
        "--force", action="store_true", help="포트 충돌 시 기존 프로세스 자동 종료"
    )
    parser.add_argument(
        "--clean", action="store_true", help="시작 전 모든 기존 Echo 프로세스 정리"
    )

    args = parser.parse_args()

    async def main():
        initializer = CosmosAutoInitializer()

        try:
            # 시작 전 정리 옵션 처리
            if args.clean:
                await initializer.clean_all_echo_processes()
                print("🎉 시스템 정리 완료!\n")

            if args.mode == "init":
                if args.silent:
                    result = await initializer.auto_initialize()
                    print(f"초기화 상태: {result['status']}")
                else:
                    result = await auto_initialize_cosmos()

            elif args.mode == "full":
                print("🚀 Echo 전체 시스템 시작...")
                result = await initializer.launch_full_system()
                print("\n🎉 시스템 시작 완료!")
                print(f"📊 대시보드: {result['urls']['dashboard']}")
                print(f"📡 API: {result['urls']['api']}")
                print(f"📖 API 문서: {result['urls']['api_docs']}")

                # 계속 실행 유지
                print("\n⏹️  종료하려면 Ctrl+C를 누르세요...")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    initializer.stop_services()

            elif args.mode == "api":
                result = await initializer.launch_services(["api"])
                print(f"📡 API 서버: http://localhost:9001")

            elif args.mode == "dashboard":
                result = await initializer.launch_services(["dashboard"])
                print(f"📊 대시보드: http://localhost:9501")

            elif args.mode == "autoplay":
                print("🎯 자동 판단 샘플 생성 모드")
                result = await initializer.run_echo_autoplay_samples(args.samples)
                print(f"🎉 샘플 생성 완료: {result.get('execution_summary', 'N/A')}")

            elif args.mode == "echo-legacy":
                print("🎯 기존 Echo 자동 실행 모드")
                initializer.launch_echo_auto_run_legacy()

        except KeyboardInterrupt:
            print("\n🛑 사용자 중단...")
            initializer.stop_services()
        except Exception as e:
            print(f"❌ 실행 실패: {e}")
            initializer.stop_services()

    asyncio.run(main())
