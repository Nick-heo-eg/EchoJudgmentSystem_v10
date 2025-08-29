#!/usr/bin/env python3
"""
기계적 보고서 템플릿 시스템
- 표 + 핵심지표(합계/평균/증감률) + matplotlib 차트
- 중립적 톤의 요약문 생성
- HTML/PPTX 내보내기 지원
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import base64
import io
import logging

# 한글 폰트 설정
plt.rcParams["font.family"] = ["DejaVu Sans", "Arial Unicode MS", "Malgun Gothic"]
plt.rcParams["axes.unicode_minus"] = False

logger = logging.getLogger(__name__)


class MechanicalReportTemplater:
    """기계적 보고서 템플릿 생성기"""

    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # 차트 스타일 설정
        sns.set_style("whitegrid")
        plt.style.use("default")

    def build(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """기계적 보고서 생성"""
        if df.empty:
            return self._empty_report(question)

        logger.info(f"기계적 보고서 생성 시작: {len(df)}행 데이터")

        # 1. 기본 통계 계산
        key_metrics = self._calculate_key_metrics(df)

        # 2. 차트 생성
        chart_paths = self._generate_charts(df, question)

        # 3. 데이터 테이블 HTML 생성
        table_html = self._generate_table_html(df)

        # 4. 중립적 요약 생성
        summary = self._generate_neutral_summary(df, key_metrics, question)

        # 5. 종합 HTML 보고서
        html_report = self._generate_html_report(
            question, df, key_metrics, chart_paths, table_html, summary
        )

        return {
            "type": "mechanical",
            "question": question,
            "data_summary": {
                "rows": len(df),
                "columns": len(df.columns),
                "data_types": df.dtypes.to_dict(),
            },
            "key_metrics": key_metrics,
            "chart_paths": chart_paths,
            "table_html": table_html,
            "summary": summary,
            "html_report": html_report,
            "status": "success",
        }

    def _calculate_key_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """핵심 지표 계산"""
        metrics = {"total_rows": len(df), "total_columns": len(df.columns)}

        # 수치형 컬럼들에 대한 통계
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            numeric_data = df[numeric_cols]

            metrics.update(
                {
                    "numeric_columns": len(numeric_cols),
                    "total_sum": numeric_data.sum().to_dict(),
                    "averages": numeric_data.mean().to_dict(),
                    "medians": numeric_data.median().to_dict(),
                    "std_deviations": numeric_data.std().to_dict(),
                    "min_values": numeric_data.min().to_dict(),
                    "max_values": numeric_data.max().to_dict(),
                }
            )

            # 증감률 계산 (시계열 데이터인 경우)
            date_cols = df.select_dtypes(include=["datetime64"]).columns
            if len(date_cols) > 0 and len(numeric_cols) > 0:
                try:
                    df_sorted = df.sort_values(date_cols[0])
                    first_value = df_sorted[numeric_cols[0]].iloc[0]
                    last_value = df_sorted[numeric_cols[0]].iloc[-1]

                    if first_value != 0:
                        growth_rate = ((last_value - first_value) / first_value) * 100
                        metrics["growth_rate"] = {
                            "column": numeric_cols[0],
                            "rate_percent": round(growth_rate, 2),
                            "first_value": first_value,
                            "last_value": last_value,
                        }
                except:
                    pass

        # 범주형 데이터 통계
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            cat_stats = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                cat_stats[col] = {
                    "unique_count": len(value_counts),
                    "top_values": value_counts.head(3).to_dict(),
                    "null_count": df[col].isnull().sum(),
                }
            metrics["categorical_stats"] = cat_stats

        return metrics

    def _generate_charts(self, df: pd.DataFrame, question: str) -> List[str]:
        """차트 생성"""
        chart_paths = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=["object"]).columns

        # 1. 히스토그램 (수치형 데이터)
        if len(numeric_cols) > 0:
            fig, axes = plt.subplots(1, min(len(numeric_cols), 3), figsize=(15, 5))
            if len(numeric_cols) == 1:
                axes = [axes]

            for i, col in enumerate(numeric_cols[:3]):
                if i < len(axes):
                    df[col].hist(ax=axes[i], bins=20)
                    axes[i].set_title(f"{col} 분포")
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel("빈도")

            plt.tight_layout()
            chart_path = self.output_dir / f"histogram_{hash(question) % 10000}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches="tight")
            plt.close()
            chart_paths.append(str(chart_path))

        # 2. 막대 차트 (범주형 데이터)
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            value_counts = df[col].value_counts().head(10)

            plt.figure(figsize=(12, 6))
            value_counts.plot(kind="bar")
            plt.title(f"{col} 상위 10개 분포")
            plt.xlabel(col)
            plt.ylabel("개수")
            plt.xticks(rotation=45)
            plt.tight_layout()

            chart_path = self.output_dir / f"bar_{hash(question) % 10000}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches="tight")
            plt.close()
            chart_paths.append(str(chart_path))

        # 3. 상관관계 히트맵 (수치형 데이터가 2개 이상인 경우)
        if len(numeric_cols) >= 2:
            correlation = df[numeric_cols].corr()

            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation, annot=True, cmap="coolwarm", center=0)
            plt.title("컬럼 간 상관관계")
            plt.tight_layout()

            chart_path = self.output_dir / f"correlation_{hash(question) % 10000}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches="tight")
            plt.close()
            chart_paths.append(str(chart_path))

        # 4. 시계열 차트 (날짜 컬럼이 있는 경우)
        date_cols = df.select_dtypes(include=["datetime64"]).columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            try:
                df_sorted = df.sort_values(date_cols[0])

                plt.figure(figsize=(12, 6))
                plt.plot(
                    df_sorted[date_cols[0]], df_sorted[numeric_cols[0]], marker="o"
                )
                plt.title(f"{numeric_cols[0]} 시계열 변화")
                plt.xlabel(date_cols[0])
                plt.ylabel(numeric_cols[0])
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()

                chart_path = (
                    self.output_dir / f"timeseries_{hash(question) % 10000}.png"
                )
                plt.savefig(chart_path, dpi=150, bbox_inches="tight")
                plt.close()
                chart_paths.append(str(chart_path))
            except:
                pass

        logger.info(f"차트 생성 완료: {len(chart_paths)}개")
        return chart_paths

    def _generate_table_html(self, df: pd.DataFrame, max_rows: int = 100) -> str:
        """데이터 테이블 HTML 생성"""
        # 최대 행 수 제한
        display_df = df.head(max_rows)

        # HTML 스타일링
        html = display_df.to_html(
            classes="table table-striped table-bordered",
            table_id="data-table",
            index=False,
            escape=False,
        )

        return html

    def _generate_neutral_summary(
        self, df: pd.DataFrame, metrics: Dict[str, Any], question: str
    ) -> str:
        """중립적 톤의 요약문 생성"""
        summary_parts = []

        # 기본 정보
        summary_parts.append(
            f"분석 대상 데이터는 총 {metrics['total_rows']}행 {metrics['total_columns']}개 컬럼으로 구성되어 있습니다."
        )

        # 수치형 데이터 요약
        if metrics.get("numeric_columns", 0) > 0:
            numeric_summary = []

            if "total_sum" in metrics:
                for col, total in metrics["total_sum"].items():
                    avg = metrics["averages"][col]
                    numeric_summary.append(
                        f"{col}의 합계는 {total:,.0f}, 평균은 {avg:,.2f}입니다."
                    )

            if numeric_summary:
                summary_parts.extend(numeric_summary[:3])  # 최대 3개 컬럼

        # 증감률 정보
        if "growth_rate" in metrics:
            rate = metrics["growth_rate"]
            direction = "증가" if rate["rate_percent"] > 0 else "감소"
            summary_parts.append(
                f"{rate['column']}은(는) {rate['first_value']:,.2f}에서 {rate['last_value']:,.2f}로 "
                f"{abs(rate['rate_percent']):.1f}% {direction}하였습니다."
            )

        # 범주형 데이터 요약
        if "categorical_stats" in metrics:
            for col, stats in list(metrics["categorical_stats"].items())[
                :2
            ]:  # 최대 2개 컬럼
                top_value = list(stats["top_values"].keys())[0]
                top_count = list(stats["top_values"].values())[0]
                summary_parts.append(
                    f"{col}에서 가장 빈도가 높은 값은 '{top_value}'로 {top_count}건 입니다."
                )

        # 데이터 품질 정보
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            summary_parts.append(
                f"데이터에서 결측값이 총 {null_counts.sum()}개 발견되었습니다."
            )

        return " ".join(summary_parts)

    def _generate_html_report(
        self,
        question: str,
        df: pd.DataFrame,
        metrics: Dict[str, Any],
        chart_paths: List[str],
        table_html: str,
        summary: str,
    ) -> str:
        """종합 HTML 보고서 생성"""

        # 차트를 base64로 인코딩
        chart_html = ""
        for chart_path in chart_paths:
            try:
                with open(chart_path, "rb") as f:
                    chart_data = base64.b64encode(f.read()).decode()
                chart_html += f'<img src="data:image/png;base64,{chart_data}" class="chart-image" style="max-width: 100%; margin: 10px 0;">\n'
            except:
                chart_html += f"<p>차트를 로드할 수 없습니다: {chart_path}</p>\n"

        # 핵심 지표 HTML
        metrics_html = "<div class='metrics-grid'>"

        if "total_sum" in metrics:
            metrics_html += "<div class='metric-card'><h4>합계 정보</h4><ul>"
            for col, total in list(metrics["total_sum"].items())[:3]:
                metrics_html += f"<li>{col}: {total:,.0f}</li>"
            metrics_html += "</ul></div>"

        if "averages" in metrics:
            metrics_html += "<div class='metric-card'><h4>평균 정보</h4><ul>"
            for col, avg in list(metrics["averages"].items())[:3]:
                metrics_html += f"<li>{col}: {avg:,.2f}</li>"
            metrics_html += "</ul></div>"

        if "growth_rate" in metrics:
            rate = metrics["growth_rate"]
            color = "green" if rate["rate_percent"] > 0 else "red"
            metrics_html += f"""
            <div class='metric-card'>
                <h4>증감률</h4>
                <p>{rate['column']}: <span style="color: {color}; font-weight: bold;">{rate['rate_percent']:.1f}%</span></p>
            </div>
            """

        metrics_html += "</div>"

        html_template = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>데이터 분석 보고서</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .section {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .chart-image {{ border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2196f3; }}
                h1, h2, h3 {{ color: #333; }}
                .info-badge {{ display: inline-block; background: #667eea; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 데이터 분석 보고서</h1>
                <p><strong>질의:</strong> {question}</p>
                <div>
                    <span class="info-badge">{metrics['total_rows']} 행</span>
                    <span class="info-badge">{metrics['total_columns']} 컬럼</span>
                    <span class="info-badge">기계적 분석</span>
                </div>
            </div>

            <div class="section">
                <h2>📈 핵심 지표</h2>
                {metrics_html}
            </div>

            <div class="section">
                <h2>📋 요약</h2>
                <div class="summary">
                    {summary}
                </div>
            </div>

            <div class="section">
                <h2>📊 시각화 차트</h2>
                {chart_html}
            </div>

            <div class="section">
                <h2>🗃️ 데이터 테이블</h2>
                {table_html}
            </div>

            <div class="section" style="text-align: center; color: #666; font-size: 12px;">
                <p>이 보고서는 Echo 시스템의 기계적 분석 파이프라인에 의해 자동 생성되었습니다.</p>
            </div>
        </body>
        </html>
        """

        return html_template

    def _empty_report(self, question: str) -> Dict[str, Any]:
        """빈 데이터에 대한 보고서"""
        return {
            "type": "mechanical",
            "question": question,
            "data_summary": {"rows": 0, "columns": 0},
            "key_metrics": {},
            "chart_paths": [],
            "table_html": "<p>분석할 데이터가 없습니다.</p>",
            "summary": "질의에 해당하는 데이터를 찾을 수 없습니다. 쿼리 조건을 확인해주세요.",
            "html_report": f"<html><body><h1>데이터 없음</h1><p>질의: {question}</p><p>분석할 데이터가 없습니다.</p></body></html>",
            "status": "no_data",
        }

    def export_report(
        self, report_data: Dict[str, Any], filename: str, fmt: str = "html"
    ) -> str:
        """보고서 내보내기"""
        output_path = self.output_dir / f"{filename}.{fmt}"

        if fmt == "html":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_data["html_report"])
        elif fmt == "json":
            import json

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        else:
            raise ValueError(f"지원하지 않는 형식: {fmt}")

        logger.info(f"보고서 내보내기 완료: {output_path}")
        return str(output_path)
