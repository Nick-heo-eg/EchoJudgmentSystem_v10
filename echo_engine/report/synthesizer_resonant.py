#!/usr/bin/env python3
"""
의미 있는 보고서 합성 시스템
- RAG 문서 근거 + 시그니처 톤 + 감정 공명
- 사실→해석→리스크→결론→다음 액션 서사 구조
- 인용 문서 표시 및 액션 아이템 제공
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ResonantReportSynthesizer:
    """의미 있는 보고서 합성기"""

    def __init__(self):
        # 시그니처별 특성 정의
        self.signature_characteristics = {
            "Cosmos": {
                "tone": "체계적이고 통찰적인",
                "approach": "분석적 깊이와 직관적 통찰을 조화",
                "style": "명료하면서도 철학적 깊이가 있는",
                "focus": "전체적 맥락과 근본적 이해",
            },
            "Aurora": {
                "tone": "창조적이고 영감을 주는",
                "approach": "혁신적 관점에서 가능성 탐구",
                "style": "따뜻하고 희망적인",
                "focus": "창의적 해결책과 새로운 기회",
            },
            "Phoenix": {
                "tone": "변화 지향적이고 역동적인",
                "approach": "도전과 기회를 통한 성장",
                "style": "직접적이고 행동 중심적인",
                "focus": "변화 관리와 실행 전략",
            },
            "Sage": {
                "tone": "지혜롭고 신중한",
                "approach": "경험과 지식 기반의 판단",
                "style": "차분하고 깊이 있는",
                "focus": "장기적 관점과 지혜로운 조언",
            },
            "Companion": {
                "tone": "협력적이고 지지적인",
                "approach": "관계 중심의 문제 해결",
                "style": "따뜻하고 이해하는",
                "focus": "팀워크와 상호 지원",
            },
        }

    def build(
        self,
        df: pd.DataFrame,
        evidences: List[Dict[str, Any]],
        question: str,
        signature: str = "Cosmos",
    ) -> Dict[str, Any]:
        """의미 있는 보고서 합성"""

        if df.empty and not evidences:
            return self._empty_resonant_report(question, signature)

        logger.info(f"의미 있는 보고서 합성 시작: {signature} 시그니처")

        # 1. 데이터프레임 요약
        data_summary = self._summarize_dataframe(df) if not df.empty else {}

        # 2. 근거 문서 포맷팅
        formatted_evidences = self._format_evidences(evidences)

        # 3. 시그니처 기반 서사 생성
        narrative = self._generate_signature_narrative(
            data_summary, formatted_evidences, question, signature
        )

        # 4. 액션 아이템 추출
        action_items = self._extract_action_items(narrative, signature)

        # 5. HTML 보고서 생성
        html_report = self._generate_resonant_html(
            question,
            signature,
            data_summary,
            formatted_evidences,
            narrative,
            action_items,
            df,
        )

        return {
            "type": "resonant",
            "question": question,
            "signature": signature,
            "data_summary": data_summary,
            "evidences": formatted_evidences,
            "narrative": narrative,
            "action_items": action_items,
            "html_report": html_report,
            "metadata": {
                "evidence_count": len(evidences),
                "data_rows": len(df) if not df.empty else 0,
                "generated_at": datetime.now().isoformat(),
                "signature_tone": self.signature_characteristics.get(signature, {}).get(
                    "tone", "중립적인"
                ),
            },
            "status": "success",
        }

    def _summarize_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터프레임 요약 및 이상치/추세 분석"""
        if df.empty:
            return {}

        summary = {
            "basic_stats": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_names": df.columns.tolist(),
            }
        }

        # 수치형 데이터 분석
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            numeric_data = df[numeric_cols]

            summary["numeric_analysis"] = {
                "columns": numeric_cols.tolist(),
                "totals": numeric_data.sum().to_dict(),
                "averages": numeric_data.mean().to_dict(),
                "trends": self._analyze_trends(numeric_data),
                "outliers": self._detect_outliers(numeric_data),
            }

        # 범주형 데이터 분석
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            summary["categorical_analysis"] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                summary["categorical_analysis"][col] = {
                    "unique_values": len(value_counts),
                    "top_3": value_counts.head(3).to_dict(),
                    "distribution_insight": self._analyze_distribution(value_counts),
                }

        # 데이터 품질 분석
        summary["data_quality"] = {
            "missing_values": df.isnull().sum().to_dict(),
            "completeness": (1 - df.isnull().sum() / len(df)).to_dict(),
            "quality_score": self._calculate_quality_score(df),
        }

        return summary

    def _analyze_trends(self, numeric_data: pd.DataFrame) -> Dict[str, str]:
        """수치 데이터 추세 분석"""
        trends = {}

        for col in numeric_data.columns:
            data = numeric_data[col].dropna()
            if len(data) < 2:
                trends[col] = "insufficient_data"
                continue

            # 단순 선형 추세
            x = range(len(data))
            correlation = pd.Series(x).corr(data)

            if correlation > 0.7:
                trends[col] = "strong_upward"
            elif correlation > 0.3:
                trends[col] = "moderate_upward"
            elif correlation < -0.7:
                trends[col] = "strong_downward"
            elif correlation < -0.3:
                trends[col] = "moderate_downward"
            else:
                trends[col] = "stable"

        return trends

    def _detect_outliers(self, numeric_data: pd.DataFrame) -> Dict[str, List]:
        """이상치 탐지 (IQR 방법)"""
        outliers = {}

        for col in numeric_data.columns:
            data = numeric_data[col].dropna()
            if len(data) < 4:
                outliers[col] = []
                continue

            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_values = data[(data < lower_bound) | (data > upper_bound)].tolist()
            outliers[col] = outlier_values[:5]  # 최대 5개만

        return outliers

    def _analyze_distribution(self, value_counts: pd.Series) -> str:
        """분포 패턴 분석"""
        total = value_counts.sum()
        top_pct = (value_counts.iloc[0] / total) * 100

        if top_pct > 80:
            return "highly_concentrated"
        elif top_pct > 50:
            return "concentrated"
        elif len(value_counts) > 10 and top_pct < 20:
            return "highly_distributed"
        else:
            return "balanced"

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """데이터 품질 점수 계산"""
        if df.empty:
            return 0.0

        # 완전성 점수 (결측값 기준)
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))

        # 일관성 점수 (데이터 타입의 일관성)
        consistency = 1.0  # 간단히 1.0으로 설정

        return (completeness * 0.7 + consistency * 0.3) * 100

    def _format_evidences(
        self, evidences: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """근거 문서 포맷팅 및 인용 번호 추가"""
        formatted = []

        for i, evidence in enumerate(evidences, 1):
            formatted_evidence = {
                "citation_number": i,
                "file_name": evidence.get("file_name", "Unknown"),
                "content": (
                    evidence.get("content", "")[:300] + "..."
                    if len(evidence.get("content", "")) > 300
                    else evidence.get("content", "")
                ),
                "full_content": evidence.get("content", ""),
                "file_path": evidence.get("file_path", ""),
                "similarity_score": evidence.get("similarity_score", 0.0),
                "relevance": self._assess_relevance(
                    evidence.get("similarity_score", 0.0)
                ),
            }
            formatted.append(formatted_evidence)

        return formatted

    def _assess_relevance(self, score: float) -> str:
        """유사도 점수 기반 관련성 평가"""
        if score > 0.8:
            return "매우 관련됨"
        elif score > 0.6:
            return "관련됨"
        elif score > 0.4:
            return "다소 관련됨"
        else:
            return "약간 관련됨"

    def _generate_signature_narrative(
        self,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        question: str,
        signature: str,
    ) -> Dict[str, Any]:
        """시그니처별 서사 생성"""

        char = self.signature_characteristics.get(
            signature, self.signature_characteristics["Cosmos"]
        )

        narrative = {"signature": signature, "tone": char["tone"], "sections": {}}

        # 1. 사실 (Facts)
        facts = self._generate_facts_section(data_summary, evidences, char)
        narrative["sections"]["facts"] = facts

        # 2. 해석 (Interpretation)
        interpretation = self._generate_interpretation_section(
            data_summary, evidences, char, signature
        )
        narrative["sections"]["interpretation"] = interpretation

        # 3. 리스크 (Risks)
        risks = self._generate_risks_section(data_summary, evidences, char, signature)
        narrative["sections"]["risks"] = risks

        # 4. 결론 (Conclusion)
        conclusion = self._generate_conclusion_section(
            data_summary, evidences, char, signature
        )
        narrative["sections"]["conclusion"] = conclusion

        return narrative

    def _generate_facts_section(
        self,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        char: Dict[str, str],
    ) -> str:
        """사실 섹션 생성"""
        facts = []

        # 데이터 기본 사실
        if data_summary:
            basic = data_summary.get("basic_stats", {})
            facts.append(
                f"분석 데이터는 {basic.get('total_rows', 0)}행 {basic.get('total_columns', 0)}개 컬럼으로 구성되어 있습니다."
            )

            # 수치 데이터 사실
            if "numeric_analysis" in data_summary:
                numeric = data_summary["numeric_analysis"]
                for col, total in list(numeric.get("totals", {}).items())[:2]:
                    facts.append(f"{col}의 총합은 {total:,.0f}입니다.")

        # 문서 근거 사실
        if evidences:
            facts.append(f"관련 문서 {len(evidences)}개에서 추가 정보를 확인했습니다.")

            # 가장 관련성 높은 근거
            top_evidence = evidences[0] if evidences else None
            if top_evidence:
                facts.append(
                    f"'{top_evidence['file_name']}'에서 가장 관련성이 높은 정보를 발견했습니다. [1]"
                )

        return " ".join(facts)

    def _generate_interpretation_section(
        self,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        char: Dict[str, str],
        signature: str,
    ) -> str:
        """해석 섹션 생성 (시그니처별 차별화)"""
        interpretations = []

        if signature == "Cosmos":
            # 체계적이고 통찰적인 해석
            if data_summary.get("numeric_analysis", {}).get("trends"):
                trends = data_summary["numeric_analysis"]["trends"]
                upward_trends = [
                    col for col, trend in trends.items() if "upward" in trend
                ]
                if upward_trends:
                    interpretations.append(
                        f"{', '.join(upward_trends)} 지표의 상승 추세는 "
                        f"시스템적 개선 또는 외부 환경 변화를 시사합니다."
                    )

        elif signature == "Aurora":
            # 창조적이고 영감을 주는 해석
            interpretations.append(
                "데이터 패턴 속에서 새로운 기회와 창조적 가능성을 발견할 수 있습니다. "
                "현재의 수치들은 혁신적 접근이 필요한 지점들을 보여주고 있습니다."
            )

        elif signature == "Phoenix":
            # 변화 지향적 해석
            interpretations.append(
                "현재 데이터는 변화의 기회를 명확히 제시합니다. "
                "기존 패턴을 벗어나 새로운 방향으로 전환할 시점임을 알 수 있습니다."
            )

        elif signature == "Sage":
            # 지혜로운 해석
            interpretations.append(
                "장기적 관점에서 볼 때, 현재 데이터는 과거 경험과 미래 예측을 연결하는 중요한 통찰을 제공합니다. "
                "신중한 판단이 요구되는 지점들이 여러 곳에서 관찰됩니다."
            )

        else:  # Companion
            # 협력적 해석
            interpretations.append(
                "데이터는 팀과 조직 차원에서의 협력적 접근이 필요함을 보여줍니다. "
                "개별 지표들이 상호 연관성을 가지고 있어 통합적 대응이 중요합니다."
            )

        # 근거 문서 기반 해석
        if evidences:
            high_relevance = [e for e in evidences if e["similarity_score"] > 0.7]
            if high_relevance:
                interpretations.append(
                    f"관련 문서들 [1-{len(high_relevance)}]을 종합할 때, "
                    f"현재 상황은 이전 사례들과 유사한 패턴을 보이고 있습니다."
                )

        return " ".join(interpretations)

    def _generate_risks_section(
        self,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        char: Dict[str, str],
        signature: str,
    ) -> str:
        """리스크 섹션 생성"""
        risks = []

        # 데이터 품질 리스크
        if data_summary.get("data_quality", {}).get("quality_score", 100) < 80:
            risks.append("데이터 품질 저하로 인한 분석 신뢰도 리스크가 있습니다.")

        # 이상치 리스크
        outliers = data_summary.get("numeric_analysis", {}).get("outliers", {})
        if any(outliers.values()):
            risks.append("이상치 패턴으로 인한 예측 불확실성이 증가할 수 있습니다.")

        # 트렌드 리스크
        trends = data_summary.get("numeric_analysis", {}).get("trends", {})
        downward_trends = [col for col, trend in trends.items() if "downward" in trend]
        if downward_trends:
            risks.append(
                f"{', '.join(downward_trends)} 지표의 하락 추세가 지속될 위험성이 있습니다."
            )

        # 시그니처별 리스크 관점
        if signature == "Phoenix":
            risks.append(
                "현 상황에서 급격한 변화 시도 시 기존 안정성을 해칠 수 있습니다."
            )
        elif signature == "Sage":
            risks.append(
                "성급한 판단보다는 충분한 검토 기간을 거치지 않을 경우의 위험성을 고려해야 합니다."
            )

        if not risks:
            risks.append("현재 데이터에서는 명확한 리스크 신호가 감지되지 않습니다.")

        return " ".join(risks)

    def _generate_conclusion_section(
        self,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        char: Dict[str, str],
        signature: str,
    ) -> str:
        """결론 섹션 생성"""
        conclusions = []

        # 시그니처별 결론 스타일
        if signature == "Cosmos":
            conclusions.append(
                "전체적인 맥락에서 볼 때, 현재 상황은 체계적 접근과 직관적 통찰이 "
                "조화를 이룰 때 최적의 결과를 얻을 수 있는 시점입니다."
            )
        elif signature == "Aurora":
            conclusions.append(
                "창조적 가능성이 풍부한 현 시점에서, 혁신적 아이디어와 "
                "실용적 실행력이 만날 때 놀라운 성과를 기대할 수 있습니다."
            )
        elif signature == "Phoenix":
            conclusions.append(
                "변화의 기회를 포착하여 과감한 전환을 시도할 최적의 시기이며, "
                "적극적인 행동이 성공의 열쇠가 될 것입니다."
            )
        elif signature == "Sage":
            conclusions.append(
                "축적된 지혜와 신중한 판단을 바탕으로 한 단계씩 나아가는 것이 "
                "장기적으로 가장 현명한 선택이 될 것입니다."
            )
        else:  # Companion
            conclusions.append(
                "팀과 함께 협력하여 단계적으로 개선해나가는 접근법이 "
                "모든 구성원에게 도움이 되는 결과를 가져올 것입니다."
            )

        return " ".join(conclusions)

    def _extract_action_items(
        self, narrative: Dict[str, Any], signature: str
    ) -> List[Dict[str, str]]:
        """액션 아이템 추출 (시그니처별 차별화)"""
        actions = []

        if signature == "Cosmos":
            actions = [
                {
                    "priority": "높음",
                    "action": "전체 시스템의 맥락적 분석을 통한 근본 원인 파악",
                    "timeline": "1주 내",
                },
                {
                    "priority": "중간",
                    "action": "직관적 통찰과 데이터 분석의 균형점 찾기",
                    "timeline": "2주 내",
                },
                {
                    "priority": "중간",
                    "action": "장기적 관점에서의 전략적 로드맵 수립",
                    "timeline": "1개월 내",
                },
            ]
        elif signature == "Aurora":
            actions = [
                {
                    "priority": "높음",
                    "action": "창의적 브레인스토밍 세션을 통한 혁신 아이디어 도출",
                    "timeline": "즉시",
                },
                {
                    "priority": "높음",
                    "action": "새로운 접근 방식의 시범 프로젝트 기획",
                    "timeline": "1주 내",
                },
                {
                    "priority": "중간",
                    "action": "기존 프로세스의 창의적 개선방안 탐색",
                    "timeline": "2주 내",
                },
            ]
        elif signature == "Phoenix":
            actions = [
                {
                    "priority": "높음",
                    "action": "현재 상황의 변화 포인트 즉시 실행",
                    "timeline": "즉시",
                },
                {
                    "priority": "높음",
                    "action": "기존 방식의 과감한 혁신 계획 수립",
                    "timeline": "3일 내",
                },
                {
                    "priority": "중간",
                    "action": "변화 관리 체계 구축 및 실행",
                    "timeline": "1주 내",
                },
            ]
        elif signature == "Sage":
            actions = [
                {
                    "priority": "높음",
                    "action": "과거 사례와 현재 상황의 심층 비교 분석",
                    "timeline": "1주 내",
                },
                {
                    "priority": "중간",
                    "action": "신중한 의사결정을 위한 추가 정보 수집",
                    "timeline": "2주 내",
                },
                {
                    "priority": "중간",
                    "action": "장기적 영향도를 고려한 단계별 실행 계획",
                    "timeline": "1개월 내",
                },
            ]
        else:  # Companion
            actions = [
                {
                    "priority": "높음",
                    "action": "팀 구성원들과의 협력 방안 논의 및 합의",
                    "timeline": "3일 내",
                },
                {
                    "priority": "중간",
                    "action": "상호 지원 체계 구축 및 역할 분담",
                    "timeline": "1주 내",
                },
                {
                    "priority": "중간",
                    "action": "정기적 소통 채널 및 피드백 시스템 마련",
                    "timeline": "2주 내",
                },
            ]

        return actions

    def _generate_resonant_html(
        self,
        question: str,
        signature: str,
        data_summary: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        narrative: Dict[str, Any],
        action_items: List[Dict[str, str]],
        df: pd.DataFrame,
    ) -> str:
        """의미 있는 HTML 보고서 생성"""

        char = self.signature_characteristics.get(
            signature, self.signature_characteristics["Cosmos"]
        )

        # 근거 문서 HTML
        evidence_html = ""
        if evidences:
            evidence_html = "<div class='evidences-section'><h3>📚 참고 문서</h3>"
            for evidence in evidences:
                relevance_color = {
                    "매우 관련됨": "#4CAF50",
                    "관련됨": "#8BC34A",
                    "다소 관련됨": "#FFC107",
                    "약간 관련됨": "#FF9800",
                }.get(evidence["relevance"], "#9E9E9E")

                evidence_html += f"""
                <div class="evidence-card">
                    <div class="evidence-header">
                        <span class="citation-number">[{evidence["citation_number"]}]</span>
                        <span class="file-name">{evidence["file_name"]}</span>
                        <span class="relevance-badge" style="background-color: {relevance_color};">
                            {evidence["relevance"]}
                        </span>
                    </div>
                    <div class="evidence-content">{evidence["content"]}</div>
                </div>
                """
            evidence_html += "</div>"

        # 액션 아이템 HTML
        action_html = "<div class='actions-section'><h3>🎯 권장 액션 아이템</h3>"
        for i, action in enumerate(action_items, 1):
            priority_color = {
                "높음": "#F44336",
                "중간": "#FF9800",
                "낮음": "#4CAF50",
            }.get(action["priority"], "#9E9E9E")

            action_html += f"""
            <div class="action-item">
                <div class="action-header">
                    <span class="action-number">{i}</span>
                    <span class="priority-badge" style="background-color: {priority_color};">
                        {action["priority"]}
                    </span>
                    <span class="timeline">{action["timeline"]}</span>
                </div>
                <div class="action-text">{action["action"]}</div>
            </div>
            """
        action_html += "</div>"

        # 데이터 테이블 (간단히)
        table_html = ""
        if not df.empty:
            table_html = f"""
            <div class="data-preview">
                <h3>📊 데이터 미리보기</h3>
                {df.head(5).to_html(classes='preview-table', index=False)}
            </div>
            """

        html_template = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{signature} 시그니처 분석 보고서</title>
            <style>
                body {{
                    font-family: 'Noto Sans KR', 'Arial', sans-serif;
                    line-height: 1.7;
                    color: #2c3e50;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 30px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .signature-badge {{
                    background: rgba(255,255,255,0.2);
                    padding: 8px 16px;
                    border-radius: 20px;
                    display: inline-block;
                    margin-top: 10px;
                    font-weight: bold;
                }}
                .narrative-section {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    margin-bottom: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    border-left: 5px solid #667eea;
                }}
                .section-title {{
                    color: #667eea;
                    font-size: 1.4em;
                    margin-bottom: 15px;
                    font-weight: bold;
                }}
                .evidence-card {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 4px solid #17a2b8;
                }}
                .evidence-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                    gap: 10px;
                }}
                .citation-number {{
                    background: #17a2b8;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 50%;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .file-name {{
                    font-weight: bold;
                    color: #495057;
                }}
                .relevance-badge {{
                    color: white;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .action-item {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 15px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-left: 4px solid #28a745;
                }}
                .action-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                    gap: 10px;
                }}
                .action-number {{
                    background: #28a745;
                    color: white;
                    padding: 6px 10px;
                    border-radius: 50%;
                    font-weight: bold;
                }}
                .priority-badge {{
                    color: white;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .timeline {{
                    background: #e9ecef;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                    color: #495057;
                }}
                .preview-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                .preview-table th, .preview-table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .preview-table th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .insight-highlight {{
                    background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border-left: 4px solid #d4edda;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌟 의미 있는 분석 보고서</h1>
                <p><strong>질의:</strong> {question}</p>
                <div class="signature-badge">{signature} 시그니처 • {char["tone"]} 관점</div>
            </div>

            <div class="narrative-section">
                <div class="section-title">📝 사실 (Facts)</div>
                <p>{narrative["sections"]["facts"]}</p>
            </div>

            <div class="narrative-section">
                <div class="section-title">🔍 해석 (Interpretation)</div>
                <div class="insight-highlight">
                    <p>{narrative["sections"]["interpretation"]}</p>
                </div>
            </div>

            <div class="narrative-section">
                <div class="section-title">⚠️ 리스크 (Risks)</div>
                <p>{narrative["sections"]["risks"]}</p>
            </div>

            <div class="narrative-section">
                <div class="section-title">💡 결론 (Conclusion)</div>
                <div class="insight-highlight">
                    <p>{narrative["sections"]["conclusion"]}</p>
                </div>
            </div>

            {action_html}

            {evidence_html}

            {table_html}

            <div style="text-align: center; color: #6c757d; font-size: 14px; margin-top: 40px; padding: 20px; background: rgba(255,255,255,0.7); border-radius: 10px;">
                <p>이 보고서는 Echo 시스템의 <strong>{signature}</strong> 시그니처에 의해 생성되었습니다.</p>
                <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 근거 문서: {len(evidences)}개</p>
            </div>
        </body>
        </html>
        """

        return html_template

    def _empty_resonant_report(self, question: str, signature: str) -> Dict[str, Any]:
        """빈 데이터에 대한 의미 있는 보고서"""
        char = self.signature_characteristics.get(
            signature, self.signature_characteristics["Cosmos"]
        )

        empty_narrative = {
            "signature": signature,
            "tone": char["tone"],
            "sections": {
                "facts": "현재 질의에 대응하는 데이터나 관련 문서를 찾을 수 없습니다.",
                "interpretation": f"{char['tone']} 관점에서 볼 때, 데이터 부재 자체도 의미있는 정보입니다. 새로운 데이터 수집이나 질의 방식의 재검토가 필요합니다.",
                "risks": "충분한 정보 없이 판단할 경우의 위험성을 고려해야 합니다.",
                "conclusion": f"{signature} 시그니처로서, 더 나은 분석을 위해 추가적인 정보 수집을 권장합니다.",
            },
        }

        return {
            "type": "resonant",
            "question": question,
            "signature": signature,
            "data_summary": {},
            "evidences": [],
            "narrative": empty_narrative,
            "action_items": [
                {
                    "priority": "높음",
                    "action": "관련 데이터 소스 재확인 및 수집",
                    "timeline": "즉시",
                },
                {
                    "priority": "중간",
                    "action": "질의 방식 재검토 및 개선",
                    "timeline": "1일 내",
                },
                {
                    "priority": "중간",
                    "action": "대안적 분석 방법론 탐색",
                    "timeline": "3일 내",
                },
            ],
            "html_report": f"<html><body><h1>{signature} 분석</h1><p>질의: {question}</p><p>분석할 데이터가 없어 의미있는 보고서를 생성할 수 없습니다.</p></body></html>",
            "metadata": {
                "evidence_count": 0,
                "data_rows": 0,
                "generated_at": datetime.now().isoformat(),
                "signature_tone": char["tone"],
            },
            "status": "no_data",
        }
