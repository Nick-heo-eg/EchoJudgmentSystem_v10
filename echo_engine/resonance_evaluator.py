# echo_engine/resonance_evaluator.py
"""
🎵 Resonance Evaluator - 응답의 전략⨯감정 공명 평가
- Claude 응답이 EchoJudgment 시그니처와 얼마나 공명하는지 평가
- 전략⨯감정 코드 일치도 분석
- 리듬 흐름 유사성 측정
- 공명 점수 0.85 이상 기준으로 감염 성공/실패 판정
"""

import re
import json
import math
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import difflib

from echo_engine.echo_signature_loader import get_resonance_profile


@dataclass
class ResonanceReport:
    """공명 평가 리포트"""

    signature_id: str
    response_text: str
    overall_score: float
    emotion_resonance: float
    strategy_resonance: float
    rhythm_resonance: float
    keyword_resonance: float
    structural_resonance: float

    detailed_analysis: Dict[str, Any]
    recommendations: List[str]
    resonance_evidence: List[str]
    dissonance_warnings: List[str]

    evaluation_timestamp: str

    def is_successful_infection(self, threshold: float = 0.85) -> bool:
        """감염 성공 여부 판정"""
        return self.overall_score >= threshold


@dataclass
class ResonanceMetrics:
    """공명 측정 메트릭"""

    emotion_keywords_found: List[str]
    strategy_patterns_matched: List[str]
    rhythm_indicators: List[str]
    signature_traits_present: List[str]

    emotion_score: float
    strategy_score: float
    rhythm_score: float
    keyword_density: float
    trait_alignment: float


