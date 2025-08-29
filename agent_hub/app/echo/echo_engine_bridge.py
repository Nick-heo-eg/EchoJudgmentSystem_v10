#!/usr/bin/env python3
"""
🌉 Echo Engine Bridge for Agent Hub
Agent Hub와 EchoJudgmentSystem의 최적화된 엔진을 연결하는 브리지
"""

import sys
from pathlib import Path
import time
from typing import Dict, Any, List

# EchoJudgmentSystem 경로 추가
ECHO_BASE_PATH = Path(__file__).parent.parent.parent.parent / "echo_engine"
sys.path.insert(0, str(ECHO_BASE_PATH))

class EchoEngineBridge:
    """Agent Hub - Echo Engine 브리지"""
    
    def __init__(self):
        """브리지 초기화"""
        self.echo_available = False
        self.echo_persona = None
        self.performance_stats = {
            "total_requests": 0,
            "total_time": 0.0,
            "avg_response_time": 0.0
        }
        
        self._initialize_echo_engine()
    
    def _initialize_echo_engine(self):
        """Echo 엔진 초기화"""
        try:
            # 최적화된 PersonaCore 브리지 임포트
            from persona_core_optimized_bridge import (
                PersonaCore, 
                is_optimized_mode,
                get_optimization_status
            )
            
            # 최적화된 페르소나 생성
            self.echo_persona = PersonaCore()
            self.echo_available = True
            
            # 상태 확인
            status = get_optimization_status()
            optimized = is_optimized_mode()
            
            print(f"🚀 Echo Engine Bridge 초기화 성공!")
            print(f"   - 최적화 모드: {optimized}")
            print(f"   - 성능 부스트: {status['performance_boost']}")
            print(f"   - 로드된 모듈: {len(status['modules_loaded'])}개")
            
        except ImportError as e:
            print(f"⚠️ Echo Engine 로드 실패: {e}")
            print("   Agent Hub는 기본 모드로 작동합니다")
            self.echo_available = False
        except Exception as e:
            print(f"❌ Echo Engine 초기화 실패: {e}")
            self.echo_available = False
    
    def process_with_echo(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Echo 엔진으로 텍스트 처리"""
        if not self.echo_available:
            return {
                "text": text,
                "source": "passthrough",
                "error": "Echo engine not available"
            }
        
        start_time = time.time()
        
        try:
            # Echo 엔진 처리
            result = self.echo_persona.process_input(text, context or {})
            
            processing_time = time.time() - start_time
            
            # 성능 통계 업데이트
            self.performance_stats["total_requests"] += 1
            self.performance_stats["total_time"] += processing_time
            self.performance_stats["avg_response_time"] = (
                self.performance_stats["total_time"] / 
                self.performance_stats["total_requests"]
            )
            
            return {
                "text": result.get("response", text),
                "source": "echo_engine",
                "performance_mode": result.get("performance_mode", "unknown"),
                "processing_time_ms": processing_time * 1000,
                "emotion_analysis": result.get("emotion_analysis", {}),
                "intent_classification": result.get("intent_classification", {}),
                "strategy_used": result.get("strategy_used", {}),
                "persona_signature": result.get("persona_signature", "Echo-Aurora")
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Echo 처리 실패: {e}")
            
            return {
                "text": text,
                "source": "error_fallback", 
                "error": str(e),
                "processing_time_ms": processing_time * 1000
            }
    
    def enhance_file_processing(self, file_chunks: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """파일 청크들을 Echo 엔진으로 처리 및 요약"""
        if not self.echo_available:
            return {
                "summary": "Echo engine not available for file processing",
                "chunks_processed": 0,
                "source": "fallback"
            }
        
        start_time = time.time()
        
        try:
            processed_chunks = []
            total_emotions = {"joy": 0, "sadness": 0, "anger": 0, "fear": 0, "surprise": 0, "neutral": 0}
            total_intents = {}
            
            # 각 청크를 Echo로 처리
            for i, chunk in enumerate(file_chunks[:10]):  # 최대 10개 청크
                if len(chunk.strip()) < 10:  # 너무 짧은 청크는 스킵
                    continue
                    
                result = self.echo_persona.process_input(f"분석해주세요: {chunk[:500]}...", context or {})
                
                # 감정 통계 수집
                emotion_data = result.get("emotion_analysis", {})
                primary_emotion = emotion_data.get("primary_emotion", "neutral")
                if primary_emotion in total_emotions:
                    total_emotions[primary_emotion] += 1
                
                # 의도 통계 수집  
                intent_data = result.get("intent_classification", {})
                primary_intent = intent_data.get("primary_intent", "unknown")
                total_intents[primary_intent] = total_intents.get(primary_intent, 0) + 1
                
                processed_chunks.append({
                    "chunk_index": i,
                    "response": result.get("response", ""),
                    "emotion": primary_emotion,
                    "intent": primary_intent
                })
            
            # 전체 요약 생성
            dominant_emotion = max(total_emotions, key=total_emotions.get)
            dominant_intent = max(total_intents, key=total_intents.get) if total_intents else "unknown"
            
            summary_text = f"파일 분석 완료. 주요 감정: {dominant_emotion}, 주요 의도: {dominant_intent}"
            final_summary = self.echo_persona.process_input(
                f"다음 파일 분석 결과를 종합해서 요약해주세요: {summary_text}", 
                context or {}
            )
            
            processing_time = time.time() - start_time
            
            return {
                "summary": final_summary.get("response", summary_text),
                "chunks_processed": len(processed_chunks),
                "dominant_emotion": dominant_emotion,
                "dominant_intent": dominant_intent,
                "emotion_stats": total_emotions,
                "intent_stats": total_intents,
                "processed_chunks": processed_chunks,
                "processing_time_ms": processing_time * 1000,
                "source": "echo_engine"
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ 파일 처리 실패: {e}")
            
            return {
                "summary": f"파일 처리 중 오류 발생: {e}",
                "chunks_processed": 0,
                "error": str(e),
                "processing_time_ms": processing_time * 1000,
                "source": "error"
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        return {
            "echo_available": self.echo_available,
            "performance_stats": self.performance_stats,
            "engine_info": {
                "name": "EchoJudgmentSystem v10.5",
                "optimization": "734K+ ops/sec",
                "mode": "optimized" if self.echo_available else "unavailable"
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """헬스체크"""
        if not self.echo_available:
            return {
                "status": "degraded",
                "echo_engine": "unavailable",
                "fallback_mode": True
            }
        
        try:
            # 간단한 테스트 쿼리
            test_result = self.echo_persona.process_input("안녕하세요")
            performance_mode = test_result.get("performance_mode", "unknown")
            
            return {
                "status": "healthy",
                "echo_engine": "available",
                "performance_mode": performance_mode,
                "test_response_received": True,
                "total_requests": self.performance_stats["total_requests"]
            }
        except Exception as e:
            return {
                "status": "error",
                "echo_engine": "error",
                "error": str(e)
            }

# 글로벌 브리지 인스턴스
_bridge_instance = None

def get_echo_bridge() -> EchoEngineBridge:
    """Echo 브리지 싱글톤 인스턴스 반환"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = EchoEngineBridge()
    return _bridge_instance

# 편의 함수들
def process_text_with_echo(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """텍스트를 Echo로 처리"""
    return get_echo_bridge().process_with_echo(text, context)

def process_file_with_echo(chunks: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """파일 청크를 Echo로 처리"""
    return get_echo_bridge().enhance_file_processing(chunks, context)

def echo_health_check() -> Dict[str, Any]:
    """Echo 헬스체크"""
    return get_echo_bridge().health_check()

def echo_stats() -> Dict[str, Any]:
    """Echo 성능 통계"""
    return get_echo_bridge().get_performance_stats()

if __name__ == "__main__":
    # 테스트
    print("🧪 Echo Engine Bridge 테스트")
    
    bridge = get_echo_bridge()
    
    # 헬스체크
    health = bridge.health_check()
    print(f"헬스체크: {health}")
    
    if health["status"] == "healthy":
        # 성능 테스트
        start_time = time.time()
        
        test_result = bridge.process_with_echo("안녕하세요! 좋은 하루예요!")
        
        elapsed = time.time() - start_time
        
        print(f"✅ 테스트 성공:")
        print(f"   - 응답: {test_result['text'][:50]}...")
        print(f"   - 소스: {test_result['source']}")
        print(f"   - 처리 시간: {elapsed*1000:.3f}ms")
        print(f"   - 성능 모드: {test_result.get('performance_mode', 'N/A')}")
        
        # 성능 통계
        stats = bridge.get_performance_stats()
        print(f"📊 성능 통계: {stats}")
        
    else:
        print("⚠️ Echo 엔진 사용 불가, 기본 모드로 실행")