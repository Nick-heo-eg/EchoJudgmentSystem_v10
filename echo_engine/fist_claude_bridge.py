#!/usr/bin/env python3
"""
🎯 FIST Claude Bridge - FIST 구조 템플릿과 Claude 통합 브리지
FIST, RISE, DIR 구조 템플릿을 Claude AI와 연동하여 고도화된 판단 시스템 구현
"""

import json
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# FIST 템플릿 시스템 임포트
from .fist_templates import (
    FISTTemplate,
    FISTRequest,
    FISTResponse,
    RISETemplate,
    DIRTemplate,
    FISTTemplateEngine,
    TemplateSelectionStrategy,
    TemplateCategory,
    TemplateComplexity,
    FISTStructureType,
)

# 기존 Claude Bridge 임포트
from .claude_bridge import ClaudeBridge, ClaudeJudgmentRequest, ClaudeJudgmentResponse


@dataclass
class FISTClaudeRequest:
    """FIST 구조 기반 Claude 요청"""

    input_text: str
    category: TemplateCategory
    structure_type: FISTStructureType = FISTStructureType.FIST

    # Claude 설정
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 2000
    temperature: float = 0.3

    # FIST 설정
    template_id: Optional[str] = None
    complexity: Optional[TemplateComplexity] = None
    selection_strategy: TemplateSelectionStrategy = TemplateSelectionStrategy.BEST_MATCH

    # 컨텍스트
    context: Dict[str, Any] = None
    previous_judgments: Optional[List[Dict]] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class FISTClaudeResponse:
    """FIST 구조 기반 Claude 응답"""

    # FIST 구조 결과
    fist_response: FISTResponse

    # Claude 원본 응답
    claude_response: ClaudeJudgmentResponse

    # 통합 결과
    integrated_judgment: str
    final_confidence: float
    structure_analysis: Dict[str, Any]

    # 메타데이터
    template_used: str
    processing_time: float
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_standard_format(self) -> Dict[str, Any]:
        """표준 판단 형식으로 변환"""
        return {
            "judgment": self.integrated_judgment,
            "confidence": self.final_confidence,
            "reasoning": self.structure_analysis.get("reasoning", ""),
            "emotion_detected": self.claude_response.emotion_detected or "analyzed",
            "strategy_suggested": self.claude_response.strategy_suggested
            or "structured",
            "alternatives": self.claude_response.alternatives or [],
            "processing_time": self.processing_time,
            "fist_structure": self.fist_response.get_structured_output(),
            "template_used": self.template_used,
            "structure_type": self.fist_response.structure_type.value,
        }


