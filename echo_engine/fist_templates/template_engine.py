"""
🎯 FIST Template Engine - 템플릿 렌더링 및 처리 엔진
FIST, RISE, DIR 구조의 템플릿을 처리하고 Claude와 연동하는 핵심 엔진
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import os
from pathlib import Path

from .fist_core import (
    FISTTemplate,
    FISTRequest,
    FISTResponse,
    RISETemplate,
    DIRTemplate,
    FISTStructureType,
    TemplateCategory,
    TemplateComplexity,
    FISTComponent,
    load_template_from_dict,
)


class TemplateRenderer:
    """템플릿 렌더링 클래스"""

    def __init__(self):
        self.rendering_stats = {
            "total_renderings": 0,
            "successful_renderings": 0,
            "failed_renderings": 0,
            "average_render_time": 0.0,
        }

    def render_template(self, template: FISTTemplate, context: Dict[str, Any]) -> str:
        """템플릿을 컨텍스트와 함께 렌더링"""
        start_time = time.time()
        self.rendering_stats["total_renderings"] += 1

        try:
            # 기본 컨텍스트 설정
            render_context = self._prepare_render_context(template, context)

            # 템플릿 렌더링
            rendered_prompt = template.get_full_prompt(render_context)

            # 성공 통계 업데이트
            self.rendering_stats["successful_renderings"] += 1
            render_time = time.time() - start_time
            self._update_render_stats(render_time)

            return rendered_prompt

        except Exception as e:
            self.rendering_stats["failed_renderings"] += 1
            raise ValueError(f"템플릿 렌더링 실패: {e}")

    def _prepare_render_context(
        self, template: FISTTemplate, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """렌더링 컨텍스트 준비"""
        base_context = {
            "template_name": template.name,
            "template_category": template.category.value,
            "complexity_level": template.complexity.value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "structure_type": template.structure_type.value,
        }

        # 사용자 컨텍스트 병합
        base_context.update(context)

        # 🔧 패치: 필수 템플릿 변수 검증 및 기본값 설정
        base_context = self._ensure_template_keys(base_context)

        return base_context

    def _ensure_template_keys(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 필수 키 검증 및 기본값 설정"""
        required_keys = [
            "key_people",
            "situation",
            "focus",
            "insights",
            "strategic_direction",
            "implementation",
            "risk_factors",
            "decision_criteria",
            "target_audience",
            "context_summary",
            "stakeholders",
            "objectives",
            "constraints",
        ]

        for key in required_keys:
            if key not in context or context[key] is None:
                context[key] = "미지정"
                print(f"[DEBUG] 템플릿 변수 기본값 설정: {key} = '미지정'")

        return context

    def _update_render_stats(self, render_time: float):
        """렌더링 통계 업데이트"""
        total_successful = self.rendering_stats["successful_renderings"]
        current_avg = self.rendering_stats["average_render_time"]

        if total_successful == 1:
            self.rendering_stats["average_render_time"] = render_time
        else:
            new_avg = (
                current_avg * (total_successful - 1) + render_time
            ) / total_successful
            self.rendering_stats["average_render_time"] = new_avg

    def get_render_stats(self) -> Dict[str, Any]:
        """렌더링 통계 반환"""
        return self.rendering_stats.copy()


