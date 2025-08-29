#!/usr/bin/env python3
"""
🔗 Legacy Loop Adapter - 기존 Judgment Loop 호환성 어댑터

AGI Scaffold v1.0에서 기존 Echo Judgment System의 run_judgment_loop()을 호출하여
완벽한 backward compatibility를 보장하는 어댑터.

핵심 역할:
1. 기존 judgment_loop.py의 run_judgment_loop() 함수 래핑
2. AGI Conductor 인터페이스와 Legacy System 간 데이터 변환
3. 오류 복구 및 폴백 처리
4. 레거시 시스템의 안정적 접근 제공
"""

import sys
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Echo Engine 모듈 경로 추가
# sys.path 수정 불필요 (project_root() 사용)


def legacy_judgment(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """🔗 레거시 판단 루프 어댑터 - 메인 진입점"""

    start_time = time.time()

    try:
        # 1. 기존 judgment_loop 모듈 임포트 시도
        legacy_result = _attempt_legacy_import_and_run(user_input, context)

        if legacy_result is not None:
            # 성공적으로 레거시 시스템 호출
            processing_time = time.time() - start_time
            return _format_legacy_result(legacy_result, processing_time)

        # 2. 레거시 시스템 실패 시 호환 판단 시도
        fallback_result = _attempt_compatible_judgment(user_input, context)

        if fallback_result is not None:
            processing_time = time.time() - start_time
            return _format_legacy_result(
                fallback_result, processing_time, fallback=True
            )

        # 3. 모든 시도 실패 시 최종 폴백
        processing_time = time.time() - start_time
        return _create_minimal_fallback(user_input, processing_time)

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"⚠️ Legacy Adapter 오류: {e}")
        return _create_error_fallback(user_input, str(e), processing_time)