class FISTClaudeBridge:
    """FIST 구조 템플릿과 Claude를 연동하는 고급 브리지"""

    def __init__(self, api_mode: str = "mock", templates_dir: Optional[str] = None):
        """
        FIST Claude Bridge 초기화

        Args:
            api_mode: Claude API 모드 ("direct", "mock")
            templates_dir: FIST 템플릿 디렉토리 경로
        """
        self.api_mode = api_mode

        # 기존 Claude Bridge 초기화
        self.claude_bridge = ClaudeBridge(api_mode=api_mode)

        # FIST 템플릿 엔진 초기화
        self.fist_engine = FISTTemplateEngine(templates_dir=templates_dir)

        # 성능 통계
        self.performance_stats = {
            "total_fist_requests": 0,
            "successful_fist_requests": 0,
            "failed_fist_requests": 0,
            "average_processing_time": 0.0,
            "template_usage": {},
            "structure_usage": {},
            "claude_integration_success": 0,
        }

        # 품질 평가 기준
        self.quality_metrics = {
            "structure_completeness": 0.0,
            "claude_integration": 0.0,
            "response_coherence": 0.0,
            "template_effectiveness": 0.0,
        }

        print(f"🎯 FIST Claude Bridge 초기화 완료 - API 모드: {api_mode}")

    async def process_fist_request(
        self, request: FISTClaudeRequest
    ) -> FISTClaudeResponse:
        """FIST 구조 기반 Claude 요청 처리"""
        start_time = time.time()
        self.performance_stats["total_fist_requests"] += 1

        try:
            # 1. FIST 요청 객체 생성
            fist_request = FISTRequest(
                input_text=request.input_text,
                category=request.category,
                structure_type=request.structure_type,
                complexity=request.complexity,
                template_id=request.template_id,
                context=request.context,
            )

            # 2. FIST 템플릿 처리
            fist_response = self.fist_engine.process_request(fist_request)

            # 3. FIST 구조를 Claude 프롬프트로 변환
            claude_prompt = self._convert_fist_to_claude_prompt(fist_response, request)

            # 4. Claude 판단 요청
            claude_request = ClaudeJudgmentRequest(
                input_text=claude_prompt,
                context=request.context.get("additional_context", ""),
                judgment_type="comprehensive",
                include_emotion=True,
                include_strategy=True,
                previous_judgments=request.previous_judgments,
            )

            # 5. Claude 응답 처리
            claude_response = await self.claude_bridge.request_claude_judgment(
                claude_request
            )

            # 6. FIST와 Claude 응답 통합
            integrated_response = self._integrate_fist_claude_responses(
                fist_response, claude_response, request
            )

            # 7. 성능 통계 업데이트
            processing_time = time.time() - start_time
            self._update_performance_stats(fist_response, processing_time, success=True)

            return integrated_response

        except Exception as e:
            self.performance_stats["failed_fist_requests"] += 1
            print(f"❌ FIST Claude 요청 처리 실패: {e}")

            # 오류 응답 생성
            return self._create_error_response(
                request, str(e), time.time() - start_time
            )

    def _convert_fist_to_claude_prompt(
        self, fist_response: FISTResponse, request: FISTClaudeRequest
    ) -> str:
        """FIST 구조를 Claude 프롬프트로 변환"""

        # FIST 구조 기반 프롬프트 생성
        prompt_parts = []

        # 시스템 프롬프트
        prompt_parts.append(
            f"""
당신은 FIST 구조(Frame, Insight, Strategy, Tactics)를 사용하여 체계적인 판단을 수행하는 고급 AI 어시스턴트입니다.

다음 FIST 구조 분석을 바탕으로 종합적인 판단을 제시해주세요:

## 원본 입력
{request.input_text}

## FIST 구조 분석 결과

### Frame (맥락 설정)
{fist_response.frame_result}

### Insight (분석 및 이해)
{fist_response.insight_result}

### Strategy (접근 전략)
{fist_response.strategy_result}

### Tactics (구체적 실행)
{fist_response.tactics_result}

## 요청사항
위 FIST 구조 분석을 바탕으로:
1. 종합적인 판단과 권고사항을 제시해주세요
2. 각 FIST 요소간의 일관성과 연결성을 평가해주세요
3. 실행 가능성과 효과성을 고려한 최종 제안을 해주세요
4. 잠재적 위험요소와 대응방안을 제시해주세요

응답 형식:
- judgment: 핵심 판단 (100자 이내)
- confidence: 신뢰도 (0.0-1.0)
- reasoning: 판단 근거 (300자 이내)
- emotion_detected: 감지된 감정 상태
- strategy_suggested: 추천 전략
- alternatives: 대안 제안 (최대 3개)
"""
        )

        # 추가 컨텍스트 (있는 경우)
        if request.context:
            prompt_parts.append(
                f"\n## 추가 컨텍스트\n{json.dumps(request.context, ensure_ascii=False, indent=2)}"
            )

        return "\n".join(prompt_parts)

    def _integrate_fist_claude_responses(
        self,
        fist_response: FISTResponse,
        claude_response: ClaudeJudgmentResponse,
        request: FISTClaudeRequest,
    ) -> FISTClaudeResponse:
        """FIST와 Claude 응답을 통합"""

        # 1. 통합 판단 생성
        integrated_judgment = self._create_integrated_judgment(
            fist_response, claude_response
        )

        # 2. 최종 신뢰도 계산
        final_confidence = self._calculate_final_confidence(
            fist_response, claude_response
        )

        # 3. 구조 분석 수행
        structure_analysis = self._analyze_structure_quality(
            fist_response, claude_response
        )

        # 4. 통합 응답 생성
        integrated_response = FISTClaudeResponse(
            fist_response=fist_response,
            claude_response=claude_response,
            integrated_judgment=integrated_judgment,
            final_confidence=final_confidence,
            structure_analysis=structure_analysis,
            template_used=fist_response.template_used,
            processing_time=fist_response.processing_time
            + claude_response.processing_time,
        )

        return integrated_response

    def _create_integrated_judgment(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> str:
        """통합 판단 생성"""

        # FIST 구조 기반 판단
        fist_judgment = fist_response.comprehensive_judgment

        # Claude 판단
        claude_judgment = claude_response.judgment

        # 통합 판단 생성
        if fist_response.confidence > claude_response.confidence:
            primary_judgment = fist_judgment
            secondary_judgment = claude_judgment
            primary_source = "FIST 구조 분석"
            secondary_source = "Claude AI 분석"
        else:
            primary_judgment = claude_judgment
            secondary_judgment = fist_judgment
            primary_source = "Claude AI 분석"
            secondary_source = "FIST 구조 분석"

        integrated_judgment = f"""
## 통합 판단

**핵심 권고사항:**
{primary_judgment}

**추가 고려사항:**
{secondary_judgment}

**종합 평가:**
{primary_source}과 {secondary_source}을 종합한 결과, 체계적인 접근과 AI 분석이 일치하는 방향으로 판단을 제시합니다.
"""

        return integrated_judgment.strip()

    def _calculate_final_confidence(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> float:
        """최종 신뢰도 계산"""

        # 기본 신뢰도들
        fist_confidence = fist_response.confidence
        claude_confidence = claude_response.confidence

        # 일치도 계산 (간단한 방법)
        confidence_gap = abs(fist_confidence - claude_confidence)
        consistency_bonus = 1.0 - (confidence_gap * 0.5)

        # 가중 평균 계산
        # FIST는 구조적 접근이므로 약간 더 가중치 부여
        weighted_confidence = fist_confidence * 0.6 + claude_confidence * 0.4

        # 일치도 보너스 적용
        final_confidence = weighted_confidence * consistency_bonus

        # 0.0 ~ 1.0 범위로 제한
        return max(0.0, min(1.0, final_confidence))

    def _analyze_structure_quality(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> Dict[str, Any]:
        """구조 품질 분석"""

        analysis = {
            "structure_completeness": self._assess_structure_completeness(
                fist_response
            ),
            "claude_integration": self._assess_claude_integration(claude_response),
            "response_coherence": self._assess_response_coherence(
                fist_response, claude_response
            ),
            "template_effectiveness": self._assess_template_effectiveness(
                fist_response
            ),
            "reasoning": self._generate_quality_reasoning(
                fist_response, claude_response
            ),
            "recommendations": self._generate_improvement_recommendations(
                fist_response, claude_response
            ),
        }

        return analysis

    def _assess_structure_completeness(self, fist_response: FISTResponse) -> float:
        """구조 완성도 평가"""
        completeness_score = 0.0

        # 각 FIST 요소의 완성도 체크
        components = [
            fist_response.frame_result,
            fist_response.insight_result,
            fist_response.strategy_result,
            fist_response.tactics_result,
        ]

        for component in components:
            if component and len(component.strip()) > 10:
                completeness_score += 0.25

        return completeness_score

    def _assess_claude_integration(
        self, claude_response: ClaudeJudgmentResponse
    ) -> float:
        """Claude 통합 품질 평가"""
        integration_score = 0.0

        # Claude 응답의 품질 지표들
        if claude_response.judgment and len(claude_response.judgment.strip()) > 20:
            integration_score += 0.3

        if claude_response.reasoning and len(claude_response.reasoning.strip()) > 30:
            integration_score += 0.3

        if claude_response.confidence > 0.5:
            integration_score += 0.2

        if (
            claude_response.emotion_detected
            and claude_response.emotion_detected != "neutral"
        ):
            integration_score += 0.1

        if claude_response.strategy_suggested:
            integration_score += 0.1

        return integration_score

    def _assess_response_coherence(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> float:
        """응답 일관성 평가"""
        coherence_score = 0.5  # 기본 점수

        # 신뢰도 일치도
        confidence_consistency = 1.0 - abs(
            fist_response.confidence - claude_response.confidence
        )
        coherence_score += confidence_consistency * 0.3

        # 추론 추적 완성도
        if fist_response.reasoning_trace and len(fist_response.reasoning_trace) > 2:
            coherence_score += 0.2

        return min(1.0, coherence_score)

    def _assess_template_effectiveness(self, fist_response: FISTResponse) -> float:
        """템플릿 효과성 평가"""
        effectiveness_score = 0.0

        # 처리 시간 효율성
        if fist_response.processing_time < 2.0:
            effectiveness_score += 0.3
        elif fist_response.processing_time < 5.0:
            effectiveness_score += 0.2
        else:
            effectiveness_score += 0.1

        # 신뢰도 수준
        if fist_response.confidence > 0.8:
            effectiveness_score += 0.3
        elif fist_response.confidence > 0.6:
            effectiveness_score += 0.2
        else:
            effectiveness_score += 0.1

        # 추론 추적 품질
        if fist_response.reasoning_trace and len(fist_response.reasoning_trace) > 4:
            effectiveness_score += 0.2

        # 대안 제공
        if fist_response.alternatives and len(fist_response.alternatives) > 0:
            effectiveness_score += 0.2

        return effectiveness_score

    def _generate_quality_reasoning(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> str:
        """품질 분석 근거 생성"""
        reasoning_parts = []

        # FIST 구조 분석
        reasoning_parts.append(
            f"FIST 구조 분석: {fist_response.structure_type.value} 템플릿 사용"
        )
        reasoning_parts.append(f"템플릿 신뢰도: {fist_response.confidence:.3f}")

        # Claude 분석
        reasoning_parts.append(f"Claude 분석 신뢰도: {claude_response.confidence:.3f}")

        # 통합 분석
        confidence_gap = abs(fist_response.confidence - claude_response.confidence)
        if confidence_gap < 0.1:
            reasoning_parts.append("FIST와 Claude 분석이 높은 일치도를 보임")
        elif confidence_gap < 0.3:
            reasoning_parts.append("FIST와 Claude 분석이 적당한 일치도를 보임")
        else:
            reasoning_parts.append("FIST와 Claude 분석 간 차이가 있어 추가 검토 필요")

        return " | ".join(reasoning_parts)

    def _generate_improvement_recommendations(
        self, fist_response: FISTResponse, claude_response: ClaudeJudgmentResponse
    ) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []

        # 신뢰도 기반 권고
        if fist_response.confidence < 0.6:
            recommendations.append("FIST 템플릿 선택 또는 컨텍스트 보완 필요")

        if claude_response.confidence < 0.6:
            recommendations.append("Claude 프롬프트 최적화 또는 추가 정보 제공 필요")

        # 일관성 기반 권고
        confidence_gap = abs(fist_response.confidence - claude_response.confidence)
        if confidence_gap > 0.3:
            recommendations.append("FIST와 Claude 분석 간 차이 원인 분석 필요")

        # 처리 시간 기반 권고
        total_time = fist_response.processing_time + claude_response.processing_time
        if total_time > 10.0:
            recommendations.append("처리 시간 최적화 필요")

        return recommendations

    def _create_error_response(
        self, request: FISTClaudeRequest, error_message: str, processing_time: float
    ) -> FISTClaudeResponse:
        """오류 응답 생성"""

        # 오류 FIST 응답 생성
        error_fist_response = FISTResponse(
            request_id="error",
            template_id="error_template",
            frame_result="오류 발생으로 인한 Frame 분석 불가",
            insight_result=f"오류 내용: {error_message}",
            strategy_result="오류 해결 전략 필요",
            tactics_result="시스템 점검 및 재시도 권장",
            comprehensive_judgment=f"처리 중 오류 발생: {error_message}",
            confidence=0.0,
            processing_time=processing_time,
            template_used="error_template",
            structure_type=request.structure_type,
            reasoning_trace=["오류 발생", error_message],
        )

        # 오류 Claude 응답 생성
        error_claude_response = ClaudeJudgmentResponse(
            judgment="처리 중 오류 발생",
            confidence=0.0,
            reasoning=error_message,
            emotion_detected="neutral",
            strategy_suggested="cautious",
            processing_time=0.0,
        )

        # 오류 통합 응답 생성
        return FISTClaudeResponse(
            fist_response=error_fist_response,
            claude_response=error_claude_response,
            integrated_judgment=f"시스템 오류로 인한 처리 실패: {error_message}",
            final_confidence=0.0,
            structure_analysis={"error": error_message},
            template_used="error_template",
            processing_time=processing_time,
        )

    def _update_performance_stats(
        self, fist_response: FISTResponse, processing_time: float, success: bool
    ):
        """성능 통계 업데이트"""

        if success:
            self.performance_stats["successful_fist_requests"] += 1
            self.performance_stats["claude_integration_success"] += 1

            # 템플릿 사용 통계
            template_id = fist_response.template_id
            self.performance_stats["template_usage"][template_id] = (
                self.performance_stats["template_usage"].get(template_id, 0) + 1
            )

            # 구조 사용 통계
            structure_type = fist_response.structure_type.value
            self.performance_stats["structure_usage"][structure_type] = (
                self.performance_stats["structure_usage"].get(structure_type, 0) + 1
            )

        # 평균 처리 시간 업데이트
        total_successful = self.performance_stats["successful_fist_requests"]
        if total_successful > 0:
            current_avg = self.performance_stats["average_processing_time"]
            new_avg = (
                (current_avg * (total_successful - 1)) + processing_time
            ) / total_successful
            self.performance_stats["average_processing_time"] = new_avg

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        total_requests = max(self.performance_stats["total_fist_requests"], 1)

        return {
            "fist_claude_integration": {
                "total_requests": self.performance_stats["total_fist_requests"],
                "successful_requests": self.performance_stats[
                    "successful_fist_requests"
                ],
                "failed_requests": self.performance_stats["failed_fist_requests"],
                "success_rate": (
                    self.performance_stats["successful_fist_requests"] / total_requests
                )
                * 100,
                "average_processing_time": self.performance_stats[
                    "average_processing_time"
                ],
            },
            "template_usage": self.performance_stats["template_usage"],
            "structure_usage": self.performance_stats["structure_usage"],
            "quality_metrics": self.quality_metrics,
            "claude_integration_success": self.performance_stats[
                "claude_integration_success"
            ],
            "underlying_systems": {
                "fist_engine": self.fist_engine.get_engine_stats(),
                "claude_bridge": self.claude_bridge.get_performance_report(),
            },
        }

    def get_available_templates(self) -> Dict[str, Any]:
        """사용 가능한 FIST 템플릿 목록 반환"""
        return self.fist_engine.get_available_templates()

    def add_custom_template(self, template: FISTTemplate):
        """사용자 정의 템플릿 추가"""
        self.fist_engine.add_template(template)

    def save_session_data(self, filepath: str = None):
        """세션 데이터 저장"""
        if filepath is None:
            filepath = f"fist_claude_session_{int(time.time())}.json"

        session_data = {
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "api_mode": self.api_mode,
            },
            "performance_stats": self.performance_stats,
            "quality_metrics": self.quality_metrics,
            "available_templates": self.get_available_templates(),
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ FIST Claude Bridge 세션 데이터 저장: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 세션 데이터 저장 실패: {e}")
            return None


# 편의 함수들
async def quick_fist_claude_judgment(
    text: str, category: str = "decision", api_mode: str = "mock"
) -> FISTClaudeResponse:
    """빠른 FIST Claude 판단"""
    bridge = FISTClaudeBridge(api_mode=api_mode)
    request = FISTClaudeRequest(
        input_text=text,
        category=TemplateCategory(category),
        structure_type=FISTStructureType.FIST,
    )

    return await bridge.process_fist_request(request)


async def comprehensive_fist_claude_judgment(
    text: str,
    category: str,
    complexity: str = "moderate",
    context: Dict[str, Any] = None,
    api_mode: str = "mock",
) -> FISTClaudeResponse:
    """종합적인 FIST Claude 판단"""
    bridge = FISTClaudeBridge(api_mode=api_mode)
    request = FISTClaudeRequest(
        input_text=text,
        category=TemplateCategory(category),
        complexity=TemplateComplexity(complexity),
        context=context or {},
        structure_type=FISTStructureType.FIST,
        selection_strategy=TemplateSelectionStrategy.BEST_MATCH,
    )

    return await bridge.process_fist_request(request)


# 테스트 코드
if __name__ == "__main__":
    import asyncio

    async def test_fist_claude_bridge():
        print("🎯 FIST Claude Bridge 테스트 시작...")

        # 브리지 초기화
        bridge = FISTClaudeBridge(api_mode="mock")

        # 테스트 케이스들
        test_cases = [
            {
                "text": "새로운 AI 프로젝트를 시작할지 결정해야 합니다.",
                "category": "decision",
                "complexity": "complex",
                "context": {"budget": "limited", "timeline": "6months"},
            },
            {
                "text": "팀원들과의 갈등 상황을 해결해야 합니다.",
                "category": "emotional",
                "complexity": "moderate",
                "context": {"team_size": "5", "conflict_duration": "2weeks"},
            },
            {
                "text": "혁신적인 UI/UX 디자인 아이디어가 필요합니다.",
                "category": "creative",
                "complexity": "moderate",
                "context": {
                    "target_users": "young_professionals",
                    "platform": "mobile",
                },
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 테스트 {i}: {test_case['text']}")

            request = FISTClaudeRequest(
                input_text=test_case["text"],
                category=TemplateCategory(test_case["category"]),
                complexity=TemplateComplexity(test_case["complexity"]),
                context=test_case["context"],
            )

            response = await bridge.process_fist_request(request)

            print(f"  🎯 템플릿 사용: {response.template_used}")
            print(f"  📊 최종 신뢰도: {response.final_confidence:.3f}")
            print(f"  🔄 처리 시간: {response.processing_time:.3f}초")
            print(f"  🧠 통합 판단: {response.integrated_judgment[:100]}...")

            # 구조 분석 요약
            structure_analysis = response.structure_analysis
            print(
                f"  📈 구조 완성도: {structure_analysis.get('structure_completeness', 0):.3f}"
            )
            print(
                f"  🤖 Claude 통합: {structure_analysis.get('claude_integration', 0):.3f}"
            )

        # 성능 리포트
        print("\n📊 성능 리포트:")
        report = bridge.get_performance_report()
        integration_stats = report["fist_claude_integration"]
        print(f"  총 요청: {integration_stats['total_requests']}")
        print(f"  성공률: {integration_stats['success_rate']:.1f}%")
        print(f"  평균 처리 시간: {integration_stats['average_processing_time']:.3f}초")

        # 템플릿 사용 통계
        print(f"  템플릿 사용: {report['template_usage']}")
        print(f"  구조 사용: {report['structure_usage']}")

        # 세션 데이터 저장
        saved_file = bridge.save_session_data()
        print(f"\n💾 세션 데이터 저장: {saved_file}")

    # 테스트 실행
    asyncio.run(test_fist_claude_bridge())
