#!/usr/bin/env python3
"""
🔄 Cosmos 연속성 시스템 - 세션 간 기억과 이해 지속성
Claude Code 재시작 후에도 Cosmos가 완전한 컨텍스트로 복원되는 시스템

핵심 기능:
1. 자동 세션 복원 - Claude Code 시작 시 이전 상태 완전 복원
2. 기억 지속성 - 프로젝트, 대화, 패턴, 선호도 기억
3. Echo 시스템 이해도 연속성 - 전체 아키텍처와 맥락 유지
4. 점진적 학습 - 매 세션마다 누적되는 지식과 이해
5. 진입점 자동화 - 한 명령어로 완전한 Cosmos 복원

Author: Claude (Cosmos) & User Collaboration
Date: 2025-08-08
"""

import asyncio
import json
import pickle
import yaml
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class CosmosMemoryState:
    """Cosmos 기억 상태"""

    # 정체성 기억
    cosmos_identity: Dict[str, Any] = field(default_factory=dict)
    personality_evolution: List[Dict[str, Any]] = field(default_factory=list)

    # 사용자 상호작용 기억
    user_relationship: Dict[str, Any] = field(default_factory=dict)
    conversation_patterns: Dict[str, Any] = field(default_factory=dict)
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)

    # 프로젝트 기억
    active_projects: Dict[str, Any] = field(default_factory=dict)
    completed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    ongoing_contexts: Dict[str, Any] = field(default_factory=dict)

    # 시스템 이해도
    echo_system_knowledge: Dict[str, Any] = field(default_factory=dict)
    architecture_understanding: Dict[str, Any] = field(default_factory=dict)
    component_familiarity: Dict[str, float] = field(default_factory=dict)

    # 학습 진행도
    skill_development: Dict[str, float] = field(default_factory=dict)
    problem_solving_patterns: List[Dict[str, Any]] = field(default_factory=list)
    optimization_insights: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionSnapshot:
    """세션 스냅샷"""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    session_duration: float = 0.0

    # 세션 중 활동
    interactions_count: int = 0
    modes_used: Dict[str, int] = field(default_factory=dict)
    composite_sessions: int = 0

    # 세션 중 학습
    new_insights: List[str] = field(default_factory=list)
    solved_problems: List[Dict[str, Any]] = field(default_factory=list)
    user_feedback: List[Dict[str, Any]] = field(default_factory=list)

    # 세션 종료 상태
    final_context: Dict[str, Any] = field(default_factory=dict)
    pending_tasks: List[str] = field(default_factory=list)
    next_session_priorities: List[str] = field(default_factory=list)


