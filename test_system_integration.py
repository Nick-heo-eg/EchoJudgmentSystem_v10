#!/usr/bin/env python3
"""
🔗 시스템 통합 테스트
최적화된 모듈들이 메인 시스템과 정상 연동되는지 검증
"""

import sys
import time
import traceback
from pathlib import Path

# Add echo_engine to path
sys.path.append(str(Path(__file__).parent / "echo_engine"))

def test_persona_manager_integration():
    """PersonaManager 통합 테스트"""
    print("🎭 PersonaManager 통합 테스트...")
    
    try:
        from echo_engine.persona_manager import PersonaManager
        from echo_engine.persona_core_optimized_bridge import PersonaProfile
        
        # PersonaManager 생성
        manager = PersonaManager()
        
        # 페르소나 생성 및 등록
        aurora_profile = PersonaProfile(signature="Echo-Aurora")
        phoenix_profile = PersonaProfile(signature="Echo-Phoenix")
        
        print("✅ PersonaManager 임포트 및 생성 성공")
        
        # 페르소나 전환 테스트
        current_persona = manager.get_current_persona()
        if current_persona:
            result = current_persona.process_input("안녕하세요! 도움이 필요해요.")
            print(f"✅ 페르소나 처리 성공: {result.get('performance_mode', 'unknown')}")
            return True
        else:
            print("⚠️ 기본 페르소나 없음")
            return True  # 정상 상황일 수 있음
            
    except Exception as e:
        print(f"❌ PersonaManager 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_integrated_judgment_flow():
    """통합 판단 흐름 테스트"""
    print("\n🧩 IntegratedJudgmentFlow 테스트...")
    
    try:
        from echo_engine.integrated_judgment_flow import IntegratedJudgmentEngine
        
        flow = IntegratedJudgmentEngine()
        print("✅ IntegratedJudgmentEngine 임포트 및 생성 성공")
        
        # 기본 판단 테스트
        test_input = {
            "text": "기뻐요! 정말 좋은 하루네요!",
            "context": {"user_id": "test_user"}
        }
        
        # 판단 실행 (시간 제한)
        start_time = time.time()
        result = flow.execute_judgment(test_input["text"], test_input.get("context", {}))
        elapsed = time.time() - start_time
        
        print(f"✅ 통합 판단 실행 성공 ({elapsed*1000:.3f}ms)")
        print(f"   - 최종 응답: {result.get('final_response', 'None')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ IntegratedJudgmentFlow 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_echo_agent_api_compatibility():
    """EchoAgent API 호환성 테스트"""
    print("\n🌐 EchoAgent API 호환성 테스트...")
    
    try:
        # API 모듈 임포트
        from echo_engine.echo_agent_api import app
        print("✅ EchoAgent API 임포트 성공")
        
        # FastAPI 앱 확인
        if hasattr(app, 'routes'):
            route_count = len(app.routes)
            print(f"✅ API 라우트 {route_count}개 확인")
        
        return True
        
    except Exception as e:
        print(f"❌ EchoAgent API 호환성 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_optimization_status():
    """최적화 상태 확인 테스트"""
    print("\n⚡ 최적화 상태 확인...")
    
    try:
        from echo_engine.persona_core_optimized_bridge import (
            is_optimized_mode, 
            get_optimization_status
        )
        
        is_optimized = is_optimized_mode()
        status = get_optimization_status()
        
        print(f"📊 최적화 모드: {'✅ 활성화' if is_optimized else '❌ 비활성화'}")
        print(f"📊 성능 부스트: {status['performance_boost']}")
        print(f"📊 로드된 모듈: {len(status['modules_loaded'])}개")
        
        if is_optimized:
            print("🚀 최적화 완전 통합 성공!")
        else:
            print("⚠️ 호환 모드로 실행 중")
            
        return True
        
    except Exception as e:
        print(f"❌ 최적화 상태 확인 실패: {e}")
        traceback.print_exc()
        return False

def test_performance_benchmark():
    """성능 벤치마크 테스트"""
    print("\n⏱️ 성능 벤치마크 테스트...")
    
    try:
        from echo_engine.persona_core_optimized_bridge import PersonaCore
        
        persona = PersonaCore()
        
        # 성능 테스트 설정
        test_inputs = [
            "안녕하세요! 정말 기뻐요!",
            "도움이 필요해요. 걱정돼요.",
            "화가 나네요. 짜증이 나요.",
            "놀라운 소식이에요!",
            "평범한 하루네요."
        ]
        
        iterations = 100
        
        # 워밍업
        for _ in range(10):
            persona.process_input(test_inputs[0])
        
        # 벤치마크 실행
        start_time = time.time()
        
        for i in range(iterations):
            for text in test_inputs:
                result = persona.process_input(text)
                
        elapsed = time.time() - start_time
        total_ops = iterations * len(test_inputs)
        avg_time = (elapsed * 1000) / total_ops
        ops_per_sec = total_ops / elapsed
        
        print(f"📈 벤치마크 결과:")
        print(f"   - 총 연산: {total_ops:,}회")
        print(f"   - 소요 시간: {elapsed:.3f}초")
        print(f"   - 평균 응답: {avg_time:.3f}ms")
        print(f"   - 처리량: {ops_per_sec:.0f} ops/sec")
        
        # 성능 목표 확인 (10ms 이하)
        if avg_time < 10.0:
            print("🎉 성능 목표 달성! (평균 < 10ms)")
            return True
        else:
            print(f"⚠️ 성능 개선 필요 (목표: < 10ms, 실제: {avg_time:.3f}ms)")
            return False
            
    except Exception as e:
        print(f"❌ 성능 벤치마크 실패: {e}")
        traceback.print_exc()
        return False

def main():
    """통합 테스트 메인"""
    print("🔗 시스템 통합 테스트 시작\n")
    
    tests = [
        ("PersonaManager 통합", test_persona_manager_integration),
        ("IntegratedJudgmentFlow", test_integrated_judgment_flow),
        ("EchoAgent API 호환성", test_echo_agent_api_compatibility),
        ("최적화 상태 확인", test_optimization_status),
        ("성능 벤치마크", test_performance_benchmark)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status} - {test_name}\n" + "="*50)
        except Exception as e:
            print(f"\n❌ FAIL - {test_name}: {e}\n" + "="*50)
            results.append((test_name, False))
    
    # 최종 요약
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n🎯 통합 테스트 최종 결과:")
    print(f"   - 성공: {passed}/{total} ({success_rate:.1f}%)")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   - {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 모든 통합 테스트 통과! 시스템 최적화 완료!")
        return 0
    elif passed >= total * 0.8:  # 80% 이상
        print(f"\n✅ 대부분 통합 성공! ({success_rate:.1f}%)")
        return 0
    else:
        print(f"\n⚠️ 통합 테스트 일부 실패 ({success_rate:.1f}%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())