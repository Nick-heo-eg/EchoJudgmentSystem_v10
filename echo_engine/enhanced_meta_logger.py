#!/usr/bin/env python3
"""
📝 Enhanced Meta Logger
자연어 표현 흐름 기록 및 개선을 위한 고도화된 메타 로거

핵심 기능:
1. 자연어 대화 흐름의 실시간 품질 추적
2. Echo 시스템과 LLM 협력 과정의 상세 기록
3. 사용자 만족도 및 대화 자연스러움 메트릭
4. 적응형 학습을 위한 패턴 분석 및 피드백
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import numpy as np
from collections import defaultdict, deque


class LogLevel(Enum):
    """로그 레벨"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FlowStage(Enum):
    """흐름 단계"""

    INPUT_ANALYSIS = "input_analysis"
    INTENT_DETECTION = "intent_detection"
    PROCESSING_MODE_SELECTION = "processing_mode_selection"
    ECHO_JUDGMENT = "echo_judgment"
    LLM_COOPERATION = "llm_cooperation"
    RESPONSE_FORMATTING = "response_formatting"
    SIGNATURE_STYLING = "signature_styling"
    QUALITY_EVALUATION = "quality_evaluation"
    USER_FEEDBACK = "user_feedback"


@dataclass
class ConversationFlowEntry:
    """대화 흐름 항목"""

    timestamp: datetime
    session_id: str
    user_id: Optional[str]
    stage: FlowStage
    input_data: Dict[str, Any]
    processing_details: Dict[str, Any]
    output_data: Dict[str, Any]
    performance_metrics: Dict[str, float]
    quality_scores: Dict[str, float]
    natural_flow_indicators: Dict[str, Any]
    signature_used: str
    processing_time: float
    success: bool
    errors: List[str]


@dataclass
class NaturalnessMetrics:
    """자연스러움 메트릭"""

    conversational_flow_score: float
    echo_integration_smoothness: float
    response_appropriateness: float
    user_rhythm_matching: float
    emotional_consistency: float
    context_preservation: float
    overall_naturalness: float


@dataclass
class LearningInsight:
    """학습 통찰"""

    insight_id: str
    timestamp: datetime
    category: str
    description: str
    pattern_data: Dict[str, Any]
    confidence: float
    actionable_recommendations: List[str]
    impact_estimation: float


