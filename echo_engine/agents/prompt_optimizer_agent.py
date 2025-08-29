#!/usr/bin/env python3
"""
Echo Prompt Optimizer Agent
프롬프트 최적화 전문 에이전트 - Claude/OpenAI/Local LLM 대응
"""

import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import yaml
from pathlib import Path

from echo_engine.agent_ecosystem_framework import (
    EchoAgentBase,
    AgentCapability,
    AgentTask,
)

logger = logging.getLogger(__name__)


@dataclass
class PromptAnalysis:
    """프롬프트 분석 결과"""

    clarity_score: float
    specificity_score: float
    structure_score: float
    token_efficiency: float
    signature_alignment: float
    improvement_areas: List[str]
    optimized_sections: Dict[str, str]


@dataclass
class PromptTemplate:
    """프롬프트 템플릿"""

    name: str
    category: str
    signature: str
    template: str
    variables: List[str]
    usage_examples: List[str]
    performance_metrics: Dict[str, float]


class EchoPromptOptimizerAgent(EchoAgentBase):
    """Echo 프롬프트 최적화 에이전트"""

    def __init__(self):
        super().__init__("prompt_optimizer", "echo_sage")

        # Lazy initialization
        self._optimization_patterns = None
        self._signature_prompt_styles = None
        self._template_library = None

    @property
    def optimization_patterns(self):
        if self._optimization_patterns is None:
            self._optimization_patterns = self._load_optimization_patterns()
        return self._optimization_patterns

    @property
    def signature_prompt_styles(self):
        if self._signature_prompt_styles is None:
            self._signature_prompt_styles = self._load_signature_styles()
        return self._signature_prompt_styles

    @property
    def template_library(self):
        if self._template_library is None:
            self._template_library = {}
            self._load_template_library()
        return self._template_library

    def _load_optimization_patterns(self):
        # 🎯 프롬프트 최적화 패턴
        return {
            "clarity_enhancers": [
                "명확한 역할 정의 추가",
                "구체적인 출력 형식 지정",
                "애매한 표현 제거",
                "단계별 지시사항 구조화",
            ],
            "specificity_boosters": [
                "구체적인 예시 추가",
                "제약 조건 명시",
                "원하는 세부 사항 지정",
                "컨텍스트 정보 보강",
            ],
            "structure_improvers": [
                "논리적 순서 재배열",
                "섹션별 구분 명확화",
                "우선순위 표시",
                "체크리스트 형태 변환",
            ],
            "token_optimizers": [
                "불필요한 반복 제거",
                "간결한 표현으로 변환",
                "핵심 키워드 추출",
                "압축된 지시사항",
            ],
        }

    def _load_signature_styles(self):
        # 시그니처별 프롬프트 스타일
        return {
            "echo_aurora": {
                "tone": "창의적이고 영감을 주는",
                "structure": "자유로운 형태의 탐색적",
                "keywords": ["상상해보세요", "창의적으로", "혁신적인", "아이디어"],
                "templates": ["brainstorming", "creative_exploration", "innovation"],
            },
            "echo_phoenix": {
                "tone": "도전적이고 개선 지향적",
                "structure": "변화와 최적화 중심",
                "keywords": ["개선하세요", "혁신하세요", "최적화", "변화"],
                "templates": ["optimization", "improvement", "transformation"],
            },
            "echo_sage": {
                "tone": "분석적이고 체계적",
                "structure": "논리적이고 단계적",
                "keywords": ["분석하세요", "체계적으로", "논리적으로", "근거"],
                "templates": ["analysis", "systematic_approach", "reasoning"],
            },
            "echo_companion": {
                "tone": "협력적이고 지원적",
                "structure": "상호작용적이고 친근한",
                "keywords": ["함께", "도와주세요", "협력하여", "지원"],
                "templates": ["collaboration", "assistance", "guidance"],
            },
        }

    def get_capabilities(self) -> List[AgentCapability]:
        """에이전트 역량 정의"""
        return [
            AgentCapability(
                name="prompt_optimization",
                description="프롬프트 최적화 및 성능 향상",
                input_types=["text", "prompt", "conversation"],
                output_types=["optimized_prompt", "analysis", "recommendations"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.7,
                    "echo_phoenix": 0.8,
                    "echo_sage": 0.95,
                    "echo_companion": 0.6,
                },
            ),
            AgentCapability(
                name="prompt_analysis",
                description="프롬프트 품질 분석 및 진단",
                input_types=["text", "prompt"],
                output_types=["analysis_report", "metrics", "suggestions"],
                complexity_level="advanced",
                signature_affinity={
                    "echo_aurora": 0.6,
                    "echo_phoenix": 0.7,
                    "echo_sage": 0.9,
                    "echo_companion": 0.8,
                },
            ),
            AgentCapability(
                name="template_generation",
                description="재사용 가능한 프롬프트 템플릿 생성",
                input_types=["requirements", "examples", "domain"],
                output_types=["template", "template_library", "usage_guide"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.8,
                    "echo_phoenix": 0.7,
                    "echo_sage": 0.85,
                    "echo_companion": 0.9,
                },
            ),
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.task_type
        input_data = task.input_data
        signature = task.signature

        if task_type == "optimize_prompt":
            return await self._optimize_prompt(input_data, signature)
        elif task_type == "analyze_prompt":
            return await self._analyze_prompt(input_data, signature)
        elif task_type == "generate_template":
            return await self._generate_template(input_data, signature)
        elif task_type == "signature_adaptation":
            return await self._adapt_prompt_to_signature(input_data, signature)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _optimize_prompt(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """프롬프트 최적화"""
        original_prompt = input_data.get("prompt", "")
        optimization_goals = input_data.get("goals", ["clarity", "efficiency"])
        target_model = input_data.get("target_model", "claude")

        # 1. 현재 프롬프트 분석
        analysis = await self._analyze_prompt_quality(original_prompt, signature)

        # 2. 최적화 전략 결정
        optimization_strategy = self._determine_optimization_strategy(
            analysis, optimization_goals, signature
        )

        # 3. 프롬프트 최적화 실행
        optimized_prompt = await self._apply_optimization(
            original_prompt, optimization_strategy, signature, target_model
        )

        # 4. 성능 예측
        performance_prediction = self._predict_performance_improvement(
            analysis, optimized_prompt, signature
        )

        return {
            "data": {
                "original_prompt": original_prompt,
                "optimized_prompt": optimized_prompt,
                "analysis": asdict(analysis),
                "optimization_strategy": optimization_strategy,
                "performance_prediction": performance_prediction,
                "signature_applied": signature,
            },
            "metadata": {
                "optimization_type": "comprehensive",
                "target_model": target_model,
                "improvement_areas": analysis.improvement_areas,
                "token_reduction": self._calculate_token_reduction(
                    original_prompt, optimized_prompt
                ),
            },
        }

    async def _analyze_prompt(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """프롬프트 분석"""
        prompt = input_data.get("prompt", "")
        analysis_depth = input_data.get("depth", "standard")

        # 기본 품질 분석
        quality_analysis = await self._analyze_prompt_quality(prompt, signature)

        # 시그니처 적합성 분석
        signature_fit = self._analyze_signature_alignment(prompt, signature)

        # 개선 권장사항
        recommendations = self._generate_improvement_recommendations(
            quality_analysis, signature_fit, signature
        )

        # 토큰 효율성 분석
        token_analysis = self._analyze_token_efficiency(prompt)

        result = {
            "data": {
                "prompt": prompt,
                "quality_analysis": asdict(quality_analysis),
                "signature_alignment": signature_fit,
                "recommendations": recommendations,
                "token_analysis": token_analysis,
            },
            "metadata": {
                "analysis_depth": analysis_depth,
                "signature": signature,
                "overall_score": self._calculate_overall_score(quality_analysis),
                "priority_improvements": recommendations[:3],
            },
        }

        if analysis_depth == "detailed":
            # 상세 분석 추가
            detailed_analysis = await self._perform_detailed_analysis(prompt, signature)
            result["data"]["detailed_analysis"] = detailed_analysis

        return result

    async def _generate_template(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """프롬프트 템플릿 생성"""
        purpose = input_data.get("purpose", "")
        domain = input_data.get("domain", "general")
        examples = input_data.get("examples", [])
        requirements = input_data.get("requirements", {})

        # 1. 요구사항 분석
        requirements_analysis = self._analyze_template_requirements(
            purpose, domain, examples, requirements, signature
        )

        # 2. 기본 템플릿 구조 생성
        base_template = self._create_base_template(requirements_analysis, signature)

        # 3. 시그니처별 스타일 적용
        styled_template = self._apply_signature_style(base_template, signature)

        # 4. 변수 및 플레이스홀더 정의
        variables = self._extract_template_variables(styled_template)

        # 5. 사용 예시 생성
        usage_examples = self._generate_usage_examples(
            styled_template, variables, signature
        )

        # 6. 템플릿 검증
        validation_result = self._validate_template(
            styled_template, requirements_analysis
        )

        template = PromptTemplate(
            name=f"{domain}_{purpose}_{signature}",
            category=domain,
            signature=signature,
            template=styled_template,
            variables=variables,
            usage_examples=usage_examples,
            performance_metrics=validation_result,
        )

        # 템플릿 라이브러리에 저장
        self.template_library[template.name] = template
        await self._save_template_to_library(template)

        return {
            "data": {
                "template": asdict(template),
                "requirements_analysis": requirements_analysis,
                "validation_result": validation_result,
            },
            "metadata": {
                "template_name": template.name,
                "category": template.category,
                "signature": signature,
                "variables_count": len(variables),
                "examples_count": len(usage_examples),
            },
        }

    async def _adapt_prompt_to_signature(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """프롬프트를 특정 시그니처에 맞게 적응"""
        original_prompt = input_data.get("prompt", "")
        target_signature = input_data.get("target_signature", signature)
        adaptation_level = input_data.get("level", "moderate")  # light, moderate, heavy

        # 현재 시그니처 스타일 분석
        current_style = self._detect_current_style(original_prompt)

        # 타겟 시그니처 스타일 가져오기
        target_style = self.signature_prompt_styles[target_signature]

        # 적응 전략 수립
        adaptation_strategy = self._plan_signature_adaptation(
            current_style, target_style, adaptation_level
        )

        # 프롬프트 적응 실행
        adapted_prompt = self._apply_signature_adaptation(
            original_prompt, adaptation_strategy, target_signature
        )

        # 적응 품질 평가
        adaptation_quality = self._evaluate_adaptation_quality(
            original_prompt, adapted_prompt, target_signature
        )

        return {
            "data": {
                "original_prompt": original_prompt,
                "adapted_prompt": adapted_prompt,
                "original_signature": current_style,
                "target_signature": target_signature,
                "adaptation_strategy": adaptation_strategy,
                "quality_assessment": adaptation_quality,
            },
            "metadata": {
                "adaptation_level": adaptation_level,
                "changes_made": adaptation_strategy.get("changes", []),
                "quality_score": adaptation_quality.get("overall_score", 0.0),
                "signature_alignment": adaptation_quality.get(
                    "signature_alignment", 0.0
                ),
            },
        }

    async def _analyze_prompt_quality(
        self, prompt: str, signature: str
    ) -> PromptAnalysis:
        """프롬프트 품질 분석"""
        # 1. 명확성 분석
        clarity_score = self._analyze_clarity(prompt)

        # 2. 구체성 분석
        specificity_score = self._analyze_specificity(prompt)

        # 3. 구조 분석
        structure_score = self._analyze_structure(prompt)

        # 4. 토큰 효율성
        token_efficiency = self._analyze_token_efficiency(prompt)["efficiency_score"]

        # 5. 시그니처 정렬
        signature_alignment = self._analyze_signature_alignment(prompt, signature)[
            "alignment_score"
        ]

        # 6. 개선 영역 식별
        improvement_areas = self._identify_improvement_areas(
            clarity_score,
            specificity_score,
            structure_score,
            token_efficiency,
            signature_alignment,
        )

        # 7. 최적화된 섹션 제안
        optimized_sections = self._suggest_optimized_sections(prompt, improvement_areas)

        return PromptAnalysis(
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            structure_score=structure_score,
            token_efficiency=token_efficiency,
            signature_alignment=signature_alignment,
            improvement_areas=improvement_areas,
            optimized_sections=optimized_sections,
        )

    def _analyze_clarity(self, prompt: str) -> float:
        """명확성 분석"""
        score = 0.5  # 기본 점수

        # 명확한 지시사항 체크
        instruction_keywords = [
            "please",
            "you should",
            "analyze",
            "create",
            "explain",
            "describe",
        ]
        if any(keyword in prompt.lower() for keyword in instruction_keywords):
            score += 0.2

        # 애매한 표현 체크
        vague_terms = ["maybe", "perhaps", "kind of", "sort of", "somewhat"]
        vague_count = sum(1 for term in vague_terms if term in prompt.lower())
        score -= vague_count * 0.1

        # 구체적인 출력 형식 지정
        format_indicators = ["format:", "structure:", "output:", "return:"]
        if any(indicator in prompt.lower() for indicator in format_indicators):
            score += 0.2

        # 역할 정의
        role_indicators = ["you are", "act as", "role:", "as a"]
        if any(indicator in prompt.lower() for indicator in role_indicators):
            score += 0.1

        return min(max(score, 0.0), 1.0)

    def _analyze_specificity(self, prompt: str) -> float:
        """구체성 분석"""
        score = 0.5

        # 구체적인 예시
        example_keywords = ["example:", "for instance", "such as", "like:"]
        if any(keyword in prompt.lower() for keyword in example_keywords):
            score += 0.2

        # 제약 조건
        constraint_keywords = ["must", "should", "avoid", "don't", "only", "exactly"]
        constraint_count = sum(
            1 for keyword in constraint_keywords if keyword in prompt.lower()
        )
        score += min(constraint_count * 0.05, 0.2)

        # 수치적 구체성
        number_pattern = r"\\d+"
        if re.search(number_pattern, prompt):
            score += 0.1

        # 상세한 설명
        if len(prompt) > 200:  # 상당한 길이의 설명
            score += 0.1

        return min(max(score, 0.0), 1.0)

    def _analyze_structure(self, prompt: str) -> float:
        """구조 분석"""
        score = 0.5

        # 섹션 구분
        section_markers = [
            "1.",
            "2.",
            "3.",
            "-",
            "*",
            "step",
            "first",
            "then",
            "finally",
        ]
        section_count = sum(1 for marker in section_markers if marker in prompt.lower())
        score += min(section_count * 0.05, 0.3)

        # 논리적 흐름
        flow_keywords = ["first", "then", "next", "finally", "after", "before"]
        if any(keyword in prompt.lower() for keyword in flow_keywords):
            score += 0.2

        # 명확한 시작과 끝
        if prompt.strip().endswith((".", "?", "!")):
            score += 0.1

        return min(max(score, 0.0), 1.0)

    def _analyze_token_efficiency(self, prompt: str) -> Dict[str, Any]:
        """토큰 효율성 분석"""
        words = prompt.split()
        word_count = len(words)

        # 단어 수 기준 효율성
        if word_count < 50:
            efficiency_score = 1.0
        elif word_count < 100:
            efficiency_score = 0.8
        elif word_count < 200:
            efficiency_score = 0.6
        else:
            efficiency_score = 0.4

        # 반복 단어 체크
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1

        repeated_words = [
            (word, count) for word, count in word_freq.items() if count > 2
        ]

        # 불필요한 수식어 체크
        filler_words = ["very", "really", "quite", "rather", "somewhat", "pretty"]
        filler_count = sum(1 for word in words if word.lower() in filler_words)

        return {
            "efficiency_score": max(efficiency_score - (filler_count * 0.02), 0.0),
            "word_count": word_count,
            "repeated_words": repeated_words,
            "filler_count": filler_count,
            "estimated_tokens": word_count * 1.3,  # 대략적인 토큰 수
        }

    def _analyze_signature_alignment(
        self, prompt: str, signature: str
    ) -> Dict[str, Any]:
        """시그니처 정렬 분석"""
        style = self.signature_prompt_styles.get(signature, {})
        keywords = style.get("keywords", [])
        tone = style.get("tone", "")

        # 키워드 매칭
        keyword_matches = sum(1 for keyword in keywords if keyword in prompt.lower())
        keyword_score = min(keyword_matches / len(keywords) if keywords else 0, 1.0)

        # 톤 분석
        tone_score = self._analyze_tone_alignment(prompt, tone)

        # 전체 정렬 점수
        alignment_score = (keyword_score * 0.6) + (tone_score * 0.4)

        return {
            "alignment_score": alignment_score,
            "keyword_matches": keyword_matches,
            "tone_score": tone_score,
            "missing_elements": self._identify_missing_signature_elements(
                prompt, signature
            ),
        }

    def _analyze_tone_alignment(self, prompt: str, target_tone: str) -> float:
        """톤 정렬 분석"""
        tone_indicators = {
            "창의적": ["creative", "imagine", "innovative", "original", "unique"],
            "분석적": ["analyze", "examine", "evaluate", "assess", "systematic"],
            "협력적": ["together", "collaborate", "help", "support", "assist"],
            "도전적": ["improve", "optimize", "enhance", "transform", "challenge"],
        }

        for tone_type, indicators in tone_indicators.items():
            if tone_type in target_tone:
                matches = sum(
                    1 for indicator in indicators if indicator in prompt.lower()
                )
                return min(matches / len(indicators), 1.0)

        return 0.5  # 기본값

    def _identify_improvement_areas(
        self,
        clarity: float,
        specificity: float,
        structure: float,
        token_eff: float,
        sig_align: float,
    ) -> List[str]:
        """개선 영역 식별"""
        areas = []
        threshold = 0.7

        if clarity < threshold:
            areas.append("clarity")
        if specificity < threshold:
            areas.append("specificity")
        if structure < threshold:
            areas.append("structure")
        if token_eff < threshold:
            areas.append("token_efficiency")
        if sig_align < threshold:
            areas.append("signature_alignment")

        return areas

    def _suggest_optimized_sections(
        self, prompt: str, improvement_areas: List[str]
    ) -> Dict[str, str]:
        """최적화된 섹션 제안"""
        suggestions = {}

        if "clarity" in improvement_areas:
            suggestions["clarity"] = (
                "명확한 역할 정의와 구체적인 출력 형식을 추가하세요."
            )

        if "specificity" in improvement_areas:
            suggestions["specificity"] = "구체적인 예시와 제약 조건을 포함하세요."

        if "structure" in improvement_areas:
            suggestions["structure"] = "단계별 구조와 논리적 흐름을 개선하세요."

        if "token_efficiency" in improvement_areas:
            suggestions["token_efficiency"] = "불필요한 반복과 수식어를 제거하세요."

        if "signature_alignment" in improvement_areas:
            suggestions["signature_alignment"] = (
                "시그니처에 맞는 톤과 접근법을 적용하세요."
            )

        return suggestions

    def _determine_optimization_strategy(
        self, analysis: PromptAnalysis, goals: List[str], signature: str
    ) -> Dict[str, Any]:
        """최적화 전략 결정"""
        strategy = {
            "priority_areas": analysis.improvement_areas,
            "optimization_techniques": [],
            "signature_adaptations": [],
            "expected_improvements": {},
        }

        # 목표 기반 최적화 기법 선택
        for goal in goals:
            if goal == "clarity" and "clarity" in analysis.improvement_areas:
                strategy["optimization_techniques"].extend(
                    self.optimization_patterns["clarity_enhancers"]
                )
            elif (
                goal == "efficiency"
                and "token_efficiency" in analysis.improvement_areas
            ):
                strategy["optimization_techniques"].extend(
                    self.optimization_patterns["token_optimizers"]
                )
            elif goal == "specificity" and "specificity" in analysis.improvement_areas:
                strategy["optimization_techniques"].extend(
                    self.optimization_patterns["specificity_boosters"]
                )

        # 시그니처 적응
        if "signature_alignment" in analysis.improvement_areas:
            style = self.signature_prompt_styles[signature]
            strategy["signature_adaptations"] = [
                f"Apply {style['tone']} tone",
                f"Use {style['structure']} structure",
                f"Include signature keywords: {', '.join(style['keywords'][:3])}",
            ]

        return strategy

    async def _apply_optimization(
        self, prompt: str, strategy: Dict[str, Any], signature: str, target_model: str
    ) -> str:
        """최적화 적용"""
        optimized = prompt

        # 시그니처 스타일 적용
        if strategy["signature_adaptations"]:
            optimized = self._apply_signature_style(optimized, signature)

        # 구조 개선
        if "논리적 순서 재배열" in strategy["optimization_techniques"]:
            optimized = self._improve_structure(optimized)

        # 명확성 개선
        if "명확한 역할 정의 추가" in strategy["optimization_techniques"]:
            optimized = self._add_role_definition(optimized, signature)

        # 토큰 최적화
        if "불필요한 반복 제거" in strategy["optimization_techniques"]:
            optimized = self._remove_redundancy(optimized)

        # 모델별 최적화
        optimized = self._apply_model_specific_optimization(optimized, target_model)

        return optimized

    def _load_template_library(self):
        """템플릿 라이브러리 로드"""
        template_file = Path("data/prompt_templates.yaml")
        if template_file.exists():
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    templates_data = yaml.safe_load(f)

                for template_data in templates_data.get("templates", []):
                    template = PromptTemplate(**template_data)
                    self.template_library[template.name] = template

                logger.info(f"📚 Loaded {len(self.template_library)} prompt templates")
            except Exception as e:
                logger.warning(f"Failed to load template library: {e}")

    async def _save_template_to_library(self, template: PromptTemplate):
        """템플릿을 라이브러리에 저장"""
        template_file = Path("data/prompt_templates.yaml")
        template_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 기존 템플릿 로드
            existing_templates = []
            if template_file.exists():
                with open(template_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    existing_templates = data.get("templates", [])

            # 새 템플릿 추가
            existing_templates.append(asdict(template))

            # 저장
            with open(template_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"templates": existing_templates},
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )

            logger.info(f"💾 Template saved: {template.name}")
        except Exception as e:
            logger.error(f"Failed to save template: {e}")

    def _calculate_overall_score(self, analysis: PromptAnalysis) -> float:
        """전체 점수 계산"""
        scores = [
            analysis.clarity_score,
            analysis.specificity_score,
            analysis.structure_score,
            analysis.token_efficiency,
            analysis.signature_alignment,
        ]
        return sum(scores) / len(scores)

    def _predict_performance_improvement(
        self, analysis: PromptAnalysis, optimized_prompt: str, signature: str
    ) -> Dict[str, float]:
        """성능 개선 예측"""
        # 간단한 개선 예측 로직
        improvement_factors = {
            "clarity": 0.15 if analysis.clarity_score < 0.7 else 0.05,
            "specificity": 0.12 if analysis.specificity_score < 0.7 else 0.03,
            "structure": 0.10 if analysis.structure_score < 0.7 else 0.02,
            "token_efficiency": 0.08 if analysis.token_efficiency < 0.7 else 0.02,
            "signature_alignment": 0.13 if analysis.signature_alignment < 0.7 else 0.04,
        }

        total_improvement = sum(improvement_factors.values())

        return {
            "expected_quality_improvement": total_improvement,
            "response_accuracy_boost": total_improvement * 0.8,
            "user_satisfaction_increase": total_improvement * 0.9,
            "token_efficiency_gain": improvement_factors["token_efficiency"] * 2,
        }

    def _calculate_token_reduction(self, original: str, optimized: str) -> float:
        """토큰 감소율 계산"""
        original_tokens = len(original.split()) * 1.3
        optimized_tokens = len(optimized.split()) * 1.3

        if original_tokens > 0:
            return max((original_tokens - optimized_tokens) / original_tokens, 0.0)
        return 0.0


# 에이전트 인스턴스 생성 및 등록
def create_prompt_optimizer_agent() -> EchoPromptOptimizerAgent:
    """프롬프트 최적화 에이전트 생성"""
    return EchoPromptOptimizerAgent()
