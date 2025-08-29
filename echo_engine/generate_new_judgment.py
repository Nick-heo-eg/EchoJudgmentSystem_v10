#!/usr/bin/env python3
"""
🔧 Generate New Judgment v1.0 - 신규 판단 생성기

기존 모듈들을 연동하여 새로운 판단을 생성하는 파이프라인.
감정 추론 → 전략 선택 → 템플릿 적용 → 시그니처 스타일링 순서로 실행.

연동 모듈:
- emotion_infer.py (감정 추론)
- strategy_picker.py (전략 선택)
- template_formatter.py (템플릿 생성)
- signature_response_sync.py (시그니처 스타일링)

핵심 기능:
1. LLM-Free 판단 파이프라인 실행
2. 각 단계별 오류 처리 및 fallback
3. 판단 품질 검증
4. 메타데이터 수집
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# 기존 모듈 임포트 (연동만 수행)
try:
    from .emotion_infer import infer_emotion
    from .strategy_picker import pick_strategy, get_detailed_strategy_recommendation
    from .template_formatter import TemplateFormatter
    from .signature_response_sync import apply_signature_style
except ImportError:
    # 상대 임포트 실패 시 절대 임포트 시도
    import sys
    import os

    # sys.path 수정 불필요 (portable_paths 사용)

    try:
        from echo_engine.emotion_infer import infer_emotion as emotion_infer_func
        from echo_engine.strategy_picker import (
            pick_strategy,
            get_detailed_strategy_recommendation,
        )
        from echo_engine.template_formatter import TemplateFormatter
        from echo_engine.signature_response_sync import apply_signature_style

        # emotion_infer 함수가 EmotionInferenceResult를 반환하므로 래핑
        def infer_emotion(text: str) -> Tuple[str, float]:
            try:
                result = emotion_infer_func(text)
                # EmotionInferenceResult 객체인 경우
                if hasattr(result, "primary_emotion") and hasattr(result, "confidence"):
                    return result.primary_emotion, result.confidence
                elif hasattr(result, "dominant_emotion") and hasattr(
                    result, "confidence"
                ):
                    return result.dominant_emotion, result.confidence
                elif hasattr(result, "emotion") and hasattr(result, "confidence"):
                    return result.emotion, result.confidence
                else:
                    # 단순 문자열이 반환된 경우
                    return str(result), 0.7
            except Exception as e:
                print(f"⚠️ 감정 추론 세부 오류: {e}")
                return "neutral", 0.5

    except ImportError as e:
        print(f"⚠️ 기존 모듈 임포트 실패: {e}")
        print("   임시 stub 함수를 사용합니다.")

        # 임시 stub 함수들 (실제 모듈이 없을 경우)
        def infer_emotion(text: str) -> Tuple[str, float]:
            """임시 감정 추론 함수"""
            if "피곤" in text or "힘들" in text:
                return "sadness", 0.7
            elif "기뻐" in text or "좋" in text:
                return "joy", 0.8
            elif "화나" in text or "짜증" in text:
                return "anger", 0.7
            elif "무서" in text or "두려" in text:
                return "fear", 0.6
            else:
                return "neutral", 0.5

        def pick_strategy(
            text: str, emotion: str = "neutral", context: Optional[Dict] = None
        ) -> Any:
            """임시 전략 선택 함수"""

            class MockStrategy:
                def __init__(self, value):
                    self.value = value

            if emotion == "sadness":
                return MockStrategy("retreat")
            elif emotion == "joy":
                return MockStrategy("initiate")
            elif emotion == "anger":
                return MockStrategy("confront")
            elif emotion == "fear":
                return MockStrategy("analyze")
            else:
                return MockStrategy("adapt")

        def get_detailed_strategy_recommendation(
            text: str, emotion: str = "neutral", context: Optional[Dict] = None
        ) -> Any:
            """임시 상세 전략 추천 함수"""

            class MockRecommendation:
                def __init__(self):
                    self.primary_strategy = pick_strategy(text, emotion, context)
                    self.confidence = 0.7
                    self.reasoning = ["임시 추론"]

            return MockRecommendation()

        class TemplateFormatter:
            """임시 템플릿 포매터"""

            def __init__(self):
                pass

            def format_template(
                self, emotion: str, strategy: str, context: Optional[Dict] = None
            ) -> str:
                return f"[{emotion}_{strategy}] 템플릿 응답입니다."

        def apply_signature_style(template: str, signature: str = "Selene") -> str:
            """임시 시그니처 스타일링 함수"""
            styles = {
                "Selene": f"조용히... {template}",
                "Aurora": f"밝게! {template}",
                "Phoenix": f"변화를 위해 {template}",
                "Sage": f"지혜롭게 {template}",
                "Companion": f"친근하게 {template}",
            }
            return styles.get(signature, template)


@dataclass
class JudgmentGenerationResult:
    """판단 생성 결과"""

    success: bool
    emotion: str
    emotion_confidence: float
    strategy: str
    strategy_confidence: float
    template: str
    styled_sentence: str
    processing_steps: List[str]
    processing_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class NewJudgmentGenerator:
    """🔧 신규 판단 생성기"""

    def __init__(self):
        """초기화"""
        self.version = "1.0.0"

        # 하위 모듈 초기화
        try:
            self.template_formatter = TemplateFormatter()
        except Exception as e:
            print(f"⚠️ TemplateFormatter 초기화 실패: {e}")
            self.template_formatter = TemplateFormatter()  # stub으로 대체

        # 설정
        self.min_confidence_threshold = 0.3
        self.enable_quality_check = True

        # 통계
        self.stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "emotion_step_failures": 0,
            "strategy_step_failures": 0,
            "template_step_failures": 0,
            "styling_step_failures": 0,
            "processing_times": [],
            "emotion_distribution": {},
            "strategy_distribution": {},
        }

        print(f"🔧 NewJudgmentGenerator v{self.version} 초기화 완료")

    def generate_judgment(
        self,
        input_text: str,
        signature: str = "Selene",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        신규 판단 생성 메인 함수

        Args:
            input_text: 입력 텍스트
            signature: 시그니처
            context: 추가 컨텍스트

        Returns:
            판단 결과 딕셔너리
        """
        start_time = time.time()
        self.stats["total_generations"] += 1

        processing_steps = []

        try:
            # 1단계: 감정 추론
            emotion_result = self._infer_emotion_step(input_text)
            processing_steps.append(
                f"감정 추론: {emotion_result['emotion']} ({emotion_result['confidence']:.2f})"
            )

            # 2단계: 전략 선택
            strategy_result = self._select_strategy_step(
                input_text, emotion_result["emotion"]
            )
            processing_steps.append(
                f"전략 선택: {strategy_result['strategy']} ({strategy_result['confidence']:.2f})"
            )

            # 3단계: 템플릿 생성
            template_result = self._generate_template_step(
                emotion_result["emotion"], strategy_result["strategy"], context
            )
            processing_steps.append(
                f"템플릿 생성: {template_result['template'][:30]}..."
            )

            # 4단계: 시그니처 스타일링
            styling_result = self._apply_styling_step(
                template_result["template"], signature
            )
            processing_steps.append(f"스타일링 적용: {signature}")

            # 5단계: 품질 검증 (선택적)
            if self.enable_quality_check:
                quality_check = self._validate_quality(
                    styling_result["styled_sentence"]
                )
                processing_steps.append(
                    f"품질 검증: {'통과' if quality_check['valid'] else '실패'}"
                )

                if not quality_check["valid"]:
                    # 품질 검증 실패 시 fallback
                    styling_result = self._create_fallback_response(
                        input_text, signature
                    )
                    processing_steps.append("Fallback 응답 적용")

            # 통계 업데이트
            self.stats["successful_generations"] += 1
            self.stats["emotion_distribution"][emotion_result["emotion"]] = (
                self.stats["emotion_distribution"].get(emotion_result["emotion"], 0) + 1
            )
            self.stats["strategy_distribution"][strategy_result["strategy"]] = (
                self.stats["strategy_distribution"].get(strategy_result["strategy"], 0)
                + 1
            )

            processing_time = time.time() - start_time
            self.stats["processing_times"].append(processing_time)

            return {
                "emotion": emotion_result["emotion"],
                "emotion_confidence": emotion_result["confidence"],
                "strategy": strategy_result["strategy"],
                "strategy_confidence": strategy_result["confidence"],
                "template": template_result["template"],
                "styled_sentence": styling_result["styled_sentence"],
                "processing_steps": processing_steps,
                "processing_time": processing_time,
                "metadata": {
                    "emotion_metadata": emotion_result.get("metadata", {}),
                    "strategy_metadata": strategy_result.get("metadata", {}),
                    "template_metadata": template_result.get("metadata", {}),
                    "styling_metadata": styling_result.get("metadata", {}),
                },
            }

        except Exception as e:
            # 전체 파이프라인 실패 시 fallback
            fallback_result = self._create_fallback_response(input_text, signature)
            processing_steps.append(f"전체 실패 - Fallback: {str(e)[:50]}")

            processing_time = time.time() - start_time
            self.stats["processing_times"].append(processing_time)

            return {
                "emotion": "neutral",
                "emotion_confidence": 0.3,
                "strategy": "analyze",
                "strategy_confidence": 0.3,
                "template": "fallback_template",
                "styled_sentence": fallback_result["styled_sentence"],
                "processing_steps": processing_steps,
                "processing_time": processing_time,
                "error": str(e),
                "metadata": {"fallback_reason": str(e)},
            }

    def _infer_emotion_step(self, input_text: str) -> Dict[str, Any]:
        """감정 추론 단계"""
        try:
            result = infer_emotion(input_text)

            # 튜플인 경우
            if isinstance(result, tuple) and len(result) == 2:
                emotion, confidence = result
            # EmotionInferenceResult 객체인 경우
            elif hasattr(result, "primary_emotion") and hasattr(result, "confidence"):
                emotion, confidence = result.primary_emotion, result.confidence
            elif hasattr(result, "dominant_emotion") and hasattr(result, "confidence"):
                emotion, confidence = result.dominant_emotion, result.confidence
            # 기존 호환성을 위한 속성 체크
            elif hasattr(result, "emotion") and hasattr(result, "confidence"):
                emotion, confidence = result.emotion, result.confidence
            # 문자열인 경우
            elif isinstance(result, str):
                emotion, confidence = result, 0.7
            else:
                emotion, confidence = "neutral", 0.5

            return {
                "emotion": emotion,
                "confidence": confidence,
                "metadata": {
                    "method": "emotion_infer_module",
                    "input_length": len(input_text),
                },
            }

        except Exception as e:
            self.stats["emotion_step_failures"] += 1
            print(f"⚠️ 감정 추론 실패: {e}")

            # Fallback 감정 추론
            return {
                "emotion": "neutral",
                "confidence": 0.4,
                "metadata": {"method": "fallback", "error": str(e)},
            }

    def _select_strategy_step(self, input_text: str, emotion: str) -> Dict[str, Any]:
        """전략 선택 단계"""
        try:
            # 상세 전략 추천 시도
            try:
                detailed_recommendation = get_detailed_strategy_recommendation(
                    input_text, emotion
                )
                strategy = detailed_recommendation.primary_strategy.value
                confidence = detailed_recommendation.confidence
                reasoning = detailed_recommendation.reasoning
            except:
                # 간단한 전략 선택으로 fallback
                strategy_obj = pick_strategy(input_text, emotion)
                strategy = (
                    strategy_obj.value
                    if hasattr(strategy_obj, "value")
                    else str(strategy_obj)
                )
                confidence = 0.6
                reasoning = ["기본 전략 선택"]

            return {
                "strategy": strategy,
                "confidence": confidence,
                "metadata": {
                    "method": "strategy_picker_module",
                    "reasoning": reasoning,
                    "emotion_used": emotion,
                },
            }

        except Exception as e:
            self.stats["strategy_step_failures"] += 1
            print(f"⚠️ 전략 선택 실패: {e}")

            # Fallback 전략 선택
            fallback_strategies = {
                "sadness": "retreat",
                "joy": "initiate",
                "anger": "confront",
                "fear": "analyze",
                "surprise": "analyze",
                "neutral": "adapt",
            }

            return {
                "strategy": fallback_strategies.get(emotion, "adapt"),
                "confidence": 0.4,
                "metadata": {"method": "fallback", "error": str(e)},
            }

    def _generate_template_step(
        self, emotion: str, strategy: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """템플릿 생성 단계"""
        try:
            # format_template(frame, tactics, emotion) 순서 맞춤
            template = self.template_formatter.format_template(
                strategy, "함께 이야기해보겠습니다", emotion
            )

            return {
                "template": template,
                "metadata": {
                    "method": "template_formatter_module",
                    "emotion": emotion,
                    "strategy": strategy,
                    "template_length": len(template),
                },
            }

        except Exception as e:
            self.stats["template_step_failures"] += 1
            print(f"⚠️ 템플릿 생성 실패: {e}")

            # Fallback 템플릿
            fallback_templates = {
                "sadness_retreat": "힘드시겠어요. 충분히 쉬세요.",
                "joy_initiate": "좋은 기분이시네요! 함께 시작해봐요.",
                "anger_confront": "화가 나셨군요. 문제를 해결해봅시다.",
                "fear_analyze": "걱정이 되시는군요. 차근차근 살펴봅시다.",
                "neutral_adapt": "상황에 맞게 접근해보겠습니다.",
            }

            template_key = f"{emotion}_{strategy}"
            fallback_template = fallback_templates.get(
                template_key, "함께 이야기해보겠습니다."
            )

            return {
                "template": fallback_template,
                "metadata": {
                    "method": "fallback",
                    "template_key": template_key,
                    "error": str(e),
                },
            }

    def _apply_styling_step(self, template: str, signature: str) -> Dict[str, Any]:
        """시그니처 스타일링 단계"""
        try:
            styled_sentence = apply_signature_style(template, signature)

            return {
                "styled_sentence": styled_sentence,
                "metadata": {
                    "method": "signature_response_sync_module",
                    "signature": signature,
                    "original_template": template,
                },
            }

        except Exception as e:
            self.stats["styling_step_failures"] += 1
            print(f"⚠️ 스타일링 실패: {e}")

            # Fallback 스타일링 (기본 템플릿 그대로 사용)
            return {
                "styled_sentence": template,
                "metadata": {
                    "method": "fallback",
                    "signature": signature,
                    "error": str(e),
                },
            }

    def _validate_quality(self, styled_sentence: str) -> Dict[str, Any]:
        """응답 품질 검증"""
        issues = []

        # 길이 체크
        if len(styled_sentence.strip()) < 3:
            issues.append("응답이 너무 짧음")

        if len(styled_sentence) > 200:
            issues.append("응답이 너무 길음")

        # 특수 문자 체크
        if styled_sentence.count("[") != styled_sentence.count("]"):
            issues.append("괄호 불일치")

        # 반복 체크
        words = styled_sentence.split()
        if len(words) > 2 and len(set(words)) < len(words) * 0.7:
            issues.append("단어 반복 과다")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 1.0 - len(issues) * 0.3),
        }

    def _create_fallback_response(
        self, input_text: str, signature: str
    ) -> Dict[str, Any]:
        """최종 fallback 응답 생성"""

        # 시그니처별 fallback 응답
        fallback_responses = {
            "Selene": "음... 조금 더 자세히 말씀해주시겠어요?",
            "Aurora": "흥미로워요! 더 구체적으로 얘기해주세요!",
            "Phoenix": "새로운 관점이네요. 더 발전시켜봅시다.",
            "Sage": "흥미로운 주제네요. 분석해볼 가치가 있어 보입니다.",
            "Companion": "그렇구나! 더 자세히 얘기해줄래?",
        }

        return {
            "styled_sentence": fallback_responses.get(signature, "더 이야기해주세요."),
            "metadata": {
                "method": "final_fallback",
                "signature": signature,
                "original_input": input_text,
            },
        }

    def get_generation_statistics(self) -> Dict[str, Any]:
        """생성 통계 정보"""
        total = self.stats["total_generations"]
        if total == 0:
            return {"message": "생성된 판단이 없습니다"}

        success_rate = (self.stats["successful_generations"] / total) * 100
        avg_time = (
            sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            if self.stats["processing_times"]
            else 0
        )

        return {
            "total_generations": total,
            "successful_generations": self.stats["successful_generations"],
            "success_rate": f"{success_rate:.1f}%",
            "average_processing_time": f"{avg_time:.3f}초",
            "step_failure_rates": {
                "emotion": f"{(self.stats['emotion_step_failures'] / total) * 100:.1f}%",
                "strategy": f"{(self.stats['strategy_step_failures'] / total) * 100:.1f}%",
                "template": f"{(self.stats['template_step_failures'] / total) * 100:.1f}%",
                "styling": f"{(self.stats['styling_step_failures'] / total) * 100:.1f}%",
            },
            "emotion_distribution": self.stats["emotion_distribution"],
            "strategy_distribution": self.stats["strategy_distribution"],
        }


