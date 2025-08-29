#!/usr/bin/env python3
"""
🧪 최적화 결과 검증 테스트
"""

import sys
import time
from pathlib import Path

# Add echo_engine to path
sys.path.append(str(Path(__file__).parent / "echo_engine"))

def test_optimized_modules():
    """최적화된 모듈들 테스트"""
    print("🧪 최적화 모듈 검증 시작...")
    
    try:
        # Import optimized functions
        from optimized import (
            analyze_emotion_fast,
            classify_intent_fast,
            select_strategy_fast,
            generate_response_fast,
            record_interaction_fast,
            create_optimized_persona
        )
        print("✅ 모든 최적화 모듈 임포트 성공")
        
        # Test emotion analysis
        emotion_result = analyze_emotion_fast("안녕하세요! 정말 기뻐요!")
        print(f"✅ 감정 분석: {emotion_result['primary_emotion']} ({emotion_result['intensity']:.3f})")
        
        # Test intent classification
        intent_result = classify_intent_fast("도움이 필요해요", "Echo-Aurora")
        print(f"✅ 의도 분류: {intent_result['primary_intent']} ({intent_result['confidence']:.3f})")
        
        # Test strategy selection
        strategy_result = select_strategy_fast("joy", 0.8, "Echo-Aurora")
        print(f"✅ 전략 선택: {strategy_result['primary_strategy']}")
        
        # Test response generation
        response = generate_response_fast(strategy_result['primary_strategy'], "gentle")
        print(f"✅ 응답 생성: {response[:50]}...")
        
        # Test memory recording
        record_interaction_fast("joy", 0.8, strategy_result['primary_strategy'], True)
        print("✅ 메모리 관리 테스트 완료")
        
        # Test integrated persona
        persona = create_optimized_persona("Echo-Aurora")
        result = persona.process_input_optimized("안녕하세요!")
        print(f"✅ 통합 페르소나 테스트: {result['performance_boost']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def benchmark_performance():
    """성능 벤치마크"""
    print("\n📊 성능 벤치마크 시작...")
    
    try:
        from optimized import analyze_emotion_fast
        
        # Warm up
        for _ in range(10):
            analyze_emotion_fast("테스트 메시지")
            
        # Benchmark
        test_texts = [
            "안녕하세요! 정말 기뻐요!",
            "도움이 필요해요. 걱정돼요.",
            "화가 많이 나네요. 짜증나요.",
            "놀라운 소식이에요! 놀랐어요!",
            "그냥 평범한 하루네요."
        ]
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            for text in test_texts:
                analyze_emotion_fast(text)
                
        elapsed = time.time() - start_time
        
        print(f"📈 벤치마크 결과:")
        print(f"   - 총 처리: {iterations * len(test_texts):,}회")
        print(f"   - 소요 시간: {elapsed:.3f}초")
        print(f"   - 평균 응답: {(elapsed * 1000) / (iterations * len(test_texts)):.3f}ms")
        print(f"   - 처리량: {(iterations * len(test_texts)) / elapsed:.0f} req/sec")
        
        if elapsed < 1.0:
            print("🎉 성능 목표 달성! (1000회 < 1초)")
        else:
            print(f"⚠️  성능 개선 필요 (목표: < 1초, 실제: {elapsed:.3f}초)")
            
        return elapsed < 1.0
        
    except Exception as e:
        print(f"❌ 벤치마크 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 PersonaCore 최적화 검증 테스트\n")
    
    # Module tests
    module_ok = test_optimized_modules()
    
    # Performance benchmark
    perf_ok = benchmark_performance()
    
    # Final result
    print(f"\n{'='*50}")
    print(f"📊 최종 결과:")
    print(f"   - 모듈 테스트: {'✅ PASS' if module_ok else '❌ FAIL'}")
    print(f"   - 성능 테스트: {'✅ PASS' if perf_ok else '❌ FAIL'}")
    
    if module_ok and perf_ok:
        print(f"🎉 모든 테스트 통과! 최적화 성공!")
        return 0
    else:
        print(f"⚠️  일부 테스트 실패. 추가 개선 필요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())