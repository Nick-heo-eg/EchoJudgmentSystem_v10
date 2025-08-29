#!/usr/bin/env python3
"""
🧠 Judgment Meta Logger - EchoJudgmentSystem v10 고도화 메타 로깅 시스템

판단 과정의 모든 메타데이터를 수집, 분석, 저장하는 고도화된 로깅 시스템
성능, 패턴, 학습 데이터를 종합적으로 관리
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict


@dataclass
class JudgmentMetaData:
    """판단 메타데이터 구조"""

    # 기본 정보
    judgment_id: str
    timestamp: datetime
    input_text: str
    input_hash: str
    session_id: str

    # 판단 결과
    echo_judgment: Optional[str] = None
    claude_judgment: Optional[str] = None
    final_judgment: str = ""
    confidence_score: float = 0.0

    # 감정 및 전략
    detected_emotion: Optional[str] = None
    emotion_confidence: float = 0.0
    suggested_strategy: Optional[str] = None
    strategy_confidence: float = 0.0

    # 성능 지표
    processing_time: float = 0.0
    echo_response_time: float = 0.0
    claude_response_time: float = 0.0
    total_tokens_used: int = 0

    # 컨텍스트
    user_context: Optional[str] = None
    system_context: Dict[str, Any] = None
    previous_judgments: List[str] = None

    # 품질 지표
    consistency_score: float = 0.0  # Echo vs Claude 일치도
    complexity_score: float = 0.0  # 입력 복잡도
    novelty_score: float = 0.0  # 새로운 패턴 정도

    # 학습 데이터
    feedback_received: Optional[str] = None
    user_rating: Optional[int] = None
    correction_applied: bool = False

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.system_context is None:
            self.system_context = {}
        if self.previous_judgments is None:
            self.previous_judgments = []


class JudgmentMetaLogger:
    """판단 메타 로거 클래스"""

    def __init__(self, log_directory: str = "meta_logs"):
        self.log_directory = log_directory
        self.session_id = f"meta_session_{int(time.time())}"
        self.current_session_data = []
        self.performance_aggregates = defaultdict(list)
        self.pattern_cache = {}
        self.lock = threading.Lock()

        # 디렉토리 생성
        os.makedirs(self.log_directory, exist_ok=True)

        # 세션 시작 로그
        self._log_session_start()

    def _log_session_start(self):
        """세션 시작 로그"""
        session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "system_info": {
                "python_version": "3.11+",
                "echo_engine_version": "v10",
                "logging_features": [
                    "meta_logging",
                    "performance_tracking",
                    "pattern_analysis",
                    "learning_data_collection",
                ],
            },
        }

        session_file = os.path.join(
            self.log_directory, f"session_{self.session_id}.json"
        )
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_info, f, ensure_ascii=False, indent=2)

    def generate_judgment_id(self, input_text: str, timestamp: datetime) -> str:
        """판단 ID 생성"""
        combined = f"{input_text}_{timestamp.isoformat()}_{self.session_id}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]

    def calculate_input_hash(self, input_text: str) -> str:
        """입력 텍스트 해시 계산"""
        return hashlib.sha256(input_text.encode()).hexdigest()[:16]

    def analyze_text_complexity(self, text: str) -> float:
        """텍스트 복잡도 분석"""
        # 간단한 복잡도 지표
        factors = {
            "length": len(text) / 100,  # 길이
            "sentences": text.count(".") + text.count("!") + text.count("?"),
            "words": len(text.split()),
            "unique_words": len(set(text.lower().split())),
            "punctuation": sum(1 for c in text if c in ".,!?;:"),
        }

        # 정규화 및 가중 평균
        normalized_length = min(factors["length"], 5) / 5
        sentence_complexity = min(factors["sentences"], 10) / 10
        word_diversity = factors["unique_words"] / max(factors["words"], 1)

        complexity = (
            normalized_length * 0.3 + sentence_complexity * 0.3 + word_diversity * 0.4
        )

        return min(complexity, 1.0)

    def calculate_consistency_score(
        self, echo_judgment: str, claude_judgment: str
    ) -> float:
        """Echo와 Claude 판단 일치도 계산"""
        if not echo_judgment or not claude_judgment:
            return 0.0

        # 간단한 유사도 계산 (실제로는 더 정교한 방법 사용)
        echo_words = set(echo_judgment.lower().split())
        claude_words = set(claude_judgment.lower().split())

        if not echo_words or not claude_words:
            return 0.0

        intersection = len(echo_words & claude_words)
        union = len(echo_words | claude_words)

        return intersection / union if union > 0 else 0.0

    def calculate_novelty_score(self, input_text: str) -> float:
        """새로운 패턴 정도 계산"""
        input_hash = self.calculate_input_hash(input_text)

        # 캐시에서 유사한 패턴 검색
        similar_patterns = 0
        for cached_hash, cached_data in self.pattern_cache.items():
            # 해시의 유사도 체크 (간단한 방법)
            if sum(a == b for a, b in zip(input_hash, cached_hash)) > 8:
                similar_patterns += 1

        # 새로운 패턴일수록 높은 점수
        novelty = 1.0 - (similar_patterns / max(len(self.pattern_cache), 1))

        # 패턴 캐시 업데이트
        self.pattern_cache[input_hash] = {
            "first_seen": datetime.now().isoformat(),
            "frequency": self.pattern_cache.get(input_hash, {}).get("frequency", 0) + 1,
        }

        return novelty

    def create_meta_data(
        self,
        input_text: str,
        echo_judgment: Optional[str] = None,
        claude_judgment: Optional[str] = None,
        final_judgment: str = "",
        confidence_score: float = 0.0,
        detected_emotion: Optional[str] = None,
        emotion_confidence: float = 0.0,
        suggested_strategy: Optional[str] = None,
        strategy_confidence: float = 0.0,
        processing_time: float = 0.0,
        echo_response_time: float = 0.0,
        claude_response_time: float = 0.0,
        user_context: Optional[str] = None,
        previous_judgments: List[str] = None,
    ) -> JudgmentMetaData:
        """메타데이터 생성"""

        timestamp = datetime.now()
        judgment_id = self.generate_judgment_id(input_text, timestamp)
        input_hash = self.calculate_input_hash(input_text)

        # 분석 지표 계산
        complexity_score = self.analyze_text_complexity(input_text)
        consistency_score = self.calculate_consistency_score(
            echo_judgment or "", claude_judgment or ""
        )
        novelty_score = self.calculate_novelty_score(input_text)

        return JudgmentMetaData(
            judgment_id=judgment_id,
            timestamp=timestamp,
            input_text=input_text,
            input_hash=input_hash,
            session_id=self.session_id,
            echo_judgment=echo_judgment,
            claude_judgment=claude_judgment,
            final_judgment=final_judgment,
            confidence_score=confidence_score,
            detected_emotion=detected_emotion,
            emotion_confidence=emotion_confidence,
            suggested_strategy=suggested_strategy,
            strategy_confidence=strategy_confidence,
            processing_time=processing_time,
            echo_response_time=echo_response_time,
            claude_response_time=claude_response_time,
            user_context=user_context,
            system_context={
                "session_id": self.session_id,
                "timestamp": timestamp.isoformat(),
                "system_version": "v10",
            },
            previous_judgments=previous_judgments or [],
            consistency_score=consistency_score,
            complexity_score=complexity_score,
            novelty_score=novelty_score,
        )

    def log_judgment(self, meta_data: JudgmentMetaData):
        """판단 메타데이터 로그"""
        with self.lock:
            try:
                # 세션 데이터에 추가
                self.current_session_data.append(meta_data)

                # 성능 집계 업데이트
                self.performance_aggregates["processing_times"].append(
                    meta_data.processing_time
                )
                self.performance_aggregates["confidence_scores"].append(
                    meta_data.confidence_score
                )
                self.performance_aggregates["consistency_scores"].append(
                    meta_data.consistency_score
                )
                self.performance_aggregates["complexity_scores"].append(
                    meta_data.complexity_score
                )
                self.performance_aggregates["novelty_scores"].append(
                    meta_data.novelty_score
                )

                # 개별 판단 파일 저장
                judgment_file = os.path.join(
                    self.log_directory, f"judgment_{meta_data.judgment_id}.json"
                )

                with open(judgment_file, "w", encoding="utf-8") as f:
                    json.dump(
                        asdict(meta_data), f, ensure_ascii=False, indent=2, default=str
                    )

                # 세션 집계 업데이트
                self._update_session_aggregates()

                print(f"✅ 메타 로그 저장: {meta_data.judgment_id}")

            except Exception as e:
                print(f"❌ 메타 로그 저장 실패: {e}")

    def _update_session_aggregates(self):
        """세션 집계 업데이트"""
        if not self.current_session_data:
            return

        # 집계 계산
        processing_times = [d.processing_time for d in self.current_session_data]
        confidence_scores = [d.confidence_score for d in self.current_session_data]
        consistency_scores = [d.consistency_score for d in self.current_session_data]

        aggregates = {
            "session_id": self.session_id,
            "last_updated": datetime.now().isoformat(),
            "total_judgments": len(self.current_session_data),
            "average_processing_time": sum(processing_times) / len(processing_times),
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "average_consistency": sum(consistency_scores) / len(consistency_scores),
            "emotion_distribution": self._calculate_distribution("detected_emotion"),
            "strategy_distribution": self._calculate_distribution("suggested_strategy"),
            "complexity_stats": {
                "min": min(d.complexity_score for d in self.current_session_data),
                "max": max(d.complexity_score for d in self.current_session_data),
                "avg": sum(d.complexity_score for d in self.current_session_data)
                / len(self.current_session_data),
            },
        }

        # 집계 파일 저장
        aggregates_file = os.path.join(
            self.log_directory, f"session_aggregates_{self.session_id}.json"
        )
        with open(aggregates_file, "w", encoding="utf-8") as f:
            json.dump(aggregates, f, ensure_ascii=False, indent=2)

    def _calculate_distribution(self, field: str) -> Dict[str, int]:
        """필드별 분포 계산"""
        distribution = defaultdict(int)
        for data in self.current_session_data:
            value = getattr(data, field, None)
            if value:
                distribution[value] += 1
        return dict(distribution)

    def get_session_summary(self) -> Dict[str, Any]:
        """세션 요약 정보 반환"""
        if not self.current_session_data:
            return {"message": "세션 데이터 없음"}

        latest_data = self.current_session_data[-1]

        return {
            "session_id": self.session_id,
            "total_judgments": len(self.current_session_data),
            "session_duration": str(
                datetime.now() - self.current_session_data[0].timestamp
            ),
            "latest_judgment": {
                "id": latest_data.judgment_id,
                "text": latest_data.input_text[:50] + "...",
                "judgment": latest_data.final_judgment,
                "confidence": latest_data.confidence_score,
                "emotion": latest_data.detected_emotion,
                "strategy": latest_data.suggested_strategy,
            },
            "performance_summary": {
                "avg_processing_time": sum(
                    d.processing_time for d in self.current_session_data
                )
                / len(self.current_session_data),
                "avg_confidence": sum(
                    d.confidence_score for d in self.current_session_data
                )
                / len(self.current_session_data),
                "avg_consistency": sum(
                    d.consistency_score for d in self.current_session_data
                )
                / len(self.current_session_data),
                "avg_complexity": sum(
                    d.complexity_score for d in self.current_session_data
                )
                / len(self.current_session_data),
                "avg_novelty": sum(d.novelty_score for d in self.current_session_data)
                / len(self.current_session_data),
            },
        }

    def analyze_patterns(self, lookback_days: int = 7) -> Dict[str, Any]:
        """패턴 분석"""
        # 지난 N일간의 로그 파일 수집
        cutoff_date = datetime.now() - timedelta(days=lookback_days)

        pattern_analysis = {
            "time_range": f"{lookback_days}일",
            "emotion_patterns": {},
            "strategy_patterns": {},
            "performance_trends": {},
            "complexity_trends": {},
            "novelty_insights": {},
        }

        # 패턴 분석 로직 (실제로는 더 복잡한 분석)
        emotion_counts = defaultdict(int)
        strategy_counts = defaultdict(int)

        for data in self.current_session_data:
            if data.timestamp >= cutoff_date:
                if data.detected_emotion:
                    emotion_counts[data.detected_emotion] += 1
                if data.suggested_strategy:
                    strategy_counts[data.suggested_strategy] += 1

        pattern_analysis["emotion_patterns"] = dict(emotion_counts)
        pattern_analysis["strategy_patterns"] = dict(strategy_counts)

        return pattern_analysis

    def export_learning_data(self, output_file: str = None) -> str:
        """학습 데이터 내보내기"""
        if output_file is None:
            output_file = f"learning_data_{self.session_id}.json"

        learning_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "total_samples": len(self.current_session_data),
            "data": [asdict(data) for data in self.current_session_data],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(learning_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ 학습 데이터 내보내기: {output_file}")
        return output_file


# 전역 메타 로거 인스턴스
_global_meta_logger = None


def get_meta_logger() -> JudgmentMetaLogger:
    """전역 메타 로거 반환"""
    global _global_meta_logger
    if _global_meta_logger is None:
        _global_meta_logger = JudgmentMetaLogger()
    return _global_meta_logger


def log_judgment_meta(input_text: str, **kwargs):
    """편의 함수: 판단 메타데이터 로그"""
    logger = get_meta_logger()
    meta_data = logger.create_meta_data(input_text, **kwargs)
    logger.log_judgment(meta_data)
    return meta_data


# 테스트 함수
def test_meta_logger():
    """메타 로거 테스트"""
    print("🧠 판단 메타 로거 테스트 시작...")

    logger = JudgmentMetaLogger()

    # 테스트 데이터 생성
    test_cases = [
        {
            "input_text": "오늘 정말 좋은 날이에요!",
            "echo_judgment": "긍정적인 하루",
            "claude_judgment": "기쁜 감정 표현",
            "final_judgment": "positive_day",
            "confidence_score": 0.95,
            "detected_emotion": "joy",
            "emotion_confidence": 0.9,
            "suggested_strategy": "empathetic",
            "strategy_confidence": 0.85,
            "processing_time": 0.234,
        },
        {
            "input_text": "복잡한 문제를 해결해야 해요.",
            "echo_judgment": "문제 해결 필요",
            "claude_judgment": "논리적 접근 권장",
            "final_judgment": "problem_solving",
            "confidence_score": 0.78,
            "detected_emotion": "neutral",
            "emotion_confidence": 0.7,
            "suggested_strategy": "logical",
            "strategy_confidence": 0.88,
            "processing_time": 0.456,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 테스트 케이스 {i}: {test_case['input_text']}")

        meta_data = logger.create_meta_data(**test_case)
        logger.log_judgment(meta_data)

        print(f"  📊 복잡도: {meta_data.complexity_score:.2f}")
        print(f"  🔄 일치도: {meta_data.consistency_score:.2f}")
        print(f"  ✨ 새로움: {meta_data.novelty_score:.2f}")

    # 세션 요약
    print("\n📋 세션 요약:")
    summary = logger.get_session_summary()
    print(f"  총 판단 수: {summary['total_judgments']}")
    print(
        f"  평균 처리 시간: {summary['performance_summary']['avg_processing_time']:.3f}초"
    )
    print(f"  평균 신뢰도: {summary['performance_summary']['avg_confidence']:.2f}")
    print(f"  평균 일치도: {summary['performance_summary']['avg_consistency']:.2f}")

    # 학습 데이터 내보내기
    export_file = logger.export_learning_data()
    print(f"\n💾 학습 데이터 내보내기: {export_file}")

    print("\n🎉 메타 로거 테스트 완료!")


if __name__ == "__main__":
    test_meta_logger()
