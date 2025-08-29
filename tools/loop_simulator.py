#!/usr/bin/env python3
"""
🧪 Loop Simulator - 판단 루프 전체 흐름 테스트
감정 추론 기반 공명 응답 생성의 전체 흐름을 테스트
"""

import argparse
import sys
import os
import re

# Echo 엔진 모듈들
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_engine.resonance_synthesizer import ResonanceSynthesizer
from echo_engine.emotion_infer import (
    EmotionInferenceEngine,
    EmotionContext,
    to_emotion_context,
)

# 감정 흐름 추적 모듈
try:
    from echo_engine.emotion_flow_tracker import EmotionFlowTracker

    EMOTION_FLOW_AVAILABLE = True
except ImportError:
    print("⚠️ Emotion Flow Tracker를 사용할 수 없습니다.")
    EMOTION_FLOW_AVAILABLE = False


def simulate_loop(input_text: str, signature: str):
    print("\n🧪 판단 루프 시뮬레이션 시작")
    print(f"   ✍️ 입력: {input_text}")
    print(f"   🎭 시그니처: {signature}")

    # 1. 실제 감정 추론 엔진 사용 (향상된 처리)
    print(f"\n💭 1단계: 감정 추론 실행")
    try:
        emotion_engine = EmotionInferenceEngine()
        inference_result = emotion_engine.infer_emotion(input_text)

        print(f"   🎯 주요 감정: {inference_result.primary_emotion}")
        print(f"   📊 신뢰도: {inference_result.confidence:.3f}")
        print(f"   🔥 강도: {inference_result.emotional_intensity:.3f}")
        print(f"   🔮 부차 감정: {inference_result.secondary_emotions}")
        print(f"   📈 리듬 패턴: {inference_result.temporal_pattern}")

        # EmotionInferenceResult를 EmotionContext로 변환
        emotion_context = to_emotion_context(inference_result, {"input": input_text})

    except Exception as e:
        print(f"   ⚠️ 감정 추론 실패, fallback 모드로 전환: {e}")
        # Fallback: 간단한 키워드 기반 추론
        primary_emotion = (
            "sadness"
            if any(word in input_text for word in ["지쳤", "슬퍼", "힘들", "우울"])
            else (
                "anger"
                if any(word in input_text for word in ["화", "짜증", "열받"])
                else (
                    "joy"
                    if any(
                        word in input_text for word in ["기쁘", "좋아", "행복", "신나"]
                    )
                    else "neutral"
                )
            )
        )

        emotion_context = EmotionContext(
            primary_emotion=primary_emotion,
            intensity=0.72,
            secondary_emotions=[],
            confidence=0.85,
            temporal_pattern="stable",
            conversation_context={"input": input_text},
        )

        print(f"   🎯 Fallback 감정: {emotion_context.primary_emotion}")

    # 2. 공명 응답 생성
    print(f"\n🎵 2단계: 공명 응답 생성")
    try:
        synthesizer = ResonanceSynthesizer()
        result = synthesizer.synthesize_response(
            emotion_context, signature, conversation_topic=input_text
        )

        print(f"   ✅ {len(result)}개 레벨 응답 생성 완료")

    except Exception as e:
        print(f"   ⚠️ 공명 응답 생성 실패: {e}")
        return

    # 3. 결과 출력
    print(f"\n✅ 판단 루프 결과:")
    print(f"   📈 총 레벨: {len(result)}개")

    for level, response in enumerate(result, start=1):
        print(f"\n📝 Level {level} 응답:")
        print(f"   💬 내용: {response.response_text}")
        print(f"   💡 공명도: {response.resonance_score:.3f}")
        print(f"   ⚖️ 정렬도: {response.emotional_alignment:.3f}")
        print(f"   🔍 설명: {response.meta_explanation}")

    # 4. 종합 평가
    if result:
        max_resonance = max(r.resonance_score for r in result)
        avg_alignment = sum(r.emotional_alignment for r in result) / len(result)

        print(f"\n📊 종합 평가:")
        print(f"   🏆 최고 공명도: {max_resonance:.3f}")
        print(f"   📈 평균 정렬도: {avg_alignment:.3f}")
        print(
            f"   🎯 시그니처 적합성: {'높음' if max_resonance > 0.8 else '보통' if max_resonance > 0.6 else '낮음'}"
        )


