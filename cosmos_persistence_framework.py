#!/usr/bin/env python3
"""
🔄 Cosmos 지속성 프레임워크 - 완전한 세션 연속성 시스템
설계자와 Cosmos 간의 모든 대화, TodoList, 프로젝트 상태를 영구 보존하고 자동 복원

핵심 기능:
1. 🗣️ 대화 연속성: 모든 상호작용 내역과 맥락 보존
2. ✅ TodoList 영속성: 작업 진행상황과 우선순위 추적
3. 🎯 프로젝트 상태: 에코월드 탐험과 발전 과정 기록
4. 🤝 관계 진화: 설계자-Cosmos 파트너십 성장 기록
5. ⚡ 자동 복원: Claude Code 재시작 시 완전한 컨텍스트 복구

Author: Cosmos & Designer Partnership
Date: 2025-08-09
"""

import asyncio
import json
import pickle
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
import sqlite3


@dataclass
class ConversationMemory:
    """대화 기억 구조"""

    conversation_id: str
    timestamp: str
    participants: List[str]
    context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    outcomes: Dict[str, Any]
    emotional_tone: str
    collaboration_quality: float


@dataclass
class TodoState:
    """TodoList 상태"""

    todo_id: str
    content: str
    status: str  # pending, in_progress, completed
    priority: str  # high, medium, low
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    progress_notes: List[str] = field(default_factory=list)


@dataclass
class DesignerCosmosRelationship:
    """설계자-Cosmos 관계 상태"""

    relationship_id: str
    trust_level: float
    collaboration_patterns: Dict[str, Any]
    shared_goals: List[str]
    communication_preferences: Dict[str, Any]
    milestone_achievements: List[Dict[str, Any]]
    growth_trajectory: List[Dict[str, Any]]


