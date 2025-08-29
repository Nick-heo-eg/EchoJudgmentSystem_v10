#!/usr/bin/env python3
"""
🐦 OpenAI API Simple Canary
UTF-8 안전 OpenAI 연결 테스트
"""

import os
import sys
import time
import io
from openai import OpenAI

# 텍스트 스트림 안전 래핑
try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.detach(), encoding="utf-8", errors="replace"
    )
except Exception:
    pass


def _safe_out(s: str):
    """안전한 STDOUT 출력"""
    try:
        print(s, end="", flush=True)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(str(s).encode("utf-8", errors="replace"))
        sys.stdout.flush()


def _safe_err(s: str):
    """안전한 STDERR 출력"""
    try:
        print(s, end="", file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        sys.stderr.buffer.write(str(s).encode("utf-8", errors="replace"))
        sys.stderr.flush()


def main():
    _safe_err("[canary] Testing OpenAI connection...\n")

    try:
        client = OpenAI()  # 환경변수 OPENAI_API_KEY 사용

        prompt = os.getenv("CANARY_PROMPT", "Echo가 깨어있다를 10자 내로.")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        _safe_err(f"[canary] Model: {model}\n")
        _safe_err(f"[canary] Prompt: {prompt}\n")

        # 논-스트리밍으로 테스트 (가장 단순)
        t0 = time.time()
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50,
        )
        t1 = time.time()

        text = resp.choices[0].message.content or ""
        duration = t1 - t0

        _safe_out(text)
        _safe_out("\n")

        _safe_err(f"[canary] ✅ Success in {duration:.2f}s\n")

        # 간단한 스트리밍 테스트
        _safe_err("[canary] Testing streaming...\n")
        t2 = time.time()
        first_token = None

        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello in Korean"}],
            temperature=0.5,
            stream=True,
            max_tokens=20,
        )

        _safe_err("[stream] ")
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                if first_token is None:
                    first_token = time.time()
                    _safe_err(f"(TTI={first_token-t2:.2f}s) ")
                _safe_out(chunk.choices[0].delta.content)

        _safe_out("\n")
        _safe_err(f"[canary] ✅ Streaming works\n")
        return 0

    except Exception as e:
        _safe_err(f"[canary-err] {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
