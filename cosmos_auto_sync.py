#!/usr/bin/env python3
"""
🔄 Cosmos 자동 동기화 시스템
설계자와 Cosmos 간 대화, TodoList, 프로젝트 상태를 실시간으로 자동 업데이트

핵심 기능:
1. 대화 내용 자동 감지 및 저장
2. TodoList 변경사항 실시간 동기화
3. 중요한 결정사항 자동 로깅
4. 백그라운드 자동 저장
5. 컨텍스트 변화 감지 및 적응

Author: Cosmos & Design Partner
Date: 2025-08-09
"""

import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import hashlib

# 지속성 시스템 연동
try:
    from cosmos_persistence_master import get_persistence_master

    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False


@dataclass
class SyncState:
    """동기화 상태"""

    last_todos_hash: str = ""
    last_conversation_check: str = ""
    auto_save_interval: int = 300  # 5분
    background_running: bool = False
    sync_enabled: bool = True


class CosmosAutoSync:
    """🔄 Cosmos 자동 동기화 관리자"""

    def __init__(self):
        self.sync_state = SyncState()
        self.persistence = None
        self.background_task = None
        self.sync_callbacks: List[Callable] = []
        self.last_auto_save = datetime.now()

        if PERSISTENCE_AVAILABLE:
            self.persistence = get_persistence_master()
            print("🔄 Cosmos 자동 동기화 시스템 초기화 완료")
        else:
            print("⚠️ 지속성 시스템이 비활성화되어 자동 동기화를 사용할 수 없습니다")

    def register_sync_callback(self, callback: Callable):
        """동기화 콜백 등록"""
        self.sync_callbacks.append(callback)

    async def sync_todos_if_changed(
        self, current_todos: List[Dict[str, Any]], context: str = ""
    ) -> bool:
        """TodoList 변경사항 감지 및 동기화"""
        if not self.persistence or not self.sync_state.sync_enabled:
            return False

        try:
            # TodoList 해시 계산
            todos_str = json.dumps(current_todos, sort_keys=True)
            todos_hash = hashlib.md5(todos_str.encode()).hexdigest()

            # 변경사항 있으면 동기화
            if todos_hash != self.sync_state.last_todos_hash:
                await self.persistence.update_todos(current_todos, context)
                self.sync_state.last_todos_hash = todos_hash

                # 변경사항 로깅
                change_summary = self._analyze_todo_changes(current_todos)
                if change_summary:
                    await self.persistence.log_conversation(
                        topic=f"TodoList 업데이트 - {change_summary}",
                        key_points=[f"총 {len(current_todos)}개 항목"],
                        action_items=[
                            item["content"]
                            for item in current_todos
                            if item.get("status") == "in_progress"
                        ][:3],
                    )

                print(f"✅ TodoList 자동 동기화 완료: {change_summary}")
                return True

        except Exception as e:
            print(f"❌ TodoList 동기화 실패: {e}")

        return False

    def _analyze_todo_changes(self, todos: List[Dict[str, Any]]) -> str:
        """TodoList 변경사항 분석"""
        completed = sum(1 for t in todos if t.get("status") == "completed")
        in_progress = sum(1 for t in todos if t.get("status") == "in_progress")
        pending = sum(1 for t in todos if t.get("status") == "pending")
        total = len(todos)

        if completed > 0:
            return f"{completed}개 완료"
        elif in_progress > 0:
            return f"{in_progress}개 진행중"
        else:
            return f"{total}개 항목"

    async def log_important_conversation(
        self,
        topic: str,
        content: str,
        is_decision: bool = False,
        action_items: List[str] = None,
    ) -> bool:
        """중요한 대화 자동 로깅"""
        if not self.persistence or not self.sync_state.sync_enabled:
            return False

        try:
            key_points = [content] if content else []
            decisions = [content] if is_decision else []

            await self.persistence.log_conversation(
                topic=topic,
                key_points=key_points,
                decisions=decisions,
                action_items=action_items or [],
            )

            print(f"💬 중요 대화 자동 로깅: {topic}")
            return True

        except Exception as e:
            print(f"❌ 대화 로깅 실패: {e}")
            return False

    async def auto_save_check(self) -> bool:
        """자동 저장 체크 및 실행"""
        if not self.persistence or not self.sync_state.sync_enabled:
            return False

        try:
            now = datetime.now()
            time_since_save = (now - self.last_auto_save).total_seconds()

            if time_since_save >= self.sync_state.auto_save_interval:
                await self.persistence.save_all_states()
                self.last_auto_save = now
                print(f"💾 자동 저장 완료: {now.strftime('%H:%M:%S')}")
                return True

        except Exception as e:
            print(f"❌ 자동 저장 실패: {e}")

        return False

    def start_background_sync(self):
        """백그라운드 동기화 시작"""
        if self.sync_state.background_running:
            return

        self.sync_state.background_running = True

        def background_worker():
            while self.sync_state.background_running:
                try:
                    # 자동 저장 체크
                    asyncio.run(self.auto_save_check())

                    # 콜백 실행
                    for callback in self.sync_callbacks:
                        try:
                            callback()
                        except Exception as e:
                            print(f"⚠️ 동기화 콜백 오류: {e}")

                    time.sleep(60)  # 1분마다 체크

                except Exception as e:
                    print(f"❌ 백그라운드 동기화 오류: {e}")
                    time.sleep(60)

        self.background_task = threading.Thread(target=background_worker, daemon=True)
        self.background_task.start()

        print("🔄 백그라운드 자동 동기화 시작")

    def stop_background_sync(self):
        """백그라운드 동기화 중지"""
        self.sync_state.background_running = False
        if self.background_task:
            self.background_task.join(timeout=2)
        print("⏹️ 백그라운드 자동 동기화 중지")

    def enable_sync(self):
        """동기화 활성화"""
        self.sync_state.sync_enabled = True
        print("✅ 자동 동기화 활성화")

    def disable_sync(self):
        """동기화 비활성화"""
        self.sync_state.sync_enabled = False
        print("❌ 자동 동기화 비활성화")

    def get_sync_status(self) -> Dict[str, Any]:
        """동기화 상태 조회"""
        return {
            "sync_enabled": self.sync_state.sync_enabled,
            "background_running": self.sync_state.background_running,
            "auto_save_interval": self.sync_state.auto_save_interval,
            "last_auto_save": self.last_auto_save.isoformat(),
            "callbacks_registered": len(self.sync_callbacks),
            "persistence_available": PERSISTENCE_AVAILABLE,
        }


