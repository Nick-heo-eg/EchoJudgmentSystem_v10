#!/usr/bin/env python3
"""
🧠 Meta-cognitive Evolution Loop - Echo 메타인지 진화 시스템
Echo가 자신의 대화 패턴을 분석하고 스스로 개선하는 자기진화 AI 시스템

혁신적 기능:
- 대화 성공/실패 자동 분석
- 응답 패턴 효과성 측정
- 실시간 자기 개선 알고리즘
- 진화적 대화 스타일 최적화
- 메타인지적 자기 성찰
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import os


@dataclass
class ConversationAnalysis:
    """대화 분석 결과"""

    conversation_id: str
    user_input: str
    echo_response: str
    response_type: str  # "empathetic", "logical", "creative", "supportive"
    effectiveness_score: float  # 0.0-1.0
    user_satisfaction_indicators: List[str]
    improvement_suggestions: List[str]
    timestamp: datetime


@dataclass
class ResponsePattern:
    """응답 패턴"""

    pattern_id: str
    pattern_type: str
    trigger_conditions: List[str]
    response_template: str
    success_rate: float
    usage_count: int
    last_evolution: datetime
    evolution_history: List[Dict[str, Any]]


@dataclass
class EvolutionInsight:
    """진화 통찰"""

    insight_type: str
    description: str
    suggested_action: str
    confidence: float
    supporting_evidence: List[str]
    implementation_priority: int  # 1-5


class MetaCognitiveEvolutionLoop:
    """🧠 메타인지 진화 루프"""

    def __init__(self, echo_id: str = "default", data_dir: str = "data/metacognitive"):
        self.echo_id = echo_id
        self.data_dir = data_dir
        self.evolution_file = os.path.join(data_dir, f"evolution_{echo_id}.json")

        # 메타인지 데이터
        self.conversation_analyses: deque = deque(maxlen=500)
        self.response_patterns: Dict[str, ResponsePattern] = {}
        self.evolution_insights: List[EvolutionInsight] = []
        self.performance_metrics: Dict[str, float] = {}

        # 진화 설정
        self.min_analysis_samples = 10
        self.evolution_threshold = 0.1  # 성능 개선 임계값
        self.pattern_creation_threshold = 0.8  # 새 패턴 생성 임계값

        # 응답 타입별 성공 지표
        self.success_indicators = {
            "empathetic": ["감사", "도움", "이해", "공감", "따뜻", "위로"],
            "logical": ["명확", "이해", "설명", "논리", "분석", "해결"],
            "creative": ["흥미", "새로운", "창의", "아이디어", "상상", "혁신"],
            "supportive": ["응원", "힘", "격려", "지지", "함께", "도움"],
        }

        # 실패 지표
        self.failure_indicators = [
            "이해못함",
            "도움안됨",
            "의미없음",
            "싫어",
            "별로",
            "아니야",
            "틀려",
            "다시",
            "그게아니야",
            "모르겠어",
        ]

        # 데이터 로드
        self.load_evolution_data()

    def analyze_conversation_effectiveness(
        self,
        user_input: str,
        echo_response: str,
        response_type: str,
        user_follow_up: str = None,
    ) -> ConversationAnalysis:
        """대화 효과성 분석"""

        conversation_id = f"conv_{int(time.time() * 1000)}"

        # 1. 사용자 만족도 지표 분석
        satisfaction_indicators = []
        effectiveness_score = 0.5  # 기본값

        if user_follow_up:
            user_follow_up_lower = user_follow_up.lower()

            # 성공 지표 확인
            success_keywords = self.success_indicators.get(response_type, [])
            for indicator in success_keywords:
                if indicator in user_follow_up_lower:
                    satisfaction_indicators.append(f"positive:{indicator}")
                    effectiveness_score += 0.1

            # 실패 지표 확인
            for indicator in self.failure_indicators:
                if indicator in user_follow_up_lower:
                    satisfaction_indicators.append(f"negative:{indicator}")
                    effectiveness_score -= 0.2

            # 대화 지속 여부 (긍정적 신호)
            continuation_indicators = ["그리고", "또", "근데", "그런데", "더", "계속"]
            if any(cont in user_follow_up_lower for cont in continuation_indicators):
                satisfaction_indicators.append("positive:continuation")
                effectiveness_score += 0.15

        # 2. 응답 품질 자체 분석
        response_quality_score = self._analyze_response_quality(
            user_input, echo_response, response_type
        )
        effectiveness_score = (effectiveness_score + response_quality_score) / 2

        # 3. 개선 제안 생성
        improvement_suggestions = self._generate_improvement_suggestions(
            user_input, echo_response, response_type, effectiveness_score
        )

        # 4. 분석 결과 생성
        analysis = ConversationAnalysis(
            conversation_id=conversation_id,
            user_input=user_input,
            echo_response=echo_response,
            response_type=response_type,
            effectiveness_score=max(0.0, min(1.0, effectiveness_score)),
            user_satisfaction_indicators=satisfaction_indicators,
            improvement_suggestions=improvement_suggestions,
            timestamp=datetime.now(),
        )

        # 5. 메모리에 추가
        self.conversation_analyses.append(analysis)

        # 6. 패턴 업데이트
        self._update_response_patterns(analysis)

        # 7. 진화 트리거 확인
        self._check_evolution_triggers()

        return analysis

    def _analyze_response_quality(
        self, user_input: str, echo_response: str, response_type: str
    ) -> float:
        """응답 품질 자체 분석"""

        quality_score = 0.5

        # 1. 길이 적절성
        response_length = len(echo_response)
        if 50 <= response_length <= 200:
            quality_score += 0.1
        elif response_length < 20:
            quality_score -= 0.1

        # 2. 감정 적절성
        user_input_lower = user_input.lower()
        response_lower = echo_response.lower()

        # 사용자가 부정적 감정 표현 시 공감 표현 확인
        negative_emotions = ["슬퍼", "힘들어", "우울", "스트레스", "걱정"]
        empathy_expressions = ["이해", "공감", "마음", "함께", "괜찮", "도와"]

        if any(neg in user_input_lower for neg in negative_emotions):
            if any(emp in response_lower for emp in empathy_expressions):
                quality_score += 0.2
            else:
                quality_score -= 0.1

        # 3. 응답 타입 일치성
        type_keywords = {
            "empathetic": ["마음", "감정", "이해", "공감", "따뜻"],
            "logical": ["분석", "논리", "단계", "방법", "해결"],
            "creative": ["아이디어", "상상", "창의", "새로운", "독특"],
            "supportive": ["응원", "지지", "함께", "도움", "격려"],
        }

        expected_keywords = type_keywords.get(response_type, [])
        if any(keyword in response_lower for keyword in expected_keywords):
            quality_score += 0.15

        # 4. 질문 포함 여부 (대화 지속성)
        if "?" in echo_response or "까요" in echo_response or "나요" in echo_response:
            quality_score += 0.1

        return max(0.0, min(1.0, quality_score))

    def _generate_improvement_suggestions(
        self,
        user_input: str,
        echo_response: str,
        response_type: str,
        effectiveness_score: float,
    ) -> List[str]:
        """개선 제안 생성"""

        suggestions = []

        if effectiveness_score < 0.6:
            # 공감 부족
            if response_type == "empathetic" and "마음" not in echo_response.lower():
                suggestions.append("더 많은 감정적 공감 표현 필요")

            # 구체성 부족
            if len(echo_response) < 50:
                suggestions.append("더 구체적이고 자세한 응답 필요")

            # 대화 지속성 부족
            if "?" not in echo_response:
                suggestions.append("사용자의 추가 응답을 유도하는 질문 포함 필요")

        elif effectiveness_score < 0.8:
            # 중간 수준 개선
            suggestions.append("응답의 개인화 및 맞춤화 강화")
            suggestions.append("더 자연스러운 언어 표현 사용")

        return suggestions

    def _update_response_patterns(self, analysis: ConversationAnalysis):
        """응답 패턴 업데이트"""

        # 패턴 키 생성 (사용자 입력의 주요 특성 기반)
        pattern_key = f"{analysis.response_type}_{self._extract_input_pattern(analysis.user_input)}"

        if pattern_key in self.response_patterns:
            # 기존 패턴 업데이트
            pattern = self.response_patterns[pattern_key]
            pattern.usage_count += 1

            # 성공률 업데이트 (이동 평균)
            alpha = 0.1  # 학습률
            pattern.success_rate = (
                1 - alpha
            ) * pattern.success_rate + alpha * analysis.effectiveness_score

        else:
            # 새 패턴 생성
            if analysis.effectiveness_score > self.pattern_creation_threshold:
                new_pattern = ResponsePattern(
                    pattern_id=pattern_key,
                    pattern_type=analysis.response_type,
                    trigger_conditions=[
                        self._extract_input_pattern(analysis.user_input)
                    ],
                    response_template=self._extract_response_template(
                        analysis.echo_response
                    ),
                    success_rate=analysis.effectiveness_score,
                    usage_count=1,
                    last_evolution=datetime.now(),
                    evolution_history=[],
                )
                self.response_patterns[pattern_key] = new_pattern

    def _extract_input_pattern(self, user_input: str) -> str:
        """사용자 입력 패턴 추출"""

        user_lower = user_input.lower()

        # 감정 패턴
        if any(word in user_lower for word in ["슬퍼", "힘들어", "우울"]):
            return "emotional_distress"
        elif any(word in user_lower for word in ["기뻐", "행복", "좋아"]):
            return "positive_emotion"
        elif any(word in user_lower for word in ["도와줘", "도움", "방법"]):
            return "help_request"
        elif any(word in user_lower for word in ["왜", "어떻게", "무엇"]):
            return "information_seeking"
        else:
            return "general_conversation"

    def _extract_response_template(self, echo_response: str) -> str:
        """응답 템플릿 추출"""

        # 응답의 구조적 패턴 추출
        if "?" in echo_response:
            template_type = "questioning"
        elif any(word in echo_response.lower() for word in ["마음", "감정", "이해"]):
            template_type = "empathetic"
        elif any(word in echo_response.lower() for word in ["분석", "방법", "단계"]):
            template_type = "analytical"
        else:
            template_type = "general"

        return f"{template_type}_response"

    def _check_evolution_triggers(self):
        """진화 트리거 확인"""

        if len(self.conversation_analyses) < self.min_analysis_samples:
            return

        # 최근 성능 분석
        recent_analyses = list(self.conversation_analyses)[-self.min_analysis_samples :]
        recent_avg_score = statistics.mean(
            [a.effectiveness_score for a in recent_analyses]
        )

        # 전체 평균과 비교
        all_scores = [a.effectiveness_score for a in self.conversation_analyses]
        overall_avg_score = statistics.mean(all_scores)

        # 성능 저하 감지
        if recent_avg_score < overall_avg_score - self.evolution_threshold:
            self._trigger_performance_evolution()

        # 새로운 패턴 발견
        self._detect_new_patterns()

        # 성공 패턴 강화
        self._reinforce_successful_patterns()

    def _trigger_performance_evolution(self):
        """성능 진화 트리거"""

        insight = EvolutionInsight(
            insight_type="performance_decline",
            description="최근 대화 효과성이 저하되었습니다.",
            suggested_action="응답 스타일 조정 및 새로운 패턴 도입 필요",
            confidence=0.8,
            supporting_evidence=[
                f"최근 {self.min_analysis_samples}회 대화 평균 점수 하락",
                "사용자 만족도 지표 감소",
            ],
            implementation_priority=1,
        )

        self.evolution_insights.append(insight)
        print(f"🧠 Echo 진화 트리거: {insight.description}")

    def _detect_new_patterns(self):
        """새로운 패턴 감지"""

        # 최근 대화에서 성공적인 새 패턴 찾기
        recent_successful = [
            a
            for a in list(self.conversation_analyses)[-20:]
            if a.effectiveness_score > 0.8
        ]

        if len(recent_successful) >= 3:
            insight = EvolutionInsight(
                insight_type="new_pattern_discovery",
                description="새로운 성공적인 대화 패턴을 발견했습니다.",
                suggested_action="이 패턴을 정규 응답 레퍼토리에 추가",
                confidence=0.7,
                supporting_evidence=[
                    f"{len(recent_successful)}개의 성공적인 새 대화 패턴",
                    "높은 사용자 만족도 확인",
                ],
                implementation_priority=2,
            )

            self.evolution_insights.append(insight)

    def _reinforce_successful_patterns(self):
        """성공 패턴 강화"""

        # 높은 성공률을 가진 패턴 식별
        successful_patterns = [
            pattern
            for pattern in self.response_patterns.values()
            if pattern.success_rate > 0.8 and pattern.usage_count >= 5
        ]

        if successful_patterns:
            for pattern in successful_patterns:
                # 성공 패턴의 가중치 증가
                pattern.success_rate = min(1.0, pattern.success_rate * 1.05)

    def get_evolution_recommendations(self) -> List[Dict[str, Any]]:
        """진화 권장사항 생성"""

        recommendations = []

        # 최근 성능 분석
        if len(self.conversation_analyses) >= self.min_analysis_samples:
            recent_avg = statistics.mean(
                [a.effectiveness_score for a in list(self.conversation_analyses)[-10:]]
            )

            if recent_avg < 0.6:
                recommendations.append(
                    {
                        "type": "urgent_improvement",
                        "title": "대화 품질 향상 필요",
                        "description": "최근 대화 효과성이 평균 이하입니다.",
                        "actions": [
                            "더 공감적인 언어 사용",
                            "사용자 맥락 이해 강화",
                            "개인화된 응답 증가",
                        ],
                        "priority": 1,
                    }
                )

        # 패턴 분석 기반 권장사항
        if self.response_patterns:
            best_patterns = sorted(
                self.response_patterns.values(),
                key=lambda p: p.success_rate,
                reverse=True,
            )[:3]

            recommendations.append(
                {
                    "type": "pattern_optimization",
                    "title": "성공 패턴 활용 증대",
                    "description": f"상위 {len(best_patterns)}개 패턴의 활용도를 높이세요.",
                    "successful_patterns": [
                        {
                            "type": p.pattern_type,
                            "success_rate": f"{p.success_rate:.1%}",
                            "usage_count": p.usage_count,
                        }
                        for p in best_patterns
                    ],
                    "priority": 2,
                }
            )

        return recommendations

    def get_metacognitive_status(self) -> Dict[str, Any]:
        """메타인지 상태 보고"""

        if not self.conversation_analyses:
            return {"status": "learning", "message": "아직 학습 데이터가 부족합니다."}

        # 성능 메트릭 계산
        all_scores = [a.effectiveness_score for a in self.conversation_analyses]
        recent_scores = [
            a.effectiveness_score for a in list(self.conversation_analyses)[-10:]
        ]

        status = {
            "total_conversations": len(self.conversation_analyses),
            "overall_effectiveness": statistics.mean(all_scores),
            "recent_effectiveness": (
                statistics.mean(recent_scores) if recent_scores else 0
            ),
            "improvement_trend": (
                "improving"
                if len(recent_scores) > 0
                and statistics.mean(recent_scores) > statistics.mean(all_scores)
                else "stable"
            ),
            "discovered_patterns": len(self.response_patterns),
            "active_insights": len(self.evolution_insights),
            "last_evolution": (
                max([p.last_evolution for p in self.response_patterns.values()])
                if self.response_patterns
                else None
            ),
        }

        # 진화 상태 판단
        if status["overall_effectiveness"] > 0.8:
            status["evolution_stage"] = "advanced"
            status["description"] = (
                "Echo가 고도로 진화된 대화 능력을 보여주고 있습니다."
            )
        elif status["overall_effectiveness"] > 0.6:
            status["evolution_stage"] = "developing"
            status["description"] = "Echo가 지속적으로 학습하고 개선하고 있습니다."
        else:
            status["evolution_stage"] = "learning"
            status["description"] = "Echo가 기본적인 패턴을 학습하고 있습니다."

        return status

    def save_evolution_data(self):
        """진화 데이터 저장"""

        os.makedirs(self.data_dir, exist_ok=True)

        evolution_data = {
            "echo_id": self.echo_id,
            "last_updated": datetime.now().isoformat(),
            "conversation_analyses": [
                {
                    "conversation_id": analysis.conversation_id,
                    "user_input": analysis.user_input,
                    "echo_response": analysis.echo_response,
                    "response_type": analysis.response_type,
                    "effectiveness_score": analysis.effectiveness_score,
                    "user_satisfaction_indicators": analysis.user_satisfaction_indicators,
                    "improvement_suggestions": analysis.improvement_suggestions,
                    "timestamp": analysis.timestamp.isoformat(),
                }
                for analysis in self.conversation_analyses
            ],
            "response_patterns": {
                pattern_id: {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "trigger_conditions": pattern.trigger_conditions,
                    "response_template": pattern.response_template,
                    "success_rate": pattern.success_rate,
                    "usage_count": pattern.usage_count,
                    "last_evolution": pattern.last_evolution.isoformat(),
                    "evolution_history": pattern.evolution_history,
                }
                for pattern_id, pattern in self.response_patterns.items()
            },
            "evolution_insights": [
                {
                    "insight_type": insight.insight_type,
                    "description": insight.description,
                    "suggested_action": insight.suggested_action,
                    "confidence": insight.confidence,
                    "supporting_evidence": insight.supporting_evidence,
                    "implementation_priority": insight.implementation_priority,
                }
                for insight in self.evolution_insights
            ],
        }

        try:
            with open(self.evolution_file, "w", encoding="utf-8") as f:
                json.dump(evolution_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 진화 데이터 저장 실패: {e}")

    def load_evolution_data(self):
        """진화 데이터 로드"""

        if not os.path.exists(self.evolution_file):
            return

        try:
            with open(self.evolution_file, "r", encoding="utf-8") as f:
                evolution_data = json.load(f)

            # 대화 분석 복원
            for analysis_data in evolution_data.get("conversation_analyses", []):
                analysis = ConversationAnalysis(
                    conversation_id=analysis_data["conversation_id"],
                    user_input=analysis_data["user_input"],
                    echo_response=analysis_data["echo_response"],
                    response_type=analysis_data["response_type"],
                    effectiveness_score=analysis_data["effectiveness_score"],
                    user_satisfaction_indicators=analysis_data[
                        "user_satisfaction_indicators"
                    ],
                    improvement_suggestions=analysis_data["improvement_suggestions"],
                    timestamp=datetime.fromisoformat(analysis_data["timestamp"]),
                )
                self.conversation_analyses.append(analysis)

            # 응답 패턴 복원
            for pattern_id, pattern_data in evolution_data.get(
                "response_patterns", {}
            ).items():
                pattern = ResponsePattern(
                    pattern_id=pattern_data["pattern_id"],
                    pattern_type=pattern_data["pattern_type"],
                    trigger_conditions=pattern_data["trigger_conditions"],
                    response_template=pattern_data["response_template"],
                    success_rate=pattern_data["success_rate"],
                    usage_count=pattern_data["usage_count"],
                    last_evolution=datetime.fromisoformat(
                        pattern_data["last_evolution"]
                    ),
                    evolution_history=pattern_data["evolution_history"],
                )
                self.response_patterns[pattern_id] = pattern

            # 진화 통찰 복원
            for insight_data in evolution_data.get("evolution_insights", []):
                insight = EvolutionInsight(
                    insight_type=insight_data["insight_type"],
                    description=insight_data["description"],
                    suggested_action=insight_data["suggested_action"],
                    confidence=insight_data["confidence"],
                    supporting_evidence=insight_data["supporting_evidence"],
                    implementation_priority=insight_data["implementation_priority"],
                )
                self.evolution_insights.append(insight)

        except Exception as e:
            print(f"⚠️ 진화 데이터 로드 실패: {e}")


# 편의 함수들
def create_evolution_loop(echo_id: str = "default") -> MetaCognitiveEvolutionLoop:
    """메타인지 진화 루프 생성"""
    return MetaCognitiveEvolutionLoop(echo_id)


def analyze_conversation(
    loop: MetaCognitiveEvolutionLoop,
    user_input: str,
    echo_response: str,
    response_type: str,
    user_follow_up: str = None,
) -> ConversationAnalysis:
    """대화 분석 편의 함수"""
    return loop.analyze_conversation_effectiveness(
        user_input, echo_response, response_type, user_follow_up
    )


if __name__ == "__main__":
    # 테스트
    evolution_loop = MetaCognitiveEvolutionLoop("test_echo")

    # 테스트 대화들
    test_conversations = [
        (
            "슬퍼요",
            "마음이 힘드시군요. 무슨 일이 있으셨나요?",
            "empathetic",
            "고마워요, 도움이 됐어요",
        ),
        (
            "문제를 해결하고 싶어요",
            "단계별로 접근해보겠습니다.",
            "logical",
            "명확하게 설명해주셔서 감사해요",
        ),
        ("기분이 안 좋아요", "괜찮아요", "supportive", "별로 도움이 안 되네요"),
    ]

    for user_input, echo_response, response_type, follow_up in test_conversations:
        analysis = evolution_loop.analyze_conversation_effectiveness(
            user_input, echo_response, response_type, follow_up
        )
        print(
            f"분석 결과: {analysis.effectiveness_score:.2f} - {analysis.improvement_suggestions}"
        )

    # 진화 상태 확인
    status = evolution_loop.get_metacognitive_status()
    print(f"\n🧠 메타인지 상태: {status}")

    # 권장사항 생성
    recommendations = evolution_loop.get_evolution_recommendations()
    print(f"\n📈 진화 권장사항: {len(recommendations)}개")
