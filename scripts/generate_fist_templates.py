#!/usr/bin/env python3
"""
🎯 FIST Templates Auto-Generator - 감정 × 전략 조합 기반 템플릿 생성기

EchoJudgmentSystem의 fallback 판단 구조 강화를 위한 FIST 템플릿 자동 생성 도구.
감정(6개) × 전략(6개) = 총 36개의 조합 템플릿을 YAML 형식으로 생성합니다.

핵심 기능:
1. 감정 목록: joy, sadness, anger, fear, surprise, neutral
2. 전략 목록: adapt, confront, retreat, analyze, initiate, harmonize
3. 템플릿 구조: frame, insight, strategy, tactics
4. 출력 위치: echo_engine/templates/fist_autogen/*.yaml
5. template_engine.py 호환 구조
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class FISTTemplateGenerator:
    """🎭 FIST 템플릿 자동 생성기"""

    def __init__(self):
        self.version = "1.0.0"

        # 감정 목록 (총 6개)
        self.emotions = {
            "joy": {"korean": "기쁨", "description": "긍정적이고 밝은 감정 상태"},
            "sadness": {"korean": "슬픔", "description": "우울하고 침울한 감정 상태"},
            "anger": {"korean": "분노", "description": "화나고 격정적인 감정 상태"},
            "fear": {
                "korean": "두려움",
                "description": "불안하고 걱정스러운 감정 상태",
            },
            "surprise": {
                "korean": "놀라움",
                "description": "예상치 못한 상황에 대한 감정 상태",
            },
            "neutral": {"korean": "중립", "description": "평온하고 균형잡힌 감정 상태"},
        }

        # 전략 목록 (총 6개)
        self.strategies = {
            "adapt": {
                "korean": "적응",
                "description": "상황에 맞춰 유연하게 변화하는 전략",
            },
            "confront": {
                "korean": "대응",
                "description": "문제에 직면하여 해결하는 전략",
            },
            "retreat": {
                "korean": "후퇴",
                "description": "일시적으로 물러나서 재정비하는 전략",
            },
            "analyze": {
                "korean": "분석",
                "description": "상황을 깊이 파악하고 이해하는 전략",
            },
            "initiate": {
                "korean": "주도",
                "description": "적극적으로 변화를 이끄는 전략",
            },
            "harmonize": {
                "korean": "조화",
                "description": "균형과 화합을 추구하는 전략",
            },
        }

        # 출력 디렉토리
        self.output_dir = Path("echo_engine/templates/fist_autogen")

        print(f"🎭 FIST Template Generator v{self.version} 초기화 완료")
        print(f"   감정 종류: {len(self.emotions)}개")
        print(f"   전략 종류: {len(self.strategies)}개")
        print(f"   생성 예정: {len(self.emotions) * len(self.strategies)}개 템플릿")

    def create_output_directory(self):
        """출력 디렉토리 생성"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 출력 디렉토리 준비: {self.output_dir}")

    def generate_template_content(self, emotion: str, strategy: str) -> Dict[str, Any]:
        """개별 템플릿 콘텐츠 생성"""

        emotion_info = self.emotions[emotion]
        strategy_info = self.strategies[strategy]

        # Frame 생성 (상황 인식)
        frame_templates = {
            "joy": {
                "adapt": "당신의 기쁨이 상황을 밝게 비추고 있습니다.",
                "confront": "긍정적인 에너지로 문제에 맞서볼 시간입니다.",
                "retreat": "기쁨을 간직한 채 잠시 휴식을 취해보세요.",
                "analyze": "이 좋은 순간을 더 깊이 이해해보겠습니다.",
                "initiate": "기쁜 마음으로 새로운 시작을 만들어보세요.",
                "harmonize": "당신의 기쁨이 주변과 아름다운 조화를 이루고 있어요.",
            },
            "sadness": {
                "adapt": "슬픔 속에서도 변화에 적응할 수 있는 힘이 있어요.",
                "confront": "이 슬픔을 정면으로 마주하며 극복해나가겠습니다.",
                "retreat": "슬픔을 받아들이며 잠시 마음을 쉬어가세요.",
                "analyze": "이 슬픔이 무엇을 말하고 있는지 함께 살펴보겠습니다.",
                "initiate": "슬픔을 딛고 새로운 변화를 시작해보세요.",
                "harmonize": "슬픔도 삶의 한 부분으로 받아들이며 균형을 찾아가겠습니다.",
            },
            "anger": {
                "adapt": "분노의 에너지를 건설적인 방향으로 바꿔보겠습니다.",
                "confront": "이 분노의 원인에 정면으로 맞서보겠습니다.",
                "retreat": "분노를 진정시키며 마음의 평정을 되찾아보세요.",
                "analyze": "이 분노가 어디서 오는지 차근차근 살펴보겠습니다.",
                "initiate": "분노를 변화의 동력으로 전환해보겠습니다.",
                "harmonize": "분노와 평온 사이의 균형점을 찾아보겠습니다.",
            },
            "fear": {
                "adapt": "두려움 속에서도 상황에 맞춰 유연하게 대응해보세요.",
                "confront": "두려움에 맞서며 용기를 내어보겠습니다.",
                "retreat": "두려울 때는 안전한 곳에서 마음을 다스려보세요.",
                "analyze": "이 두려움의 정체가 무엇인지 함께 파악해보겠습니다.",
                "initiate": "두려움을 넘어 새로운 도전을 시작해보세요.",
                "harmonize": "두려움과 용기 사이의 균형을 찾아가겠습니다.",
            },
            "surprise": {
                "adapt": "예상치 못한 상황에 유연하게 적응해보겠습니다.",
                "confront": "놀라운 상황을 정면으로 받아들여보겠습니다.",
                "retreat": "놀라움을 차분히 정리할 시간을 가져보세요.",
                "analyze": "이 놀라운 상황이 무엇을 의미하는지 살펴보겠습니다.",
                "initiate": "놀라운 기회를 새로운 시작점으로 만들어보세요.",
                "harmonize": "놀라움과 안정감 사이의 균형을 찾아보겠습니다.",
            },
            "neutral": {
                "adapt": "평온한 마음으로 상황 변화에 적응해보겠습니다.",
                "confront": "차분한 상태에서 문제를 해결해보겠습니다.",
                "retreat": "평정심을 유지하며 잠시 물러나 관찰해보세요.",
                "analyze": "중립적 관점에서 상황을 객관적으로 분석해보겠습니다.",
                "initiate": "안정된 마음으로 새로운 변화를 주도해보세요.",
                "harmonize": "이미 균형잡힌 상태에서 더 나은 조화를 추구해보겠습니다.",
            },
        }

        # Insight 생성 (핵심 통찰)
        insight_templates = {
            "adapt": f"지금은 {emotion_info['korean']}을 유지하며 적응 전략을 펼칠 수 있는 시점입니다.",
            "confront": f"{emotion_info['korean']} 상태에서 직면 전략이 가장 효과적일 것 같습니다.",
            "retreat": f"{emotion_info['korean']}을 느끼는 지금, 잠시 후퇴하며 재정비하는 것이 현명합니다.",
            "analyze": f"{emotion_info['korean']} 속에서 상황을 깊이 분석해볼 필요가 있습니다.",
            "initiate": f"{emotion_info['korean']}의 에너지로 주도적 전략을 펼칠 수 있습니다.",
            "harmonize": f"{emotion_info['korean']}과 조화하며 균형잡힌 접근이 필요합니다.",
        }

        # Tactics 생성 (구체적 행동 지침)
        tactics_templates = {
            "adapt": f"이 {emotion_info['korean']}을 유지하면서 주변 변화에 유연하게 대응해보세요.",
            "confront": f"{emotion_info['korean']}의 힘으로 문제에 정면으로 맞서보겠습니다.",
            "retreat": f"{emotion_info['korean']}을 인정하며 잠시 거리를 두고 상황을 재평가해보세요.",
            "analyze": f"{emotion_info['korean']} 상태에서 차근차근 원인과 해결책을 찾아보겠습니다.",
            "initiate": f"{emotion_info['korean']}을 동력 삼아 적극적으로 변화를 만들어보세요.",
            "harmonize": f"{emotion_info['korean']}과 다른 요소들 간의 균형점을 찾아 조화를 이뤄보겠습니다.",
        }

        template_content = {
            "template_name": f"{emotion}_{strategy}",
            "category": "fist",
            "emotion": emotion,
            "strategy": strategy,
            "emotion_korean": emotion_info["korean"],
            "strategy_korean": strategy_info["korean"],
            "description": f"{emotion_info['description']} + {strategy_info['description']}",
            "frame": frame_templates[emotion][strategy],
            "insight": insight_templates[strategy],
            "strategy": strategy,
            "tactics": tactics_templates[strategy],
            "metadata": {
                "generated_by": "FIST Template Generator v1.0.0",
                "generated_at": datetime.now().isoformat(),
                "compatibility": "template_engine.py",
            },
        }

        return template_content

    def save_template(self, emotion: str, strategy: str, content: Dict[str, Any]):
        """템플릿을 YAML 파일로 저장"""

        filename = f"{emotion}_{strategy}.yaml"
        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(
                    content, f, default_flow_style=False, allow_unicode=True, indent=2
                )

            print(f"✅ {filename} 생성 완료")
            return True

        except Exception as e:
            print(f"❌ {filename} 생성 실패: {e}")
            return False

    def generate_all_templates(self) -> Dict[str, Any]:
        """모든 감정 × 전략 조합 템플릿 생성"""

        print(f"\n🚀 FIST 템플릿 자동 생성 시작...")
        print("=" * 50)

        self.create_output_directory()

        success_count = 0
        failed_count = 0
        generated_templates = []

        for emotion in self.emotions.keys():
            for strategy in self.strategies.keys():
                print(f"\n🎯 생성 중: {emotion} × {strategy}")

                # 템플릿 콘텐츠 생성
                content = self.generate_template_content(emotion, strategy)

                # 파일 저장
                if self.save_template(emotion, strategy, content):
                    success_count += 1
                    generated_templates.append(
                        {
                            "emotion": emotion,
                            "strategy": strategy,
                            "filename": f"{emotion}_{strategy}.yaml",
                            "korean_name": f"{self.emotions[emotion]['korean']}_{self.strategies[strategy]['korean']}",
                        }
                    )
                else:
                    failed_count += 1

        # 결과 요약
        total_expected = len(self.emotions) * len(self.strategies)

        print(f"\n🎉 FIST 템플릿 생성 완료!")
        print("=" * 50)
        print(f"📊 생성 결과:")
        print(f"   성공: {success_count}개")
        print(f"   실패: {failed_count}개")
        print(f"   전체: {total_expected}개")
        print(f"   성공률: {(success_count/total_expected)*100:.1f}%")

        if success_count == total_expected:
            print(f"✅ 모든 템플릿이 성공적으로 생성되었습니다!")
        elif failed_count > 0:
            print(f"⚠️ {failed_count}개 템플릿 생성에 실패했습니다.")

        print(f"\n📁 생성된 파일 위치: {self.output_dir}")

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_expected": total_expected,
            "success_rate": (success_count / total_expected) * 100,
            "output_directory": str(self.output_dir),
            "generated_templates": generated_templates,
        }

    def verify_generated_templates(self) -> Dict[str, Any]:
        """생성된 템플릿 검증"""

        print(f"\n🔍 생성된 템플릿 검증 중...")

        verification_results = {
            "files_found": 0,
            "files_valid": 0,
            "files_invalid": 0,
            "missing_keys": [],
            "validation_errors": [],
        }

        required_keys = [
            "template_name",
            "category",
            "emotion",
            "strategy",
            "frame",
            "insight",
            "tactics",
        ]

        for yaml_file in self.output_dir.glob("*.yaml"):
            verification_results["files_found"] += 1

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)

                # 필수 키 확인
                missing_keys = [
                    key for key in required_keys if key not in template_data
                ]

                if missing_keys:
                    verification_results["files_invalid"] += 1
                    verification_results["missing_keys"].append(
                        {"file": yaml_file.name, "missing": missing_keys}
                    )
                else:
                    verification_results["files_valid"] += 1

            except Exception as e:
                verification_results["files_invalid"] += 1
                verification_results["validation_errors"].append(
                    {"file": yaml_file.name, "error": str(e)}
                )

        print(f"📊 검증 결과:")
        print(f"   발견된 파일: {verification_results['files_found']}개")
        print(f"   유효한 파일: {verification_results['files_valid']}개")
        print(f"   무효한 파일: {verification_results['files_invalid']}개")

        if verification_results["files_invalid"] == 0:
            print(f"✅ 모든 템플릿이 유효합니다!")
        else:
            print(
                f"⚠️ {verification_results['files_invalid']}개 파일에 문제가 있습니다."
            )

            for issue in verification_results["missing_keys"]:
                print(f"   {issue['file']}: 누락된 키 {issue['missing']}")

            for error in verification_results["validation_errors"]:
                print(f"   {error['file']}: {error['error']}")

        return verification_results