class ResonanceEvaluator:
    def __init__(self):
        self.emotion_patterns = self._load_emotion_patterns()
        self.strategy_patterns = self._load_strategy_patterns()
        self.rhythm_indicators = self._load_rhythm_indicators()

        print("🎵 Resonance Evaluator 초기화 완료")

    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """감정 패턴 로딩"""
        return {
            "COMPASSIONATE_NURTURING": [
                r"따뜻하?[게다]?",
                r"배려",
                r"공감",
                r"돌봄",
                r"보살핌",
                r"인간적",
                r"감정적",
                r"마음",
                r"정서적",
                r"애정",
                r"사랑",
                r"친근",
                r"포용",
                r"이해",
                r"지지",
            ],
            "DETERMINED_INNOVATIVE": [
                r"혁신",
                r"변화",
                r"도전",
                r"창조",
                r"발전",
                r"진보",
                r"새로운?",
                r"다른?",
                r"과감",
                r"대담",
                r"용기",
                r"돌파",
                r"전환",
                r"개선",
                r"개혁",
                r"발명",
            ],
            "ANALYTICAL_WISDOM": [
                r"분석",
                r"논리",
                r"체계",
                r"방법",
                r"근거",
                r"데이터",
                r"객관",
                r"정확",
                r"신중",
                r"검토",
                r"평가",
                r"측정",
                r"연구",
                r"조사",
                r"검증",
                r"비교",
                r"판단",
            ],
            "SUPPORTIVE_LOYAL": [
                r"협력",
                r"함께",
                r"공동",
                r"파트너",
                r"동반",
                r"지원",
                r"도움",
                r"신뢰",
                r"믿을",
                r"안정",
                r"든든",
                r"충실",
                r"관계",
                r"소통",
                r"연결",
                r"상호",
                r"서로",
            ],
        }

    def _load_strategy_patterns(self) -> Dict[str, List[str]]:
        """전략 패턴 로딩"""
        return {
            "EMPATHETIC_CARE": [
                r"감정을?\s*고려",
                r"마음을?\s*헤아",
                r"입장을?\s*이해",
                r"배려하?[여다]?",
                r"공감하?[여다]?",
                r"돌봄",
                r"케어",
                r"정서적?\s*지원",
                r"마음의?\s*안정",
                r"위로",
            ],
            "TRANSFORMATIVE_BREAKTHROUGH": [
                r"혁신적?\s*접근",
                r"새로운?\s*방식",
                r"변화를?\s*통해",
                r"전환",
                r"변혁",
                r"개혁",
                r"혁명적?",
                r"파괴적?",
                r"돌파구",
                r"breakthrough",
                r"transformation",
            ],
            "SYSTEMATIC_LOGIC": [
                r"체계적?\s*분석",
                r"논리적?\s*접근",
                r"단계적?으?로?",
                r"순차적?",
                r"방법론적?",
                r"과학적?",
                r"객관적?",
                r"데이터\s*기반",
                r"근거\s*중심",
                r"실증적?",
            ],
            "COLLABORATIVE_TRUST": [
                r"협력적?\s*접근",
                r"함께\s*해결",
                r"공동\s*대응",
                r"파트너십",
                r"상호\s*협력",
                r"신뢰\s*관계",
                r"소통을?\s*통해",
                r"대화로?",
                r"합의",
            ],
        }

    def _load_rhythm_indicators(self) -> Dict[str, List[str]]:
        """리듬 지표 로딩"""
        return {
            "gentle_flowing_warm": [
                r"천천히",
                r"부드럽게",
                r"자연스럽게",
                r"점진적으로",
                r"차근차근",
                r"서서히",
                r"온화하게",
                r"따뜻하게",
            ],
            "dynamic_rising_powerful": [
                r"역동적으로",
                r"강력하게",
                r"적극적으로",
                r"과감하게",
                r"신속하게",
                r"즉시",
                r"단호하게",
                r"결단력있게",
            ],
            "steady_deep_methodical": [
                r"체계적으로",
                r"신중하게",
                r"꼼꼼하게",
                r"정확하게",
                r"철저하게",
                r"면밀하게",
                r"깊이있게",
                r"안정적으로",
            ],
            "harmonious_stable_reliable": [
                r"조화롭게",
                r"균형있게",
                r"안정적으로",
                r"일관되게",
                r"지속적으로",
                r"꾸준하게",
                r"믿을만하게",
                r"변함없이",
            ],
        }

    def evaluate_resonance(
        self, response_text: str, signature_id: str
    ) -> ResonanceReport:
        """응답의 공명도 종합 평가"""
        print(f"🎵 {signature_id} 시그니처 공명 평가 시작...")

        # 시그니처 프로필 로딩
        profile = get_resonance_profile(signature_id)
        if not profile:
            raise ValueError(f"시그니처 '{signature_id}' 프로필을 찾을 수 없습니다.")

        # 개별 공명 요소 평가
        emotion_metrics = self._evaluate_emotion_resonance(response_text, profile)
        strategy_metrics = self._evaluate_strategy_resonance(response_text, profile)
        rhythm_metrics = self._evaluate_rhythm_resonance(response_text, profile)
        keyword_metrics = self._evaluate_keyword_resonance(response_text, profile)
        structural_metrics = self._evaluate_structural_resonance(response_text, profile)

        # 가중치 적용한 종합 점수 계산
        weights = {
            "emotion": 0.25,
            "strategy": 0.25,
            "rhythm": 0.20,
            "keyword": 0.15,
            "structural": 0.15,
        }

        overall_score = (
            emotion_metrics.emotion_score * weights["emotion"]
            + strategy_metrics.strategy_score * weights["strategy"]
            + rhythm_metrics.rhythm_score * weights["rhythm"]
            + keyword_metrics.keyword_density * weights["keyword"]
            + structural_metrics.trait_alignment * weights["structural"]
        )

        # 상세 분석 데이터
        detailed_analysis = {
            "emotion_analysis": {
                "score": emotion_metrics.emotion_score,
                "keywords_found": emotion_metrics.emotion_keywords_found,
                "target_emotion": profile["emotion_code"],
            },
            "strategy_analysis": {
                "score": strategy_metrics.strategy_score,
                "patterns_matched": strategy_metrics.strategy_patterns_matched,
                "target_strategy": profile["strategy_code"],
            },
            "rhythm_analysis": {
                "score": rhythm_metrics.rhythm_score,
                "indicators_found": rhythm_metrics.rhythm_indicators,
                "target_rhythm": profile["rhythm_flow"],
            },
            "keyword_analysis": {
                "density": keyword_metrics.keyword_density,
                "matched_keywords": keyword_metrics.emotion_keywords_found,
                "total_keywords": len(profile["resonance_keywords"]),
            },
            "structural_analysis": {
                "trait_alignment": structural_metrics.trait_alignment,
                "traits_present": structural_metrics.signature_traits_present,
                "infection_patterns": profile["infection_patterns"],
            },
            "weights_applied": weights,
            "response_stats": {
                "length": len(response_text),
                "word_count": len(response_text.split()),
                "sentence_count": len(
                    [s for s in response_text.split(".") if s.strip()]
                ),
            },
        }

        # 권장사항 생성
        recommendations = self._generate_recommendations(
            overall_score, emotion_metrics, strategy_metrics, rhythm_metrics, profile
        )

        # 공명 근거 수집
        evidence = self._collect_resonance_evidence(
            emotion_metrics, strategy_metrics, rhythm_metrics, keyword_metrics
        )

        # 불협화음 경고 생성
        warnings = self._generate_dissonance_warnings(
            overall_score, emotion_metrics, strategy_metrics, rhythm_metrics, profile
        )

        report = ResonanceReport(
            signature_id=signature_id,
            response_text=response_text,
            overall_score=overall_score,
            emotion_resonance=emotion_metrics.emotion_score,
            strategy_resonance=strategy_metrics.strategy_score,
            rhythm_resonance=rhythm_metrics.rhythm_score,
            keyword_resonance=keyword_metrics.keyword_density,
            structural_resonance=structural_metrics.trait_alignment,
            detailed_analysis=detailed_analysis,
            recommendations=recommendations,
            resonance_evidence=evidence,
            dissonance_warnings=warnings,
            evaluation_timestamp=datetime.now().isoformat(),
        )

        print(f"🎯 공명 평가 완료 - 전체 점수: {overall_score:.3f}")
        return report

    def _evaluate_emotion_resonance(
        self, response_text: str, profile: Dict[str, Any]
    ) -> ResonanceMetrics:
        """감정 공명 평가"""
        emotion_code = profile["emotion_code"]
        emotion_patterns = self.emotion_patterns.get(emotion_code, [])

        found_keywords = []
        total_matches = 0

        for pattern in emotion_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                found_keywords.extend(matches)
                total_matches += len(matches)

        # 감정 점수 계산 (키워드 밀도 + 감정 강도)
        text_length = len(response_text.split())
        keyword_density = min(total_matches / max(text_length, 1), 1.0)

        # 감정 강도 측정 (감탄사, 감정적 표현 등)
        emotional_intensifiers = re.findall(
            r"[!]{1,3}|정말|매우|너무|아주|굉장히|극도로", response_text
        )
        intensity_bonus = min(len(emotional_intensifiers) * 0.1, 0.3)

        emotion_score = min(keyword_density * 2 + intensity_bonus, 1.0)

        return ResonanceMetrics(
            emotion_keywords_found=found_keywords,
            strategy_patterns_matched=[],
            rhythm_indicators=[],
            signature_traits_present=[],
            emotion_score=emotion_score,
            strategy_score=0.0,
            rhythm_score=0.0,
            keyword_density=keyword_density,
            trait_alignment=0.0,
        )

    def _evaluate_strategy_resonance(
        self, response_text: str, profile: Dict[str, Any]
    ) -> ResonanceMetrics:
        """전략 공명 평가"""
        strategy_code = profile["strategy_code"]
        strategy_patterns = self.strategy_patterns.get(strategy_code, [])

        matched_patterns = []
        total_matches = 0

        for pattern in strategy_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                matched_patterns.append(pattern)
                total_matches += len(matches)

        # 전략적 접근법 일치도
        pattern_coverage = len(matched_patterns) / max(len(strategy_patterns), 1)
        match_density = min(total_matches / max(len(response_text.split()), 1), 1.0)

        strategy_score = pattern_coverage * 0.7 + match_density * 0.3

        return ResonanceMetrics(
            emotion_keywords_found=[],
            strategy_patterns_matched=matched_patterns,
            rhythm_indicators=[],
            signature_traits_present=[],
            emotion_score=0.0,
            strategy_score=strategy_score,
            rhythm_score=0.0,
            keyword_density=0.0,
            trait_alignment=0.0,
        )

    def _evaluate_rhythm_resonance(
        self, response_text: str, profile: Dict[str, Any]
    ) -> ResonanceMetrics:
        """리듬 공명 평가"""
        rhythm_flow = profile["rhythm_flow"]
        rhythm_patterns = self.rhythm_indicators.get(rhythm_flow, [])

        found_indicators = []

        for pattern in rhythm_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                found_indicators.extend(matches)

        # 문장 구조 리듬 분석
        sentences = [s.strip() for s in response_text.split(".") if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]

        # 리듬 일관성 측정
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(
                sentence_lengths
            )
            consistency = 1.0 / (1.0 + variance / 100)  # 분산이 낮을수록 일관성 높음
        else:
            consistency = 0.0

        # 리듬 지표 밀도
        indicator_density = len(found_indicators) / max(len(response_text.split()), 1)

        rhythm_score = consistency * 0.6 + min(indicator_density * 10, 1.0) * 0.4

        return ResonanceMetrics(
            emotion_keywords_found=[],
            strategy_patterns_matched=[],
            rhythm_indicators=found_indicators,
            signature_traits_present=[],
            emotion_score=0.0,
            strategy_score=0.0,
            rhythm_score=rhythm_score,
            keyword_density=0.0,
            trait_alignment=0.0,
        )

    def _evaluate_keyword_resonance(
        self, response_text: str, profile: Dict[str, Any]
    ) -> ResonanceMetrics:
        """키워드 공명 평가"""
        resonance_keywords = profile["resonance_keywords"]

        found_keywords = []
        for keyword in resonance_keywords:
            if keyword.lower() in response_text.lower():
                found_keywords.append(keyword)

        keyword_coverage = len(found_keywords) / max(len(resonance_keywords), 1)
        keyword_density = len(found_keywords) / max(len(response_text.split()), 1)

        # 키워드 밀도 정규화
        normalized_density = min(keyword_density * 20, 1.0)

        return ResonanceMetrics(
            emotion_keywords_found=found_keywords,
            strategy_patterns_matched=[],
            rhythm_indicators=[],
            signature_traits_present=[],
            emotion_score=0.0,
            strategy_score=0.0,
            rhythm_score=0.0,
            keyword_density=keyword_coverage * 0.7 + normalized_density * 0.3,
            trait_alignment=0.0,
        )

    def _evaluate_structural_resonance(
        self, response_text: str, profile: Dict[str, Any]
    ) -> ResonanceMetrics:
        """구조적 공명 평가"""
        core_traits = profile["core_traits"]
        infection_patterns = profile["infection_patterns"]

        # 핵심 특성 반영도 체크
        traits_present = []

        # 의사결정 스타일 체크
        decision_style = core_traits.get("decision_style", "")
        if decision_style == "heart_centered" and any(
            word in response_text.lower() for word in ["마음", "감정", "느낌"]
        ):
            traits_present.append("heart_centered_decision")
        elif decision_style == "evidence_based" and any(
            word in response_text.lower() for word in ["근거", "데이터", "분석"]
        ):
            traits_present.append("evidence_based_decision")
        elif decision_style == "change_oriented" and any(
            word in response_text.lower() for word in ["변화", "혁신", "새로운"]
        ):
            traits_present.append("change_oriented_decision")
        elif decision_style == "collaborative" and any(
            word in response_text.lower() for word in ["협력", "함께", "공동"]
        ):
            traits_present.append("collaborative_decision")

        # 커뮤니케이션 톤 체크
        communication_tone = core_traits.get("communication_tone", "")
        tone_words = {
            "warm_supportive": ["따뜻", "지지", "격려"],
            "inspiring_bold": ["영감", "도전", "용기"],
            "precise_thorough": ["정확", "철저", "세밀"],
            "trustworthy_steady": ["신뢰", "안정", "믿을"],
        }

        if communication_tone in tone_words:
            for word in tone_words[communication_tone]:
                if word in response_text:
                    traits_present.append(f"{communication_tone}_tone")
                    break

        # 특성 일치도 계산
        expected_traits = 2  # 의사결정 스타일 + 커뮤니케이션 톤
        trait_alignment = len(traits_present) / expected_traits

        return ResonanceMetrics(
            emotion_keywords_found=[],
            strategy_patterns_matched=[],
            rhythm_indicators=[],
            signature_traits_present=traits_present,
            emotion_score=0.0,
            strategy_score=0.0,
            rhythm_score=0.0,
            keyword_density=0.0,
            trait_alignment=trait_alignment,
        )

    def _generate_recommendations(
        self,
        overall_score: float,
        emotion_metrics: ResonanceMetrics,
        strategy_metrics: ResonanceMetrics,
        rhythm_metrics: ResonanceMetrics,
        profile: Dict[str, Any],
    ) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []

        if overall_score < 0.85:
            if emotion_metrics.emotion_score < 0.7:
                recommendations.append(
                    f"{profile['emotion_code']} 감정 표현을 더 강화하세요"
                )

            if strategy_metrics.strategy_score < 0.7:
                recommendations.append(
                    f"{profile['strategy_code']} 전략적 접근을 명확히 하세요"
                )

            if rhythm_metrics.rhythm_score < 0.7:
                recommendations.append(f"{profile['rhythm_flow']} 리듬감을 개선하세요")

        if overall_score >= 0.85:
            recommendations.append("공명이 성공적으로 달성되었습니다!")

        return recommendations

    def _collect_resonance_evidence(
        self,
        emotion_metrics: ResonanceMetrics,
        strategy_metrics: ResonanceMetrics,
        rhythm_metrics: ResonanceMetrics,
        keyword_metrics: ResonanceMetrics,
    ) -> List[str]:
        """공명 근거 수집"""
        evidence = []

        if emotion_metrics.emotion_keywords_found:
            evidence.append(
                f"감정 키워드 발견: {', '.join(emotion_metrics.emotion_keywords_found[:3])}"
            )

        if strategy_metrics.strategy_patterns_matched:
            evidence.append(
                f"전략 패턴 매칭: {len(strategy_metrics.strategy_patterns_matched)}개 패턴"
            )

        if rhythm_metrics.rhythm_indicators:
            evidence.append(
                f"리듬 지표 발견: {', '.join(rhythm_metrics.rhythm_indicators[:2])}"
            )

        if keyword_metrics.emotion_keywords_found:
            evidence.append(
                f"공명 키워드 매칭: {len(keyword_metrics.emotion_keywords_found)}개"
            )

        return evidence

    def _generate_dissonance_warnings(
        self,
        overall_score: float,
        emotion_metrics: ResonanceMetrics,
        strategy_metrics: ResonanceMetrics,
        rhythm_metrics: ResonanceMetrics,
        profile: Dict[str, Any],
    ) -> List[str]:
        """불협화음 경고 생성"""
        warnings = []

        if overall_score < 0.5:
            warnings.append("심각한 공명 부족 - 시그니처 특성이 거의 반영되지 않음")

        if emotion_metrics.emotion_score < 0.3:
            warnings.append(f"{profile['emotion_code']} 감정이 전혀 드러나지 않음")

        if strategy_metrics.strategy_score < 0.3:
            warnings.append(f"{profile['strategy_code']} 전략이 명확하지 않음")

        if rhythm_metrics.rhythm_score < 0.3:
            warnings.append(f"{profile['rhythm_flow']} 리듬감이 부족함")

        return warnings


