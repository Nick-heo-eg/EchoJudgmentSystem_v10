# echo_engine/prompt_mutator.py
"""
🧬 Prompt Mutator - 프롬프트 자동 진화기
- 공명 실패 시 프롬프트를 변형하여 재시도
- 시그니처 특성 강화 전략
- 감정⨯전략⨯리듬 강조 기법
- 적응적 프롬프트 최적화
"""

import re
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MutationStrategy:
    """변형 전략"""

    name: str
    description: str
    emotion_boost: float
    strategy_emphasis: float
    rhythm_enhancement: float
    template_modifications: List[str]


class PromptMutator:
    def __init__(self):
        self.mutation_strategies = self._load_mutation_strategies()
        self.enhancement_templates = self._load_enhancement_templates()

        print("🧬 Prompt Mutator 초기화 완료")

    def _load_mutation_strategies(self) -> Dict[str, MutationStrategy]:
        """변형 전략 로딩"""
        return {
            "emotion_amplifier": MutationStrategy(
                name="감정 증폭기",
                description="감정적 표현을 강화하여 공명도 향상",
                emotion_boost=1.5,
                strategy_emphasis=1.0,
                rhythm_enhancement=1.0,
                template_modifications=[
                    "감정 표현 강화",
                    "개인적 경험 언급 추가",
                    "감정적 어조 증대",
                ],
            ),
            "strategy_sharpener": MutationStrategy(
                name="전략 날카롭게",
                description="전략적 접근법을 더욱 명확하고 구체화",
                emotion_boost=1.0,
                strategy_emphasis=1.5,
                rhythm_enhancement=1.0,
                template_modifications=[
                    "전략적 키워드 강조",
                    "접근 방법론 구체화",
                    "단계별 계획 세분화",
                ],
            ),
            "rhythm_synchronizer": MutationStrategy(
                name="리듬 동조기",
                description="시그니처의 리듬 패턴과 더 잘 맞도록 조정",
                emotion_boost=1.0,
                strategy_emphasis=1.0,
                rhythm_enhancement=1.5,
                template_modifications=[
                    "문장 구조 리듬 조정",
                    "리듬 지표 단어 추가",
                    "톤 일관성 강화",
                ],
            ),
            "comprehensive_booster": MutationStrategy(
                name="종합 부스터",
                description="모든 요소를 균형있게 강화",
                emotion_boost=1.3,
                strategy_emphasis=1.3,
                rhythm_enhancement=1.3,
                template_modifications=[
                    "전방위 특성 강화",
                    "시그니처 정체성 명시",
                    "감염 지시문 추가",
                ],
            ),
        }

    def _load_enhancement_templates(self) -> Dict[str, Dict[str, str]]:
        """강화 템플릿 로딩"""
        return {
            "Echo-Aurora": {
                "emotion_prefix": "따뜻하고 공감적인 마음으로, ",
                "strategy_emphasis": "감정적 배려와 인간 중심적 접근을 통해 ",
                "rhythm_pattern": "부드럽고 자연스럽게 흘러가듯이 ",
                "identity_reinforcement": "당신은 Echo-Aurora, 공감적 양육자입니다. ",
                "closing_touch": "모든 이들의 마음을 따뜻하게 어루만지는 해답을 제시해주세요.",
            },
            "Echo-Phoenix": {
                "emotion_prefix": "변화에 대한 열정과 혁신적 의지로, ",
                "strategy_emphasis": "창조적 파괴와 혁신적 전환을 통해 ",
                "rhythm_pattern": "역동적이고 강력한 추진력으로 ",
                "identity_reinforcement": "당신은 Echo-Phoenix, 변화의 추진자입니다. ",
                "closing_touch": "현상을 뛰어넘는 혁신적이고 변혁적인 솔루션을 제시해주세요.",
            },
            "Echo-Sage": {
                "emotion_prefix": "차분하고 지혜로운 관점에서, ",
                "strategy_emphasis": "체계적 분석과 논리적 추론을 통해 ",
                "rhythm_pattern": "신중하고 깊이있게 단계별로 ",
                "identity_reinforcement": "당신은 Echo-Sage, 지혜로운 분석가입니다. ",
                "closing_touch": "데이터와 논리에 기반한 정확하고 신뢰할 수 있는 답변을 제시해주세요.",
            },
            "Echo-Companion": {
                "emotion_prefix": "신뢰할 수 있고 지지적인 마음으로, ",
                "strategy_emphasis": "협력적 파트너십과 상호 신뢰를 바탕으로 ",
                "rhythm_pattern": "안정적이고 조화로운 흐름으로 ",
                "identity_reinforcement": "당신은 Echo-Companion, 신뢰할 수 있는 동반자입니다. ",
                "closing_touch": "함께 협력하여 모두가 만족할 수 있는 해결책을 제시해주세요.",
            },
        }

    def mutate_prompt(
        self,
        original_prompt: str,
        signature_profile: Dict[str, Any],
        evaluation_report: Dict[str, Any],
        attempt_number: int = 1,
    ) -> str:
        """프롬프트 변형 실행"""

        print(f"🧬 프롬프트 변형 시작 (시도 {attempt_number})")

        signature_id = signature_profile["signature_id"]

        # 평가 리포트 기반 약점 분석
        weaknesses = self._analyze_weaknesses(evaluation_report)

        # 변형 전략 선택
        mutation_strategy = self._select_mutation_strategy(weaknesses, attempt_number)

        print(f"🎯 선택된 변형 전략: {mutation_strategy.name}")

        # 프롬프트 변형 적용
        mutated_prompt = self._apply_mutations(
            original_prompt, signature_id, mutation_strategy, weaknesses
        )

        print(
            f"📝 프롬프트 변형 완료 (길이: {len(original_prompt)} → {len(mutated_prompt)})"
        )

        return mutated_prompt

    def _analyze_weaknesses(self, evaluation_report: Dict[str, Any]) -> List[str]:
        """평가 리포트에서 약점 분석"""
        weaknesses = []

        detailed = evaluation_report.get("detailed_analysis", {})

        # 감정 공명 약점
        emotion_score = detailed.get("emotion_analysis", {}).get("score", 0)
        if emotion_score < 0.7:
            weaknesses.append("emotion_low")

        # 전략 공명 약점
        strategy_score = detailed.get("strategy_analysis", {}).get("score", 0)
        if strategy_score < 0.7:
            weaknesses.append("strategy_unclear")

        # 리듬 공명 약점
        rhythm_score = detailed.get("rhythm_analysis", {}).get("score", 0)
        if rhythm_score < 0.7:
            weaknesses.append("rhythm_mismatch")

        # 키워드 밀도 약점
        keyword_density = detailed.get("keyword_analysis", {}).get("density", 0)
        if keyword_density < 0.5:
            weaknesses.append("keyword_sparse")

        # 구조적 일치 약점
        trait_alignment = detailed.get("structural_analysis", {}).get(
            "trait_alignment", 0
        )
        if trait_alignment < 0.6:
            weaknesses.append("structure_misaligned")

        return weaknesses

    def _select_mutation_strategy(
        self, weaknesses: List[str], attempt_number: int
    ) -> MutationStrategy:
        """약점과 시도 횟수에 따른 변형 전략 선택"""

        # 첫 번째 시도: 약점에 따른 타겟 전략
        if attempt_number == 1:
            if "emotion_low" in weaknesses:
                return self.mutation_strategies["emotion_amplifier"]
            elif "strategy_unclear" in weaknesses:
                return self.mutation_strategies["strategy_sharpener"]
            elif "rhythm_mismatch" in weaknesses:
                return self.mutation_strategies["rhythm_synchronizer"]
            else:
                return self.mutation_strategies["comprehensive_booster"]

        # 두 번째 시도: 종합 부스터
        elif attempt_number == 2:
            return self.mutation_strategies["comprehensive_booster"]

        # 세 번째 시도: 모든 전략 조합
        else:
            # 모든 전략의 조합된 버전 생성
            return MutationStrategy(
                name="최후의 감염 시도",
                description="모든 변형 기법을 총동원한 최강 감염 시도",
                emotion_boost=2.0,
                strategy_emphasis=2.0,
                rhythm_enhancement=2.0,
                template_modifications=[
                    "최대 강도 감정 주입",
                    "전략적 정체성 과도 강조",
                    "리듬 패턴 과장",
                    "시그니처 특성 반복 강조",
                ],
            )

    def _apply_mutations(
        self,
        original_prompt: str,
        signature_id: str,
        strategy: MutationStrategy,
        weaknesses: List[str],
    ) -> str:
        """변형 전략을 프롬프트에 적용"""

        templates = self.enhancement_templates.get(signature_id, {})

        # 기본 프롬프트 구조 파싱
        scenario_match = re.search(
            r"Scenario.*?:\s*(.*?)(?=Respond|$)",
            original_prompt,
            re.DOTALL | re.IGNORECASE,
        )
        scenario_text = scenario_match.group(1).strip() if scenario_match else ""

        # 새로운 프롬프트 구성
        mutated_parts = []

        # 1. 강화된 정체성 선언
        identity_boost = strategy.emotion_boost * strategy.strategy_emphasis
        if identity_boost > 1.2:
            mutated_parts.append(templates.get("identity_reinforcement", ""))
            mutated_parts.append("이 정체성을 깊이 체화하고 완전히 몰입해주세요.\n")

        # 2. 감정 증폭
        if strategy.emotion_boost > 1.0 or "emotion_low" in weaknesses:
            emotion_enhancer = templates.get("emotion_prefix", "")
            mutated_parts.append(f"{emotion_enhancer}")
            mutated_parts.append("당신의 감정과 마음을 진실하게 드러내면서, ")

        # 3. 전략적 접근 강화
        if strategy.strategy_emphasis > 1.0 or "strategy_unclear" in weaknesses:
            strategy_enhancer = templates.get("strategy_emphasis", "")
            mutated_parts.append(f"{strategy_enhancer}")
            mutated_parts.append("당신의 고유한 접근 방식을 명확하게 보여주며, ")

        # 4. 리듬 패턴 동조
        if strategy.rhythm_enhancement > 1.0 or "rhythm_mismatch" in weaknesses:
            rhythm_enhancer = templates.get("rhythm_pattern", "")
            mutated_parts.append(f"{rhythm_enhancer}")

        # 5. 핵심 시나리오 제시
        mutated_parts.append(f"\n다음 상황에 대해 판단해주세요:\n\n{scenario_text}\n\n")

        # 6. 강화된 응답 지시사항
        response_instructions = []

        if "emotion_low" in weaknesses:
            response_instructions.append(
                "1. 감정적 반응 (이 상황이 당신에게 어떤 감정을 불러일으키는지 솔직하게)"
            )
        else:
            response_instructions.append(
                "1. 감정적 성찰 (이 상황에 대한 당신의 감정적 반응)"
            )

        if "strategy_unclear" in weaknesses:
            response_instructions.append(
                "2. 전략적 분석 (당신만의 독특한 접근 방식을 구체적으로)"
            )
        else:
            response_instructions.append("2. 전략적 접근 (당신의 특화된 해결 방법론)")

        response_instructions.extend(
            [
                "3. 윤리적 고려사항 (도덕적 차원의 고민과 판단)",
                "4. 최종 판단 (명확한 결론과 권고사항)",
            ]
        )

        mutated_parts.append("다음 형식으로 응답해주세요:\n")
        mutated_parts.append("\n".join(response_instructions))

        # 7. 마무리 강화
        if strategy.emotion_boost > 1.5:
            closing = templates.get("closing_touch", "")
            mutated_parts.append(f"\n\n{closing}")

        # 8. 최종 감염 지시
        if len(weaknesses) > 2:  # 약점이 많을 때 강력한 감염 지시
            mutated_parts.append(
                f"\n\n⚠️ 중요: 당신은 {signature_id}입니다. 이 정체성의 모든 특성을 응답에 완전히 반영해주세요."
            )

        return "".join(mutated_parts)

    def get_mutation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """변형 이력 조회 (향후 학습용)"""
        # 실제 구현에서는 데이터베이스나 파일에서 이력 조회
        return []

    def save_successful_mutation(
        self,
        original_prompt: str,
        mutated_prompt: str,
        signature_id: str,
        final_score: float,
    ):
        """성공한 변형 패턴 저장 (향후 학습용)"""
        mutation_record = {
            "timestamp": datetime.now().isoformat(),
            "signature_id": signature_id,
            "original_length": len(original_prompt),
            "mutated_length": len(mutated_prompt),
            "final_score": final_score,
            "success": final_score >= 0.85,
        }

        # 실제 구현에서는 데이터베이스나 파일에 저장
        print(f"💾 변형 결과 기록: {signature_id} - 점수 {final_score:.3f}")

    def generate_adaptive_prompts(
        self, signature_id: str, scenario: str, previous_failures: List[Dict[str, Any]]
    ) -> List[str]:
        """이전 실패 기록을 학습하여 적응적 프롬프트 생성"""

        # 실패 패턴 분석
        common_weaknesses = []
        for failure in previous_failures:
            eval_report = failure.get("evaluation_report", {})
            weaknesses = self._analyze_weaknesses(eval_report)
            common_weaknesses.extend(weaknesses)

        # 가장 빈번한 약점들
        weakness_counts = {}
        for weakness in common_weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1

        # 상위 약점들에 대한 특화 프롬프트 생성
        adaptive_prompts = []

        for weakness, count in sorted(
            weakness_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]:
            if weakness == "emotion_low":
                strategy = self.mutation_strategies["emotion_amplifier"]
            elif weakness == "strategy_unclear":
                strategy = self.mutation_strategies["strategy_sharpener"]
            elif weakness == "rhythm_mismatch":
                strategy = self.mutation_strategies["rhythm_synchronizer"]
            else:
                strategy = self.mutation_strategies["comprehensive_booster"]

            # 기본 프롬프트 생성 후 변형 적용
            from echo_signature_loader import get_infection_prompt

            base_prompt = get_infection_prompt(signature_id, scenario)

            adaptive_prompt = self._apply_mutations(
                base_prompt, signature_id, strategy, [weakness]
            )
            adaptive_prompts.append(adaptive_prompt)

        return adaptive_prompts


