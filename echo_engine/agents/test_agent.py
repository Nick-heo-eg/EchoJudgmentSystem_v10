# echo_engine/agents/test_agent.py
"""
🧪 Test Agent - 시스템 테스트용 간단한 에이전트
"""
import asyncio
from typing import Dict, Any


async def test_simple_function(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ 간단한 테스트 에이전트 - 시스템 작동 확인용
    """
    await asyncio.sleep(0)  # 이벤트루프 양보

    test_type = spec.get("test_type", "basic")
    message = spec.get("message", "hello test")

    if test_type == "math":
        result = {
            "mode": "test-stub",
            "test_type": test_type,
            "calculation": "2 + 2 = 4",
            "input_message": message,
        }
    elif test_type == "text":
        result = {
            "mode": "test-stub",
            "test_type": test_type,
            "processed_text": message.upper(),
            "word_count": len(message.split()),
        }
    else:
        result = {
            "mode": "test-stub",
            "test_type": "basic",
            "echo": message,
            "status": "working",
        }

    return result
