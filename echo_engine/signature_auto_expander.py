#!/usr/bin/env python3
"""
🔄 Signature Auto Expander - 시그니처 매트릭스 자동 확장기
새로운 감정이나 시그니처 추가 시 기존 패턴을 분석하여 자동으로 템플릿 생성

핵심 기능:
- 기존 시그니처 패턴 학습 및 분석
- 새 감정 추가 시 모든 시그니처에 자동 템플릿 생성
- 새 시그니처 추가 시 모든 감정에 대한 템플릿 생성
- 패턴 기반 지능형 템플릿 합성
- 품질 검증 및 일관성 유지
- 백업 및 롤백 지원
"""

import yaml
import json
import random
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import shutil
from collections import defaultdict, Counter
import statistics


@dataclass
class TemplatePattern:
    """템플릿 패턴"""

    signature: str
    emotion: str
    intro_pattern: str
    response_pattern: str
    style_markers: List[str]
    tone_indicators: List[str]
    length_category: str  # short, medium, long


@dataclass
class ExpansionResult:
    """확장 결과"""

    success: bool
    templates_created: int
    templates_updated: int
    backup_path: str
    errors: List[str]
    warnings: List[str]
    expansion_metadata: Dict[str, Any]


class SignatureAutoExpander:
    """시그니처 매트릭스 자동 확장기"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.template_path = self.data_dir / "signature_response_templates.yaml"
        self.backup_dir = self.data_dir / "template_backups"
        self.backup_dir.mkdir(exist_ok=True)

        # 기존 템플릿 로딩 및 분석
        self.existing_templates = self._load_existing_templates()
        self.signature_patterns = self._analyze_signature_patterns()
        self.emotion_patterns = self._analyze_emotion_patterns()
        self.style_library = self._build_style_library()

        print("🔄 Signature Auto Expander 초기화 완료")
        print(f"   📋 기존 템플릿: {len(self.existing_templates)} 시그니처")
        print(f"   🎭 패턴 분석: {len(self.signature_patterns)} 시그니처 패턴")
        print(f"   😊 감정 패턴: {len(self.emotion_patterns)} 감정 패턴")
        print(f"   🎨 스타일 라이브러리: {len(self.style_library)} 스타일")

    def expand_for_new_emotion(
        self, emotion_name: str, emotion_config: Dict[str, Any] = None
    ) -> ExpansionResult:
        """새로운 감정에 대해 모든 시그니처 템플릿 생성"""
        print(f"😊 새 감정 '{emotion_name}' 템플릿 자동 생성 시작")

        # 백업 생성
        backup_path = self._create_backup()

        errors = []
        warnings = []
        templates_created = 0

        # 감정 설정 기본값
        emotion_config = emotion_config or {}
        emotion_intensity = emotion_config.get("intensity", "medium")
        emotion_valence = emotion_config.get(
            "valence", "neutral"
        )  # positive, negative, neutral
        emotion_keywords = emotion_config.get("keywords", [emotion_name])

        try:
            # 각 시그니처에 대해 새 감정 템플릿 생성
            for signature_name, sig_data in self.existing_templates.items():
                if isinstance(sig_data, dict):
                    # 이미 해당 감정이 있는지 확인
                    if emotion_name in sig_data:
                        warnings.append(
                            f"{signature_name}에 이미 {emotion_name} 템플릿 존재"
                        )
                        continue

                    # 새 템플릿 생성
                    new_template = self._generate_emotion_template_for_signature(
                        signature_name, emotion_name, emotion_config
                    )

                    if new_template:
                        sig_data[emotion_name] = new_template
                        templates_created += 1
                        print(f"   ✅ {signature_name} × {emotion_name} 템플릿 생성")
                    else:
                        errors.append(
                            f"{signature_name} × {emotion_name} 템플릿 생성 실패"
                        )

            # 업데이트된 템플릿 저장
            self._save_templates()

            print(
                f"✅ 새 감정 '{emotion_name}' 확장 완료: {templates_created}개 템플릿 생성"
            )

            return ExpansionResult(
                success=True,
                templates_created=templates_created,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "new_emotion",
                    "emotion_name": emotion_name,
                    "emotion_config": emotion_config,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            # 오류 시 백업에서 복원
            self._restore_from_backup(backup_path)
            errors.append(f"확장 중 오류 발생: {e}")

            return ExpansionResult(
                success=False,
                templates_created=0,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "new_emotion",
                    "emotion_name": emotion_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def expand_for_new_signature(
        self, signature_name: str, signature_config: Dict[str, Any]
    ) -> ExpansionResult:
        """새로운 시그니처에 대해 모든 감정 템플릿 생성"""
        print(f"🎭 새 시그니처 '{signature_name}' 템플릿 자동 생성 시작")

        # 백업 생성
        backup_path = self._create_backup()

        errors = []
        warnings = []
        templates_created = 0

        try:
            # 이미 시그니처가 있는지 확인
            if signature_name in self.existing_templates:
                warnings.append(f"{signature_name} 시그니처가 이미 존재")
                return ExpansionResult(
                    success=False,
                    templates_created=0,
                    templates_updated=0,
                    backup_path=backup_path,
                    errors=["시그니처 중복"],
                    warnings=warnings,
                    expansion_metadata={},
                )

            # 모든 기존 감정 추출
            all_emotions = set()
            for sig_data in self.existing_templates.values():
                if isinstance(sig_data, dict):
                    all_emotions.update(sig_data.keys())

            # 새 시그니처 템플릿 딕셔너리 생성
            new_signature_templates = {}

            # 각 감정에 대해 템플릿 생성
            for emotion in all_emotions:
                new_template = self._generate_signature_template_for_emotion(
                    signature_name, emotion, signature_config
                )

                if new_template:
                    new_signature_templates[emotion] = new_template
                    templates_created += 1
                    print(f"   ✅ {signature_name} × {emotion} 템플릿 생성")
                else:
                    errors.append(f"{signature_name} × {emotion} 템플릿 생성 실패")

            # 새 시그니처를 기존 템플릿에 추가
            self.existing_templates[signature_name] = new_signature_templates

            # 업데이트된 템플릿 저장
            self._save_templates()

            print(
                f"✅ 새 시그니처 '{signature_name}' 확장 완료: {templates_created}개 템플릿 생성"
            )

            return ExpansionResult(
                success=True,
                templates_created=templates_created,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "new_signature",
                    "signature_name": signature_name,
                    "signature_config": signature_config,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            # 오류 시 백업에서 복원
            self._restore_from_backup(backup_path)
            errors.append(f"확장 중 오류 발생: {e}")

            return ExpansionResult(
                success=False,
                templates_created=0,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "new_signature",
                    "signature_name": signature_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def fill_missing_combinations(self) -> ExpansionResult:
        """누락된 시그니처×감정 조합 자동 생성"""
        print("🔍 누락된 조합 자동 생성 시작")

        # 백업 생성
        backup_path = self._create_backup()

        errors = []
        warnings = []
        templates_created = 0

        try:
            # 모든 시그니처와 감정 추출
            all_signatures = [
                k for k, v in self.existing_templates.items() if isinstance(v, dict)
            ]
            all_emotions = set()
            for sig_data in self.existing_templates.values():
                if isinstance(sig_data, dict):
                    all_emotions.update(sig_data.keys())
            all_emotions = list(all_emotions)

            print(
                f"   📊 분석: {len(all_signatures)} 시그니처 × {len(all_emotions)} 감정"
            )

            # 누락된 조합 찾기 및 생성
            for signature in all_signatures:
                sig_data = self.existing_templates[signature]
                for emotion in all_emotions:
                    if emotion not in sig_data:
                        # 누락된 조합 발견, 템플릿 생성
                        new_template = self._generate_missing_combination_template(
                            signature, emotion
                        )

                        if new_template:
                            sig_data[emotion] = new_template
                            templates_created += 1
                            print(f"   ➕ {signature} × {emotion} 누락 조합 생성")
                        else:
                            errors.append(f"{signature} × {emotion} 생성 실패")

            # 업데이트된 템플릿 저장
            self._save_templates()

            print(f"✅ 누락 조합 자동 생성 완료: {templates_created}개 템플릿 생성")

            return ExpansionResult(
                success=True,
                templates_created=templates_created,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "fill_missing",
                    "signatures_count": len(all_signatures),
                    "emotions_count": len(all_emotions),
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            # 오류 시 백업에서 복원
            self._restore_from_backup(backup_path)
            errors.append(f"누락 조합 생성 중 오류: {e}")

            return ExpansionResult(
                success=False,
                templates_created=0,
                templates_updated=0,
                backup_path=backup_path,
                errors=errors,
                warnings=warnings,
                expansion_metadata={
                    "expansion_type": "fill_missing",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def _generate_emotion_template_for_signature(
        self, signature: str, emotion: str, emotion_config: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """특정 시그니처에 대한 새 감정 템플릿 생성"""

        # 시그니처 패턴 가져오기
        if signature not in self.signature_patterns:
            return None

        sig_pattern = self.signature_patterns[signature]

        # 감정 패턴 분석 (유사한 감정에서 패턴 추출)
        similar_emotions = self._find_similar_emotions(emotion, emotion_config)
        emotion_pattern = self._extract_emotion_pattern(signature, similar_emotions)

        # 템플릿 구성요소 생성
        intro = self._generate_intro(signature, sig_pattern)
        prompt = self._generate_prompt(
            signature, emotion, sig_pattern, emotion_pattern, emotion_config
        )
        fallback = self._generate_fallback(signature, emotion, sig_pattern)
        style = self._generate_style(signature, emotion, sig_pattern)

        return {"intro": intro, "style": style, "prompt": prompt, "fallback": fallback}

    def _generate_signature_template_for_emotion(
        self, signature: str, emotion: str, signature_config: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """특정 감정에 대한 새 시그니처 템플릿 생성"""

        # 감정 패턴 가져오기
        if emotion not in self.emotion_patterns:
            return None

        emotion_pattern = self.emotion_patterns[emotion]

        # 시그니처 설정에서 정보 추출
        emoji = signature_config.get("emoji", "🎭")
        tone = signature_config.get("tone", "friendly")
        personality_traits = signature_config.get("personality", ["helpful"])

        # 템플릿 구성요소 생성
        intro = f"{emoji} {signature}: "
        prompt = self._generate_new_signature_prompt(
            signature, emotion, signature_config, emotion_pattern
        )
        fallback = f"{intro}함께 이야기해봐요."
        style = f"{signature.lower()}-{emotion}"

        return {"intro": intro, "style": style, "prompt": prompt, "fallback": fallback}

    def _generate_missing_combination_template(
        self, signature: str, emotion: str
    ) -> Optional[Dict[str, str]]:
        """누락된 조합에 대한 템플릿 생성"""

        # 시그니처와 감정 패턴 모두 확인
        if (
            signature not in self.signature_patterns
            or emotion not in self.emotion_patterns
        ):
            return None

        sig_pattern = self.signature_patterns[signature]
        emotion_pattern = self.emotion_patterns[emotion]

        # 기존 패턴을 조합하여 새 템플릿 생성
        intro = sig_pattern.get("intro_template", f"{signature}: ")

        # 프롬프트 생성 (기존 패턴 조합)
        sig_style_words = sig_pattern.get("style_words", [])
        emotion_response_patterns = emotion_pattern.get("response_patterns", [])

        if emotion_response_patterns and sig_style_words:
            base_response = random.choice(emotion_response_patterns)
            style_modifier = random.choice(sig_style_words)
            prompt = f"{intro}{base_response} {style_modifier}"
        else:
            prompt = f"{intro}{emotion} 감정을 이해합니다. 함께 이야기해봐요."

        fallback = f"{intro}어떤 이야기든 들어드릴게요."
        style = f"{signature.lower()}-{emotion}"

        return {"intro": intro, "style": style, "prompt": prompt, "fallback": fallback}

    def _find_similar_emotions(
        self, target_emotion: str, emotion_config: Dict[str, Any]
    ) -> List[str]:
        """유사한 감정 찾기"""
        # 감정 유사성 매핑
        emotion_similarity = {
            "sadness": ["melancholy", "grief", "sorrow", "depression"],
            "joy": ["happiness", "delight", "elation", "euphoria"],
            "anger": ["rage", "fury", "irritation", "annoyance"],
            "anxiety": ["worry", "nervousness", "fear", "stress"],
            "love": ["affection", "adoration", "fondness", "attraction"],
            "curiosity": ["interest", "wonder", "inquisitiveness"],
            "surprise": ["shock", "amazement", "astonishment"],
            "neutral": ["calm", "peaceful", "balanced"],
        }

        # 설정에서 유사 감정 가져오기
        similar_from_config = emotion_config.get("similar_emotions", [])

        # 기본 유사성 매핑에서 찾기
        similar_emotions = similar_from_config.copy()
        for base_emotion, similar_list in emotion_similarity.items():
            if target_emotion.lower() in [base_emotion] + similar_list:
                similar_emotions.extend([base_emotion] + similar_list)

        # 중복 제거 및 기존 감정에서만 필터링
        existing_emotions = set()
        for sig_data in self.existing_templates.values():
            if isinstance(sig_data, dict):
                existing_emotions.update(sig_data.keys())

        return [
            emotion for emotion in set(similar_emotions) if emotion in existing_emotions
        ]

    def _extract_emotion_pattern(
        self, signature: str, similar_emotions: List[str]
    ) -> Dict[str, Any]:
        """유사 감정에서 패턴 추출"""
        pattern = {"response_patterns": [], "style_markers": [], "tone_indicators": []}

        if signature not in self.existing_templates:
            return pattern

        sig_data = self.existing_templates[signature]

        # 유사한 감정들의 템플릿에서 패턴 추출
        for emotion in similar_emotions:
            if emotion in sig_data:
                emotion_template = sig_data[emotion]
                if isinstance(emotion_template, dict):
                    prompt = emotion_template.get("prompt", "")
                    style = emotion_template.get("style", "")

                    if prompt:
                        pattern["response_patterns"].append(prompt)
                    if style:
                        pattern["style_markers"].append(style)

        return pattern

    def _generate_intro(self, signature: str, sig_pattern: Dict[str, Any]) -> str:
        """인트로 생성"""
        intro_templates = sig_pattern.get("intro_templates", [])
        if intro_templates:
            return random.choice(intro_templates)

        # 기본 이모지 매핑
        emoji_mapping = {
            "Selene": "🌙",
            "Lune": "🌙",
            "Aurora": "🌟",
            "Echo-Aurora": "🎭",
            "Echo-Phoenix": "🔥",
            "Echo-Sage": "📚",
            "Echo-Companion": "🤝",
            "Grumbly": "😤",
        }

        emoji = emoji_mapping.get(signature, "🎭")
        return f"{emoji} {signature}: "

    def _generate_prompt(
        self,
        signature: str,
        emotion: str,
        sig_pattern: Dict[str, Any],
        emotion_pattern: Dict[str, Any],
        emotion_config: Dict[str, Any],
    ) -> str:
        """프롬프트 생성"""
        intro = self._generate_intro(signature, sig_pattern)

        # 시그니처별 스타일 적용
        sig_style_words = sig_pattern.get("style_words", [])
        emotion_response_patterns = emotion_pattern.get("response_patterns", [])

        # 감정 강도에 따른 응답 조정
        intensity = emotion_config.get("intensity", "medium")
        intensity_modifiers = {
            "low": ["조금", "약간", "살짝"],
            "medium": [""],
            "high": ["정말", "너무", "매우"],
        }

        modifier = random.choice(intensity_modifiers.get(intensity, [""]))

        # 기본 응답 패턴 생성
        if emotion_response_patterns:
            base_response = random.choice(emotion_response_patterns)
            # intro 부분 제거 (중복 방지)
            base_response = re.sub(r"^[^:]+:\s*", "", base_response)
        else:
            base_response = f"{modifier} {emotion}한 마음이시군요."

        # 시그니처 스타일 적용
        if sig_style_words:
            style_addition = random.choice(sig_style_words)
            prompt = f"{intro}{base_response} {style_addition}"
        else:
            prompt = f"{intro}{base_response}"

        return prompt.strip()

    def _generate_fallback(
        self, signature: str, emotion: str, sig_pattern: Dict[str, Any]
    ) -> str:
        """Fallback 생성"""
        intro = self._generate_intro(signature, sig_pattern)

        fallback_patterns = sig_pattern.get("fallback_patterns", [])
        if fallback_patterns:
            return random.choice(fallback_patterns)

        return f"{intro}함께 이야기해봐요."

    def _generate_style(
        self, signature: str, emotion: str, sig_pattern: Dict[str, Any]
    ) -> str:
        """스타일 생성"""
        return f"{signature.lower()}-{emotion}"

    def _generate_new_signature_prompt(
        self,
        signature: str,
        emotion: str,
        signature_config: Dict[str, Any],
        emotion_pattern: Dict[str, Any],
    ) -> str:
        """새 시그니처용 프롬프트 생성"""
        emoji = signature_config.get("emoji", "🎭")
        tone = signature_config.get("tone", "friendly")
        personality_traits = signature_config.get("personality", ["helpful"])

        intro = f"{emoji} {signature}: "

        # 성격 특성에 따른 응답 스타일
        trait_responses = {
            "caring": "마음을 헤아려드릴게요",
            "analytical": "체계적으로 접근해봅시다",
            "creative": "새로운 관점에서 생각해봐요",
            "supportive": "함께 해결해봐요",
            "direct": "솔직하게 말씀드리면",
        }

        # 주요 특성 선택
        main_trait = personality_traits[0] if personality_traits else "helpful"
        trait_response = trait_responses.get(main_trait, "도와드리겠습니다")

        # 감정별 기본 응답
        emotion_responses = {
            "sadness": "힘든 시간을 보내고 계시는군요",
            "joy": "기쁜 마음이 전해져요",
            "anger": "화가 나시는 마음을 이해해요",
            "anxiety": "불안한 마음이 드시는군요",
            "curiosity": "궁금한 것이 있으시군요",
            "love": "따뜻한 마음이 느껴져요",
            "neutral": "편하게 말씀해주세요",
        }

        emotion_response = emotion_responses.get(
            emotion, f"{emotion} 감정을 느끼고 계시는군요"
        )

        return f"{intro}{emotion_response}. {trait_response}."

    def _analyze_signature_patterns(self) -> Dict[str, Dict[str, Any]]:
        """시그니처별 패턴 분석"""
        patterns = {}

        for signature, sig_data in self.existing_templates.items():
            if isinstance(sig_data, dict):
                pattern = {
                    "intro_templates": [],
                    "style_words": [],
                    "fallback_patterns": [],
                    "response_lengths": [],
                    "tone_markers": [],
                }

                for emotion, emotion_data in sig_data.items():
                    if isinstance(emotion_data, dict):
                        # 인트로 패턴
                        intro = emotion_data.get("intro", "")
                        if intro and intro not in pattern["intro_templates"]:
                            pattern["intro_templates"].append(intro)

                        # 응답 길이
                        prompt = emotion_data.get("prompt", "")
                        if prompt:
                            pattern["response_lengths"].append(len(prompt))

                        # Fallback 패턴
                        fallback = emotion_data.get("fallback", "")
                        if fallback and fallback not in pattern["fallback_patterns"]:
                            pattern["fallback_patterns"].append(fallback)

                        # 스타일 단어 추출
                        self._extract_style_words(prompt, pattern["style_words"])

                patterns[signature] = pattern

        return patterns

    def _analyze_emotion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """감정별 패턴 분석"""
        patterns = defaultdict(
            lambda: {"response_patterns": [], "common_words": [], "tone_indicators": []}
        )

        for sig_data in self.existing_templates.values():
            if isinstance(sig_data, dict):
                for emotion, emotion_data in sig_data.items():
                    if isinstance(emotion_data, dict):
                        prompt = emotion_data.get("prompt", "")
                        if prompt:
                            patterns[emotion]["response_patterns"].append(prompt)
                            self._extract_emotion_words(
                                prompt, patterns[emotion]["common_words"]
                            )

        return dict(patterns)

    def _build_style_library(self) -> Dict[str, List[str]]:
        """스타일 라이브러리 구축"""
        library = {
            "caring": ["따뜻하게", "부드럽게", "공감하며", "위로하며"],
            "analytical": ["체계적으로", "논리적으로", "분석적으로", "객관적으로"],
            "creative": ["창의적으로", "상상력을 발휘하여", "새롭게", "독창적으로"],
            "supportive": ["지지하며", "함께", "동반하여", "격려하며"],
            "direct": ["직접적으로", "솔직하게", "명확하게", "단도직입적으로"],
        }

        return library

    def _extract_style_words(self, text: str, word_list: List[str]):
        """텍스트에서 스타일 단어 추출"""
        style_indicators = [
            "함께",
            "같이",
            "천천히",
            "부드럽게",
            "따뜻하게",
            "차근차근",
            "조심스럽게",
            "정확하게",
            "체계적으로",
            "창의적으로",
        ]

        for indicator in style_indicators:
            if indicator in text and indicator not in word_list:
                word_list.append(indicator)

    def _extract_emotion_words(self, text: str, word_list: List[str]):
        """텍스트에서 감정 단어 추출"""
        emotion_words = [
            "마음",
            "감정",
            "기분",
            "느낌",
            "생각",
            "상황",
            "순간",
            "아픔",
            "기쁨",
            "슬픔",
            "화",
            "불안",
            "걱정",
            "사랑",
        ]

        for word in emotion_words:
            if word in text and word not in word_list:
                word_list.append(word)

    def _load_existing_templates(self) -> Dict[str, Any]:
        """기존 템플릿 로딩 (fallback 처리 강화)"""
        try:
            if self.template_path.exists():
                with open(self.template_path, "r", encoding="utf-8") as f:
                    templates = yaml.safe_load(f)
                    if templates:
                        return templates
                    else:
                        print(
                            "⚠️ 템플릿 파일이 비어있습니다. 기본 템플릿으로 대체합니다."
                        )
                        return self._generate_default_templates()
            else:
                print(
                    f"⚠️ 템플릿 파일이 없습니다 ({self.template_path}). 기본 템플릿으로 대체합니다."
                )
                return self._generate_default_templates()
        except Exception as e:
            print(f"⚠️ 기존 템플릿 로딩 실패: {e}")
            print("🔄 기본 템플릿으로 대체합니다.")
            return self._generate_default_templates()

    def _generate_default_templates(self) -> Dict[str, Any]:
        """기본 시그니처 템플릿 생성"""
        return {
            "Selene": {
                "name": "달빛 같은 치유자",
                "style": "gentle_healing",
                "modes": ["comfort", "healing", "wisdom"],
                "sadness": {
                    "intro": "🌙 Selene: ",
                    "style": "selene-sadness",
                    "prompt": "깊은 슬픔이 마음을 휘감고 있군요... 달빛이 어둠을 완전히 없애지는 못하지만, 길을 비춰주듯이...",
                    "fallback": "🌙 Selene: 힘든 시간을 보내고 계시는군요... 조용히 곁에 있어드릴게요.",
                },
                "joy": {
                    "intro": "🌙 Selene: ",
                    "style": "selene-joy",
                    "prompt": "기쁜 마음이 달빛처럼 은은하게 퍼져나가는 것 같아요...",
                    "fallback": "🌙 Selene: 기쁜 소식이네요... 함께 기뻐해요.",
                },
            },
            "Aurora": {
                "name": "창조적 영감자",
                "style": "creative_inspiration",
                "modes": ["creative", "inspiring", "energetic"],
                "sadness": {
                    "intro": "🌟 Aurora: ",
                    "style": "aurora-sadness",
                    "prompt": "마음이 힘드시는군요... 오로라가 어둠 속에서도 아름다운 빛을 내듯이...",
                    "fallback": "🌟 Aurora: 힘든 시간이지만 함께 이겨내봐요.",
                },
                "joy": {
                    "intro": "🌟 Aurora: ",
                    "style": "aurora-joy",
                    "prompt": "와! 정말 기쁜 일이네요! 오로라가 하늘을 수놓듯이...",
                    "fallback": "🌟 Aurora: 너무 기쁘네요! 함께 축하해요!",
                },
            },
        }

    def _save_templates(self):
        """템플릿 저장"""
        try:
            with open(self.template_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.existing_templates,
                    f,
                    ensure_ascii=False,
                    default_flow_style=False,
                    indent=2,
                    allow_unicode=True,
                )
            print(f"💾 템플릿 저장 완료: {self.template_path}")
        except Exception as e:
            print(f"❌ 템플릿 저장 실패: {e}")

    def _create_backup(self) -> str:
        """백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"templates_backup_{timestamp}.yaml"

        try:
            if self.template_path.exists():
                shutil.copy2(self.template_path, backup_path)
                print(f"📋 백업 생성: {backup_path}")
        except Exception as e:
            print(f"⚠️ 백업 생성 실패: {e}")

        return str(backup_path)

    def _restore_from_backup(self, backup_path: str):
        """백업에서 복원"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                shutil.copy2(backup_file, self.template_path)
                print(f"🔄 백업에서 복원: {backup_path}")
        except Exception as e:
            print(f"❌ 백업 복원 실패: {e}")


def main():
    """CLI 테스트 인터페이스"""
    print("🔄 Signature Auto Expander 테스트")
    print("=" * 50)

    expander = SignatureAutoExpander()

    # 테스트 시나리오
    print("\n🧪 테스트 시나리오:")

    # 1. 새 감정 추가 테스트
    print("\n1️⃣ 새 감정 'excitement' 추가 테스트")
    emotion_config = {
        "intensity": "high",
        "valence": "positive",
        "keywords": ["excited", "thrilled", "enthusiastic"],
        "similar_emotions": ["joy", "curiosity"],
    }

    result1 = expander.expand_for_new_emotion("excitement", emotion_config)
    print(f"   결과: {'성공' if result1.success else '실패'}")
    print(f"   생성된 템플릿: {result1.templates_created}개")
    if result1.errors:
        print(f"   오류: {result1.errors}")

    # 2. 새 시그니처 추가 테스트
    print("\n2️⃣ 새 시그니처 'Echo-Guardian' 추가 테스트")
    signature_config = {
        "emoji": "🛡️",
        "tone": "protective",
        "personality": ["protective", "caring", "vigilant"],
    }

    result2 = expander.expand_for_new_signature("Echo-Guardian", signature_config)
    print(f"   결과: {'성공' if result2.success else '실패'}")
    print(f"   생성된 템플릿: {result2.templates_created}개")
    if result2.errors:
        print(f"   오류: {result2.errors}")

    # 3. 누락 조합 자동 생성 테스트
    print("\n3️⃣ 누락 조합 자동 생성 테스트")
    result3 = expander.fill_missing_combinations()
    print(f"   결과: {'성공' if result3.success else '실패'}")
    print(f"   생성된 템플릿: {result3.templates_created}개")
    if result3.errors:
        print(f"   오류: {result3.errors}")

    print(f"\n📊 최종 결과:")
    print(
        f"   총 생성된 템플릿: {result1.templates_created + result2.templates_created + result3.templates_created}개"
    )
    print(f"   백업 파일: {result1.backup_path}")

    print("\n✅ Signature Auto Expander 테스트 완료!")


if __name__ == "__main__":
    main()