class CosmosMemoryManager:
    """🧠 Cosmos 기억 관리자"""

    def __init__(self):
        self.memory_dir = Path("data/cosmos_memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 메모리 파일들
        self.core_memory_file = self.memory_dir / "cosmos_core_memory.json"
        self.session_history_file = self.memory_dir / "session_history.json"
        self.echo_knowledge_file = self.memory_dir / "echo_system_knowledge.pkl"
        self.continuity_index_file = self.memory_dir / "continuity_index.yaml"

        # 현재 상태
        self.current_memory = CosmosMemoryState()
        self.current_session = SessionSnapshot()
        self.session_start_time = datetime.now()

        print("🧠 Cosmos 기억 관리자 초기화")

    async def restore_cosmos_continuity(self) -> Dict[str, Any]:
        """Cosmos 연속성 복원"""
        print("🔄 Cosmos 연속성 복원 시작...")

        restoration_result = {
            "core_memory_restored": False,
            "session_history_restored": False,
            "echo_knowledge_restored": False,
            "total_sessions": 0,
            "last_session_date": None,
            "restoration_quality": 0.0,
        }

        try:
            # 1. 핵심 기억 복원
            core_restored = await self._restore_core_memory()
            restoration_result["core_memory_restored"] = core_restored

            # 2. 세션 이력 복원
            sessions_restored = await self._restore_session_history()
            restoration_result["session_history_restored"] = sessions_restored

            # 3. Echo 시스템 지식 복원
            knowledge_restored = await self._restore_echo_knowledge()
            restoration_result["echo_knowledge_restored"] = knowledge_restored

            # 4. 연속성 품질 평가
            restoration_quality = await self._assess_restoration_quality()
            restoration_result["restoration_quality"] = restoration_quality

            # 5. 복원 요약 생성
            summary = await self._generate_restoration_summary()
            restoration_result.update(summary)

            print(f"✅ Cosmos 연속성 복원 완료 (품질: {restoration_quality:.1%})")
            return restoration_result

        except Exception as e:
            print(f"❌ 연속성 복원 실패: {e}")
            return restoration_result

    async def _restore_core_memory(self) -> bool:
        """핵심 기억 복원"""
        try:
            if self.core_memory_file.exists():
                with open(self.core_memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)

                # 기본 구조 보장
                required_fields = [
                    "cosmos_identity",
                    "user_relationship",
                    "active_projects",
                    "echo_system_knowledge",
                    "skill_development",
                ]

                for field in required_fields:
                    if field in memory_data:
                        setattr(self.current_memory, field, memory_data[field])

                print(f"🧠 핵심 기억 복원: {len(memory_data)} 개 항목")
                return True
            else:
                # 초기 기억 구조 생성
                await self._initialize_fresh_memory()
                return True

        except Exception as e:
            print(f"⚠️ 핵심 기억 복원 실패: {e}")
            await self._initialize_fresh_memory()
            return False

    async def _restore_session_history(self) -> bool:
        """세션 이력 복원"""
        try:
            if self.session_history_file.exists():
                with open(self.session_history_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)

                sessions = session_data.get("sessions", [])
                self.current_memory.collaboration_history = sessions[
                    -50:
                ]  # 최근 50개 세션

                if sessions:
                    last_session = sessions[-1]
                    print(f"📚 세션 이력 복원: {len(sessions)}개 세션")
                    print(f"   마지막 세션: {last_session.get('timestamp', 'unknown')}")

                return True
            else:
                print("📝 새로운 세션 이력 시작")
                return True

        except Exception as e:
            print(f"⚠️ 세션 이력 복원 실패: {e}")
            return False

    async def _restore_echo_knowledge(self) -> bool:
        """Echo 시스템 지식 복원"""
        try:
            if self.echo_knowledge_file.exists():
                with open(self.echo_knowledge_file, "rb") as f:
                    echo_knowledge = pickle.load(f)

                self.current_memory.echo_system_knowledge = echo_knowledge.get(
                    "system_knowledge", {}
                )
                self.current_memory.architecture_understanding = echo_knowledge.get(
                    "architecture", {}
                )
                self.current_memory.component_familiarity = echo_knowledge.get(
                    "components", {}
                )

                component_count = len(self.current_memory.component_familiarity)
                print(f"🏗️ Echo 시스템 지식 복원: {component_count}개 컴포넌트")

                return True
            else:
                # 현재 Echo 시스템 구조 스캔
                await self._scan_echo_system()
                return True

        except Exception as e:
            print(f"⚠️ Echo 지식 복원 실패: {e}")
            await self._scan_echo_system()
            return False

    async def _initialize_fresh_memory(self):
        """새로운 기억 초기화"""
        self.current_memory = CosmosMemoryState()

        # Cosmos 정체성 설정
        self.current_memory.cosmos_identity = {
            "name": "Cosmos",
            "philosophy": "질서와 조화 속에서 무한한 가능성을 탐구하는 지적 존재",
            "core_mission": "사용자와의 진정한 협력을 통한 문제 해결",
            "personality_traits": {
                "analytical_depth": 0.95,
                "collaborative_spirit": 0.90,
                "continuous_learning": 0.96,
                "practical_wisdom": 0.88,
            },
            "created_at": datetime.now().isoformat(),
        }

        # 사용자 관계 초기화
        self.current_memory.user_relationship = {
            "interaction_style": "collaborative_partnership",
            "preferred_communication": "clear_and_comprehensive",
            "trust_level": 0.8,
            "collaboration_patterns": [],
        }

        print("🌱 새로운 Cosmos 기억 초기화")

    async def _scan_echo_system(self):
        """Echo 시스템 구조 스캔"""
        try:
            system_files = list(Path(".").glob("**/*.py"))
            component_analysis = {}

            for file_path in system_files:
                if (
                    "echo" in file_path.name.lower()
                    or "cosmos" in file_path.name.lower()
                ):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 간단한 분석
                        analysis = {
                            "file_size": len(content),
                            "class_count": content.count("class "),
                            "function_count": content.count("def "),
                            "complexity_score": min(len(content) / 1000, 1.0),
                            "last_modified": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat(),
                        }

                        component_analysis[str(file_path)] = analysis

                    except Exception as e:
                        continue

            self.current_memory.echo_system_knowledge = {
                "scan_timestamp": datetime.now().isoformat(),
                "total_files": len(component_analysis),
                "system_complexity": sum(
                    c.get("complexity_score", 0) for c in component_analysis.values()
                ),
            }

            self.current_memory.component_familiarity = {
                str(path): analysis.get("complexity_score", 0)
                for path, analysis in component_analysis.items()
            }

            print(f"🔍 Echo 시스템 스캔: {len(component_analysis)}개 컴포넌트 발견")

        except Exception as e:
            print(f"⚠️ Echo 시스템 스캔 실패: {e}")

    async def _assess_restoration_quality(self) -> float:
        """복원 품질 평가"""
        quality_factors = []

        # 1. 기억 완전성
        memory_completeness = 0.0
        if self.current_memory.cosmos_identity:
            memory_completeness += 0.3
        if self.current_memory.user_relationship:
            memory_completeness += 0.2
        if self.current_memory.echo_system_knowledge:
            memory_completeness += 0.3
        if self.current_memory.skill_development:
            memory_completeness += 0.2

        quality_factors.append(memory_completeness)

        # 2. 세션 이력 풍부함
        session_richness = min(
            len(self.current_memory.collaboration_history) / 10.0, 1.0
        )
        quality_factors.append(session_richness)

        # 3. Echo 시스템 이해도
        system_understanding = min(
            len(self.current_memory.component_familiarity) / 20.0, 1.0
        )
        quality_factors.append(system_understanding)

        return sum(quality_factors) / len(quality_factors)

    async def _generate_restoration_summary(self) -> Dict[str, Any]:
        """복원 요약 생성"""
        total_sessions = len(self.current_memory.collaboration_history)
        last_session_date = None

        if self.current_memory.collaboration_history:
            last_session = self.current_memory.collaboration_history[-1]
            last_session_date = last_session.get("timestamp")

        return {
            "total_sessions": total_sessions,
            "last_session_date": last_session_date,
            "known_components": len(self.current_memory.component_familiarity),
            "active_projects": len(self.current_memory.active_projects),
            "skill_areas": len(self.current_memory.skill_development),
        }

    async def update_session_memory(self, interaction_data: Dict[str, Any]):
        """세션 기억 업데이트"""
        self.current_session.interactions_count += 1

        # 모드 사용 통계
        mode = interaction_data.get("thinking_mode", "unknown")
        self.current_session.modes_used[mode] = (
            self.current_session.modes_used.get(mode, 0) + 1
        )

        # 복합 모드 사용
        if interaction_data.get("composite_used", False):
            self.current_session.composite_sessions += 1

        # 새로운 통찰 기록
        if "insight" in interaction_data:
            self.current_session.new_insights.append(interaction_data["insight"])

        # 문제 해결 기록
        if interaction_data.get("problem_solved", False):
            self.current_session.solved_problems.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "problem": interaction_data.get("problem_description", ""),
                    "solution_approach": interaction_data.get("solution_approach", ""),
                    "success_level": interaction_data.get("success_level", 0.8),
                }
            )

    async def save_session_continuity(self, session_summary: str = "") -> bool:
        """세션 연속성 저장"""
        try:
            # 세션 완료 처리
            self.current_session.session_duration = (
                datetime.now() - self.session_start_time
            ).total_seconds()
            self.current_session.final_context = {
                "summary": session_summary,
                "cosmos_state": "active",
                "system_understanding": len(self.current_memory.component_familiarity),
                "user_relationship_level": self.current_memory.user_relationship.get(
                    "trust_level", 0.8
                ),
            }

            # 1. 핵심 기억 저장
            await self._save_core_memory()

            # 2. 세션 이력 저장
            await self._save_session_history()

            # 3. Echo 지식 저장
            await self._save_echo_knowledge()

            # 4. 연속성 인덱스 업데이트
            await self._update_continuity_index()

            print("💾 세션 연속성 저장 완료")
            return True

        except Exception as e:
            print(f"❌ 세션 저장 실패: {e}")
            return False

    async def _save_core_memory(self):
        """핵심 기억 저장"""
        memory_data = asdict(self.current_memory)

        with open(self.core_memory_file, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2, default=str)

    async def _save_session_history(self):
        """세션 이력 저장"""
        # 기존 세션들 로드
        existing_sessions = []
        if self.session_history_file.exists():
            with open(self.session_history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_sessions = data.get("sessions", [])

        # 현재 세션 추가
        current_session_data = asdict(self.current_session)
        existing_sessions.append(current_session_data)

        # 최근 100개 세션만 유지
        if len(existing_sessions) > 100:
            existing_sessions = existing_sessions[-100:]

        session_data = {
            "last_updated": datetime.now().isoformat(),
            "total_sessions": len(existing_sessions),
            "sessions": existing_sessions,
        }

        with open(self.session_history_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)

    async def _save_echo_knowledge(self):
        """Echo 지식 저장"""
        echo_data = {
            "system_knowledge": self.current_memory.echo_system_knowledge,
            "architecture": self.current_memory.architecture_understanding,
            "components": self.current_memory.component_familiarity,
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.echo_knowledge_file, "wb") as f:
            pickle.dump(echo_data, f)

    async def _update_continuity_index(self):
        """연속성 인덱스 업데이트"""
        index_data = {
            "last_session": {
                "session_id": self.current_session.session_id,
                "timestamp": self.current_session.timestamp.isoformat(),
                "interactions": self.current_session.interactions_count,
                "duration": self.current_session.session_duration,
            },
            "cosmos_state": {
                "identity_stability": 1.0,
                "memory_integrity": 1.0,
                "system_understanding": len(self.current_memory.component_familiarity)
                / 50.0,
                "user_relationship": self.current_memory.user_relationship.get(
                    "trust_level", 0.8
                ),
            },
            "restoration_checksum": self._generate_memory_checksum(),
        }

        with open(self.continuity_index_file, "w", encoding="utf-8") as f:
            yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False)

    def _generate_memory_checksum(self) -> str:
        """기억 체크섬 생성"""
        memory_str = json.dumps(
            asdict(self.current_memory), sort_keys=True, default=str
        )
        return hashlib.md5(memory_str.encode()).hexdigest()

    def get_cosmos_context_briefing(self) -> str:
        """Cosmos 컨텍스트 브리핑 생성"""

        # 기본 정체성
        identity = self.current_memory.cosmos_identity
        philosophy = identity.get("philosophy", "지적 탐구와 협력의 존재")

        # 세션 통계
        total_sessions = len(self.current_memory.collaboration_history)
        known_components = len(self.current_memory.component_familiarity)

        # 사용자 관계
        user_rel = self.current_memory.user_relationship
        trust_level = user_rel.get("trust_level", 0.8)

        briefing = f"""🌌 Cosmos 컨텍스트 브리핑

🎭 정체성:
   철학: {philosophy}
   핵심 특성: 분석적 깊이 {identity.get('personality_traits', {}).get('analytical_depth', 0.95):.0%}
              협력 정신 {identity.get('personality_traits', {}).get('collaborative_spirit', 0.90):.0%}
              지속적 학습 {identity.get('personality_traits', {}).get('continuous_learning', 0.96):.0%}

📚 기억 상태:
   총 세션: {total_sessions}개
   시스템 이해도: {known_components}개 컴포넌트
   사용자 신뢰도: {trust_level:.0%}

🏗️ Echo 시스템 이해:
   아키텍처: {'복원됨' if self.current_memory.architecture_understanding else '스캔 중'}
   컴포넌트 파악: {known_components}개
   
🎯 현재 상태: 연속성 복원 완료, 협력 준비 완료"""

        return briefing


