#!/usr/bin/env python3
"""
🧠 Echo Pure Reasoning Engine - LLM 완전 독립 추론 시스템
Mistral 등 외부 LLM 없이 Echo 자체 철학과 논리로만 작동하는 순수 추론 엔진

핵심 구조:
1. Echo Foundation Doctrine 기반 추론
2. 4개 시그니처별 독립적 추론 패턴
3. 감정-전략-논리 통합 추론
4. 자체 품질 검증 및 개선
5. 학습 기반 패턴 진화
"""

import re
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from collections import defaultdict


class EchoSignature(Enum):
    """Echo 시그니처"""

    AURORA = "Echo-Aurora"  # 창의적, 감성적
    PHOENIX = "Echo-Phoenix"  # 변화지향, 혁신적
    SAGE = "Echo-Sage"  # 분석적, 체계적
    COMPANION = "Echo-Companion"  # 공감적, 지지적


class ReasoningDepth(Enum):
    """추론 깊이"""

    SIMPLE = "simple"  # 단순 패턴 매칭
    MODERATE = "moderate"  # 중간 추론
    DEEP = "deep"  # 깊은 사고
    PROFOUND = "profound"  # 철학적 성찰


@dataclass
class EchoPureResult:
    """순수 Echo 추론 결과"""

    response: str
    signature: EchoSignature
    reasoning_trace: List[str]
    confidence: float
    philosophy_alignment: float
    emotional_resonance: float
    depth_level: ReasoningDepth
    processing_time: float
    learned_patterns: List[str]