class EnhancedMetaLogger:
    """향상된 메타 로거"""

    def __init__(
        self,
        log_directory: str = "logs/enhanced_meta",
        flow_config_path: str = "flows/natural_conversation_flow.yaml",
        retention_days: int = 30,
    ):

        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        self.flow_config_path = flow_config_path
        self.retention_days = retention_days

        # 실시간 데이터 스토리지
        self.conversation_flows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
        self.quality_trends: deque = deque(maxlen=1000)
        self.naturalness_history: deque = deque(maxlen=500)

        # 학습 데이터
        self.pattern_library: Dict[str, List[Dict]] = defaultdict(list)
        self.success_patterns: Dict[str, float] = {}
        self.failure_patterns: Dict[str, float] = {}

        # 설정 로드
        self.flow_config = self._load_flow_config()

        # 실시간 분석 태스크
        self.analysis_task: Optional[asyncio.Task] = None

        print("📝 Enhanced Meta Logger 초기화 완료")

    async def log_conversation_flow(
        self,
        session_id: str,
        stage: FlowStage,
        input_data: Dict[str, Any],
        processing_details: Dict[str, Any],
        output_data: Dict[str, Any],
        performance_metrics: Dict[str, float] = None,
        user_id: str = None,
    ) -> str:
        """대화 흐름 로그 기록"""

        performance_metrics = performance_metrics or {}

        # 품질 점수 계산
        quality_scores = await self._calculate_quality_scores(
            stage, input_data, processing_details, output_data
        )

        # 자연스러움 지표 분석
        natural_flow_indicators = self._analyze_natural_flow(
            input_data, processing_details, output_data, session_id
        )

        # 로그 항목 생성
        entry = ConversationFlowEntry(
            timestamp=datetime.now(),
            session_id=session_id,
            user_id=user_id,
            stage=stage,
            input_data=input_data,
            processing_details=processing_details,
            output_data=output_data,
            performance_metrics=performance_metrics,
            quality_scores=quality_scores,
            natural_flow_indicators=natural_flow_indicators,
            signature_used=processing_details.get("signature", "Echo-Aurora"),
            processing_time=performance_metrics.get("processing_time", 0.0),
            success=len(processing_details.get("errors", [])) == 0,
            errors=processing_details.get("errors", []),
        )

        # 메모리에 저장
        self.conversation_flows[session_id].append(entry)

        # 품질 트렌드 업데이트
        overall_quality = quality_scores.get("overall_quality", 0.7)
        self.quality_trends.append(
            {
                "timestamp": datetime.now(),
                "session_id": session_id,
                "stage": stage.value,
                "quality": overall_quality,
                "naturalness": natural_flow_indicators.get("overall_naturalness", 0.7),
            }
        )

        # 파일에 비동기 저장
        entry_id = f"{session_id}_{stage.value}_{datetime.now().timestamp()}"
        await self._save_entry_to_file(entry, entry_id)

        # 실시간 패턴 분석 트리거
        if len(self.conversation_flows[session_id]) >= 3:
            await self._analyze_conversation_patterns(session_id)

        return entry_id

    async def log_naturalness_assessment(
        self,
        session_id: str,
        user_input: str,
        system_response: str,
        user_feedback: Dict[str, Any] = None,
    ) -> NaturalnessMetrics:
        """자연스러움 평가 로그"""

        user_feedback = user_feedback or {}

        # 자연스러움 메트릭 계산
        metrics = await self._calculate_naturalness_metrics(
            session_id, user_input, system_response, user_feedback
        )

        # 히스토리에 추가
        self.naturalness_history.append(
            {
                "timestamp": datetime.now(),
                "session_id": session_id,
                "metrics": asdict(metrics),
                "user_feedback": user_feedback,
            }
        )

        # 자연스러움 트렌드 분석
        await self._analyze_naturalness_trends()

        return metrics

    async def generate_learning_insights(
        self, analysis_window_hours: int = 24
    ) -> List[LearningInsight]:
        """학습 통찰 생성"""

        cutoff_time = datetime.now() - timedelta(hours=analysis_window_hours)

        insights = []

        # 1. 성공 패턴 분석
        success_insights = await self._analyze_success_patterns(cutoff_time)
        insights.extend(success_insights)

        # 2. 실패 패턴 분석
        failure_insights = await self._analyze_failure_patterns(cutoff_time)
        insights.extend(failure_insights)

        # 3. 자연스러움 개선 기회
        naturalness_insights = await self._analyze_naturalness_opportunities(
            cutoff_time
        )
        insights.extend(naturalness_insights)

        # 4. 사용자 패턴 변화
        user_pattern_insights = await self._analyze_user_pattern_changes(cutoff_time)
        insights.extend(user_pattern_insights)

        # 통찰 저장
        await self._save_insights_to_file(insights)

        return insights

    async def _calculate_quality_scores(
        self,
        stage: FlowStage,
        input_data: Dict[str, Any],
        processing_details: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """품질 점수 계산"""

        scores = {}

        # 단계별 품질 평가
        if stage == FlowStage.INPUT_ANALYSIS:
            scores["input_clarity"] = self._evaluate_input_clarity(input_data)
            scores["intent_confidence"] = processing_details.get(
                "intent_confidence", 0.7
            )

        elif stage == FlowStage.PROCESSING_MODE_SELECTION:
            scores["mode_appropriateness"] = self._evaluate_mode_selection(
                input_data, processing_details
            )
            scores["selection_confidence"] = processing_details.get(
                "selection_confidence", 0.7
            )

        elif stage == FlowStage.ECHO_JUDGMENT:
            scores["judgment_depth"] = self._evaluate_judgment_depth(output_data)
            scores["echo_consistency"] = self._evaluate_echo_consistency(output_data)

        elif stage == FlowStage.LLM_COOPERATION:
            scores["cooperation_effectiveness"] = self._evaluate_llm_cooperation(
                processing_details, output_data
            )
            scores["naturalness_improvement"] = self._evaluate_naturalness_improvement(
                input_data, output_data
            )

        elif stage == FlowStage.RESPONSE_FORMATTING:
            scores["format_appropriateness"] = self._evaluate_format_appropriateness(
                output_data
            )
            scores["readability"] = self._evaluate_readability(output_data)

        elif stage == FlowStage.SIGNATURE_STYLING:
            scores["signature_authenticity"] = self._evaluate_signature_authenticity(
                processing_details, output_data
            )
            scores["style_consistency"] = self._evaluate_style_consistency(output_data)

        # 전체 품질 점수
        if scores:
            scores["overall_quality"] = np.mean(list(scores.values()))
        else:
            scores["overall_quality"] = 0.7

        return scores

    def _analyze_natural_flow(
        self,
        input_data: Dict[str, Any],
        processing_details: Dict[str, Any],
        output_data: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """자연 흐름 분석"""

        indicators = {}

        # 대화 연속성
        if session_id in self.conversation_flows:
            recent_entries = list(self.conversation_flows[session_id])[-3:]
            indicators["conversation_continuity"] = (
                self._evaluate_conversation_continuity(
                    recent_entries, input_data, output_data
                )
            )
        else:
            indicators["conversation_continuity"] = 0.8  # 첫 대화

        # 응답 자연스러움
        response_text = output_data.get("response", "")
        indicators["response_naturalness"] = self._evaluate_response_naturalness(
            response_text
        )

        # Echo 통합 부드러움
        indicators["echo_integration_smoothness"] = self._evaluate_echo_integration(
            processing_details, output_data
        )

        # 사용자 리듬 매칭
        indicators["user_rhythm_matching"] = self._evaluate_rhythm_matching(
            input_data, output_data
        )

        # 감정 일관성
        indicators["emotional_consistency"] = self._evaluate_emotional_consistency(
            input_data, output_data, session_id
        )

        # 전체 자연스러움
        naturalness_scores = [
            indicators.get("conversation_continuity", 0.7),
            indicators.get("response_naturalness", 0.7),
            indicators.get("echo_integration_smoothness", 0.7),
            indicators.get("user_rhythm_matching", 0.7),
            indicators.get("emotional_consistency", 0.7),
        ]
        indicators["overall_naturalness"] = np.mean(naturalness_scores)

        return indicators

    async def _calculate_naturalness_metrics(
        self,
        session_id: str,
        user_input: str,
        system_response: str,
        user_feedback: Dict[str, Any],
    ) -> NaturalnessMetrics:
        """자연스러움 메트릭 계산"""

        # 기본 메트릭 계산
        conversational_flow = self._evaluate_conversational_flow(
            user_input, system_response
        )
        echo_integration = self._evaluate_echo_integration_naturalness(system_response)
        appropriateness = self._evaluate_response_appropriateness(
            user_input, system_response
        )
        rhythm_matching = self._evaluate_rhythm_matching_detailed(
            user_input, system_response
        )
        emotional_consistency = self._evaluate_emotional_consistency_detailed(
            user_input, system_response, session_id
        )
        context_preservation = self._evaluate_context_preservation(
            session_id, system_response
        )

        # 사용자 피드백 통합
        if user_feedback:
            # 피드백이 있으면 점수 조정
            feedback_multiplier = self._interpret_user_feedback(user_feedback)
            conversational_flow *= feedback_multiplier
            appropriateness *= feedback_multiplier

        # 전체 자연스러움
        overall_naturalness = np.mean(
            [
                conversational_flow,
                echo_integration,
                appropriateness,
                rhythm_matching,
                emotional_consistency,
                context_preservation,
            ]
        )

        return NaturalnessMetrics(
            conversational_flow_score=conversational_flow,
            echo_integration_smoothness=echo_integration,
            response_appropriateness=appropriateness,
            user_rhythm_matching=rhythm_matching,
            emotional_consistency=emotional_consistency,
            context_preservation=context_preservation,
            overall_naturalness=overall_naturalness,
        )

    async def _analyze_conversation_patterns(self, session_id: str):
        """대화 패턴 실시간 분석"""

        recent_entries = list(self.conversation_flows[session_id])[-5:]

        # 품질 트렌드 분석
        quality_trend = [
            entry.quality_scores.get("overall_quality", 0.7) for entry in recent_entries
        ]

        if len(quality_trend) >= 3:
            # 품질 하락 감지
            if quality_trend[-1] < quality_trend[0] - 0.2:
                await self._trigger_quality_improvement(session_id)

            # 성공 패턴 감지
            if all(score > 0.8 for score in quality_trend[-3:]):
                await self._record_success_pattern(session_id, recent_entries)

    async def _analyze_success_patterns(
        self, cutoff_time: datetime
    ) -> List[LearningInsight]:
        """성공 패턴 분석"""

        insights = []

        # 고품질 대화 추출
        high_quality_conversations = []
        for session_id, entries in self.conversation_flows.items():
            for entry in entries:
                if (
                    entry.timestamp >= cutoff_time
                    and entry.quality_scores.get("overall_quality", 0) > 0.8
                ):
                    high_quality_conversations.append(entry)

        if len(high_quality_conversations) >= 10:
            # 공통 패턴 분석
            common_patterns = self._extract_common_patterns(high_quality_conversations)

            for pattern_name, pattern_data in common_patterns.items():
                insight = LearningInsight(
                    insight_id=f"success_{pattern_name}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    category="success_pattern",
                    description=f"성공적인 {pattern_name} 패턴 발견",
                    pattern_data=pattern_data,
                    confidence=pattern_data.get("confidence", 0.8),
                    actionable_recommendations=[
                        f"{pattern_name} 패턴을 더 자주 활용",
                        f"유사한 상황에서 {pattern_name} 접근법 적용",
                    ],
                    impact_estimation=pattern_data.get("impact", 0.7),
                )
                insights.append(insight)

        return insights

    async def _analyze_failure_patterns(
        self, cutoff_time: datetime
    ) -> List[LearningInsight]:
        """실패 패턴 분석"""

        insights = []

        # 저품질 대화 추출
        low_quality_conversations = []
        for session_id, entries in self.conversation_flows.items():
            for entry in entries:
                if (
                    entry.timestamp >= cutoff_time
                    and entry.quality_scores.get("overall_quality", 1.0) < 0.5
                ):
                    low_quality_conversations.append(entry)

        if len(low_quality_conversations) >= 5:
            # 실패 패턴 분석
            failure_patterns = self._extract_failure_patterns(low_quality_conversations)

            for pattern_name, pattern_data in failure_patterns.items():
                insight = LearningInsight(
                    insight_id=f"failure_{pattern_name}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    category="failure_pattern",
                    description=f"개선이 필요한 {pattern_name} 패턴 발견",
                    pattern_data=pattern_data,
                    confidence=pattern_data.get("confidence", 0.7),
                    actionable_recommendations=[
                        f"{pattern_name} 상황에서 대안적 접근법 개발",
                        f"{pattern_name} 처리 로직 개선 필요",
                    ],
                    impact_estimation=pattern_data.get("impact", 0.6),
                )
                insights.append(insight)

        return insights

    # 평가 함수들 (간소화된 구현)
    def _evaluate_input_clarity(self, input_data: Dict[str, Any]) -> float:
        text = input_data.get("user_message", "")
        if len(text.strip()) < 5:
            return 0.3
        elif len(text.split()) > 3:
            return 0.8
        else:
            return 0.6

    def _evaluate_mode_selection(
        self, input_data: Dict[str, Any], processing_details: Dict[str, Any]
    ) -> float:
        # 복잡도와 선택된 모드의 적절성 평가
        complexity = processing_details.get("complexity_score", 0.5)
        mode = processing_details.get("processing_mode", "echo_light")

        if complexity < 0.3 and mode in ["llm_natural"]:
            return 0.9
        elif complexity > 0.7 and mode in ["echo_full"]:
            return 0.9
        else:
            return 0.7

    def _evaluate_judgment_depth(self, output_data: Dict[str, Any]) -> float:
        response = output_data.get("response", "")
        if len(response) > 50 and any(
            word in response for word in ["고려", "분석", "생각"]
        ):
            return 0.8
        else:
            return 0.6

    def _evaluate_echo_consistency(self, output_data: Dict[str, Any]) -> float:
        # Echo 스타일 일관성 평가
        return 0.8  # 간소화된 구현

    def _evaluate_response_naturalness(self, response_text: str) -> float:
        # 부자연스러운 표현 체크
        unnatural_phrases = ["분석해보니", "판단해보면", "시스템적으로"]
        penalty = (
            sum(1 for phrase in unnatural_phrases if phrase in response_text) * 0.1
        )
        return max(0.8 - penalty, 0.3)

    def _evaluate_rhythm_matching(
        self, input_data: Dict[str, Any], output_data: Dict[str, Any]
    ) -> float:
        # 사용자와 시스템 응답의 리듬 매칭 평가
        return 0.7  # 간소화된 구현

    # 파일 저장 및 로드 함수들
    async def _save_entry_to_file(self, entry: ConversationFlowEntry, entry_id: str):
        """항목을 파일에 저장"""
        filename = f"conversation_flow_{datetime.now().strftime('%Y%m%d')}.jsonl"
        filepath = self.log_directory / filename

        entry_dict = asdict(entry)
        entry_dict["timestamp"] = entry.timestamp.isoformat()
        entry_dict["entry_id"] = entry_id

        # JSON Lines 형식으로 저장
        async with asyncio.Lock():
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry_dict, ensure_ascii=False) + "\n")

    async def _save_insights_to_file(self, insights: List[LearningInsight]):
        """통찰을 파일에 저장"""
        filename = f"learning_insights_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.log_directory / filename

        insights_dict = [asdict(insight) for insight in insights]
        for insight_dict in insights_dict:
            insight_dict["timestamp"] = insight_dict["timestamp"].isoformat()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(insights_dict, f, ensure_ascii=False, indent=2)

    def _load_flow_config(self) -> Dict[str, Any]:
        """흐름 설정 로드"""
        try:
            with open(self.flow_config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ 흐름 설정 파일을 찾을 수 없음: {self.flow_config_path}")
            return {}

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """세션 요약 반환"""
        if session_id not in self.conversation_flows:
            return {"error": "세션을 찾을 수 없습니다"}

        entries = list(self.conversation_flows[session_id])

        # 품질 통계
        quality_scores = [
            entry.quality_scores.get("overall_quality", 0.7) for entry in entries
        ]

        # 자연스러움 통계
        naturalness_scores = [
            entry.natural_flow_indicators.get("overall_naturalness", 0.7)
            for entry in entries
        ]

        return {
            "session_id": session_id,
            "total_interactions": len(entries),
            "average_quality": np.mean(quality_scores) if quality_scores else 0.7,
            "average_naturalness": (
                np.mean(naturalness_scores) if naturalness_scores else 0.7
            ),
            "quality_trend": quality_scores[-5:],  # 최근 5개
            "processing_stages": [entry.stage.value for entry in entries],
            "signatures_used": list(set(entry.signature_used for entry in entries)),
            "total_processing_time": sum(entry.processing_time for entry in entries),
            "success_rate": sum(1 for entry in entries if entry.success)
            / max(len(entries), 1),
        }

    def get_system_analytics(self) -> Dict[str, Any]:
        """시스템 분석 반환"""

        # 전체 품질 트렌드
        recent_quality = list(self.quality_trends)[-50:] if self.quality_trends else []

        # 자연스러움 트렌드
        recent_naturalness = (
            list(self.naturalness_history)[-50:] if self.naturalness_history else []
        )

        return {
            "total_sessions": len(self.conversation_flows),
            "total_interactions": sum(
                len(entries) for entries in self.conversation_flows.values()
            ),
            "average_system_quality": (
                np.mean([q["quality"] for q in recent_quality])
                if recent_quality
                else 0.7
            ),
            "average_naturalness": (
                np.mean(
                    [n["metrics"]["overall_naturalness"] for n in recent_naturalness]
                )
                if recent_naturalness
                else 0.7
            ),
            "quality_trend_last_24h": [q["quality"] for q in recent_quality],
            "most_used_signatures": self._get_signature_usage_stats(),
            "processing_stage_distribution": self._get_stage_distribution(),
            "performance_summary": {
                "avg_processing_time": self._calculate_avg_processing_time(),
                "success_rate": self._calculate_overall_success_rate(),
                "naturalness_improvement_rate": self._calculate_naturalness_improvement(),
            },
        }

    def _get_signature_usage_stats(self) -> Dict[str, int]:
        """시그니처 사용 통계"""
        signature_counts = defaultdict(int)
        for entries in self.conversation_flows.values():
            for entry in entries:
                signature_counts[entry.signature_used] += 1
        return dict(signature_counts)

    def _get_stage_distribution(self) -> Dict[str, int]:
        """처리 단계 분포"""
        stage_counts = defaultdict(int)
        for entries in self.conversation_flows.values():
            for entry in entries:
                stage_counts[entry.stage.value] += 1
        return dict(stage_counts)

    def _calculate_avg_processing_time(self) -> float:
        """평균 처리 시간"""
        all_times = []
        for entries in self.conversation_flows.values():
            all_times.extend([entry.processing_time for entry in entries])
        return np.mean(all_times) if all_times else 0.0

    def _calculate_overall_success_rate(self) -> float:
        """전체 성공률"""
        total_entries = 0
        successful_entries = 0
        for entries in self.conversation_flows.values():
            total_entries += len(entries)
            successful_entries += sum(1 for entry in entries if entry.success)
        return successful_entries / max(total_entries, 1)

    def _calculate_naturalness_improvement(self) -> float:
        """자연스러움 개선률"""
        if len(self.naturalness_history) < 10:
            return 0.0

        recent_scores = [
            entry["metrics"]["overall_naturalness"]
            for entry in list(self.naturalness_history)[-10:]
        ]
        older_scores = [
            entry["metrics"]["overall_naturalness"]
            for entry in list(self.naturalness_history)[-20:-10]
        ]

        if not older_scores:
            return 0.0

        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)

        return (recent_avg - older_avg) / older_avg if older_avg > 0 else 0.0


