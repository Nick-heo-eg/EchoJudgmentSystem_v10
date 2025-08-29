"""
Asset Value Judger - Echo 자산 가치 판단 엔진
==========================================

Echo 시스템 내의 코드 자산을 분석하여 T/S/P 점수를 기반으로
dormant(잠재자산), pending(검토필요), junk(폐기대상)로 분류합니다.

Main Interface:
    judge_assets() - 메인 판단 엔진
"""

from .core import judge_assets
from .schemas import AssetReport, AssetMetrics, AssetDecision

__version__ = "1.0.0"
__all__ = ["judge_assets", "AssetReport", "AssetMetrics", "AssetDecision"]
