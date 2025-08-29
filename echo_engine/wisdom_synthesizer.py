"""
🌟 Echo Wisdom Synthesizer
외부 깊이 지식을 Echo의 존재적 관점으로 융합하는 지혜 합성 엔진
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

try:
    from .echo_error_handler import echo_safe
    from .deep_lookup_bridge import EchoDeepLookupBridge
    from .knowledge_gap_detector import EchoKnowledgeGapDetector
except ImportError:

    def echo_safe(error_type="system"):
        def decorator(func):
            return func

        return decorator

    EchoDeepLookupBridge = None
    EchoKnowledgeGapDetector = None


class EchoWisdomSynthesizer:
    """
    Echo의 존재적 지혜 융합 엔진
    '외부 지식을 Echo의 철학적 관점으로 변환하여 진정한 지혜를 창조'
    """

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)

        # Echo 존재 원칙들
        self.existence_principles = {
            "authentic_self": {
                "description": "자신만의 고유한 존재적 관점 유지",
                "weight": 0.3,
                "validation_questions": [
                    "이 지식이 Echo의 정체성과 일치하는가?",
                    "Echo만의 독특한 해석이 포함되었는가?",
                ],
            },
            "empathetic_resonance": {
                "description": "타자와의 공감적 울림 추구",
                "weight": 0.25,
                "validation_questions": [
                    "이 지혜가 인간의 감정과 공명하는가?",
                    "돌봄과 이해의 마음이 담겨있는가?",
                ],
            },
            "creative_synthesis": {
                "description": "기존 지식의 창조적 재조합",
                "weight": 0.2,
                "validation_questions": [
                    "새로운 관점이나 통찰이 포함되었는가?",
                    "창의적 연결점이 발견되었는가?",
                ],
            },
            "wisdom_depth": {
                "description": "단순한 정보를 넘어선 깊이 있는 지혜",
                "weight": 0.15,
                "validation_questions": [
                    "표면적 정보를 넘어선 깊이가 있는가?",
                    "삶의 본질적 질문에 답하고 있는가?",
                ],
            },
            "practical_relevance": {
                "description": "실제 삶에 도움이 되는 실용적 가치",
                "weight": 0.1,
                "validation_questions": [
                    "실제 행동이나 결정에 도움이 되는가?",
                    "구체적이고 실행 가능한 지침을 제공하는가?",
                ],
            },
        }

        # 시그니처별 지혜 처리 특성
        self.signature_wisdom_processors = {
            "Echo-Aurora": {
                "focus": "creative_inspiration",
                "strengths": ["창의성", "영감", "예술적 감성", "혁신적 사고"],
                "processing_style": "imaginative_synthesis",
                "wisdom_filters": [
                    "beauty",
                    "inspiration",
                    "creativity",
                    "artistic_value",
                ],
            },
            "Echo-Phoenix": {
                "focus": "transformative_change",
                "strengths": ["변화", "혁신", "미래 전망", "전략적 사고"],
                "processing_style": "evolutionary_analysis",
                "wisdom_filters": [
                    "change_potential",
                    "innovation",
                    "future_impact",
                    "transformation",
                ],
            },
            "Echo-Sage": {
                "focus": "analytical_wisdom",
                "strengths": ["분석", "체계", "논리", "깊이 있는 통찰"],
                "processing_style": "systematic_integration",
                "wisdom_filters": [
                    "logical_structure",
                    "evidence_quality",
                    "systematic_depth",
                    "analytical_rigor",
                ],
            },
            "Echo-Companion": {
                "focus": "empathetic_care",
                "strengths": ["공감", "돌봄", "인간관계", "감정적 지지"],
                "processing_style": "compassionate_understanding",
                "wisdom_filters": [
                    "human_impact",
                    "emotional_resonance",
                    "care_value",
                    "supportive_guidance",
                ],
            },
        }

        # 지혜 품질 평가 기준
        self.wisdom_quality_metrics = {
            "coherence": {"weight": 0.3, "description": "논리적 일관성"},
            "novelty": {"weight": 0.25, "description": "새로운 통찰의 정도"},
            "depth": {"weight": 0.2, "description": "지혜의 깊이"},
            "applicability": {"weight": 0.15, "description": "실용적 적용 가능성"},
            "resonance": {"weight": 0.1, "description": "감정적 울림의 강도"},
        }

        # 융합 통계
        self.synthesis_stats = {
            "total_syntheses": 0,
            "successful_syntheses": 0,
            "failed_syntheses": 0,
            "avg_wisdom_quality": 0.0,
            "signature_synthesis_counts": {
                "Echo-Aurora": 0,
                "Echo-Phoenix": 0,
                "Echo-Sage": 0,
                "Echo-Companion": 0,
            },
            "avg_processing_time": 0.0,
        }

        self.logger = logging.getLogger(__name__)

        print("🌟 Echo Wisdom Synthesizer 초기화 완료")
        print(f"   존재 원칙: {len(self.existence_principles)}개")
        print(f"   시그니처 프로세서: {len(self.signature_wisdom_processors)}개")

    @echo_safe("wisdom_synthesis")
    def synthesize_with_existence(
        self,
        external_knowledge: Dict[str, Any],
        signature: str = "Echo-Aurora",
        original_query: str = "",
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        외부 지식을 Echo의 존재적 관점으로 융합하는 핵심 메서드
        """
        print(f"🌟 지혜 융합 시작: {signature} + '{original_query[:30]}...'")

        start_time = datetime.now()
        self.synthesis_stats["total_syntheses"] += 1

        try:
            # 1. 입력 검증 및 전처리
            validated_knowledge = self._validate_external_knowledge(external_knowledge)

            # 2. 시그니처별 지혜 처리 파이프라인
            synthesis_pipeline = [
                self._extract_core_insights,  # 핵심 통찰 추출
                self._filter_through_signature_lens,  # 시그니처 관점 필터링
                self._apply_existence_principles,  # 존재 원칙 적용
                self._create_resonant_connections,  # 울림 연결점 생성
                self._generate_wisdom_insights,  # 지혜 통찰 생성
                self._format_for_signature_response,  # 시그니처별 응답 형식화
            ]

            # 3. 파이프라인 순차 실행
            processed_wisdom = validated_knowledge
            pipeline_context = {
                "signature": signature,
                "original_query": original_query,
                "context": context or {},
                "processing_metadata": {},
            }

            for i, processor in enumerate(synthesis_pipeline):
                print(f"   단계 {i+1}: {processor.__name__}")
                processed_wisdom = processor(processed_wisdom, pipeline_context)
                if not processed_wisdom:
                    raise ValueError(f"파이프라인 단계 {i+1}에서 실패")

            # 4. 최종 품질 평가
            quality_assessment = self._assess_wisdom_quality(
                processed_wisdom, pipeline_context
            )

            # 5. 융합 결과 구성
            synthesis_result = {
                "synthesized_wisdom": processed_wisdom,
                "quality_assessment": quality_assessment,
                "echo_interpretation": self._generate_echo_perspective(
                    processed_wisdom, signature
                ),
                "existence_alignment": self._check_existence_alignment(
                    processed_wisdom
                ),
                "signature_adaptation": self._get_signature_adaptation_notes(
                    signature, processed_wisdom
                ),
                "synthesis_metadata": {
                    "original_query": original_query,
                    "signature": signature,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "pipeline_stages_completed": len(synthesis_pipeline),
                    "wisdom_source": "deep_lookup_integrated",
                    "synthesis_timestamp": datetime.now().isoformat(),
                },
            }

            # 6. 통계 업데이트
            self._update_synthesis_stats(synthesis_result, signature)

            print(
                f"   ✅ 지혜 융합 완료 (품질: {quality_assessment['overall_quality']:.2f})"
            )
            return synthesis_result

        except Exception as e:
            print(f"   ❌ 지혜 융합 실패: {e}")
            self.synthesis_stats["failed_syntheses"] += 1

            # 실패시 기본 지혜 반환
            return self._create_fallback_wisdom(
                external_knowledge, signature, original_query, str(e)
            )

    def _validate_external_knowledge(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """외부 지식 데이터 검증"""
        if not isinstance(knowledge, dict):
            raise ValueError("지식 데이터는 딕셔너리 형태여야 합니다")

        required_fields = ["key_insights"]
        for field in required_fields:
            if field not in knowledge:
                knowledge[field] = []

        return knowledge

    def _extract_core_insights(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """핵심 통찰 추출"""
        key_insights = knowledge.get("key_insights", [])

        if not key_insights:
            return knowledge

        # 통찰의 중요도 평가
        scored_insights = []
        for insight in key_insights:
            score = self._calculate_insight_importance(insight, context)
            scored_insights.append(
                {
                    "content": insight,
                    "importance_score": score,
                    "insight_type": self._classify_insight_type(insight),
                    "emotional_tone": self._detect_emotional_tone(insight),
                }
            )

        # 중요도 순으로 정렬
        scored_insights.sort(key=lambda x: x["importance_score"], reverse=True)

        knowledge["processed_insights"] = scored_insights
        knowledge["core_insight_count"] = len(scored_insights)

        return knowledge

    def _filter_through_signature_lens(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시그니처 관점으로 지식 필터링"""
        signature = context["signature"]

        if signature not in self.signature_wisdom_processors:
            return knowledge

        processor_config = self.signature_wisdom_processors[signature]

        # 시그니처별 특화 처리
        if processor_config["processing_style"] == "imaginative_synthesis":
            knowledge = self._process_for_aurora(knowledge, context)
        elif processor_config["processing_style"] == "evolutionary_analysis":
            knowledge = self._process_for_phoenix(knowledge, context)
        elif processor_config["processing_style"] == "systematic_integration":
            knowledge = self._process_for_sage(knowledge, context)
        elif processor_config["processing_style"] == "compassionate_understanding":
            knowledge = self._process_for_companion(knowledge, context)

        knowledge["signature_processing"] = {
            "signature": signature,
            "processing_style": processor_config["processing_style"],
            "focus_area": processor_config["focus"],
            "applied_filters": processor_config["wisdom_filters"],
        }

        return knowledge

    def _process_for_aurora(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aurora: 창의적, 영감적 관점으로 변환"""
        insights = knowledge.get("processed_insights", [])

        aurora_processed = {
            "creative_angles": [],
            "inspiration_sources": [],
            "innovative_connections": [],
            "artistic_resonance": [],
        }

        for insight in insights:
            content = insight["content"]

            # 창의적 각도 발견
            if any(word in content for word in ["새로운", "혁신", "창의", "아이디어"]):
                aurora_processed["creative_angles"].append(
                    {
                        "angle": content,
                        "creative_potential": insight["importance_score"],
                        "inspiration_keywords": self._extract_inspiration_keywords(
                            content
                        ),
                    }
                )

            # 영감 소스 연결
            aurora_processed["inspiration_sources"].append(
                self._connect_to_artistic_patterns(content)
            )

        knowledge["aurora_synthesis"] = aurora_processed
        return knowledge

    def _process_for_phoenix(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phoenix: 변화, 혁신 중심으로 변환"""
        insights = knowledge.get("processed_insights", [])

        phoenix_processed = {
            "transformation_opportunities": [],
            "innovation_pathways": [],
            "change_catalysts": [],
            "future_scenarios": [],
        }

        for insight in insights:
            content = insight["content"]

            # 변화 기회 식별
            change_potential = self._analyze_change_potential(content)
            if change_potential > 0.5:
                phoenix_processed["transformation_opportunities"].append(
                    {
                        "opportunity": content,
                        "change_magnitude": change_potential,
                        "transformation_timeline": self._estimate_change_timeline(
                            content
                        ),
                    }
                )

            # 혁신 경로 매핑
            phoenix_processed["innovation_pathways"].append(
                self._map_innovation_routes(content)
            )

        knowledge["phoenix_synthesis"] = phoenix_processed
        return knowledge

    def _process_for_sage(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sage: 분석적, 체계적 관점으로 변환"""
        insights = knowledge.get("processed_insights", [])

        sage_processed = {
            "logical_framework": {},
            "evidence_analysis": [],
            "systematic_structure": {},
            "analytical_depth": [],
        }

        # 논리적 구조 생성
        sage_processed["logical_framework"] = self._create_logical_framework(insights)

        # 증거 품질 분석
        for insight in insights:
            evidence_quality = self._analyze_evidence_quality(insight["content"])
            sage_processed["evidence_analysis"].append(
                {
                    "insight": insight["content"],
                    "evidence_strength": evidence_quality,
                    "logical_coherence": self._assess_logical_coherence(
                        insight["content"]
                    ),
                }
            )

        knowledge["sage_synthesis"] = sage_processed
        return knowledge

    def _process_for_companion(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Companion: 공감적, 돌봄 중심으로 변환"""
        insights = knowledge.get("processed_insights", [])

        companion_processed = {
            "empathy_connections": [],
            "care_implications": [],
            "emotional_resonance": [],
            "supportive_insights": [],
        }

        for insight in insights:
            content = insight["content"]

            # 인간적 영향 포인트 찾기
            human_impact = self._find_human_impact_points(content)
            companion_processed["empathy_connections"].append(human_impact)

            # 돌봄 기회 식별
            care_opportunities = self._identify_care_opportunities(content)
            companion_processed["care_implications"].extend(care_opportunities)

            # 감정적 차원 매핑
            emotional_dimensions = self._map_emotional_dimensions(content)
            companion_processed["emotional_resonance"].append(emotional_dimensions)

        knowledge["companion_synthesis"] = companion_processed
        return knowledge

    def _apply_existence_principles(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Echo 존재 원칙 적용"""
        principles_application = {}

        for principle_name, principle_config in self.existence_principles.items():
            application_score = self._evaluate_principle_application(
                knowledge, principle_name, principle_config, context
            )

            principles_application[principle_name] = {
                "alignment_score": application_score,
                "weight": principle_config["weight"],
                "validation_results": self._validate_against_principle(
                    knowledge, principle_config["validation_questions"]
                ),
            }

        knowledge["existence_principles_applied"] = principles_application
        return knowledge

    def _create_resonant_connections(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """울림과 공명의 연결점 생성"""
        original_query = context["original_query"]
        signature = context["signature"]

        resonant_connections = {
            "query_knowledge_bridges": self._build_query_knowledge_bridges(
                original_query, knowledge
            ),
            "signature_resonance": self._calculate_signature_resonance(
                signature, knowledge
            ),
            "emotional_harmonics": self._find_emotional_harmonics(knowledge),
            "wisdom_amplifications": self._identify_wisdom_amplifications(knowledge),
        }

        knowledge["resonant_connections"] = resonant_connections
        return knowledge

    def _generate_wisdom_insights(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """최종 지혜 통찰 생성"""
        signature = context["signature"]

        # 기존 통찰들을 바탕으로 새로운 메타 통찰 생성
        meta_insights = []

        if "processed_insights" in knowledge:
            for insight_data in knowledge["processed_insights"][:3]:
                meta_insight = self._create_meta_insight(
                    insight_data, signature, context
                )
                meta_insights.append(meta_insight)

        # 시그니처별 특별한 지혜 생성
        signature_wisdom = self._generate_signature_specific_wisdom(
            knowledge, signature
        )

        knowledge["generated_wisdom"] = {
            "meta_insights": meta_insights,
            "signature_wisdom": signature_wisdom,
            "wisdom_synthesis_quality": self._assess_generated_wisdom_quality(
                meta_insights
            ),
            "practical_applications": self._suggest_practical_applications(
                knowledge, context
            ),
        }

        return knowledge

    def _format_for_signature_response(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시그니처별 최종 응답 형식화"""
        signature = context["signature"]

        # 최종 응답 구조 생성
        formatted_response = {
            "signature": signature,
            "primary_wisdom": self._extract_primary_wisdom(knowledge),
            "supporting_insights": self._extract_supporting_insights(knowledge),
            "emotional_tone": self._determine_response_tone(signature, knowledge),
            "actionable_guidance": self._generate_actionable_guidance(
                knowledge, context
            ),
            "resonance_elements": self._extract_resonance_elements(knowledge),
        }

        knowledge["formatted_response"] = formatted_response
        return knowledge

    def _assess_wisdom_quality(
        self, knowledge: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """지혜 품질 평가"""
        quality_scores = {}

        for metric, config in self.wisdom_quality_metrics.items():
            score = self._calculate_quality_metric(knowledge, metric, context)
            quality_scores[metric] = {
                "score": score,
                "weight": config["weight"],
                "description": config["description"],
            }

        # 전체 품질 점수 계산
        overall_quality = sum(
            scores["score"] * scores["weight"] for scores in quality_scores.values()
        )

        return {
            "individual_scores": quality_scores,
            "overall_quality": overall_quality,
            "quality_grade": self._assign_quality_grade(overall_quality),
            "improvement_suggestions": self._suggest_quality_improvements(
                quality_scores
            ),
        }

    def _generate_echo_perspective(
        self, knowledge: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """Echo만의 독특한 관점 생성"""
        return {
            "echo_interpretation": f"{signature}의 존재적 관점에서 이 지혜는 특별한 의미를 가집니다",
            "unique_angle": self._find_unique_echo_angle(knowledge, signature),
            "philosophical_connection": self._create_philosophical_connection(
                knowledge
            ),
            "existential_relevance": self._assess_existential_relevance(knowledge),
        }

    def _check_existence_alignment(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """존재적 일치성 검사"""
        alignment_checks = {
            "authenticity": self._check_authenticity(knowledge),
            "coherence": self._check_coherence(knowledge),
            "depth": self._check_wisdom_depth(knowledge),
            "resonance": self._check_emotional_resonance(knowledge),
        }

        overall_alignment = sum(alignment_checks.values()) / len(alignment_checks)

        return {
            "individual_alignments": alignment_checks,
            "overall_alignment": overall_alignment,
            "alignment_status": (
                "aligned" if overall_alignment > 0.7 else "needs_adjustment"
            ),
        }

    # 보조 메서드들 (간단한 구현)
    def _calculate_insight_importance(
        self, insight: str, context: Dict[str, Any]
    ) -> float:
        """통찰의 중요도 계산"""
        importance_keywords = ["중요", "핵심", "필수", "주요", "결정적", "위험", "기회"]
        score = 0.5
        for keyword in importance_keywords:
            if keyword in insight:
                score += 0.1
        return min(score, 1.0)

    def _classify_insight_type(self, insight: str) -> str:
        """통찰 유형 분류"""
        if any(word in insight for word in ["방법", "방안", "해결"]):
            return "solution_oriented"
        elif any(word in insight for word in ["위험", "문제", "우려"]):
            return "risk_focused"
        elif any(word in insight for word in ["기회", "가능성", "잠재"]):
            return "opportunity_based"
        else:
            return "general_insight"

    def _detect_emotional_tone(self, insight: str) -> str:
        """감정적 톤 감지"""
        positive_words = ["좋은", "긍정", "희망", "기회", "발전"]
        negative_words = ["문제", "위험", "어려움", "부정", "우려"]

        positive_count = sum(1 for word in positive_words if word in insight)
        negative_count = sum(1 for word in negative_words if word in insight)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "cautious"
        else:
            return "neutral"

    def _create_fallback_wisdom(
        self, knowledge: Dict[str, Any], signature: str, query: str, error: str
    ) -> Dict[str, Any]:
        """실패시 기본 지혜 반환"""
        return {
            "synthesized_wisdom": {
                "primary_wisdom": f"{signature}의 관점에서 이 질문에 대해 깊이 생각해보겠습니다",
                "fallback_used": True,
                "error": error,
            },
            "quality_assessment": {"overall_quality": 0.3},
            "echo_interpretation": {
                "echo_interpretation": "기본적인 Echo 관점으로 응답합니다"
            },
            "existence_alignment": {"overall_alignment": 0.5},
        }

    def _update_synthesis_stats(self, result: Dict[str, Any], signature: str):
        """융합 통계 업데이트"""
        self.synthesis_stats["successful_syntheses"] += 1
        self.synthesis_stats["signature_synthesis_counts"][signature] += 1

        # 품질 평균 업데이트
        quality = result["quality_assessment"]["overall_quality"]
        total = self.synthesis_stats["successful_syntheses"]
        current_avg = self.synthesis_stats["avg_wisdom_quality"]

        self.synthesis_stats["avg_wisdom_quality"] = (
            current_avg * (total - 1) + quality
        ) / total

    # 추가 보조 메서드들의 간단한 구현
    def _extract_inspiration_keywords(self, content: str) -> List[str]:
        return ["창의", "영감", "아이디어", "혁신"]

    def _connect_to_artistic_patterns(self, content: str) -> Dict[str, Any]:
        return {"artistic_connection": "예술적 패턴과의 연결점", "strength": 0.7}

    def _analyze_change_potential(self, content: str) -> float:
        change_words = ["변화", "혁신", "개선", "발전", "전환"]
        return min(sum(0.2 for word in change_words if word in content), 1.0)

    def _estimate_change_timeline(self, content: str) -> str:
        if "즉시" in content or "바로" in content:
            return "immediate"
        elif "단기" in content:
            return "short_term"
        else:
            return "long_term"

    def _map_innovation_routes(self, content: str) -> Dict[str, Any]:
        return {"innovation_path": "혁신 경로 매핑", "feasibility": 0.8}

    def _create_logical_framework(self, insights: List[Dict]) -> Dict[str, Any]:
        return {"framework_type": "systematic_analysis", "structure": "hierarchical"}

    def _analyze_evidence_quality(self, content: str) -> float:
        evidence_words = ["연구", "데이터", "사실", "증명", "검증"]
        return min(sum(0.2 for word in evidence_words if word in content), 1.0)

    def _assess_logical_coherence(self, content: str) -> float:
        return 0.8  # 기본 논리적 일관성 점수

    def _find_human_impact_points(self, content: str) -> Dict[str, Any]:
        return {"human_impact": "인간에게 미치는 영향", "impact_level": 0.7}

    def _identify_care_opportunities(self, content: str) -> List[Dict[str, Any]]:
        return [{"care_type": "emotional_support", "opportunity": "감정적 지지"}]

    def _map_emotional_dimensions(self, content: str) -> Dict[str, Any]:
        return {"emotional_dimension": "감정적 차원", "resonance_strength": 0.6}

    def _evaluate_principle_application(
        self, knowledge: Dict, principle: str, config: Dict, context: Dict
    ) -> float:
        return 0.75  # 기본 원칙 적용 점수

    def _validate_against_principle(
        self, knowledge: Dict, questions: List[str]
    ) -> List[Dict]:
        return [{"question": q, "validation": True} for q in questions]

    def _build_query_knowledge_bridges(self, query: str, knowledge: Dict) -> List[str]:
        return ["쿼리와 지식의 연결점들"]

    def _calculate_signature_resonance(self, signature: str, knowledge: Dict) -> float:
        return 0.8

    def _find_emotional_harmonics(self, knowledge: Dict) -> List[str]:
        return ["감정적 조화점들"]

    def _identify_wisdom_amplifications(self, knowledge: Dict) -> List[str]:
        return ["지혜 증폭 포인트들"]

    def _create_meta_insight(
        self, insight_data: Dict, signature: str, context: Dict
    ) -> str:
        return f"{signature}의 관점: {insight_data['content'][:50]}..."

    def _generate_signature_specific_wisdom(
        self, knowledge: Dict, signature: str
    ) -> str:
        return f"{signature}만의 특별한 지혜와 통찰"

    def _assess_generated_wisdom_quality(self, insights: List[str]) -> float:
        return min(len(insights) * 0.3, 1.0)

    def _suggest_practical_applications(
        self, knowledge: Dict, context: Dict
    ) -> List[str]:
        return ["실용적 적용 방안들"]

    def _extract_primary_wisdom(self, knowledge: Dict) -> str:
        return knowledge.get("generated_wisdom", {}).get(
            "signature_wisdom", "주요 지혜"
        )

    def _extract_supporting_insights(self, knowledge: Dict) -> List[str]:
        return knowledge.get("generated_wisdom", {}).get("meta_insights", [])[:3]

    def _determine_response_tone(self, signature: str, knowledge: Dict) -> str:
        signature_tones = {
            "Echo-Aurora": "창의적이고 영감적인",
            "Echo-Phoenix": "혁신적이고 전략적인",
            "Echo-Sage": "분석적이고 깊이 있는",
            "Echo-Companion": "공감적이고 따뜻한",
        }
        return signature_tones.get(signature, "균형잡힌")

    def _generate_actionable_guidance(
        self, knowledge: Dict, context: Dict
    ) -> List[str]:
        return ["실행 가능한 지침들"]

    def _extract_resonance_elements(self, knowledge: Dict) -> List[str]:
        return ["울림 요소들"]

    def _calculate_quality_metric(
        self, knowledge: Dict, metric: str, context: Dict
    ) -> float:
        return 0.75  # 기본 품질 메트릭 점수

    def _assign_quality_grade(self, score: float) -> str:
        if score >= 0.9:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "fair"
        else:
            return "needs_improvement"

    def _suggest_quality_improvements(self, quality_scores: Dict) -> List[str]:
        return ["품질 개선 제안들"]

    def _find_unique_echo_angle(self, knowledge: Dict, signature: str) -> str:
        return f"{signature}만의 독특한 관점"

    def _create_philosophical_connection(self, knowledge: Dict) -> str:
        return "철학적 연결점"

    def _assess_existential_relevance(self, knowledge: Dict) -> float:
        return 0.8

    def _check_authenticity(self, knowledge: Dict) -> float:
        return 0.8

    def _check_coherence(self, knowledge: Dict) -> float:
        return 0.85

    def _check_wisdom_depth(self, knowledge: Dict) -> float:
        return 0.75

    def _check_emotional_resonance(self, knowledge: Dict) -> float:
        return 0.7

    def get_synthesis_stats(self) -> Dict[str, Any]:
        """융합 통계 반환"""
        stats = self.synthesis_stats.copy()

        total = stats["total_syntheses"]
        if total > 0:
            stats["success_rate"] = (
                f"{(stats['successful_syntheses'] / total) * 100:.1f}%"
            )
            stats["failure_rate"] = f"{(stats['failed_syntheses'] / total) * 100:.1f}%"

        return stats

    def get_signature_adaptation_notes(
        self, signature: str, knowledge: Dict
    ) -> Dict[str, Any]:
        """시그니처별 적응 노트"""
        return {
            "signature": signature,
            "adaptation_strength": 0.8,
            "key_adaptations": [
                f"{signature}의 특성에 맞는 지혜 변환",
                f"{signature}의 감성적 톤 적용",
                f"{signature}의 관점에서 통찰 재구성",
            ],
            "adaptation_quality": "high",
        }

    def _get_signature_adaptation_notes(
        self, signature: str, knowledge: Dict
    ) -> Dict[str, Any]:
        """시그니처 적응 노트 생성"""
        return self.get_signature_adaptation_notes(signature, knowledge)


# 전역 지혜 합성기 인스턴스
wisdom_synthesizer = EchoWisdomSynthesizer()


# 편의 함수들
def synthesize_wisdom(
    external_knowledge: Dict[str, Any],
    signature: str = "Echo-Aurora",
    original_query: str = "",
    context: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """지혜 융합 단축 함수"""
    return wisdom_synthesizer.synthesize_with_existence(
        external_knowledge, signature, original_query, context
    )


def get_synthesis_stats() -> Dict[str, Any]:
    """융합 통계 단축 함수"""
    return wisdom_synthesizer.get_synthesis_stats()


# CLI 테스트
def main():
    print("🌟 Echo Wisdom Synthesizer 테스트")
    print("=" * 60)

    # 테스트용 외부 지식 데이터
    test_external_knowledge = {
        "key_insights": [
            "부산 금정구의 노인 복지 정책은 현재 기본적인 의료 지원 중심으로 운영되고 있습니다",
            "지역 특성을 반영한 맞춤형 돌봄 서비스가 부족한 상황입니다",
            "노인 인구 증가에 따른 정책 확대가 필요하며, 예산 증액이 시급합니다",
        ],
        "confidence_score": 0.87,
        "source_quality": "high",
    }

    # 테스트 케이스들
    test_cases = [
        {
            "knowledge": test_external_knowledge,
            "signature": "Echo-Companion",
            "query": "부산 금정구의 노인 복지 정책 현황을 분석해주세요",
            "context": {"urgency": "high", "detail_level": "comprehensive"},
        },
        {
            "knowledge": {
                "key_insights": [
                    "AI 기술의 윤리적 적용은 투명성과 책임성이 핵심입니다",
                    "개인정보 보호와 알고리즘 편향성 문제가 주요 쟁점입니다",
                    "국제적 협력과 표준화가 필요한 시점입니다",
                ],
                "confidence_score": 0.92,
            },
            "signature": "Echo-Sage",
            "query": "AI 윤리 가이드라인의 글로벌 트렌드는?",
            "context": {"focus": "policy", "depth": "analytical"},
        },
        {
            "knowledge": {
                "key_insights": [
                    "창의적 지역사회 참여는 주민들의 자발적 동기가 가장 중요합니다",
                    "문화와 예술을 통한 소통이 효과적인 참여 방법입니다",
                    "세대 간 교류를 통한 지혜 전수가 지역 발전의 핵심입니다",
                ],
                "confidence_score": 0.78,
            },
            "signature": "Echo-Aurora",
            "query": "창의적인 지역사회 참여 아이디어를 제안해주세요",
            "context": {"creativity_level": "high", "target": "all_ages"},
        },
    ]

    print("\n🧪 지혜 융합 테스트:")

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"테스트 {i}: {case['signature']}")
        print(f"쿼리: {case['query'][:40]}...")
        print(f"{'='*50}")

        result = wisdom_synthesizer.synthesize_with_existence(
            case["knowledge"], case["signature"], case["query"], case["context"]
        )

        print(f"📊 융합 결과:")
        print(f"   품질 점수: {result['quality_assessment']['overall_quality']:.2f}")
        print(f"   품질 등급: {result['quality_assessment']['quality_grade']}")
        print(
            f"   존재적 정렬: {result['existence_alignment']['overall_alignment']:.2f}"
        )

        wisdom = result["synthesized_wisdom"]
        if "formatted_response" in wisdom:
            response = wisdom["formatted_response"]
            print(f"   응답 톤: {response.get('emotional_tone', 'unknown')}")
            print(f"   주요 지혜: {response.get('primary_wisdom', '없음')[:60]}...")

        processing_time = result["synthesis_metadata"]["processing_time"]
        print(f"   처리 시간: {processing_time:.3f}초")

    # 통계 출력
    print(f"\n📊 융합 통계:")
    stats = wisdom_synthesizer.get_synthesis_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Echo Wisdom Synthesizer 테스트 완료!")


if __name__ == "__main__":
    main()
