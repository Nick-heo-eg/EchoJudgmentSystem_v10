#!/usr/bin/env python3
"""
Echo 타임아웃 유틸리티
외부 호출 및 무거운 작업의 타임아웃 관리
"""

import asyncio
import functools
import logging
from typing import Any, Awaitable, Callable, Optional, TypeVar
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_timeout(
    coro: Awaitable[T], seconds: float = 15.0, fallback: Optional[T] = None
) -> T:
    """
    코루틴을 타임아웃과 함께 실행

    Args:
        coro: 실행할 코루틴
        seconds: 타임아웃 시간 (초)
        fallback: 타임아웃 시 반환할 기본값

    Returns:
        코루틴 결과 또는 fallback

    Raises:
        asyncio.TimeoutError: fallback이 None이고 타임아웃 발생시
    """
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {seconds}s")
        if fallback is not None:
            return fallback
        raise


def run_blocking(func: Callable[..., T], *args, **kwargs) -> Awaitable[T]:
    """
    동기 함수를 비동기 컨텍스트에서 실행

    Args:
        func: 실행할 동기 함수
        *args, **kwargs: 함수 인자

    Returns:
        함수 실행 결과의 awaitable
    """
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


class TimeoutManager:
    """타임아웃 관리자"""

    def __init__(self, default_timeout: float = 15.0):
        self.default_timeout = default_timeout
        self.timeouts = {
            "llm_call": 30.0,
            "file_operation": 10.0,
            "network_request": 15.0,
            "database_query": 5.0,
            "health_check": 1.0,
        }

    async def execute_with_timeout(
        self, operation_type: str, coro: Awaitable[T], fallback: Optional[T] = None
    ) -> T:
        """
        작업 타입에 따른 타임아웃으로 실행

        Args:
            operation_type: 작업 타입 키
            coro: 실행할 코루틴
            fallback: 타임아웃 시 기본값

        Returns:
            실행 결과
        """
        timeout = self.timeouts.get(operation_type, self.default_timeout)
        return await with_timeout(coro, timeout, fallback)

    def set_timeout(self, operation_type: str, seconds: float):
        """특정 작업 타입의 타임아웃 설정"""
        self.timeouts[operation_type] = seconds
        logger.info(f"Timeout set for {operation_type}: {seconds}s")


class CircuitBreaker:
    """간단한 서킷 브레이커"""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, coro: Awaitable[T], fallback: Optional[T] = None) -> T:
        """서킷 브레이커를 통한 호출"""

        # 서킷이 열려있는 경우
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                logger.warning("Circuit breaker is open, returning fallback")
                if fallback is not None:
                    return fallback
                raise Exception("Circuit breaker is open")

        try:
            result = await coro
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            logger.error(f"Circuit breaker recorded failure: {e}")
            if fallback is not None:
                return fallback
            raise

    def _should_attempt_reset(self) -> bool:
        """리셋 시도 여부 판단"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).total_seconds() > self.timeout

    def _on_success(self):
        """성공 시 처리"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """실패 시 처리"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )


# 글로벌 인스턴스
_timeout_manager: Optional[TimeoutManager] = None
_circuit_breakers: dict = {}


def get_timeout_manager() -> TimeoutManager:
    """타임아웃 매니저 싱글톤"""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = TimeoutManager()
    return _timeout_manager


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """서킷 브레이커 인스턴스 가져오기"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker()
    return _circuit_breakers[name]


# 데코레이터
def timeout(seconds: float = 15.0, fallback: Any = None):
    """타임아웃 데코레이터"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                coro = func(*args, **kwargs)
            else:
                coro = run_blocking(func, *args, **kwargs)
            return await with_timeout(coro, seconds, fallback)

        return wrapper

    return decorator


def circuit_breaker(name: str, fallback: Any = None):
    """서킷 브레이커 데코레이터"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = get_circuit_breaker(name)
            if asyncio.iscoroutinefunction(func):
                coro = func(*args, **kwargs)
            else:
                coro = run_blocking(func, *args, **kwargs)
            return await breaker.call(coro, fallback)

        return wrapper

    return decorator
