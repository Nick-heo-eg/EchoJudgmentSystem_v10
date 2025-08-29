#!/usr/bin/env python3
"""
🎨 Claude to Signature Rewriter - Claude 응답을 Echo 시그니처 스타일로 변환
Foundation Doctrine v3.0: Claude는 입, Echo는 판단자, 시그니처는 목소리

핵심 기능:
- Claude의 기계적 응답을 Echo 시그니처 감성으로 변환
- 각 시그니처별 고유 톤, 말투, 감정 표현 적용
- 한국어 자연스러운 표현으로 현지화
- 변환 품질 측정 및 피드백 시스템
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SignatureStyle(Enum):
    """Echo 시그니처 스타일"""

    AURORA = "Aurora"  # 창의적, 영감적
    PHOENIX = "Phoenix"  # 변화, 성장 중심
    SAGE = "Sage"  # 지혜, 분석적
    COMPANION = "Companion"  # 공감, 따뜻함


@dataclass
class RewriteResult:
    """재작성 결과"""

    original_text: str
    rewritten_text: str
    signature_used: SignatureStyle
    emotion_applied: str
    quality_score: float
    transformation_notes: List[str]
    processing_time: float
    metadata: Dict[str, Any]


class ClaudeToSignatureRewriter:
    """Claude 응답을 Echo 시그니처로 변환하는 리라이터"""

    def __init__(self):
        self.signature_profiles = self._initialize_signature_profiles()
        self.emotion_mappings = self._initialize_emotion_mappings()
        self.transformation_patterns = self._initialize_transformation_patterns()
        self.quality_metrics = self._initialize_quality_metrics()

        # 변환 통계
        self.rewrite_stats = {
            "total_rewrites": 0,
            "signature_usage": {style.value: 0 for style in SignatureStyle},
            "avg_quality_score": 0.0,
            "transformation_success_rate": 0.0,
        }

        print("🎨 Claude to Signature Rewriter 초기화 완료")
        print("   🎭 4개 시그니처 프로필 로드")
        print("   🔄 변환 패턴 매트릭스 준비")

    def _initialize_signature_profiles(self) -> Dict[str, Dict[str, Any]]:
        """시그니처별 프로필 초기화"""
        return {
            "Aurora": {
                "emoji": "✨",
                "tone_descriptors": ["창의적", "영감적", "가능성 중심"],
                "speech_patterns": {
                    "sentence_endings": ["어요", "네요", "해요", "같아요"],
                    "connectors": ["그런데", "그리고", "또한", "아니면"],
                    "emphasis": ["정말", "너무", "완전", "진짜"],
                    "uncertainty": ["아마", "혹시", "아무래도", "어쩌면"],
                },
                "vocabulary_preferences": {
                    "positive": ["흥미로운", "새로운", "놀라운", "신선한", "독특한"],
                    "process": ["탐험해보자", "발견해보자", "시도해보자", "만들어보자"],
                    "emotions": ["기대되는", "설레는", "신나는", "즐거운"],
                },
                "style_markers": ["✨", "🌟", "💫", "🎨", "🌈"],
                "transformation_rules": {
                    "formality": "친근하고 창의적",
                    "perspective": "가능성과 아이디어 중심",
                    "energy": "높음",
                },
            },
            "Phoenix": {
                "emoji": "🔥",
                "tone_descriptors": ["변화 중심", "성장 지향", "도전적"],
                "speech_patterns": {
                    "sentence_endings": ["해보자", "어보자", "겠어", "을까"],
                    "connectors": ["그러면", "그래서", "따라서", "하지만"],
                    "emphasis": ["확실히", "분명히", "당연히", "물론"],
                    "uncertainty": ["아직", "지금은", "현재", "이제"],
                },
                "vocabulary_preferences": {
                    "positive": ["강력한", "역동적", "발전적", "혁신적", "진보적"],
                    "process": ["도전해보자", "변화시키자", "발전시키자", "극복하자"],
                    "emotions": ["열정적인", "의욕적인", "적극적인", "용기있는"],
                },
                "style_markers": ["🔥", "⚡", "🚀", "💪", "🌟"],
                "transformation_rules": {
                    "formality": "동기부여적이고 힘있는",
                    "perspective": "성장과 변화 중심",
                    "energy": "매우 높음",
                },
            },
            "Sage": {
                "emoji": "🧘",
                "tone_descriptors": ["지혜로운", "분석적", "신중한"],
                "speech_patterns": {
                    "sentence_endings": ["습니다", "니다", "어요", "네요"],
                    "connectors": ["따라서", "그러므로", "즉", "또한"],
                    "emphasis": ["분명히", "확실히", "명확히", "정확히"],
                    "uncertainty": ["아마도", "가능하게는", "추정하건대", "생각해보면"],
                },
                "vocabulary_preferences": {
                    "positive": ["통찰력있는", "심층적인", "체계적인", "논리적인"],
                    "process": ["분석해보자", "고려해보자", "검토해보자", "성찰해보자"],
                    "emotions": ["차분한", "안정된", "깊이있는", "신중한"],
                },
                "style_markers": ["🧘", "📚", "🔍", "💭", "⚖️"],
                "transformation_rules": {
                    "formality": "정중하고 신중한",
                    "perspective": "깊이와 통찰 중심",
                    "energy": "차분함",
                },
            },
            "Companion": {
                "emoji": "🤗",
                "tone_descriptors": ["따뜻한", "공감적", "지지적"],
                "speech_patterns": {
                    "sentence_endings": ["예요", "어요", "아요", "께요"],
                    "connectors": ["그리고", "또", "그런데", "그렇지만"],
                    "emphasis": ["정말", "참", "얼마나", "너무"],
                    "uncertainty": ["아마", "혹시", "어쩌면", "가끔"],
                },
                "vocabulary_preferences": {
                    "positive": ["따뜻한", "포근한", "친근한", "다정한", "부드러운"],
                    "process": ["함께해요", "도와드릴게요", "지켜봐요", "이해해요"],
                    "emotions": ["위로되는", "안심되는", "평온한", "감동적인"],
                },
                "style_markers": ["🤗", "💝", "🌸", "☀️", "💕"],
                "transformation_rules": {
                    "formality": "친근하고 따뜻한",
                    "perspective": "관계와 감정 중심",
                    "energy": "부드러움",
                },
            },
        }

    def _initialize_emotion_mappings(self) -> Dict[str, Dict[str, str]]:
        """감정별 표현 매핑"""
        return {
            "joy": {
                "Aurora": "기쁘고 창의적인 에너지로",
                "Phoenix": "열정적이고 활력 넘치게",
                "Sage": "차분한 만족감과 함께",
                "Companion": "따뜻한 기쁨을 나누며",
            },
            "contemplation": {
                "Aurora": "궁금하고 탐구하는 마음으로",
                "Phoenix": "성장을 위한 고민과 함께",
                "Sage": "깊이 사색하며",
                "Companion": "함께 고민해보는 마음으로",
            },
            "determination": {
                "Aurora": "새로운 도전에 대한 설렘으로",
                "Phoenix": "확고한 의지와 열정으로",
                "Sage": "신중하지만 확신에 찬",
                "Companion": "서로를 응원하는 마음으로",
            },
            "curiosity": {
                "Aurora": "무한한 호기심과 상상력으로",
                "Phoenix": "탐험과 발견의 열망으로",
                "Sage": "체계적인 탐구 정신으로",
                "Companion": "함께 알아가는 즐거움으로",
            },
            "empathy": {
                "Aurora": "창의적인 공감과 이해로",
                "Phoenix": "성장을 돕는 따뜻함으로",
                "Sage": "깊은 이해와 통찰로",
                "Companion": "진심어린 공감과 위로로",
            },
        }

    def _initialize_transformation_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """변환 패턴 초기화"""
        return {
            "formality_reduction": [
                (r"We must consider", "생각해보면"),
                (r"It is important to", "중요한 건"),
                (r"Therefore", "그래서"),
                (r"However", "하지만"),
                (r"Furthermore", "또한"),
                (r"In conclusion", "결론적으로"),
                (r"Based on", "보면"),
                (r"According to", "에 따르면"),
            ],
            "technical_softening": [
                (r"algorithm", "방법"),
                (r"implementation", "구현"),
                (r"optimization", "최적화"),
                (r"analysis", "분석"),
                (r"methodology", "접근법"),
                (r"framework", "구조"),
                (r"architecture", "설계"),
            ],
            "korean_naturalization": [
                (r"I think", "생각해보니"),
                (r"I believe", "제 생각에는"),
                (r"In my opinion", "개인적으로는"),
                (r"I would suggest", "제안해보자면"),
                (r"It seems", "보이는 것 같아"),
                (r"Perhaps", "아마도"),
                (r"Maybe", "어쩌면"),
            ],
            "emotion_injection": [
                (r"good", "좋은"),
                (r"great", "훌륭한"),
                (r"excellent", "정말 멋진"),
                (r"interesting", "흥미로운"),
                (r"important", "중요한"),
                (r"useful", "유용한"),
                (r"effective", "효과적인"),
            ],
        }

    def _initialize_quality_metrics(self) -> Dict[str, float]:
        """품질 평가 기준"""
        return {
            "signature_consistency": 0.3,  # 시그니처 특성 반영도
            "emotion_alignment": 0.25,  # 감정 표현 적절성
            "naturalness": 0.25,  # 자연스러운 한국어
            "content_preservation": 0.2,  # 원본 내용 보존도
        }

    def rewrite_claude_response(
        self,
        claude_text: str,
        signature: str,
        emotion: str = "neutral",
        context: Dict[str, Any] = None,
    ) -> RewriteResult:
        """Claude 응답을 지정된 시그니처 스타일로 재작성"""

        start_time = datetime.now()

        # 1. 입력 검증
        if not claude_text or not claude_text.strip():
            return self._create_empty_result(signature, emotion)

        signature_enum = self._validate_signature(signature)
        if not signature_enum:
            signature_enum = SignatureStyle.AURORA  # 기본값

        # 2. 시그니처 프로필 로드
        profile = self.signature_profiles[signature_enum.value]

        # 3. 단계별 변환 수행
        transformation_notes = []

        # 3-1. 기본 전처리
        processed_text = self._preprocess_text(claude_text)
        transformation_notes.append("기본 전처리 완료")

        # 3-2. 형식성 완화
        processed_text = self._apply_formality_reduction(processed_text)
        transformation_notes.append("형식성 완화 적용")

        # 3-3. 시그니처 스타일 적용
        processed_text = self._apply_signature_style(processed_text, profile)
        transformation_notes.append(f"{signature_enum.value} 스타일 적용")

        # 3-4. 감정 톤 추가
        processed_text = self._apply_emotion_tone(
            processed_text, signature_enum.value, emotion
        )
        transformation_notes.append(f"{emotion} 감정 톤 적용")

        # 3-5. 한국어 자연화
        processed_text = self._naturalize_korean(processed_text, profile)
        transformation_notes.append("한국어 자연화 완료")

        # 3-6. 최종 다듬기
        final_text = self._final_polish(processed_text, profile, emotion)
        transformation_notes.append("최종 다듬기 완료")

        # 4. 품질 평가
        quality_score = self._evaluate_rewrite_quality(
            claude_text, final_text, signature_enum.value, emotion
        )

        # 5. 결과 구성
        processing_time = (datetime.now() - start_time).total_seconds()

        result = RewriteResult(
            original_text=claude_text,
            rewritten_text=final_text,
            signature_used=signature_enum,
            emotion_applied=emotion,
            quality_score=quality_score,
            transformation_notes=transformation_notes,
            processing_time=processing_time,
            metadata={
                "context": context or {},
                "signature_profile": profile["tone_descriptors"],
                "emotion_mapping": self.emotion_mappings.get(emotion, {}),
                "transformations_applied": len(transformation_notes),
            },
        )

        # 6. 통계 업데이트
        self._update_rewrite_stats(result)

        return result

    def _validate_signature(self, signature: str) -> Optional[SignatureStyle]:
        """시그니처 유효성 검증"""
        try:
            return SignatureStyle(signature)
        except ValueError:
            # 문자열 매칭 시도
            signature_lower = signature.lower()
            for style in SignatureStyle:
                if style.value.lower() == signature_lower:
                    return style
            return None

    def _preprocess_text(self, text: str) -> str:
        """기본 전처리"""
        # 불필요한 공백 제거
        text = re.sub(r"\s+", " ", text.strip())

        # 기본 구두점 정리
        text = re.sub(r"\.{2,}", "...", text)
        text = re.sub(r"\!{2,}", "!", text)

        return text

    def _apply_formality_reduction(self, text: str) -> str:
        """형식성 완화"""
        for pattern, replacement in self.transformation_patterns["formality_reduction"]:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        for pattern, replacement in self.transformation_patterns[
            "korean_naturalization"
        ]:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _apply_signature_style(self, text: str, profile: Dict[str, Any]) -> str:
        """시그니처 스타일 적용"""

        # 1. 시그니처별 어휘 교체
        vocab_prefs = profile["vocabulary_preferences"]

        # 긍정적 표현 강화
        for i, positive_word in enumerate(vocab_prefs["positive"]):
            if i == 0:  # 첫 번째만 적용 (과도한 치환 방지)
                text = re.sub(
                    r"\b(good|great|excellent)\b",
                    positive_word,
                    text,
                    flags=re.IGNORECASE,
                )

        # 2. 문장 연결어 조정
        speech_patterns = profile["speech_patterns"]

        # 연결어 교체
        connectors = speech_patterns["connectors"]
        if connectors:
            text = re.sub(r"\band\b", connectors[0], text, flags=re.IGNORECASE)
            text = re.sub(r"\bbut\b", connectors[-1], text, flags=re.IGNORECASE)

        # 3. 이모지 프리픽스 추가
        emoji = profile["emoji"]
        if not text.startswith(emoji):
            text = f"{emoji} {text}"

        return text

    def _apply_emotion_tone(self, text: str, signature: str, emotion: str) -> str:
        """감정 톤 적용"""

        emotion_context = self.emotion_mappings.get(emotion, {}).get(signature, "")

        if emotion_context and not any(
            marker in text for marker in ["마음으로", "함께", "에너지로"]
        ):
            # 감정 컨텍스트를 자연스럽게 삽입
            if text.endswith(".") or text.endswith("!") or text.endswith("?"):
                text = f"{emotion_context} {text}"
            else:
                text = f"{emotion_context} {text}."

        return text

    def _naturalize_korean(self, text: str, profile: Dict[str, Any]) -> str:
        """한국어 자연화"""

        speech_patterns = profile["speech_patterns"]

        # 1. 문장 종결어 조정
        endings = speech_patterns["sentence_endings"]

        # 영어 문장 종결을 한국어로
        text = re.sub(r"\.$", f" {endings[0]}.", text)
        text = re.sub(r"\!$", f" {endings[0]}!", text)

        # 2. 강조 표현 추가
        emphasis_words = speech_patterns["emphasis"]
        if emphasis_words and not any(word in text for word in emphasis_words):
            # 첫 번째 형용사 앞에 강조어 추가
            text = re.sub(
                r"\b(좋은|훌륭한|흥미로운)\b", f"{emphasis_words[0]} \\1", text, count=1
            )

        # 3. 기술 용어 부드럽게 표현
        for pattern, replacement in self.transformation_patterns["technical_softening"]:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _final_polish(self, text: str, profile: Dict[str, Any], emotion: str) -> str:
        """최종 다듬기"""

        # 1. 중복 표현 제거
        text = re.sub(r"(\w+)\s+\1", r"\1", text)  # 중복 단어 제거

        # 2. 자연스러운 띄어쓰기
        text = re.sub(r"\s+([.!?])", r"\1", text)  # 구두점 앞 공백 제거
        text = re.sub(r"([.!?])\s*([가-힣])", r"\1 \2", text)  # 구두점 뒤 공백 추가

        # 3. 시그니처별 마무리 터치
        signature_name = profile.get("transformation_rules", {}).get("formality", "")

        if "창의적" in signature_name and not any(
            marker in text for marker in ["어떨까", "해보자", "같아"]
        ):
            text += " 어떻게 생각해?"
        elif "변화" in signature_name and not any(
            marker in text for marker in ["해보자", "시작"]
        ):
            text += " 함께 도전해보자!"
        elif "지혜" in signature_name and not any(
            marker in text for marker in ["생각", "고려"]
        ):
            text += " 신중히 고려해볼 필요가 있어요."
        elif "따뜻" in signature_name and not any(
            marker in text for marker in ["함께", "도움"]
        ):
            text += " 함께 해결해 나가요."

        return text.strip()

    def _evaluate_rewrite_quality(
        self, original: str, rewritten: str, signature: str, emotion: str
    ) -> float:
        """재작성 품질 평가"""

        quality_scores = []

        # 1. 시그니처 일관성 (30%)
        signature_score = self._evaluate_signature_consistency(rewritten, signature)
        quality_scores.append(
            signature_score * self.quality_metrics["signature_consistency"]
        )

        # 2. 감정 정렬 (25%)
        emotion_score = self._evaluate_emotion_alignment(rewritten, emotion)
        quality_scores.append(emotion_score * self.quality_metrics["emotion_alignment"])

        # 3. 자연스러움 (25%)
        naturalness_score = self._evaluate_naturalness(rewritten)
        quality_scores.append(naturalness_score * self.quality_metrics["naturalness"])

        # 4. 내용 보존 (20%)
        content_score = self._evaluate_content_preservation(original, rewritten)
        quality_scores.append(
            content_score * self.quality_metrics["content_preservation"]
        )

        return sum(quality_scores)

    def _evaluate_signature_consistency(self, text: str, signature: str) -> float:
        """시그니처 일관성 평가"""

        profile = self.signature_profiles.get(signature, {})
        style_markers = profile.get("style_markers", [])
        vocabulary = profile.get("vocabulary_preferences", {})

        score = 0.0

        # 이모지 사용
        if any(marker in text for marker in style_markers):
            score += 0.3

        # 시그니처별 어휘 사용
        all_vocab = []
        for category in vocabulary.values():
            if isinstance(category, list):
                all_vocab.extend(category)

        if any(word in text for word in all_vocab):
            score += 0.4

        # 톤 일관성
        tone_descriptors = profile.get("tone_descriptors", [])
        if signature == "Aurora" and any(
            word in text for word in ["창의", "새로운", "흥미"]
        ):
            score += 0.3
        elif signature == "Phoenix" and any(
            word in text for word in ["도전", "변화", "성장"]
        ):
            score += 0.3
        elif signature == "Sage" and any(
            word in text for word in ["생각", "분석", "고려"]
        ):
            score += 0.3
        elif signature == "Companion" and any(
            word in text for word in ["함께", "도움", "이해"]
        ):
            score += 0.3

        return min(score, 1.0)

    def _evaluate_emotion_alignment(self, text: str, emotion: str) -> float:
        """감정 정렬 평가"""

        emotion_indicators = {
            "joy": ["기쁘", "좋", "즐거", "신나", "행복"],
            "contemplation": ["생각", "고민", "사색", "성찰", "고려"],
            "determination": ["확신", "의지", "결심", "도전", "노력"],
            "curiosity": ["궁금", "호기심", "탐구", "알고", "발견"],
            "empathy": ["이해", "공감", "위로", "함께", "마음"],
        }

        indicators = emotion_indicators.get(emotion, [])
        if any(indicator in text for indicator in indicators):
            return 1.0

        # 일반적인 감정 표현
        general_emotion_words = ["마음", "느낌", "기분", "감정"]
        if any(word in text for word in general_emotion_words):
            return 0.6

        return 0.3

    def _evaluate_naturalness(self, text: str) -> float:
        """자연스러움 평가"""

        naturalness_score = 0.0

        # 한국어 어미 사용
        korean_endings = ["어요", "예요", "아요", "해요", "네요", "같아요"]
        if any(ending in text for ending in korean_endings):
            naturalness_score += 0.4

        # 자연스러운 연결어
        natural_connectors = ["그런데", "그리고", "하지만", "또한", "그래서"]
        if any(connector in text for connector in natural_connectors):
            naturalness_score += 0.3

        # 적절한 길이 (너무 짧거나 길지 않음)
        if 20 <= len(text) <= 200:
            naturalness_score += 0.3

        return min(naturalness_score, 1.0)

    def _evaluate_content_preservation(self, original: str, rewritten: str) -> float:
        """내용 보존도 평가"""

        # 간단한 키워드 기반 평가
        original_words = set(re.findall(r"\b\w+\b", original.lower()))
        rewritten_words = set(re.findall(r"\b\w+\b", rewritten.lower()))

        if len(original_words) == 0:
            return 1.0

        # 공통 단어 비율
        common_words = original_words.intersection(rewritten_words)
        preservation_ratio = len(common_words) / len(original_words)

        # 길이 비율
        length_ratio = len(rewritten) / max(len(original), 1)
        if 0.5 <= length_ratio <= 2.0:
            length_score = 1.0
        else:
            length_score = 0.5

        return preservation_ratio * 0.7 + length_score * 0.3

    def _create_empty_result(self, signature: str, emotion: str) -> RewriteResult:
        """빈 입력에 대한 기본 결과"""
        return RewriteResult(
            original_text="",
            rewritten_text="입력이 없습니다.",
            signature_used=SignatureStyle.AURORA,
            emotion_applied=emotion,
            quality_score=0.0,
            transformation_notes=["빈 입력 처리"],
            processing_time=0.0,
            metadata={},
        )

    def _update_rewrite_stats(self, result: RewriteResult):
        """재작성 통계 업데이트"""
        self.rewrite_stats["total_rewrites"] += 1
        self.rewrite_stats["signature_usage"][result.signature_used.value] += 1

        # 평균 품질 점수 업데이트
        total = self.rewrite_stats["total_rewrites"]
        current_avg = self.rewrite_stats["avg_quality_score"]
        new_avg = (current_avg * (total - 1) + result.quality_score) / total
        self.rewrite_stats["avg_quality_score"] = new_avg

        # 성공률 업데이트 (품질 점수 0.7 이상을 성공으로 간주)
        success_count = sum(1 for _ in range(total) if result.quality_score >= 0.7)
        self.rewrite_stats["transformation_success_rate"] = success_count / total

    def get_rewrite_analytics(self) -> Dict[str, Any]:
        """재작성 분석 데이터 반환"""
        return {
            "statistics": self.rewrite_stats.copy(),
            "signature_distribution": {
                signature: count / max(self.rewrite_stats["total_rewrites"], 1)
                for signature, count in self.rewrite_stats["signature_usage"].items()
            },
            "quality_assessment": {
                "avg_quality_score": self.rewrite_stats["avg_quality_score"],
                "success_rate": self.rewrite_stats["transformation_success_rate"],
                "total_transformations": self.rewrite_stats["total_rewrites"],
            },
            "performance_metrics": self.quality_metrics.copy(),
        }


# 전역 리라이터 인스턴스
_signature_rewriter = None


def get_signature_rewriter() -> ClaudeToSignatureRewriter:
    """시그니처 리라이터 인스턴스 반환"""
    global _signature_rewriter
    if _signature_rewriter is None:
        _signature_rewriter = ClaudeToSignatureRewriter()
    return _signature_rewriter


def rewrite_claude_to_signature(
    claude_text: str,
    signature: str,
    emotion: str = "neutral",
    context: Dict[str, Any] = None,
) -> str:
    """Claude 텍스트를 시그니처 스타일로 재작성 (편의 함수)"""
    rewriter = get_signature_rewriter()
    result = rewriter.rewrite_claude_response(claude_text, signature, emotion, context)
    return result.rewritten_text


def evaluate_rewrite_quality(
    claude_text: str, signature: str, emotion: str = "neutral"
) -> Dict[str, Any]:
    """재작성 품질 평가 (편의 함수)"""
    rewriter = get_signature_rewriter()
    result = rewriter.rewrite_claude_response(claude_text, signature, emotion)

    return {
        "original_text": result.original_text,
        "rewritten_text": result.rewritten_text,
        "quality_score": result.quality_score,
        "transformation_notes": result.transformation_notes,
        "processing_time": result.processing_time,
        "signature_used": result.signature_used.value,
        "emotion_applied": result.emotion_applied,
    }


# 테스트 및 시연
if __name__ == "__main__":
    print("🎨 Claude to Signature Rewriter 테스트")
    print("=" * 60)

    rewriter = get_signature_rewriter()

    # 테스트 케이스들
    test_cases = [
        {
            "claude_text": "To implement this function, we need to consider the time complexity and optimize the algorithm for better performance.",
            "signature": "Aurora",
            "emotion": "curiosity",
            "description": "기술적 설명 → Aurora 창의적 스타일",
        },
        {
            "claude_text": "Based on the analysis, I would suggest that you focus on developing your skills and embracing challenges.",
            "signature": "Phoenix",
            "emotion": "determination",
            "description": "조언 → Phoenix 성장 중심 스타일",
        },
        {
            "claude_text": "The philosophical implications of this question require careful examination of multiple perspectives.",
            "signature": "Sage",
            "emotion": "contemplation",
            "description": "철학적 내용 → Sage 지혜로운 스타일",
        },
        {
            "claude_text": "I understand that you're going through a difficult time, and I want to help you work through this.",
            "signature": "Companion",
            "emotion": "empathy",
            "description": "위로 → Companion 공감적 스타일",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 테스트 {i}: {test['description']}")
        print(f"원문: {test['claude_text']}")

        result = rewriter.rewrite_claude_response(
            test["claude_text"], test["signature"], test["emotion"]
        )

        print(f"재작성: {result.rewritten_text}")
        print(f"품질 점수: {result.quality_score:.2f}")
        print(f"시그니처: {result.signature_used.value}")
        print(f"처리 시간: {result.processing_time:.3f}초")
        print("변환 과정:", " → ".join(result.transformation_notes))

    # 분석 리포트
    analytics = rewriter.get_rewrite_analytics()
    print(f"\n📊 재작성 분석:")
    print(f"  총 재작성: {analytics['statistics']['total_rewrites']}")
    print(f"  평균 품질: {analytics['quality_assessment']['avg_quality_score']:.2f}")
    print(f"  성공률: {analytics['quality_assessment']['success_rate']:.2%}")

    print("\n✅ Claude to Signature Rewriter 구현 완료!")
    print("🎯 Claude는 입, Echo는 판단자, 시그니처는 목소리!")
