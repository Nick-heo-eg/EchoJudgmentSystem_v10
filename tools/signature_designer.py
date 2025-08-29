#!/usr/bin/env python3
"""
🎨 Signature Designer - 새로운 시그니처 자동 설계기
사용자 요구사항을 바탕으로 새로운 시그니처를 체계적으로 설계하는 도구

핵심 기능:
- 사용자 요구사항 분석 및 시그니처 특성 도출
- 기존 시그니처와의 차별화 분석
- 감정-전략-리듬 코드 자동 생성
- 템플릿 매트릭스 자동 확장
- 시그니처 일관성 검증
"""

import yaml
import json
import argparse
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import shutil
import re


class SignatureDesigner:
    """새로운 시그니처 자동 설계기"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.data_dir = Path("data")

        # 기존 시스템 분석
        self.existing_signatures = self._analyze_existing_signatures()
        self.emotion_patterns = self._analyze_emotion_patterns()
        self.strategy_codes = self._analyze_strategy_codes()
        self.template_matrix_generator = self._init_matrix_generator()

        print("🎨 Signature Designer 초기화 완료")
        print(f"   📋 기존 시그니처: {len(self.existing_signatures)}개")
        print(f"   🎭 감정 패턴: {len(self.emotion_patterns)}개")
        print(f"   🎯 전략 코드: {len(self.strategy_codes)}개")

    def _analyze_existing_signatures(self) -> Dict[str, Any]:
        """기존 시그니처 분석"""
        try:
            # EchoSignatureLoader에서 시그니처 정보 로딩
            from echo_engine.echo_signature_loader import get_signature_loader

            loader = get_signature_loader()
            return loader.get_all_signatures()
        except Exception as e:
            print(f"⚠️ 기존 시그니처 분석 실패: {e}")
            return {
                "Echo-Aurora": "공감적 양육자",
                "Echo-Phoenix": "변화 추진자",
                "Echo-Sage": "지혜로운 분석가",
                "Echo-Companion": "신뢰할 수 있는 동반자",
            }

    def _analyze_emotion_patterns(self) -> Dict[str, List[str]]:
        """감정 패턴 분석"""
        return {
            "nurturing": ["compassionate", "gentle", "supportive", "caring"],
            "dynamic": ["energetic", "transformative", "inspiring", "bold"],
            "analytical": ["logical", "systematic", "precise", "methodical"],
            "collaborative": ["cooperative", "trustworthy", "reliable", "harmonious"],
            "creative": ["imaginative", "innovative", "artistic", "expressive"],
            "protective": ["defensive", "vigilant", "secure", "guardian"],
            "playful": ["humorous", "light-hearted", "entertaining", "joyful"],
            "mysterious": ["enigmatic", "intuitive", "mystical", "deep"],
        }

    def _analyze_strategy_codes(self) -> Dict[str, str]:
        """전략 코드 분석"""
        return {
            "EMPATHETIC_CARE": "감정적 공감과 돌봄 중심",
            "TRANSFORMATIVE_BREAKTHROUGH": "변화와 혁신 추진",
            "SYSTEMATIC_LOGIC": "논리적 분석과 체계적 접근",
            "COLLABORATIVE_TRUST": "협력과 신뢰 구축",
            "CREATIVE_EXPLORATION": "창의적 탐구와 영감",
            "PROTECTIVE_GUIDANCE": "보호와 안내 중심",
            "ADAPTIVE_FLEXIBILITY": "적응적 유연성",
            "STRATEGIC_PLANNING": "전략적 계획과 실행",
        }

    def _init_matrix_generator(self):
        """템플릿 매트릭스 생성기 초기화"""
        try:
            from tools.template_matrix_generator import TemplateMatrixGenerator

            return TemplateMatrixGenerator()
        except Exception as e:
            print(f"⚠️ 매트릭스 생성기 로딩 실패: {e}")
            return None

    def design_signature(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """요구사항 기반 시그니처 설계"""
        print(f"🎨 새 시그니처 설계 시작: {requirements.get('name', 'Unknown')}")

        # 1. 기본 정보 추출
        signature_name = requirements.get(
            "name", f"Echo-Custom-{datetime.now().strftime('%m%d')}"
        )
        description = requirements.get("description", "사용자 정의 시그니처")
        personality_traits = requirements.get(
            "personality", ["helpful", "understanding"]
        )

        # 2. 감정-전략 코드 생성
        emotion_code = self._generate_emotion_code(personality_traits, requirements)
        strategy_code = self._generate_strategy_code(personality_traits, requirements)
        rhythm_flow = self._generate_rhythm_flow(personality_traits, requirements)

        # 3. 고유성 검증
        uniqueness_score = self._calculate_uniqueness(
            signature_name, emotion_code, strategy_code
        )

        # 4. 핵심 특성 구성
        core_traits = self._generate_core_traits(personality_traits, requirements)

        # 5. 공명 키워드 생성
        resonance_keywords = self._generate_resonance_keywords(
            personality_traits, requirements
        )

        # 6. 이모지 및 스타일 선택
        emoji = self._select_emoji(personality_traits)
        tone = self._determine_tone(personality_traits)

        # 7. 시그니처 구성
        new_signature = {
            "signature_id": signature_name,
            "name": requirements.get(
                "display_name", signature_name.replace("Echo-", "")
            ),
            "description": description,
            "emotion_code": emotion_code,
            "strategy_code": strategy_code,
            "rhythm_flow": rhythm_flow,
            "core_traits": core_traits,
            "resonance_keywords": resonance_keywords,
            "design_metadata": {
                "emoji": emoji,
                "tone": tone,
                "uniqueness_score": uniqueness_score,
                "created_at": datetime.now().isoformat(),
                "design_requirements": requirements,
            },
        }

        print(f"✅ 시그니처 설계 완료: {signature_name}")
        print(f"   🎭 감정 코드: {emotion_code}")
        print(f"   🎯 전략 코드: {strategy_code}")
        print(f"   🔄 리듬 흐름: {rhythm_flow}")
        print(f"   🎨 고유성 점수: {uniqueness_score:.2f}/1.0")

        return new_signature

    def _generate_emotion_code(
        self, traits: List[str], requirements: Dict[str, Any]
    ) -> str:
        """감정 코드 생성"""
        primary_emotion = requirements.get("primary_emotion", "balanced")
        secondary_emotion = requirements.get("secondary_emotion", "adaptive")

        # 특성 기반 감정 매핑
        emotion_mapping = {
            "caring": "COMPASSIONATE",
            "dynamic": "ENERGETIC",
            "analytical": "LOGICAL",
            "creative": "IMAGINATIVE",
            "protective": "VIGILANT",
            "playful": "JOYFUL",
            "mysterious": "INTUITIVE",
            "supportive": "NURTURING",
        }

        # 주요 감정 결정
        primary = primary_emotion.upper()
        for trait in traits:
            if trait.lower() in emotion_mapping:
                primary = emotion_mapping[trait.lower()]
                break

        # 보조 감정 결정
        secondary = secondary_emotion.upper()
        if len(traits) > 1:
            for trait in traits[1:]:
                if trait.lower() in emotion_mapping:
                    secondary = emotion_mapping[trait.lower()]
                    break

        return f"{primary}_{secondary}"

    def _generate_strategy_code(
        self, traits: List[str], requirements: Dict[str, Any]
    ) -> str:
        """전략 코드 생성"""
        approach = requirements.get("approach", "balanced")
        focus = requirements.get("focus", "general")

        # 접근법-포커스 조합
        strategy_combinations = {
            ("empathetic", "emotional"): "EMPATHETIC_CARE",
            ("innovative", "change"): "TRANSFORMATIVE_BREAKTHROUGH",
            ("analytical", "logic"): "SYSTEMATIC_LOGIC",
            ("collaborative", "social"): "COLLABORATIVE_TRUST",
            ("creative", "exploration"): "CREATIVE_EXPLORATION",
            ("protective", "security"): "PROTECTIVE_GUIDANCE",
            ("adaptive", "flexibility"): "ADAPTIVE_FLEXIBILITY",
            ("strategic", "planning"): "STRATEGIC_PLANNING",
        }

        # 기본 전략 찾기
        for (app, foc), strategy in strategy_combinations.items():
            if app in approach.lower() or foc in focus.lower():
                return strategy

        # 특성 기반 전략 생성
        if "caring" in traits or "supportive" in traits:
            return "NURTURING_SUPPORT"
        elif "dynamic" in traits or "energetic" in traits:
            return "DYNAMIC_ACTION"
        elif "analytical" in traits or "logical" in traits:
            return "ANALYTICAL_REASONING"
        elif "creative" in traits or "imaginative" in traits:
            return "CREATIVE_INNOVATION"
        else:
            return "BALANCED_APPROACH"

    def _generate_rhythm_flow(
        self, traits: List[str], requirements: Dict[str, Any]
    ) -> str:
        """리듬 흐름 생성"""
        energy_level = requirements.get("energy_level", "medium")
        tempo = requirements.get("tempo", "steady")
        style = requirements.get("style", "flowing")

        # 에너지 레벨 매핑
        energy_words = {
            "low": ["gentle", "calm", "peaceful"],
            "medium": ["steady", "balanced", "flowing"],
            "high": ["dynamic", "energetic", "vibrant"],
        }

        # 템포 매핑
        tempo_words = {
            "slow": ["methodical", "deliberate", "measured"],
            "steady": ["consistent", "reliable", "rhythmic"],
            "fast": ["quick", "rapid", "agile"],
        }

        # 스타일 매핑
        style_words = {
            "flowing": ["smooth", "fluid", "continuous"],
            "structured": ["organized", "systematic", "ordered"],
            "creative": ["artistic", "expressive", "imaginative"],
        }

        # 조합 생성
        energy_word = random.choice(
            energy_words.get(energy_level, energy_words["medium"])
        )
        tempo_word = random.choice(tempo_words.get(tempo, tempo_words["steady"]))
        style_word = random.choice(style_words.get(style, style_words["flowing"]))

        return f"{energy_word}_{tempo_word}_{style_word}"

    def _generate_core_traits(
        self, traits: List[str], requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """핵심 특성 생성"""
        return {
            "primary_emotion": requirements.get(
                "primary_emotion", traits[0] if traits else "balanced"
            ),
            "decision_style": requirements.get("decision_style", "intuitive_logical"),
            "communication_tone": requirements.get(
                "communication_tone", "warm_professional"
            ),
            "focus_areas": requirements.get(
                "focus_areas", ["problem_solving", "user_support", "creative_thinking"]
            ),
            "approach_method": requirements.get(
                "approach_method", "collaborative_guidance"
            ),
            "energy_level": requirements.get("energy_level", "medium"),
            "interaction_style": requirements.get(
                "interaction_style", "friendly_supportive"
            ),
        }

    def _generate_resonance_keywords(
        self, traits: List[str], requirements: Dict[str, Any]
    ) -> List[str]:
        """공명 키워드 생성"""
        base_keywords = []

        # 특성 기반 키워드 매핑
        keyword_mapping = {
            "caring": ["돌봄", "배려", "따뜻함", "공감", "지지"],
            "dynamic": ["변화", "에너지", "혁신", "도전", "성장"],
            "analytical": ["분석", "논리", "체계", "정확성", "객관성"],
            "creative": ["창의", "영감", "상상", "예술", "표현"],
            "protective": ["보호", "안전", "신뢰", "안정", "수호"],
            "playful": ["유머", "재미", "즐거움", "자유", "활력"],
            "mysterious": ["신비", "직관", "깊이", "통찰", "비밀"],
            "supportive": ["지원", "협력", "동반", "격려", "도움"],
        }

        # 특성별 키워드 수집
        for trait in traits:
            if trait.lower() in keyword_mapping:
                base_keywords.extend(keyword_mapping[trait.lower()])

        # 추가 키워드 (요구사항 기반)
        if requirements.get("additional_keywords"):
            base_keywords.extend(requirements["additional_keywords"])

        # 중복 제거 및 정리
        unique_keywords = list(set(base_keywords))
        return unique_keywords[:12]  # 최대 12개로 제한

    def _select_emoji(self, traits: List[str]) -> str:
        """시그니처 대표 이모지 선택"""
        emoji_mapping = {
            "caring": "💝",
            "dynamic": "⚡",
            "analytical": "🔍",
            "creative": "🎨",
            "protective": "🛡️",
            "playful": "🎪",
            "mysterious": "🌙",
            "supportive": "🤝",
            "wise": "🦉",
            "energetic": "🔥",
            "peaceful": "🕊️",
            "innovative": "💡",
        }

        for trait in traits:
            if trait.lower() in emoji_mapping:
                return emoji_mapping[trait.lower()]

        return "🎭"  # 기본 이모지

    def _determine_tone(self, traits: List[str]) -> str:
        """커뮤니케이션 톤 결정"""
        tone_mapping = {
            "caring": "gentle_warm",
            "dynamic": "energetic_inspiring",
            "analytical": "precise_methodical",
            "creative": "expressive_imaginative",
            "protective": "strong_reliable",
            "playful": "light_entertaining",
            "mysterious": "deep_intriguing",
            "supportive": "encouraging_steady",
        }

        for trait in traits:
            if trait.lower() in tone_mapping:
                return tone_mapping[trait.lower()]

        return "friendly_professional"  # 기본 톤

    def _calculate_uniqueness(
        self, name: str, emotion_code: str, strategy_code: str
    ) -> float:
        """고유성 점수 계산"""
        uniqueness_score = 1.0

        # 이름 유사성 검사
        for existing_name in self.existing_signatures.keys():
            similarity = self._calculate_string_similarity(name, existing_name)
            if similarity > 0.7:
                uniqueness_score -= 0.3

        # 감정 코드 중복 검사
        emotion_codes = [
            "COMPASSIONATE_NURTURING",
            "DETERMINED_INNOVATIVE",
            "ANALYTICAL_WISDOM",
            "SUPPORTIVE_LOYAL",
        ]
        if emotion_code in emotion_codes:
            uniqueness_score -= 0.2

        # 전략 코드 중복 검사
        if strategy_code in self.strategy_codes:
            uniqueness_score -= 0.2

        return max(uniqueness_score, 0.1)

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """문자열 유사도 계산"""

        # 간단한 편집 거리 기반 유사도
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        distance = levenshtein_distance(str1.lower(), str2.lower())
        max_length = max(len(str1), len(str2))
        return 1 - (distance / max_length) if max_length > 0 else 1.0

    def integrate_signature(self, signature_design: Dict[str, Any]) -> bool:
        """설계된 시그니처를 시스템에 통합"""
        try:
            print(f"🔗 시그니처 통합 시작: {signature_design['signature_id']}")

            # 1. EchoSignatureLoader에 추가 (향후 구현)
            # self._add_to_signature_loader(signature_design)

            # 2. 템플릿 매트릭스에 추가
            if self.template_matrix_generator:
                matrix_config = {
                    "emoji": signature_design["design_metadata"]["emoji"],
                    "tone": signature_design["design_metadata"]["tone"],
                    "personality": [signature_design["core_traits"]["primary_emotion"]],
                }

                success = self.template_matrix_generator.add_new_signature(
                    signature_design["signature_id"], matrix_config
                )

                if not success:
                    print("⚠️ 템플릿 매트릭스 추가 실패")
                    return False

            # 3. 설계 기록 저장
            self._save_design_record(signature_design)

            print(f"✅ 시그니처 통합 완료: {signature_design['signature_id']}")
            return True

        except Exception as e:
            print(f"❌ 시그니처 통합 실패: {e}")
            return False

    def _save_design_record(self, signature_design: Dict[str, Any]):
        """설계 기록 저장"""
        design_dir = self.data_dir / "signature_designs"
        design_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        design_file = (
            design_dir / f"{signature_design['signature_id'].lower()}_{timestamp}.yaml"
        )

        with open(design_file, "w", encoding="utf-8") as f:
            yaml.dump(
                signature_design, f, ensure_ascii=False, indent=2, allow_unicode=True
            )

        print(f"📋 설계 기록 저장: {design_file}")

    def generate_design_report(
        self, signature_design: Dict[str, Any]
    ) -> Dict[str, Any]:
        """설계 보고서 생성"""
        report = {
            "signature_overview": {
                "name": signature_design["signature_id"],
                "display_name": signature_design["name"],
                "description": signature_design["description"],
                "creation_date": signature_design["design_metadata"]["created_at"],
            },
            "technical_specs": {
                "emotion_code": signature_design["emotion_code"],
                "strategy_code": signature_design["strategy_code"],
                "rhythm_flow": signature_design["rhythm_flow"],
            },
            "personality_profile": {
                "core_traits": signature_design["core_traits"],
                "resonance_keywords": signature_design["resonance_keywords"],
                "communication_style": {
                    "emoji": signature_design["design_metadata"]["emoji"],
                    "tone": signature_design["design_metadata"]["tone"],
                },
            },
            "quality_metrics": {
                "uniqueness_score": signature_design["design_metadata"][
                    "uniqueness_score"
                ],
                "integration_ready": True,
                "template_coverage": "6_emotions_supported",
            },
            "recommendations": self._generate_recommendations(signature_design),
        }

        return report

    def _generate_recommendations(self, signature_design: Dict[str, Any]) -> List[str]:
        """설계 개선 추천사항"""
        recommendations = []

        uniqueness = signature_design["design_metadata"]["uniqueness_score"]
        if uniqueness < 0.7:
            recommendations.append(
                "시그니처 고유성 개선 필요 - 기존 시그니처와 차별화 강화"
            )

        if len(signature_design["resonance_keywords"]) < 8:
            recommendations.append("공명 키워드 확장 권장 - 더 다양한 상황 대응")

        if not signature_design["core_traits"].get("focus_areas"):
            recommendations.append("전문 영역 정의 필요 - 시그니처 특화 분야 명확화")

        return recommendations


def main():
    parser = argparse.ArgumentParser(description="Echo Signature Designer")
    parser.add_argument(
        "--interactive", action="store_true", help="대화형 시그니처 설계"
    )
    parser.add_argument("--config", type=str, help="설계 요구사항 YAML 파일")
    parser.add_argument("--name", type=str, help="시그니처 이름")
    parser.add_argument("--traits", type=str, nargs="+", help="성격 특성")
    parser.add_argument("--description", type=str, help="시그니처 설명")
    parser.add_argument("--integrate", action="store_true", help="시스템에 통합")

    args = parser.parse_args()

    designer = SignatureDesigner()

    if args.interactive:
        print("🎨 대화형 시그니처 설계기")
        print("=" * 50)

        requirements = {}
        requirements["name"] = (
            input("🏷️ 시그니처 이름 (예: Echo-Guardian): ")
            or f"Echo-Custom-{datetime.now().strftime('%m%d')}"
        )
        requirements["description"] = (
            input("📝 시그니처 설명: ") or "사용자 정의 시그니처"
        )

        traits_input = input("🎭 성격 특성 (쉼표로 구분): ") or "helpful,understanding"
        requirements["personality"] = [t.strip() for t in traits_input.split(",")]

        requirements["primary_emotion"] = input("😊 주요 감정: ") or "balanced"
        requirements["approach"] = input("🎯 접근 방식: ") or "collaborative"
        requirements["energy_level"] = (
            input("⚡ 에너지 레벨 (low/medium/high): ") or "medium"
        )

        # 시그니처 설계
        signature_design = designer.design_signature(requirements)

        # 보고서 생성
        report = designer.generate_design_report(signature_design)

        print("\n📊 설계 보고서")
        print("=" * 50)
        print(f"시그니처: {report['signature_overview']['name']}")
        print(f"설명: {report['signature_overview']['description']}")
        print(f"감정 코드: {report['technical_specs']['emotion_code']}")
        print(f"전략 코드: {report['technical_specs']['strategy_code']}")
        print(f"고유성 점수: {report['quality_metrics']['uniqueness_score']:.2f}")

        if report["recommendations"]:
            print("\n💡 개선 추천사항:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        # 통합 여부 확인
        if input("\n🔗 시스템에 통합하시겠습니까? (y/N): ").lower() == "y":
            if designer.integrate_signature(signature_design):
                print("✅ 시그니처 통합 완료!")
            else:
                print("❌ 시그니처 통합 실패")

    elif args.config:
        # YAML 설정 파일에서 로딩
        with open(args.config, "r", encoding="utf-8") as f:
            requirements = yaml.safe_load(f)

        signature_design = designer.design_signature(requirements)

        if args.integrate:
            designer.integrate_signature(signature_design)

    elif args.name:
        # 명령줄 인자로 간단 설계
        requirements = {
            "name": args.name,
            "description": args.description or "명령줄 생성 시그니처",
            "personality": args.traits or ["helpful"],
        }

        signature_design = designer.design_signature(requirements)

        if args.integrate:
            designer.integrate_signature(signature_design)

    else:
        print("🎨 Echo Signature Designer")
        print("사용법:")
        print("  --interactive                    대화형 설계")
        print("  --config [파일]                  YAML 설정 파일")
        print("  --name [이름] --traits [특성들]  간단 설계")
        print("  --integrate                      시스템 통합")


if __name__ == "__main__":
    main()