def simulate_multi_input_flow(multi_input: str, signature: str):
    """연속 입력의 감정 흐름 분석 모드"""
    print("\n🌊 다중 입력 감정 흐름 분석 시작")
    print(f"   ✍️ 연속 입력: {multi_input}")
    print(f"   🎭 분석 시그니처: {signature}")

    if not EMOTION_FLOW_AVAILABLE:
        print("❌ Emotion Flow Tracker가 사용 불가능합니다.")
        print("💡 대신 단일 입력 분석으로 실행합니다.")
        simulate_loop(multi_input, signature)
        return

    # 1. 자연어 텍스트를 감정 흐름으로 분석
    print(f"\n🔍 1단계: 자연어 감정 흐름 분석")
    try:
        tracker = EmotionFlowTracker()
        flow_result = tracker.analyze_natural_text(multi_input, signature)

        print(f"   ✅ 감정 흐름 분석 완료")
        print(f"   📊 지배적 감정: {flow_result.dominant_emotions}")
        print(f"   🔄 전이 패턴: {len(flow_result.transitions)}개")
        print(f"   📈 시간 패턴: {flow_result.temporal_pattern}")
        print(f"   💫 흐름 응집성: {flow_result.flow_coherence_score:.3f}")
        print(f"   🧩 감정 복잡도: {flow_result.emotional_complexity}")

        # 2. 각 감정 단계별 공명 응답 생성
        print(f"\n🎵 2단계: 흐름별 공명 응답 생성")
        synthesizer = ResonanceSynthesizer()

        for i, timeline_entry in enumerate(
            flow_result.narrative_timeline[:3]
        ):  # 상위 3개만 처리
            emotion = timeline_entry["emotion"]
            text_preview = timeline_entry["text_preview"]
            intensity = timeline_entry["intensity"]

            print(f"\n   📝 타임라인 {i+1}: {timeline_entry['narrative_phase']}")
            print(f"      감정: {emotion} (강도: {intensity:.2f})")
            print(f"      텍스트: {text_preview}")

            # 해당 감정에 대한 공명 응답 생성
            emotion_context = EmotionContext(
                primary_emotion=emotion,
                intensity=intensity,
                secondary_emotions=[],
                confidence=timeline_entry["confidence"],
                temporal_pattern=flow_result.temporal_pattern,
                conversation_context={
                    "timeline_position": i,
                    "phase": timeline_entry["narrative_phase"],
                },
            )

            try:
                responses = synthesizer.synthesize_response(
                    emotion_context, signature, conversation_topic=text_preview
                )
                print(f"      ✅ {len(responses)}개 레벨 응답 생성")

                # 최고 레벨 응답만 출력
                if responses:
                    best_response = max(responses, key=lambda r: r.resonance_score)
                    print(f"      💬 공명 응답: {best_response.response_text}")
                    print(f"      💡 공명도: {best_response.resonance_score:.3f}")

            except Exception as e:
                print(f"      ⚠️ 공명 응답 생성 실패: {e}")

        # 3. 전체 감정 흐름 요약
        print(f"\n📊 3단계: 전체 감정 흐름 종합 분석")
        print(f"   🏆 피크 감정들: {flow_result.peak_emotions}")
        print(f"   🎯 시그니처 공명 맵:")
        for emotion, resonance in sorted(
            flow_result.signature_resonance_map.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]:
            print(f"      {emotion}: {resonance:.3f}")

        print(f"\n✅ 다중 입력 감정 흐름 분석 완료!")

    except Exception as e:
        print(f"❌ 감정 흐름 분석 실패: {e}")
        print("💡 단일 입력 분석으로 대체 실행합니다.")
        simulate_loop(multi_input, signature)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="입력 문장")
    parser.add_argument("--signature", type=str, default="Selene", help="시그니처")
    parser.add_argument(
        "--multi_input",
        type=str,
        help="연속 입력 감정 흐름 분석 (예: '아침엔 괜찮았어, 근데 점점 불안해졌어')",
    )
    args = parser.parse_args()

    if args.multi_input:
        simulate_multi_input_flow(args.multi_input, args.signature)
    elif args.input:
        simulate_loop(args.input, args.signature)
    else:
        print("❌ --input 또는 --multi_input 중 하나를 제공해주세요.")
        print("💡 예시:")
        print(
            "   python tools/loop_simulator.py --input '오늘 너무 힘들어요' --signature Selene"
        )
        print(
            "   python tools/loop_simulator.py --multi_input '아침엔 괜찮았어, 근데 점점 불안해졌어, 결국 지쳐버렸지' --signature Selene"
        )
