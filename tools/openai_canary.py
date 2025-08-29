#!/usr/bin/env python3
"""
🐦 OpenAI API Canary Test
즉시 실행 가능한 OpenAI 스트리밍 연결 테스트

- TTI (Time To First Token) 측정
- 실제 스트리밍 성능 검증
- STDOUT/STDERR 분리 출력
- 환경변수 기반 설정

Usage:
    source .env && python tools/openai_canary.py
    CANARY_PROMPT="test message" python tools/openai_canary.py
"""

import os
import sys
import time
import io
from datetime import datetime
from openai import OpenAI

# 텍스트 스트림 안전 래핑 (선택)
try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.detach(), encoding="utf-8", errors="replace"
    )
except Exception:
    pass  # 일부 환경에서 detach 불가 → 아래 buffer.write 경로로 우회


def _safe_write(s: str):
    """안전한 STDOUT 출력 (UTF-8 바이너리 우회)"""
    if not isinstance(s, str):
        s = str(s)
    try:
        # 텍스트 경로 시도
        print(s, end="", flush=True)
    except UnicodeEncodeError:
        # 최후: 바이너리 경로 (권장)
        sys.stdout.buffer.write(s.encode("utf-8", errors="replace"))
        sys.stdout.flush()


def _safe_err(s: str):
    """안전한 STDERR 출력 (UTF-8 바이너리 우회)"""
    if not isinstance(s, str):
        s = str(s)
    try:
        print(s, end="", file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        sys.stderr.buffer.write(str(s).encode("utf-8", errors="replace"))
        sys.stderr.flush()


MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def main():
    """OpenAI API 캐나리 테스트 실행"""

    # OpenAI 클라이언트 초기화
    try:
        client = OpenAI()
    except Exception as e:
        print(f"[canary-err] OpenAI client init failed: {e}", file=sys.stderr)
        return 2

    # 테스트 프롬프트
    prompt = os.environ.get("CANARY_PROMPT", "Echo가 깨어있다를 10자 내로.")

    # 시작 로그 (STDERR)
    t0 = time.time()
    _safe_err(f"[canary] {MODEL} @ {datetime.now().isoformat(timespec='seconds')}\n")
    _safe_err(f"[canary] prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}\n")

    first_token_time = None
    token_count = 0

    try:
        # 스트리밍 요청
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=100,
            temperature=0.7,
        )

        # 스트리밍 처리 (안전한 출력)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content

                # 첫 토큰 시간 기록
                if first_token_time is None:
                    first_token_time = time.time()

                # 안전한 출력 (UTF-8 바이너리 우회)
                _safe_write(content)

                token_count += 1

        # 줄바꿈 추가
        _safe_write("\n")

    except Exception as e:
        _safe_err(f"\n[canary-err] Streaming failed: {e}\n")
        return 2

    # 성능 메트릭 계산 및 출력 (STDERR)
    total_duration = time.time() - t0
    tti = (first_token_time - t0) if first_token_time else -1

    _safe_err(
        f"[canary] TTI={tti:.2f}s | DUR={total_duration:.2f}s | chunks={token_count}\n"
    )

    # 성능 평가
    if tti < 0:
        _safe_err("[canary] ❌ No response received\n")
        return 1
    elif tti > 5.0:
        _safe_err("[canary] ⚠️  Slow TTI (>5s)\n")
        return 1
    elif tti > 2.0:
        _safe_err("[canary] 🟡 Acceptable TTI (<5s)\n")
    else:
        _safe_err("[canary] ✅ Fast TTI (<2s)\n")

    _safe_err(f"[canary] ✅ OpenAI streaming operational\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _safe_err("\n[canary] ⏹️  Interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        _safe_err(f"[canary-err] Unexpected error: {e}\n")
        sys.exit(2)