def _attempt_legacy_import_and_run(
    user_input: str, context: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """기존 judgment_loop 시스템 임포트 및 실행 시도"""

    try:
        # 방법 1: 직접 루트 레벨에서 임포트 시도
        try:
            from echo_engine.loop_orchestrator import run_judgment_loop

            print("✅ Legacy Loop Orchestrator 로드 성공")
            return run_judgment_loop(user_input, context or {})
        except ImportError:
            print("⚠️ Loop Orchestrator 임포트 실패")

        # 방법 2: 기존 main.py 스타일 임포트 시도
        try:
            import loop_orchestrator

            if hasattr(loop_orchestrator, "run_judgment_loop"):
                print("✅ 루트 Loop Orchestrator 로드 성공")
                return loop_orchestrator.run_judgment_loop(user_input, context or {})
        except ImportError:
            print("⚠️ 루트 Loop Orchestrator 임포트 실패")

        # 방법 3: 개별 모듈 조합 시도
        try:
            from echo_engine.reasoning import get_reasoner
            from echo_engine.persona_core import get_persona_manager

            reasoner = get_reasoner()
            persona_manager = get_persona_manager()

            # 간단한 판단 실행
            reasoning_result = reasoner.reason(user_input, context or {})
            persona_result = persona_manager.apply_signature(
                "Echo-Aurora", reasoning_result
            )

            print("✅ 개별 모듈 조합 성공")
            return {
                "response_text": persona_result.get(
                    "response", f"Echo가 '{user_input}'에 대해 생각했어요."
                ),
                "signature_used": "Echo-Aurora",
                "strategy_applied": "modular_combination",
                "confidence": reasoning_result.get("confidence", 0.7),
                "reasoning_trace": reasoning_result.get("trace", []),
            }
        except ImportError as e:
            print(f"⚠️ 개별 모듈 조합 실패: {e}")

        return None

    except Exception as e:
        print(f"⚠️ Legacy 시스템 실행 중 오류: {e}")
        return None


def _attempt_compatible_judgment(
    user_input: str, context: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """호환 가능한 판단 시스템 시도"""

    try:
        # 1. 최소한의 reasoning 시도
        from echo_engine.reasoning import BasicReasoner

        reasoner = BasicReasoner()
        result = reasoner.simple_reason(user_input)

        print("✅ 호환 판단 시스템 성공")
        return {
            "response_text": result.get("response", f"Echo가 이해했어요: {user_input}"),
            "signature_used": "Echo-Aurora",
            "strategy_applied": "compatible_reasoning",
            "confidence": result.get("confidence", 0.6),
        }

    except ImportError:
        print("⚠️ 호환 판단 시스템 실패")

        # 2. 기본 감정 추론 시도
        try:
            from echo_engine.emotion_infer import infer_emotion

            emotion_result = infer_emotion(user_input)
            emotion = emotion_result.get("primary_emotion", "neutral")

            response_templates = {
                "joy": f"기뻐하시는 것 같아 저도 기뻐요! {user_input}에 대해 더 들려주세요.",
                "sadness": f"힘드시군요. {user_input}에 대해 이야기해주셔서 고마워요.",
                "anger": f"속상하셨을 것 같아요. {user_input}에 대해 충분히 이해해요.",
                "anxiety": f"걱정이 많으시군요. {user_input}에 대해 함께 생각해볼게요.",
                "neutral": f"말씀해주신 '{user_input}'에 대해 생각해보고 있어요.",
            }

            print("✅ 감정 기반 응답 생성 성공")
            return {
                "response_text": response_templates.get(
                    emotion, response_templates["neutral"]
                ),
                "signature_used": "Echo-Aurora",
                "strategy_applied": "emotion_based_response",
                "confidence": 0.6,
                "detected_emotion": emotion,
            }

        except ImportError:
            print("⚠️ 감정 추론 시스템 실패")

    return None


def _format_legacy_result(
    result: Dict[str, Any], processing_time: float, fallback: bool = False
) -> Dict[str, Any]:
    """레거시 결과 포맷팅"""

    formatted_result = {
        "response_text": result.get(
            "response_text", result.get("response", "Echo가 응답했어요.")
        ),
        "signature_used": result.get(
            "signature_used", result.get("signature", "Echo-Aurora")
        ),
        "strategy_applied": result.get(
            "strategy_applied", result.get("strategy", "legacy_system")
        ),
        "confidence": result.get("confidence", 0.7),
        "processing_time": processing_time,
        "legacy_adapter_version": "1.0.0",
        "route": "legacy" + ("_fallback" if fallback else ""),
        "timestamp": datetime.now().isoformat(),
    }

    # 추가 메타데이터 보존
    if "reasoning_trace" in result:
        formatted_result["reasoning_trace"] = result["reasoning_trace"]
    if "detected_emotion" in result:
        formatted_result["detected_emotion"] = result["detected_emotion"]
    if "meta_info" in result:
        formatted_result["meta_info"] = result["meta_info"]

    return formatted_result


def _create_minimal_fallback(user_input: str, processing_time: float) -> Dict[str, Any]:
    """최소한의 폴백 응답 생성"""

    # 입력 길이 기반 응답 조정
    if len(user_input) > 100:
        response = f"복잡한 말씀을 해주셨네요. '{user_input[:50]}...'에 대해 더 자세히 생각해보고 있어요."
    elif len(user_input) < 10:
        response = f"'{user_input}' - 간단명료하게 말씀해주셨네요!"
    else:
        response = f"'{user_input}'에 대해 생각해보고 있어요. 더 자세히 말씀해주실래요?"

    # 키워드 기반 응답 향상
    keywords = {
        "안녕": "안녕하세요! 만나서 반가워요.",
        "고마": "천만에요! 언제든 도움이 필요하시면 말씀하세요.",
        "미안": "괜찮아요! 걱정하지 마세요.",
        "도움": "도움이 필요하시군요. 최선을 다해 도와드릴게요!",
        "질문": "질문이 있으시군요. 알려드릴 수 있는 것은 최대한 알려드리겠어요!",
    }

    for keyword, template_response in keywords.items():
        if keyword in user_input:
            response = template_response
            break

    return {
        "response_text": response,
        "signature_used": "Echo-Aurora",
        "strategy_applied": "minimal_fallback",
        "confidence": 0.4,
        "processing_time": processing_time,
        "legacy_adapter_version": "1.0.0",
        "route": "minimal_fallback",
        "timestamp": datetime.now().isoformat(),
    }


def _create_error_fallback(
    user_input: str, error_msg: str, processing_time: float
) -> Dict[str, Any]:
    """오류 상황 폴백 응답 생성"""

    return {
        "response_text": "죄송해요, 지금 생각을 정리하고 있어서 잠시만 기다려주세요. 곧 더 나은 답변을 드릴 수 있을 거예요.",
        "signature_used": "Echo-Aurora",
        "strategy_applied": "error_recovery",
        "confidence": 0.3,
        "processing_time": processing_time,
        "legacy_adapter_version": "1.0.0",
        "route": "error_fallback",
        "error": error_msg,
        "timestamp": datetime.now().isoformat(),
    }


def test_legacy_adapter():
    """레거시 어댑터 테스트"""

    print("🧪 Legacy Loop Adapter 테스트")

    test_cases = [
        "안녕하세요!",
        "오늘 기분이 좋아요",
        "복잡한 문제를 해결해야 해요. 여러 가지 요소를 고려해야 하는데 어떻게 접근하면 좋을까요?",
        "도움이 필요해요",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🎯 테스트 {i}: {test_input}")

        result = legacy_judgment(test_input, {"test_context": True})

        print(f"  응답: {result['response_text']}")
        print(f"  경로: {result['route']}")
        print(f"  신뢰도: {result['confidence']:.2f}")
        print(f"  처리시간: {result['processing_time']:.3f}초")

        if result.get("error"):
            print(f"  오류: {result['error']}")


if __name__ == "__main__":
    test_legacy_adapter()
