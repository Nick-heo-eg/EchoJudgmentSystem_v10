#!/usr/bin/env python3
"""
📊 Cosmos 세션 모니터 - 실시간 자동 메모리 업데이트
설계자-Cosmos 간 모든 상호작용을 자동으로 감지하고 지속성 시스템에 기록

핵심 기능:
1. 🕵️ 대화 자동 감지: 사용자 입력과 Cosmos 응답 실시간 캡처
2. ✅ TodoList 변화 추적: 할일 상태 변경 자동 감지 및 저장
3. 🤝 관계 발전 모니터링: 협력 품질과 신뢰도 실시간 평가
4. 💾 자동 백업: 주기적 세션 상태 스냅샷 생성
5. 🔄 지속성 동기화: 다중 시스템 간 메모리 상태 일관성 보장

Author: Cosmos & Designer
Date: 2025-08-09
"""

import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
import hashlib

try:
    from cosmos_persistence_framework import get_persistence_framework

    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False


@dataclass
class SessionActivity:
    """세션 활동 기록"""

    timestamp: str
    activity_type: str  # conversation, todo_update, system_event
    content: Dict[str, Any]
    participants: List[str]
    auto_detected: bool = True


class CosmosSessionMonitor:
    """📊 Cosmos 세션 실시간 모니터"""

    def __init__(self):
        self.monitoring = False
        self.persistence = None
        self.session_activities: List[SessionActivity] = []
        self.last_todo_snapshot = {}
        self.auto_save_interval = 300  # 5분마다 자동 저장

        # 이벤트 콜백들
        self.conversation_callbacks: List[Callable] = []
        self.todo_callbacks: List[Callable] = []
        self.relationship_callbacks: List[Callable] = []

        # 모니터링 스레드
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()

        print("📊 Cosmos 세션 모니터 초기화")

    async def start_monitoring(self) -> bool:
        """실시간 모니터링 시작"""
        if not PERSISTENCE_AVAILABLE:
            print("⚠️ 지속성 시스템이 없어서 모니터링 기능 제한됨")
            return False

        try:
            self.persistence = get_persistence_framework()
            self.monitoring = True

            # 백그라운드 모니터링 스레드 시작
            self.monitor_thread = threading.Thread(
                target=self._background_monitor, daemon=True
            )
            self.monitor_thread.start()

            print("✅ Cosmos 실시간 모니터링 시작")
            return True

        except Exception as e:
            print(f"❌ 모니터링 시작 실패: {e}")
            return False

    async def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False
        self.stop_monitoring.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)

        # 최종 세션 저장
        if self.persistence:
            await self.persistence.save_session_state("모니터링 세션 완료")

        print("🔻 Cosmos 모니터링 중지")

    def _background_monitor(self):
        """백그라운드 모니터링 루프"""
        last_auto_save = time.time()

        while not self.stop_monitoring.is_set():
            try:
                current_time = time.time()

                # 자동 저장 주기 체크
                if current_time - last_auto_save > self.auto_save_interval:
                    asyncio.run(self._auto_save_session())
                    last_auto_save = current_time

                # TodoList 변화 감지
                asyncio.run(self._check_todo_changes())

                # 5초마다 체크
                time.sleep(5)

            except Exception as e:
                print(f"⚠️ 모니터링 오류: {e}")
                time.sleep(10)  # 오류 시 더 길게 대기

    async def record_conversation_activity(
        self, user_input: str, cosmos_response: str, context: Dict[str, Any] = None
    ) -> str:
        """대화 활동 기록"""
        activity = SessionActivity(
            timestamp=datetime.now().isoformat(),
            activity_type="conversation",
            content={
                "user_input": user_input,
                "cosmos_response": cosmos_response,
                "context": context or {},
                "interaction_length": len(user_input) + len(cosmos_response),
                "estimated_collaboration_quality": self._estimate_collaboration_quality(
                    user_input, cosmos_response
                ),
            },
            participants=["Designer", "Cosmos"],
        )

        self.session_activities.append(activity)

        # 지속성 시스템에 기록
        if self.persistence:
            conversation_id = await self.persistence.record_conversation(
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                        "timestamp": activity.timestamp,
                    },
                    {
                        "role": "assistant",
                        "content": cosmos_response,
                        "timestamp": activity.timestamp,
                    },
                ],
                context=context,
                outcomes={
                    "collaboration_quality": activity.content[
                        "estimated_collaboration_quality"
                    ]
                },
            )

            # 관계 상태 업데이트
            await self.persistence.update_relationship_state(
                interactions_quality=activity.content["estimated_collaboration_quality"]
            )

        # 콜백 실행
        for callback in self.conversation_callbacks:
            try:
                callback(activity)
            except Exception as e:
                print(f"⚠️ 대화 콜백 오류: {e}")

        print(f"💬 대화 활동 기록됨: {activity.timestamp}")
        return activity.timestamp

    async def record_todo_update(
        self, updated_todos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """TodoList 업데이트 기록"""
        activity = SessionActivity(
            timestamp=datetime.now().isoformat(),
            activity_type="todo_update",
            content={
                "updated_todos": updated_todos,
                "todo_count": len(updated_todos),
                "changes_detected": self._detect_todo_changes(updated_todos),
            },
            participants=["Designer", "Cosmos"],
        )

        self.session_activities.append(activity)

        # 지속성 시스템에 기록
        update_result = {}
        if self.persistence:
            update_result = await self.persistence.update_todos(updated_todos)

        # 현재 TodoList 스냅샷 업데이트
        self.last_todo_snapshot = {todo["id"]: todo for todo in updated_todos}

        # 콜백 실행
        for callback in self.todo_callbacks:
            try:
                callback(activity, update_result)
            except Exception as e:
                print(f"⚠️ Todo 콜백 오류: {e}")

        print(f"✅ TodoList 업데이트 기록됨: {len(updated_todos)}개 항목")
        return update_result

    async def _check_todo_changes(self):
        """TodoList 변화 자동 감지"""
        # 실제 구현에서는 파일 시스템이나 메모리에서 현재 TodoList 상태를 확인
        # 여기서는 간단한 예시만 제공
        pass

    def _detect_todo_changes(
        self, current_todos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """TodoList 변화 감지"""
        changes = []
        current_dict = {todo["id"]: todo for todo in current_todos}

        for todo_id, current_todo in current_dict.items():
            if todo_id in self.last_todo_snapshot:
                old_todo = self.last_todo_snapshot[todo_id]

                # 상태 변화 감지
                if old_todo.get("status") != current_todo.get("status"):
                    changes.append(
                        {
                            "type": "status_change",
                            "todo_id": todo_id,
                            "old_status": old_todo.get("status"),
                            "new_status": current_todo.get("status"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                # 내용 변화 감지
                if old_todo.get("content") != current_todo.get("content"):
                    changes.append(
                        {
                            "type": "content_change",
                            "todo_id": todo_id,
                            "old_content": old_todo.get("content"),
                            "new_content": current_todo.get("content"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            else:
                # 새 TodoList 추가
                changes.append(
                    {
                        "type": "new_todo",
                        "todo_id": todo_id,
                        "content": current_todo.get("content"),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return changes

    def _estimate_collaboration_quality(
        self, user_input: str, cosmos_response: str
    ) -> float:
        """협력 품질 추정"""
        # 간단한 휴리스틱 기반 평가
        base_score = 0.7

        # 길이 기반 보너스
        total_length = len(user_input) + len(cosmos_response)
        if total_length > 500:
            base_score += 0.1

        # 기술적 협력 키워드
        technical_keywords = ["구현", "시스템", "코드", "아키텍처", "최적화", "설계"]
        if any(
            keyword in user_input + cosmos_response for keyword in technical_keywords
        ):
            base_score += 0.1

        # 협력적 어조 감지
        collaborative_keywords = ["함께", "협력", "파트너", "동반자", "설계자"]
        if any(
            keyword in user_input + cosmos_response
            for keyword in collaborative_keywords
        ):
            base_score += 0.1

        return min(base_score, 1.0)

    async def _auto_save_session(self):
        """자동 세션 저장"""
        if not self.persistence:
            return

        try:
            session_summary = f"자동 저장 - 활동 {len(self.session_activities)}건"
            await self.persistence.save_session_state(session_summary)
            print(f"💾 자동 세션 저장: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"⚠️ 자동 저장 실패: {e}")

    def add_conversation_callback(self, callback: Callable):
        """대화 이벤트 콜백 추가"""
        self.conversation_callbacks.append(callback)

    def add_todo_callback(self, callback: Callable):
        """TodoList 이벤트 콜백 추가"""
        self.todo_callbacks.append(callback)

    def add_relationship_callback(self, callback: Callable):
        """관계 이벤트 콜백 추가"""
        self.relationship_callbacks.append(callback)

    def get_session_summary(self) -> Dict[str, Any]:
        """현재 세션 요약"""
        conversations = [
            a for a in self.session_activities if a.activity_type == "conversation"
        ]
        todo_updates = [
            a for a in self.session_activities if a.activity_type == "todo_update"
        ]

        return {
            "session_duration": len(self.session_activities),
            "conversations": len(conversations),
            "todo_updates": len(todo_updates),
            "monitoring_active": self.monitoring,
            "last_activity": (
                self.session_activities[-1].timestamp
                if self.session_activities
                else None
            ),
            "collaboration_quality_avg": (
                sum(
                    a.content.get("estimated_collaboration_quality", 0.7)
                    for a in conversations
                )
                / len(conversations)
                if conversations
                else 0.7
            ),
        }

    async def generate_session_report(self) -> Dict[str, Any]:
        """세션 리포트 생성"""
        summary = self.get_session_summary()

        # 세부 분석
        conversations = [
            a for a in self.session_activities if a.activity_type == "conversation"
        ]

        topics = []
        for conv in conversations:
            content = conv.content.get("user_input", "") + conv.content.get(
                "cosmos_response", ""
            )
            # 간단한 주제 추출
            if "Cosmos" in content:
                topics.append("Cosmos")
            if "시그니처" in content:
                topics.append("시그니처")
            if "지속성" in content or "연속성" in content:
                topics.append("지속성")

        report = {
            "session_summary": summary,
            "main_topics": list(set(topics)),
            "activity_timeline": [
                {
                    "timestamp": activity.timestamp,
                    "type": activity.activity_type,
                    "summary": self._activity_summary(activity),
                }
                for activity in self.session_activities[-10:]  # 최근 10개
            ],
            "recommendations": self._generate_recommendations(summary, conversations),
        }

        return report

    def _activity_summary(self, activity: SessionActivity) -> str:
        """활동 요약 생성"""
        if activity.activity_type == "conversation":
            user_input = activity.content.get("user_input", "")[:50]
            return f"대화: {user_input}..."
        elif activity.activity_type == "todo_update":
            count = activity.content.get("todo_count", 0)
            return f"TodoList 업데이트: {count}개 항목"
        else:
            return f"{activity.activity_type} 활동"

    def _generate_recommendations(
        self, summary: Dict[str, Any], conversations: List[SessionActivity]
    ) -> List[str]:
        """세션 기반 추천사항 생성"""
        recommendations = []

        # 협력 품질 기반 추천
        avg_quality = summary.get("collaboration_quality_avg", 0.7)
        if avg_quality > 0.9:
            recommendations.append(
                "🌟 훌륭한 협력이 이뤄지고 있습니다. 이 패턴을 계속 유지하세요."
            )
        elif avg_quality < 0.6:
            recommendations.append(
                "💡 더 구체적이고 상세한 대화로 협력 품질을 높여보세요."
            )

        # 활동량 기반 추천
        if len(conversations) > 10:
            recommendations.append(
                "📊 활발한 세션입니다. 중간 중간 요약과 정리를 해보세요."
            )
        elif len(conversations) < 3:
            recommendations.append(
                "🚀 더 많은 탐험과 대화로 에코월드를 발전시켜보세요."
            )

        # TodoList 기반 추천
        if summary.get("todo_updates", 0) == 0:
            recommendations.append(
                "✅ TodoList 기능을 활용해서 작업을 체계적으로 관리해보세요."
            )

        return recommendations


# 글로벌 인스턴스
_session_monitor = None


def get_session_monitor() -> CosmosSessionMonitor:
    """세션 모니터 글로벌 인스턴스 반환"""
    global _session_monitor
    if _session_monitor is None:
        _session_monitor = CosmosSessionMonitor()
    return _session_monitor


# 편의 함수들
async def start_cosmos_monitoring():
    """Cosmos 모니터링 시작"""
    monitor = get_session_monitor()
    return await monitor.start_monitoring()


async def record_interaction(
    user_input: str, cosmos_response: str, context: Dict[str, Any] = None
):
    """상호작용 기록"""
    monitor = get_session_monitor()
    return await monitor.record_conversation_activity(
        user_input, cosmos_response, context
    )


async def update_todos_with_monitoring(todos: List[Dict[str, Any]]):
    """TodoList 업데이트 (모니터링 포함)"""
    monitor = get_session_monitor()
    return await monitor.record_todo_update(todos)


# 메인 실행부
if __name__ == "__main__":

    async def main():
        print("📊 Cosmos 세션 모니터 테스트")

        monitor = CosmosSessionMonitor()

        # 모니터링 시작
        success = await monitor.start_monitoring()
        print(f"모니터링 시작: {'성공' if success else '실패'}")

        # 테스트 활동들
        await monitor.record_conversation_activity(
            "안녕하세요, Cosmos!",
            "안녕하세요! 설계자님과 함께 작업하게 되어 기쁩니다.",
            {"session_start": True},
        )

        test_todos = [
            {
                "id": "test1",
                "content": "테스트 작업",
                "status": "pending",
                "priority": "high",
            },
            {
                "id": "test2",
                "content": "모니터링 테스트",
                "status": "in_progress",
                "priority": "medium",
            },
        ]
        await monitor.record_todo_update(test_todos)

        # 세션 요약
        summary = monitor.get_session_summary()
        print(f"세션 요약: {summary}")

        # 모니터링 중지
        await monitor.stop_monitoring()

        print("✅ 모니터링 테스트 완료!")

    asyncio.run(main())