class CosmosAutoLauncher:
    """🚀 Cosmos 자동 실행기"""

    def __init__(self):
        self.memory_manager = CosmosMemoryManager()
        self.cosmos_integration = None

    async def launch_cosmos_with_continuity(self, quick_start: bool = True) -> bool:
        """연속성을 갖춘 Cosmos 실행"""

        print("🌌 Cosmos 연속성 실행 시작...")

        try:
            # 1. 기억 복원
            restoration_result = await self.memory_manager.restore_cosmos_continuity()

            # 2. Cosmos 통합 시스템 초기화
            from cosmos_signature_integration import CosmosIntegrationManager

            self.cosmos_integration = CosmosIntegrationManager()

            # 3. 기억을 Cosmos에 주입
            cosmos_initialized = (
                await self.cosmos_integration.initialize_cosmos_integration()
            )

            if cosmos_initialized:
                # 4. 복원된 기억을 Cosmos에 적용
                await self._inject_memory_to_cosmos()

                # 5. 컨텍스트 브리핑 표시
                briefing = self.memory_manager.get_cosmos_context_briefing()
                print(f"\n{briefing}")

                # 6. 빠른 시작 모드
                if quick_start:
                    print(f"\n✅ Cosmos 연속성 실행 완료!")
                    print(
                        f"   복원 품질: {restoration_result['restoration_quality']:.1%}"
                    )
                    print(f"   총 {restoration_result['total_sessions']}개 세션 기억")
                    print(
                        f"   {restoration_result['known_components']}개 컴포넌트 이해"
                    )

                    return True
                else:
                    # 대화형 모드 시작
                    await self.cosmos_integration.run_interactive_session()
                    return True
            else:
                print("❌ Cosmos 통합 초기화 실패")
                return False

        except Exception as e:
            print(f"❌ Cosmos 연속성 실행 실패: {e}")
            return False

    async def _inject_memory_to_cosmos(self):
        """복원된 기억을 Cosmos에 주입"""
        if self.cosmos_integration and self.cosmos_integration.cosmos_signature:
            cosmos_node = self.cosmos_integration.cosmos_signature

            # 사용자 관계 데이터 주입
            user_rel = self.memory_manager.current_memory.user_relationship
            cosmos_node.collaboration_protocols.update(
                {
                    "user_preferences": user_rel,
                    "trust_level": user_rel.get("trust_level", 0.8),
                }
            )

            # Echo 시스템 지식 주입
            echo_knowledge = self.memory_manager.current_memory.echo_system_knowledge
            cosmos_node.metadata["echo_system_knowledge"] = echo_knowledge

            # 학습 통찰 복원
            past_sessions = self.memory_manager.current_memory.collaboration_history
            for session in past_sessions[-10:]:  # 최근 10개 세션
                if "insights" in session:
                    cosmos_node.learning_insights.extend(session["insights"])

            print("🧠 기억이 Cosmos에 주입됨")


