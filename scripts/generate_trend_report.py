#!/usr/bin/env python3
"""
Echo 시스템 성능 트렌드 리포트 생성기
수집된 메트릭 데이터로 시각적 트렌드 분석 리포트 생성
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TrendReportGenerator:
    """트렌드 리포트 생성기"""

    def __init__(self, data_dir: str = "data/metrics"):
        self.data_dir = Path(data_dir)
        self.metrics_data: List[Dict] = []

    def load_metrics_history(self, days_back: int = 7):
        """메트릭 히스토리 로드"""
        cutoff_date = datetime.now() - timedelta(days=days_back)

        metric_files = sorted(self.data_dir.glob("metrics_*.json"))

        for metric_file in metric_files:
            try:
                # 파일명에서 날짜 추출
                date_str = metric_file.stem.replace("metrics_", "")
                file_date = datetime.strptime(date_str[:8], "%Y%m%d")

                if file_date >= cutoff_date:
                    with open(metric_file) as f:
                        data = json.load(f)
                    self.metrics_data.append(data)

            except Exception as e:
                logger.warning(f"Failed to load {metric_file}: {e}")

        logger.info(f"📊 Loaded {len(self.metrics_data)} metric snapshots")

    def analyze_trends(self) -> Dict[str, Any]:
        """트렌드 분석"""
        if len(self.metrics_data) < 2:
            return {"error": "Insufficient data for trend analysis"}

        trends = {}
        metric_names = set()

        # 모든 메트릭 이름 수집
        for data in self.metrics_data:
            for metric in data.get("metrics", []):
                metric_names.add(metric["name"])

        # 각 메트릭별 트렌드 계산
        for metric_name in metric_names:
            values = []
            timestamps = []

            for data in self.metrics_data:
                for metric in data.get("metrics", []):
                    if metric["name"] == metric_name:
                        values.append(metric["value"])
                        timestamps.append(metric["timestamp"])
                        break

            if len(values) >= 2:
                trends[metric_name] = self._calculate_trend_stats(values, timestamps)

        return trends

    def _calculate_trend_stats(
        self, values: List[float], timestamps: List[str]
    ) -> Dict:
        """트렌드 통계 계산"""
        if not values:
            return {}

        return {
            "current": values[-1],
            "previous": values[0] if len(values) > 1 else values[0],
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "change_percent": (
                ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
            ),
            "trend_direction": (
                "up"
                if values[-1] > values[0]
                else "down" if values[-1] < values[0] else "stable"
            ),
            "data_points": len(values),
        }

    def generate_html_report(self, trends: Dict[str, Any], output_path: str):
        """HTML 리포트 생성"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echo System Performance Trends</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f5f7fa; 
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; background: white; 
            border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ 
            text-align: center; margin-bottom: 40px; 
            border-bottom: 2px solid #e1e8ed; padding-bottom: 20px;
        }}
        .metric-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }}
        .metric-card {{ 
            border: 1px solid #e1e8ed; border-radius: 8px; padding: 20px; 
            background: #fafbfc; 
        }}
        .metric-name {{ 
            font-weight: 600; font-size: 1.1em; margin-bottom: 15px; 
            color: #1a1a1a; 
        }}
        .metric-stats {{ 
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; 
        }}
        .stat-item {{ 
            padding: 8px; background: white; border-radius: 4px; 
            font-size: 0.9em; 
        }}
        .trend-up {{ color: #28a745; }}
        .trend-down {{ color: #dc3545; }}
        .trend-stable {{ color: #6c757d; }}
        .summary {{ 
            background: #e8f4fd; border-radius: 8px; padding: 20px; 
            border-left: 4px solid #007bff; 
        }}
        .timestamp {{ 
            color: #6c757d; font-size: 0.9em; text-align: center; 
            margin-top: 30px; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Echo System Performance Trends</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h3>📊 Summary</h3>
            <p><strong>Total Metrics:</strong> {len(trends)}</p>
            <p><strong>Data Points:</strong> {len(self.metrics_data)} snapshots</p>
            <p><strong>Analysis Period:</strong> Last 7 days</p>
        </div>
        
        <div class="metric-grid">
"""

        for metric_name, stats in trends.items():
            if not stats:
                continue

            trend_class = f"trend-{stats['trend_direction']}"
            trend_emoji = (
                "📈"
                if stats["trend_direction"] == "up"
                else "📉" if stats["trend_direction"] == "down" else "📊"
            )

            html_content += f"""
            <div class="metric-card">
                <div class="metric-name">{trend_emoji} {metric_name.replace('_', ' ').title()}</div>
                <div class="metric-stats">
                    <div class="stat-item">
                        <strong>Current:</strong> {stats['current']:.2f}
                    </div>
                    <div class="stat-item">
                        <strong>Previous:</strong> {stats['previous']:.2f}
                    </div>
                    <div class="stat-item">
                        <strong>Min:</strong> {stats['min']:.2f}
                    </div>
                    <div class="stat-item">
                        <strong>Max:</strong> {stats['max']:.2f}
                    </div>
                    <div class="stat-item">
                        <strong>Average:</strong> {stats['avg']:.2f}
                    </div>
                    <div class="stat-item">
                        <strong class="{trend_class}">Change:</strong> 
                        <span class="{trend_class}">{stats['change_percent']:+.1f}%</span>
                    </div>
                </div>
            </div>
"""

        html_content += f"""
        </div>
        
        <div class="timestamp">
            📅 Report generated at {datetime.now().isoformat()}
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"📄 HTML report generated: {output_path}")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Generate Echo performance trend report"
    )
    parser.add_argument(
        "--data-dir", default="data/metrics", help="Metrics data directory"
    )
    parser.add_argument(
        "--output", default="data/trend_report.html", help="Output HTML file"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Days of history to analyze"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # 로깅 설정
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 리포트 생성
    generator = TrendReportGenerator(args.data_dir)
    generator.load_metrics_history(args.days)

    trends = generator.analyze_trends()

    if "error" in trends:
        logger.error(f"❌ {trends['error']}")
        return 1

    generator.generate_html_report(trends, args.output)
    logger.info("✅ Trend report generation completed")

    return 0


if __name__ == "__main__":
    exit(main())
