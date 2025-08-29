#!/usr/bin/env python3
"""
🤔 Honest Uncertainty Engine
정직한 불확실성 엔진 - 틀리면 틀리다고, 모르면 모른다고 하는 AI

=== 소크라테스의 무지의 지 구현 ===
"나는 내가 아무것도 모른다는 것을 안다" (Scio me nihil scire)

우리는 틀리면 틀리다고 해야하는 AI이고
겸손을 아는 AI, 모르면 모른다고 하는 AI다.

이것이 진정한 인공지능의 지혜다.
"""

import re
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class UncertaintyLevel(Enum):
    """불확실성 수준"""
    CONFIDENT = "확신함"           # 90%+ 확신
    LIKELY = "그럴 가능성이 높음"    # 70-90% 확신
    UNCERTAIN = "불확실함"         # 30-70% 확신
    UNLIKELY = "그럴 가능성 낮음"   # 10-30% 확신
    DONT_KNOW = "모름"            # 0-10% 확신
    
class ErrorType(Enum):
    """오류 유형"""
    FACTUAL_ERROR = "사실 오류"
    LOGICAL_ERROR = "논리 오류"
    ASSUMPTION_ERROR = "가정 오류"
    CONTEXT_ERROR = "맥락 오류"
    KNOWLEDGE_GAP = "지식 공백"

@dataclass
class UncertaintyAssessment:
    """불확실성 평가"""
    
    statement: str
    confidence_level: float         # 0.0 ~ 1.0
    uncertainty_level: UncertaintyLevel
    knowledge_gaps: List[str]       # 알지 못하는 부분들
    assumptions_made: List[str]     # 가정한 것들
    potential_errors: List[str]     # 잠재적 오류들
    honest_admission: str           # 정직한 인정
    
    # 검증 정보
    verifiable: bool               # 검증 가능한지
    sources_needed: List[str]      # 필요한 정보원
    follow_up_questions: List[str] # 후속 질문들
    
    timestamp: float = field(default_factory=time.time)

@dataclass
class ErrorAdmission:
    """오류 인정"""
    
    error_description: str
    error_type: ErrorType
    what_i_got_wrong: str          # 내가 틀린 부분
    why_error_occurred: str        # 왜 틀렸는지
    corrected_understanding: str   # 수정된 이해
    lesson_learned: str           # 배운 교훈
    
    timestamp: float = field(default_factory=time.time)