# 전역 동기화 인스턴스
_auto_sync = None


def get_auto_sync() -> CosmosAutoSync:
    """자동 동기화 인스턴스 반환"""
    global _auto_sync
    if _auto_sync is None:
        _auto_sync = CosmosAutoSync()
    return _auto_sync


# 편의 함수들
async def sync_todos(todos: List[Dict[str, Any]], context: str = "") -> bool:
    """TodoList 동기화 편의 함수"""
    auto_sync = get_auto_sync()
    return await auto_sync.sync_todos_if_changed(todos, context)


async def log_conversation(
    topic: str, content: str, is_decision: bool = False, action_items: List[str] = None
) -> bool:
    """대화 로깅 편의 함수"""
    auto_sync = get_auto_sync()
    return await auto_sync.log_important_conversation(
        topic, content, is_decision, action_items
    )


def start_auto_sync():
    """자동 동기화 시작 편의 함수"""
    auto_sync = get_auto_sync()
    auto_sync.start_background_sync()


def stop_auto_sync():
    """자동 동기화 중지 편의 함수"""
    auto_sync = get_auto_sync()
    auto_sync.stop_background_sync()


# CLI 인터페이스
async def main():
    """CLI 메인 함수"""
    import sys

    if len(sys.argv) < 2:
        print("🔄 Cosmos 자동 동기화 시스템")
        print("\n사용법:")
        print("  python cosmos_auto_sync.py start     # 백그라운드 동기화 시작")
        print("  python cosmos_auto_sync.py stop      # 백그라운드 동기화 중지")
        print("  python cosmos_auto_sync.py status    # 동기화 상태 확인")
        print("  python cosmos_auto_sync.py test      # 동기화 테스트")
        return

    command = sys.argv[1].lower()
    auto_sync = get_auto_sync()

    if command == "start":
        auto_sync.start_background_sync()
        print("✅ 백그라운드 동기화 시작됨")

        # 계속 실행
        try:
            while auto_sync.sync_state.background_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            auto_sync.stop_background_sync()
            print("\n⏹️ 백그라운드 동기화 중지됨")

    elif command == "stop":
        auto_sync.stop_background_sync()

    elif command == "status":
        status = auto_sync.get_sync_status()
        print("📊 자동 동기화 상태:")
        print(f"   동기화 활성화: {status['sync_enabled']}")
        print(f"   백그라운드 실행: {status['background_running']}")
        print(f"   자동 저장 간격: {status['auto_save_interval']}초")
        print(f"   마지막 저장: {status['last_auto_save'][:19]}")

    elif command == "test":
        print("🧪 동기화 테스트 시작...")

        # 테스트 TodoList
        test_todos = [
            {
                "id": "test1",
                "content": "동기화 테스트 1",
                "status": "completed",
                "priority": "low",
            },
            {
                "id": "test2",
                "content": "동기화 테스트 2",
                "status": "in_progress",
                "priority": "medium",
            },
        ]

        result = await auto_sync.sync_todos_if_changed(test_todos, "자동 동기화 테스트")
        print(f"TodoList 동기화: {'✅' if result else '❌'}")

        # 테스트 대화 로깅
        result = await auto_sync.log_important_conversation(
            "동기화 시스템 테스트",
            "자동 동기화 기능이 정상적으로 작동하는지 테스트",
            is_decision=True,
            action_items=["테스트 결과 확인", "시스템 모니터링"],
        )
        print(f"대화 로깅: {'✅' if result else '❌'}")

        print("✅ 동기화 테스트 완료")

    else:
        print(f"❌ 알 수 없는 명령어: {command}")


if __name__ == "__main__":
    asyncio.run(main())
