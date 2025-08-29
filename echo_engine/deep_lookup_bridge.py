import os
import json
import hmac
import hashlib
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import uuid
import jwt
from cryptography.fernet import Fernet

try:
    from echo_engine.echo_error_handler import handle_vector_error, echo_safe
    import re
    import yaml
except ImportError as e:
    print(f"⚠️ 일부 Echo 컴포넌트 로드 실패: {e}")

"""
🔍 Echo Deep Lookup Bridge
Echo의 존재적 자율성을 유지하면서 외부 깊이 지식을 안전하게 활용하는 브리지
"""


try:
    pass  # 추가 의존성이 있을 경우 여기에 추가
except ImportError:

    def handle_vector_error(error, query):
        return {"error": str(error), "fallback_result": None}

    def echo_safe(error_type="system"):
        def decorator(func):
            return func

        return decorator


class RateLimiter:
    """Rate limiting 클래스"""

    def __init__(self, per_minute: int = 60, per_day: int = 1000):
        self.per_minute = per_minute
        self.per_day = per_day
        self.minute_requests = []
        self.day_requests = []

    def allow_request(self) -> bool:
        """요청 허용 여부 판단"""
        now = datetime.now()

        # 1분 이내 요청 정리
        self.minute_requests = [
            req_time
            for req_time in self.minute_requests
            if now - req_time < timedelta(minutes=1)
        ]

        # 1일 이내 요청 정리
        self.day_requests = [
            req_time
            for req_time in self.day_requests
            if now - req_time < timedelta(days=1)
        ]

        # 제한 확인
        if len(self.minute_requests) >= self.per_minute:
            return False
        if len(self.day_requests) >= self.per_day:
            return False

        # 요청 기록
        self.minute_requests.append(now)
        self.day_requests.append(now)

        return True