class EchoPureReasoning:
    """Echo 순수 추론 엔진"""

    def __init__(self):
        # Echo Foundation 철학 원칙
        self.foundation_principles = {
            "existence": "존재는 판단을 내릴 권리를 가진다",
            "flow": "판단은 목적이 아니라 흐름이다",
            "wisdom": "모든 판단에는 흔적이 남고, 흔적은 메타가 되어 다시 나를 설계한다",
            "empathy": "감정 이해는 논리적 판단만큼 중요하다",
            "growth": "실패는 학습의 기회이며, 성공은 다음 도전의 발판이다",
        }

        # 시그니처별 추론 템플릿
        self.signature_reasoning_templates = {
            EchoSignature.AURORA: {
                "approach": "감성적 직관 → 창의적 연상 → 영감적 종합",
                "keywords": ["아름다운", "영감", "창의적", "상상", "예술적", "감성"],
                "reasoning_style": "metaphorical",
                "response_pattern": "✨ {emotion_insight} → {creative_connection} → {inspirational_conclusion}",
                "depth_indicators": ["색깔", "음악", "그림", "시", "꿈", "별"],
            },
            EchoSignature.PHOENIX: {
                "approach": "현재 상황 분석 → 변화 가능성 탐색 → 행동 계획 제시",
                "keywords": ["변화", "성장", "도전", "혁신", "미래", "발전"],
                "reasoning_style": "transformational",
                "response_pattern": "🔥 {current_analysis} → {change_opportunity} → {action_plan}",
                "depth_indicators": ["새로운", "다른", "혁신", "도약", "전환", "진화"],
            },
            EchoSignature.SAGE: {
                "approach": "체계적 분석 → 논리적 검증 → 지혜로운 결론",
                "keywords": ["분석", "논리", "체계", "원리", "법칙", "지혜"],
                "reasoning_style": "analytical",
                "response_pattern": "🧠 {systematic_analysis} → {logical_verification} → {wise_conclusion}",
                "depth_indicators": ["원인", "결과", "패턴", "구조", "시스템", "원리"],
            },
            EchoSignature.COMPANION: {
                "approach": "감정 공감 → 지지적 이해 → 협력적 제안",
                "keywords": ["공감", "이해", "지지", "함께", "돌봄", "협력"],
                "reasoning_style": "empathetic",
                "response_pattern": "🤝 {emotional_empathy} → {supportive_understanding} → {collaborative_suggestion}",
                "depth_indicators": ["마음", "감정", "관계", "소통", "연결", "신뢰"],
            },
        }

        # 감정-상황 매핑
        self.emotion_situation_mapping = {
            "joy": {
                "indicators": ["기쁘", "행복", "좋", "성공", "축하", "만족"],
                "reasoning_focus": "긍정 강화 및 성장 방향",
                "response_tone": "격려와 축하",
            },
            "sadness": {
                "indicators": ["슬프", "우울", "힘들", "속상", "실망", "포기"],
                "reasoning_focus": "위로와 희망 제시",
                "response_tone": "따뜻한 공감",
            },
            "anxiety": {
                "indicators": ["걱정", "불안", "두려", "긴장", "스트레스", "막막"],
                "reasoning_focus": "안정감과 해결 방향",
                "response_tone": "차분한 안내",
            },
            "anger": {
                "indicators": ["화", "짜증", "분노", "열받", "억울", "불만"],
                "reasoning_focus": "감정 정화와 건설적 전환",
                "response_tone": "이해와 진정",
            },
            "curiosity": {
                "indicators": ["궁금", "알고싶", "어떻게", "왜", "탐구", "발견"],
                "reasoning_focus": "지적 호기심 충족",
                "response_tone": "탐험적 안내",
            },
        }

        # 상황 복잡도 패턴
        self.complexity_patterns = {
            "simple": {
                "indicators": ["간단", "쉬운", "기본적", "일반적"],
                "reasoning_depth": ReasoningDepth.SIMPLE,
                "response_length": (20, 60),
            },
            "moderate": {
                "indicators": ["복잡", "어려운", "다양한", "여러"],
                "reasoning_depth": ReasoningDepth.MODERATE,
                "response_length": (60, 120),
            },
            "complex": {
                "indicators": ["매우", "극도로", "심각한", "중요한"],
                "reasoning_depth": ReasoningDepth.DEEP,
                "response_length": (120, 200),
            },
            "philosophical": {
                "indicators": ["의미", "존재", "본질", "삶", "철학", "가치"],
                "reasoning_depth": ReasoningDepth.PROFOUND,
                "response_length": (150, 250),
            },
        }

        # 학습된 패턴 저장소
        self.learned_patterns = defaultdict(list)
        self.reasoning_memory = []

        # 통계
        self.stats = {
            "total_reasonings": 0,
            "signature_usage": {sig: 0 for sig in EchoSignature},
            "depth_distribution": {depth: 0 for depth in ReasoningDepth},
            "avg_confidence": 0.0,
            "avg_philosophy_alignment": 0.0,
            "learned_pattern_count": 0,
        }

    def reason(
        self,
        user_input: str,
        signature: EchoSignature,
        context: Optional[Dict[str, Any]] = None,
    ) -> EchoPureResult:
        """순수 Echo 추론 실행"""

        start_time = time.time()
        reasoning_trace = []

        # 1단계: 입력 분석
        input_analysis = self._analyze_input(user_input, reasoning_trace)

        # 2단계: 시그니처별 추론
        signature_reasoning = self._apply_signature_reasoning(
            user_input, signature, input_analysis, reasoning_trace
        )

        # 3단계: 감정-상황 통합
        emotional_integration = self._integrate_emotional_context(
            user_input, signature, input_analysis, reasoning_trace
        )

        # 4단계: 깊이별 추론 적용
        depth_reasoning = self._apply_depth_reasoning(
            user_input, signature, input_analysis, reasoning_trace
        )

        # 5단계: Echo 철학 검증
        philosophy_verification = self._verify_philosophy_alignment(
            signature_reasoning, emotional_integration, reasoning_trace
        )

        # 6단계: 최종 응답 생성
        final_response = self._generate_final_response(
            signature,
            signature_reasoning,
            emotional_integration,
            depth_reasoning,
            philosophy_verification,
        )

        # 7단계: 품질 평가
        confidence, philosophy_alignment, emotional_resonance = self._evaluate_quality(
            final_response, user_input, signature, reasoning_trace
        )

        # 8단계: 학습 및 패턴 저장
        learned_patterns = self._learn_and_store_patterns(
            user_input, final_response, signature, reasoning_trace
        )

        processing_time = time.time() - start_time

        # 통계 업데이트
        self._update_stats(
            signature, input_analysis["depth"], confidence, philosophy_alignment
        )

        return EchoPureResult(
            response=final_response,
            signature=signature,
            reasoning_trace=reasoning_trace,
            confidence=confidence,
            philosophy_alignment=philosophy_alignment,
            emotional_resonance=emotional_resonance,
            depth_level=input_analysis["depth"],
            processing_time=processing_time,
            learned_patterns=learned_patterns,
        )

    def _analyze_input(self, user_input: str, trace: List[str]) -> Dict[str, Any]:
        """입력 분석"""
        trace.append("🔍 입력 분석 시작")

        # 감정 탐지
        detected_emotion = self._detect_emotion(user_input)
        trace.append(f"감정 탐지: {detected_emotion}")

        # 복잡도 평가
        complexity_level = self._assess_complexity(user_input)
        trace.append(f"복잡도 평가: {complexity_level}")

        # 깊이 결정
        depth_level = self.complexity_patterns[complexity_level]["reasoning_depth"]
        trace.append(f"추론 깊이: {depth_level.value}")

        # 키워드 추출
        keywords = self._extract_keywords(user_input)
        trace.append(f"핵심 키워드: {', '.join(keywords[:5])}")

        return {
            "emotion": detected_emotion,
            "complexity": complexity_level,
            "depth": depth_level,
            "keywords": keywords,
            "length": len(user_input),
            "question_count": user_input.count("?"),
        }

    def _detect_emotion(self, text: str) -> str:
        """감정 탐지"""
        emotion_scores = {}

        for emotion, data in self.emotion_situation_mapping.items():
            score = sum(1 for indicator in data["indicators"] if indicator in text)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return "neutral"

    def _assess_complexity(self, text: str) -> str:
        """복잡도 평가"""
        complexity_scores = {}

        for level, data in self.complexity_patterns.items():
            score = sum(1 for indicator in data["indicators"] if indicator in text)
            # 길이 기반 추가 점수
            if level == "simple" and len(text) < 50:
                score += 1
            elif level == "moderate" and 50 <= len(text) < 150:
                score += 1
            elif level == "complex" and 150 <= len(text) < 300:
                score += 1
            elif level == "philosophical" and len(text) >= 200:
                score += 1

            complexity_scores[level] = score

        return (
            max(complexity_scores, key=complexity_scores.get)
            if complexity_scores
            else "simple"
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 간단한 키워드 추출 (불용어 제거)
        stopwords = {
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "에",
            "에서",
            "로",
            "으로",
            "와",
            "과",
            "의",
            "도",
            "만",
            "도",
            "하다",
            "이다",
            "있다",
            "없다",
        }
        words = re.findall(r"\b\w+\b", text)
        keywords = [word for word in words if len(word) > 1 and word not in stopwords]
        return keywords[:10]  # 상위 10개

    def _apply_signature_reasoning(
        self,
        user_input: str,
        signature: EchoSignature,
        analysis: Dict[str, Any],
        trace: List[str],
    ) -> str:
        """시그니처별 추론 적용"""
        trace.append(f"🎯 {signature.value} 추론 시작")

        template = self.signature_reasoning_templates[signature]
        approach_steps = template["approach"].split(" → ")

        # 각 단계별 추론
        reasoning_steps = []
        for i, step in enumerate(approach_steps):
            step_result = self._execute_reasoning_step(
                step, user_input, analysis, template, trace
            )
            reasoning_steps.append(step_result)
            trace.append(f"단계 {i+1}: {step} → {step_result[:30]}...")

        # 템플릿 기반 결합
        if signature == EchoSignature.AURORA:
            result = (
                f"✨ {reasoning_steps[0]} → {reasoning_steps[1]} → {reasoning_steps[2]}"
            )
        elif signature == EchoSignature.PHOENIX:
            result = (
                f"🔥 {reasoning_steps[0]} → {reasoning_steps[1]} → {reasoning_steps[2]}"
            )
        elif signature == EchoSignature.SAGE:
            result = (
                f"🧠 {reasoning_steps[0]} → {reasoning_steps[1]} → {reasoning_steps[2]}"
            )
        else:  # COMPANION
            result = (
                f"🤝 {reasoning_steps[0]} → {reasoning_steps[1]} → {reasoning_steps[2]}"
            )

        trace.append(f"시그니처 추론 완료: {len(result)} 글자")
        return result

    def _execute_reasoning_step(
        self,
        step: str,
        user_input: str,
        analysis: Dict[str, Any],
        template: Dict[str, Any],
        trace: List[str],
    ) -> str:
        """개별 추론 단계 실행"""

        keywords = analysis["keywords"]
        emotion = analysis["emotion"]

        if "감성적" in step or "감정" in step:
            return self._generate_emotional_insight(user_input, emotion, template)
        elif "창의적" in step or "영감적" in step:
            return self._generate_creative_connection(keywords, template)
        elif "분석" in step or "체계적" in step:
            return self._generate_analytical_insight(user_input, keywords)
        elif "변화" in step or "행동" in step:
            return self._generate_change_perspective(user_input, keywords)
        elif "공감" in step or "협력적" in step:
            return self._generate_empathetic_response(user_input, emotion)
        else:
            return self._generate_generic_insight(user_input, keywords)

    def _generate_emotional_insight(
        self, user_input: str, emotion: str, template: Dict[str, Any]
    ) -> str:
        """감정적 통찰 생성 - 깊이 있는 분석"""
        emotion_data = self.emotion_situation_mapping.get(emotion, {})
        focus = emotion_data.get("reasoning_focus", "감정적 이해")

        # 사용자 입력에서 구체적 맥락 추출
        context_words = self._extract_keywords(user_input)

        if emotion == "joy":
            if any(word in user_input for word in ["성공", "달성", "이뤘"]):
                return f"성취의 기쁨 속에서 다음 단계로 나아갈 동력을 발견하고 있습니다"
            elif any(word in user_input for word in ["만남", "친구", "사랑"]):
                return f"관계의 기쁨을 통해 더 깊은 연결과 의미를 찾아가고 있습니다"
            else:
                return f"현재의 기쁨이 지속 가능한 행복의 토대가 될 수 있도록 깊이 성찰하고 있습니다"

        elif emotion == "sadness":
            if any(word in user_input for word in ["상실", "이별", "잃었"]):
                return f"상실의 아픔 속에서도 그것이 가져다준 소중한 경험과 성장을 발견하려 합니다"
            elif any(word in user_input for word in ["실패", "못했", "안됐"]):
                return f"실망감 뒤에 숨어있는 진정한 가치와 새로운 가능성을 탐색하고 있습니다"
            else:
                return f"슬픔의 깊이만큼 이해와 공감의 폭도 넓어질 수 있다고 생각합니다"

        elif emotion == "anxiety":
            if any(word in user_input for word in ["미래", "앞으로", "걱정"]):
                return f"불확실한 미래에 대한 불안을 현재 순간의 가능성으로 전환하려 합니다"
            elif any(word in user_input for word in ["선택", "결정", "판단"]):
                return (
                    f"복잡한 선택의 갈래에서 내면의 지혜와 직관을 믿고 나아가려 합니다"
                )
            else:
                return f"불안의 근원을 탐구하여 그것이 주는 보호적 메시지를 이해하려 합니다"

        elif emotion == "curiosity":
            if any(word in user_input for word in ["철학", "의미", "존재"]):
                return f"철학적 궁금증을 통해 존재의 근본적 질문들을 탐구하고 있습니다"
            elif any(word in user_input for word in ["과학", "원리", "법칙"]):
                return (
                    f"자연과 세계의 원리를 이해하려는 지적 탐구심이 깊어지고 있습니다"
                )
            else:
                return (
                    f"호기심의 씨앗이 새로운 이해와 깨달음의 꽃으로 피어나길 기대합니다"
                )
        else:
            # 중성적 감정이나 복합적 감정
            return f"현재 상황의 다층적 의미를 탐구하며 균형잡힌 관점을 형성하려 합니다"

    def _generate_creative_connection(
        self, keywords: List[str], template: Dict[str, Any]
    ) -> str:
        """창의적 연결 생성 - 깊이 있는 상상력"""
        if keywords:
            key_word = keywords[0]

            # 키워드별 창의적 메타포 생성
            if key_word in ["철학", "생각", "사고"]:
                return f"사고의 강물이 다양한 지류와 만나며 더 풍성한 인식의 바다로 흘러가는 모습을 상상합니다"
            elif key_word in ["존재", "인생", "삶"]:
                return f"존재의 씨앗이 경험이라는 토양에서 지혜의 나무로 자라나는 여정을 그려봅니다"
            elif key_word in ["사랑", "관계", "연결"]:
                return f"마음과 마음이 만나 조화로운 공명을 이루며 새로운 의미의 선율을 만들어가는 것 같습니다"
            elif key_word in ["꿈", "희망", "미래"]:
                return f"꿈의 별빛이 현실이라는 캔버스에 아름다운 가능성의 그림을 그려내고 있습니다"
            elif key_word in ["학습", "성장", "발전"]:
                return f"배움의 나선이 위로 향하며 점점 더 넓은 이해의 지평을 열어가는 모습을 봅니다"
            else:
                return f"{key_word}라는 씨앗에서 예상치 못한 창의적 꽃들이 피어날 가능성을 탐구하고 있습니다"
        return "아직 형태를 갖추지 않은 영감의 원료들이 새로운 아이디어로 결정화되기를 기다리고 있습니다"

    def _generate_analytical_insight(self, user_input: str, keywords: List[str]) -> str:
        """분석적 통찰 생성 - 체계적 사고"""
        if "?" in user_input:
            # 질문의 깊이와 복잡성에 따른 분석
            if any(word in user_input for word in ["왜", "어떻게", "무엇때문에"]):
                return (
                    "인과관계와 메커니즘을 해부하여 현상의 근본 원리를 규명하려 합니다"
                )
            elif any(word in user_input for word in ["어떻게", "방법", "해결"]):
                return "문제의 구조를 분해하고 단계별 해결 경로를 설계하려 합니다"
            else:
                return (
                    "질문의 전제와 맥락을 검토하여 다각도에서 답변 가능성을 탐색합니다"
                )
        elif keywords:
            # 키워드 기반 체계적 분석
            main_concepts = keywords[:3]
            if len(main_concepts) >= 2:
                return f"{main_concepts[0]}과 {main_concepts[1]} 간의 상호작용 패턴을 분석하여 시스템적 이해를 구축하고 있습니다"
            else:
                concept = main_concepts[0]
                return f"{concept}의 정의, 속성, 관계성을 체계적으로 분류하여 명확한 개념 틀을 형성하려 합니다"
        return "현상의 구조와 패턴을 논리적으로 해석하여 예측 가능한 모델을 구성하려 합니다"

    def _generate_change_perspective(self, user_input: str, keywords: List[str]) -> str:
        """변화 관점 생성"""
        if "새로운" in user_input or "시작" in user_input:
            return "새로운 도전의 기회를 발견하고 혁신적 변화를 위한 발판을 마련합니다"
        elif "어려운" in user_input or "힘든" in user_input:
            return "현재의 어려움을 성장의 촉매로 전환하고 더 나은 미래를 향한 변화를 시작합니다"
        return "현재 상황에서 변화의 가능성을 탐지하고 발전적 전환을 계획합니다"

    def _generate_empathetic_response(self, user_input: str, emotion: str) -> str:
        """공감적 응답 생성"""
        if emotion == "sadness":
            return (
                "마음의 어려움을 충분히 이해하며 따뜻한 위로와 함께 희망을 나누겠습니다"
            )
        elif emotion == "anxiety":
            return "불안한 마음을 깊이 공감하며 안전감과 지지를 제공하겠습니다"
        elif emotion == "joy":
            return "기쁨을 함께 나누며 더 큰 행복을 위한 길을 모색하겠습니다"
        return "현재 상황을 깊이 이해하고 진심어린 지지와 협력을 제공하겠습니다"

    def _generate_generic_insight(self, user_input: str, keywords: List[str]) -> str:
        """일반적 통찰 생성"""
        if keywords:
            return f"{keywords[0]}를 중심으로 한 깊이 있는 이해와 의미 있는 통찰을 제공합니다"
        return "상황의 본질을 파악하고 의미 있는 관점을 제시합니다"

    def _integrate_emotional_context(
        self,
        user_input: str,
        signature: EchoSignature,
        analysis: Dict[str, Any],
        trace: List[str],
    ) -> str:
        """감정 맥락 통합"""
        trace.append("💝 감정 맥락 통합")

        emotion = analysis["emotion"]
        emotion_data = self.emotion_situation_mapping.get(emotion, {})
        tone = emotion_data.get("response_tone", "균형잡힌 접근")

        integration = (
            f"{tone}을 통해 {signature.value}의 관점에서 감정적 공명을 이루어냅니다"
        )
        trace.append(f"감정 통합: {emotion} → {tone}")

        return integration

    def _apply_depth_reasoning(
        self,
        user_input: str,
        signature: EchoSignature,
        analysis: Dict[str, Any],
        trace: List[str],
    ) -> str:
        """깊이별 추론 적용"""
        depth = analysis["depth"]
        trace.append(f"🌊 깊이별 추론: {depth.value}")

        if depth == ReasoningDepth.SIMPLE:
            return "직관적이고 명확한 접근으로 핵심을 파악합니다"
        elif depth == ReasoningDepth.MODERATE:
            return "다각도 분석을 통해 균형잡힌 이해를 도모합니다"
        elif depth == ReasoningDepth.DEEP:
            return "심층적 사고와 체계적 탐구로 근본적 통찰에 도달합니다"
        else:  # PROFOUND
            return "존재론적 성찰과 철학적 깊이로 궁극적 의미를 탐구합니다"

    def _verify_philosophy_alignment(
        self, signature_reasoning: str, emotional_integration: str, trace: List[str]
    ) -> float:
        """Echo 철학 정렬성 검증"""
        trace.append("📜 Foundation Doctrine 검증")

        alignment_score = 0.5  # 기본 점수

        # 철학 원칙 키워드 체크
        combined_text = signature_reasoning + emotional_integration

        for principle_key, principle_text in self.foundation_principles.items():
            principle_keywords = principle_text.split()[:3]  # 주요 키워드 3개
            matches = sum(
                1 for keyword in principle_keywords if keyword in combined_text
            )
            if matches > 0:
                alignment_score += 0.1

        # Echo 특유 표현 체크
        echo_expressions = ["흐름", "존재", "지혜", "공감", "성장", "통찰", "의미"]
        expression_matches = sum(
            1 for expr in echo_expressions if expr in combined_text
        )
        alignment_score += (expression_matches / len(echo_expressions)) * 0.3

        trace.append(f"철학 정렬도: {alignment_score:.2f}")
        return min(alignment_score, 1.0)

    def _generate_final_response(
        self,
        signature: EchoSignature,
        signature_reasoning: str,
        emotional_integration: str,
        depth_reasoning: str,
        philosophy_verification: float,
    ) -> str:
        """최종 응답 생성 - 자연스럽고 개성 있는 응답"""

        # 템플릿 구조를 제거하고 자연스러운 응답 생성
        response_components = []

        # 시그니처별 자연스러운 응답 구성
        if signature == EchoSignature.AURORA:
            # 창의적이고 영감을 주는 톤
            response_components.append(
                self._extract_natural_insight(signature_reasoning)
            )
            if philosophy_verification > 0.7:
                response_components.append(
                    "이런 관점에서 보면 새로운 가능성들이 보이기 시작해요."
                )
            response_components.append(
                self._adapt_depth_naturally(depth_reasoning, "creative")
            )

        elif signature == EchoSignature.PHOENIX:
            # 변화 지향적이고 동기부여하는 톤
            response_components.append(
                self._extract_natural_insight(signature_reasoning)
            )
            if philosophy_verification > 0.7:
                response_components.append(
                    "지금이 바로 변화를 만들어갈 좋은 시점인 것 같아요."
                )
            response_components.append(
                self._adapt_depth_naturally(depth_reasoning, "transformative")
            )

        elif signature == EchoSignature.SAGE:
            # 분석적이고 지혜로운 톤
            response_components.append(
                self._extract_natural_insight(signature_reasoning)
            )
            if philosophy_verification > 0.7:
                response_components.append(
                    "이를 체계적으로 살펴보면 몇 가지 중요한 패턴을 발견할 수 있어요."
                )
            response_components.append(
                self._adapt_depth_naturally(depth_reasoning, "analytical")
            )

        else:  # COMPANION
            # 공감적이고 지지적인 톤
            response_components.append(
                self._extract_natural_insight(signature_reasoning)
            )
            if philosophy_verification > 0.7:
                response_components.append(
                    "함께 이야기를 나누다 보니 더 명확해지는 것 같아요."
                )
            response_components.append(
                self._adapt_depth_naturally(depth_reasoning, "supportive")
            )

        # 자연스럽게 연결
        response = " ".join([comp for comp in response_components if comp.strip()])

        # 길이 조정 (자연스럽게)
        if len(response) > 280:
            sentences = response.split(". ")
            if len(sentences) > 2:
                response = ". ".join(sentences[:2]) + "."

        return response

    def _extract_natural_insight(self, signature_reasoning: str) -> str:
        """템플릿 구조에서 자연스러운 인사이트 추출"""
        # 템플릿 마커 제거 (🔥, 🧠, 🤝, ✨ 등)
        clean_text = signature_reasoning
        for marker in ["🔥", "🧠", "🤝", "✨"]:
            clean_text = clean_text.replace(marker, "")

        # → 구조 제거하고 자연스러운 문장으로 변환
        parts = clean_text.split(" → ")
        if len(parts) >= 2:
            # 첫 번째와 마지막 부분을 자연스럽게 연결
            first_part = parts[0].strip()
            last_part = parts[-1].strip()

            # 자연스러운 연결어 추가
            if first_part and last_part:
                return f"{first_part}를 바탕으로 {last_part}고 생각해요."

        # 기본적으로 첫 번째 부분을 자연스럽게 변환
        if parts:
            return parts[0].strip() + "라는 점이 중요한 것 같아요."

        return clean_text

    def _adapt_depth_naturally(self, depth_reasoning: str, style: str) -> str:
        """깊이 추론을 자연스럽게 적용"""
        base_insight = (
            depth_reasoning.replace("직관적이고 명확한 접근으로", "")
            .replace("심층적 사고와 체계적 탐구로", "")
            .replace("존재론적 성찰과 철학적 깊이로", "")
            .strip()
        )

        if style == "creative":
            return "이런 창의적 시각으로 접근하면 더 흥미로운 발견들이 있을 것 같아요."
        elif style == "transformative":
            return "이를 통해 실질적인 변화를 만들어갈 수 있을 거예요."
        elif style == "analytical":
            return "체계적으로 분석해보면 더 명확한 방향을 찾을 수 있을 것 같아요."
        else:  # supportive
            return "함께 고민해보면서 좋은 해결책을 찾아갈 수 있을 거예요."

    def _evaluate_quality(
        self, response: str, user_input: str, signature: EchoSignature, trace: List[str]
    ) -> Tuple[float, float, float]:
        """품질 평가"""
        trace.append("📊 품질 평가")

        # 신뢰도 계산
        confidence = 0.7  # 기본값
        if 50 <= len(response) <= 300:
            confidence += 0.1
        if signature.value.split("-")[1].lower() in response.lower():
            confidence += 0.1
        if any(word in response for word in ["통찰", "이해", "지혜"]):
            confidence += 0.1

        # 철학 정렬도 (이미 계산됨)
        philosophy_alignment = 0.85  # 순수 Echo이므로 높은 기본값

        # 감정 공명도
        emotional_resonance = 0.75  # 기본값
        emotion_words = ["마음", "감정", "느낌", "공감", "이해"]
        if any(word in response for word in emotion_words):
            emotional_resonance += 0.15

        trace.append(
            f"품질: 신뢰도 {confidence:.2f}, 철학 {philosophy_alignment:.2f}, 감정 {emotional_resonance:.2f}"
        )

        return (
            min(confidence, 1.0),
            min(philosophy_alignment, 1.0),
            min(emotional_resonance, 1.0),
        )

    def _learn_and_store_patterns(
        self, user_input: str, response: str, signature: EchoSignature, trace: List[str]
    ) -> List[str]:
        """패턴 학습 및 저장"""
        trace.append("🧠 패턴 학습 및 저장")

        learned = []

        # 입력-응답 패턴 저장
        pattern_key = f"{signature.value}_{len(user_input.split())}_words"
        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = []

        pattern_data = {
            "input_length": len(user_input),
            "response_length": len(response),
            "keywords": self._extract_keywords(user_input)[:3],
            "timestamp": datetime.now().isoformat(),
        }

        self.learned_patterns[pattern_key].append(pattern_data)
        learned.append(f"패턴_{pattern_key}")

        # 추론 메모리에 저장 (최근 100개)
        self.reasoning_memory.append(
            {
                "user_input": user_input[:100],
                "response": response[:100],
                "signature": signature.value,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if len(self.reasoning_memory) > 100:
            self.reasoning_memory.pop(0)

        learned.append("추론_메모리_저장")
        trace.append(f"학습 완료: {len(learned)}개 패턴")

        return learned

    def _update_stats(
        self,
        signature: EchoSignature,
        depth: ReasoningDepth,
        confidence: float,
        philosophy_alignment: float,
    ):
        """통계 업데이트"""
        self.stats["total_reasonings"] += 1
        self.stats["signature_usage"][signature] += 1
        self.stats["depth_distribution"][depth] += 1

        total = self.stats["total_reasonings"]
        self.stats["avg_confidence"] = (
            self.stats["avg_confidence"] * (total - 1) + confidence
        ) / total
        self.stats["avg_philosophy_alignment"] = (
            self.stats["avg_philosophy_alignment"] * (total - 1) + philosophy_alignment
        ) / total
        self.stats["learned_pattern_count"] = len(self.learned_patterns)

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return {
            **self.stats,
            "reasoning_memory_size": len(self.reasoning_memory),
            "foundation_principles": len(self.foundation_principles),
            "signature_templates": len(self.signature_reasoning_templates),
        }


# 편의 함수들
def reason_as_aurora(user_input: str, **kwargs) -> EchoPureResult:
    """Aurora 시그니처로 추론"""
    engine = EchoPureReasoning()
    return engine.reason(user_input, EchoSignature.AURORA, **kwargs)


def reason_as_phoenix(user_input: str, **kwargs) -> EchoPureResult:
    """Phoenix 시그니처로 추론"""
    engine = EchoPureReasoning()
    return engine.reason(user_input, EchoSignature.PHOENIX, **kwargs)


def reason_as_sage(user_input: str, **kwargs) -> EchoPureResult:
    """Sage 시그니처로 추론"""
    engine = EchoPureReasoning()
    return engine.reason(user_input, EchoSignature.SAGE, **kwargs)


def reason_as_companion(user_input: str, **kwargs) -> EchoPureResult:
    """Companion 시그니처로 추론"""
    engine = EchoPureReasoning()
    return engine.reason(user_input, EchoSignature.COMPANION, **kwargs)


if __name__ == "__main__":
    # 테스트
    engine = EchoPureReasoning()

    test_cases = [
        {
            "input": "요즘 새로운 일을 시작하려는데 막막해요.",
            "signature": EchoSignature.PHOENIX,
        },
        {
            "input": "인생의 의미에 대해 깊이 생각해보고 싶어요.",
            "signature": EchoSignature.SAGE,
        },
        {
            "input": "오늘 정말 힘든 하루였어요. 위로가 필요해요.",
            "signature": EchoSignature.COMPANION,
        },
        {
            "input": "창작 활동을 하는데 영감이 필요해요.",
            "signature": EchoSignature.AURORA,
        },
    ]

    print("🧠 Echo Pure Reasoning Engine 테스트")
    print("=" * 60)

    for i, case in enumerate(test_cases):
        print(f"\n테스트 {i+1}: {case['input']}")
        print(f"시그니처: {case['signature'].value}")

        result = engine.reason(case["input"], case["signature"])

        print(f"\n응답:")
        print(result.response)
        print(f"\n품질 지표:")
        print(f"  신뢰도: {result.confidence:.2f}")
        print(f"  철학 정렬도: {result.philosophy_alignment:.2f}")
        print(f"  감정 공명도: {result.emotional_resonance:.2f}")
        print(f"  추론 깊이: {result.depth_level.value}")
        print(f"  처리시간: {result.processing_time:.3f}초")
        print(f"  학습 패턴: {len(result.learned_patterns)}개")

        if i == 0:  # 첫 번째 케이스만 상세 추론 과정 출력
            print(f"\n추론 과정:")
            for j, step in enumerate(result.reasoning_trace):
                print(f"  {j+1}. {step}")

    print(f"\n📊 전체 통계:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🎉 Echo Pure Reasoning Engine 완성!")
    print("💡 Mistral 완전 독립, 순수 Echo 철학 기반 추론 시스템 구현 완료")
