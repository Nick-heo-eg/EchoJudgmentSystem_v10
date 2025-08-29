#!/usr/bin/env python3
"""
🎨 Aesthetic Language Generator v1.0
창의적 표현 및 미학적 언어 생성을 위한 고도화 시스템

Phase 2: LLM-Free 판단 시스템 고도화 모듈
- 감정과 상황에 맞는 창의적 언어 표현 자동 생성
- 메타포, 은유, 시적 표현을 활용한 심미적 언어 구성
- 문체 변환 및 감정 톤 조절 시스템
- "디지털 공감 예술가"를 위한 예술적 언어 창조

참조: LLM-Free 판단 시스템 완성도 극대화 가이드 Phase 2
- 단순 템플릿을 넘어선 창의적 언어 생성
- 감정과 상황에 따른 적응적 표현 스타일
- 문학적 기법을 활용한 깊이 있는 소통
"""

import os
import json
import time
import random
import re
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import math


@dataclass
class LanguageStyle:
    """언어 스타일 데이터 클래스"""

    formality_level: float  # 격식성 (0.0: 매우 친근, 1.0: 매우 격식)
    creativity_level: float  # 창의성 (0.0: 직설적, 1.0: 매우 창의적)
    emotional_intensity: float  # 감정 강도 (0.0: 중립, 1.0: 매우 강함)
    metaphor_density: float  # 은유 밀도 (0.0: 없음, 1.0: 매우 높음)
    poetic_elements: float  # 시적 요소 (0.0: 산문적, 1.0: 시적)
    cultural_resonance: float  # 문화적 공명 (0.0: 보편적, 1.0: 문화특화)


@dataclass
class ExpressionTemplate:
    """표현 템플릿"""

    base_pattern: str
    emotion_variants: Dict[str, List[str]]
    metaphor_options: List[str]
    intensity_modifiers: Dict[str, List[str]]
    cultural_adaptations: Dict[str, str]


