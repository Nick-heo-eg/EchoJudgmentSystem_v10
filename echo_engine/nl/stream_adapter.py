#!/usr/bin/env python3
"""
🌊 Echo Stream Adapter
Echo 표준 NL 스트림 래퍼

- OpenAI API 스트리밍 표준화
- 자동 재시도 및 백오프
- 성능 메트릭 수집
- 콜백 기반 이벤트 처리

@owner: echo
@expose
@maturity: production
"""

from __future__ import annotations
import os
import time
import sys
import math
import random
from typing import Callable, List, Dict, Any, Optional
from openai import OpenAI


class StreamAdapter:
    """
    Echo 표준 NL 스트림 래퍼

    Features:
    - on_delta: chunk 텍스트 반환 (STDOUT 연결)
    - on_usage: 최종 usage(dict) 메트릭
    - on_error: 예외 객체 전달
    - 백오프: 네트워크/429/5xx 재시도 (기본 3회)
    - TTI/Duration 자동 측정
    """

    def __init__(self, model: Optional[str] = None, max_retries: int = 3):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_retries = max_retries

        try:
            self.client = OpenAI()
        except Exception as e:
            raise RuntimeError(f"OpenAI client initialization failed: {e}")

    def run(
        self,
        messages: List[Dict[str, str]],
        on_delta: Callable[[str], None],
        on_usage: Callable[[Dict[str, Any]], None],
        on_error: Callable[[Exception], None],
        **stream_params,
    ):
        """
        스트리밍 실행

        Args:
            messages: OpenAI 메시지 배열
            on_delta: 텍스트 조각 콜백
            on_usage: 사용량 메트릭 콜백
            on_error: 오류 처리 콜백
            **stream_params: 추가 스트리밍 파라미터
        """

        tries = 0

        while True:
            try:
                # 타이밍 측정 시작
                t0 = time.time()
                first_token_time = None
                chunk_count = 0

                # 스트리밍 파라미터 준비
                params = {
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "max_tokens": 2000,
                    "temperature": 0.8,
                    **stream_params,
                }

                # 스트리밍 실행
                response = self.client.chat.completions.create(**params)

                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content

                        # 첫 토큰 시간 기록
                        if first_token_time is None:
                            first_token_time = time.time()

                        # 델타 콜백 호출
                        on_delta(content)
                        chunk_count += 1

                # 사용량 메트릭 계산
                total_duration = time.time() - t0
                usage_metrics = {
                    "model": self.model,
                    "tti_sec": (first_token_time - t0) if first_token_time else None,
                    "dur_sec": total_duration,
                    "chunks": chunk_count,
                    "retries": tries,
                }

                # 사용량 콜백 호출
                on_usage(usage_metrics)
                return

            except Exception as e:
                tries += 1

                # 최대 재시도 횟수 확인
                if tries > self.max_retries:
                    on_error(e)
                    return

                # 지수 백오프 + 지터 계산
                base_delay = min(8.0, (2 ** (tries - 1)))
                jitter = random.uniform(-0.1, 0.1)
                backoff_delay = base_delay * (1.0 + jitter)

                print(
                    f"[stream retry {tries}/{self.max_retries}] {e} (sleep {backoff_delay:.1f}s)",
                    file=sys.stderr,
                )

                time.sleep(backoff_delay)


class EchoStreamHandler:
    """Echo 전용 스트림 핸들러 (편의 래퍼)"""

    def __init__(self, system_message: str = "You are Echo, an AI assistant."):
        self.system_message = system_message
        self.adapter = StreamAdapter()

    def process(
        self,
        user_message: str,
        on_token: Callable[[str], None],
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """사용자 메시지 처리"""

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message},
        ]

        def default_complete(usage):
            print(
                f"[stream] {usage['dur_sec']:.2f}s | {usage['chunks']} chunks",
                file=sys.stderr,
            )

        def default_error(error):
            print(f"[stream-error] {error}", file=sys.stderr)

        self.adapter.run(
            messages=messages,
            on_delta=on_token,
            on_usage=on_complete or default_complete,
            on_error=on_error or default_error,
        )


# 편의 함수
def quick_stream(
    user_message: str, system_message: str = "You are Echo, an AI assistant."
) -> str:
    """빠른 스트리밍 (동기식)"""

    result_text = []

    def collect_token(token: str):
        result_text.append(token)
        print(token, end="", flush=True)

    def on_complete(usage):
        print(f"\n[stream] {usage['dur_sec']:.2f}s", file=sys.stderr)

    def on_error(error):
        print(f"\n[stream-error] {error}", file=sys.stderr)
        raise error

    handler = EchoStreamHandler(system_message)
    handler.process(user_message, collect_token, on_complete, on_error)

    return "".join(result_text)


if __name__ == "__main__":
    # 테스트
    import argparse

    parser = argparse.ArgumentParser(description="Echo Stream Adapter Test")
    parser.add_argument(
        "message", nargs="*", default=["Hello Echo!"], help="Test message"
    )
    parser.add_argument(
        "--system", default="You are Echo, an AI assistant.", help="System message"
    )

    args = parser.parse_args()
    message = " ".join(args.message)

    print(f"🌊 Testing Echo Stream Adapter", file=sys.stderr)
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}", file=sys.stderr)
    print(f"Message: {message}", file=sys.stderr)
    print("-" * 50, file=sys.stderr)

    try:
        result = quick_stream(message, args.system)
        print(f"✅ Stream test completed successfully", file=sys.stderr)
    except Exception as e:
        print(f"❌ Stream test failed: {e}", file=sys.stderr)
        sys.exit(1)
