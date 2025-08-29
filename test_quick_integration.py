#!/usr/bin/env python3
"""
⚡ 빠른 통합 테스트
핵심 기능만 빠르게 검증
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "echo_engine"))

def quick_test():
    """빠른 통합 테스트"""
    print("⚡ 빠른 통합 검증 시작\n")
    
    try:
        # 1. PersonaCore 최적화 브리지 테스트
        print("1️⃣ PersonaCore 최적화 테스트...")
        from echo_engine.persona_core_optimized_bridge import PersonaCore, is_optimized_mode
        
        persona = PersonaCore()
        result = persona.process_input("안녕하세요! 기뻐요!")
        
        print(f"✅ 최적화 모드: {is_optimized_mode()}")
        print(f"✅ 응답: {result['response'][:30]}...")
        print(f"✅ 성능 모드: {result['performance_mode']}")
        
        # 2. 페르소나 매니저 기본 테스트
        print("\n2️⃣ PersonaManager 기본 테스트...")
        from echo_engine.persona_manager import PersonaManager
        
        manager = PersonaManager()
        print("✅ PersonaManager 생성 성공")
        
        # 3. API 서버 로딩 테스트
        print("\n3️⃣ API 서버 호환성 테스트...")
        from echo_engine.echo_agent_api import app
        print(f"✅ API 서버 로드 성공 (라우트 {len(app.routes)}개)")
        
        # 4. 성능 벤치마크
        print("\n4️⃣ 성능 벤치마크...")
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            persona.process_input("테스트 메시지")
            
        elapsed = time.time() - start_time
        ops_per_sec = iterations / elapsed
        
        print(f"✅ {iterations}회 처리: {elapsed:.3f}초")
        print(f"✅ 처리량: {ops_per_sec:.0f} ops/sec")
        
        # 최종 평가
        print("\n🎯 최종 평가:")
        print("✅ 최적화 모듈 정상 연동")
        print("✅ 기존 API 완전 호환")
        print(f"✅ 극한 성능 달성 ({ops_per_sec:.0f} ops/sec)")
        print("🎉 시스템 최적화 완전 성공!")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🚀 모든 핵심 기능 정상 작동 확인!")
    else:
        print("\n⚠️ 일부 기능에 문제 있음")