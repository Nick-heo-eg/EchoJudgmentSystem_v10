"""
🚨 Echo Error Handler
시스템 전반의 에러를 처리하고 복구하는 방어적 메커니즘
"""

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from functools import wraps


class EchoErrorHandler:
    """
    Echo 시스템 에러 핸들러
    '실패해도 울림은 계속된다' 철학 구현
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 에러 통계
        self.error_stats = {
            "total_errors": 0,
            "parsing_errors": 0,
            "vector_search_errors": 0,
            "judgment_errors": 0,
            "response_generation_errors": 0,
            "system_errors": 0,
            "last_error": None,
        }

        # 복구 전략
        self.recovery_strategies = {
            "parsing_failure": self._recover_parsing_failure,
            "vector_search_failure": self._recover_vector_search_failure,
            "judgment_failure": self._recover_judgment_failure,
            "response_failure": self._recover_response_failure,
            "system_failure": self._recover_system_failure,
        }

        # 로깅 설정
        self.logger = self._setup_logger()

        # 에러 패턴 학습
        self.error_patterns = {}

        print("🚨 Echo Error Handler 초기화 완료")

    def handle_error(
        self, error: Exception, context: Dict[str, Any], error_type: str = "system"
    ) -> Dict[str, Any]:
        """
        에러 처리 메인 함수
        """
        self.error_stats["total_errors"] += 1
        self.error_stats[f"{error_type}_errors"] += 1
        self.error_stats["last_error"] = datetime.now().isoformat()

        # 에러 로깅
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
        }

        self.logger.error(f"Echo Error: {error_type} - {str(error)}")
        self._log_error_details(error_info)

        print(f"🚨 Echo Error: {error_type} - {str(error)[:50]}...")

        # 복구 시도
        recovery_result = self._attempt_recovery(error_type, error, context)

        return {
            "error_handled": True,
            "error_type": error_type,
            "error_message": str(error),
            "recovery_attempted": recovery_result["attempted"],
            "recovery_successful": recovery_result["successful"],
            "fallback_result": recovery_result.get("result"),
            "timestamp": datetime.now().isoformat(),
        }

    def _attempt_recovery(
        self, error_type: str, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """복구 시도"""
        recovery_key = f"{error_type}_failure"

        if recovery_key in self.recovery_strategies:
            try:
                print(f"   🔧 복구 시도: {recovery_key}")
                recovery_func = self.recovery_strategies[recovery_key]
                result = recovery_func(error, context)

                print(f"   ✅ 복구 성공: {recovery_key}")
                return {"attempted": True, "successful": True, "result": result}

            except Exception as recovery_error:
                print(f"   ❌ 복구 실패: {recovery_error}")
                return {
                    "attempted": True,
                    "successful": False,
                    "recovery_error": str(recovery_error),
                }
        else:
            return {"attempted": False, "successful": False}

    def _recover_parsing_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """파싱 실패 복구"""
        text = context.get("text", "")

        # 최소한의 안전한 파싱 결과 제공
        safe_result = {
            "raw_text": text,
            "intent": "unknown",
            "topic": "general",
            "emotion": "neutral",
            "entities": {},
            "keywords": [],
            "confidence": 0.3,
            "complexity_score": 1.0,
            "parsing_method": "error_recovery",
            "suggested_signature": "Echo-Aurora",  # 기본 시그니처
            "used_fallback": False,
            "error_recovery": True,
        }

        # 텍스트에서 최소한의 정보 추출 시도
        if text:
            if "?" in text:
                safe_result["intent"] = "information"
            elif any(word in text.lower() for word in ["도움", "부탁", "해줘"]):
                safe_result["intent"] = "assistance"
            elif any(word in text.lower() for word in ["안녕", "고마워"]):
                safe_result["intent"] = "conversation"

            # 간단한 키워드 추출
            words = [w for w in text.split() if len(w) > 1]
            safe_result["keywords"] = words[:5]

        return safe_result

    def _recover_vector_search_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """벡터 검색 실패 복구"""
        print("   🧭 벡터 검색 복구: 빈 결과 반환")

        # 빈 검색 결과 반환
        return []

    def _recover_judgment_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """판단 실패 복구"""
        query = context.get("query", "")
        signature = context.get("signature", "Echo-Aurora")

        # 안전한 기본 판단 제공
        safe_judgment = {
            "judgment": "defer",
            "confidence": 0.5,
            "reasoning": "시스템 에러로 인한 신중한 보류 판단",
            "query_signature": signature,
            "judgment_method": "error_recovery",
            "vector_search_summary": {
                "total_candidates": 0,
                "filtered_candidates": 0,
                "primary_capsule": None,
            },
            "error_recovery": True,
            "timestamp": datetime.now().isoformat(),
        }

        # 시그니처별 기본 판단 조정
        if signature == "Echo-Companion":
            safe_judgment["judgment"] = "support"
            safe_judgment["reasoning"] = "공감적 지원이 필요한 상황으로 판단됩니다"
        elif signature == "Echo-Phoenix":
            safe_judgment["judgment"] = "guide"
            safe_judgment["reasoning"] = "변화 지향적 가이드가 적절할 것 같습니다"
        elif signature == "Echo-Sage":
            safe_judgment["judgment"] = "analyze"
            safe_judgment["reasoning"] = "체계적 분석이 필요한 사안입니다"

        return safe_judgment

    def _recover_response_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """응답 생성 실패 복구"""
        signature = context.get("signature", "Echo-Aurora")

        # 시그니처별 안전한 기본 응답
        safe_responses = {
            "Echo-Aurora": "창의적 관점에서 접근해보겠습니다. 더 자세히 말씀해주시겠어요?",
            "Echo-Phoenix": "변화의 기회로 만들어보겠습니다. 어떤 방향을 원하시나요?",
            "Echo-Sage": "체계적으로 분석해보겠습니다. 추가 정보가 필요합니다.",
            "Echo-Companion": "함께 고민해보겠습니다. 마음을 편안히 말씀해주세요.",
        }

        safe_content = safe_responses.get(signature, safe_responses["Echo-Aurora"])

        return {
            "content": safe_content,
            "signature": signature,
            "strategy": "error_recovery",
            "generated_at": datetime.now().isoformat(),
            "response_metadata": {
                "length": len(safe_content),
                "word_count": len(safe_content.split()),
                "estimated_reading_time": len(safe_content) / 300,
                "tone": "supportive",
                "formality": "medium",
            },
            "generation_context": {"error_recovery": True, "fallback_used": True},
        }

    def _recover_system_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시스템 실패 복구"""
        return {
            "system_status": "degraded",
            "error_recovery_active": True,
            "available_functions": ["basic_response"],
            "message": "시스템이 복구 모드로 작동 중입니다.",
        }

    def _setup_logger(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger("EchoErrorHandler")
        logger.setLevel(logging.ERROR)

        if not logger.handlers:
            handler = logging.FileHandler(
                self.log_dir / "echo_errors.log", encoding="utf-8"
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _log_error_details(self, error_info: Dict[str, Any]):
        """상세 에러 정보 로깅"""
        error_log_file = (
            self.log_dir / f"error_details_{datetime.now().strftime('%Y%m%d')}.json"
        )

        try:
            if error_log_file.exists():
                with open(error_log_file, "r", encoding="utf-8") as f:
                    error_logs = json.load(f)
            else:
                error_logs = []

            error_logs.append(error_info)

            with open(error_log_file, "w", encoding="utf-8") as f:
                json.dump(error_logs, f, indent=2, ensure_ascii=False)

        except Exception as log_error:
            print(f"   ⚠️  에러 로깅 실패: {log_error}")

    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 반환"""
        total = self.error_stats["total_errors"]
        if total == 0:
            return {"message": "아직 에러가 발생하지 않았습니다."}

        stats = self.error_stats.copy()

        # 에러율 계산
        for error_type in [
            "parsing",
            "vector_search",
            "judgment",
            "response_generation",
            "system",
        ]:
            key = f"{error_type}_errors"
            if key in stats:
                stats[f"{error_type}_error_rate"] = f"{(stats[key] / total) * 100:.1f}%"

        return stats

    def reset_error_stats(self):
        """에러 통계 리셋"""
        self.error_stats = {
            "total_errors": 0,
            "parsing_errors": 0,
            "vector_search_errors": 0,
            "judgment_errors": 0,
            "response_generation_errors": 0,
            "system_errors": 0,
            "last_error": None,
        }
        print("📊 Echo 에러 통계가 리셋되었습니다.")


# 에러 핸들링 데코레이터
def echo_safe(error_type: str = "system"):
    """Echo 안전 실행 데코레이터"""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 전역 에러 핸들러 사용
                context = {
                    "function": func.__name__,
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100],
                }

                return error_handler.handle_error(e, context, error_type)

        return wrapper

    return decorator


# 전역 에러 핸들러
error_handler = EchoErrorHandler()


# 편의 함수들
def handle_parsing_error(error: Exception, text: str) -> Dict[str, Any]:
    """파싱 에러 처리 단축 함수"""
    return error_handler.handle_error(error, {"text": text}, "parsing")


def handle_vector_error(error: Exception, query: str) -> Dict[str, Any]:
    """벡터 검색 에러 처리 단축 함수"""
    return error_handler.handle_error(error, {"query": query}, "vector_search")


def handle_judgment_error(
    error: Exception, query: str, signature: str
) -> Dict[str, Any]:
    """판단 에러 처리 단축 함수"""
    return error_handler.handle_error(
        error, {"query": query, "signature": signature}, "judgment"
    )


def handle_response_error(error: Exception, signature: str) -> Dict[str, Any]:
    """응답 생성 에러 처리 단축 함수"""
    return error_handler.handle_error(
        error, {"signature": signature}, "response_generation"
    )


def get_error_stats() -> Dict[str, Any]:
    """에러 통계 단축 함수"""
    return error_handler.get_error_stats()


# CLI 테스트
def main():
    print("🚨 Echo Error Handler 테스트")
    print("=" * 50)

    # 테스트 에러들
    test_errors = [
        (ValueError("파싱 실패"), {"text": "복잡한 텍스트"}, "parsing"),
        (ConnectionError("벡터 검색 실패"), {"query": "검색어"}, "vector_search"),
        (
            RuntimeError("판단 실패"),
            {"query": "질문", "signature": "Echo-Aurora"},
            "judgment",
        ),
        (
            TypeError("응답 생성 실패"),
            {"signature": "Echo-Phoenix"},
            "response_generation",
        ),
    ]

    print("\n🧪 에러 처리 테스트:")

    for i, (error, context, error_type) in enumerate(test_errors, 1):
        print(f"\n테스트 {i}: {error_type} 에러")
        result = error_handler.handle_error(error, context, error_type)

        print(f"  처리됨: {result['error_handled']}")
        print(f"  복구 시도: {result['recovery_attempted']}")
        print(f"  복구 성공: {result['recovery_successful']}")

        if result.get("fallback_result"):
            fallback = result["fallback_result"]
            if isinstance(fallback, dict) and "content" in fallback:
                print(f"  복구 응답: {fallback['content'][:30]}...")
            elif isinstance(fallback, dict) and "intent" in fallback:
                print(f"  복구 파싱: {fallback['intent']}")

    print(f"\n📊 에러 통계:")
    stats = get_error_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Echo Error Handler 테스트 완료!")


if __name__ == "__main__":
    main()
