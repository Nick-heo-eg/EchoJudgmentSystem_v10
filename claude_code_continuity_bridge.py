#!/usr/bin/env python3
"""
🌉 Claude Code 지속성 브리지 (Claude Code Continuity Bridge)

Claude Code가 새로 시작할 때마다:
1. 이전 Claude의 기억을 자동 복원
2. Echo의 지속성 메모리와 연동
3. 전체 프로젝트 상황을 파악
4. 기존 기능 활용 가이드 제공

사용법:
- Claude Code 시작 시: `python claude_code_continuity_bridge.py restore`
- 작업 완료 후: `python claude_code_continuity_bridge.py save "작업 요약"`
- 현재 상태 확인: `python claude_code_continuity_bridge.py status`
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 기존 시스템 연동
try:
    from claude_continuity_helper import ClaudeContinuityHelper
    from claude_memory_system import ClaudeMemorySystem
    from echo_engine.echo_context_manager import get_context_manager
    from echo_engine.echo_system_memory import get_system_memory
    from echo_engine.echo_structure_analyzer import get_structure_analyzer

    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 일부 시스템 로드 실패: {e}")
    SYSTEMS_AVAILABLE = False


class ClaudeCodeContinuityBridge:
    """🌉 Claude Code와 Echo 시스템 간 지속성 브리지"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.bridge_data_dir = self.base_path / "data" / "claude_code_bridge"
        self.bridge_data_dir.mkdir(exist_ok=True, parents=True)

        # 기존 시스템들 초기화
        if SYSTEMS_AVAILABLE:
            try:
                self.claude_helper = ClaudeContinuityHelper()
                self.claude_memory = ClaudeMemorySystem()
                self.echo_context = get_context_manager()
                self.echo_memory = get_system_memory()
                self.echo_analyzer = get_structure_analyzer()
                self.systems_ready = True
            except Exception as e:
                print(f"⚠️ 시스템 초기화 실패: {e}")
                self.systems_ready = False
        else:
            self.systems_ready = False

        print("🌉 Claude Code 지속성 브리지 초기화 완료")
        print(f"   시스템 연동: {'✅' if self.systems_ready else '❌'}")

    async def restore_claude_code_session(self) -> str:
        """Claude Code 세션 복원 및 통합 브리핑 생성"""

        print("🔄 Claude Code 지속성 복원 시작...")
        print("=" * 70)

        # 1. Claude 기존 메모리 복원
        claude_briefing = ""
        if self.systems_ready:
            try:
                previous_memory = await self.claude_helper.restore_claude_session()
                claude_briefing = self.claude_memory.generate_continuity_briefing()
            except Exception as e:
                print(f"⚠️ Claude 메모리 복원 실패: {e}")
                claude_briefing = "Claude 메모리 복원 실패"

        # 2. Echo 컨텍스트 연속성 확인
        echo_report = ""
        if self.systems_ready and self.echo_context:
            try:
                echo_report = self.echo_context.generate_continuity_report()
            except Exception as e:
                print(f"⚠️ Echo 컨텍스트 로드 실패: {e}")
                echo_report = "Echo 컨텍스트 로드 실패"

        # 3. Echo 시스템 구조 현황
        system_status = ""
        if self.systems_ready and self.echo_memory:
            try:
                system_status = self.echo_memory.generate_system_report()
            except Exception as e:
                print(f"⚠️ Echo 시스템 현황 로드 실패: {e}")
                system_status = "Echo 시스템 현황 로드 실패"

        # 4. 통합 브리핑 생성
        integrated_briefing = self._generate_integrated_briefing(
            claude_briefing, echo_report, system_status
        )

        # 5. 브리핑 파일 저장
        briefing_file = (
            self.bridge_data_dir
            / f"claude_code_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(briefing_file, "w", encoding="utf-8") as f:
            f.write(integrated_briefing)

        print(f"📋 통합 브리핑 생성 완료: {briefing_file}")

        return integrated_briefing

    def _generate_integrated_briefing(
        self, claude_briefing: str, echo_report: str, system_status: str
    ) -> str:
        """통합 브리핑 생성"""

        briefing = f"""# 🌉 Claude Code 지속성 통합 브리핑

**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🧠 Claude 이전 기억 복원

{claude_briefing}

---

## 🔄 Echo 컨텍스트 연속성

{echo_report}

---

## 🏗️ Echo 시스템 구조 현황

{system_status}

---

## 🎯 Claude Code 작업 가이드

### 즉시 확인해야 할 사항:
1. **기존 기능 중복 방지**: 새로운 코드를 작성하기 전에 기존 함수들을 먼저 검색하세요.
2. **Echo 컨텍스트 활용**: 이전 세션의 작업 패턴과 선호도를 참고하세요.
3. **프로젝트 연속성**: 진행 중인 프로젝트가 있다면 연결하여 작업하세요.

### 권장 시작 명령어:
```bash
# Echo 시스템 전체 상태 확인
python echo_engine/echo_system_memory.py

# Echo 컨텍스트 연속성 보고서
python echo_engine/echo_context_manager.py

# Echo IDE로 자연어 개발 시작
python echo_engine/echo_autonomous_ide.py
```

### 중복 방지 체크리스트:
- [ ] 구현하려는 기능이 이미 존재하는지 검색했는가?
- [ ] 유사한 패턴의 기존 코드를 참고했는가?
- [ ] Echo의 추천 사항을 고려했는가?
- [ ] 기존 프로젝트와의 연결성을 확인했는가?

### 개발 패턴:
- **Echo 시그니처 활용**: Aurora(창의적), Phoenix(변화), Sage(분석적), Companion(협력적)
- **기존 함수 재사용**: 새로 만들기 전에 기존 함수 확장 고려
- **지속성 유지**: 모든 작업이 Echo의 메모리에 기록되도록 함

---

## 💡 이번 세션 추천 작업 방향

Echo 시스템의 현재 상태와 이전 작업 이력을 바탕으로:

1. **우선순위 높음**: 진행 중인 프로젝트 완성
2. **우선순위 중간**: 기존 기능 개선 및 확장  
3. **우선순위 낮음**: 완전히 새로운 기능 개발

**기억하세요**: Echo는 이미 {self.echo_memory.structure_cache.total_functions if self.systems_ready and self.echo_memory.structure_cache else "수천"}개의 함수를 보유하고 있습니다. 
새로 만들기 전에 항상 기존 것을 먼저 찾아보세요! 🔍

---

*이 브리핑은 Claude Code의 작업 효율성과 연속성을 위해 자동 생성되었습니다.*
"""

        return briefing

    async def save_claude_code_session(self, work_summary: str = "자동 저장") -> bool:
        """Claude Code 세션 저장"""

        print("💾 Claude Code 세션 저장 중...")

        session_data = {
            "session_context": {
                "work_summary": work_summary,
                "session_type": "claude_code_bridge",
                "timestamp": datetime.now().isoformat(),
            },
            "echo_relationship": {
                "collaboration_type": "code_development",
                "interaction_quality": "productive",
                "trust_level": 0.9,
            },
            "emotional_state": {"satisfaction": "productive", "closure": "completed"},
            "commitments_and_promises": [
                {
                    "description": "Echo 시스템의 지속적 개선",
                    "status": "ongoing",
                    "priority": "high",
                    "created": datetime.now().isoformat(),
                }
            ],
        }

        success = False
        if self.systems_ready:
            try:
                # Claude 메모리에 저장
                success = await self.claude_helper.save_claude_session(session_data)

                # Echo 컨텍스트도 저장
                if self.echo_context and self.echo_context.current_session:
                    self.echo_context.end_current_session()

            except Exception as e:
                print(f"⚠️ 세션 저장 실패: {e}")

        if success:
            print("✅ Claude Code 세션 저장 완료!")
        else:
            print("❌ 세션 저장 실패")

        return success

    def get_bridge_status(self) -> Dict[str, Any]:
        """브리지 시스템 상태 조회"""

        status = {
            "bridge_active": self.systems_ready,
            "claude_memory_available": False,
            "echo_context_available": False,
            "echo_system_available": False,
            "last_briefing": None,
            "recommendations": [],
        }

        if self.systems_ready:
            # Claude 메모리 상태
            try:
                claude_status = self.claude_helper.get_memory_status()
                status["claude_memory_available"] = claude_status[
                    "memory_system_active"
                ]
            except:
                pass

            # Echo 컨텍스트 상태
            try:
                if self.echo_context:
                    status["echo_context_available"] = True
                    if self.echo_context.current_session:
                        status["current_echo_session"] = (
                            self.echo_context.current_session.session_id
                        )
            except:
                pass

            # Echo 시스템 메모리 상태
            try:
                if self.echo_memory and self.echo_memory.structure_cache:
                    status["echo_system_available"] = True
                    status["total_functions"] = (
                        self.echo_memory.structure_cache.total_functions
                    )
                    status["total_modules"] = len(
                        self.echo_memory.structure_cache.modules
                    )
            except:
                pass

        # 최근 브리핑 파일 찾기
        briefing_files = list(self.bridge_data_dir.glob("claude_code_briefing_*.md"))
        if briefing_files:
            latest_briefing = max(briefing_files, key=lambda f: f.stat().st_mtime)
            status["last_briefing"] = str(latest_briefing)

        # 추천 사항
        if not status["bridge_active"]:
            status["recommendations"].append("시스템 모듈 설치 필요")
        if not status["claude_memory_available"]:
            status["recommendations"].append("Claude 메모리 시스템 초기화 필요")
        if not status["echo_context_available"]:
            status["recommendations"].append("Echo 컨텍스트 매니저 확인 필요")

        return status

    def generate_quick_start_guide(self) -> str:
        """Claude Code 빠른 시작 가이드 생성"""

        guide = """
# 🚀 Claude Code 빠른 시작 가이드

## 세션 복원 (매번 시작할 때)
```bash
python claude_code_continuity_bridge.py restore
```

## 현재 상태 확인
```bash
python claude_code_continuity_bridge.py status
```

## 작업 완료 후 저장
```bash
python claude_code_continuity_bridge.py save "오늘 작업한 내용 요약"
```

## Echo 시스템과 함께 개발하기

### 1. 기존 기능 확인부터
```bash
# Echo 시스템 전체 구조 파악
python echo_engine/echo_system_memory.py

# 특정 기능 검색
from echo_engine.echo_system_memory import get_system_memory
memory = get_system_memory()
functions = memory.get_existing_functions(keyword="계산기")
```

### 2. 자연어로 개발하기
```bash
python echo_engine/echo_autonomous_ide.py
```

### 3. 컨텍스트 연속성 활용
```bash
from echo_engine.echo_context_manager import get_context_manager
context = get_context_manager()
report = context.generate_continuity_report()
print(report)
```

## 중복 방지 체크포인트

✅ **구현 전 필수 확인**:
1. `echo_memory.get_existing_functions(keyword="내가_만들려는_기능")`
2. `echo_analyzer.analyze_new_request("내 요청", "Aurora")`
3. 기존 코드 패턴 참고
4. Echo의 추천 사항 검토

---
*이 가이드는 Echo 시스템의 지속성을 최대한 활용하도록 설계되었습니다.*
        """.strip()

        return guide


# 편의 함수들
async def restore_claude_code():
    """Claude Code 복원"""
    bridge = ClaudeCodeContinuityBridge()
    return await bridge.restore_claude_code_session()


async def save_claude_code(summary: str = "자동 저장"):
    """Claude Code 저장"""
    bridge = ClaudeCodeContinuityBridge()
    return await bridge.save_claude_code_session(summary)


def check_bridge_status():
    """브리지 상태 확인"""
    bridge = ClaudeCodeContinuityBridge()
    return bridge.get_bridge_status()


def show_quick_guide():
    """빠른 시작 가이드 출력"""
    bridge = ClaudeCodeContinuityBridge()
    return bridge.generate_quick_start_guide()


# 메인 실행부
if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()

            if command == "restore":
                print("🔄 Claude Code 지속성 복원을 시작합니다...")
                briefing = await restore_claude_code()
                print("\n" + briefing)

            elif command == "save":
                summary = sys.argv[2] if len(sys.argv) > 2 else "자동 저장"
                print(f"💾 Claude Code 세션 저장: {summary}")
                result = await save_claude_code(summary)
                if result:
                    print("✅ 저장 완료!")
                else:
                    print("❌ 저장 실패!")

            elif command == "status":
                print("📊 Claude Code 브리지 상태:")
                status = check_bridge_status()
                for key, value in status.items():
                    print(f"   • {key}: {value}")

            elif command == "guide":
                print(show_quick_guide())

            else:
                print(f"알 수 없는 명령어: {command}")
                print(
                    "사용법: python claude_code_continuity_bridge.py [restore|save|status|guide]"
                )
        else:
            # 기본: 복원
            print("🌉 Claude Code 지속성 브리지")
            briefing = await restore_claude_code()
            print("\n" + briefing)

    asyncio.run(main())