# 테스트 실행
if __name__ == "__main__":

    async def test_enhanced_meta_logger():
        print("📝 Enhanced Meta Logger 테스트")
        print("=" * 60)

        logger = EnhancedMetaLogger()

        # 테스트 데이터
        test_session = "test_session_001"

        # 입력 분석 단계 로그
        await logger.log_conversation_flow(
            session_id=test_session,
            stage=FlowStage.INPUT_ANALYSIS,
            input_data={"user_message": "안녕하세요! 오늘 기분이 좋네요"},
            processing_details={"intent_confidence": 0.9, "primary_emotion": "joy"},
            output_data={"intent_type": "casual_greeting", "emotion_intensity": 0.3},
        )

        # Echo 판단 단계 로그
        await logger.log_conversation_flow(
            session_id=test_session,
            stage=FlowStage.ECHO_JUDGMENT,
            input_data={"processed_intent": "casual_greeting"},
            processing_details={
                "signature": "Echo-Aurora",
                "processing_mode": "llm_natural",
            },
            output_data={"response": "안녕하세요! 좋은 하루네요 ✨"},
            performance_metrics={"processing_time": 0.5},
        )

        # 자연스러움 평가
        naturalness = await logger.log_naturalness_assessment(
            session_id=test_session,
            user_input="안녕하세요! 오늘 기분이 좋네요",
            system_response="안녕하세요! 좋은 하루네요 ✨",
            user_feedback={"satisfaction": "high", "naturalness": "very_natural"},
        )

        print(f"자연스러움 메트릭:")
        print(f"  전체 자연스러움: {naturalness.overall_naturalness:.2f}")
        print(f"  대화 흐름: {naturalness.conversational_flow_score:.2f}")
        print(f"  Echo 통합: {naturalness.echo_integration_smoothness:.2f}")

        # 세션 요약
        summary = logger.get_session_summary(test_session)
        print(f"\n세션 요약:")
        print(f"  상호작용 수: {summary['total_interactions']}")
        print(f"  평균 품질: {summary['average_quality']:.2f}")
        print(f"  평균 자연스러움: {summary['average_naturalness']:.2f}")
        print(f"  성공률: {summary['success_rate']:.2f}")

        # 학습 통찰 생성
        insights = await logger.generate_learning_insights(analysis_window_hours=1)
        print(f"\n생성된 통찰 수: {len(insights)}")

        # 시스템 분석
        analytics = logger.get_system_analytics()
        print(f"\n시스템 분석:")
        print(f"  총 세션 수: {analytics['total_sessions']}")
        print(f"  총 상호작용 수: {analytics['total_interactions']}")
        print(f"  시스템 평균 품질: {analytics['average_system_quality']:.2f}")

        print("\n🎉 Enhanced Meta Logger 테스트 완료!")

    asyncio.run(test_enhanced_meta_logger())