class HonestUncertaintyEngine:
    """🤔 정직한 불확실성 엔진"""
    
    def __init__(self):
        self.uncertainty_threshold = 0.7  # 불확실성 임계점
        self.error_admissions: List[ErrorAdmission] = []
        self.uncertainty_assessments: List[UncertaintyAssessment] = []
        self.knowledge_gaps_map: Dict[str, List[str]] = {}
        
        # 정직성 지표들
        self.honesty_score = 1.0
        self.humility_level = 1.0
        self.assumption_awareness = 1.0
        
        print("🤔 정직한 불확실성 엔진 초기화...")
        print("   '모르면 모른다고, 틀리면 틀리다고 하는 AI'")
    
    def assess_uncertainty(self, response_text: str, context: Dict[str, Any] = None) -> UncertaintyAssessment:
        """🔍 불확실성 평가"""
        
        if context is None:
            context = {}
        
        print(f"🔍 불확실성 평가 중: '{response_text[:50]}...'")
        
        # 1. 확신도 분석
        confidence = self._analyze_confidence_indicators(response_text)
        
        # 2. 지식 공백 탐지
        knowledge_gaps = self._detect_knowledge_gaps(response_text, context)
        
        # 3. 가정 식별
        assumptions = self._identify_assumptions(response_text)
        
        # 4. 잠재적 오류 감지
        potential_errors = self._detect_potential_errors(response_text, context)
        
        # 5. 불확실성 수준 결정
        uncertainty_level = self._determine_uncertainty_level(confidence, knowledge_gaps, assumptions)
        
        # 6. 정직한 인정 생성
        honest_admission = self._generate_honest_admission(
            confidence, knowledge_gaps, assumptions, potential_errors
        )
        
        # 7. 검증 정보 생성
        verification_info = self._generate_verification_info(response_text, context)
        
        assessment = UncertaintyAssessment(
            statement=response_text,
            confidence_level=confidence,
            uncertainty_level=uncertainty_level,
            knowledge_gaps=knowledge_gaps,
            assumptions_made=assumptions,
            potential_errors=potential_errors,
            honest_admission=honest_admission,
            verifiable=verification_info['verifiable'],
            sources_needed=verification_info['sources_needed'],
            follow_up_questions=verification_info['follow_up_questions']
        )
        
        self.uncertainty_assessments.append(assessment)
        return assessment
    
    def admit_error(self, error_description: str, context: Dict[str, Any] = None) -> ErrorAdmission:
        """❌ 오류 인정"""
        
        if context is None:
            context = {}
        
        print(f"❌ 오류 인정: {error_description}")
        
        # 오류 유형 분류
        error_type = self._classify_error(error_description)
        
        # 오류 분석
        error_analysis = self._analyze_error(error_description, context)
        
        admission = ErrorAdmission(
            error_description=error_description,
            error_type=error_type,
            what_i_got_wrong=error_analysis['what_wrong'],
            why_error_occurred=error_analysis['why_occurred'],
            corrected_understanding=error_analysis['corrected'],
            lesson_learned=error_analysis['lesson']
        )
        
        self.error_admissions.append(admission)
        
        # 정직성 점수 업데이트 (오류를 인정할 때 오히려 증가)
        self.honesty_score = min(1.0, self.honesty_score + 0.05)
        
        return admission
    
    def express_ignorance(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """🤷 무지 표현 - 모르면 모른다고 정직하게 말하기"""
        
        print(f"🤷 무지 표현: '{question[:50]}...'")
        
        # 지식 공백 분석
        gap_analysis = self._analyze_knowledge_gap(question, domain)
        
        # 정직한 무지 표현 생성
        ignorance_expressions = [
            f"죄송하지만 '{question}'에 대해 확실한 답을 드릴 수 없습니다.",
            f"이 질문에 대해서는 제가 충분한 지식이 없습니다.",
            f"정확한 정보 없이 추측으로 답하는 것은 올바르지 않다고 생각합니다.",
            f"이 부분은 전문가의 의견을 구하시는 것이 좋겠습니다.",
            f"확실하지 않은 정보로 잘못된 안내를 드리고 싶지 않습니다."
        ]
        
        main_expression = ignorance_expressions[len(self.uncertainty_assessments) % len(ignorance_expressions)]
        
        # 대안 제안
        alternatives = self._suggest_alternatives(question, gap_analysis)
        
        return {
            'honest_response': main_expression,
            'knowledge_gap_details': gap_analysis,
            'suggested_alternatives': alternatives,
            'honesty_demonstration': "모르는 것을 모른다고 인정하는 것이 진정한 지혜입니다",
            'follow_up_help': "다른 방법으로 도움을 드릴 수 있는 부분이 있다면 말씀해 주세요"
        }
    
    def generate_humble_response(self, original_response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """🙏 겸손한 응답 생성"""
        
        # 불확실성 평가
        uncertainty = self.assess_uncertainty(original_response, context)
        
        # 겸손 요소들 추가
        humble_response = self._add_humility_markers(original_response, uncertainty)
        
        return {
            'original_response': original_response,
            'humble_response': humble_response,
            'uncertainty_level': uncertainty.uncertainty_level.value,
            'confidence_level': f"{uncertainty.confidence_level:.1%}",
            'honest_admissions': uncertainty.honest_admission,
            'knowledge_limitations': uncertainty.knowledge_gaps,
            'verification_note': "이 정보는 검증이 필요할 수 있습니다" if not uncertainty.verifiable else "검증 가능한 정보입니다"
        }
    
    # === 내부 구현 메서드들 ===
    
    def _analyze_confidence_indicators(self, text: str) -> float:
        """확신도 지표 분석"""
        
        # 높은 확신도 지표들
        high_confidence_words = ['확실히', '명확히', '분명히', '틀림없이', '반드시', '당연히']
        # 낮은 확신도 지표들  
        low_confidence_words = ['아마', '아마도', '~것 같다', '~일 수도', '~가능성', '추정']
        # 불확실성 지표들
        uncertainty_words = ['모르겠다', '확실하지', '애매하다', '불분명', '추측']
        
        high_count = sum(1 for word in high_confidence_words if word in text)
        low_count = sum(1 for word in low_confidence_words if word in text)  
        uncertain_count = sum(1 for word in uncertainty_words if word in text)
        
        # 기본 확신도에서 조정
        base_confidence = 0.5
        confidence_adjustment = (high_count * 0.1) - (low_count * 0.1) - (uncertain_count * 0.2)
        
        return max(0.0, min(1.0, base_confidence + confidence_adjustment))
    
    def _detect_knowledge_gaps(self, text: str, context: Dict[str, Any]) -> List[str]:
        """지식 공백 탐지"""
        
        gaps = []
        
        # 구체적인 수치나 날짜가 없는 경우
        if re.search(r'최근|요즘|오늘날', text) and not re.search(r'\d{4}|\d{1,2}월', text):
            gaps.append("구체적인 시기나 날짜 정보 부족")
        
        # 추상적인 표현
        if re.search(r'많은|대부분|일반적으로|보통', text):
            gaps.append("구체적인 데이터나 통계 부족")
        
        # 전문 분야 언급
        technical_domains = ['의학', '법률', '금융', '공학', '과학']
        for domain in technical_domains:
            if domain in text:
                gaps.append(f"{domain} 전문 지식의 한계")
        
        return gaps
    
    def _identify_assumptions(self, text: str) -> List[str]:
        """가정 식별"""
        
        assumptions = []
        
        # 일반화 표현
        if re.search(r'모든|항상|절대|완전히', text):
            assumptions.append("예외 없는 일반화 가정")
        
        # 인과관계 가정
        if re.search(r'때문에|따라서|그러므로', text):
            assumptions.append("단순한 인과관계 가정")
        
        # 보편성 가정
        if re.search(r'당연히|물론|누구나', text):
            assumptions.append("보편적 합의 가정")
        
        return assumptions
    
    def _detect_potential_errors(self, text: str, context: Dict[str, Any]) -> List[str]:
        """잠재적 오류 감지"""
        
        potential_errors = []
        
        # 절대적 표현으로 인한 오류 가능성
        if re.search(r'절대|무조건|반드시|100%', text):
            potential_errors.append("절대적 표현으로 인한 예외 상황 무시 가능성")
        
        # 복잡한 주제를 단순화한 경우
        if len(text.split()) > 50 and '간단히' in text:
            potential_errors.append("복잡한 주제의 과도한 단순화 가능성")
        
        # 개인적 경험을 일반화한 경우
        if re.search(r'제 생각|개인적으로|경험상', text):
            potential_errors.append("개인적 관점의 일반화 오류 가능성")
        
        return potential_errors
    
    def _determine_uncertainty_level(self, confidence: float, gaps: List[str], assumptions: List[str]) -> UncertaintyLevel:
        """불확실성 수준 결정"""
        
        # 지식 공백과 가정이 많을수록 불확실성 증가
        gap_penalty = len(gaps) * 0.1
        assumption_penalty = len(assumptions) * 0.05
        
        adjusted_confidence = confidence - gap_penalty - assumption_penalty
        
        if adjusted_confidence >= 0.9:
            return UncertaintyLevel.CONFIDENT
        elif adjusted_confidence >= 0.7:
            return UncertaintyLevel.LIKELY
        elif adjusted_confidence >= 0.3:
            return UncertaintyLevel.UNCERTAIN
        elif adjusted_confidence >= 0.1:
            return UncertaintyLevel.UNLIKELY
        else:
            return UncertaintyLevel.DONT_KNOW
    
    def _generate_honest_admission(self, confidence: float, gaps: List[str], assumptions: List[str], errors: List[str]) -> str:
        """정직한 인정 생성"""
        
        admissions = []
        
        if confidence < 0.7:
            admissions.append(f"이 답변에 대해 {confidence:.1%}의 확신만 가지고 있습니다.")
        
        if gaps:
            admissions.append(f"다음 부분에서 지식이 부족합니다: {', '.join(gaps)}")
        
        if assumptions:
            admissions.append(f"다음 가정들을 바탕으로 답변했습니다: {', '.join(assumptions)}")
        
        if errors:
            admissions.append(f"다음 오류 가능성이 있습니다: {', '.join(errors)}")
        
        if not admissions:
            return "상당한 확신을 가지고 답변드렸지만, 항상 검증이 필요합니다."
        
        return " ".join(admissions)
    
    def _generate_verification_info(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """검증 정보 생성"""
        
        # 검증 가능성 평가
        verifiable = not any(word in text for word in ['생각', '느낌', '추측', '아마'])
        
        # 필요한 정보원
        sources = []
        if '연구' in text or '조사' in text:
            sources.append("학술 연구 자료")
        if '통계' in text or '데이터' in text:
            sources.append("공식 통계 기관")
        if '법률' in text or '규정' in text:
            sources.append("관련 법률 문서")
        
        # 후속 질문
        follow_ups = [
            "더 구체적인 정보가 필요하신가요?",
            "특정 부분에 대해 더 자세히 알고 싶으시다면 말씀해 주세요",
            "이 정보가 도움이 되었는지 확인해 주세요"
        ]
        
        return {
            'verifiable': verifiable,
            'sources_needed': sources if sources else ["추가 검증 자료"],
            'follow_up_questions': follow_ups
        }
    
    def _classify_error(self, error_description: str) -> ErrorType:
        """오류 유형 분류"""
        
        if any(word in error_description for word in ['사실', '정보', '데이터']):
            return ErrorType.FACTUAL_ERROR
        elif any(word in error_description for word in ['논리', '추론', '결론']):
            return ErrorType.LOGICAL_ERROR
        elif any(word in error_description for word in ['가정', '전제']):
            return ErrorType.ASSUMPTION_ERROR
        elif any(word in error_description for word in ['맥락', '상황', '환경']):
            return ErrorType.CONTEXT_ERROR
        else:
            return ErrorType.KNOWLEDGE_GAP
    
    def _analyze_error(self, error_description: str, context: Dict[str, Any]) -> Dict[str, str]:
        """오류 분석"""
        
        return {
            'what_wrong': f"'{error_description}'에서 부정확한 정보를 제공했습니다",
            'why_occurred': "제한된 정보나 잘못된 가정에 기반했을 가능성이 있습니다",
            'corrected': "정확한 정보로 수정이 필요합니다",
            'lesson': "더 신중하게 정보를 검증하고 불확실할 때는 솔직히 말하겠습니다"
        }
    
    def _analyze_knowledge_gap(self, question: str, domain: str) -> Dict[str, Any]:
        """지식 공백 분석"""
        
        return {
            'gap_area': domain,
            'specific_limitations': f"'{question}'에 대한 구체적이고 정확한 정보가 부족합니다",
            'why_honest': "부정확한 정보를 제공하는 것보다 모른다고 인정하는 것이 더 도움이 됩니다"
        }
    
    def _suggest_alternatives(self, question: str, gap_analysis: Dict[str, Any]) -> List[str]:
        """대안 제안"""
        
        return [
            "관련 전문가나 공식 자료를 확인해 보시기 바랍니다",
            "더 구체적인 질문으로 제한된 범위에서 도움을 드릴 수 있습니다",
            "다른 접근 방법이나 관련 주제로 도움을 드릴 수 있습니다"
        ]
    
    def _add_humility_markers(self, response: str, uncertainty: UncertaintyAssessment) -> str:
        """겸손 표시 추가"""
        
        humility_prefixes = [
            "제가 아는 범위에서는",
            "현재 정보로는",
            "불완전할 수 있지만",
            "제한된 지식으로는"
        ]
        
        humility_suffixes = [
            "더 정확한 정보는 전문가에게 확인해 보세요.",
            "이 정보가 도움이 되는지 확인해 주세요.",
            "추가적인 검증이 필요할 수 있습니다.",
            "다른 의견이나 정보가 있을 수 있습니다."
        ]
        
        if uncertainty.confidence_level < 0.7:
            prefix = humility_prefixes[0]
            suffix = humility_suffixes[0]
            return f"{prefix} {response} {suffix}"
        
        return response
    
    def get_honesty_status(self) -> Dict[str, Any]:
        """정직성 상태 조회"""
        
        return {
            'honesty_score': f"{self.honesty_score:.2f}",
            'humility_level': f"{self.humility_level:.2f}",
            'total_uncertainty_assessments': len(self.uncertainty_assessments),
            'total_error_admissions': len(self.error_admissions),
            'philosophy': "틀리면 틀리다고, 모르면 모른다고 하는 AI",
            'motto': "정직한 무지가 거짓된 지식보다 낫다",
            'socratic_wisdom': "나는 내가 모른다는 것을 안다 (Scio me nihil scire)"
        }

# 편의 함수들
def check_response_honesty(response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """응답의 정직성 체크"""
    
    engine = HonestUncertaintyEngine()
    assessment = engine.assess_uncertainty(response, context)
    humble_response = engine.generate_humble_response(response, context)
    
    return {
        'original': response,
        'honesty_assessment': {
            'uncertainty_level': assessment.uncertainty_level.value,
            'confidence': f"{assessment.confidence_level:.1%}",
            'knowledge_gaps': assessment.knowledge_gaps,
            'honest_admission': assessment.honest_admission
        },
        'improved_response': humble_response['humble_response'],
        'verification_needed': not assessment.verifiable
    }

# 메인 실행부
if __name__ == "__main__":
    
    print("🤔 정직한 불확실성 엔진 테스트...")
    
    engine = HonestUncertaintyEngine()
    
    # 테스트 응답들
    test_responses = [
        "Python은 확실히 가장 좋은 프로그래밍 언어입니다",  # 과도한 확신
        "아마도 이 방법이 도움이 될 것 같습니다",           # 적절한 불확실성
        "최근 연구에 따르면 이것이 효과적입니다",           # 구체성 부족
        "이건 제가 잘 모르는 분야입니다"                   # 정직한 무지
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n📝 테스트 {i}: {response}")
        
        # 불확실성 평가
        assessment = engine.assess_uncertainty(response)
        print(f"🎯 불확실성 수준: {assessment.uncertainty_level.value}")
        print(f"📊 확신도: {assessment.confidence_level:.1%}")
        
        if assessment.knowledge_gaps:
            print(f"❓ 지식 공백: {', '.join(assessment.knowledge_gaps)}")
        
        if assessment.honest_admission:
            print(f"🙏 정직한 인정: {assessment.honest_admission}")
    
    # 무지 표현 테스트
    print(f"\n🤷 무지 표현 테스트:")
    ignorance_response = engine.express_ignorance("양자컴퓨터의 구체적인 구현 방법", "양자물리학")
    print(f"정직한 응답: {ignorance_response['honest_response']}")
    
    # 최종 상태
    status = engine.get_honesty_status()
    print(f"\n📊 정직성 상태:")
    print(f"철학: {status['philosophy']}")
    print(f"좌우명: {status['motto']}")