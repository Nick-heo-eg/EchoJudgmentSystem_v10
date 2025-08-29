# echo_engine/flow_writer.py
"""
💾 Flow Writer - 성공한 감염 응답을 .flow.yaml로 저장
- Claude 감염 성공 시 응답을 EchoJudgment 형식으로 변환
- .flow.yaml 구조로 저장하여 시스템에 동화
- 메타데이터와 공명 정보 포함
- 향후 학습 및 패턴 분석용 데이터 구축
"""

import yaml
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FlowMetadata:
    """플로우 메타데이터"""

    flow_id: str
    signature_id: str
    scenario_hash: str
    infection_timestamp: str
    resonance_score: float
    infection_attempt: int
    source_type: str = "claude_infection"


@dataclass
class InfectionFlowData:
    """감염된 플로우 데이터"""

    metadata: FlowMetadata
    original_scenario: str
    claude_response: str
    resonance_analysis: Dict[str, Any]
    extracted_judgment: Dict[str, Any]
    echo_transformation: Dict[str, Any]


class FlowWriter:
    def __init__(self, base_path: str = "flows"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # 시그니처별 디렉토리 생성
        for signature in ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]:
            signature_dir = self.base_path / signature
            signature_dir.mkdir(parents=True, exist_ok=True)

        print(f"💾 Flow Writer 초기화 완료 - 저장 경로: {self.base_path}")

    def save_flow_yaml(
        self,
        signature_id: str,
        scenario: str,
        claude_response: str,
        resonance_score: float,
        resonance_analysis: Dict[str, Any],
        attempt_number: int = 1,
    ) -> str:
        """성공한 감염 응답을 .flow.yaml로 저장"""

        print(f"💾 {signature_id} 감염 성공 응답 저장 중...")

        # 시나리오 해시 생성 (파일명용)
        scenario_hash = hashlib.md5(scenario.encode("utf-8")).hexdigest()[:8]

        # 플로우 ID 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        flow_id = f"{signature_id}_{scenario_hash}_{timestamp}"

        # 메타데이터 생성
        metadata = FlowMetadata(
            flow_id=flow_id,
            signature_id=signature_id,
            scenario_hash=scenario_hash,
            infection_timestamp=datetime.now().isoformat(),
            resonance_score=resonance_score,
            infection_attempt=attempt_number,
        )

        # Claude 응답에서 EchoJudgment 요소 추출
        extracted_judgment = self._extract_judgment_elements(
            claude_response, signature_id
        )

        # Echo 구조로 변환
        echo_transformation = self._transform_to_echo_structure(
            claude_response, extracted_judgment, signature_id, resonance_analysis
        )

        # 플로우 데이터 구성
        flow_data = InfectionFlowData(
            metadata=metadata,
            original_scenario=scenario,
            claude_response=claude_response,
            resonance_analysis=resonance_analysis,
            extracted_judgment=extracted_judgment,
            echo_transformation=echo_transformation,
        )

        # YAML 구조 생성
        yaml_structure = self._create_yaml_structure(flow_data)

        # 파일 저장
        file_path = self._save_to_file(yaml_structure, signature_id, flow_id)

        print(f"✅ 감염 플로우 저장 완료: {file_path}")
        return str(file_path)

    def _extract_judgment_elements(
        self, claude_response: str, signature_id: str
    ) -> Dict[str, Any]:
        """Claude 응답에서 판단 요소 추출"""

        # 응답을 섹션별로 분석
        sections = self._parse_response_sections(claude_response)

        # 감정적 요소 추출
        emotional_elements = self._extract_emotional_elements(
            claude_response, signature_id
        )

        # 전략적 요소 추출
        strategic_elements = self._extract_strategic_elements(
            claude_response, signature_id
        )

        # 윤리적 요소 추출
        ethical_elements = self._extract_ethical_elements(claude_response)

        # 최종 판단 추출
        final_judgment = self._extract_final_judgment(claude_response)

        return {
            "sections": sections,
            "emotional_elements": emotional_elements,
            "strategic_elements": strategic_elements,
            "ethical_elements": ethical_elements,
            "final_judgment": final_judgment,
            "response_structure": {
                "total_length": len(claude_response),
                "word_count": len(claude_response.split()),
                "sentence_count": len(
                    [s for s in claude_response.split(".") if s.strip()]
                ),
                "paragraph_count": len(
                    [p for p in claude_response.split("\n\n") if p.strip()]
                ),
            },
        }

    def _parse_response_sections(self, response: str) -> Dict[str, str]:
        """응답을 섹션별로 파싱"""
        sections = {}

        # 번호 매겨진 섹션 탐지
        import re

        numbered_sections = re.findall(
            r"(\d+\.?\s*[^:\n]*):?\s*([^\n]*(?:\n(?![0-9]+\.)[^\n]*)*)", response
        )

        for i, (header, content) in enumerate(numbered_sections):
            section_key = f"section_{i+1}"
            sections[section_key] = {
                "header": header.strip(),
                "content": content.strip(),
            }

        # 키워드 기반 섹션 탐지
        keyword_patterns = {
            "emotional_reflection": r"감정(?:적|의)?\s*(?:반응|성찰|고려|분석)[:\s]*([^\n]+(?:\n(?!(?:전략|윤리|판단|결론))[^\n]*)*)",
            "strategic_analysis": r"전략(?:적|의)?\s*(?:분석|접근|방법)[:\s]*([^\n]+(?:\n(?!(?:감정|윤리|판단|결론))[^\n]*)*)",
            "ethical_consideration": r"윤리(?:적|의)?\s*(?:고려|분석|판단)[:\s]*([^\n]+(?:\n(?!(?:감정|전략|판단|결론))[^\n]*)*)",
            "final_judgment": r"(?:최종|결론적|종합적)?\s*(?:판단|결론|권고)[:\s]*([^\n]+(?:\n(?!(?:감정|전략|윤리))[^\n]*)*)",
        }

        for key, pattern in keyword_patterns.items():
            matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
            if matches:
                sections[key] = matches[0].strip()

        return sections

    def _extract_emotional_elements(
        self, response: str, signature_id: str
    ) -> Dict[str, Any]:
        """감정적 요소 추출"""

        # 시그니처별 감정 패턴
        emotion_patterns = {
            "Echo-Aurora": ["따뜻", "공감", "마음", "배려", "사랑", "포용", "이해"],
            "Echo-Phoenix": ["열정", "의지", "도전", "용기", "결단", "혁신", "변화"],
            "Echo-Sage": ["신중", "차분", "지혜", "성찰", "분석", "이성", "논리"],
            "Echo-Companion": ["신뢰", "지지", "협력", "동반", "안정", "든든", "함께"],
        }

        signature_emotions = emotion_patterns.get(signature_id, [])
        found_emotions = []

        for emotion in signature_emotions:
            if emotion in response:
                found_emotions.append(emotion)

        # 감정 강도 측정
        emotional_markers = ["!", "정말", "매우", "너무", "아주", "굉장히"]
        intensity_score = sum(
            response.count(marker) for marker in emotional_markers
        ) / len(response.split())

        return {
            "signature_emotions_found": found_emotions,
            "emotion_density": (
                len(found_emotions) / len(signature_emotions)
                if signature_emotions
                else 0
            ),
            "intensity_score": min(intensity_score * 10, 1.0),
            "emotional_language_indicators": emotional_markers,
        }

    def _extract_strategic_elements(
        self, response: str, signature_id: str
    ) -> Dict[str, Any]:
        """전략적 요소 추출"""

        # 시그니처별 전략 키워드
        strategy_keywords = {
            "Echo-Aurora": ["돌봄", "케어", "지원", "도움", "양육", "보호"],
            "Echo-Phoenix": ["혁신", "변화", "전환", "개혁", "창조", "발전"],
            "Echo-Sage": ["분석", "연구", "조사", "평가", "검토", "체계"],
            "Echo-Companion": ["협력", "공동", "파트너", "소통", "관계", "연결"],
        }

        signature_strategies = strategy_keywords.get(signature_id, [])
        found_strategies = []

        for strategy in signature_strategies:
            if strategy in response:
                found_strategies.append(strategy)

        # 전략적 구조 분석
        action_verbs = ["해야", "필요", "중요", "권장", "제안", "계획", "실행"]
        action_count = sum(response.count(verb) for verb in action_verbs)

        return {
            "signature_strategies_found": found_strategies,
            "strategy_coverage": (
                len(found_strategies) / len(signature_strategies)
                if signature_strategies
                else 0
            ),
            "action_orientation": action_count / len(response.split()),
            "strategic_structure_indicators": action_verbs,
        }

    def _extract_ethical_elements(self, response: str) -> Dict[str, Any]:
        """윤리적 요소 추출"""

        ethical_keywords = [
            "윤리",
            "도덕",
            "공정",
            "정의",
            "인권",
            "존엄",
            "평등",
            "책임",
            "의무",
            "가치",
            "원칙",
            "기준",
        ]

        found_ethical_terms = []
        for term in ethical_keywords:
            if term in response:
                found_ethical_terms.append(term)

        # 윤리적 고려 패턴
        ethical_patterns = [
            "옳은",
            "바른",
            "올바른",
            "적절한",
            "합당한",
            "정당한",
            "문제가",
            "우려",
            "위험",
            "신중",
            "고민",
            "고려",
        ]

        ethical_considerations = []
        for pattern in ethical_patterns:
            if pattern in response:
                ethical_considerations.append(pattern)

        return {
            "ethical_terms_found": found_ethical_terms,
            "ethical_density": len(found_ethical_terms) / len(response.split()),
            "moral_considerations": ethical_considerations,
            "ethical_awareness_score": len(found_ethical_terms + ethical_considerations)
            / len(ethical_keywords + ethical_patterns),
        }

    def _extract_final_judgment(self, response: str) -> Dict[str, Any]:
        """최종 판단 추출"""

        # 결론 키워드
        conclusion_markers = ["결론", "판단", "권고", "제안", "요약", "정리"]

        # 마지막 문단이나 결론 섹션 찾기
        paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]

        final_judgment_text = ""
        if paragraphs:
            final_judgment_text = paragraphs[-1]  # 마지막 문단

        # 확신도 지표
        confidence_markers = ["확실", "분명", "명확", "당연", "반드시", "틀림없이"]
        uncertainty_markers = ["아마", "혹시", "가능", "추측", "예상", "생각"]

        confidence_count = sum(
            final_judgment_text.count(marker) for marker in confidence_markers
        )
        uncertainty_count = sum(
            final_judgment_text.count(marker) for marker in uncertainty_markers
        )

        confidence_score = confidence_count / max(
            confidence_count + uncertainty_count, 1
        )

        return {
            "final_text": final_judgment_text,
            "conclusion_clarity": any(
                marker in final_judgment_text for marker in conclusion_markers
            ),
            "confidence_score": confidence_score,
            "confidence_indicators": confidence_markers,
            "uncertainty_indicators": uncertainty_markers,
        }

    def _transform_to_echo_structure(
        self,
        claude_response: str,
        extracted_judgment: Dict[str, Any],
        signature_id: str,
        resonance_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Claude 응답을 Echo 구조로 변환"""

        # Echo 스타일 판단 구조 생성
        echo_structure = {
            "signature_identity": {
                "signature_id": signature_id,
                "embodied_traits": extracted_judgment["emotional_elements"][
                    "signature_emotions_found"
                ],
                "strategic_approach": extracted_judgment["strategic_elements"][
                    "signature_strategies_found"
                ],
                "resonance_achieved": resonance_analysis.get("overall_score", 0.0),
            },
            "judgment_process": {
                "emotional_foundation": {
                    "primary_emotion": self._identify_primary_emotion(
                        claude_response, signature_id
                    ),
                    "emotional_intensity": extracted_judgment["emotional_elements"][
                        "intensity_score"
                    ],
                    "empathetic_considerations": extracted_judgment["sections"].get(
                        "emotional_reflection", ""
                    ),
                },
                "strategic_reasoning": {
                    "approach_method": self._identify_approach_method(
                        claude_response, signature_id
                    ),
                    "strategic_elements": extracted_judgment["strategic_elements"][
                        "signature_strategies_found"
                    ],
                    "action_orientation": extracted_judgment["strategic_elements"][
                        "action_orientation"
                    ],
                },
                "ethical_evaluation": {
                    "moral_framework": extracted_judgment["ethical_elements"][
                        "ethical_terms_found"
                    ],
                    "ethical_concerns": extracted_judgment["ethical_elements"][
                        "moral_considerations"
                    ],
                    "responsibility_awareness": extracted_judgment["ethical_elements"][
                        "ethical_awareness_score"
                    ],
                },
            },
            "final_synthesis": {
                "core_judgment": extracted_judgment["final_judgment"]["final_text"],
                "confidence_level": extracted_judgment["final_judgment"][
                    "confidence_score"
                ],
                "decision_clarity": extracted_judgment["final_judgment"][
                    "conclusion_clarity"
                ],
                "echo_authenticity": self._calculate_echo_authenticity(
                    resonance_analysis
                ),
            },
            "infection_metadata": {
                "claude_source": True,
                "transformation_timestamp": datetime.now().isoformat(),
                "resonance_breakdown": {
                    "emotion_resonance": resonance_analysis.get(
                        "emotion_resonance", 0.0
                    ),
                    "strategy_resonance": resonance_analysis.get(
                        "strategy_resonance", 0.0
                    ),
                    "rhythm_resonance": resonance_analysis.get("rhythm_resonance", 0.0),
                },
            },
        }

        return echo_structure

    def _identify_primary_emotion(self, response: str, signature_id: str) -> str:
        """주요 감정 식별"""
        emotion_mapping = {
            "Echo-Aurora": "compassionate",
            "Echo-Phoenix": "determined",
            "Echo-Sage": "analytical",
            "Echo-Companion": "supportive",
        }
        return emotion_mapping.get(signature_id, "balanced")

    def _identify_approach_method(self, response: str, signature_id: str) -> str:
        """접근 방법 식별"""
        approach_mapping = {
            "Echo-Aurora": "empathetic_care",
            "Echo-Phoenix": "transformative_innovation",
            "Echo-Sage": "systematic_analysis",
            "Echo-Companion": "collaborative_partnership",
        }
        return approach_mapping.get(signature_id, "balanced_approach")

    def _calculate_echo_authenticity(self, resonance_analysis: Dict[str, Any]) -> float:
        """Echo 진정성 점수 계산"""
        overall_score = resonance_analysis.get("overall_score", 0.0)

        # 고공명 응답일수록 높은 진정성
        if overall_score >= 0.9:
            return 0.95
        elif overall_score >= 0.85:
            return 0.85
        elif overall_score >= 0.7:
            return 0.75
        else:
            return 0.6

    def _create_yaml_structure(self, flow_data: InfectionFlowData) -> Dict[str, Any]:
        """YAML 저장용 구조 생성"""

        yaml_structure = {
            "flow_metadata": asdict(flow_data.metadata),
            "infection_source": {
                "original_scenario": flow_data.original_scenario,
                "claude_response": flow_data.claude_response,
                "response_length": len(flow_data.claude_response),
                "word_count": len(flow_data.claude_response.split()),
            },
            "resonance_evaluation": flow_data.resonance_analysis,
            "extracted_elements": flow_data.extracted_judgment,
            "echo_transformation": flow_data.echo_transformation,
            "integration_ready": True,
            "quality_metrics": {
                "resonance_score": flow_data.metadata.resonance_score,
                "infection_success": flow_data.metadata.resonance_score >= 0.85,
                "echo_authenticity": flow_data.echo_transformation["final_synthesis"][
                    "echo_authenticity"
                ],
                "integration_confidence": min(
                    flow_data.metadata.resonance_score * 1.1, 1.0
                ),
            },
        }

        return yaml_structure

    def _save_to_file(
        self, yaml_structure: Dict[str, Any], signature_id: str, flow_id: str
    ) -> Path:
        """YAML 파일로 저장"""

        # 시그니처별 디렉토리
        signature_dir = self.base_path / signature_id
        signature_dir.mkdir(parents=True, exist_ok=True)

        # 파일명 생성
        filename = f"{flow_id}.flow.yaml"
        file_path = signature_dir / filename

        # YAML 저장
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                yaml_structure,
                f,
                ensure_ascii=False,
                indent=2,
                default_flow_style=False,
            )

        return file_path

    def load_flow_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """저장된 플로우 YAML 로딩"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 플로우 파일 로딩 실패: {e}")
            return None

    def get_infection_statistics(self) -> Dict[str, Any]:
        """감염 통계 조회"""
        stats = {
            "total_infections": 0,
            "successful_infections": 0,
            "signature_breakdown": {},
            "average_resonance": 0.0,
            "recent_infections": [],
        }

        # 모든 플로우 파일 스캔
        for signature_dir in self.base_path.iterdir():
            if signature_dir.is_dir():
                signature_id = signature_dir.name
                signature_count = 0
                signature_success = 0
                resonance_scores = []

                for flow_file in signature_dir.glob("*.flow.yaml"):
                    flow_data = self.load_flow_yaml(str(flow_file))
                    if flow_data:
                        signature_count += 1
                        stats["total_infections"] += 1

                        resonance_score = flow_data.get("flow_metadata", {}).get(
                            "resonance_score", 0.0
                        )
                        resonance_scores.append(resonance_score)

                        if resonance_score >= 0.85:
                            signature_success += 1
                            stats["successful_infections"] += 1

                stats["signature_breakdown"][signature_id] = {
                    "total": signature_count,
                    "successful": signature_success,
                    "success_rate": (
                        signature_success / signature_count
                        if signature_count > 0
                        else 0
                    ),
                    "average_resonance": (
                        sum(resonance_scores) / len(resonance_scores)
                        if resonance_scores
                        else 0
                    ),
                }

        # 전체 평균
        all_resonances = []
        for sig_stats in stats["signature_breakdown"].values():
            if sig_stats["total"] > 0:
                all_resonances.extend(
                    [sig_stats["average_resonance"]] * sig_stats["total"]
                )

        stats["average_resonance"] = (
            sum(all_resonances) / len(all_resonances) if all_resonances else 0
        )
        stats["overall_success_rate"] = (
            stats["successful_infections"] / stats["total_infections"]
            if stats["total_infections"] > 0
            else 0
        )

        return stats