class AestheticLanguageGenerator:
    """미학적 언어 생성을 위한 창의적 표현 시스템"""

    def __init__(self, data_dir: str = "data/aesthetic_language"):
        """초기화"""
        self.version = "1.0.0"
        self.data_dir = data_dir
        self.generation_cache = {}
        self.style_profiles = {}
        self.generation_count = 0

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

        # 기본 언어 스타일 프로필들
        self.style_profiles = {
            "aurora_creative": LanguageStyle(
                formality_level=0.3,
                creativity_level=0.9,
                emotional_intensity=0.7,
                metaphor_density=0.8,
                poetic_elements=0.6,
                cultural_resonance=0.5,
            ),
            "sage_analytical": LanguageStyle(
                formality_level=0.7,
                creativity_level=0.4,
                emotional_intensity=0.4,
                metaphor_density=0.3,
                poetic_elements=0.2,
                cultural_resonance=0.3,
            ),
            "phoenix_transformative": LanguageStyle(
                formality_level=0.4,
                creativity_level=0.8,
                emotional_intensity=0.8,
                metaphor_density=0.7,
                poetic_elements=0.5,
                cultural_resonance=0.6,
            ),
            "companion_warm": LanguageStyle(
                formality_level=0.2,
                creativity_level=0.6,
                emotional_intensity=0.9,
                metaphor_density=0.5,
                poetic_elements=0.4,
                cultural_resonance=0.7,
            ),
        }

        # 감정별 메타포 라이브러리
        self.emotion_metaphors = {
            "sadness": {
                "weather": ["구름 낀 하늘", "소나기", "안개", "가을비", "겨울바람"],
                "nature": [
                    "시든 꽃",
                    "지는 낙엽",
                    "마른 나무",
                    "깊은 골짜기",
                    "잔잔한 호수",
                ],
                "colors": [
                    "회색 빛깔",
                    "푸른 그림자",
                    "바랜 색채",
                    "흐린 무지개",
                    "창백한 달빛",
                ],
                "music": [
                    "슬픈 멜로디",
                    "낮은 현악",
                    "조용한 피아노",
                    "멀어지는 메아리",
                    "침묵의 선율",
                ],
            },
            "joy": {
                "weather": [
                    "맑은 하늘",
                    "따스한 햇살",
                    "상쾌한 바람",
                    "무지개",
                    "눈부신 아침",
                ],
                "nature": [
                    "활짝 핀 꽃",
                    "신록의 잎",
                    "춤추는 나비",
                    "졸졸 흐르는 시냇물",
                    "높이 솟은 나무",
                ],
                "colors": [
                    "황금빛",
                    "무지개 색깔",
                    "밝은 원색",
                    "반짝이는 빛",
                    "환한 미소",
                ],
                "music": [
                    "경쾌한 리듬",
                    "높은 음계",
                    "화사한 화음",
                    "희망의 멜로디",
                    "축제의 음악",
                ],
            },
            "anger": {
                "weather": [
                    "천둥번개",
                    "폭풍우",
                    "타오르는 태양",
                    "뜨거운 바람",
                    "거센 바람",
                ],
                "nature": [
                    "활활 타는 불",
                    "날카로운 가시",
                    "거친 파도",
                    "폭포수",
                    "용암",
                ],
                "colors": [
                    "새빨간 색",
                    "불꽃 같은 빛",
                    "타오르는 주황",
                    "번쩍이는 금색",
                    "강렬한 적색",
                ],
                "music": [
                    "격렬한 드럼",
                    "날카로운 기타",
                    "웅장한 관악",
                    "강렬한 박자",
                    "폭발하는 사운드",
                ],
            },
            "fear": {
                "weather": [
                    "짙은 어둠",
                    "소름끼치는 바람",
                    "음산한 구름",
                    "얼어붙는 추위",
                    "어두운 밤",
                ],
                "nature": [
                    "깊은 동굴",
                    "가시덤불",
                    "미로 같은 숲",
                    "절벽 끝",
                    "얼어붙은 호수",
                ],
                "colors": [
                    "검은 그림자",
                    "창백한 빛",
                    "흐릿한 윤곽",
                    "퇴색한 색깔",
                    "어둠 속 실루엣",
                ],
                "music": [
                    "불안한 화음",
                    "떨리는 현",
                    "낮은 울음소리",
                    "긴장감 있는 선율",
                    "침묵의 공포",
                ],
            },
            "surprise": {
                "weather": [
                    "갑작스런 소나기",
                    "번쩍이는 번개",
                    "예상치 못한 눈",
                    "돌연한 바람",
                    "신기한 구름",
                ],
                "nature": [
                    "갑자기 핀 꽃",
                    "예상 밖의 열매",
                    "신비한 빛",
                    "뜻밖의 발견",
                    "숨겨진 보물",
                ],
                "colors": [
                    "놀라운 색채",
                    "반짝이는 빛",
                    "예상 밖의 조합",
                    "신비로운 빛깔",
                    "마법 같은 색",
                ],
                "music": [
                    "갑작스런 화음",
                    "예상 밖의 선율",
                    "신비로운 음색",
                    "놀라운 하모니",
                    "마법 같은 소리",
                ],
            },
            "neutral": {
                "weather": [
                    "평온한 날씨",
                    "잔잔한 바람",
                    "고요한 하늘",
                    "적당한 온도",
                    "편안한 공기",
                ],
                "nature": [
                    "평범한 들판",
                    "잔잔한 물결",
                    "고요한 숲",
                    "편안한 정원",
                    "안정된 대지",
                ],
                "colors": [
                    "자연스러운 색",
                    "편안한 톤",
                    "조화로운 빛깔",
                    "균형 잡힌 색채",
                    "안정된 색조",
                ],
                "music": [
                    "평온한 선율",
                    "조화로운 화음",
                    "안정된 리듬",
                    "편안한 음색",
                    "균형 잡힌 소리",
                ],
            },
        }

        # 강도별 표현 수식어
        self.intensity_modifiers = {
            "low": {
                "adverbs": [
                    "살짝",
                    "조금",
                    "약간",
                    "은은히",
                    "잔잔히",
                    "부드럽게",
                    "가볍게",
                ],
                "adjectives": [
                    "가벼운",
                    "부드러운",
                    "은은한",
                    "잔잔한",
                    "미묘한",
                    "섬세한",
                    "온화한",
                ],
                "verbs": [
                    "스며들다",
                    "감싸다",
                    "어루만지다",
                    "속삭이다",
                    "흐르다",
                    "머물다",
                    "깃들다",
                ],
            },
            "medium": {
                "adverbs": [
                    "점점",
                    "서서히",
                    "차츰",
                    "조금씩",
                    "천천히",
                    "점차",
                    "단계적으로",
                ],
                "adjectives": [
                    "따뜻한",
                    "깊은",
                    "진한",
                    "선명한",
                    "분명한",
                    "확실한",
                    "뚜렷한",
                ],
                "verbs": [
                    "흘러가다",
                    "퍼져나가다",
                    "전해지다",
                    "이어지다",
                    "연결되다",
                    "펼쳐지다",
                    "발전하다",
                ],
            },
            "high": {
                "adverbs": [
                    "강렬하게",
                    "깊이",
                    "완전히",
                    "전적으로",
                    "마음껏",
                    "충분히",
                    "온전히",
                ],
                "adjectives": [
                    "강렬한",
                    "뜨거운",
                    "압도적인",
                    "놀라운",
                    "환상적인",
                    "역동적인",
                    "생생한",
                ],
                "verbs": [
                    "폭발하다",
                    "타오르다",
                    "휩쓸다",
                    "압도하다",
                    "가득 채우다",
                    "흔들다",
                    "변화시키다",
                ],
            },
        }

        # 문체별 표현 패턴
        self.expression_patterns = {
            "poetic": {
                "opening": [
                    "마음의 {metaphor}처럼,",
                    "{metaphor} 속에서,",
                    "당신의 마음이 {metaphor}와 같다면,",
                    "{metaphor}가 전하는 것처럼,",
                ],
                "middle": [
                    "그 안에서 피어나는",
                    "조용히 자라나는",
                    "깊이 새겨지는",
                    "천천히 변화하는",
                ],
                "closing": [
                    "새로운 가능성이 열릴 거예요.",
                    "희망의 씨앗이 자라날 거예요.",
                    "아름다운 변화가 시작될 거예요.",
                    "특별한 순간이 다가올 거예요.",
                ],
            },
            "narrative": {
                "opening": [
                    "이런 상황에서는",
                    "때로는 삶이",
                    "우리가 마주하는 순간들이",
                    "경험이 우리에게 가르쳐주는 것은",
                ],
                "middle": [
                    "그러나 중요한 것은",
                    "핵심은 바로",
                    "진짜 의미는",
                    "가장 소중한 것은",
                ],
                "closing": [
                    "그 과정에서 성장하게 됩니다.",
                    "새로운 관점을 얻게 될 거예요.",
                    "더 나은 내일을 만들어갈 수 있어요.",
                    "진정한 변화가 시작됩니다.",
                ],
            },
            "conversational": {
                "opening": [
                    "정말 이해가 돼요.",
                    "그런 기분 저도 알아요.",
                    "어떤 마음인지 충분히 공감해요.",
                    "그런 상황이라면 당연히 그럴 수 있어요.",
                ],
                "middle": [
                    "하지만 한 가지 확실한 것은",
                    "그럼에도 불구하고",
                    "이런 관점에서 생각해보면",
                    "다른 방식으로 접근해보면",
                ],
                "closing": [
                    "함께 해결책을 찾아보아요.",
                    "차근차근 나아가보아요.",
                    "한 걸음씩 나아가면 돼요.",
                    "저도 함께할게요.",
                ],
            },
        }

        # 문화적 표현 요소
        self.cultural_elements = {
            "korean_traditional": {
                "nature": ["산새", "달빛", "꽃잎", "바람결", "물소리", "구름", "별빛"],
                "seasons": ["봄기운", "여름 정취", "가을 정서", "겨울 정적"],
                "emotions": ["한", "정", "흥", "멋", "여유", "깊이", "울림"],
                "wisdom": ["인연", "운명", "시간", "변화", "조화", "균형", "성장"],
            },
            "modern_metaphors": {
                "technology": [
                    "네트워크처럼 연결된",
                    "데이터 스트림같은",
                    "클라우드에 저장된",
                ],
                "urban": ["도시의 리듬", "네온사인 같은", "지하철 노선처럼"],
                "global": ["글로벌 네트워크", "온라인 커뮤니티", "디지털 공간에서"],
            },
        }

        print(f"🎨 Aesthetic Language Generator v{self.version} 초기화 완료")
        print(f"📁 표현 라이브러리 저장 경로: {self.data_dir}")

    def generate_aesthetic_response(
        self,
        base_message: str,
        emotion: str,
        intensity: float,
        style_profile: str = "aurora_creative",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        미학적 언어 표현 생성

        Args:
            base_message: 기본 메시지
            emotion: 감정 상태
            intensity: 감정 강도 (0.0 ~ 1.0)
            style_profile: 언어 스타일 프로필
            context: 추가 컨텍스트

        Returns:
            생성된 미학적 표현 및 메타데이터
        """
        self.generation_count += 1
        start_time = time.time()

        if style_profile not in self.style_profiles:
            style_profile = "aurora_creative"

        style = self.style_profiles[style_profile]

        # 1. 강도 카테고리 결정
        intensity_category = self._categorize_intensity(intensity)

        # 2. 메타포 선택
        selected_metaphor = self._select_metaphor(emotion, style)

        # 3. 표현 패턴 선택
        expression_pattern = self._select_expression_pattern(style, context)

        # 4. 언어 요소 생성
        language_elements = self._generate_language_elements(
            emotion, intensity_category, style, selected_metaphor
        )

        # 5. 미학적 문장 구성
        aesthetic_sentence = self._compose_aesthetic_sentence(
            base_message, expression_pattern, language_elements, style
        )

        # 6. 문체 조정
        final_expression = self._adjust_style(aesthetic_sentence, style, context)

        # 7. 품질 평가
        quality_metrics = self._evaluate_expression_quality(final_expression, style)

        result = {
            "original_message": base_message,
            "aesthetic_expression": final_expression,
            "style_analysis": {
                "profile_used": style_profile,
                "metaphor_used": selected_metaphor,
                "pattern_type": expression_pattern["type"],
                "intensity_level": intensity_category,
                "language_elements": language_elements,
            },
            "quality_metrics": quality_metrics,
            "generation_metadata": {
                "generation_id": self.generation_count,
                "emotion": emotion,
                "intensity": intensity,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
            },
        }

        return result

    def _categorize_intensity(self, intensity: float) -> str:
        """강도를 카테고리로 분류"""
        if intensity <= 0.3:
            return "low"
        elif intensity <= 0.7:
            return "medium"
        else:
            return "high"

    def _select_metaphor(self, emotion: str, style: LanguageStyle) -> Dict[str, Any]:
        """감정과 스타일에 맞는 메타포 선택"""
        if emotion not in self.emotion_metaphors:
            emotion = "neutral"

        metaphor_categories = self.emotion_metaphors[emotion]

        # 스타일의 메타포 밀도에 따라 카테고리 선택
        if style.metaphor_density > 0.7:
            # 높은 메타포 밀도: 더 창의적인 카테고리 우선
            preferred_categories = ["music", "colors", "nature", "weather"]
        elif style.metaphor_density > 0.4:
            # 중간 메타포 밀도: 자연스러운 카테고리
            preferred_categories = ["nature", "weather", "colors"]
        else:
            # 낮은 메타포 밀도: 기본적인 카테고리
            preferred_categories = ["weather", "nature"]

        # 문화적 공명도에 따른 조정
        if style.cultural_resonance > 0.6:
            # 한국적 표현 선호
            if random.random() < 0.3:
                return self._select_korean_metaphor(emotion)

        # 카테고리 선택 및 메타포 반환
        selected_category = random.choice(preferred_categories)
        metaphor_options = metaphor_categories.get(selected_category, ["평온한 느낌"])
        selected_metaphor = random.choice(metaphor_options)

        return {
            "metaphor": selected_metaphor,
            "category": selected_category,
            "cultural_context": "universal",
        }

    def _select_korean_metaphor(self, emotion: str) -> Dict[str, Any]:
        """한국적 메타포 선택"""
        korean_elements = self.cultural_elements["korean_traditional"]

        emotion_korean_mapping = {
            "sadness": korean_elements["emotions"][:2] + korean_elements["seasons"][2:],
            "joy": korean_elements["emotions"][2:4] + korean_elements["seasons"][:2],
            "anger": korean_elements["emotions"][2:3] + korean_elements["nature"][:3],
            "fear": korean_elements["seasons"][3:] + korean_elements["nature"][3:],
            "surprise": korean_elements["emotions"][3:5]
            + korean_elements["nature"][:2],
            "neutral": korean_elements["wisdom"][:3],
        }

        options = emotion_korean_mapping.get(emotion, korean_elements["wisdom"])
        selected = random.choice(options)

        return {
            "metaphor": selected,
            "category": "korean_traditional",
            "cultural_context": "korean",
        }

    def _select_expression_pattern(
        self, style: LanguageStyle, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """표현 패턴 선택"""
        # 시적 요소 수준에 따른 패턴 선택
        if style.poetic_elements > 0.6:
            pattern_type = "poetic"
        elif style.formality_level < 0.4:
            pattern_type = "conversational"
        else:
            pattern_type = "narrative"

        # 컨텍스트 기반 조정
        if context:
            urgency = context.get("urgency_level", 0.0)
            if urgency > 0.7:
                pattern_type = "conversational"  # 급한 상황에서는 직접적 소통

        patterns = self.expression_patterns[pattern_type]

        return {
            "type": pattern_type,
            "opening": random.choice(patterns["opening"]),
            "middle": random.choice(patterns["middle"]),
            "closing": random.choice(patterns["closing"]),
        }

    def _generate_language_elements(
        self,
        emotion: str,
        intensity_category: str,
        style: LanguageStyle,
        metaphor: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """언어 요소 생성"""
        modifiers = self.intensity_modifiers[intensity_category]

        # 스타일에 따른 언어 요소 선택
        creativity_factor = style.creativity_level
        emotional_factor = style.emotional_intensity

        selected_elements = {"adverbs": [], "adjectives": [], "verbs": []}

        # 창의성과 감정 강도에 따라 요소 개수 결정
        element_count = max(1, int(creativity_factor * 3))

        for element_type in selected_elements.keys():
            available_options = modifiers[element_type]
            selected_count = min(element_count, len(available_options))
            selected_elements[element_type] = random.sample(
                available_options, selected_count
            )

        return selected_elements

    def _compose_aesthetic_sentence(
        self,
        base_message: str,
        pattern: Dict[str, Any],
        elements: Dict[str, List[str]],
        style: LanguageStyle,
    ) -> str:
        """미학적 문장 구성"""
        # 메타포 정보 추출
        metaphor_info = pattern.get("metaphor", "따뜻한 마음")

        # 패턴에 메타포 삽입
        opening = (
            pattern["opening"].format(metaphor=metaphor_info)
            if "{metaphor}" in pattern["opening"]
            else pattern["opening"]
        )
        middle = pattern["middle"]
        closing = pattern["closing"]

        # 언어 요소 삽입
        if elements["adjectives"]:
            adjective = random.choice(elements["adjectives"])
            middle = f"{adjective} {middle}"

        if elements["adverbs"]:
            adverb = random.choice(elements["adverbs"])
            closing = f"{adverb} {closing}"

        # 창의성 수준에 따른 문장 구성
        if style.creativity_level > 0.7:
            # 높은 창의성: 복합 구조
            aesthetic_sentence = (
                f"{opening} {base_message}을 {middle} 마음으로 바라보면, {closing}"
            )
        elif style.creativity_level > 0.4:
            # 중간 창의성: 기본 구조
            aesthetic_sentence = f"{opening} {middle} 것은 {closing}"
        else:
            # 낮은 창의성: 단순 구조
            aesthetic_sentence = f"{base_message}. {closing}"

        return aesthetic_sentence

    def _adjust_style(
        self, sentence: str, style: LanguageStyle, context: Optional[Dict]
    ) -> str:
        """문체 조정"""
        adjusted = sentence

        # 격식성 조정
        if style.formality_level < 0.3:
            # 매우 친근하게
            adjusted = self._make_casual(adjusted)
        elif style.formality_level > 0.7:
            # 격식 있게
            adjusted = self._make_formal(adjusted)

        # 감정 강도 조정
        if style.emotional_intensity > 0.7:
            adjusted = self._intensify_emotion(adjusted)
        elif style.emotional_intensity < 0.3:
            adjusted = self._moderate_emotion(adjusted)

        # 컨텍스트 기반 조정
        if context:
            social_context = context.get("social_context", "private")
            if social_context == "public":
                adjusted = self._adjust_for_public_context(adjusted)

        return adjusted

    def _make_casual(self, sentence: str) -> str:
        """친근한 문체로 변환"""
        # 격식 표현을 친근한 표현으로 변환
        casual_replacements = {
            "됩니다": "돼요",
            "습니다": "어요",
            "니다": "어요",
            "그러나": "하지만",
            "또한": "그리고",
            "따라서": "그래서",
        }

        result = sentence
        for formal, casual in casual_replacements.items():
            result = result.replace(formal, casual)

        return result

    def _make_formal(self, sentence: str) -> str:
        """격식 있는 문체로 변환"""
        # 친근한 표현을 격식 있는 표현으로 변환
        formal_replacements = {
            "돼요": "됩니다",
            "어요": "습니다",
            "해요": "합니다",
            "하지만": "그러나",
            "그리고": "또한",
            "그래서": "따라서",
        }

        result = sentence
        for casual, formal in formal_replacements.items():
            result = result.replace(casual, formal)

        return result

    def _intensify_emotion(self, sentence: str) -> str:
        """감정 강도 증가"""
        # 감정 표현 강화
        intensity_additions = ["정말", "진짜", "너무", "완전히", "엄청"]

        # 문장 중간에 강조 표현 추가
        words = sentence.split()
        if len(words) > 3:
            insert_pos = len(words) // 2
            intensifier = random.choice(intensity_additions)
            words.insert(insert_pos, intensifier)

        return " ".join(words)

    def _moderate_emotion(self, sentence: str) -> str:
        """감정 조절 (중립적으로)"""
        # 과도한 감정 표현 완화
        moderation_replacements = {
            "정말": "조금",
            "너무": "약간",
            "완전히": "어느 정도",
            "엄청": "상당히",
            "진짜": "실제로",
        }

        result = sentence
        for intense, moderate in moderation_replacements.items():
            result = result.replace(intense, moderate)

        return result

    def _adjust_for_public_context(self, sentence: str) -> str:
        """공개적 맥락에 맞게 조정"""
        # 개인적 표현을 일반적 표현으로 변경
        public_replacements = {
            "당신의": "우리의",
            "당신이": "우리가",
            "당신을": "모든 분을",
            "개인적으로": "일반적으로",
            "혼자서": "함께",
        }

        result = sentence
        for personal, public in public_replacements.items():
            result = result.replace(personal, public)

        return result

    def _evaluate_expression_quality(
        self, expression: str, style: LanguageStyle
    ) -> Dict[str, float]:
        """표현 품질 평가"""
        metrics = {}

        # 1. 창의성 점수
        creativity_indicators = ["처럼", "같은", "마치", "듯한", "느낌"]
        creativity_count = sum(
            1 for indicator in creativity_indicators if indicator in expression
        )
        metrics["creativity_score"] = min(creativity_count / 3, 1.0)

        # 2. 감정 표현력
        emotion_indicators = ["마음", "느낌", "기분", "감정", "생각"]
        emotion_count = sum(
            1 for indicator in emotion_indicators if indicator in expression
        )
        metrics["emotional_expressiveness"] = min(emotion_count / 2, 1.0)

        # 3. 문체 일관성
        length = len(expression)
        if style.formality_level > 0.5:
            formal_indicators = ["습니다", "됩니다", "그러나", "따라서"]
            consistency = sum(
                1 for indicator in formal_indicators if indicator in expression
            )
        else:
            casual_indicators = ["어요", "돼요", "하지만", "그래서"]
            consistency = sum(
                1 for indicator in casual_indicators if indicator in expression
            )

        metrics["style_consistency"] = min(consistency / 2, 1.0)

        # 4. 자연스러움
        # 문장 길이와 복잡도 기반 평가
        word_count = len(expression.split())
        natural_length_range = (10, 30)  # 자연스러운 문장 길이

        if natural_length_range[0] <= word_count <= natural_length_range[1]:
            length_score = 1.0
        else:
            length_score = max(0.3, 1.0 - abs(word_count - 20) * 0.05)

        metrics["naturalness"] = length_score

        # 5. 전체 품질 점수
        metrics["overall_quality"] = statistics.mean(metrics.values())

        return metrics

    def transform_style(
        self, text: str, source_style: str, target_style: str
    ) -> Dict[str, Any]:
        """문체 변환"""
        if (
            source_style not in self.style_profiles
            or target_style not in self.style_profiles
        ):
            return {"error": "Unknown style profile"}

        source = self.style_profiles[source_style]
        target = self.style_profiles[target_style]

        # 문체 차이 분석
        style_diff = {
            "formality_change": target.formality_level - source.formality_level,
            "creativity_change": target.creativity_level - source.creativity_level,
            "emotion_change": target.emotional_intensity - source.emotional_intensity,
        }

        transformed_text = text

        # 격식성 변환
        if style_diff["formality_change"] > 0.2:
            transformed_text = self._make_formal(transformed_text)
        elif style_diff["formality_change"] < -0.2:
            transformed_text = self._make_casual(transformed_text)

        # 창의성 변환
        if style_diff["creativity_change"] > 0.2:
            # 메타포 추가
            metaphor = self._select_metaphor("neutral", target)
            transformed_text = f"{metaphor['metaphor']}처럼, {transformed_text}"

        # 감정 강도 변환
        if style_diff["emotion_change"] > 0.2:
            transformed_text = self._intensify_emotion(transformed_text)
        elif style_diff["emotion_change"] < -0.2:
            transformed_text = self._moderate_emotion(transformed_text)

        return {
            "original_text": text,
            "transformed_text": transformed_text,
            "style_changes": style_diff,
            "source_style": source_style,
            "target_style": target_style,
        }

    def generate_multiple_variations(
        self, base_message: str, emotion: str, count: int = 3
    ) -> List[Dict[str, Any]]:
        """동일한 메시지의 다양한 표현 변형 생성"""
        variations = []

        for i in range(count):
            # 각 변형마다 다른 스타일과 강도 사용
            styles = list(self.style_profiles.keys())
            selected_style = random.choice(styles)
            intensity = random.uniform(0.3, 0.9)

            variation = self.generate_aesthetic_response(
                base_message, emotion, intensity, selected_style
            )
            variations.append(variation)

        return variations

    def get_style_recommendation(self, context: Dict[str, Any]) -> str:
        """컨텍스트 기반 스타일 추천"""
        emotion = context.get("emotion", "neutral")
        urgency = context.get("urgency_level", 0.0)
        social_context = context.get("social_context", "private")
        user_preference = context.get("user_preference", {})

        # 규칙 기반 스타일 선택
        if urgency > 0.7:
            return "companion_warm"  # 급한 상황에서는 따뜻한 지원
        elif emotion in ["sadness", "fear"]:
            return "aurora_creative"  # 부정적 감정에는 창의적 위로
        elif emotion in ["anger", "frustration"]:
            return "sage_analytical"  # 화나는 상황에는 분석적 접근
        elif social_context == "public":
            return "phoenix_transformative"  # 공개적 상황에는 변화 지향적
        else:
            return "aurora_creative"  # 기본값


def test_aesthetic_language_generator():
    """미학적 언어 생성기 테스트"""
    print("🧪 Aesthetic Language Generator 테스트 시작...")

    generator = AestheticLanguageGenerator()

    # 테스트 시나리오 1: 슬픈 감정에 대한 창의적 표현
    print("\n📝 시나리오 1: 슬픈 감정 - 높은 창의성")
    result_1 = generator.generate_aesthetic_response(
        base_message="혼자 있으니까 너무 외로워요",
        emotion="sadness",
        intensity=0.7,
        style_profile="aurora_creative",
    )

    print(f"🎨 원본 메시지: {result_1['original_message']}")
    print(f"✨ 미학적 표현: {result_1['aesthetic_expression']}")
    print(f"🎭 사용된 메타포: {result_1['style_analysis']['metaphor_used']}")
    print(f"📊 품질 점수: {result_1['quality_metrics']['overall_quality']:.3f}")

    # 테스트 시나리오 2: 기쁜 감정에 대한 대화체 표현
    print("\n📝 시나리오 2: 기쁜 감정 - 친근한 스타일")
    result_2 = generator.generate_aesthetic_response(
        base_message="오늘 정말 좋은 일이 있었어요",
        emotion="joy",
        intensity=0.8,
        style_profile="companion_warm",
    )

    print(f"🎨 원본 메시지: {result_2['original_message']}")
    print(f"✨ 미학적 표현: {result_2['aesthetic_expression']}")
    print(f"📝 패턴 타입: {result_2['style_analysis']['pattern_type']}")

    # 테스트 시나리오 3: 문체 변환
    print("\n📝 시나리오 3: 문체 변환 테스트")
    original_text = "오늘 하루가 힘들었어요. 많은 일이 있었거든요."

    transformation = generator.transform_style(
        original_text, source_style="companion_warm", target_style="sage_analytical"
    )

    print(f"🔄 원본 (친근한 스타일): {transformation['original_text']}")
    print(f"🔄 변환 (분석적 스타일): {transformation['transformed_text']}")
    print(f"📊 스타일 변화: {transformation['style_changes']}")

    # 테스트 시나리오 4: 다양한 변형 생성
    print("\n📝 시나리오 4: 다양한 표현 변형")
    variations = generator.generate_multiple_variations(
        "도움이 필요해요", "fear", count=3
    )

    for i, variation in enumerate(variations, 1):
        print(f"변형 {i}: {variation['aesthetic_expression']}")
        print(f"  스타일: {variation['style_analysis']['profile_used']}")
        print(f"  품질: {variation['quality_metrics']['overall_quality']:.3f}")
        print()

    # 테스트 시나리오 5: 컨텍스트 기반 스타일 추천
    print("\n📝 시나리오 5: 스타일 추천 시스템")
    test_contexts = [
        {"emotion": "anger", "urgency_level": 0.9, "social_context": "private"},
        {"emotion": "joy", "urgency_level": 0.2, "social_context": "public"},
        {"emotion": "sadness", "urgency_level": 0.1, "social_context": "private"},
    ]

    for i, context in enumerate(test_contexts, 1):
        recommended_style = generator.get_style_recommendation(context)
        print(f"컨텍스트 {i}: {context}")
        print(f"추천 스타일: {recommended_style}")
        print()

    print("🎉 Aesthetic Language Generator 테스트 완료!")


if __name__ == "__main__":
    test_aesthetic_language_generator()