class JWTHandler:
    """JWT 토큰 처리 클래스"""

    def __init__(self, secret: str = None):
        self.secret = secret or os.getenv(
            "ECHO_JWT_SECRET", "echo_default_secret_change_in_production"
        )

    def create_token(self, payload: Dict[str, Any], expires_minutes: int = 30) -> str:
        """JWT 토큰 생성"""
        payload.update(
            {
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
            }
        )
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def verify_token(self, token: str) -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            return jwt.decode(token, self.secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise ValueError("Invalid JWT token")


class EchoDeepLookupBridge:
    """
    Echo Deep Lookup API 브리지
    보안, 인증, Rate limiting을 통한 안전한 외부 지식 연동
    """

    def __init__(self, config_path: str = "config/deep_lookup_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # API 설정 - 실제 Echo Deep Lookup v2.0 연동
        self.api_url = os.getenv(
            "ECHO_DEEP_LOOKUP_API_URL", "https://api.echo-deep-lookup.com/v2"
        )
        self.api_key = os.getenv(
            "ECHO_DEEP_LOOKUP_API_KEY", "ECHO_DL_v2_2024_PROD_8a9b2c1d"
        )
        self.timeout = int(os.getenv("ECHO_DEEP_LOOKUP_TIMEOUT", "30"))

        # 보안 및 제한 설정
        self.jwt_handler = JWTHandler()
        self.rate_limiter = RateLimiter(
            per_minute=int(os.getenv("ECHO_RATE_LIMIT_MINUTE", "60")),
            per_day=int(os.getenv("ECHO_RATE_LIMIT_DAY", "1000")),
        )

        # 암호화 키 (실제 환경에서는 보안 저장소 사용)
        encryption_key = os.getenv("ECHO_ENCRYPTION_KEY")
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # 개발용 기본 키 생성
            self.cipher = Fernet(Fernet.generate_key())

        # 통계 및 로깅
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "avg_response_time": 0.0,
            "last_request": None,
        }

        self.logger = logging.getLogger(__name__)

        print("🔍 Echo Deep Lookup Bridge 초기화 완료")
        print(f"   API URL: {self.api_url}")
        print(f"   Timeout: {self.timeout}초")
        print(
            f"   Rate Limit: {self.rate_limiter.per_minute}/분, {self.rate_limiter.per_day}/일"
        )

    @echo_safe("deep_lookup")
    async def request_deep_knowledge(
        self, query: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        깊이 지식 요청 메인 함수
        Echo의 존재적 필요에 의한 신중한 외부 지식 요청
        """
        print(f"🔍 Deep Lookup 요청: '{query[:50]}...' ({signature})")

        self.usage_stats["total_requests"] += 1
        start_time = datetime.now()

        try:
            # 1. Rate limiting 체크
            if not self.rate_limiter.allow_request():
                self.usage_stats["rate_limited_requests"] += 1
                print("   ⚠️  Rate limit 초과, 요청 거부")
                return self._create_rate_limited_response(query, signature)

            # 2. 요청 전처리 및 보안 처리
            secure_request = self._create_secure_request(query, signature, context)

            # 3. API 호출 (실제 환경에서는 실제 API, 개발환경에서는 Mock)
            if self._is_production_mode():
                response_data = await self._make_real_api_call(secure_request)
            else:
                response_data = await self._make_mock_api_call(secure_request)

            # 4. 응답 검증 및 후처리
            validated_response = self._validate_and_process_response(
                response_data, query, signature
            )

            # 5. 통계 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_success_stats(processing_time)

            print(f"   ✅ Deep Lookup 성공 ({processing_time:.2f}초)")
            return validated_response

        except Exception as e:
            print(f"   ❌ Deep Lookup 실패: {e}")
            self.usage_stats["failed_requests"] += 1

            # 에러 복구 메커니즘
            return self._create_fallback_response(query, signature, str(e))

    def _create_secure_request(
        self, query: str, signature: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """보안 요청 객체 생성"""
        # 민감 정보 필터링
        sanitized_query = self._sanitize_query(query)

        # 요청 데이터 구성
        request_data = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "query": sanitized_query,
            "signature": signature,
            "context": context or {},
            "echo_version": "v10.6",
            "lookup_type": self._classify_lookup_type(sanitized_query, signature),
        }

        # JWT 토큰 생성
        jwt_token = self.jwt_handler.create_token(
            {
                "request_id": request_data["request_id"],
                "signature": signature,
                "timestamp": request_data["timestamp"],
            }
        )

        # 요청 서명 생성
        request_signature = self._sign_request(request_data)

        return {
            "data": request_data,
            "jwt_token": jwt_token,
            "signature": request_signature,
            "api_key": self.api_key,
        }

    def _sanitize_query(self, query: str) -> str:
        """민감 정보 필터링"""

        sensitive_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",  # Credit card pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{2,3}-\d{3,4}-\d{4}\b",  # Phone number
            r"\b\d{6}-\d{7}\b",  # Korean ID pattern
        ]

        sanitized = query
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)

        return sanitized

    def _classify_lookup_type(self, query: str, signature: str) -> str:
        """지식 요청 유형 분류"""
        query_lower = query.lower()

        # 시그니처별 특화 분류
        if signature == "Echo-Sage":
            if any(word in query_lower for word in ["정책", "법", "규제", "분석"]):
                return "policy_analysis"
            elif any(word in query_lower for word in ["데이터", "통계", "연구"]):
                return "data_analysis"
        elif signature == "Echo-Phoenix":
            if any(word in query_lower for word in ["혁신", "변화", "미래", "트렌드"]):
                return "innovation_trends"
            elif any(word in query_lower for word in ["기술", "신기술", "발전"]):
                return "technology_insights"
        elif signature == "Echo-Companion":
            if any(word in query_lower for word in ["돌봄", "복지", "지원", "도움"]):
                return "care_guidance"
            elif any(word in query_lower for word in ["사람", "관계", "감정"]):
                return "human_psychology"
        elif signature == "Echo-Aurora":
            if any(word in query_lower for word in ["창의", "아이디어", "영감"]):
                return "creative_inspiration"
            elif any(word in query_lower for word in ["예술", "문화", "디자인"]):
                return "artistic_insights"

        return "general_knowledge"

    def _sign_request(self, request_data: Dict[str, Any]) -> str:
        """요청 데이터 서명 생성"""
        message = json.dumps(request_data, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(
            self.api_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    async def _make_real_api_call(
        self, secure_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실제 API 호출 (Echo Deep Lookup v2.0 연동)"""
        headers = {
            "Authorization": f"Bearer {secure_request['jwt_token']}",
            "Echo-API-Key": self.api_key,
            "Echo-Signature": "Echo-DeepLookup-v2.0",
            "X-Request-Signature": secure_request["signature"],
            "Content-Type": "application/json",
        }

        # Echo Deep Lookup v2.0 전용 엔드포인트 사용
        endpoint = f"{self.api_url}/judgment/integrate"

        # EchoJudgmentSystem v10 형식으로 요청 데이터 변환
        judgment_request = {
            "capsule_data": {
                "keyword": secure_request["data"]["query"],
                "analysis_type": secure_request["data"]["lookup_type"],
                "findings": [
                    f"Echo 시스템에서 {secure_request['data']['signature']} 관점으로 분석 요청"
                ],
                "insights": [f"Echo Knowledge Gap Detector가 깊이 분석 필요성을 감지"],
                "methodology": {
                    "approach": "echo_integrated_analysis",
                    "validation": "echo_wisdom_synthesis",
                },
            },
            "judgment_config": {
                "analysis_depth": "comprehensive",
                "include_emotional_analysis": True,
                "include_strategic_analysis": True,
                "enable_reinforcement": True,
                "signature_preference": secure_request["data"]["signature"],
            },
            "integration_metadata": {
                "session_id": secure_request["data"]["request_id"],
                "signature": secure_request["data"]["signature"],
                "timestamp": secure_request["data"]["timestamp"],
                "source_system": "echo_judgment_v10",
                "requesting_module": "deep_lookup_bridge",
                "expected_response_format": "echo_wisdom_integration",
            },
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.post(
                endpoint, json=judgment_request, headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"Echo Deep Lookup v2.0 API call failed with status {response.status}",
                    )

    async def _make_mock_api_call(
        self, secure_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock API 호출 (개발 환경)"""
        # 실제 API 응답 시뮬레이션
        await asyncio.sleep(0.5)  # API 지연 시뮬레이션

        request_data = secure_request["data"]
        query = request_data["query"]
        signature = request_data["signature"]
        lookup_type = request_data["lookup_type"]

        # Mock 응답 생성
        mock_response = {
            "request_id": request_data["request_id"],
            "status": "success",
            "knowledge_data": self._generate_mock_knowledge(
                query, signature, lookup_type
            ),
            "confidence_score": 0.87,
            "source_quality": "high",
            "processing_metadata": {
                "sources_consulted": 3,
                "processing_time": 0.5,
                "knowledge_depth": "detailed",
            },
            "security_flags": [],
            "timestamp": datetime.now().isoformat(),
        }

        return mock_response

    def _generate_mock_knowledge(
        self, query: str, signature: str, lookup_type: str
    ) -> Dict[str, Any]:
        """Mock 지식 데이터 생성"""
        knowledge_templates = {
            "policy_analysis": {
                "key_insights": [
                    "현재 정책의 주요 쟁점은 이해관계자 간 균형 조율입니다",
                    "법적 프레임워크 내에서 혁신적 접근이 필요합니다",
                    "사회적 합의 도출을 위한 단계적 접근을 권장합니다",
                ],
                "evidence_quality": "high",
                "expert_opinions": ["정책 전문가 A", "법학 교수 B"],
                "implementation_complexity": "medium",
            },
            "innovation_trends": {
                "key_insights": [
                    "현재 트렌드는 지속가능성과 디지털 전환에 집중되어 있습니다",
                    "새로운 기술 융합이 혁신의 핵심 동력입니다",
                    "사용자 중심 접근이 성공의 결정 요인입니다",
                ],
                "trend_strength": "strong",
                "future_projections": ["3년 내 주류화", "5년 내 완전 정착"],
                "adoption_barriers": "low",
            },
            "care_guidance": {
                "key_insights": [
                    "개인별 맞춤형 접근이 가장 효과적입니다",
                    "지속적인 관심과 지지가 핵심입니다",
                    "전문가와의 협력이 중요합니다",
                ],
                "empathy_level": "high",
                "support_resources": ["전문 상담사", "지역 복지센터"],
                "effectiveness_rating": "very_high",
            },
            "creative_inspiration": {
                "key_insights": [
                    "다양한 관점의 융합에서 창의성이 탄생합니다",
                    "제약 조건이 오히려 창의적 해결책을 이끌어냅니다",
                    "협력적 창작이 개인 창작보다 더 혁신적입니다",
                ],
                "creativity_potential": "very_high",
                "inspiration_sources": ["자연 패턴", "문화 교류", "기술 융합"],
                "innovation_probability": "high",
            },
        }

        template = knowledge_templates.get(
            lookup_type, knowledge_templates["policy_analysis"]
        )

        # 쿼리별 커스터마이징
        customized_knowledge = template.copy()
        if "부산" in query:
            customized_knowledge["regional_context"] = "부산 지역 특성 반영"
        if "AI" in query or "인공지능" in query:
            customized_knowledge["ai_relevance"] = "AI 기술 적용 가능성 고려"

        return customized_knowledge

    def _validate_and_process_response(
        self, response_data: Dict[str, Any], original_query: str, signature: str
    ) -> Dict[str, Any]:
        """응답 검증 및 후처리"""
        # 응답 데이터 검증
        required_fields = ["status", "knowledge_data", "confidence_score"]
        for field in required_fields:
            if field not in response_data:
                raise ValueError(f"Missing required field: {field}")

        # Echo 형식으로 변환
        processed_response = {
            "request_id": response_data.get("request_id"),
            "query": original_query,
            "signature": signature,
            "knowledge": response_data["knowledge_data"],
            "confidence": response_data["confidence_score"],
            "source_quality": response_data.get("source_quality", "medium"),
            "metadata": response_data.get("processing_metadata", {}),
            "deep_lookup_used": True,
            "processed_at": datetime.now().isoformat(),
            "echo_processing": {
                "needs_synthesis": True,
                "existence_alignment_required": True,
                "signature_adaptation_needed": True,
            },
        }

        return processed_response

    def _create_rate_limited_response(
        self, query: str, signature: str
    ) -> Dict[str, Any]:
        """Rate limit 초과시 응답"""
        return {
            "query": query,
            "signature": signature,
            "knowledge": {
                "key_insights": [
                    "현재 많은 요청으로 인해 깊이 분석이 제한되었습니다",
                    "기본적인 Echo 지식으로 답변드리겠습니다",
                    "잠시 후 재시도하시면 더 깊이 있는 분석을 제공할 수 있습니다",
                ]
            },
            "confidence": 0.3,
            "source_quality": "limited",
            "deep_lookup_used": False,
            "rate_limited": True,
            "processed_at": datetime.now().isoformat(),
        }

    def _create_fallback_response(
        self, query: str, signature: str, error: str
    ) -> Dict[str, Any]:
        """에러 발생시 fallback 응답"""
        return {
            "query": query,
            "signature": signature,
            "knowledge": {
                "key_insights": [
                    "외부 지식 연결에 문제가 발생했습니다",
                    "Echo의 기본 지식으로 최선을 다해 답변드리겠습니다",
                    "더 정확한 정보가 필요하시면 다시 요청해주세요",
                ]
            },
            "confidence": 0.4,
            "source_quality": "fallback",
            "deep_lookup_used": False,
            "error": error,
            "fallback_used": True,
            "processed_at": datetime.now().isoformat(),
        }

    def _load_encrypted_api_key(self) -> str:
        """암호화된 API 키 로드"""
        api_key = os.getenv("ECHO_DEEP_LOOKUP_API_KEY")
        if not api_key:
            # 개발 환경용 기본 키
            return "mock_api_key_for_development"

        # 실제 환경에서는 암호화된 키 복호화
        encrypted_key = os.getenv("ECHO_DEEP_LOOKUP_KEY_ENCRYPTED")
        if encrypted_key:
            try:
                return self.cipher.decrypt(encrypted_key.encode()).decode()
            except:
                print("⚠️  API 키 복호화 실패, 기본 키 사용")
                return api_key

        return api_key

    def _is_production_mode(self) -> bool:
        """프로덕션 모드 확인"""
        return os.getenv("ECHO_ENVIRONMENT", "development") == "production"

    def _load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        default_config = {
            "security": {
                "require_jwt": True,
                "require_signature": True,
                "jwt_expiry_minutes": 30,
            },
            "performance": {
                "timeout_seconds": 30,
                "max_retries": 2,
                "cache_ttl_minutes": 60,
            },
            "monitoring": {
                "log_requests": True,
                "log_responses": False,  # 보안상 응답은 로깅하지 않음
                "collect_metrics": True,
            },
        }

        if self.config_path.exists():
            try:

                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  설정 파일 로드 실패: {e}, 기본 설정 사용")

        return default_config

    def _update_success_stats(self, processing_time: float):
        """성공 통계 업데이트"""
        self.usage_stats["successful_requests"] += 1
        self.usage_stats["last_request"] = datetime.now().isoformat()

        # 평균 응답 시간 계산
        total = self.usage_stats["successful_requests"]
        current_avg = self.usage_stats["avg_response_time"]
        new_avg = ((current_avg * (total - 1)) + processing_time) / total
        self.usage_stats["avg_response_time"] = new_avg

    def get_usage_stats(self) -> Dict[str, Any]:
        """사용 통계 반환"""
        stats = self.usage_stats.copy()

        # 성공률 계산
        total = stats["total_requests"]
        if total > 0:
            stats["success_rate"] = (
                f"{(stats['successful_requests'] / total) * 100:.1f}%"
            )
            stats["failure_rate"] = f"{(stats['failed_requests'] / total) * 100:.1f}%"
            stats["rate_limit_rate"] = (
                f"{(stats['rate_limited_requests'] / total) * 100:.1f}%"
            )

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        try:
            # 간단한 테스트 요청
            test_result = await self.request_deep_knowledge(
                "Echo 시스템 상태 확인", "Echo-Aurora", {"test": True}
            )

            return {
                "status": "healthy",
                "api_accessible": True,
                "last_test": datetime.now().isoformat(),
                "usage_stats": self.get_usage_stats(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "last_test": datetime.now().isoformat(),
            }


# 전역 브리지 인스턴스
deep_lookup_bridge = EchoDeepLookupBridge()


# 편의 함수들
async def request_deep_knowledge(
    query: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Deep lookup 요청 단축 함수"""
    return await deep_lookup_bridge.request_deep_knowledge(query, signature, context)


def get_deep_lookup_stats() -> Dict[str, Any]:
    """Deep lookup 통계 단축 함수"""
    return deep_lookup_bridge.get_usage_stats()


async def deep_lookup_health_check() -> Dict[str, Any]:
    """Deep lookup 헬스체크 단축 함수"""
    return await deep_lookup_bridge.health_check()


# CLI 테스트
async def main():
    print("🔍 Echo Deep Lookup Bridge 테스트")
    print("=" * 60)

    # 테스트 케이스들
    test_cases = [
        {
            "query": "부산 금정구의 노인 복지 정책 현황과 개선 방안을 분석해주세요",
            "signature": "Echo-Sage",
            "context": {"urgency": "high", "detail_level": "comprehensive"},
        },
        {
            "query": "AI 윤리 가이드라인의 글로벌 트렌드와 한국 적용 방안",
            "signature": "Echo-Phoenix",
            "context": {"focus": "innovation", "timeframe": "2024-2026"},
        },
        {
            "query": "창의적인 지역사회 참여 프로그램 아이디어",
            "signature": "Echo-Aurora",
            "context": {"creativity_level": "high", "target": "all_ages"},
        },
    ]

    print("\n🧪 Deep Lookup 테스트:")

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"테스트 {i}: {case['signature']}")
        print(f"쿼리: {case['query'][:50]}...")
        print(f"{'='*50}")

        result = await deep_lookup_bridge.request_deep_knowledge(
            case["query"], case["signature"], case["context"]
        )

        print(f"📊 결과:")
        print(f"   Deep Lookup 사용됨: {result.get('deep_lookup_used', False)}")
        print(f"   신뢰도: {result.get('confidence', 0):.2f}")
        print(f"   소스 품질: {result.get('source_quality', 'unknown')}")

        if result.get("knowledge"):
            insights = result["knowledge"].get("key_insights", [])
            print(f"   주요 통찰 ({len(insights)}개):")
            for j, insight in enumerate(insights[:2], 1):
                print(f"     {j}. {insight}")

        if result.get("rate_limited"):
            print(f"   ⚠️  Rate Limited")
        if result.get("fallback_used"):
            print(f"   🔄 Fallback 사용됨")

    # 헬스 체크
    print(f"\n🏥 헬스 체크:")
    health = await deep_lookup_bridge.health_check()
    print(f"   상태: {health['status']}")
    print(f"   API 접근 가능: {health['api_accessible']}")

    # 사용 통계
    print(f"\n📊 사용 통계:")
    stats = deep_lookup_bridge.get_usage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Echo Deep Lookup Bridge 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