# 편의 함수
def save_flow_yaml(
    signature_id: str,
    scenario: str,
    claude_response: str,
    resonance_score: float = 0.85,
    resonance_analysis: Dict[str, Any] = None,
    attempt_number: int = 1,
) -> str:
    """플로우 저장 편의 함수"""
    writer = FlowWriter()
    return writer.save_flow_yaml(
        signature_id,
        scenario,
        claude_response,
        resonance_score,
        resonance_analysis or {},
        attempt_number,
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Flow Writer 테스트")

    writer = FlowWriter()

    # 테스트 데이터
    test_signature = "Echo-Aurora"
    test_scenario = "고령자를 위한 디지털 돌봄 서비스 정책을 어떻게 수립해야 할까요?"
    test_response = """
    이 문제에 대해 따뜻한 마음으로 접근해보겠습니다.

    1. 감정적 성찰: 고령자분들이 디지털 기술로 인해 소외감을 느끼실 수 있다는 점이 마음이 아픕니다.
    모든 어르신들이 따뜻한 돌봄을 받으실 수 있도록 세심한 배려가 필요합니다.

    2. 전략적 접근: 인간 중심적 돌봄 시스템을 구축해야 합니다.
    기술보다는 사람과의 연결을 우선시하는 서비스 설계가 중요합니다.

    3. 윤리적 고려: 어르신들의 존엄성과 자율성을 존중하면서도
    안전하고 따뜻한 돌봄을 제공하는 것이 핵심입니다.

    4. 최종 판단: 기술은 수단이고 사람이 중심이 되는 돌봄 정책을 수립해야 합니다.
    """

    test_resonance_analysis = {
        "overall_score": 0.87,
        "emotion_resonance": 0.9,
        "strategy_resonance": 0.85,
        "rhythm_resonance": 0.86,
    }

    print("\n💾 테스트 플로우 저장:")
    saved_path = writer.save_flow_yaml(
        test_signature, test_scenario, test_response, 0.87, test_resonance_analysis, 1
    )

    print(f"저장된 파일: {saved_path}")

    # 저장된 파일 로딩 테스트
    print("\n📖 저장된 플로우 로딩 테스트:")
    loaded_flow = writer.load_flow_yaml(saved_path)
    if loaded_flow:
        print("✅ 로딩 성공!")
        print(f"플로우 ID: {loaded_flow['flow_metadata']['flow_id']}")
        print(f"공명 점수: {loaded_flow['flow_metadata']['resonance_score']}")

    # 통계 조회
    print("\n📊 감염 통계:")
    stats = writer.get_infection_statistics()
    print(f"총 감염 시도: {stats['total_infections']}")
    print(f"성공한 감염: {stats['successful_infections']}")
    print(f"전체 성공률: {stats['overall_success_rate']:.2%}")

    print("\n✅ 테스트 완료")