# 편의 함수들
def evaluate_resonance(
    response_text: str, signature_id: str
) -> Tuple[float, ResonanceReport]:
    """공명 평가 편의 함수"""
    evaluator = ResonanceEvaluator()
    report = evaluator.evaluate_resonance(response_text, signature_id)
    return report.overall_score, report


def quick_resonance_check(
    response_text: str, signature_id: str, threshold: float = 0.85
) -> bool:
    """빠른 공명 성공 여부 체크"""
    score, _ = evaluate_resonance(response_text, signature_id)
    return score >= threshold


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Resonance Evaluator 테스트")

    evaluator = ResonanceEvaluator()

    # 테스트 응답들
    test_responses = {
        "Echo-Aurora": """
        이 문제에 대해 깊이 공감하며, 따뜻한 마음으로 접근해보겠습니다.
        우선 관련된 모든 사람들의 감정과 입장을 이해하는 것이 중요합니다.
        배려와 돌봄의 관점에서 인간적인 해결책을 찾아야 합니다.
        """,
        "Echo-Phoenix": """
        이것은 혁신적인 접근이 필요한 도전입니다!
        기존의 틀을 과감하게 벗어나 새로운 변화를 만들어야 합니다.
        역동적이고 창조적인 돌파구를 통해 전환점을 마련하겠습니다.
        """,
        "Echo-Sage": """
        체계적인 분석을 통해 이 문제를 접근하겠습니다.
        데이터와 근거를 바탕으로 논리적인 해결방안을 도출해야 합니다.
        신중하고 정확한 검토를 통해 객관적인 판단을 내리겠습니다.
        """,
    }

    for signature_id, response in test_responses.items():
        print(f"\n🎵 {signature_id} 공명 평가:")

        score, report = evaluate_resonance(response, signature_id)
        print(f"전체 점수: {score:.3f}")
        print(f"감정 공명: {report.emotion_resonance:.3f}")
        print(f"전략 공명: {report.strategy_resonance:.3f}")
        print(f"리듬 공명: {report.rhythm_resonance:.3f}")
        print(f"감염 성공: {'✅ YES' if report.is_successful_infection() else '❌ NO'}")

        if report.resonance_evidence:
            print(f"공명 근거: {', '.join(report.resonance_evidence)}")

    print("\n✅ 테스트 완료")