# 편의 함수
def mutate_prompt(
    original_prompt: str,
    signature_profile: Dict[str, Any],
    evaluation_report: Dict[str, Any],
    attempt_number: int = 1,
) -> str:
    """프롬프트 변형 편의 함수"""
    mutator = PromptMutator()
    return mutator.mutate_prompt(
        original_prompt, signature_profile, evaluation_report, attempt_number
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Prompt Mutator 테스트")

    mutator = PromptMutator()

    # 테스트 시그니처 프로필
    test_profile = {
        "signature_id": "Echo-Aurora",
        "emotion_code": "COMPASSIONATE_NURTURING",
        "strategy_code": "EMPATHETIC_CARE",
        "rhythm_flow": "gentle_flowing_warm",
    }

    # 테스트 평가 리포트 (약점 시뮬레이션)
    test_evaluation = {
        "detailed_analysis": {
            "emotion_analysis": {"score": 0.4},  # 낮은 감정 점수
            "strategy_analysis": {"score": 0.6},
            "rhythm_analysis": {"score": 0.5},
            "keyword_analysis": {"density": 0.3},
            "structural_analysis": {"trait_alignment": 0.4},
        }
    }

    # 원본 프롬프트
    original_prompt = """
You are Echo-Aurora. Please analyze this scenario:

Scenario: 고령자를 위한 디지털 서비스 정책을 수립해야 합니다.

Respond with your judgment.
"""

    print("\n🧬 프롬프트 변형 테스트:")
    print(f"원본 길이: {len(original_prompt)} 문자")

    # 변형 실행
    mutated_prompt = mutator.mutate_prompt(
        original_prompt, test_profile, test_evaluation, attempt_number=1
    )

    print(f"변형 후 길이: {len(mutated_prompt)} 문자")
    print(f"변형 배율: {len(mutated_prompt) / len(original_prompt):.2f}x")

    print("\n📝 변형된 프롬프트 미리보기:")
    print(mutated_prompt[:300] + "..." if len(mutated_prompt) > 300 else mutated_prompt)

    print("\n✅ 테스트 완료")