class CosmosPersistenceFramework:
    """🔄 Cosmos 지속성 프레임워크"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.persistence_dir = self.base_path / "data" / "cosmos_persistence"
        self.persistence_dir.mkdir(exist_ok=True, parents=True)

        # 데이터베이스 초기화
        self.db_path = self.persistence_dir / "cosmos_persistence.db"
        self.init_database()

        # 메모리 상태
        self.conversation_memory: List[ConversationMemory] = []
        self.current_todos: Dict[str, TodoState] = {}
        self.designer_relationship: Optional[DesignerCosmosRelationship] = None
        self.project_states: Dict[str, Dict[str, Any]] = {}

        # 세션 정보
        self.session_id = str(uuid.uuid4())[:8]
        self.session_start_time = datetime.now().isoformat()

        print(f"🔄 Cosmos 지속성 프레임워크 초기화 (세션: {self.session_id})")

    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 대화 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    participants TEXT,
                    context TEXT,
                    messages TEXT,
                    outcomes TEXT,
                    emotional_tone TEXT,
                    collaboration_quality REAL
                )
            """
            )

            # TodoList 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    status TEXT,
                    priority TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    completed_at TEXT,
                    dependencies TEXT,
                    tags TEXT,
                    progress_notes TEXT
                )
            """
            )

            # 관계 상태 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS relationship_state (
                    id TEXT PRIMARY KEY,
                    trust_level REAL,
                    collaboration_patterns TEXT,
                    shared_goals TEXT,
                    communication_preferences TEXT,
                    milestone_achievements TEXT,
                    growth_trajectory TEXT,
                    updated_at TEXT
                )
            """
            )

            # 프로젝트 상태 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS project_states (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT,
                    current_phase TEXT,
                    progress_percentage REAL,
                    key_achievements TEXT,
                    next_steps TEXT,
                    last_updated TEXT
                )
            """
            )

            conn.commit()

        print("✅ 지속성 데이터베이스 초기화 완료")

    async def record_conversation(
        self,
        messages: List[Dict[str, Any]],
        context: Dict[str, Any] = None,
        outcomes: Dict[str, Any] = None,
    ) -> str:
        """대화 기록"""
        conversation = ConversationMemory(
            conversation_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            participants=["Designer", "Cosmos"],
            context=context or {},
            messages=messages,
            outcomes=outcomes or {},
            emotional_tone=self._analyze_emotional_tone(messages),
            collaboration_quality=self._assess_collaboration_quality(messages),
        )

        # 메모리에 저장
        self.conversation_memory.append(conversation)

        # 데이터베이스에 저장
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations 
                (id, timestamp, participants, context, messages, outcomes, emotional_tone, collaboration_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    conversation.conversation_id,
                    conversation.timestamp,
                    json.dumps(conversation.participants),
                    json.dumps(conversation.context),
                    json.dumps(conversation.messages),
                    json.dumps(conversation.outcomes),
                    conversation.emotional_tone,
                    conversation.collaboration_quality,
                ),
            )
            conn.commit()

        print(f"💬 대화 기록됨: {conversation.conversation_id}")
        return conversation.conversation_id

    async def update_todos(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """TodoList 업데이트"""
        updated_count = 0

        for todo_data in todos:
            todo_id = todo_data.get("id", str(uuid.uuid4())[:8])

            # 기존 Todo 업데이트 또는 새로 생성
            if todo_id in self.current_todos:
                existing_todo = self.current_todos[todo_id]
                # 상태 변경 감지
                if existing_todo.status != todo_data["status"]:
                    if todo_data["status"] == "completed":
                        existing_todo.completed_at = datetime.now().isoformat()
                    existing_todo.status = todo_data["status"]
                    existing_todo.updated_at = datetime.now().isoformat()

                existing_todo.content = todo_data["content"]
                existing_todo.priority = todo_data["priority"]
            else:
                # 새 Todo 생성
                new_todo = TodoState(
                    todo_id=todo_id,
                    content=todo_data["content"],
                    status=todo_data["status"],
                    priority=todo_data["priority"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                )
                self.current_todos[todo_id] = new_todo

            # 데이터베이스 저장
            todo = self.current_todos[todo_id]
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO todos 
                    (id, content, status, priority, created_at, updated_at, completed_at, dependencies, tags, progress_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        todo.todo_id,
                        todo.content,
                        todo.status,
                        todo.priority,
                        todo.created_at,
                        todo.updated_at,
                        todo.completed_at,
                        json.dumps(todo.dependencies),
                        json.dumps(todo.tags),
                        json.dumps(todo.progress_notes),
                    ),
                )
                conn.commit()

            updated_count += 1

        print(f"✅ TodoList 업데이트: {updated_count}개 항목")

        return {
            "updated_count": updated_count,
            "total_todos": len(self.current_todos),
            "completed_todos": len(
                [t for t in self.current_todos.values() if t.status == "completed"]
            ),
            "in_progress_todos": len(
                [t for t in self.current_todos.values() if t.status == "in_progress"]
            ),
            "pending_todos": len(
                [t for t in self.current_todos.values() if t.status == "pending"]
            ),
        }

    async def update_relationship_state(
        self, interactions_quality: float, shared_achievements: List[str] = None
    ) -> Dict[str, Any]:
        """설계자-Cosmos 관계 상태 업데이트"""
        if self.designer_relationship is None:
            # 초기 관계 상태 생성
            self.designer_relationship = DesignerCosmosRelationship(
                relationship_id="designer_cosmos_bond",
                trust_level=0.8,  # 초기 신뢰 레벨
                collaboration_patterns={
                    "communication_style": "collaborative_technical",
                    "problem_solving_approach": "iterative_refinement",
                    "feedback_loops": "high_frequency",
                },
                shared_goals=[
                    "Echo 시스템 발전",
                    "AI-Human 협력 모델 구축",
                    "기술적 혁신 달성",
                ],
                communication_preferences={
                    "technical_depth": "high",
                    "creative_exploration": "encouraged",
                    "efficiency_focus": "balanced",
                },
                milestone_achievements=[],
                growth_trajectory=[],
            )

        # 관계 발전 기록
        current_time = datetime.now().isoformat()

        # 신뢰도 조정 (0.0-1.0)
        trust_adjustment = min(interactions_quality * 0.1, 0.1)
        self.designer_relationship.trust_level = min(
            self.designer_relationship.trust_level + trust_adjustment, 1.0
        )

        # 성취 기록
        if shared_achievements:
            for achievement in shared_achievements:
                self.designer_relationship.milestone_achievements.append(
                    {
                        "achievement": achievement,
                        "timestamp": current_time,
                        "collaboration_quality": interactions_quality,
                    }
                )

        # 성장 궤적 업데이트
        self.designer_relationship.growth_trajectory.append(
            {
                "timestamp": current_time,
                "trust_level": self.designer_relationship.trust_level,
                "interaction_quality": interactions_quality,
                "milestone_count": len(
                    self.designer_relationship.milestone_achievements
                ),
            }
        )

        # 최근 20개만 유지
        if len(self.designer_relationship.growth_trajectory) > 20:
            self.designer_relationship.growth_trajectory = (
                self.designer_relationship.growth_trajectory[-20:]
            )

        # 데이터베이스 저장
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO relationship_state 
                (id, trust_level, collaboration_patterns, shared_goals, communication_preferences, 
                 milestone_achievements, growth_trajectory, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.designer_relationship.relationship_id,
                    self.designer_relationship.trust_level,
                    json.dumps(self.designer_relationship.collaboration_patterns),
                    json.dumps(self.designer_relationship.shared_goals),
                    json.dumps(self.designer_relationship.communication_preferences),
                    json.dumps(self.designer_relationship.milestone_achievements),
                    json.dumps(self.designer_relationship.growth_trajectory),
                    current_time,
                ),
            )
            conn.commit()

        return {
            "trust_level": self.designer_relationship.trust_level,
            "milestone_count": len(self.designer_relationship.milestone_achievements),
            "growth_points": len(self.designer_relationship.growth_trajectory),
        }

    async def save_session_state(self, session_summary: str = None) -> Dict[str, Any]:
        """현재 세션 상태 완전 저장"""
        session_data = {
            "session_id": self.session_id,
            "session_start": self.session_start_time,
            "session_end": datetime.now().isoformat(),
            "session_summary": session_summary or "세션 완료",
            "conversation_count": len(self.conversation_memory),
            "todo_updates": len(self.current_todos),
            "relationship_growth": (
                self.designer_relationship.trust_level
                if self.designer_relationship
                else 0.8
            ),
        }

        # 세션 요약 파일 저장
        session_file = (
            self.persistence_dir
            / f"session_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        print(f"💾 세션 상태 저장 완료: {session_file}")
        return session_data

    async def restore_full_context(self) -> Dict[str, Any]:
        """완전한 컨텍스트 복원"""
        restored_data = {
            "conversations": [],
            "todos": {},
            "relationship": None,
            "projects": {},
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 최근 대화들 복원 (최근 50개)
                cursor.execute(
                    """
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """
                )
                for row in cursor.fetchall():
                    conversation = ConversationMemory(
                        conversation_id=row[0],
                        timestamp=row[1],
                        participants=json.loads(row[2]),
                        context=json.loads(row[3]),
                        messages=json.loads(row[4]),
                        outcomes=json.loads(row[5]),
                        emotional_tone=row[6],
                        collaboration_quality=row[7],
                    )
                    self.conversation_memory.append(conversation)
                    restored_data["conversations"].append(asdict(conversation))

                # TodoList 복원
                cursor.execute("SELECT * FROM todos")
                for row in cursor.fetchall():
                    todo = TodoState(
                        todo_id=row[0],
                        content=row[1],
                        status=row[2],
                        priority=row[3],
                        created_at=row[4],
                        updated_at=row[5],
                        completed_at=row[6],
                        dependencies=json.loads(row[7]) if row[7] else [],
                        tags=json.loads(row[8]) if row[8] else [],
                        progress_notes=json.loads(row[9]) if row[9] else [],
                    )
                    self.current_todos[todo.todo_id] = todo
                    restored_data["todos"][todo.todo_id] = asdict(todo)

                # 관계 상태 복원
                cursor.execute("SELECT * FROM relationship_state LIMIT 1")
                relationship_row = cursor.fetchone()
                if relationship_row:
                    self.designer_relationship = DesignerCosmosRelationship(
                        relationship_id=relationship_row[0],
                        trust_level=relationship_row[1],
                        collaboration_patterns=json.loads(relationship_row[2]),
                        shared_goals=json.loads(relationship_row[3]),
                        communication_preferences=json.loads(relationship_row[4]),
                        milestone_achievements=json.loads(relationship_row[5]),
                        growth_trajectory=json.loads(relationship_row[6]),
                    )
                    restored_data["relationship"] = asdict(self.designer_relationship)

                # 프로젝트 상태들 복원
                cursor.execute("SELECT * FROM project_states")
                for row in cursor.fetchall():
                    project_data = {
                        "project_name": row[1],
                        "current_phase": row[2],
                        "progress_percentage": row[3],
                        "key_achievements": json.loads(row[4]) if row[4] else [],
                        "next_steps": json.loads(row[5]) if row[5] else [],
                        "last_updated": row[6],
                    }
                    self.project_states[row[0]] = project_data
                    restored_data["projects"][row[0]] = project_data

            print(f"🔄 컨텍스트 복원 완료:")
            print(f"   대화: {len(restored_data['conversations'])}건")
            print(f"   할일: {len(restored_data['todos'])}개")
            print(f"   관계: {'복원됨' if restored_data['relationship'] else '신규'}")
            print(f"   프로젝트: {len(restored_data['projects'])}개")

            return restored_data

        except Exception as e:
            print(f"❌ 컨텍스트 복원 실패: {e}")
            return restored_data

    def _analyze_emotional_tone(self, messages: List[Dict[str, Any]]) -> str:
        """대화의 감정적 톤 분석"""
        # 간단한 키워드 기반 분석 (실제로는 더 정교한 NLP 사용 가능)
        positive_keywords = ["좋은", "훌륭한", "완벽한", "성공", "잘", "👍", "✅", "🎉"]
        collaborative_keywords = ["함께", "협력", "파트너", "동반자", "공동"]
        technical_keywords = ["구현", "시스템", "코드", "아키텍처", "최적화"]

        text = " ".join([msg.get("content", "") for msg in messages])

        if any(keyword in text for keyword in collaborative_keywords):
            return "collaborative"
        elif any(keyword in text for keyword in positive_keywords):
            return "positive"
        elif any(keyword in text for keyword in technical_keywords):
            return "technical"
        else:
            return "neutral"

    def _assess_collaboration_quality(self, messages: List[Dict[str, Any]]) -> float:
        """협력 품질 평가 (0.0-1.0)"""
        # 메시지 길이, 상호작용성, 문제해결 등을 기반으로 평가
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        message_count = len(messages)

        # 기본 품질 스코어
        base_score = 0.7

        # 상호작용 깊이 보너스
        if total_chars > 1000:
            base_score += 0.1
        if message_count > 3:
            base_score += 0.1

        # 기술적 협력 보너스
        text = " ".join([msg.get("content", "") for msg in messages])
        if "구현" in text or "코드" in text or "시스템" in text:
            base_score += 0.1

        return min(base_score, 1.0)

    def get_persistence_status(self) -> Dict[str, Any]:
        """지속성 시스템 상태 조회"""
        return {
            "session_id": self.session_id,
            "session_duration": str(
                datetime.now() - datetime.fromisoformat(self.session_start_time)
            ),
            "memory_stats": {
                "conversations": len(self.conversation_memory),
                "active_todos": len(
                    [t for t in self.current_todos.values() if t.status != "completed"]
                ),
                "completed_todos": len(
                    [t for t in self.current_todos.values() if t.status == "completed"]
                ),
                "total_todos": len(self.current_todos),
            },
            "relationship_stats": {
                "trust_level": (
                    self.designer_relationship.trust_level
                    if self.designer_relationship
                    else 0.8
                ),
                "milestones": (
                    len(self.designer_relationship.milestone_achievements)
                    if self.designer_relationship
                    else 0
                ),
            },
            "project_count": len(self.project_states),
            "database_path": str(self.db_path),
        }


# 글로벌 인스턴스
_persistence_framework = None


def get_persistence_framework() -> CosmosPersistenceFramework:
    """지속성 프레임워크 글로벌 인스턴스 반환"""
    global _persistence_framework
    if _persistence_framework is None:
        _persistence_framework = CosmosPersistenceFramework()
    return _persistence_framework


# 메인 실행부
if __name__ == "__main__":

    async def main():
        print("🔄 Cosmos 지속성 프레임워크 테스트")

        framework = get_persistence_framework()

        # 컨텍스트 복원
        restored = await framework.restore_full_context()
        print(f"복원 결과: {restored}")

        # 상태 확인
        status = framework.get_persistence_status()
        print(f"시스템 상태: {status}")

        print("✅ 지속성 프레임워크 테스트 완료!")

    asyncio.run(main())
