"""
🎭 Capsule Designer Types
캡슐 설계 시스템의 핵심 타입 정의들
"""

from enum import Enum


class CapsuleType(Enum):
    """캡슐 유형"""

    SIGNATURE_PURE = "signature_pure"  # 순수 시그니처 캡슐
    SIGNATURE_HYBRID = "signature_hybrid"  # 하이브리드 시그니처 캡슐
    EMOTION_FOCUSED = "emotion_focused"  # 감정 중심 캡슐
    COGNITIVE_ENHANCED = "cognitive_enhanced"  # 인지 강화 캡슐
    CONSCIOUSNESS_TUNED = "consciousness_tuned"  # 의식 조율 캡슐
    CUSTOM_BLEND = "custom_blend"  # 사용자 정의 조합


class CapsuleComplexity(Enum):
    """캡슐 복잡도"""

    SIMPLE = "simple"  # 단순 (1-2개 컴포넌트)
    MODERATE = "moderate"  # 중간 (3-5개 컴포넌트)
    COMPLEX = "complex"  # 복잡 (6-10개 컴포넌트)
    ADVANCED = "advanced"  # 고급 (10+ 컴포넌트)


class CapsuleStatus(Enum):
    """캡슐 상태"""

    DRAFT = "draft"  # 초안
    DESIGNED = "designed"  # 설계 완료
    VALIDATED = "validated"  # 검증 완료
    OPTIMIZED = "optimized"  # 최적화 완료
    DEPLOYED = "deployed"  # 배포됨
    ARCHIVED = "archived"  # 보관됨