def main():
    """메인 실행 함수"""

    print("🎭 FIST Template Generator 시작")
    print("=" * 60)
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 생성기 초기화
        generator = FISTTemplateGenerator()

        # 모든 템플릿 생성
        results = generator.generate_all_templates()

        # 생성된 템플릿 검증
        verification = generator.verify_generated_templates()

        # 최종 리포트
        print(f"\n📋 최종 리포트")
        print("=" * 60)

        if (
            results["success_count"] == results["total_expected"]
            and verification["files_invalid"] == 0
        ):
            print(f"🎉 FIST 템플릿 생성기 작업 완료!")
            print(f"   ✅ {results['success_count']}개 템플릿 생성 성공")
            print(f"   ✅ 모든 템플릿 검증 통과")
            print(f"   📁 위치: {results['output_directory']}")

            print(f"\n🔗 후속 작업 안내:")
            print(f"   1. template_engine.py에서 fist_autogen 디렉토리 인식 확인")
            print(f"   2. fallback 판단기에서 템플릿 로드 테스트")
            print(f"   3. 실제 판단 시나리오에서 템플릿 활용 검증")

            return True
        else:
            print(f"⚠️ 일부 작업에서 문제가 발생했습니다.")
            print(f"   생성 성공률: {results['success_rate']:.1f}%")
            print(
                f"   검증 통과율: {(verification['files_valid']/verification['files_found'])*100:.1f}%"
            )
            return False

    except Exception as e:
        print(f"❌ FIST 템플릿 생성 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
