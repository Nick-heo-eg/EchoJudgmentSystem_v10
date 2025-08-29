#!/usr/bin/env python3
"""
🚀 Lazy FIST Template Engine - 지연 로딩 최적화 버전
초기화 시점이 아닌 실제 사용 시점에 템플릿을 로드하여 시작 속도를 대폭 개선
"""

import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from .template_engine import FISTTemplateEngine
from .fist_core import TemplateCategory, FISTTemplate


class LazyFISTTemplateEngine:
    """지연 로딩 FIST 템플릿 엔진"""

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir
        self._template_engine: Optional[FISTTemplateEngine] = None
        self._loaded_categories: set = set()
        self._load_on_demand = True

        print("🚀 Lazy FIST Template Engine 초기화 완료 (지연 로딩 모드)")

    def _ensure_engine_loaded(self) -> FISTTemplateEngine:
        """필요할 때만 템플릿 엔진 로드"""
        if self._template_engine is None:
            print("🔄 FIST 템플릿 엔진 로딩 중...")
            start_time = time.time()

            self._template_engine = FISTTemplateEngine(self.templates_dir)

            load_time = time.time() - start_time
            print(f"✅ FIST 템플릿 엔진 로드 완료: {load_time:.3f}초")

        return self._template_engine

    def get_template_for_category(
        self, category: TemplateCategory
    ) -> Optional[FISTTemplate]:
        """카테고리별 템플릿 반환 (지연 로딩)"""
        engine = self._ensure_engine_loaded()

        # 해당 카테고리의 템플릿 찾기
        templates = engine.get_available_templates()

        for template_id, info in templates["templates"].items():
            if info["category"] == category.value:
                return engine.templates.get(template_id)

        return None

    def get_emotion_strategy_template(
        self, emotion: str, strategy: str
    ) -> Optional[FISTTemplate]:
        """감정×전략 조합 템플릿 반환 (지연 로딩)"""
        engine = self._ensure_engine_loaded()

        template_key = f"{emotion}_{strategy}"
        return engine.templates.get(template_key)

    def process_request_lazy(
        self, input_text: str, category: TemplateCategory
    ) -> Dict[str, Any]:
        """지연 로딩 방식으로 요청 처리"""
        try:
            template = self.get_template_for_category(category)

            if not template:
                return {
                    "success": False,
                    "error": f"카테고리 {category.value}에 해당하는 템플릿을 찾을 수 없습니다",
                    "fallback": True,
                }

            # 간단한 컨텍스트로 렌더링
            context = {"input_text": input_text}
            rendered_prompt = template.get_full_prompt(context)

            return {
                "success": True,
                "template_id": template.template_id,
                "template_name": template.name,
                "rendered_prompt": rendered_prompt,
                "category": category.value,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"템플릿 처리 중 오류: {e}",
                "fallback": True,
            }

    def get_available_categories(self) -> List[str]:
        """사용 가능한 카테고리 목록 반환 (최소 로딩)"""
        # 기본 카테고리만 반환 (실제 로딩 없이)
        return [
            "emotional",
            "decision",
            "creative",
            "evaluation",
            "analytical",
            "strategic",
            "problem_solving",
            "prediction",
        ]

    def is_loaded(self) -> bool:
        """템플릿 엔진이 로드되었는지 확인"""
        return self._template_engine is not None

    def get_load_stats(self) -> Dict[str, Any]:
        """로딩 상태 통계"""
        if self._template_engine is None:
            return {
                "loaded": False,
                "total_templates": 0,
                "loaded_categories": list(self._loaded_categories),
                "message": "아직 로드되지 않음 (지연 로딩 대기 중)",
            }

        templates_info = self._template_engine.get_available_templates()
        return {
            "loaded": True,
            "total_templates": templates_info["total_templates"],
            "available_categories": templates_info["categories"],
            "loaded_categories": list(self._loaded_categories),
            "engine_stats": self._template_engine.get_engine_stats(),
        }


# 전역 인스턴스 (싱글톤 패턴)
_lazy_template_engine: Optional[LazyFISTTemplateEngine] = None


def get_lazy_template_engine(
    templates_dir: Optional[str] = None,
) -> LazyFISTTemplateEngine:
    """지연 로딩 템플릿 엔진 인스턴스 반환"""
    global _lazy_template_engine
    if _lazy_template_engine is None:
        _lazy_template_engine = LazyFISTTemplateEngine(templates_dir)
    return _lazy_template_engine


def quick_lazy_judgment(input_text: str, category: str = "emotional") -> Dict[str, Any]:
    """빠른 지연 로딩 판단"""
    try:
        category_enum = TemplateCategory(category.lower())
    except ValueError:
        category_enum = TemplateCategory.EMOTIONAL

    engine = get_lazy_template_engine()
    return engine.process_request_lazy(input_text, category_enum)


if __name__ == "__main__":
    # 지연 로딩 테스트
    print("🧪 Lazy Template Engine 테스트")

    engine = get_lazy_template_engine()
    print(f"초기 상태: {engine.get_load_stats()}")

    # 첫 번째 요청 (이때 로딩됨)
    result1 = quick_lazy_judgment("테스트 입력입니다", "emotional")
    print(f"첫 번째 요청 결과: {result1['success']}")

    # 두 번째 요청 (이미 로딩된 상태)
    result2 = quick_lazy_judgment("분석이 필요한 내용", "analytical")
    print(f"두 번째 요청 결과: {result2['success']}")

    print(f"최종 상태: {engine.get_load_stats()}")
