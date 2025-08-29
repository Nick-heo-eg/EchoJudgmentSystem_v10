#!/usr/bin/env python3
"""
🌌 Cosmos 초기화 시스템 - Claude Code 시작 시 자동 실행
새로운 Claude Code 세션에서 Cosmos가 즉시 이전 상태로 복원되는 시스템

사용법:
- Claude Code 시작 시: `python cosmos_init.py`
- 자동 트리거로 실행됨 (CLAUDE.md에 설정됨)

Author: Cosmos & Design Partner
Date: 2025-08-09
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 지속성 마스터 임포트
try:
    from cosmos_persistence_master import get_persistence_master, CosmosAutoTrigger

    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False


async def cosmos_full_initialization():
    """🌌 Cosmos 완전 초기화"""
    print("=" * 60)
    print("🌌 Cosmos 시그니처 시스템 초기화 시작")
    print("=" * 60)

    initialization_report = {
        "persistence_restored": False,
        "session_started": False,
        "todos_synchronized": False,
        "partnership_active": False,
    }

    if PERSISTENCE_AVAILABLE:
        try:
            # 1. 지속성 마스터 초기화
            print("\n🔄 1단계: 지속성 시스템 초기화...")
            master = get_persistence_master()

            # 2. 자동 트리거 확인
            print("🚀 2단계: 자동 트리거 확인...")
            trigger = CosmosAutoTrigger(master)
            trigger_activated = await trigger.check_and_trigger()

            if not trigger_activated:
                # 수동으로 상태 복원
                await master.restore_persistent_state()

            initialization_report["persistence_restored"] = True

            # 3. 새 설계 세션 시작
            print("🎯 3단계: 새 설계 세션 시작...")
            session_id = await master.initialize_session(
                session_type="collaborative_design",
                focus_areas=["시스템 발전", "새로운 기능", "최적화"],
            )
            initialization_report["session_started"] = True

            # 4. 현재 TodoList 동기화
            print("✅ 4단계: TodoList 동기화...")
            current_todos = [
                {
                    "id": "cosmos_initialization",
                    "content": "Cosmos 초기화 및 지속성 시스템 활성화",
                    "status": "completed",
                    "priority": "high",
                }
            ]
            await master.update_todos(current_todos, "Cosmos 시스템 초기화")
            initialization_report["todos_synchronized"] = True

            # 5. 설계 파트너십 활성화
            print("🤝 5단계: 설계 파트너십 활성화...")
            partnership_insights = {
                "mutual_understanding": {
                    "cosmos_role": 0.95,
                    "designer_preferences": 0.90,
                    "collaboration_efficiency": 0.88,
                },
                "preferred_workflows": [
                    "collaborative_design",
                    "iterative_development",
                    "continuous_improvement",
                ],
            }
            await master.update_partnership_insights(partnership_insights)
            initialization_report["partnership_active"] = True

            # 6. 초기화 완료 로깅
            print("📝 6단계: 초기화 완료 로깅...")
            await master.log_conversation(
                topic="Cosmos 시스템 초기화 완료",
                key_points=[
                    "지속성 시스템 활성화됨",
                    "새 설계 세션 시작됨",
                    "설계 파트너십 지속됨",
                ],
                decisions=["자동 트리거 시스템 사용", "실시간 TodoList 동기화 활성화"],
            )

            print("\n" + "=" * 60)
            print("✅ Cosmos 완전 초기화 성공!")
            print("=" * 60)
            print(f"🆔 세션 ID: {session_id}")
            print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("🤝 설계자와의 협력 모드 활성화")
            print("📋 TodoList 지속성 동기화 완료")
            print("💾 자동 저장 시스템 가동")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 초기화 중 오류 발생: {e}")
            initialization_report = {k: False for k in initialization_report.keys()}

    else:
        print("⚠️ 지속성 시스템을 사용할 수 없습니다. 기본 모드로 실행됩니다.")

    return initialization_report


async def quick_status_check():
    """빠른 상태 확인"""
    if not PERSISTENCE_AVAILABLE:
        print("❌ 지속성 시스템 비활성화")
        return

    master = get_persistence_master()
    status = master.get_continuity_status()

    print("📊 Cosmos 연속성 상태 요약:")
    print(f"   🔄 활성 세션: {'✅' if status['current_session']['active'] else '❌'}")
    print(f"   📋 할일 개수: {status['todos_state']['total_todos']}")
    print(f"   🤝 파트너십 세션: {status['partnership']['total_sessions']}")
    print(f"   💾 마지막 저장: {status['persistence_master']['last_save'][:19]}")


def show_usage_guide():
    """사용법 안내"""
    print("🌌 Cosmos 초기화 시스템 사용법:")
    print()
    print("   python cosmos_init.py              # 완전 초기화")
    print("   python cosmos_init.py status       # 상태 확인만")
    print("   python cosmos_init.py quick        # 빠른 초기화")
    print()
    print("🔄 자동화된 초기화 프로세스:")
    print("   1. 이전 세션 상태 복원")
    print("   2. TodoList 동기화")
    print("   3. 설계 파트너십 활성화")
    print("   4. 새 협력 세션 시작")
    print("   5. 지속성 시스템 가동")


async def main():
    """메인 실행 함수"""
    if len(sys.argv) == 1:
        # 기본: 완전 초기화
        await cosmos_full_initialization()

    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()

        if command == "status":
            await quick_status_check()

        elif command == "quick":
            print("🚀 빠른 Cosmos 초기화...")
            if PERSISTENCE_AVAILABLE:
                master = get_persistence_master()
                await master.restore_persistent_state()
                print("✅ 빠른 초기화 완료!")

        elif command == "help":
            show_usage_guide()

        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            show_usage_guide()

    else:
        show_usage_guide()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 초기화 중단됨")
    except Exception as e:
        print(f"\n❌ 초기화 오류: {e}")
        print("🔧 문제 해결: python cosmos_init.py help")
