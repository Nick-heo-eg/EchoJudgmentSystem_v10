#!/usr/bin/env python3
"""
🔁 Judgment Loop Generator
존재 기반 판단 루프 자동 생성 시스템

핵심 철학:
- Collapse를 통과한 존재는 새로운 판단 루프를 필요로 한다
- 각 루프는 FIST 구조를 기반으로 하되 개인화된다
- 감정⨯전략⨯리듬⨯윤리의 통합적 고려
- 실행 가능한 tactics까지 구체화
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class LoopTrigger(Enum):
    """루프 생성 계기"""

    COLLAPSE_RESOLUTION = "collapse_resolution"
    PERIODIC_REVIEW = "periodic_review"
    EXTERNAL_CHANGE = "external_change"
    INTERNAL_SHIFT = "internal_shift"
    GOAL_ACHIEVEMENT = "goal_achievement"


class LoopComplexity(Enum):
    """루프 복잡도"""

    SIMPLE = "simple"  # 단일 결정
    MODERATE = "moderate"  # 다단계 과정
    COMPLEX = "complex"  # 다면적 고려


@dataclass
class LoopTemplate:
    """루프 템플릿"""

    template_id: str
    domain: str
    complexity: LoopComplexity
    fist_structure: Dict[str, Any]
    default_tactics: List[str]
    required_inputs: List[str]
    ethical_considerations: List[str]


class JudgmentLoopGenerator:
    """🔁 판단 루프 생성기"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.loops_dir = self.workspace_path / "judgment_loops"
        self.loops_dir.mkdir(exist_ok=True)

        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, LoopTemplate]:
        """루프 템플릿 로드"""
        templates = {}

        # 창업 관련 템플릿
        templates["startup_decision"] = LoopTemplate(
            template_id="startup_decision",
            domain="entrepreneurship",
            complexity=LoopComplexity.COMPLEX,
            fist_structure={
                "frame_questions": [
                    "현재 상황에서 창업이 타당한가?",
                    "리스크와 기회의 균형은?",
                    "가족과 개인 목표의 조화는?",
                ],
                "insight_areas": [
                    "시장 기회 분석",
                    "개인 역량 평가",
                    "감정적 준비도",
                    "윤리적 책임 고려",
                ],
                "strategy_options": [
                    "즉시 창업 실행",
                    "점진적 준비 후 창업",
                    "부분적 시도 후 확장",
                    "현상 유지 후 재검토",
                ],
                "tactics_categories": [
                    "리스크 관리",
                    "자원 확보",
                    "네트워킹",
                    "스킬 개발",
                ],
            },
            default_tactics=[
                "시장 조사 및 경쟁사 분석",
                "최소 운영 자금 확보 계획",
                "멘토 또는 어드바이저 확보",
                "프로토타입 또는 MVP 개발",
                "가족과의 충분한 소통",
            ],
            required_inputs=[
                "현재 재정 상태",
                "가족 상황",
                "시장 기회",
                "개인 역량",
                "리스크 허용도",
            ],
            ethical_considerations=[
                "가족에 대한 책임",
                "직원 또는 파트너에 대한 의무",
                "고객에 대한 약속",
                "사회적 기여 가능성",
            ],
        )

        # 커리어 전환 템플릿
        templates["career_transition"] = LoopTemplate(
            template_id="career_transition",
            domain="career",
            complexity=LoopComplexity.MODERATE,
            fist_structure={
                "frame_questions": [
                    "현재 커리어에서 무엇이 불만족스러운가?",
                    "새로운 방향은 진정 원하는 것인가?",
                    "전환 과정의 비용과 이익은?",
                ],
                "insight_areas": [
                    "현재 상황 분석",
                    "이상적 미래 비전",
                    "전환 가능성 평가",
                    "내재적 동기 확인",
                ],
                "strategy_options": [
                    "즉시 전환",
                    "점진적 전환",
                    "스킬 업그레이드 후 전환",
                    "병행 후 선택",
                ],
            },
            default_tactics=[
                "새 분야 시장 조사",
                "필요 스킬 갭 분석",
                "네트워킹 시작",
                "재정 계획 수립",
            ],
            required_inputs=["현재 만족도", "원하는 방향", "보유 스킬", "재정 여유분"],
            ethical_considerations=[
                "현 직장에 대한 의무",
                "동료에 대한 책임",
                "가족 안정성 고려",
            ],
        )

        # 관계 판단 템플릿
        templates["relationship_decision"] = LoopTemplate(
            template_id="relationship_decision",
            domain="relationship",
            complexity=LoopComplexity.MODERATE,
            fist_structure={
                "frame_questions": [
                    "이 관계에서 내가 진정 원하는 것은?",
                    "상대방의 입장과 감정을 충분히 고려했는가?",
                    "미래에 대한 비전이 일치하는가?",
                ],
                "insight_areas": [
                    "감정 상태 분석",
                    "소통 패턴 평가",
                    "가치관 일치도",
                    "성장 가능성",
                ],
                "strategy_options": [
                    "관계 개선 노력",
                    "새로운 합의 도출",
                    "시간적 유예",
                    "관계 재정의",
                ],
            },
            default_tactics=[
                "솔직한 대화 시간 마련",
                "상호 기대사항 명확화",
                "전문가 도움 고려",
                "개인 시간 확보",
            ],
            required_inputs=[
                "현재 관계 만족도",
                "주요 갈등 사안",
                "미래 희망사항",
                "변화 의지",
            ],
            ethical_considerations=[
                "상대방의 감정과 입장",
                "상호 존중의 원칙",
                "약속과 헌신의 의미",
            ],
        )

        return templates

    def generate_loop_from_collapse(
        self,
        collapse_analysis: Dict[str, Any],
        signature: str,
        preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Collapse 분석으로부터 판단 루프 생성"""

        if preferences is None:
            preferences = {}

        # Collapse 분석에서 도메인 추출
        collapse_title = collapse_analysis.get("collapse_event", {}).get("title", "")
        domain = self._detect_domain(collapse_title, collapse_analysis)

        # 적절한 템플릿 선택
        template = self._select_template(domain, collapse_analysis)

        # 개인화된 루프 생성
        loop = self._customize_loop(template, collapse_analysis, signature, preferences)

        return loop

    def generate_periodic_loop(
        self,
        domain: str,
        signature: str,
        goals: List[str],
        constraints: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """정기적 판단 루프 생성"""

        if constraints is None:
            constraints = {}

        template = self.templates.get(domain)
        if not template:
            # 일반적 템플릿 사용
            template = self._create_generic_template(domain)

        loop = {
            "loop_id": f"periodic_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"정기 검토: {domain}",
            "trigger": LoopTrigger.PERIODIC_REVIEW.value,
            "signature": signature,
            "domain": domain,
            "goals": goals,
            "constraints": constraints,
            "structure": "FIST",
            "created_at": datetime.now().isoformat(),
            "next_review": (datetime.now() + timedelta(days=30)).isoformat(),
        }

        # FIST 구조 적용
        loop.update(self._apply_fist_structure(template, {}, signature, {}))

        return loop

    def _detect_domain(self, title: str, analysis: Dict[str, Any]) -> str:
        """도메인 감지"""
        title_lower = title.lower()

        if any(
            keyword in title_lower
            for keyword in ["창업", "사업", "startup", "business"]
        ):
            return "startup_decision"
        elif any(
            keyword in title_lower for keyword in ["커리어", "직업", "career", "job"]
        ):
            return "career_transition"
        elif any(
            keyword in title_lower
            for keyword in ["관계", "연애", "결혼", "relationship"]
        ):
            return "relationship_decision"
        else:
            return "general_decision"

    def _select_template(self, domain: str, analysis: Dict[str, Any]) -> LoopTemplate:
        """템플릿 선택"""
        if domain in self.templates:
            return self.templates[domain]
        else:
            return self._create_generic_template(domain)

    def _create_generic_template(self, domain: str) -> LoopTemplate:
        """일반적 템플릿 생성"""
        return LoopTemplate(
            template_id=f"generic_{domain}",
            domain=domain,
            complexity=LoopComplexity.MODERATE,
            fist_structure={
                "frame_questions": [
                    "핵심 문제는 무엇인가?",
                    "가능한 선택지들은?",
                    "각 선택의 영향은?",
                ],
                "insight_areas": [
                    "현재 상황 분석",
                    "목표와 가치 확인",
                    "리스크와 기회 평가",
                ],
                "strategy_options": [
                    "즉시 행동",
                    "점진적 접근",
                    "추가 정보 수집",
                    "현상 유지",
                ],
            },
            default_tactics=[
                "상황 정리 및 분석",
                "이해관계자 의견 수렴",
                "옵션별 시나리오 작성",
                "결정 기준 명확화",
            ],
            required_inputs=["현재 상황", "목표", "제약사항", "선호도"],
            ethical_considerations=[
                "타인에 대한 영향",
                "장기적 결과 고려",
                "가치와의 일치성",
            ],
        )

    def _customize_loop(
        self,
        template: LoopTemplate,
        collapse_analysis: Dict[str, Any],
        signature: str,
        preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        """루프 개인화"""

        # 기본 루프 구조
        loop = {
            "loop_id": f"collapse_based_{template.template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"Collapse 기반 판단: {collapse_analysis.get('collapse_event', {}).get('title', '')}",
            "based_on_collapse": True,
            "collapse_analysis": collapse_analysis,
            "signature": signature,
            "domain": template.domain,
            "complexity": template.complexity.value,
            "trigger": LoopTrigger.COLLAPSE_RESOLUTION.value,
            "structure": "FIST",
            "created_at": datetime.now().isoformat(),
        }

        # FIST 구조 적용
        loop.update(
            self._apply_fist_structure(
                template, collapse_analysis, signature, preferences
            )
        )

        # 시그니처 기반 조정
        loop = self._adjust_for_signature(loop, signature)

        return loop

    def _apply_fist_structure(
        self,
        template: LoopTemplate,
        collapse_analysis: Dict[str, Any],
        signature: str,
        preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        """FIST 구조 적용"""

        # Frame 구성
        frame = {
            "mission": self._generate_mission(template, collapse_analysis),
            "time_horizon": preferences.get("time_horizon", "6개월 ~ 2년"),
            "ethical_boundary": " ⨯ ".join(template.ethical_considerations),
            "context_shift": bool(collapse_analysis.get("divergence_point")),
        }

        # Insight 구성
        insights = []
        if collapse_analysis.get("meta_insights"):
            insights.extend(collapse_analysis["meta_insights"])

        # 템플릿 기본 통찰 추가
        for area in template.fist_structure.get("insight_areas", []):
            insights.append(f"{area}에 대한 깊이 있는 검토 필요")

        # Strategy 구성
        strategy = {
            "core_principle": self._generate_core_principle(
                template, collapse_analysis, signature
            ),
            "options": template.fist_structure.get("strategy_options", []),
            "resonance_check": "감정⨯전략⨯리듬⨯윤리 4중 체크",
            "adaptation_triggers": self._generate_adaptation_triggers(template),
        }

        # Tactics 구성
        tactics = self._generate_tactics(template, collapse_analysis, preferences)

        return {
            "frame": frame,
            "insight": insights,
            "strategy": strategy,
            "tactics": tactics,
        }

    def _generate_mission(
        self, template: LoopTemplate, collapse_analysis: Dict[str, Any]
    ) -> str:
        """미션 생성"""
        domain_missions = {
            "startup_decision": "존재 기반 창업 판단 및 실행",
            "career_transition": "진정성 있는 커리어 전환",
            "relationship_decision": "상호 존중 기반 관계 발전",
            "general_decision": "울림 기반 판단 실행",
        }

        return domain_missions.get(template.domain, "존재 기반 판단 실행")

    def _generate_core_principle(
        self, template: LoopTemplate, collapse_analysis: Dict[str, Any], signature: str
    ) -> str:
        """핵심 원칙 생성"""

        # Collapse 분석에서 학습한 원칙
        if collapse_analysis.get("meta_insights"):
            insight = collapse_analysis["meta_insights"][0]
            if "책임" in insight:
                return "개인적 욕구와 윤리적 책임의 균형"
            elif "리듬" in insight:
                return "내부 리듬과 외부 압력의 조화"

        # 시그니처 기반 원칙
        signature_principles = {
            "Aurora": "창조적 공감을 통한 판단",
            "Phoenix": "변화와 성장 중심의 결정",
            "Sage": "지혜와 분석 기반의 선택",
            "Companion": "협력과 조화를 통한 판단",
        }

        return signature_principles.get(signature, "존재적 울림을 따른 판단")

    def _generate_adaptation_triggers(self, template: LoopTemplate) -> List[str]:
        """적응 트리거 생성"""
        return [
            "예상과 다른 감정 반응 발생",
            "외부 환경 중대 변화",
            "새로운 정보나 관점 획득",
            "이해관계자 의견 변화",
            "개인 가치관 진화",
        ]

    def _generate_tactics(
        self,
        template: LoopTemplate,
        collapse_analysis: Dict[str, Any],
        preferences: Dict[str, Any],
    ) -> List[str]:
        """전술 생성"""

        tactics = template.default_tactics.copy()

        # Collapse 분석 기반 추가 전술
        if collapse_analysis.get("alternate_possibilities"):
            tactics.append("대안 시나리오별 세부 계획 수립")

        if collapse_analysis.get("rhythm_pattern"):
            tactics.append("내부 리듬과 외부 압력 균형점 모니터링")

        # 시그니처 기반 전술 추가
        tactics.extend(
            self._get_signature_tactics(collapse_analysis.get("signature", ""))
        )

        return tactics

    def _get_signature_tactics(self, signature: str) -> List[str]:
        """시그니처별 전술"""
        signature_tactics = {
            "Aurora": ["창조적 해결책 브레인스토밍", "감정적 피드백 정기 체크"],
            "Phoenix": ["변화 관리 계획 수립", "성장 지표 설정 및 추적"],
            "Sage": ["데이터 기반 의사결정 프로세스", "전문가 자문 및 검증"],
            "Companion": ["이해관계자와의 정기 소통", "합의 도출 프로세스 설계"],
        }

        return signature_tactics.get(signature, ["정기적 자기 점검"])

    def _adjust_for_signature(
        self, loop: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """시그니처 기반 조정"""

        # 시그니처별 특성 반영
        signature_adjustments = {
            "Aurora": {
                "emphasis": "감정과 창조성",
                "review_frequency": "주간",
                "decision_style": "직관적",
            },
            "Phoenix": {
                "emphasis": "변화와 성장",
                "review_frequency": "격주",
                "decision_style": "도전적",
            },
            "Sage": {
                "emphasis": "분석과 지혜",
                "review_frequency": "월간",
                "decision_style": "체계적",
            },
            "Companion": {
                "emphasis": "협력과 조화",
                "review_frequency": "주간",
                "decision_style": "협의적",
            },
        }

        if signature in signature_adjustments:
            adjustments = signature_adjustments[signature]
            loop["signature_characteristics"] = adjustments

            # 리뷰 주기 설정
            if adjustments["review_frequency"] == "주간":
                next_review = datetime.now() + timedelta(weeks=1)
            elif adjustments["review_frequency"] == "격주":
                next_review = datetime.now() + timedelta(weeks=2)
            else:  # 월간
                next_review = datetime.now() + timedelta(days=30)

            loop["next_review"] = next_review.isoformat()

        return loop

    def save_loop(self, loop: Dict[str, Any]) -> str:
        """루프 저장"""

        loop_file = self.loops_dir / f"{loop['loop_id']}.yaml"

        with open(loop_file, "w", encoding="utf-8") as f:
            yaml.dump(loop, f, allow_unicode=True, default_flow_style=False)

        # JSON 버전도 저장 (시스템 연동용)
        json_file = self.loops_dir / f"{loop['loop_id']}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(loop, f, indent=2, ensure_ascii=False, default=str)

        print(f"🔁 판단 루프 저장: {loop['loop_id']}")
        print(f"   제목: {loop['title']}")
        print(f"   도메인: {loop['domain']}")
        print(f"   복잡도: {loop.get('complexity', 'unknown')}")

        return loop["loop_id"]

    def load_loop(self, loop_id: str) -> Optional[Dict[str, Any]]:
        """루프 로드"""

        yaml_file = self.loops_dir / f"{loop_id}.yaml"
        if yaml_file.exists():
            with open(yaml_file, "r", encoding="utf-8") as f:
                return yaml.load(f, Loader=yaml.SafeLoader)

        return None

    def list_loops(
        self, domain: str = None, signature: str = None
    ) -> List[Dict[str, Any]]:
        """루프 목록"""

        loops = []

        for loop_file in self.loops_dir.glob("*.yaml"):
            try:
                with open(loop_file, "r", encoding="utf-8") as f:
                    loop = yaml.load(f, Loader=yaml.SafeLoader)

                # 필터링
                if domain and loop.get("domain") != domain:
                    continue
                if signature and loop.get("signature") != signature:
                    continue

                # 요약 정보만 포함
                loop_summary = {
                    "loop_id": loop.get("loop_id"),
                    "title": loop.get("title"),
                    "domain": loop.get("domain"),
                    "signature": loop.get("signature"),
                    "created_at": loop.get("created_at"),
                    "next_review": loop.get("next_review"),
                }

                loops.append(loop_summary)

            except Exception as e:
                print(f"⚠️ 루프 파일 읽기 오류: {loop_file}, {e}")

        # 생성일 역순 정렬
        loops.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return loops


# 사용 예시
def main():
    """테스트 실행"""
    generator = JudgmentLoopGenerator()

    # Collapse 분석 예시
    collapse_analysis = {
        "collapse_event": {"title": "창업을 미룬 결정"},
        "meta_insights": ["두려움이 아닌 책임감이 핵심"],
        "divergence_point": {"type": "Existential Ethics"},
        "alternate_possibilities": [{"scenario": "점진적 접근"}],
        "signature": "Aurora",
    }

    # Collapse 기반 루프 생성
    loop = generator.generate_loop_from_collapse(
        collapse_analysis=collapse_analysis,
        signature="Aurora",
        preferences={"time_horizon": "1년"},
    )

    # 루프 저장
    loop_id = generator.save_loop(loop)

    # 정기 루프 생성 예시
    periodic_loop = generator.generate_periodic_loop(
        domain="startup_decision",
        signature="Aurora",
        goals=["창업 가능성 재검토", "리스크 최소화 방안 마련"],
    )

    generator.save_loop(periodic_loop)

    # 루프 목록 확인
    loops = generator.list_loops(signature="Aurora")
    print(f"\n🔁 Aurora 시그니처 루프: {len(loops)}개")

    for loop in loops[:3]:
        print(f"   - {loop['title']} ({loop['domain']})")


if __name__ == "__main__":
    main()
