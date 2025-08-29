"""
패턴 기반 추론기
단순한 키워드/패턴 매칭을 통한 추론 시스템
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter


class PatternBasedReasoner:
    """
    패턴 기반 추론기
    키워드 매칭, 패턴 인식, 문맥 분석을 통한 추론
    """

    def __init__(self, ruleset: Dict[str, Any]):
        """
        추론기 초기화

        Args:
            ruleset: 규칙 세트 (감정, 전략, 문맥 패턴)
        """
        self.ruleset = ruleset
        self.emotion_patterns = ruleset.get("emotion_patterns", {})
        self.strategy_patterns = ruleset.get("strategy_patterns", {})
        self.context_patterns = ruleset.get("context_patterns", {})

        # 추론 가중치 설정
        self.weights = {"emotion": 0.4, "strategy": 0.3, "context": 0.3}

    def reason(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        메인 추론 함수

        Args:
            text: 분석할 텍스트
            context: 추가 문맥 정보

        Returns:
            추론 결과 딕셔너리
        """
        # 텍스트 전처리
        processed_text = self._preprocess_text(text)
        processed_context = self._preprocess_text(context)

        # 각 차원별 분석
        emotion_analysis = self._analyze_emotion(processed_text)
        strategy_analysis = self._analyze_strategy(processed_text)
        context_analysis = self._analyze_context(processed_text, processed_context)

        # 키워드 분석
        keywords = self._extract_keywords(processed_text)

        # 패턴 매칭
        matched_patterns = self._match_patterns(processed_text)

        # 종합 점수 계산
        scores = self._calculate_scores(
            emotion_analysis, strategy_analysis, context_analysis
        )

        # 최종 추론 결과 생성
        reasoning_result = {
            "input_analysis": f"텍스트 길이: {len(text)}자, 키워드 수: {len(keywords)}개",
            "emotion": emotion_analysis["top_emotion"],
            "emotion_score": emotion_analysis["score"],
            "strategy": strategy_analysis["top_strategy"],
            "strategy_score": strategy_analysis["score"],
            "context": context_analysis["top_context"],
            "context_score": context_analysis["score"],
            "keywords": keywords,
            "matched_patterns": matched_patterns,
            "pattern_score": scores["pattern_score"],
            "keyword_score": scores["keyword_score"],
            "overall_score": scores["overall_score"],
        }

        return reasoning_result

    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        if not text:
            return ""

        # 기본 정리
        text = text.strip().lower()

        # 특수 문자 제거 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r"[^\w\s가-힣]", " ", text)

        # 중복 공백 제거
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """감정 분석"""
        emotion_scores = defaultdict(float)

        for emotion, keywords in self.emotion_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    # 키워드 출현 횟수에 따른 가중치
                    count = text.count(keyword)
                    emotion_scores[emotion] += count * 1.0

        # 최고 점수 감정 선택
        if emotion_scores:
            top_emotion = max(emotion_scores, key=emotion_scores.get)
            max_score = emotion_scores[top_emotion]

            # 정규화 (0.0 ~ 1.0)
            normalized_score = min(max_score / 3.0, 1.0)
        else:
            top_emotion = "neutral"
            normalized_score = 0.5

        return {
            "top_emotion": top_emotion,
            "score": normalized_score,
            "all_scores": dict(emotion_scores),
        }

    def _analyze_strategy(self, text: str) -> Dict[str, Any]:
        """전략 분석"""
        strategy_scores = defaultdict(float)

        for strategy, keywords in self.strategy_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    count = text.count(keyword)
                    strategy_scores[strategy] += count * 1.0

        # 최고 점수 전략 선택
        if strategy_scores:
            top_strategy = max(strategy_scores, key=strategy_scores.get)
            max_score = strategy_scores[top_strategy]
            normalized_score = min(max_score / 2.0, 1.0)
        else:
            top_strategy = "balanced"
            normalized_score = 0.5

        return {
            "top_strategy": top_strategy,
            "score": normalized_score,
            "all_scores": dict(strategy_scores),
        }

    def _analyze_context(self, text: str, context: str) -> Dict[str, Any]:
        """문맥 분석"""
        context_scores = defaultdict(float)
        combined_text = f"{text} {context}".strip()

        for ctx_type, keywords in self.context_patterns.items():
            for keyword in keywords:
                if keyword in combined_text:
                    count = combined_text.count(keyword)
                    context_scores[ctx_type] += count * 1.0

        # 최고 점수 문맥 선택
        if context_scores:
            top_context = max(context_scores, key=context_scores.get)
            max_score = context_scores[top_context]
            normalized_score = min(max_score / 2.0, 1.0)
        else:
            top_context = "general"
            normalized_score = 0.3

        return {
            "top_context": top_context,
            "score": normalized_score,
            "all_scores": dict(context_scores),
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        if not text:
            return []

        # 단어 분리
        words = text.split()

        # 불용어 제거
        stop_words = {
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "의",
            "에",
            "에서",
            "으로",
            "와",
            "과",
            "그리고",
            "하지만",
            "그런데",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 1]

        # 중복 제거 및 빈도 기준 정렬
        keyword_counts = Counter(keywords)

        # 상위 10개 키워드 반환
        return [word for word, count in keyword_counts.most_common(10)]

    def _match_patterns(self, text: str) -> List[str]:
        """패턴 매칭"""
        matched_patterns = []

        # 질문 패턴
        if "?" in text or any(
            word in text for word in ["어떻게", "왜", "무엇", "언제", "어디서"]
        ):
            matched_patterns.append("question_pattern")

        # 감정 표현 패턴
        if any(word in text for word in ["너무", "정말", "아주", "엄청", "완전"]):
            matched_patterns.append("emotion_intensifier")

        # 부정 표현 패턴
        if any(word in text for word in ["안", "못", "아니", "없", "말고"]):
            matched_patterns.append("negative_expression")

        # 긍정 표현 패턴
        if any(word in text for word in ["좋", "잘", "성공", "완성", "해냈"]):
            matched_patterns.append("positive_expression")

        # 요청 패턴
        if any(word in text for word in ["도와주", "부탁", "조언", "추천", "제안"]):
            matched_patterns.append("request_pattern")

        # 고민 패턴
        if any(word in text for word in ["고민", "걱정", "불안", "어려움", "힘들"]):
            matched_patterns.append("concern_pattern")

        return matched_patterns

    def _calculate_scores(
        self, emotion_analysis: Dict, strategy_analysis: Dict, context_analysis: Dict
    ) -> Dict[str, float]:
        """점수 계산"""
        # 패턴 점수 (각 분석의 점수 평균)
        pattern_score = (
            emotion_analysis["score"] * self.weights["emotion"]
            + strategy_analysis["score"] * self.weights["strategy"]
            + context_analysis["score"] * self.weights["context"]
        )

        # 키워드 점수 (감정 + 전략 키워드 매칭도)
        keyword_score = (emotion_analysis["score"] + strategy_analysis["score"]) / 2.0

        # 전체 점수
        overall_score = (pattern_score + keyword_score) / 2.0

        return {
            "pattern_score": round(pattern_score, 3),
            "keyword_score": round(keyword_score, 3),
            "overall_score": round(overall_score, 3),
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """감정 분석 (단순 버전)"""
        emotion_analysis = self._analyze_emotion(self._preprocess_text(text))
        return {
            "sentiment": emotion_analysis["top_emotion"],
            "confidence": emotion_analysis["score"],
            "details": emotion_analysis["all_scores"],
        }

    def suggest_strategy(self, text: str) -> Dict[str, Any]:
        """전략 제안"""
        strategy_analysis = self._analyze_strategy(self._preprocess_text(text))
        return {
            "strategy": strategy_analysis["top_strategy"],
            "confidence": strategy_analysis["score"],
            "details": strategy_analysis["all_scores"],
        }

    def detect_context(self, text: str, context: str = "") -> Dict[str, Any]:
        """문맥 감지"""
        context_analysis = self._analyze_context(
            self._preprocess_text(text), self._preprocess_text(context)
        )
        return {
            "context": context_analysis["top_context"],
            "confidence": context_analysis["score"],
            "details": context_analysis["all_scores"],
        }


# 편의 함수들
def quick_emotion_analysis(text: str) -> str:
    """빠른 감정 분석"""
    # 기본 규칙 세트
    basic_ruleset = {
        "emotion_patterns": {
            "joy": ["기쁘", "행복", "좋", "최고", "성공"],
            "sadness": ["슬프", "우울", "힘들", "속상", "실망"],
            "anger": ["화", "짜증", "분노", "열받", "억울"],
            "fear": ["무서", "걱정", "불안", "두려", "긴장"],
            "surprise": ["놀라", "와우", "헐", "대박", "깜짝"],
        },
        "strategy_patterns": {},
        "context_patterns": {},
    }

    reasoner = PatternBasedReasoner(basic_ruleset)
    result = reasoner.analyze_sentiment(text)
    return result["sentiment"]


def quick_strategy_suggestion(text: str) -> str:
    """빠른 전략 제안"""
    basic_ruleset = {
        "emotion_patterns": {},
        "strategy_patterns": {
            "logical": ["분석", "논리", "이성", "합리", "데이터"],
            "empathetic": ["감정", "공감", "이해", "마음", "느낌"],
            "creative": ["창의", "새로운", "혁신", "아이디어", "독창적"],
            "cautious": ["신중", "조심", "안전", "확실", "검토"],
        },
        "context_patterns": {},
    }

    reasoner = PatternBasedReasoner(basic_ruleset)
    result = reasoner.suggest_strategy(text)
    return result["strategy"]


if __name__ == "__main__":
    # 테스트 코드
    print("🔍 패턴 기반 추론기 테스트")

    # 테스트 규칙 세트
    test_ruleset = {
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
            "creative": ["창의", "새로운", "혁신", "아이디어", "독창적", "참신"],
            "cautious": ["신중", "조심", "안전", "확실", "검토", "보수적"],
        },
        "context_patterns": {
            "work": ["회의", "업무", "직장", "동료", "상사", "프로젝트"],
            "personal": ["친구", "가족", "연인", "개인", "취미", "여행"],
            "academic": ["공부", "학교", "시험", "과제", "교수", "학습"],
            "social": ["모임", "파티", "사람들", "관계", "소통", "네트워킹"],
        },
    }

    reasoner = PatternBasedReasoner(test_ruleset)

    test_cases = [
        "오늘 승진 소식을 들었어요! 정말 기뻐요!",
        "회의에서 데이터 분석 결과를 발표했습니다.",
        "친구와 갈등이 있어서 마음이 아파요.",
        "새로운 창의적 아이디어가 생각났어요!",
        "시험이 다가와서 너무 걱정되고 불안해요.",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        print(f"입력: {test_case}")

        result = reasoner.reason(test_case)

        print(f"감정: {result['emotion']} (신뢰도: {result['emotion_score']:.3f})")
        print(f"전략: {result['strategy']} (신뢰도: {result['strategy_score']:.3f})")
        print(f"문맥: {result['context']} (신뢰도: {result['context_score']:.3f})")
        print(f"키워드: {', '.join(result['keywords'])}")
        print(f"패턴: {', '.join(result['matched_patterns'])}")
        print(f"전체 점수: {result['overall_score']:.3f}")

    # 개별 분석 테스트
    print(f"\n🔍 개별 분석 테스트:")
    test_text = "정말 기쁘지만 조심스럽게 접근해야겠어요"

    emotion = reasoner.analyze_sentiment(test_text)
    strategy = reasoner.suggest_strategy(test_text)
    context = reasoner.detect_context(test_text)

    print(f"감정 분석: {emotion}")
    print(f"전략 제안: {strategy}")
    print(f"문맥 감지: {context}")