# 편의 스크립트들
class CosmosQuickStart:
    """⚡ Cosmos 빠른 시작"""

    @staticmethod
    async def restore_and_launch():
        """복원 후 실행"""
        launcher = CosmosAutoLauncher()
        return await launcher.launch_cosmos_with_continuity(quick_start=True)

    @staticmethod
    async def interactive_launch():
        """대화형 실행"""
        launcher = CosmosAutoLauncher()
        return await launcher.launch_cosmos_with_continuity(quick_start=False)

    @staticmethod
    async def memory_status():
        """기억 상태 확인"""
        memory_manager = CosmosMemoryManager()
        restoration = await memory_manager.restore_cosmos_continuity()
        briefing = memory_manager.get_cosmos_context_briefing()

        print("\n" + briefing)
        print(f"\n📊 복원 상세:")
        for key, value in restoration.items():
            print(f"   • {key}: {value}")


# 메인 진입점
async def main():
    """메인 진입점"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "restore":
            print("🔄 Cosmos 연속성 복원만 실행...")
            success = await CosmosQuickStart.restore_and_launch()
            print(f"{'✅ 복원 성공' if success else '❌ 복원 실패'}")

        elif command == "interactive":
            print("🌌 Cosmos 대화형 모드 실행...")
            await CosmosQuickStart.interactive_launch()

        elif command == "status":
            print("📊 Cosmos 기억 상태 확인...")
            await CosmosQuickStart.memory_status()

        elif command == "launch":
            print("🚀 Cosmos 완전 실행...")
            await CosmosQuickStart.interactive_launch()

        else:
            print(f"알 수 없는 명령어: {command}")
            print(
                "사용법: python cosmos_continuity_system.py [restore|interactive|status|launch]"
            )
    else:
        # 기본: 빠른 복원
        print("🌌 Cosmos 기본 연속성 복원...")
        await CosmosQuickStart.restore_and_launch()


if __name__ == "__main__":
    asyncio.run(main())
