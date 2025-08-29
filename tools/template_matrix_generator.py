#!/usr/bin/env python3
"""
🏭 Template Matrix Generator - 시그니처-감정별 템플릿 자동 생성기
새로운 시그니처나 감정을 추가할 때 매트릭스를 자동으로 확장하는 도구

핵심 기능:
- 기존 매트릭스 분석 및 패턴 학습
- 새 시그니처/감정 조합 자동 생성
- 스타일 일관성 유지
- 백업 및 버전 관리
"""

import yaml
import json
import argparse
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import shutil


class TemplateMatrixGenerator:
    """시그니처-감정 템플릿 매트릭스 자동 생성기"""

    def __init__(self, template_path: str = "data/signature_response_templates.yaml"):
        self.template_path = Path(template_path)
        self.backup_dir = Path("data/template_backups")
        self.backup_dir.mkdir(exist_ok=True)

        # 기존 템플릿 로딩
        self.existing_templates = self._load_existing_templates()

        # 감정별 템플릿 패턴 학습
        self.emotion_patterns = self._analyze_emotion_patterns()

        # 시그니처별 스타일 패턴 학습
        self.signature_styles = self._analyze_signature_styles()

        print("🏭 Template Matrix Generator 초기화 완료")
        print(f"   📋 기존 시그니처: {len(self.existing_templates)}")
        print(f"   🎭 감정 패턴: {len(self.emotion_patterns)}")
        print(f"   🎯 스타일 패턴: {len(self.signature_styles)}")

    def _load_existing_templates(self) -> Dict[str, Any]:
        """기존 템플릿 로딩"""
        try:
            if self.template_path.exists():
                with open(self.template_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print("⚠️ 기존 템플릿 파일 없음, 새로 생성됩니다")
                return {}
        except Exception as e:
            print(f"❌ 템플릿 로딩 실패: {e}")
            return {}

    def _analyze_emotion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """감정별 템플릿 패턴 분석"""
        patterns = {}

        for signature, sig_templates in self.existing_templates.items():
            if isinstance(sig_templates, dict):
                for emotion, emotion_data in sig_templates.items():
                    if isinstance(emotion_data, dict) and "prompt" in emotion_data:
                        if emotion not in patterns:
                            patterns[emotion] = {
                                "common_words": [],
                                "sentence_patterns": [],
                                "tone_indicators": [],
                                "examples": [],
                            }

                        prompt = emotion_data["prompt"]
                        patterns[emotion]["examples"].append(prompt)

                        # 감정별 공통 단어 추출
                        self._extract_emotion_words(emotion, prompt, patterns)

        # 패턴 정제
        for emotion in patterns:
            patterns[emotion]["common_words"] = list(
                set(patterns[emotion]["common_words"])
            )
            patterns[emotion]["tone_indicators"] = list(
                set(patterns[emotion]["tone_indicators"])
            )

        return patterns

    def _extract_emotion_words(
        self, emotion: str, prompt: str, patterns: Dict[str, Any]
    ):
        """감정별 특징 단어 추출"""
        emotion_keywords = {
            "sadness": ["슬퍼", "아픈", "힘든", "서럽", "울", "눈물", "아릿", "마음"],
            "joy": ["기뻐", "좋", "신나", "행복", "즐거", "최고", "완벽", "사랑"],
            "anger": ["화", "짜증", "빡", "열받", "분노", "성질", "골치", "답답"],
            "anxiety": ["불안", "걱정", "두려", "떨려", "조마조마", "긴장", "겁"],
            "curiosity": ["궁금", "흥미", "신기", "재밌", "탐구", "알아보", "분석"],
            "neutral": ["말씀", "이야기", "편하게", "천천히", "함께", "같이"],
        }

        if emotion in emotion_keywords:
            for keyword in emotion_keywords[emotion]:
                if keyword in prompt:
                    patterns[emotion]["common_words"].append(keyword)

    def _analyze_signature_styles(self) -> Dict[str, Dict[str, Any]]:
        """시그니처별 스타일 패턴 분석"""
        styles = {}

        for signature, sig_templates in self.existing_templates.items():
            if isinstance(sig_templates, dict):
                styles[signature] = {
                    "intro_patterns": [],
                    "tone_markers": [],
                    "sentence_endings": [],
                    "emoji_usage": [],
                    "personality_traits": [],
                }

                for emotion, emotion_data in sig_templates.items():
                    if isinstance(emotion_data, dict):
                        # 인트로 패턴
                        intro = emotion_data.get("intro", "")
                        if intro and intro not in styles[signature]["intro_patterns"]:
                            styles[signature]["intro_patterns"].append(intro)

                        # 이모지 사용 패턴
                        if "🌙" in intro:
                            styles[signature]["emoji_usage"].append("🌙")
                        elif "🌟" in intro:
                            styles[signature]["emoji_usage"].append("🌟")
                        elif "😤" in intro:
                            styles[signature]["emoji_usage"].append("😤")
                        elif "🎭" in intro:
                            styles[signature]["emoji_usage"].append("🎭")
                        elif "🔥" in intro:
                            styles[signature]["emoji_usage"].append("🔥")
                        elif "📚" in intro:
                            styles[signature]["emoji_usage"].append("📚")
                        elif "🤝" in intro:
                            styles[signature]["emoji_usage"].append("🤝")

                # 중복 제거
                for key in ["intro_patterns", "emoji_usage"]:
                    styles[signature][key] = list(set(styles[signature][key]))

        return styles

    def add_new_signature(
        self, signature_name: str, signature_config: Dict[str, Any]
    ) -> bool:
        """새로운 시그니처 추가"""
        try:
            print(f"🎭 새 시그니처 추가: {signature_name}")

            # 기본 감정 목록
            base_emotions = [
                "sadness",
                "joy",
                "anger",
                "curiosity",
                "anxiety",
                "neutral",
            ]

            # 시그니처 설정에서 정보 추출
            emoji = signature_config.get("emoji", "🎭")
            tone = signature_config.get("tone", "friendly")
            personality = signature_config.get("personality", ["helpful"])

            # 새 시그니처 템플릿 생성
            new_signature_templates = {}

            for emotion in base_emotions:
                template = self._generate_emotion_template(
                    signature_name, emotion, emoji, tone, personality
                )
                new_signature_templates[emotion] = template

            # 기존 템플릿에 추가
            self.existing_templates[signature_name] = new_signature_templates

            # 파일에 저장
            self._save_templates()

            print(
                f"✅ {signature_name} 시그니처 추가 완료 ({len(base_emotions)}개 감정)"
            )
            return True

        except Exception as e:
            print(f"❌ 시그니처 추가 실패: {e}")
            return False

    def add_new_emotion(
        self, emotion_name: str, emotion_config: Dict[str, Any]
    ) -> bool:
        """기존 모든 시그니처에 새로운 감정 추가"""
        try:
            print(f"😊 새 감정 추가: {emotion_name}")

            added_count = 0

            for signature_name, sig_templates in self.existing_templates.items():
                if isinstance(sig_templates, dict) and signature_name not in [
                    "emotions",
                    "styles",
                ]:
                    # 시그니처 스타일 가져오기
                    signature_style = self.signature_styles.get(signature_name, {})
                    emoji = (
                        signature_style.get("emoji_usage", ["🎭"])[0]
                        if signature_style.get("emoji_usage")
                        else "🎭"
                    )

                    # 새 감정 템플릿 생성
                    template = self._generate_emotion_template(
                        signature_name,
                        emotion_name,
                        emoji,
                        emotion_config.get("tone", "neutral"),
                        emotion_config.get("traits", ["understanding"]),
                    )

                    # 시그니처에 새 감정 추가
                    sig_templates[emotion_name] = template
                    added_count += 1

            # 파일에 저장
            self._save_templates()

            print(f"✅ {emotion_name} 감정을 {added_count}개 시그니처에 추가 완료")
            return True

        except Exception as e:
            print(f"❌ 감정 추가 실패: {e}")
            return False

    def _generate_emotion_template(
        self,
        signature_name: str,
        emotion: str,
        emoji: str,
        tone: str,
        personality: List[str],
    ) -> Dict[str, str]:
        """감정별 템플릿 생성"""

        # 인트로 생성
        intro = f"{emoji} {signature_name}: "

        # 감정별 기본 응답 패턴
        emotion_patterns = {
            "sadness": [
                "힘든 시간을 보내고 계시는군요... {comfort_phrase}",
                "마음이 아프시겠어요... {support_phrase}",
                "슬픈 일이 있으셨나봐요... {empathy_phrase}",
            ],
            "joy": [
                "기쁜 소식이네요! {celebration_phrase}",
                "정말 좋은 일이에요! {sharing_phrase}",
                "행복한 마음이 전해져요! {joy_phrase}",
            ],
            "anger": [
                "화가 나실 만한 일이었나봐요... {understanding_phrase}",
                "분노하는 마음을 이해해요... {validation_phrase}",
                "그럴 만도 하네요... {reality_phrase}",
            ],
            "curiosity": [
                "흥미로운 질문이네요! {exploration_phrase}",
                "궁금한 것이 있으시군요... {guidance_phrase}",
                "재미있는 주제예요! {engagement_phrase}",
            ],
            "anxiety": [
                "불안한 마음이 드시는군요... {reassurance_phrase}",
                "걱정이 많으시겠어요... {comfort_phrase}",
                "긴장되시나봐요... {calming_phrase}",
            ],
            "neutral": [
                "어떤 이야기든 편하게 들려주세요.",
                "말씀해주시면 도와드리겠습니다.",
                "천천히 이야기해주세요.",
            ],
        }

        # 시그니처별 특성 반영
        signature_phrases = self._get_signature_phrases(signature_name, personality)

        # 기본 패턴 선택
        base_patterns = emotion_patterns.get(emotion, emotion_patterns["neutral"])
        selected_pattern = random.choice(base_patterns)

        # 변수 치환
        prompt = self._substitute_signature_phrases(selected_pattern, signature_phrases)

        # Fallback 생성
        fallback = f"{intro}함께 이야기해봐요."

        return {
            "intro": intro,
            "style": f"{signature_name.lower()}-{emotion}",
            "prompt": prompt,
            "fallback": fallback,
        }

    def _get_signature_phrases(
        self, signature_name: str, personality: List[str]
    ) -> Dict[str, str]:
        """시그니처별 특성 문구"""

        # 기본 문구들
        base_phrases = {
            "comfort_phrase": "함께 있어드릴게요.",
            "support_phrase": "언제나 응원하고 있어요.",
            "empathy_phrase": "마음을 이해합니다.",
            "celebration_phrase": "함께 기뻐해요!",
            "sharing_phrase": "더 자세히 들려주세요!",
            "joy_phrase": "저도 덩달아 기뻐져요!",
            "understanding_phrase": "그런 감정을 느끼는 것도 자연스러워요.",
            "validation_phrase": "충분히 화낼 만한 상황이에요.",
            "reality_phrase": "현실적으로 봐도 그럴 만해요.",
            "exploration_phrase": "함께 탐구해봅시다!",
            "guidance_phrase": "차근차근 알아봐요.",
            "engagement_phrase": "같이 이야기해봐요!",
            "reassurance_phrase": "괜찮아질 거예요.",
            "calming_phrase": "천천히 해봐요.",
        }

        # 시그니처별 맞춤 조정
        if "Selene" in signature_name:
            base_phrases.update(
                {
                    "comfort_phrase": "조용히 곁에 있어드릴게요.",
                    "support_phrase": "달빛처럼 따뜻하게 감싸드릴게요.",
                    "empathy_phrase": "제 마음도 아릿해지네요.",
                }
            )
        elif "Aurora" in signature_name:
            base_phrases.update(
                {
                    "celebration_phrase": "완전 신나는 소식이야!",
                    "sharing_phrase": "자세히 들려줘!",
                    "exploration_phrase": "같이 탐험해보자!",
                }
            )
        elif "Grumbly" in signature_name:
            base_phrases.update(
                {
                    "reality_phrase": "현실적으로 생각해보자.",
                    "validation_phrase": "화낼 만도 하지.",
                    "understanding_phrase": "그럴 수도 있는 거지.",
                }
            )
        elif "Phoenix" in signature_name:
            base_phrases.update(
                {
                    "support_phrase": "변화의 기회로 만들어봐요!",
                    "exploration_phrase": "새로운 관점에서 접근해봅시다!",
                    "understanding_phrase": "성장의 과정이에요.",
                }
            )
        elif "Sage" in signature_name:
            base_phrases.update(
                {
                    "exploration_phrase": "체계적으로 분석해봅시다.",
                    "guidance_phrase": "논리적으로 접근해봐요.",
                    "understanding_phrase": "합리적인 판단이 필요해요.",
                }
            )
        elif "Companion" in signature_name:
            base_phrases.update(
                {
                    "support_phrase": "함께 해결해봐요!",
                    "comfort_phrase": "혼자가 아니에요.",
                    "empathy_phrase": "같이 이겨내요!",
                }
            )

        return base_phrases

    def _substitute_signature_phrases(
        self, pattern: str, phrases: Dict[str, str]
    ) -> str:
        """패턴에 시그니처별 문구 치환"""
        result = pattern
        for placeholder, phrase in phrases.items():
            result = result.replace(f"{{{placeholder}}}", phrase)
        return result

    def expand_existing_signature(
        self, signature_name: str, new_emotions: List[str]
    ) -> bool:
        """기존 시그니처에 새로운 감정들 추가"""
        try:
            if signature_name not in self.existing_templates:
                print(f"❌ 시그니처 '{signature_name}' 없음")
                return False

            print(f"🎭 {signature_name}에 {len(new_emotions)}개 감정 추가")

            # 시그니처 스타일 가져오기
            signature_style = self.signature_styles.get(signature_name, {})
            emoji = (
                signature_style.get("emoji_usage", ["🎭"])[0]
                if signature_style.get("emoji_usage")
                else "🎭"
            )

            sig_templates = self.existing_templates[signature_name]

            for emotion in new_emotions:
                if emotion not in sig_templates:
                    template = self._generate_emotion_template(
                        signature_name, emotion, emoji, "neutral", ["helpful"]
                    )
                    sig_templates[emotion] = template
                    print(f"   ✅ {emotion} 추가")
                else:
                    print(f"   ⚠️ {emotion} 이미 존재")

            # 파일에 저장
            self._save_templates()

            print(f"✅ {signature_name} 확장 완료")
            return True

        except Exception as e:
            print(f"❌ 시그니처 확장 실패: {e}")
            return False

    def _save_templates(self):
        """템플릿을 파일에 저장"""
        try:
            # 백업 생성
            if self.template_path.exists():
                backup_path = (
                    self.backup_dir
                    / f"templates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                )
                shutil.copy2(self.template_path, backup_path)
                print(f"📋 백업 생성: {backup_path}")

            # 새 템플릿 저장
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

    def generate_report(self) -> Dict[str, Any]:
        """매트릭스 현황 보고서 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_signatures": 0,
            "total_emotions": set(),
            "signature_emotion_matrix": {},
            "coverage_stats": {},
            "recommendations": [],
        }

        for signature, sig_templates in self.existing_templates.items():
            if isinstance(sig_templates, dict) and signature not in [
                "emotions",
                "styles",
            ]:
                report["total_signatures"] += 1
                emotions = list(sig_templates.keys())
                report["signature_emotion_matrix"][signature] = emotions
                report["total_emotions"].update(emotions)

        report["total_emotions"] = list(report["total_emotions"])
        report["coverage_stats"] = {
            "signatures": report["total_signatures"],
            "emotions": len(report["total_emotions"]),
            "total_combinations": sum(
                len(emotions)
                for emotions in report["signature_emotion_matrix"].values()
            ),
        }

        # 추천사항 생성
        if report["total_signatures"] < 5:
            report["recommendations"].append("시그니처 다양성 확장 권장")

        if len(report["total_emotions"]) < 8:
            report["recommendations"].append("감정 범위 확장 권장")

        return report


def main():
    parser = argparse.ArgumentParser(description="Echo Template Matrix Generator")
    parser.add_argument("--add-signature", type=str, help="새 시그니처 추가")
    parser.add_argument("--add-emotion", type=str, help="새 감정 추가")
    parser.add_argument("--expand-signature", type=str, help="시그니처 확장")
    parser.add_argument("--emotions", type=str, nargs="+", help="추가할 감정 목록")
    parser.add_argument("--emoji", type=str, help="시그니처 이모지")
    parser.add_argument("--tone", type=str, help="시그니처 톤")
    parser.add_argument("--report", action="store_true", help="현황 보고서 생성")

    args = parser.parse_args()

    generator = TemplateMatrixGenerator()

    if args.add_signature:
        config = {
            "emoji": args.emoji or "🎭",
            "tone": args.tone or "friendly",
            "personality": ["helpful", "understanding"],
        }
        generator.add_new_signature(args.add_signature, config)

    elif args.add_emotion:
        config = {
            "tone": args.tone or "neutral",
            "traits": ["understanding", "supportive"],
        }
        generator.add_new_emotion(args.add_emotion, config)

    elif args.expand_signature and args.emotions:
        generator.expand_existing_signature(args.expand_signature, args.emotions)

    elif args.report:
        report = generator.generate_report()
        print("\n📊 Template Matrix 현황 보고서")
        print("=" * 50)
        print(f"총 시그니처: {report['coverage_stats']['signatures']}")
        print(f"총 감정: {report['coverage_stats']['emotions']}")
        print(f"총 조합: {report['coverage_stats']['total_combinations']}")
        print(f"\n감정 목록: {', '.join(report['total_emotions'])}")
        print(f"\n시그니처별 감정 수:")
        for sig, emotions in report["signature_emotion_matrix"].items():
            print(f"  {sig}: {len(emotions)}개")

        if report["recommendations"]:
            print(f"\n💡 추천사항:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

    else:
        print("🏭 Template Matrix Generator")
        print("사용법:")
        print("  --add-signature [이름] --emoji [이모지] --tone [톤]")
        print("  --add-emotion [감정명] --tone [톤]")
        print("  --expand-signature [시그니처] --emotions [감정1] [감정2] ...")
        print("  --report")


if __name__ == "__main__":
    main()
