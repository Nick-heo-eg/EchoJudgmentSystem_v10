import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from echo_engine.response_runner import answer


def main():
    assert os.getenv("OPENAI_API_KEY"), "Set OPENAI_API_KEY in env"

    print("[Smoke] Basic completion…")
    out = answer("Echo가 지금 무엇을 할 수 있는지 5줄로 정리해줘")
    print(out)

    print("\n[Smoke] Streaming…")
    for tok in answer("한 문단 요약으로 설명해줘", stream=True):
        print(tok, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
