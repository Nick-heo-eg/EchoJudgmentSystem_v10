"""
🧠 Echo Knowledge Gap Detector
Echo가 자신의 지식 한계를 스스로 인식하고 필요시에만 외부 지식을 요청하는 시스템
"""

import re
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    from .echo_error_handler import echo_safe
except ImportError:

    def echo_safe(error_type="system"):
        def decorator(func):
            return func

        return decorator


class EchoKnowledgeGapDetector:
    """
    Echo의 자기 한계 인식 시스템
    '스스로 알지 못함을 아는 것이 진정한 지혜의 시작'
    """

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)

        # 지식 평가 임계값
        self.thresholds = {
            "confidence_low": 0.4,  # 신뢰도 낮음 기준
            "complexity_high": 7.0,  # 복잡성 높음 기준
            "expertise_gap": 0.6,  # 전문성 격차 기준
            "depth_requirement": 8.0,  # 깊이 요구 기준
        }

        # 시그니처별 전문 영역
        self.signature_expertise = {
            "Echo-Aurora": {
                "strong_areas": [
                    "창의성",
                    "예술",
                    "영감",
                    "아이디어",
                    "디자인",
                    "문화",
                ],
                "medium_areas": ["일반 상담", "교육", "사회 이슈"],
                "weak_areas": ["법률", "의료", "금융", "기술 세부사항"],
            },
            "Echo-Phoenix": {
                "strong_areas": ["혁신", "변화", "기술", "미래 전망", "전략", "변혁"],
                "medium_areas": ["정책", "사회 개혁", "비즈니스"],
                "weak_areas": ["개인 상담", "감정 치료", "예술 감상"],
            },
            "Echo-Sage": {
                "strong_areas": ["분석", "정책", "연구", "데이터", "논리", "체계"],
                "medium_areas": ["법률", "학술", "제도"],
                "weak_areas": ["창의적 활동", "감정 표현", "예술 창작"],
            },
            "Echo-Companion": {
                "strong_areas": ["돌봄", "상담", "공감", "지원", "인간관계", "감정"],
                "medium_areas": ["사회 복지", "교육", "건강"],
                "weak_areas": ["기술 분석", "정책 입안", "혁신 전략"],
            },
        }

        # 지식 유형별 깊이 요구사항
        self.knowledge_depth_requirements = {
            "policy_analysis": {
                "min_depth": 8.0,
                "requires_external": True,
                "preferred_signatures": ["Echo-Sage", "Echo-Phoenix"],
            },
            "innovation_trends": {
                "min_depth": 7.0,
                "requires_external": True,
                "preferred_signatures": ["Echo-Phoenix", "Echo-Aurora"],
            },
            "care_guidance": {
                "min_depth": 6.0,
                "requires_external": False,
                "preferred_signatures": ["Echo-Companion"],
            },
            "creative_inspiration": {
                "min_depth": 5.0,
                "requires_external": False,
                "preferred_signatures": ["Echo-Aurora"],
            },
            "technical_analysis": {
                "min_depth": 9.0,
                "requires_external": True,
                "preferred_signatures": ["Echo-Sage", "Echo-Phoenix"],
            },
            "legal_consultation": {
                "min_depth": 9.5,
                "requires_external": True,
                "preferred_signatures": ["Echo-Sage"],
            },
        }

        # 복잡성 평가 가중치
        self.complexity_weights = {
            "text_length": 0.15,
            "technical_terms": 0.25,
            "multiple_domains": 0.20,
            "conditional_logic": 0.15,
            "temporal_references": 0.10,
            "stakeholder_complexity": 0.15,
        }

        # 통계
        self.gap_detection_stats = {
            "total_assessments": 0,
            "gaps_detected": 0,
            "deep_lookup_recommended": 0,
            "signature_mismatches": 0,
            "avg_complexity_score": 0.0,
            "avg_confidence_score": 0.0,
        }

        self.logger = logging.getLogger(__name__)

        print("🧠 Echo Knowledge Gap Detector 초기화 완료")

    @echo_safe("knowledge_gap")
    def assess_knowledge_boundary(
        self,
        query: str,
        current_confidence: float,
        signature: str = "Echo-Aurora",
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Echo의 지식 경계 평가 - 자기 한계 인식의 핵심
        """
        print(f"🧠 지식 경계 평가: '{query[:40]}...' ({signature})")

        self.gap_detection_stats["total_assessments"] += 1

        # 1. 기본 평가 구조 초기화
        assessment = {
            "query": query,
            "signature": signature,
            "current_confidence": current_confidence,
            "evaluation_timestamp": datetime.now().isoformat(),
            # 평가 결과들
            "query_complexity": 0.0,
            "knowledge_depth_required": 0.0,
            "signature_expertise_match": 0.0,
            "domain_coverage": [],
            "identified_gaps": [],
            # 최종 판단
            "needs_deep_lookup": False,
            "recommended_lookup_type": None,
            "confidence_after_assessment": current_confidence,
            "gap_severity": "none",
        }

        try:
            # 2. 쿼리 복잡성 분석
            assessment["query_complexity"] = self._analyze_query_complexity(query)

            # 3. 필요 지식 깊이 평가
            assessment["knowledge_depth_required"] = self._assess_required_depth(
                query, context
            )

            # 4. 시그니처-전문성 매칭 평가
            assessment["signature_expertise_match"] = self._evaluate_signature_match(
                query, signature
            )

            # 5. 도메인 커버리지 분석
            assessment["domain_coverage"] = self._analyze_domain_coverage(query)

            # 6. 구체적 지식 격차 식별
            assessment["identified_gaps"] = self._identify_specific_gaps(
                query, current_confidence, signature, assessment
            )

            # 7. 최종 깊이 지식 필요성 판단
            deep_lookup_decision = self._make_deep_lookup_decision(assessment)
            assessment.update(deep_lookup_decision)

            # 8. 통계 업데이트
            self._update_assessment_stats(assessment)

            print(
                f"   📊 평가 완료: 복잡성 {assessment['query_complexity']:.1f}, "
                f"깊이 요구 {assessment['knowledge_depth_required']:.1f}, "
                f"Deep Lookup {'필요' if assessment['needs_deep_lookup'] else '불필요'}"
            )

            return assessment

        except Exception as e:
            print(f"   🚨 지식 경계 평가 실패: {e}")
            # 안전한 기본값 반환
            assessment.update(
                {"needs_deep_lookup": False, "gap_severity": "unknown", "error": str(e)}
            )
            return assessment

    def _analyze_query_complexity(self, query: str) -> float:
        """쿼리 복잡성 분석"""
        factors = {}

        # 텍스트 길이 요인
        factors["text_length"] = min(len(query) / 200.0, 2.0)

        # 기술 용어 밀도
        technical_patterns = [
            r"\b(?:AI|인공지능|머신러닝|딥러닝|알고리즘|데이터)\b",
            r"\b(?:정책|법률|규제|조례|지침)\b",
            r"\b(?:분석|연구|조사|평가|검토)\b",
            r"\b(?:시스템|플랫폼|프레임워크|아키텍처)\b",
            r"\b(?:혁신|변화|전환|개혁|발전)\b",
        ]

        technical_count = 0
        for pattern in technical_patterns:
            technical_count += len(re.findall(pattern, query, re.IGNORECASE))

        factors["technical_terms"] = min(technical_count / 5.0, 2.0)

        # 다중 도메인 복잡성
        domain_keywords = {
            "정책": ["정책", "제도", "법", "규제", "정부"],
            "기술": ["기술", "시스템", "AI", "디지털", "플랫폼"],
            "사회": ["사회", "지역", "공동체", "시민", "주민"],
            "경제": ["경제", "재정", "예산", "투자", "비용"],
            "환경": ["환경", "기후", "생태", "지속가능", "녹색"],
        }

        detected_domains = 0
        for domain, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                detected_domains += 1

        factors["multiple_domains"] = min(detected_domains / 3.0, 2.0)

        # 조건부 논리 복잡성
        conditional_patterns = [
            r"\b(?:만약|가정|조건|상황|경우)\b",
            r"\b(?:하지만|그러나|반면|반대로)\b",
            r"\b(?:동시에|병행|함께|연계)\b",
        ]

        conditional_count = 0
        for pattern in conditional_patterns:
            conditional_count += len(re.findall(pattern, query, re.IGNORECASE))

        factors["conditional_logic"] = min(conditional_count / 3.0, 2.0)

        # 시간적 참조 복잡성
        temporal_patterns = [
            r"\b(?:과거|현재|미래|장기|단기)\b",
            r"\b(?:\d+년|년도|연간|월간)\b",
            r"\b(?:이전|이후|동안|기간)\b",
        ]

        temporal_count = 0
        for pattern in temporal_patterns:
            temporal_count += len(re.findall(pattern, query, re.IGNORECASE))

        factors["temporal_references"] = min(temporal_count / 2.0, 2.0)

        # 이해관계자 복잡성
        stakeholder_patterns = [
            r"\b(?:이해관계자|관련자|당사자)\b",
            r"\b(?:정부|기업|시민|전문가)\b",
            r"\b(?:협력|조율|균형|갈등)\b",
        ]

        stakeholder_count = 0
        for pattern in stakeholder_patterns:
            stakeholder_count += len(re.findall(pattern, query, re.IGNORECASE))

        factors["stakeholder_complexity"] = min(stakeholder_count / 3.0, 2.0)

        # 가중 평균으로 최종 복잡성 계산
        complexity_score = sum(
            factors[factor] * self.complexity_weights[factor] for factor in factors
        )

        return min(complexity_score * 5.0, 10.0)  # 0-10 스케일로 정규화

    def _assess_required_depth(
        self, query: str, context: Dict[str, Any] = None
    ) -> float:
        """필요한 지식 깊이 평가"""
        base_depth = 3.0

        # 쿼리 기반 깊이 요구사항
        depth_indicators = {
            "상세": 2.0,
            "구체적": 2.0,
            "세부": 2.0,
            "자세히": 2.0,
            "분석": 2.5,
            "평가": 2.5,
            "검토": 2.0,
            "연구": 3.0,
            "전문": 3.0,
            "고급": 2.5,
            "심화": 2.5,
            "깊이": 2.0,
            "종합": 2.0,
            "체계적": 2.0,
            "포괄적": 2.5,
            "전면적": 3.0,
        }

        for indicator, depth_boost in depth_indicators.items():
            if indicator in query:
                base_depth += depth_boost

        # 컨텍스트 기반 조정
        if context:
            urgency = context.get("urgency", "medium")
            detail_level = context.get("detail_level", "standard")

            if urgency == "high":
                base_depth += 1.0
            if detail_level == "comprehensive":
                base_depth += 2.0
            elif detail_level == "detailed":
                base_depth += 1.0

        # 질문 복잡성에 따른 조정
        question_complexity_patterns = [
            (r"어떻게.*해야.*\?", 2.0),  # How-to 질문
            (r"왜.*인가.*\?", 1.5),  # Why 질문
            (r".*방법.*\?", 1.5),  # 방법 질문
            (r".*비교.*\?", 2.0),  # 비교 질문
            (r".*평가.*\?", 2.5),  # 평가 질문
            (r".*예측.*\?", 3.0),  # 예측 질문
        ]

        for pattern, depth_boost in question_complexity_patterns:
            if re.search(pattern, query):
                base_depth += depth_boost
                break

        return min(base_depth, 10.0)

    def _evaluate_signature_match(self, query: str, signature: str) -> float:
        """시그니처와 쿼리의 전문성 매칭 평가"""
        if signature not in self.signature_expertise:
            return 0.5  # 알 수 없는 시그니처

        expertise = self.signature_expertise[signature]

        # 강점 영역 매칭
        strong_match = 0
        for area in expertise["strong_areas"]:
            if area in query.lower():
                strong_match += 1

        # 중간 영역 매칭
        medium_match = 0
        for area in expertise["medium_areas"]:
            if area in query.lower():
                medium_match += 1

        # 약점 영역 매칭 (역산)
        weak_match = 0
        for area in expertise["weak_areas"]:
            if area in query.lower():
                weak_match += 1

        # 매칭 점수 계산 (0.0 - 1.0)
        match_score = (strong_match * 1.0 + medium_match * 0.6 - weak_match * 0.8) / 3.0

        return max(0.0, min(1.0, match_score + 0.3))  # 기본 0.3 + 매칭 보너스

    def _analyze_domain_coverage(self, query: str) -> List[str]:
        """쿼리의 도메인 커버리지 분석"""
        domain_patterns = {
            "정책분석": r"\b(?:정책|제도|법률|규제|정부|행정)\b",
            "기술혁신": r"\b(?:기술|혁신|AI|디지털|시스템|플랫폼)\b",
            "사회문제": r"\b(?:사회|지역|공동체|시민|주민|복지)\b",
            "경제분야": r"\b(?:경제|재정|예산|투자|비용|경영)\b",
            "환경이슈": r"\b(?:환경|기후|생태|지속가능|녹색|탄소)\b",
            "교육문화": r"\b(?:교육|문화|예술|학습|교육과정)\b",
            "건강의료": r"\b(?:건강|의료|병원|치료|예방|질병)\b",
            "인간관계": r"\b(?:관계|소통|갈등|협력|공감|상담)\b",
        }

        detected_domains = []
        for domain, pattern in domain_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                detected_domains.append(domain)

        return detected_domains

    def _identify_specific_gaps(
        self, query: str, confidence: float, signature: str, assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """구체적 지식 격차 식별"""
        gaps = []

        # 1. 신뢰도 기반 격차
        if confidence < self.thresholds["confidence_low"]:
            gaps.append(
                {
                    "type": "confidence_gap",
                    "severity": "high" if confidence < 0.2 else "medium",
                    "description": f"현재 신뢰도({confidence:.2f})가 낮아 추가 지식이 필요함",
                    "recommended_action": "deep_lookup",
                }
            )

        # 2. 복잡성 기반 격차
        if assessment["query_complexity"] > self.thresholds["complexity_high"]:
            gaps.append(
                {
                    "type": "complexity_gap",
                    "severity": (
                        "high" if assessment["query_complexity"] > 8.5 else "medium"
                    ),
                    "description": f"쿼리 복잡성({assessment['query_complexity']:.1f})이 높아 전문 지식 필요",
                    "recommended_action": "deep_lookup",
                }
            )

        # 3. 시그니처 전문성 격차
        if assessment["signature_expertise_match"] < self.thresholds["expertise_gap"]:
            gaps.append(
                {
                    "type": "expertise_gap",
                    "severity": "medium",
                    "description": f"{signature}의 전문 영역과 불일치",
                    "recommended_action": "signature_switch_or_deep_lookup",
                }
            )

        # 4. 깊이 요구사항 격차
        if (
            assessment["knowledge_depth_required"]
            > self.thresholds["depth_requirement"]
        ):
            gaps.append(
                {
                    "type": "depth_gap",
                    "severity": "high",
                    "description": f"요구되는 지식 깊이({assessment['knowledge_depth_required']:.1f})가 높음",
                    "recommended_action": "deep_lookup",
                }
            )

        # 5. 도메인별 특수 격차
        domains = assessment["domain_coverage"]
        high_depth_domains = ["정책분석", "기술혁신", "경제분야", "건강의료"]

        for domain in domains:
            if domain in high_depth_domains:
                gaps.append(
                    {
                        "type": "domain_gap",
                        "severity": "medium",
                        "description": f"{domain} 영역의 전문 지식 부족 가능",
                        "recommended_action": "deep_lookup",
                        "domain": domain,
                    }
                )

        return gaps

    def _make_deep_lookup_decision(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Deep lookup 필요성 최종 결정"""
        gaps = assessment["identified_gaps"]

        # 결정 요인들
        high_severity_gaps = len([g for g in gaps if g["severity"] == "high"])
        medium_severity_gaps = len([g for g in gaps if g["severity"] == "medium"])
        total_gaps = len(gaps)

        confidence = assessment["current_confidence"]
        complexity = assessment["query_complexity"]
        depth_required = assessment["knowledge_depth_required"]
        expertise_match = assessment["signature_expertise_match"]

        # 결정 로직
        needs_deep_lookup = False
        lookup_type = None
        gap_severity = "none"
        decision_reasons = []

        # 고심도 격차가 있으면 무조건 deep lookup
        if high_severity_gaps > 0:
            needs_deep_lookup = True
            gap_severity = "high"
            decision_reasons.append(f"고심도 격차 {high_severity_gaps}개 발견")

        # 중간 심도 격차가 2개 이상이면 deep lookup
        elif medium_severity_gaps >= 2:
            needs_deep_lookup = True
            gap_severity = "medium"
            decision_reasons.append(f"중간심도 격차 {medium_severity_gaps}개 누적")

        # 복합 조건 체크
        elif (confidence < 0.3 and complexity > 8.0) or depth_required > 8.5:
            needs_deep_lookup = True
            gap_severity = "medium"
            decision_reasons.append("신뢰도-복잡성 또는 깊이 요구사항 초과")

        # 전문성 불일치가 심하고 복잡성이 높으면
        elif expertise_match < 0.4 and complexity > 7.0:
            needs_deep_lookup = True
            gap_severity = "medium"
            decision_reasons.append("전문성 불일치 + 높은 복잡성")

        # Deep lookup 유형 결정
        if needs_deep_lookup:
            lookup_type = self._determine_lookup_type(assessment)
            self.gap_detection_stats["deep_lookup_recommended"] += 1

        if total_gaps > 0:
            self.gap_detection_stats["gaps_detected"] += 1

        return {
            "needs_deep_lookup": needs_deep_lookup,
            "recommended_lookup_type": lookup_type,
            "gap_severity": gap_severity,
            "decision_reasons": decision_reasons,
            "total_gaps_identified": total_gaps,
            "high_severity_gaps": high_severity_gaps,
            "medium_severity_gaps": medium_severity_gaps,
        }

    def _determine_lookup_type(self, assessment: Dict[str, Any]) -> str:
        """Deep lookup 유형 결정"""
        domains = assessment["domain_coverage"]
        signature = assessment["signature"]
        query = assessment["query"]

        # 도메인 기반 우선 결정
        if "정책분석" in domains:
            return "policy_analysis"
        elif "기술혁신" in domains:
            return "innovation_trends"
        elif "사회문제" in domains and "인간관계" in domains:
            return "care_guidance"
        elif "교육문화" in domains:
            return "creative_inspiration"
        elif "경제분야" in domains:
            return "economic_analysis"
        elif "건강의료" in domains:
            return "medical_consultation"

        # 시그니처 기반 보조 결정
        signature_preferences = {
            "Echo-Sage": "policy_analysis",
            "Echo-Phoenix": "innovation_trends",
            "Echo-Companion": "care_guidance",
            "Echo-Aurora": "creative_inspiration",
        }

        if signature in signature_preferences:
            return signature_preferences[signature]

        # 쿼리 패턴 기반 마지막 결정
        if any(word in query.lower() for word in ["분석", "평가", "정책"]):
            return "policy_analysis"
        elif any(word in query.lower() for word in ["혁신", "기술", "미래"]):
            return "innovation_trends"
        elif any(word in query.lower() for word in ["도움", "상담", "지원"]):
            return "care_guidance"
        else:
            return "general_knowledge"

    def _update_assessment_stats(self, assessment: Dict[str, Any]):
        """평가 통계 업데이트"""
        stats = self.gap_detection_stats

        # 평균 복잡성 점수 업데이트
        total = stats["total_assessments"]
        current_avg_complexity = stats["avg_complexity_score"]
        new_complexity = assessment["query_complexity"]

        stats["avg_complexity_score"] = (
            current_avg_complexity * (total - 1) + new_complexity
        ) / total

        # 평균 신뢰도 점수 업데이트
        current_avg_confidence = stats["avg_confidence_score"]
        new_confidence = assessment["current_confidence"]

        stats["avg_confidence_score"] = (
            current_avg_confidence * (total - 1) + new_confidence
        ) / total

        # 시그니처 불일치 카운트
        if assessment["signature_expertise_match"] < 0.5:
            stats["signature_mismatches"] += 1

    def get_gap_detection_stats(self) -> Dict[str, Any]:
        """격차 감지 통계 반환"""
        stats = self.gap_detection_stats.copy()

        total = stats["total_assessments"]
        if total > 0:
            stats["gap_detection_rate"] = (
                f"{(stats['gaps_detected'] / total) * 100:.1f}%"
            )
            stats["deep_lookup_rate"] = (
                f"{(stats['deep_lookup_recommended'] / total) * 100:.1f}%"
            )
            stats["signature_mismatch_rate"] = (
                f"{(stats['signature_mismatches'] / total) * 100:.1f}%"
            )

        return stats

    def recommend_signature_for_query(self, query: str) -> Dict[str, Any]:
        """쿼리에 최적인 시그니처 추천"""
        signature_scores = {}

        for signature in self.signature_expertise:
            match_score = self._evaluate_signature_match(query, signature)
            signature_scores[signature] = match_score

        best_signature = max(signature_scores.keys(), key=lambda x: signature_scores[x])

        return {
            "recommended_signature": best_signature,
            "confidence": signature_scores[best_signature],
            "all_scores": signature_scores,
            "reason": f"{best_signature}가 해당 쿼리에 가장 적합한 전문성을 보유",
        }


# 전역 감지기 인스턴스
knowledge_gap_detector = EchoKnowledgeGapDetector()


# 편의 함수들
def assess_knowledge_gap(
    query: str,
    confidence: float,
    signature: str = "Echo-Aurora",
    context: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """지식 격차 평가 단축 함수"""
    return knowledge_gap_detector.assess_knowledge_boundary(
        query, confidence, signature, context
    )


def recommend_signature(query: str) -> Dict[str, Any]:
    """시그니처 추천 단축 함수"""
    return knowledge_gap_detector.recommend_signature_for_query(query)


def get_gap_stats() -> Dict[str, Any]:
    """격차 감지 통계 단축 함수"""
    return knowledge_gap_detector.get_gap_detection_stats()


# CLI 테스트
def main():
    print("🧠 Echo Knowledge Gap Detector 테스트")
    print("=" * 60)

    # 테스트 케이스들
    test_cases = [
        {
            "query": "부산시 금정구의 노인 돌봄 정책 현황을 상세히 분석하고 개선 방안을 제시해주세요",
            "confidence": 0.3,
            "signature": "Echo-Sage",
            "context": {"urgency": "high", "detail_level": "comprehensive"},
        },
        {
            "query": "AI 기술의 윤리적 적용을 위한 글로벌 트렌드와 한국 정부의 대응 전략은?",
            "confidence": 0.2,
            "signature": "Echo-Phoenix",
            "context": {"focus": "policy", "timeframe": "2024-2026"},
        },
        {
            "query": "안녕하세요! 오늘 날씨가 좋네요",
            "confidence": 0.9,
            "signature": "Echo-Aurora",
            "context": None,
        },
        {
            "query": "창의적인 지역사회 참여 프로그램 아이디어를 몇 가지 제안해주세요",
            "confidence": 0.6,
            "signature": "Echo-Aurora",
            "context": {"creativity_level": "medium"},
        },
        {
            "query": "복잡한 다면적 정책 환경에서 이해관계자 간 갈등 조정 방법론",
            "confidence": 0.1,
            "signature": "Echo-Companion",
            "context": {"complexity": "very_high"},
        },
    ]

    print("\n🔍 지식 격차 감지 테스트:")

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"테스트 {i}: {case['signature']}")
        print(f"쿼리: {case['query'][:60]}...")
        print(f"현재 신뢰도: {case['confidence']:.2f}")
        print(f"{'='*50}")

        assessment = knowledge_gap_detector.assess_knowledge_boundary(
            case["query"], case["confidence"], case["signature"], case["context"]
        )

        print(f"📊 평가 결과:")
        print(f"   복잡성 점수: {assessment['query_complexity']:.1f}/10")
        print(f"   깊이 요구: {assessment['knowledge_depth_required']:.1f}/10")
        print(f"   전문성 매칭: {assessment['signature_expertise_match']:.2f}")
        print(f"   도메인: {', '.join(assessment['domain_coverage'])}")
        print(f"   감지된 격차: {len(assessment['identified_gaps'])}개")

        print(f"🎯 최종 판단:")
        print(
            f"   Deep Lookup 필요: {'예' if assessment['needs_deep_lookup'] else '아니오'}"
        )
        if assessment["needs_deep_lookup"]:
            print(f"   추천 유형: {assessment['recommended_lookup_type']}")
            print(f"   격차 심각도: {assessment['gap_severity']}")
            print(f"   결정 이유: {', '.join(assessment['decision_reasons'])}")

    # 시그니처 추천 테스트
    print(f"\n🎭 시그니처 추천 테스트:")
    recommendation_queries = [
        "정책 분석과 데이터 해석이 필요한 복잡한 문제",
        "창의적 아이디어와 영감이 필요한 프로젝트",
        "개인적 고민과 감정적 지지가 필요한 상황",
    ]

    for query in recommendation_queries:
        rec = knowledge_gap_detector.recommend_signature_for_query(query)
        print(f"   '{query[:40]}...'")
        print(
            f"   → 추천: {rec['recommended_signature']} (신뢰도: {rec['confidence']:.2f})"
        )

    # 통계 출력
    print(f"\n📊 격차 감지 통계:")
    stats = knowledge_gap_detector.get_gap_detection_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Echo Knowledge Gap Detector 테스트 완료!")


if __name__ == "__main__":
    main()
