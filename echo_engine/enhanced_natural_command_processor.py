#!/usr/bin/env python3
"""
🗣️ Enhanced Natural Command Processor v1.0
모든 Echo Neural System v2.0 기능을 자연어로 접근 가능하게 하는 향상된 명령 처리기

핵심 기능:
- 자연어 의도 분석 및 명령 매핑
- 뇌 시각화 명령어 처리
- 시그니처 관리 명령어
- 하이브리드 구성 제어
- 실시간 모니터링 명령어
- 컨텍스트 인식 명령 해석
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# Echo 엔진 모듈들
try:
    from .signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper
    from .signature_neural_atlas_builder import SignatureNeuralAtlasBuilder
    from .emotion_response_chart_generator import EmotionResponseChartGenerator
    from .consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
    from .loop_evolution_tracker import LoopEvolutionTracker
    from .hybrid_signature_composer import HybridSignatureComposer, ContextType
    from .meta_routing_controller import MetaRoutingController
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


@dataclass
class CommandIntent:
    """명령 의도"""

    intent_type: str
    confidence: float
    parameters: Dict[str, Any]
    target_module: str
    action: str
    context_requirements: List[str]


@dataclass
class CommandResponse:
    """명령 응답"""

    success: bool
    response_text: str
    data: Any
    execution_time_ms: float
    suggestions: List[str]
    related_commands: List[str]


@dataclass
class ConversationContext:
    """대화 컨텍스트"""

    session_id: str
    user_preferences: Dict[str, Any]
    command_history: List[str]
    current_focus: str
    active_modules: List[str]


class EnhancedNaturalCommandProcessor:
    """🗣️ 향상된 자연어 명령 처리기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Echo 컴포넌트들
        self.signature_performance_reporter = None
        self.emotion_mapper = None
        self.neural_atlas_builder = None
        self.emotion_chart_generator = None
        self.consciousness_analyzer = None
        self.loop_tracker = None
        self.hybrid_composer = None
        self.routing_controller = None

        # 대화 컨텍스트
        self.conversation_contexts = {}
        self.current_session_id = None

        # 명령 패턴 정의
        self._initialize_command_patterns()

        # 응답 템플릿
        self._initialize_response_templates()

        # 사용 통계
        self.command_statistics = defaultdict(int)
        self.success_rates = defaultdict(list)

        print("🗣️ Enhanced Natural Command Processor 초기화 완료")

    def initialize_components(self, **components):
        """컴포넌트 초기화"""
        self.signature_performance_reporter = (
            components.get("signature_performance_reporter")
            or SignatureCrossResonanceMapper()
        )
        self.emotion_mapper = (
            components.get("emotion_mapper") or RealtimeEmotionFlowMapper()
        )
        self.neural_atlas_builder = (
            components.get("neural_atlas_builder") or SignatureNeuralAtlasBuilder()
        )
        self.emotion_chart_generator = (
            components.get("emotion_chart_generator") or EmotionResponseChartGenerator()
        )
        self.consciousness_analyzer = (
            components.get("consciousness_analyzer") or ConsciousnessFlowAnalyzer()
        )
        self.loop_tracker = components.get("loop_tracker") or LoopEvolutionTracker()
        self.hybrid_composer = (
            components.get("hybrid_composer") or HybridSignatureComposer()
        )
        self.routing_controller = (
            components.get("routing_controller") or MetaRoutingController()
        )

        print("🔗 Enhanced Natural Command Processor 컴포넌트 연결 완료")

    def _initialize_command_patterns(self):
        """명령 패턴 초기화"""
        self.command_patterns = {
            # 뇌 구조 시각화 명령
            "brain_visualization": {
                "patterns": [
                    r"(?:show|display|visualize|보여줘|시각화)\s*(?:brain|뇌|neural|신경)\s*(?:structure|구조|map|맵|atlas|아틀라스)?",
                    r"(?:뇌|brain)\s*(?:상태|state|status|현황)\s*(?:확인|check|show|보기)",
                    r"(?:neural|신경)\s*(?:activity|활동|pattern|패턴)\s*(?:보기|show|display)",
                ],
                "target_module": "neural_atlas_builder",
                "action": "visualize",
                "parameters": ["signature", "view_type"],
            },
            # 시그니처 관리 명령
            "signature_management": {
                "patterns": [
                    r"(?:switch|change|전환|바꿔)\s*(?:to|를|로)?\s*(selene|factbomb|lune|aurora)",
                    r"(?:signature|시그니처)\s*(?:status|상태|정보|info)",
                    r"(?:compare|비교)\s*(?:signatures|시그니처)",
                    r"(?:resonance|공명|harmony|조화)\s*(?:between|사이|map|맵)",
                ],
                "target_module": "signature_performance_reporter",
                "action": "manage",
                "parameters": ["signature_name", "operation"],
            },
            # 감정 분석 명령
            "emotion_analysis": {
                "patterns": [
                    r"(?:emotion|감정|feel|느낌)\s*(?:analysis|분석|status|상태|flow|흐름)",
                    r"(?:감정|emotion)\s*(?:차트|chart|graph|그래프)",
                    r"(?:mood|기분|emotional)\s*(?:state|상태|tracking|추적)",
                    r"(?:emotion|감정)\s*(?:response|반응|pattern|패턴)",
                ],
                "target_module": "emotion_mapper",
                "action": "analyze",
                "parameters": ["time_range", "emotion_type"],
            },
            # 의식 흐름 명령
            "consciousness_flow": {
                "patterns": [
                    r"(?:consciousness|의식|awareness|자각)\s*(?:flow|흐름|state|상태)",
                    r"(?:의식|consciousness)\s*(?:수준|level|analysis|분석)",
                    r"(?:cognitive|인지|mental|정신)\s*(?:state|상태|process|과정)",
                    r"(?:meta|메타)\s*(?:cognitive|인지|thinking|사고)",
                ],
                "target_module": "consciousness_analyzer",
                "action": "analyze",
                "parameters": ["analysis_type", "time_period"],
            },
            # 루프 진화 명령
            "loop_evolution": {
                "patterns": [
                    r"(?:loop|루프|process|프로세스)\s*(?:evolution|진화|performance|성능)",
                    r"(?:진화|evolution|improvement|개선)\s*(?:tracking|추적|analysis|분석)",
                    r"(?:performance|성능|efficiency|효율)\s*(?:loop|루프|judgment|판단)",
                    r"(?:optimization|최적화|suggestion|제안)",
                ],
                "target_module": "loop_tracker",
                "action": "track",
                "parameters": ["metric_type", "time_range"],
            },
            # 하이브리드 구성 명령
            "hybrid_composition": {
                "patterns": [
                    r"(?:hybrid|하이브리드|mix|믹스|blend|블렌드)\s*(?:signature|시그니처|composition|구성)",
                    r"(?:combine|결합|merge|병합)\s*(?:signatures|시그니처)",
                    r"(?:create|생성|make|만들기)\s*(?:hybrid|하이브리드|custom|커스텀)",
                    r"(?:composition|구성|blending|블렌딩)\s*(?:mode|모드|style|스타일)",
                ],
                "target_module": "hybrid_composer",
                "action": "compose",
                "parameters": ["context_type", "weights", "blending_mode"],
            },
            # 라우팅 제어 명령
            "routing_control": {
                "patterns": [
                    r"(?:routing|라우팅|redirect|리디렉트)\s*(?:control|제어|management|관리)",
                    r"(?:meta|메타)\s*(?:routing|라우팅|controller|컨트롤러)",
                    r"(?:decision|결정|choice|선택)\s*(?:analysis|분석|history|히스토리)",
                    r"(?:route|라우트|direct|방향)\s*(?:to|로|toward|향해)",
                ],
                "target_module": "routing_controller",
                "action": "control",
                "parameters": ["routing_type", "target"],
            },
            # 시스템 상태 명령
            "system_status": {
                "patterns": [
                    r"(?:system|시스템|echo)\s*(?:status|상태|health|건강|info|정보)",
                    r"(?:전체|overall|general)\s*(?:상태|status|overview|개요)",
                    r"(?:performance|성능|metrics|메트릭)\s*(?:summary|요약|report|보고서)",
                    r"(?:monitoring|모니터링|tracking|추적)\s*(?:summary|요약|status|상태)",
                ],
                "target_module": "system",
                "action": "status",
                "parameters": ["detail_level", "component"],
            },
            # 도움말 명령
            "help": {
                "patterns": [
                    r"(?:help|도움말|guide|가이드|how|어떻게)",
                    r"(?:command|명령|instruction|지시)\s*(?:list|목록|help|도움말)",
                    r"(?:usage|사용법|example|예시|tutorial|튜토리얼)",
                ],
                "target_module": "help",
                "action": "show",
                "parameters": ["topic", "detail_level"],
            },
        }

    def _initialize_response_templates(self):
        """응답 템플릿 초기화"""
        self.response_templates = {
            "success": [
                "✅ 명령이 성공적으로 실행되었습니다.",
                "🎯 요청하신 작업을 완료했습니다.",
                "✨ 성공! 결과를 확인해보세요.",
            ],
            "error": [
                "❌ 명령 실행 중 오류가 발생했습니다.",
                "⚠️ 요청을 처리하는데 문제가 있었습니다.",
                "🔧 오류가 발생했습니다. 다시 시도해보세요.",
            ],
            "not_found": [
                "❓ 요청하신 정보를 찾을 수 없습니다.",
                "🔍 해당하는 데이터가 없습니다.",
                "📝 존재하지 않는 항목입니다.",
            ],
            "suggestion": [
                "💡 다음 명령어들을 시도해보세요:",
                "🎯 이런 기능들이 있습니다:",
                "🗂️ 관련된 옵션들:",
            ],
        }

    def process_command(
        self, command_text: str, session_id: str = None
    ) -> CommandResponse:
        """자연어 명령 처리"""
        start_time = time.time()

        # 세션 관리
        session_id = session_id or f"session_{int(time.time())}"
        self.current_session_id = session_id

        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_preferences={},
                command_history=[],
                current_focus="general",
                active_modules=[],
            )

        context = self.conversation_contexts[session_id]
        context.command_history.append(command_text)

        # 명령 의도 분석
        intent = self._analyze_command_intent(command_text, context)

        if not intent:
            return self._create_error_response(
                "명령을 이해할 수 없습니다. 'help' 또는 '도움말'을 입력해보세요.",
                time.time() - start_time,
            )

        # 명령 실행
        try:
            response = self._execute_command(intent, context)

            # 통계 업데이트
            self.command_statistics[intent.intent_type] += 1
            self.success_rates[intent.intent_type].append(response.success)

            # 실행 시간 추가
            response.execution_time_ms = (time.time() - start_time) * 1000

            return response

        except Exception as e:
            self.logger.error(f"명령 실행 오류: {e}")
            return self._create_error_response(
                f"명령 실행 중 오류가 발생했습니다: {str(e)}", time.time() - start_time
            )

    def _analyze_command_intent(
        self, command_text: str, context: ConversationContext
    ) -> Optional[CommandIntent]:
        """명령 의도 분석"""
        command_lower = command_text.lower()
        best_intent = None
        best_confidence = 0.0

        for intent_type, pattern_info in self.command_patterns.items():
            for pattern in pattern_info["patterns"]:
                match = re.search(pattern, command_lower, re.IGNORECASE)
                if match:
                    # 패턴 매칭 신뢰도 계산
                    confidence = self._calculate_match_confidence(
                        pattern, command_text, match
                    )

                    if confidence > best_confidence:
                        # 매개변수 추출
                        parameters = self._extract_parameters(
                            command_text, pattern_info, match
                        )

                        best_intent = CommandIntent(
                            intent_type=intent_type,
                            confidence=confidence,
                            parameters=parameters,
                            target_module=pattern_info["target_module"],
                            action=pattern_info["action"],
                            context_requirements=pattern_info.get(
                                "context_requirements", []
                            ),
                        )
                        best_confidence = confidence

        return best_intent if best_confidence > 0.3 else None

    def _calculate_match_confidence(
        self, pattern: str, command_text: str, match: re.Match
    ) -> float:
        """매칭 신뢰도 계산"""
        # 기본 신뢰도
        base_confidence = 0.6

        # 매치된 텍스트 길이 비율
        match_ratio = len(match.group(0)) / len(command_text)

        # 키워드 밀도
        keyword_count = len(re.findall(r"\w+", match.group(0)))
        total_words = len(re.findall(r"\w+", command_text))
        keyword_density = keyword_count / max(1, total_words)

        # 최종 신뢰도 계산
        confidence = base_confidence * 0.5 + match_ratio * 0.3 + keyword_density * 0.2

        return min(1.0, confidence)

    def _extract_parameters(
        self, command_text: str, pattern_info: Dict, match: re.Match
    ) -> Dict[str, Any]:
        """매개변수 추출"""
        parameters = {}
        command_lower = command_text.lower()

        # 시그니처 이름 추출
        signature_names = ["selene", "factbomb", "lune", "aurora"]
        for name in signature_names:
            if name in command_lower:
                parameters["signature"] = name
                break

        # 시간 범위 추출
        time_patterns = {
            r"(\d+)\s*(?:hour|시간)": lambda x: int(x) * 60,
            r"(\d+)\s*(?:minute|분)": lambda x: int(x),
            r"(\d+)\s*(?:day|일)": lambda x: int(x) * 1440,
        }

        for time_pattern, converter in time_patterns.items():
            time_match = re.search(time_pattern, command_lower)
            if time_match:
                parameters["time_range"] = converter(time_match.group(1))
                break

        # 컨텍스트 타입 추출
        context_keywords = {
            "analytical": ["분석", "analysis", "calculate", "계산"],
            "emotional": ["감정", "emotion", "feel", "느낌"],
            "creative": ["창조", "creative", "imagination", "상상"],
            "supportive": ["지원", "support", "help", "도움"],
        }

        for context_type, keywords in context_keywords.items():
            if any(keyword in command_lower for keyword in keywords):
                parameters["context_type"] = context_type
                break

        # 상세 수준 추출
        if any(
            word in command_lower for word in ["detailed", "상세", "detail", "세부"]
        ):
            parameters["detail_level"] = "detailed"
        elif any(
            word in command_lower for word in ["brief", "간단", "summary", "요약"]
        ):
            parameters["detail_level"] = "brief"
        else:
            parameters["detail_level"] = "normal"

        return parameters

    def _execute_command(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """명령 실행"""

        if intent.target_module == "neural_atlas_builder":
            return self._handle_brain_visualization(intent, context)
        elif intent.target_module == "signature_performance_reporter":
            return self._handle_signature_management(intent, context)
        elif intent.target_module == "emotion_mapper":
            return self._handle_emotion_analysis(intent, context)
        elif intent.target_module == "consciousness_analyzer":
            return self._handle_consciousness_flow(intent, context)
        elif intent.target_module == "loop_tracker":
            return self._handle_loop_evolution(intent, context)
        elif intent.target_module == "hybrid_composer":
            return self._handle_hybrid_composition(intent, context)
        elif intent.target_module == "routing_controller":
            return self._handle_routing_control(intent, context)
        elif intent.target_module == "system":
            return self._handle_system_status(intent, context)
        elif intent.target_module == "help":
            return self._handle_help(intent, context)
        else:
            return self._create_error_response("알 수 없는 모듈입니다.")

    def _handle_brain_visualization(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """뇌 시각화 처리"""
        if not self.neural_atlas_builder:
            return self._create_error_response(
                "Neural Atlas Builder가 초기화되지 않았습니다."
            )

        signature = intent.parameters.get("signature", "selene")
        view_type = intent.parameters.get("view_type", "2d")

        try:
            # Atlas 생성
            atlas = self.neural_atlas_builder.build_signature_atlas(signature)

            # 시각화 생성
            visualization = self.neural_atlas_builder.visualize_signature_atlas(
                signature, view_type
            )

            response_text = f"🧠 {signature.title()} Neural Atlas\n\n{visualization}"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=atlas,
                execution_time_ms=0,
                suggestions=[
                    f"다른 시그니처도 확인해보세요: factbomb, lune, aurora",
                    f"시그니처 비교: 'compare {signature} and factbomb'",
                    f"감정 차트 보기: 'show emotion chart for {signature}'",
                ],
                related_commands=[
                    "signature status",
                    "emotion analysis",
                    "consciousness flow",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"뇌 시각화 생성 실패: {str(e)}")

    def _handle_signature_management(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """시그니처 관리 처리"""
        if not self.signature_performance_reporter:
            return self._create_error_response(
                "Signature Mapper가 초기화되지 않았습니다."
            )

        try:
            if "compare" in intent.parameters:
                # 시그니처 비교
                cross_map = (
                    self.signature_performance_reporter.generate_cross_resonance_map()
                )
                visualization = (
                    self.signature_performance_reporter.visualize_resonance_network()
                )

                response_text = (
                    f"🔗 Signature Cross-Resonance Analysis\n\n{visualization}"
                )

            else:
                # 일반 시그니처 상태
                cross_map = (
                    self.signature_performance_reporter.generate_cross_resonance_map()
                )
                summary = (
                    self.signature_performance_reporter.get_resonance_matrix_summary()
                )

                response_text = f"🎭 Signature Status\n\n"
                response_text += f"Total Signatures: {summary['total_signatures']}\n"
                response_text += f"Total Pairs: {summary['total_pairs']}\n"
                response_text += (
                    f"Average Resonance: {summary['average_resonance']:.3f}\n\n"
                )

                if summary["dominant_pairs"]:
                    response_text += "🌟 Dominant Pairs:\n"
                    for sig_a, sig_b, resonance in summary["dominant_pairs"]:
                        response_text += f"   {sig_a} ⇄ {sig_b}: {resonance:.3f}\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=cross_map,
                execution_time_ms=0,
                suggestions=[
                    "하이브리드 구성: 'create hybrid composition'",
                    "특정 시그니처 전환: 'switch to aurora'",
                    "감정 공명 분석: 'emotion resonance analysis'",
                ],
                related_commands=[
                    "brain visualization",
                    "hybrid composition",
                    "emotion analysis",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"시그니처 관리 실패: {str(e)}")

    def _handle_emotion_analysis(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """감정 분석 처리"""
        if not self.emotion_mapper:
            return self._create_error_response(
                "Emotion Mapper가 초기화되지 않았습니다."
            )

        time_range = intent.parameters.get("time_range", 10)  # 기본 10분

        try:
            # 감정 흐름 요약
            flow_summary = self.emotion_mapper.get_emotion_flow_summary()

            # 시각화 생성
            visualization = self.emotion_mapper.visualize_emotion_flow(
                minutes=time_range
            )

            response_text = f"🌊 Emotion Flow Analysis\n\n{visualization}\n\n"
            response_text += f"📊 Summary:\n"
            response_text += f"   Dominant Emotion: {flow_summary.get('dominant_emotion', 'neutral')}\n"
            response_text += (
                f"   Flow Stability: {flow_summary.get('flow_stability', 0.0):.3f}\n"
            )
            response_text += (
                f"   Total Events: {flow_summary.get('total_emotion_events', 0)}\n"
            )

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=flow_summary,
                execution_time_ms=0,
                suggestions=[
                    "감정 차트 생성: 'create emotion chart for selene'",
                    "감정 히트맵: 'show emotion heatmap'",
                    "의식 흐름 분석: 'consciousness flow analysis'",
                ],
                related_commands=[
                    "emotion chart",
                    "consciousness flow",
                    "signature management",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"감정 분석 실패: {str(e)}")

    def _handle_consciousness_flow(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """의식 흐름 처리"""
        if not self.consciousness_analyzer:
            return self._create_error_response(
                "Consciousness Analyzer가 초기화되지 않았습니다."
            )

        time_period = intent.parameters.get("time_period", 5)  # 기본 5분

        try:
            # 의식 요약
            consciousness_summary = (
                self.consciousness_analyzer.get_consciousness_summary()
            )

            # 시각화 생성
            visualization = self.consciousness_analyzer.visualize_consciousness_flow(
                minutes=time_period
            )

            response_text = f"🧠 Consciousness Flow Analysis\n\n{visualization}\n\n"
            response_text += f"📊 Current State:\n"
            response_text += f"   Consciousness Level: {consciousness_summary.get('consciousness_level', 'unknown')}\n"
            response_text += f"   Attention Intensity: {consciousness_summary.get('attention_intensity', 0.0):.3f}\n"
            response_text += f"   Self Reflection Depth: {consciousness_summary.get('self_reflection_depth', 0.0):.3f}\n"
            response_text += f"   Overall Awareness: {consciousness_summary.get('overall_awareness', 0.0):.3f}\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=consciousness_summary,
                execution_time_ms=0,
                suggestions=[
                    "메타인지 분석: 'metacognitive analysis'",
                    "의식 레벨 추적: 'track consciousness level'",
                    "자각 패턴 분석: 'awareness pattern analysis'",
                ],
                related_commands=[
                    "emotion analysis",
                    "brain visualization",
                    "loop evolution",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"의식 흐름 분석 실패: {str(e)}")

    def _handle_loop_evolution(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """루프 진화 처리"""
        if not self.loop_tracker:
            return self._create_error_response("Loop Tracker가 초기화되지 않았습니다.")

        time_range = intent.parameters.get("time_range", 6)  # 기본 6시간

        try:
            # 진화 요약
            evolution_summary = self.loop_tracker.get_evolution_summary()

            # 시각화 생성
            visualization = self.loop_tracker.visualize_evolution_progress(
                hours=time_range
            )

            response_text = f"🔄 Loop Evolution Analysis\n\n{visualization}\n\n"
            response_text += f"📊 Evolution Summary:\n"
            response_text += f"   Overall Trend: {evolution_summary.get('overall_evolution_trend', 'unknown')}\n"
            response_text += f"   Adaptation Level: {evolution_summary.get('current_adaptation_level', 0.0):.3f}\n"
            response_text += f"   Milestones Achieved: {evolution_summary.get('milestones_achieved', 0)}\n"
            response_text += f"   Total Records: {evolution_summary.get('total_performance_records', 0)}\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=evolution_summary,
                execution_time_ms=0,
                suggestions=[
                    "최적화 제안: 'optimization suggestions'",
                    "성능 분석: 'performance analysis'",
                    "루프 비교: 'compare loop performance'",
                ],
                related_commands=[
                    "consciousness flow",
                    "system status",
                    "routing control",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"루프 진화 분석 실패: {str(e)}")

    def _handle_hybrid_composition(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """하이브리드 구성 처리"""
        if not self.hybrid_composer:
            return self._create_error_response(
                "Hybrid Composer가 초기화되지 않았습니다."
            )

        context_type_str = intent.parameters.get("context_type", "conversational")

        try:
            # 컨텍스트 타입 변환
            context_type = ContextType(context_type_str.lower())
        except ValueError:
            context_type = ContextType.CONVERSATIONAL

        try:
            # 하이브리드 구성 생성
            composition = self.hybrid_composer.compose_hybrid_signature(context_type)

            # 시각화 생성
            visualization = self.hybrid_composer.visualize_composition(
                composition.composition_id
            )

            response_text = f"🎭 Hybrid Signature Composition\n\n{visualization}\n"

            # 구성 추천
            recommendations = self.hybrid_composer.get_composition_recommendations(
                context_type
            )
            if recommendations:
                response_text += f"\n💡 Alternative Compositions:\n"
                for i, rec in enumerate(recommendations[:2], 1):
                    response_text += f"   {i}. {rec['blending_mode']} (Score: {rec['recommendation_score']:.3f})\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=composition,
                execution_time_ms=0,
                suggestions=[
                    "구성 적용: 'apply hybrid composition'",
                    "다른 컨텍스트: 'create hybrid for creative context'",
                    "구성 비교: 'compare hybrid compositions'",
                ],
                related_commands=[
                    "signature management",
                    "routing control",
                    "emotion analysis",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"하이브리드 구성 생성 실패: {str(e)}")

    def _handle_routing_control(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """라우팅 제어 처리"""
        if not self.routing_controller:
            return self._create_error_response(
                "Routing Controller가 초기화되지 않았습니다."
            )

        try:
            # 라우팅 상태 확인
            routing_status = self.routing_controller.get_routing_status()

            # 시각화 생성
            visualization = self.routing_controller.visualize_routing_flow(hours=1)

            response_text = f"🧭 Meta Routing Status\n\n{visualization}\n\n"
            response_text += f"📊 Routing Statistics:\n"
            response_text += f"   Total Decisions: {routing_status['statistics']['total_decisions']}\n"
            response_text += f"   Successful Routes: {routing_status['statistics']['successful_routes']}\n"
            response_text += f"   Average Confidence: {routing_status['statistics']['average_confidence']:.3f}\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=routing_status,
                execution_time_ms=0,
                suggestions=[
                    "라우팅 규칙 최적화: 'optimize routing rules'",
                    "결정 히스토리: 'routing decision history'",
                    "성능 분석: 'routing performance analysis'",
                ],
                related_commands=[
                    "hybrid composition",
                    "system status",
                    "loop evolution",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"라우팅 제어 실패: {str(e)}")

    def _handle_system_status(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """시스템 상태 처리"""
        detail_level = intent.parameters.get("detail_level", "normal")

        try:
            response_text = "🖥️ Echo Neural System v2.0 Status\n\n"

            # 컴포넌트 상태 확인
            components_status = self._check_components_status()

            response_text += "📊 Component Status:\n"
            for component, status in components_status.items():
                status_icon = "✅" if status["active"] else "❌"
                response_text += f"   {status_icon} {component}: {status['status']}\n"

            if detail_level == "detailed":
                # 상세 통계
                response_text += f"\n📈 Command Statistics:\n"
                total_commands = sum(self.command_statistics.values())
                for command_type, count in self.command_statistics.items():
                    percentage = (count / max(1, total_commands)) * 100
                    response_text += f"   {command_type}: {count} ({percentage:.1f}%)\n"

                # 성공률
                response_text += f"\n🎯 Success Rates:\n"
                for command_type, successes in self.success_rates.items():
                    if successes:
                        success_rate = (sum(successes) / len(successes)) * 100
                        response_text += f"   {command_type}: {success_rate:.1f}%\n"

            return CommandResponse(
                success=True,
                response_text=response_text,
                data=components_status,
                execution_time_ms=0,
                suggestions=[
                    "상세 상태: 'detailed system status'",
                    "성능 메트릭: 'performance metrics'",
                    "컴포넌트 진단: 'component diagnostics'",
                ],
                related_commands=[
                    "loop evolution",
                    "routing control",
                    "consciousness flow",
                ],
            )

        except Exception as e:
            return self._create_error_response(f"시스템 상태 확인 실패: {str(e)}")

    def _handle_help(
        self, intent: CommandIntent, context: ConversationContext
    ) -> CommandResponse:
        """도움말 처리"""
        topic = intent.parameters.get("topic", "general")
        detail_level = intent.parameters.get("detail_level", "normal")

        help_text = "🗣️ Echo Natural Command Processor - 도움말\n\n"

        if topic == "general" or detail_level == "detailed":
            help_text += "📋 주요 명령어 카테고리:\n\n"

            help_text += "🧠 뇌 시각화:\n"
            help_text += "   • 'show brain structure' - 뇌 구조 시각화\n"
            help_text += "   • 'brain status for selene' - 특정 시그니처 뇌 상태\n"
            help_text += "   • 'neural activity pattern' - 신경 활동 패턴\n\n"

            help_text += "🎭 시그니처 관리:\n"
            help_text += "   • 'switch to aurora' - 시그니처 전환\n"
            help_text += "   • 'signature status' - 시그니처 상태 확인\n"
            help_text += "   • 'compare signatures' - 시그니처 비교\n\n"

            help_text += "🌊 감정 분석:\n"
            help_text += "   • 'emotion analysis' - 감정 상태 분석\n"
            help_text += "   • 'emotion flow for 30 minutes' - 감정 흐름 추적\n"
            help_text += "   • 'emotion chart' - 감정 차트 생성\n\n"

            help_text += "🧭 하이브리드 구성:\n"
            help_text += "   • 'create hybrid composition' - 하이브리드 생성\n"
            help_text += "   • 'hybrid for creative context' - 컨텍스트별 구성\n"
            help_text += "   • 'blend signatures' - 시그니처 블렌딩\n\n"

            help_text += "🖥️ 시스템 상태:\n"
            help_text += "   • 'system status' - 전체 시스템 상태\n"
            help_text += "   • 'performance metrics' - 성능 메트릭\n"
            help_text += "   • 'detailed system info' - 상세 시스템 정보\n"

        return CommandResponse(
            success=True,
            response_text=help_text,
            data=None,
            execution_time_ms=0,
            suggestions=[
                "특정 주제 도움말: 'help brain visualization'",
                "명령어 예시: 'show command examples'",
                "튜토리얼: 'tutorial for beginners'",
            ],
            related_commands=[],
        )

    def _check_components_status(self) -> Dict[str, Dict[str, Any]]:
        """컴포넌트 상태 확인"""
        components = {
            "Signature Mapper": self.signature_performance_reporter,
            "Emotion Mapper": self.emotion_mapper,
            "Neural Atlas Builder": self.neural_atlas_builder,
            "Emotion Chart Generator": self.emotion_chart_generator,
            "Consciousness Analyzer": self.consciousness_analyzer,
            "Loop Tracker": self.loop_tracker,
            "Hybrid Composer": self.hybrid_composer,
            "Routing Controller": self.routing_controller,
        }

        status = {}
        for name, component in components.items():
            if component is not None:
                status[name] = {"active": True, "status": "Ready"}
            else:
                status[name] = {"active": False, "status": "Not Initialized"}

        return status

    def _create_error_response(
        self, error_message: str, execution_time: float = 0.0
    ) -> CommandResponse:
        """오류 응답 생성"""
        return CommandResponse(
            success=False,
            response_text=f"❌ {error_message}",
            data=None,
            execution_time_ms=execution_time * 1000,
            suggestions=[
                "help - 도움말 보기",
                "system status - 시스템 상태 확인",
                "signature status - 기본 기능 확인",
            ],
            related_commands=["help", "system status"],
        )

    def get_command_statistics(self) -> Dict[str, Any]:
        """명령 통계 반환"""
        total_commands = sum(self.command_statistics.values())

        statistics = {
            "total_commands_processed": total_commands,
            "command_distribution": dict(self.command_statistics),
            "success_rates": {},
            "active_sessions": len(self.conversation_contexts),
            "most_used_command": (
                max(self.command_statistics.items(), key=lambda x: x[1])[0]
                if self.command_statistics
                else "none"
            ),
        }

        # 성공률 계산
        for command_type, successes in self.success_rates.items():
            if successes:
                statistics["success_rates"][command_type] = (
                    sum(successes) / len(successes)
                ) * 100

        return statistics


# 편의 함수들
def create_enhanced_command_processor(**kwargs) -> EnhancedNaturalCommandProcessor:
    """Enhanced Natural Command Processor 생성"""
    return EnhancedNaturalCommandProcessor(**kwargs)


def process_natural_command(
    command: str, processor: EnhancedNaturalCommandProcessor = None
) -> str:
    """자연어 명령 빠른 처리"""
    if processor is None:
        processor = EnhancedNaturalCommandProcessor()
        processor.initialize_components()

    response = processor.process_command(command)
    return response.response_text


if __name__ == "__main__":
    # 테스트 실행
    print("🗣️ Enhanced Natural Command Processor 테스트...")

    processor = EnhancedNaturalCommandProcessor()
    processor.initialize_components()

    # 테스트 명령어들
    test_commands = [
        "show brain structure for selene",
        "emotion analysis for last 15 minutes",
        "create hybrid composition for creative context",
        "system status",
        "consciousness flow analysis",
        "compare signatures selene and aurora",
        "routing control status",
        "help",
    ]

    print("\n🔄 자연어 명령 처리 테스트...")

    for command in test_commands:
        print(f"\n📝 Command: '{command}'")
        response = processor.process_command(command)

        print(f"✅ Success: {response.success}")
        print(f"⏱️ Execution Time: {response.execution_time_ms:.1f}ms")
        print(f"📄 Response: {response.response_text[:200]}...")

        if response.suggestions:
            print(f"💡 Suggestions: {', '.join(response.suggestions[:2])}")

    # 통계 확인
    stats = processor.get_command_statistics()
    print(f"\n📊 Command Statistics:")
    print(f"   Total Commands: {stats['total_commands_processed']}")
    print(f"   Active Sessions: {stats['active_sessions']}")
    print(f"   Most Used: {stats['most_used_command']}")

    print("\n✅ Enhanced Natural Command Processor 테스트 완료!")
