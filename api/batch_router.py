"""
배치 처리 및 고급 기능 라우터
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio

from api.advanced_features import BatchProcessor, AdvancedAnalyzer, AutoLearner

# 라우터 초기화
batch_router = APIRouter(prefix="/batch", tags=["batch"])
analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])

# 전역 인스턴스
batch_processor = BatchProcessor()
analyzer = AdvancedAnalyzer()
learner = AutoLearner()


# 요청/응답 모델
class BatchRequest(BaseModel):
    prompts: List[str]
    batch_id: Optional[str] = None


class BatchResponse(BaseModel):
    batch_id: str
    total_requests: int
    successful: int
    failed: int
    results: List[dict]
    timestamp: str


class AnalysisRequest(BaseModel):
    days: Optional[int] = 7


class AnalysisResponse(BaseModel):
    user_pattern: dict
    emotional_trend: dict
    strategy_effectiveness: dict
    recommendations: List[str]
    analysis_date: str


# 배치 처리 엔드포인트
@batch_router.post("/process", response_model=BatchResponse)
async def process_batch(request: BatchRequest):
    """배치 처리 요청"""
    try:
        result = await batch_processor.process_batch(request.prompts, request.batch_id)

        return BatchResponse(
            batch_id=result["batch_id"],
            total_requests=result["total_requests"],
            successful=result["successful"],
            failed=result["failed"],
            results=result["results"],
            timestamp=result["timestamp"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 처리 실패: {str(e)}")


@batch_router.get("/history")
async def get_batch_history():
    """배치 처리 히스토리 조회"""
    return {"history": batch_processor.batch_history}


@batch_router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """특정 배치 상태 조회"""
    for batch in batch_processor.batch_history:
        if batch["batch_id"] == batch_id:
            return batch

    raise HTTPException(status_code=404, detail="배치를 찾을 수 없습니다")


# 분석 엔드포인트
@analysis_router.post("/comprehensive", response_model=AnalysisResponse)
async def comprehensive_analysis(request: AnalysisRequest):
    """종합 분석 요청"""
    try:
        result = analyzer.generate_comprehensive_analysis(request.days)

        return AnalysisResponse(
            user_pattern=result.user_pattern,
            emotional_trend=result.emotional_trend,
            strategy_effectiveness=result.strategy_effectiveness,
            recommendations=result.recommendations,
            analysis_date=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")


@analysis_router.get("/patterns")
async def get_user_patterns(days: int = 7):
    """사용자 패턴 분석"""
    try:
        df = analyzer.load_history(days)
        patterns = analyzer.analyze_user_patterns(df)
        return {"patterns": patterns, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 분석 실패: {str(e)}")


@analysis_router.get("/emotions")
async def get_emotional_trends(days: int = 7):
    """감정 트렌드 분석"""
    try:
        df = analyzer.load_history(days)
        trends = analyzer.analyze_emotional_trends(df)
        return {"emotional_trends": trends, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정 분석 실패: {str(e)}")


@analysis_router.get("/strategies")
async def get_strategy_effectiveness(days: int = 7):
    """전략 효과성 분석"""
    try:
        df = analyzer.load_history(days)
        effectiveness = analyzer.analyze_strategy_effectiveness(df)
        return {"strategy_effectiveness": effectiveness, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전략 분석 실패: {str(e)}")


@analysis_router.get("/learning")
async def get_learning_report():
    """학습 보고서 생성"""
    try:
        report = learner.generate_learning_report()
        return {"learning_report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학습 보고서 생성 실패: {str(e)}")


# 통계 엔드포인트
@analysis_router.get("/stats")
async def get_system_stats():
    """시스템 통계"""
    try:
        df = analyzer.load_history(30)  # 30일 데이터

        if df.empty:
            return {
                "total_requests": 0,
                "active_days": 0,
                "average_daily_requests": 0,
                "most_active_hour": None,
                "data_period": "30일",
            }

        # 기본 통계
        total_requests = len(df)
        active_days = df["timestamp"].dt.date.nunique()
        avg_daily = total_requests / max(active_days, 1)

        # 시간대별 분석
        hourly_dist = df["timestamp"].dt.hour.value_counts()
        most_active_hour = hourly_dist.idxmax() if not hourly_dist.empty else None

        return {
            "total_requests": total_requests,
            "active_days": active_days,
            "average_daily_requests": round(avg_daily, 2),
            "most_active_hour": most_active_hour,
            "data_period": "30일",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


# 실시간 모니터링 엔드포인트
@analysis_router.get("/realtime")
async def get_realtime_status():
    """실시간 상태 조회"""
    try:
        df = analyzer.load_history(1)  # 최근 1일

        if df.empty:
            return {
                "status": "inactive",
                "recent_requests": 0,
                "last_activity": None,
                "current_trend": "no_data",
            }

        recent_requests = len(df)
        last_activity = df["timestamp"].max().isoformat()

        # 최근 활동 트렌드
        if recent_requests > 10:
            current_trend = "high_activity"
        elif recent_requests > 5:
            current_trend = "moderate_activity"
        else:
            current_trend = "low_activity"

        return {
            "status": "active",
            "recent_requests": recent_requests,
            "last_activity": last_activity,
            "current_trend": current_trend,
            "period": "최근 24시간",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 상태 조회 실패: {str(e)}")


# 라우터 결합
def get_advanced_routers():
    """고급 기능 라우터들 반환"""
    return [batch_router, analysis_router]