class TemplateSelector:
    """템플릿 선택 클래스"""

    def __init__(self, templates: List[FISTTemplate]):
        self.templates = templates
        self.selection_history = []

    def select_template(
        self, request: FISTRequest, strategy: str = "best_match"
    ) -> FISTTemplate:
        """최적 템플릿 선택"""

        # 카테고리 일치 템플릿 필터링
        category_matches = [t for t in self.templates if t.category == request.category]

        if not category_matches:
            # 카테고리 일치가 없으면 일반적인 템플릿 사용
            category_matches = [
                t for t in self.templates if t.category == TemplateCategory.ANALYTICAL
            ]

        if not category_matches:
            raise ValueError(
                f"카테고리 {request.category.value}에 해당하는 템플릿이 없습니다"
            )

        # 선택 전략 적용
        if strategy == "best_match":
            selected = self._select_best_match(category_matches, request)
        elif strategy == "high_performance":
            selected = self._select_high_performance(category_matches)
        elif strategy == "complexity_based":
            selected = self._select_by_complexity(category_matches, request.complexity)
        else:
            selected = category_matches[0]  # 기본값

        # 선택 이력 기록
        self.selection_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "request_id": request.request_id,
                "selected_template": selected.template_id,
                "strategy": strategy,
                "category": request.category.value,
            }
        )

        return selected

    def _select_best_match(
        self, templates: List[FISTTemplate], request: FISTRequest
    ) -> FISTTemplate:
        """최적 일치 템플릿 선택"""
        scores = []

        for template in templates:
            score = 0

            # 성능 점수 (성공률과 평균 신뢰도)
            score += template.success_rate * 0.4
            score += template.average_confidence * 0.3

            # 사용 빈도 (인기도)
            normalized_usage = min(template.usage_count / 100, 1.0)
            score += normalized_usage * 0.2

            # 복잡도 일치
            if request.complexity and template.complexity == request.complexity:
                score += 0.1

            scores.append((template, score))

        # 최고 점수 템플릿 반환
        return max(scores, key=lambda x: x[1])[0]

    def _select_high_performance(self, templates: List[FISTTemplate]) -> FISTTemplate:
        """고성능 템플릿 선택"""
        return max(templates, key=lambda t: t.success_rate * t.average_confidence)

    def _select_by_complexity(
        self, templates: List[FISTTemplate], complexity: Optional[TemplateComplexity]
    ) -> FISTTemplate:
        """복잡도 기반 템플릿 선택"""
        if complexity:
            complexity_matches = [t for t in templates if t.complexity == complexity]
            if complexity_matches:
                return complexity_matches[0]

        # 기본적으로 중간 복잡도 선택
        moderate_templates = [
            t for t in templates if t.complexity == TemplateComplexity.MODERATE
        ]
        return moderate_templates[0] if moderate_templates else templates[0]

    def get_selection_analytics(self) -> Dict[str, Any]:
        """선택 분석 결과"""
        if not self.selection_history:
            return {"message": "선택 이력이 없습니다"}

        # 템플릿 사용 통계
        template_usage = {}
        strategy_usage = {}
        category_usage = {}

        for entry in self.selection_history:
            template_id = entry["selected_template"]
            strategy = entry["strategy"]
            category = entry["category"]

            template_usage[template_id] = template_usage.get(template_id, 0) + 1
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
            category_usage[category] = category_usage.get(category, 0) + 1

        return {
            "total_selections": len(self.selection_history),
            "template_usage": template_usage,
            "strategy_usage": strategy_usage,
            "category_usage": category_usage,
            "most_used_template": (
                max(template_usage, key=template_usage.get) if template_usage else None
            ),
            "most_used_strategy": (
                max(strategy_usage, key=strategy_usage.get) if strategy_usage else None
            ),
            "most_used_category": (
                max(category_usage, key=category_usage.get) if category_usage else None
            ),
        }


