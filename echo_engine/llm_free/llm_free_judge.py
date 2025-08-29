"""
LLM-Free 판단기 - 규칙 기반 판단 시스템
Claude API 없이도 기본적인 판단 로직을 제공합니다.
"""

import json
import yaml
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .pattern_based_reasoner import PatternBasedReasoner


@dataclass
class JudgmentResult:
    """판단 결과 데이터 클래스"""

    judgment: str
    confidence: float
    reasoning_trace: List[str]
    emotion_detected: str
    strategy_suggested: str
    processing_time: float
    fallback_used: bool = True


class FallbackJudge:
    """
    LLM-Free 판단기
    규칙 기반 패턴 매칭을 통한 판단 시스템
    """

    def __init__(self, config_path: str = None, ruleset_path: str = None):
        """
        FallbackJudge 초기화

        Args:
            config_path: 판단 설정 파일 경로
            ruleset_path: 규칙 세트 파일 경로
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 기본 경로 설정
        if config_path is None:
            config_path = os.path.join(self.base_dir, "judge_config.yaml")
        if ruleset_path is None:
            ruleset_path = os.path.join(self.base_dir, "fallback_ruleset.json")

        # 설정 및 규칙 로드
        self.config = self._load_config(config_path)
        self.ruleset = self._load_ruleset(ruleset_path)

        # 패턴 기반 추론기 초기화
        self.reasoner = PatternBasedReasoner(self.ruleset)

        # 판단 통계
        self.stats = {
            "total_judgments": 0,
            "successful_judgments": 0,
            "failed_judgments": 0,
            "average_confidence": 0.0,
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 기본 설정 반환
            return {
                "judgment_mode": "pattern_based",
                "confidence_threshold": 0.6,
                "default_emotion": "neutral",
                "default_strategy": "balanced",
                "reasoning_depth": 3,
                "enable_fallback_chain": True,
            }

    def _load_ruleset(self, ruleset_path: str) -> Dict[str, Any]:
        """규칙 세트 로드"""
        try:
            with open(ruleset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 기본 규칙 세트 반환
            return {
                "emotion_patterns": {
                    "joy": ["기쁘", "행복", "좋", "최고", "성공", "축하"],
                    "sadness": ["슬프", "우울", "힘들", "속상", "실망", "포기"],
                    "anger": ["화", "짜증", "분노", "열받", "억울", "불만"],
                    "fear": ["무서", "걱정", "불안", "두려", "긴장", "스트레스"],
                    "surprise": ["놀라", "와우", "헐", "대박", "깜짝", "어머"],
                },
                "strategy_patterns": {
                    "logical": ["분석", "논리", "이성", "합리", "데이터", "객관적"],
                    "empathetic": ["감정", "공감", "이해", "마음", "느낌", "따뜻"],
                    "creative": [
                        "창의",
                        "새로운",
                        "혁신",
                        "아이디어",
                        "독창적",
                        "참신",
                    ],
                    "cautious": ["신중", "조심", "안전", "확실", "검토", "보수적"],
                },
                "context_patterns": {
                    "work": ["회의", "업무", "직장", "동료", "상사", "프로젝트"],
                    "personal": ["친구", "가족", "연인", "개인", "취미", "여행"],
                    "academic": ["공부", "학교", "시험", "과제", "교수", "학습"],
                    "social": ["모임", "파티", "사람들", "관계", "소통", "네트워킹"],
                },
            }

    def evaluate(self, input_data: Dict[str, Any]) -> JudgmentResult:
        """
        메인 판단 평가 함수

        Args:
            input_data: 판단 입력 데이터 (text, context 등)

        Returns:
            JudgmentResult: 판단 결과
        """
        start_time = datetime.now()

        try:
            # 입력 데이터 전처리
            text = input_data.get("text", str(input_data))
            context = input_data.get("context", "")

            # 패턴 기반 추론 수행
            reasoning_result = self.reasoner.reason(text, context)

            # 판단 결과 생성
            judgment = self._generate_judgment(reasoning_result)
            confidence = self._calculate_confidence(reasoning_result)

            # 감정 및 전략 추출
            emotion = reasoning_result.get("emotion", self.config["default_emotion"])
            strategy = reasoning_result.get("strategy", self.config["default_strategy"])

            # 추론 과정 기록
            reasoning_trace = self._build_reasoning_trace(reasoning_result)

            # 처리 시간 계산
            processing_time = (datetime.now() - start_time).total_seconds()

            # 결과 생성
            result = JudgmentResult(
                judgment=judgment,
                confidence=confidence,
                reasoning_trace=reasoning_trace,
                emotion_detected=emotion,
                strategy_suggested=strategy,
                processing_time=processing_time,
                fallback_used=True,
            )

            # 통계 업데이트
            self._update_stats(result)

            return result

        except Exception as e:
            # 오류 발생 시 기본 판단 반환
            processing_time = (datetime.now() - start_time).total_seconds()

            return JudgmentResult(
                judgment="판단 불가 - 입력 데이터 처리 중 오류 발생",
                confidence=0.0,
                reasoning_trace=[f"오류 발생: {str(e)}"],
                emotion_detected="neutral",
                strategy_suggested="cautious",
                processing_time=processing_time,
                fallback_used=True,
            )

    def _generate_judgment(self, reasoning_result: Dict[str, Any]) -> str:
        """추론 결과를 바탕으로 판단 생성"""
        emotion = reasoning_result.get("emotion", "neutral")
        strategy = reasoning_result.get("strategy", "balanced")
        context = reasoning_result.get("context", "general")

        # 감정-전략 조합에 따른 판단 템플릿
        judgment_templates = {
            (
                "joy",
                "empathetic",
            ): "긍정적인 상황입니다. 이 기쁨을 주변과 나누시면 좋겠어요.",
            (
                "sadness",
                "empathetic",
            ): "어려운 상황이시군요. 천천히 극복해 나가시길 응원합니다.",
            (
                "anger",
                "cautious",
            ): "화가 나시는 상황이지만, 냉정하게 접근해보시는 것이 좋겠습니다.",
            (
                "fear",
                "logical",
            ): "불안한 상황이지만, 차근차근 분석해보시면 해결책이 보일 것입니다.",
            (
                "surprise",
                "creative",
            ): "예상치 못한 상황이네요. 새로운 관점으로 접근해보시죠.",
            ("neutral", "balanced"): "상황을 균형있게 판단해보시는 것이 좋겠습니다.",
        }

        # 템플릿 매칭
        template_key = (emotion, strategy)
        if template_key in judgment_templates:
            return judgment_templates[template_key]

        # 기본 판단
        return (
            f"{emotion} 감정 상태에서 {strategy} 전략으로 접근하시는 것을 권장합니다."
        )

    def _calculate_confidence(self, reasoning_result: Dict[str, Any]) -> float:
        """판단 신뢰도 계산"""
        confidence = 0.0

        # 패턴 매칭 점수
        pattern_score = reasoning_result.get("pattern_score", 0.0)
        confidence += pattern_score * 0.4

        # 키워드 매칭 점수
        keyword_score = reasoning_result.get("keyword_score", 0.0)
        confidence += keyword_score * 0.3

        # 문맥 일치 점수
        context_score = reasoning_result.get("context_score", 0.0)
        confidence += context_score * 0.3

        # 0.0 ~ 1.0 범위로 정규화
        confidence = max(0.0, min(1.0, confidence))

        return round(confidence, 3)

    def _build_reasoning_trace(self, reasoning_result: Dict[str, Any]) -> List[str]:
        """추론 과정 기록 생성"""
        trace = []

        # 입력 분석
        if reasoning_result.get("input_analysis"):
            trace.append(f"입력 분석: {reasoning_result['input_analysis']}")

        # 패턴 매칭 결과
        if reasoning_result.get("matched_patterns"):
            patterns = ", ".join(reasoning_result["matched_patterns"])
            trace.append(f"매칭된 패턴: {patterns}")

        # 감정 분석
        if reasoning_result.get("emotion"):
            trace.append(f"감정 분석: {reasoning_result['emotion']}")

        # 전략 선택
        if reasoning_result.get("strategy"):
            trace.append(f"전략 선택: {reasoning_result['strategy']}")

        # 신뢰도 계산
        confidence = self._calculate_confidence(reasoning_result)
        trace.append(f"신뢰도: {confidence:.3f}")

        return trace

    def _update_stats(self, result: JudgmentResult):
        """판단 통계 업데이트"""
        self.stats["total_judgments"] += 1

        if result.confidence >= self.config["confidence_threshold"]:
            self.stats["successful_judgments"] += 1
        else:
            self.stats["failed_judgments"] += 1

        # 평균 신뢰도 계산
        total = self.stats["total_judgments"]
        current_avg = self.stats["average_confidence"]
        new_avg = (current_avg * (total - 1) + result.confidence) / total
        self.stats["average_confidence"] = round(new_avg, 3)

    def get_stats(self) -> Dict[str, Any]:
        """판단 통계 반환"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_judgments"]
                / max(self.stats["total_judgments"], 1)
            )
            * 100,
        }

    def reset_stats(self):
        """통계 초기화"""
        self.stats = {
            "total_judgments": 0,
            "successful_judgments": 0,
            "failed_judgments": 0,
            "average_confidence": 0.0,
        }


# 편의 함수
def quick_judgment(text: str, context: str = "") -> JudgmentResult:
    """빠른 판단 함수"""
    judge = FallbackJudge()
    return judge.evaluate({"text": text, "context": context})


if __name__ == "__main__":
    # 테스트 코드
    print("🧠 LLM-Free 판단기 테스트")

    judge = FallbackJudge()

    test_cases = [
        "오늘 승진 소식을 들었어요! 너무 기뻐요!",
        "회의에서 제안했는데 다들 조용해졌어요.",
        "요즘 스트레스가 너무 심해서 힘들어요.",
        "새로운 프로젝트 아이디어가 있는데 어떻게 시작해야 할까요?",
        "친구와 갈등이 있어서 고민이에요.",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        print(f"입력: {test_case}")

        result = judge.evaluate({"text": test_case})

        print(f"판단: {result.judgment}")
        print(f"신뢰도: {result.confidence:.3f}")
        print(f"감정: {result.emotion_detected}")
        print(f"전략: {result.strategy_suggested}")
        print(f"처리시간: {result.processing_time:.3f}초")
        print(f"추론과정: {' → '.join(result.reasoning_trace)}")

    # 통계 출력
    print(f"\n📊 판단 통계:")
    stats = judge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
