#!/usr/bin/env python3
"""
💬 Response Generator - 최적화된 응답 생성 시스템  
사전 구축된 템플릿으로 O(1) 응답 생성
"""

from typing import Dict, List
from functools import lru_cache

class OptimizedResponseGenerator:
    """최적화된 응답 생성기"""
    
    def __init__(self):
        self.response_templates = self._build_response_templates()
        self.tone_variations = self._build_tone_variations()
        
    @lru_cache(maxsize=300)
    def generate_response(self, strategy: str, tone: str, intent: str = None,
                         emotion: str = None) -> str:
        """
        빠른 응답 생성 (O(1) 템플릿 룩업)
        
        Args:
            strategy: 선택된 전략
            tone: 응답 톤
            intent: 사용자 의도
            emotion: 감지된 감정
            
        Returns:
            생성된 응답
        """
        # 기본 응답 템플릿 선택
        base_response = self.response_templates.get(strategy, {}).get(tone, 
            "도움이 되도록 최선을 다하겠습니다.")
            
        # 의도별 맞춤화
        if intent:
            customized = self._customize_for_intent(base_response, intent, emotion)
            return customized
            
        return base_response
    
    def _build_response_templates(self) -> Dict[str, Dict[str, str]]:
        """응답 템플릿 구축 (메모리에 한 번 로드)"""
        return {
            "empathetic": {
                "gentle": "이해할 수 있어요. 천천히 함께 생각해봐요.",
                "warm": "따뜻한 마음으로 들어드릴게요.", 
                "compassionate": "마음이 아프시겠어요. 제가 옆에 있어드릴게요.",
                "encouraging": "힘든 시간이지만 충분히 극복하실 수 있어요."
            },
            "analytical": {
                "objective": "상황을 객관적으로 분석해보겠습니다.",
                "logical": "논리적으로 접근해보면 다음과 같습니다.",
                "systematic": "단계별로 체계적으로 살펴보겠습니다.", 
                "measured": "신중하게 검토한 결과입니다."
            },
            "supportive": {
                "encouraging": "당신의 능력을 믿어요. 할 수 있어요!",
                "reassuring": "괜찮아요, 제가 도와드릴게요.",
                "motivating": "이미 훌륭한 첫걸음을 내디뎠네요.",
                "inspiring": "당신의 열정이 길을 만들어갈 거예요."
            },
            "balanced": {
                "neutral": "균형잡힌 관점에서 말씀드리면,",
                "moderate": "적절한 접근 방법을 찾아보겠습니다.",
                "harmonious": "조화로운 해결책을 모색해봐요.",
                "steady": "안정적으로 진행하는 것이 좋겠어요."
            }
        }
    
    def _build_tone_variations(self) -> Dict[str, List[str]]:
        """톤별 변형 패턴"""
        return {
            "encouraging": ["힘내세요!", "응원해요!", "파이팅!"],
            "gentle": ["부드럽게", "천천히", "조심스럽게"],
            "warm": ["따뜻하게", "정겨운", "온화한"], 
            "objective": ["객관적으로", "중립적으로", "사실에 근거해"]
        }
    
    @lru_cache(maxsize=100)
    def _customize_for_intent(self, base_response: str, intent: str, emotion: str) -> str:
        """의도별 응답 맞춤화"""
        intent_prefixes = {
            "avoidance_motive": "불안하신 마음 이해해요. ",
            "achievement_seeking": "목표를 향한 열정이 보여요. ", 
            "emotional_support": "마음이 힘드시겠어요. ",
            "problem_solving": "문제 해결을 위해 ",
            "creative_expression": "창의적인 아이디어네요. ",
            "decision_making": "중요한 선택이시군요. "
        }
        
        prefix = intent_prefixes.get(intent, "")
        return prefix + base_response

# 전역 인스턴스
_response_generator = OptimizedResponseGenerator()

def generate_response_fast(strategy: str, tone: str, intent: str = None, 
                          emotion: str = None) -> str:
    """빠른 응답 생성 (외부 인터페이스)"""
    return _response_generator.generate_response(strategy, tone, intent, emotion)