class FISTTemplateEngine:
    """FIST 템플릿 엔진 메인 클래스"""

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir or self._get_default_templates_dir()
        self.templates: Dict[str, FISTTemplate] = {}
        self.rise_templates: Dict[str, RISETemplate] = {}
        self.dir_templates: Dict[str, DIRTemplate] = {}

        # 컴포넌트 초기화
        self.renderer = TemplateRenderer()
        self.selector = None  # 템플릿 로드 후 초기화

        # 성능 통계
        self.engine_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "template_usage": {},
            "category_usage": {},
        }

        # 템플릿 로드
        self.load_templates()

    def _get_default_templates_dir(self) -> str:
        """기본 템플릿 디렉토리 경로 반환"""
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "templates")

    def load_templates(self):
        """템플릿 파일들을 로드"""
        try:
            # 기본 템플릿 생성 (파일이 없는 경우)
            self._create_default_templates()

            # 템플릿 디렉토리에서 템플릿 로드
            if os.path.exists(self.templates_dir):
                self._load_templates_from_directory()

            # 템플릿 셀렉터 초기화
            template_list = list(self.templates.values())
            if template_list:
                self.selector = TemplateSelector(template_list)

            print(f"✅ FIST 템플릿 로드 완료: {len(self.templates)}개")

        except Exception as e:
            print(f"⚠️ 템플릿 로드 중 오류: {e}")
            self._create_default_templates()

    def _create_default_templates(self):
        """기본 템플릿 생성"""
        from .fist_core import create_simple_fist_template

        # 의사결정 템플릿
        decision_template = create_simple_fist_template(
            name="기본 의사결정 템플릿",
            category=TemplateCategory.DECISION,
            frame_prompt="주어진 상황: '{input_text}'\n이 결정이 필요한 맥락과 배경을 분석해주세요.",
            insight_prompt="상황을 깊이 분석하여 핵심 요소들과 고려사항들을 도출해주세요.",
            strategy_prompt="분석 결과를 바탕으로 최적의 접근 전략을 수립해주세요.",
            tactics_prompt="구체적인 실행 방안과 단계별 행동 계획을 제시해주세요.",
        )

        # 평가 템플릿
        evaluation_template = create_simple_fist_template(
            name="기본 평가 템플릿",
            category=TemplateCategory.EVALUATION,
            frame_prompt="평가 대상: '{input_text}'\n평가 기준과 범위를 설정해주세요.",
            insight_prompt="대상을 다각도로 분석하여 장단점과 특성을 파악해주세요.",
            strategy_prompt="공정하고 객관적인 평가 방법론을 제시해주세요.",
            tactics_prompt="구체적인 평가 지표와 측정 방법을 제안해주세요.",
        )

        # 창의적 문제해결 템플릿
        creative_template = create_simple_fist_template(
            name="창의적 문제해결 템플릿",
            category=TemplateCategory.CREATIVE,
            frame_prompt="창의적 도전: '{input_text}'\n문제의 본질과 창의적 접근이 필요한 이유를 분석해주세요.",
            insight_prompt="기존 관점을 넘어 새로운 시각에서 문제를 재해석해주세요.",
            strategy_prompt="창의적이고 혁신적인 해결 접근법을 설계해주세요.",
            tactics_prompt="구체적인 창의적 실행 방안과 실험적 접근법을 제시해주세요.",
        )

        # 분석적 접근 템플릿 (누락된 ANALYTICAL 카테고리 대응)
        analytical_template = create_simple_fist_template(
            name="분석적 접근 템플릿",
            category=TemplateCategory.ANALYTICAL,
            frame_prompt="분석 대상: '{input_text}'\n체계적 분석이 필요한 맥락과 범위를 설정해주세요.",
            insight_prompt="데이터와 논리를 바탕으로 객관적 통찰을 도출해주세요.",
            strategy_prompt="논리적이고 체계적인 분석 방법론을 수립해주세요.",
            tactics_prompt="구체적인 분석 단계와 검증 방법을 제시해주세요.",
        )

        # 전략적 계획 템플릿 (STRATEGIC 카테고리 대응)
        strategic_template = create_simple_fist_template(
            name="전략적 계획 템플릿",
            category=TemplateCategory.STRATEGIC,
            frame_prompt="전략 목표: '{input_text}'\n전략적 사고가 필요한 상황과 목표를 정의해주세요.",
            insight_prompt="현재 상황의 강점, 약점, 기회, 위협을 분석해주세요.",
            strategy_prompt="장기적 관점에서 효과적인 전략 방향을 수립해주세요.",
            tactics_prompt="구체적인 전략 실행 계획과 단계별 목표를 제시해주세요.",
        )

        # 템플릿 등록
        self.templates[decision_template.template_id] = decision_template
        self.templates[evaluation_template.template_id] = evaluation_template
        self.templates[creative_template.template_id] = creative_template
        self.templates[analytical_template.template_id] = analytical_template
        self.templates[strategic_template.template_id] = strategic_template

        print(f"✅ 기본 템플릿 {len(self.templates)}개 생성 완료")

    def _load_templates_from_directory(self):
        """디렉토리에서 템플릿 파일 로드"""
        templates_path = Path(self.templates_dir)

        if not templates_path.exists():
            return

        # FIST 자동 생성 템플릿 로드 (fist_autogen 디렉토리)
        fist_autogen_path = templates_path / "fist_autogen"
        if fist_autogen_path.exists():
            self._load_fist_autogen_templates(fist_autogen_path)

        # 기존 JSON 템플릿 로드
        for template_file in templates_path.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                # 템플릿 타입에 따라 로드
                if template_data.get("structure_type") == "fist":
                    template = load_template_from_dict(template_data)
                    self.templates[template.template_id] = template

            except Exception as e:
                print(f"⚠️ 템플릿 파일 로드 실패 {template_file}: {e}")

    def _load_fist_autogen_templates(self, fist_autogen_path: Path):
        """자동 생성된 FIST 템플릿 로드 (YAML 형식)"""
        import yaml

        loaded_count = 0
        for yaml_file in fist_autogen_path.glob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)

                # YAML 템플릿을 FIST 구조로 변환
                fist_template = self._convert_yaml_to_fist_template(template_data)
                if fist_template:
                    self.templates[fist_template.template_id] = fist_template
                    loaded_count += 1

            except Exception as e:
                print(f"⚠️ YAML 템플릿 로드 실패 {yaml_file}: {e}")

        if loaded_count > 0:
            print(f"✅ FIST 자동생성 템플릿 {loaded_count}개 로드 완료")

    def _convert_yaml_to_fist_template(
        self, yaml_data: Dict[str, Any]
    ) -> Optional["FISTTemplate"]:
        """YAML 템플릿 데이터를 FISTTemplate 객체로 변환"""
        try:
            from .fist_core import (
                create_simple_fist_template,
                TemplateCategory,
                TemplateComplexity,
            )

            # 카테고리 매핑 (감정×전략 템플릿은 EMOTIONAL 카테고리로)
            category_mapping = {
                "fist": TemplateCategory.EMOTIONAL,  # 감정×전략 조합 템플릿
                "decision": TemplateCategory.DECISION,
                "evaluation": TemplateCategory.EVALUATION,
                "creative": TemplateCategory.CREATIVE,
                "emotional": TemplateCategory.EMOTIONAL,
                "analytical": TemplateCategory.ANALYTICAL,
                "strategic": TemplateCategory.STRATEGIC,
                "problem_solving": TemplateCategory.PROBLEM_SOLVING,
                "prediction": TemplateCategory.PREDICTION,
            }

            category = category_mapping.get(
                yaml_data.get("category", "fist"), TemplateCategory.ANALYTICAL
            )

            # 감정과 전략 조합 기반 템플릿 생성
            template_name = yaml_data.get("template_name", "unknown")
            emotion = yaml_data.get("emotion", "neutral")
            strategy = yaml_data.get("strategy", "adapt")

            # 프롬프트 구성
            frame_prompt = yaml_data.get(
                "frame", f"감정 상태: {emotion}, 전략: {strategy}"
            )
            insight_prompt = yaml_data.get(
                "insight", f"{emotion} 상태에서의 통찰을 도출합니다."
            )
            strategy_prompt = f"전략: {yaml_data.get('strategy', strategy)}"
            tactics_prompt = yaml_data.get(
                "tactics", f"{strategy} 전략에 따른 구체적 행동 방안"
            )

            # FIST 템플릿 생성 (complexity 파라미터 제거 - 버그 원인)
            fist_template = create_simple_fist_template(
                name=f"{emotion}_{strategy} 템플릿",
                category=category,
                frame_prompt=frame_prompt,
                insight_prompt=insight_prompt,
                strategy_prompt=strategy_prompt,
                tactics_prompt=tactics_prompt,
            )

            # 추가 메타데이터 설정
            fist_template.description = yaml_data.get(
                "description", f"{emotion} 감정 + {strategy} 전략 조합 템플릿"
            )
            fist_template.template_id = template_name

            return fist_template

        except Exception as e:
            print(f"⚠️ YAML 템플릿 변환 실패: {e}")
            return None

    def process_request(self, request: FISTRequest) -> FISTResponse:
        """FIST 요청 처리"""
        start_time = time.time()
        self.engine_stats["total_requests"] += 1

        try:
            # 템플릿 선택
            if request.template_id and request.template_id in self.templates:
                template = self.templates[request.template_id]
            else:
                if not self.selector:
                    raise ValueError("사용 가능한 템플릿이 없습니다")
                template = self.selector.select_template(request)

            # 컨텍스트 준비
            context = request.get_context_with_input()

            # 템플릿 렌더링
            rendered_prompt = self.renderer.render_template(template, context)

            # Claude 처리 (실제 구현에서는 Claude API 호출)
            claude_response = self._process_with_claude(
                rendered_prompt, template, context
            )

            # FIST 응답 생성
            response = self._create_fist_response(
                request, template, claude_response, time.time() - start_time
            )

            # 성공 통계 업데이트
            self.engine_stats["successful_requests"] += 1
            self._update_engine_stats(template, time.time() - start_time)

            return response

        except Exception as e:
            self.engine_stats["failed_requests"] += 1
            print(f"❌ FIST 요청 처리 실패: {e}")

            # 오류 응답 생성
            return self._create_error_response(
                request, str(e), time.time() - start_time
            )

    def _process_with_claude(
        self, prompt: str, template: FISTTemplate, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Claude를 통한 프롬프트 처리 (모의 구현)"""
        # 실제 구현에서는 Claude API를 호출
        # 현재는 모의 응답 생성

        # 각 FIST 구성요소별 응답 생성
        frame_response = f"Frame 분석: {context.get('input_text', '')[:100]}..."
        insight_response = f"Insight 도출: {template.category.value} 관점에서 분석됨"
        strategy_response = f"Strategy 수립: {template.complexity.value} 수준의 접근법"
        tactics_response = f"Tactics 제안: 구체적 실행 방안 도출"

        comprehensive = (
            f"FIST 구조 기반 종합 판단: {template.name}을 통한 체계적 분석 완료"
        )

        return {
            "frame_result": frame_response,
            "insight_result": insight_response,
            "strategy_result": strategy_response,
            "tactics_result": tactics_response,
            "comprehensive_judgment": comprehensive,
            "confidence": 0.85,  # 구조화된 접근법으로 높은 신뢰도
            "reasoning_trace": [
                "FIST 구조 템플릿 적용",
                "Frame 설정 완료",
                "Insight 도출 완료",
                "Strategy 수립 완료",
                "Tactics 제안 완료",
                "종합 판단 완성",
            ],
        }

    def _create_fist_response(
        self,
        request: FISTRequest,
        template: FISTTemplate,
        claude_response: Dict[str, Any],
        processing_time: float,
    ) -> FISTResponse:
        """FIST 응답 생성"""
        return FISTResponse(
            request_id=request.request_id,
            template_id=template.template_id,
            frame_result=claude_response["frame_result"],
            insight_result=claude_response["insight_result"],
            strategy_result=claude_response["strategy_result"],
            tactics_result=claude_response["tactics_result"],
            comprehensive_judgment=claude_response["comprehensive_judgment"],
            confidence=claude_response["confidence"],
            processing_time=processing_time,
            template_used=template.name,
            structure_type=template.structure_type,
            reasoning_trace=claude_response["reasoning_trace"],
        )

    def _create_error_response(
        self, request: FISTRequest, error_message: str, processing_time: float
    ) -> FISTResponse:
        """오류 응답 생성"""
        return FISTResponse(
            request_id=request.request_id,
            template_id="error",
            frame_result="오류 발생",
            insight_result=f"처리 중 오류: {error_message}",
            strategy_result="오류 처리 전략 필요",
            tactics_result="시스템 점검 및 재시도 권장",
            comprehensive_judgment=f"요청 처리 실패: {error_message}",
            confidence=0.0,
            processing_time=processing_time,
            template_used="error_template",
            structure_type=FISTStructureType.FIST,
            reasoning_trace=["오류 발생", error_message],
        )

    def _update_engine_stats(self, template: FISTTemplate, processing_time: float):
        """엔진 통계 업데이트"""
        # 처리 시간 평균 업데이트
        total_successful = self.engine_stats["successful_requests"]
        current_avg = self.engine_stats["average_processing_time"]

        if total_successful == 1:
            self.engine_stats["average_processing_time"] = processing_time
        else:
            new_avg = (
                current_avg * (total_successful - 1) + processing_time
            ) / total_successful
            self.engine_stats["average_processing_time"] = new_avg

        # 템플릿 사용 통계
        template_id = template.template_id
        self.engine_stats["template_usage"][template_id] = (
            self.engine_stats["template_usage"].get(template_id, 0) + 1
        )

        # 카테고리 사용 통계
        category = template.category.value
        self.engine_stats["category_usage"][category] = (
            self.engine_stats["category_usage"].get(category, 0) + 1
        )

    def get_available_templates(self) -> Dict[str, Any]:
        """사용 가능한 템플릿 목록 반환"""
        template_info = {}

        for template_id, template in self.templates.items():
            template_info[template_id] = {
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "complexity": template.complexity.value,
                "structure_type": template.structure_type.value,
                "usage_count": template.usage_count,
                "success_rate": template.success_rate,
            }

        return {
            "total_templates": len(self.templates),
            "templates": template_info,
            "categories": list(set(t.category.value for t in self.templates.values())),
            "structure_types": list(
                set(t.structure_type.value for t in self.templates.values())
            ),
        }

    def get_engine_stats(self) -> Dict[str, Any]:
        """엔진 통계 반환"""
        stats = self.engine_stats.copy()

        # 성공률 계산
        total_requests = max(stats["total_requests"], 1)
        stats["success_rate"] = (stats["successful_requests"] / total_requests) * 100
        stats["failure_rate"] = (stats["failed_requests"] / total_requests) * 100

        # 렌더링 통계 추가
        stats["rendering_stats"] = self.renderer.get_render_stats()

        # 선택 통계 추가 (있는 경우)
        if self.selector:
            stats["selection_stats"] = self.selector.get_selection_analytics()

        return stats

    def add_template(self, template: FISTTemplate):
        """새 템플릿 추가"""
        # 템플릿 유효성 검증
        validation = template.validate_template()
        if not validation["is_valid"]:
            raise ValueError(f"템플릿 유효성 검증 실패: {validation['errors']}")

        # 템플릿 추가
        self.templates[template.template_id] = template

        # 셀렉터 업데이트
        if self.selector:
            self.selector.templates = list(self.templates.values())
        else:
            self.selector = TemplateSelector(list(self.templates.values()))

        print(f"✅ 템플릿 추가 완료: {template.name}")

    def remove_template(self, template_id: str):
        """템플릿 제거"""
        if template_id in self.templates:
            removed_template = self.templates.pop(template_id)

            # 셀렉터 업데이트
            if self.selector:
                self.selector.templates = list(self.templates.values())

            print(f"✅ 템플릿 제거 완료: {removed_template.name}")
        else:
            print(f"⚠️ 템플릿을 찾을 수 없음: {template_id}")

    def save_templates(self, output_dir: Optional[str] = None):
        """템플릿을 파일로 저장"""
        save_dir = output_dir or self.templates_dir
        os.makedirs(save_dir, exist_ok=True)

        for template_id, template in self.templates.items():
            template_file = Path(save_dir) / f"{template_id}.json"

            try:
                with open(template_file, "w", encoding="utf-8") as f:
                    json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)

                print(f"✅ 템플릿 저장: {template_file}")

            except Exception as e:
                print(f"❌ 템플릿 저장 실패 {template_id}: {e}")


# 편의 함수들
def create_template_engine(templates_dir: Optional[str] = None) -> FISTTemplateEngine:
    """템플릿 엔진 생성"""
    return FISTTemplateEngine(templates_dir)


async def async_process_request(
    engine: FISTTemplateEngine, request: FISTRequest
) -> FISTResponse:
    """비동기 요청 처리"""
    # 현재는 동기 처리이지만, 실제 Claude API 연동 시 비동기로 변경
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, engine.process_request, request)


# Alias for backward compatibility
TemplateEngine = FISTTemplateEngine
