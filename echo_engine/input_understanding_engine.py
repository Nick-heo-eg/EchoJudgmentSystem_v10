#!/usr/bin/env python3
"""
🧠 Input Understanding Engine
사용자 자연어 입력을 EchoSystem 구조로 변환하는 엔진

핵심 기능:
1. 자연어 입력 → 감정 코드 추론
2. 의도 및 판단 요청 타입 분석
3. 컨텍스트 및 이전 대화 고려
4. judgment_engine에 전달할 구조화된 데이터 생성
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """사용자 의도 타입"""

    EMOTIONAL_SUPPORT = "emotional_support"  # 감정적 지지 요청
    DECISION_HELP = "decision_help"  # 의사결정 도움
    SITUATION_ANALYSIS = "situation_analysis"  # 상황 분석 요청
    CASUAL_CHAT = "casual_chat"  # 일상적 대화
    PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"  # 철학적 탐구
    SELF_REFLECTION = "self_reflection"  # 자기 성찰
    CRISIS_INTERVENTION = "crisis_intervention"  # 위기 개입 필요


@dataclass
class InputUnderstanding:
    """입력 이해 결과"""

    raw_text: str
    cleaned_text: str
    primary_emotion: str
    emotion_intensity: float
    intent_type: IntentType
    key_themes: List[str]
    urgency_level: int  # 1-5, 5가 가장 긴급
    context_references: List[str]
    judgment_request: Optional[str]
    meta_indicators: Dict[str, Any]


class InputUnderstandingEngine:
    """자연어 입력 이해 엔진"""

    def __init__(self):
        self.emotion_patterns = self._load_emotion_patterns()
        self.intent_indicators = self._load_intent_indicators()
        self.crisis_keywords = self._load_crisis_keywords()
        self.context_memory = {}  # 세션별 컨텍스트 저장

    def understand_input(self, text: str, session_id: str = None) -> InputUnderstanding:
        """사용자 입력을 종합적으로 이해"""

        # 1. 텍스트 정제
        cleaned_text = self._clean_text(text)

        # 2. 감정 추론
        primary_emotion, emotion_intensity = self._infer_emotion(cleaned_text)

        # 3. 의도 분류
        intent_type = self._classify_intent(cleaned_text, primary_emotion)

        # 4. 핵심 테마 추출
        key_themes = self._extract_themes(cleaned_text)

        # 5. 긴급도 평가
        urgency_level = self._assess_urgency(cleaned_text, primary_emotion, intent_type)

        # 6. 컨텍스트 참조 추출
        context_references = self._extract_context_references(cleaned_text, session_id)

        # 7. 판단 요청 추출
        judgment_request = self._extract_judgment_request(cleaned_text, intent_type)

        # 8. 메타 지표 수집
        meta_indicators = self._collect_meta_indicators(cleaned_text, primary_emotion)

        return InputUnderstanding(
            raw_text=text,
            cleaned_text=cleaned_text,
            primary_emotion=primary_emotion,
            emotion_intensity=emotion_intensity,
            intent_type=intent_type,
            key_themes=key_themes,
            urgency_level=urgency_level,
            context_references=context_references,
            judgment_request=judgment_request,
            meta_indicators=meta_indicators,
        )

    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        # 과도한 이모티콘, 특수문자 정리
        cleaned = re.sub(r"[ㅋㅎ]{3,}", "ㅋㅋ", text)  # 과도한 웃음 정리
        cleaned = re.sub(r"[.]{3,}", "...", cleaned)  # 과도한 점 정리
        cleaned = re.sub(r"[!]{2,}", "!", cleaned)  # 과도한 느낌표 정리
        cleaned = re.sub(r"[?]{2,}", "?", cleaned)  # 과도한 물음표 정리

        return cleaned.strip()

    def _infer_emotion(self, text: str) -> Tuple[str, float]:
        """감정 추론"""
        text_lower = text.lower()
        emotion_scores = {}

        # 각 감정별 패턴 매칭 및 점수 계산
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if isinstance(pattern, dict):
                    # 가중치가 있는 패턴
                    for keyword, weight in pattern.items():
                        if keyword in text_lower:
                            score += weight
                else:
                    # 단순 키워드
                    if pattern in text_lower:
                        score += 1
            emotion_scores[emotion] = score

        # 가장 높은 점수의 감정 선택
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            max_score = emotion_scores[primary_emotion]
            intensity = min(max_score / 3.0, 1.0)  # 정규화
        else:
            primary_emotion = "neutral"
            intensity = 0.3

        return primary_emotion, intensity

    def _classify_intent(self, text: str, emotion: str) -> IntentType:
        """의도 분류"""
        text_lower = text.lower()

        # 위기 상황 우선 체크
        if any(keyword in text_lower for keyword in self.crisis_keywords):
            return IntentType.CRISIS_INTERVENTION

        # 의도별 지표 검사
        intent_scores = {}
        for intent, indicators in self.intent_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            intent_scores[intent] = score

        # 감정과 의도의 조합 고려
        if emotion in ["anxiety", "fear", "despair"] and "결정" in text_lower:
            return IntentType.DECISION_HELP
        elif emotion in ["sadness", "loneliness"] and any(
            word in text_lower for word in ["도와", "힘들", "지지"]
        ):
            return IntentType.EMOTIONAL_SUPPORT
        elif "?" in text and emotion == "curiosity":
            return IntentType.PHILOSOPHICAL_INQUIRY

        # 최고 점수 의도 반환
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            return IntentType(best_intent)

        return IntentType.CASUAL_CHAT

    def _extract_themes(self, text: str) -> List[str]:
        """핵심 테마 추출"""
        themes = []
        text_lower = text.lower()

        # 주요 테마 패턴
        theme_patterns = {
            "relationship": ["관계", "친구", "가족", "연인", "동료", "사람"],
            "work": ["일", "직장", "업무", "회사", "커리어", "성과"],
            "health": ["건강", "몸", "병", "아픈", "치료", "운동"],
            "money": ["돈", "경제", "투자", "비용", "수입", "지출"],
            "future": ["미래", "계획", "목표", "꿈", "비전", "장래"],
            "identity": ["나", "정체성", "자아", "성격", "가치관", "신념"],
            "growth": ["성장", "발전", "배움", "공부", "개선", "향상"],
            "time": ["시간", "바쁜", "여유", "급한", "늦은", "빠른"],
        }

        for theme, keywords in theme_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)

        return themes

    def _assess_urgency(self, text: str, emotion: str, intent: IntentType) -> int:
        """긴급도 평가 (1-5)"""
        urgency = 1
        text_lower = text.lower()

        # 위기 상황
        if intent == IntentType.CRISIS_INTERVENTION:
            urgency = 5

        # 긴급 키워드
        urgent_keywords = ["급한", "빨리", "지금", "당장", "긴급", "위험", "위기"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            urgency += 2

        # 감정 강도 고려
        high_intensity_emotions = ["panic", "rage", "despair", "terror"]
        if emotion in high_intensity_emotions:
            urgency += 2

        # 반복 표현 (강조의 의미)
        if len(re.findall(r"[!]{1,}", text)) > 2:
            urgency += 1

        return min(urgency, 5)

    def _extract_context_references(self, text: str, session_id: str) -> List[str]:
        """컨텍스트 참조 추출"""
        references = []
        text_lower = text.lower()

        # 시간 참조
        time_refs = ["어제", "오늘", "내일", "지난번", "이전에", "전에", "그때"]
        references.extend([ref for ref in time_refs if ref in text_lower])

        # 관계 참조
        relation_refs = ["그 사람", "그녀", "그", "엄마", "아빠", "친구", "동료"]
        references.extend([ref for ref in relation_refs if ref in text_lower])

        # 세션 기반 컨텍스트 (실제 구현시 메모리에서 조회)
        if session_id and session_id in self.context_memory:
            prev_context = self.context_memory[session_id]
            # 이전 대화의 주제가 언급되는지 확인
            # 구현 예정

        return references

    def _extract_judgment_request(self, text: str, intent: IntentType) -> Optional[str]:
        """판단 요청 추출"""
        text_lower = text.lower()

        # 명시적 판단 요청
        judgment_patterns = [
            "어떻게 생각해",
            "판단해",
            "결정해",
            "추천해",
            "조언해",
            "어떡해",
            "뭘까",
            "맞나",
            "옳은가",
            "좋을까",
        ]

        for pattern in judgment_patterns:
            if pattern in text_lower:
                # 판단 요청의 핵심 부분 추출
                sentences = text.split(".")
                for sentence in sentences:
                    if pattern in sentence.lower():
                        return sentence.strip()

        # 의도 기반 암시적 판단 요청
        if intent in [IntentType.DECISION_HELP, IntentType.SITUATION_ANALYSIS]:
            return text  # 전체 텍스트가 판단 요청

        return None

    def _collect_meta_indicators(self, text: str, emotion: str) -> Dict[str, Any]:
        """메타 지표 수집"""
        indicators = {}

        # 텍스트 특성
        indicators["text_length"] = len(text)
        indicators["sentence_count"] = len([s for s in text.split(".") if s.strip()])
        indicators["question_count"] = text.count("?")
        indicators["exclamation_count"] = text.count("!")

        # 언어적 특성
        indicators["uses_formal_language"] = "습니다" in text or "됩니다" in text
        indicators["uses_casual_language"] = "ㅋㅋ" in text or "ㅎㅎ" in text
        indicators["uses_ellipsis"] = "..." in text

        # 감정적 특성
        indicators["emotional_words_count"] = len(
            [
                word
                for word in text.split()
                if word in ["슬픈", "행복한", "화나는", "무서운", "기쁜"]
            ]
        )

        # 자기 참조
        indicators["self_reference_count"] = text.count("나") + text.count("내")

        # 시간 참조
        indicators["time_reference"] = any(
            word in text for word in ["어제", "오늘", "내일", "지금"]
        )

        return indicators

    def _load_emotion_patterns(self) -> Dict[str, List]:
        """감정 패턴 로드"""
        return {
            "joy": ["기쁜", "행복한", "좋은", "즐거운", "만족", "뿌듯", "ㅋㅋ", "ㅎㅎ"],
            "sadness": ["슬픈", "우울한", "힘든", "괴로운", "아픈", "눈물", "울고"],
            "anger": ["화나는", "짜증나는", "분노", "열받", "빡친", "미친"],
            "fear": ["무서운", "두려운", "걱정", "불안", "공포", "떨린"],
            "anxiety": [{"걱정": 2, "불안": 2, "초조": 1, "조급": 1, "스트레스": 2}],
            "loneliness": ["외로운", "혼자", "쓸쓸", "고독", "소외"],
            "confusion": ["헷갈린", "모르겠", "애매", "복잡", "혼란"],
            "hope": ["희망", "기대", "바라", "소망", "꿈꾸"],
            "despair": ["절망", "포기", "끝", "죽고", "사라지"],
            "neutral": ["그냥", "보통", "평범", "괜찮"],
        }

    def _load_intent_indicators(self) -> Dict[str, List[str]]:
        """의도 지표 로드"""
        return {
            "emotional_support": ["힘들어", "도와줘", "위로", "지지", "함께", "이해"],
            "decision_help": ["결정", "선택", "어떻게", "뭘까", "고민", "판단"],
            "situation_analysis": ["상황", "분석", "파악", "이해", "생각", "의견"],
            "casual_chat": ["안녕", "어떻게", "뭐해", "오늘", "날씨", "음식"],
            "philosophical_inquiry": ["왜", "의미", "본질", "철학", "깊이", "근본"],
            "self_reflection": ["나는", "내가", "자신", "성찰", "돌아보", "반성"],
            "crisis_intervention": ["죽고", "사라지", "끝내", "포기", "절망", "위험"],
        }

    def _load_crisis_keywords(self) -> List[str]:
        """위기 키워드 로드"""
        return [
            "죽고싶",
            "자살",
            "끝내고싶",
            "사라지고싶",
            "포기하고싶",
            "더이상",
            "견딜수없",
            "한계",
            "절망",
            "위험해",
            "해치고싶",
        ]

    def update_context_memory(self, session_id: str, understanding: InputUnderstanding):
        """컨텍스트 메모리 업데이트"""
        if session_id not in self.context_memory:
            self.context_memory[session_id] = []

        self.context_memory[session_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "emotion": understanding.primary_emotion,
                "intent": understanding.intent_type.value,
                "themes": understanding.key_themes,
                "urgency": understanding.urgency_level,
            }
        )

        # 최대 10개까지만 유지 (메모리 관리)
        if len(self.context_memory[session_id]) > 10:
            self.context_memory[session_id] = self.context_memory[session_id][-10:]


if __name__ == "__main__":
    # 테스트
    engine = InputUnderstandingEngine()

    test_inputs = [
        "그냥 다 끝내고 싶어",
        "오늘 정말 좋은 일이 있었는데... 근데 왜 이렇게 허무하지?",
        "일이 너무 많아서 뭐부터 해야할지 모르겠어",
        "안녕하세요! 오늘 날씨가 참 좋네요",
        "인생의 의미가 뭘까요?",
    ]

    for text in test_inputs:
        result = engine.understand_input(text)
        print(f"\n입력: {text}")
        print(f"감정: {result.primary_emotion} ({result.emotion_intensity:.2f})")
        print(f"의도: {result.intent_type.value}")
        print(f"긴급도: {result.urgency_level}")
        print(f"테마: {result.key_themes}")
        print(f"판단요청: {result.judgment_request}")
        print("=" * 50)