if __name__ == "__main__":
    # 테스트
    print("🔧 NewJudgmentGenerator 테스트")

    generator = NewJudgmentGenerator()

    test_cases = [
        {"text": "오늘 너무 피곤해", "signature": "Selene"},
        {"text": "새로운 프로젝트를 시작하고 싶어", "signature": "Aurora"},
        {"text": "이 문제가 너무 복잡해", "signature": "Sage"},
        {"text": "친구와 싸웠어", "signature": "Companion"},
        {"text": "변화가 필요한 시점인 것 같아", "signature": "Phoenix"},
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n🔧 테스트 {i}: '{case['text']}' ({case['signature']})")

        result = generator.generate_judgment(case["text"], case["signature"])

        print(f"   감정: {result['emotion']} ({result['emotion_confidence']:.2f})")
        print(f"   전략: {result['strategy']} ({result['strategy_confidence']:.2f})")
        print(f"   응답: {result['styled_sentence']}")
        print(f"   처리시간: {result['processing_time']:.3f}초")
        if result.get("error"):
            print(f"   오류: {result['error']}")

    # 통계 출력
    stats = generator.get_generation_statistics()
    print(f"\n📊 생성 통계:")
    for key, value in stats.items():
        if key not in [
            "emotion_distribution",
            "strategy_distribution",
            "step_failure_rates",
        ]:
            print(f"   {key}: {value}")
