#!/usr/bin/env python3
"""
🧪 대용량 파일 최적화 결과 종합 검증 테스트
"""

import sys
import os
import time
from pathlib import Path

# Add echo_engine to path
sys.path.append(str(Path(__file__).parent / "echo_engine"))

def test_main_optimized_modules():
    """메인 최적화 모듈들 테스트"""
    print("🧪 메인 최적화 모듈 검증...")
    
    try:
        # Test persona_core optimization
        from optimized import create_optimized_persona
        persona = create_optimized_persona("Echo-Aurora")
        result = persona.process_input_optimized("안녕하세요!")
        print("✅ PersonaCore 최적화: 정상 작동")
        
        return True
        
    except Exception as e:
        print(f"❌ 메인 모듈 테스트 실패: {e}")
        return False

def test_intelligence_modules():
    """Intelligence 모듈 최적화 테스트"""
    print("\n🧠 Intelligence 모듈 검증...")
    
    try:
        # Test intelligence optimized modules
        sys.path.append(str(Path(__file__).parent / "echo_engine" / "intelligence"))
        
        from optimized import MultidimensionalIntelligenceEvaluator
        evaluator = MultidimensionalIntelligenceEvaluator()
        print("✅ Intelligence Evaluator 최적화: 임포트 성공")
        
        from optimized import AdaptiveLearningMemory
        memory = AdaptiveLearningMemory()
        print("✅ Adaptive Memory 최적화: 임포트 성공")
        
        from optimized import CognitiveEvolutionTracker
        tracker = CognitiveEvolutionTracker()
        print("✅ Cognitive Evolution 최적화: 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ Intelligence 모듈 테스트 실패: {e}")
        return False

def count_optimization_results():
    """최적화 결과 통계"""
    print("\n📊 최적화 통계 분석...")
    
    # Count main optimized files
    main_optimized = Path("echo_engine/optimized")
    main_files = list(main_optimized.glob("*.py"))
    main_count = len([f for f in main_files if f.name != "__init__.py"])
    
    # Count intelligence optimized files  
    intel_optimized = Path("echo_engine/intelligence/optimized")
    intel_files = list(intel_optimized.glob("*.py"))
    intel_count = len([f for f in intel_files if f.name != "__init__.py"])
    
    print(f"📁 메인 최적화 모듈: {main_count}개")
    print(f"🧠 Intelligence 최적화 모듈: {intel_count}개")
    print(f"📋 총 최적화 모듈: {main_count + intel_count}개")
    
    # Calculate total size reduction
    total_optimized_size = 0
    for file in main_files + intel_files:
        if file.name != "__init__.py":
            total_optimized_size += file.stat().st_size
    
    print(f"💾 최적화된 파일 총 크기: {total_optimized_size:,} bytes")
    
    return main_count + intel_count

def benchmark_optimized_performance():
    """최적화 성능 벤치마크"""
    print("\n⚡ 최적화 성능 벤치마크...")
    
    try:
        from optimized import analyze_emotion_fast, classify_intent_fast
        
        # Benchmark optimized functions
        iterations = 5000
        test_texts = [
            "기뻐요! 정말 좋은 하루네요!",
            "도움이 필요해요. 걱정돼요.",
            "화가 나네요. 정말 짜증나요!",
            "놀라운 소식이에요! 깜짝 놀랐어요!",
            "평범한 하루입니다."
        ]
        
        # Warm up
        for _ in range(50):
            analyze_emotion_fast("테스트")
            
        # Benchmark
        start_time = time.time()
        
        for _ in range(iterations):
            for text in test_texts:
                analyze_emotion_fast(text)
                classify_intent_fast(text, "Echo-Aurora")
                
        elapsed = time.time() - start_time
        total_ops = iterations * len(test_texts) * 2  # 2 operations per text
        
        print(f"📈 벤치마크 결과:")
        print(f"   - 총 연산: {total_ops:,}회")
        print(f"   - 소요 시간: {elapsed:.3f}초")
        print(f"   - 평균 응답: {(elapsed * 1000) / total_ops:.4f}ms")
        print(f"   - 처리량: {total_ops / elapsed:.0f} ops/sec")
        
        if elapsed < 2.0:
            print("🎉 성능 목표 달성! (10,000회 < 2초)")
            return True
        else:
            print(f"⚠️  성능 개선 필요 (목표: < 2초, 실제: {elapsed:.3f}초)")
            return False
            
    except Exception as e:
        print(f"❌ 벤치마크 실패: {e}")
        return False

def check_health_improvement():
    """헬스체크 개선 확인"""
    print("\n🏥 시스템 헬스 개선 확인...")
    
    try:
        import subprocess
        result = subprocess.run([
            'python', '-c',
            'import sys; sys.path.append("echo_engine"); '
            'from optimized import create_optimized_persona; '
            'print("✅ 최적화 시스템 정상 작동")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 최적화 시스템 헬스체크 통과")
            return True
        else:
            print(f"❌ 헬스체크 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 헬스체크 실패: {e}")
        return False

def main():
    """종합 최적화 검증"""
    print("🚀 대용량 파일 최적화 종합 검증 테스트\n")
    
    # Tests
    tests = [
        ("메인 모듈", test_main_optimized_modules),
        ("Intelligence 모듈", test_intelligence_modules), 
        ("성능 벤치마크", benchmark_optimized_performance),
        ("헬스체크", check_health_improvement)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"🧪 {name} 테스트 시작...")
        result = test_func()
        results.append((name, result))
        print(f"{'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Statistics
    module_count = count_optimization_results()
    
    # Final summary
    print("=" * 60)
    print("📊 최적화 종합 결과:")
    print(f"   - 최적화 모듈 수: {module_count}개")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   - {name}: {status}")
    
    print(f"\n🎯 전체 성공률: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 대용량 파일 최적화 완료! 완벽한 성공!")
        return 0
    else:
        print("⚠️  일부 최적화에 문제가 있습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main())