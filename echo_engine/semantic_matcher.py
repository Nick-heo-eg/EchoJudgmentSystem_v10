#!/usr/bin/env python3
"""
🧠 Semantic Matcher - KoSimCSE 기반 의미 유사도 매칭 시스템
자연어 입력의 의미적 유사성을 계산하여 정확한 의도 분류 지원

핵심 기능:
1. KoSimCSE 모델을 활용한 한국어 문장 임베딩
2. 의미적 유사도 계산 및 매칭
3. 코딩 의도 분류 정확도 향상
4. Echo 시그니처별 특화된 매칭 알고리즘
5. 폴백 모드 (KoSimCSE 없이도 동작)
"""

import numpy as np
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# KoSimCSE 및 관련 라이브러리 import (선택적)
KOSIMCSE_AVAILABLE = False
try:
    import torch
    from transformers import AutoModel, AutoTokenizer

    KOSIMCSE_AVAILABLE = True
    print("✅ KoSimCSE 라이브러리 로드 완료")
except ImportError as e:
    print(f"⚠️ KoSimCSE 라이브러리 없음: {e}")
    print("🔄 폴백 모드로 동작합니다")


@dataclass
class SemanticMatchResult:
    """의미 매칭 결과"""

    query: str
    best_match: str
    similarity_score: float
    confidence: float
    matched_category: str
    alternative_matches: List[Dict[str, Any]]
    matching_method: str


@dataclass
class IntentTemplate:
    """의도 템플릿"""

    category: str
    intent_name: str
    example_phrases: List[str]
    keywords: List[str]
    signature_preference: str
    complexity_hint: str


class KoSimCSEMatcher:
    """🚀 KoSimCSE 기반 의미 매칭기"""

    def __init__(self, model_name: str = "BM-K/KoSimCSE-roberta-multitask"):
        global KOSIMCSE_AVAILABLE
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cpu"  # CPU 우선 사용
        self.available = KOSIMCSE_AVAILABLE

        if KOSIMCSE_AVAILABLE:
            try:
                self._load_model()
                print(f"✅ KoSimCSE 모델 로드 완료: {model_name}")
            except Exception as e:
                print(f"❌ KoSimCSE 모델 로드 실패: {e}")
                self.available = False

    def _load_model(self):
        """KoSimCSE 모델 로드"""
        if not self.available:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)

        # GPU 사용 가능하면 GPU로, 아니면 CPU
        if torch.cuda.is_available():
            self.device = "cuda"
            self.model = self.model.to(self.device)

        self.model.eval()

    def encode_sentences(self, sentences: List[str]) -> np.ndarray:
        """문장들을 벡터로 인코딩"""
        if not self.available or not self.model:
            # 폴백: TF-IDF 유사 벡터화
            return self._fallback_encode(sentences)

        try:
            with torch.no_grad():
                # 토큰화
                inputs = self.tokenizer(
                    sentences,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512,
                ).to(self.device)

                # 모델 추론
                outputs = self.model(**inputs)

                # [CLS] 토큰의 임베딩 사용
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

                return embeddings

        except Exception as e:
            print(f"⚠️ KoSimCSE 인코딩 실패: {e}")
            return self._fallback_encode(sentences)

    def _fallback_encode(self, sentences: List[str]) -> np.ndarray:
        """폴백 인코딩 (간단한 TF-IDF 유사)"""
        from collections import Counter
        import math

        # 간단한 한국어 토큰화
        def tokenize_korean(text):
            # 기본적인 한국어 처리
            text = re.sub(r"[^\w\s가-힣]", " ", text.lower())
            return text.split()

        # 모든 문장의 토큰 수집
        all_tokens = []
        tokenized_sentences = []

        for sentence in sentences:
            tokens = tokenize_korean(sentence)
            tokenized_sentences.append(tokens)
            all_tokens.extend(tokens)

        # 단어 빈도 계산
        vocab = list(set(all_tokens))
        vocab_size = len(vocab)

        # TF-IDF 유사 벡터 생성
        vectors = []
        for tokens in tokenized_sentences:
            vector = np.zeros(vocab_size)
            token_count = Counter(tokens)

            for i, word in enumerate(vocab):
                if word in token_count:
                    tf = token_count[word] / len(tokens)
                    # 간단한 IDF 계산
                    df = sum(
                        1 for sent_tokens in tokenized_sentences if word in sent_tokens
                    )
                    idf = math.log(len(sentences) / (df + 1))
                    vector[i] = tf * idf

            vectors.append(vector)

        return np.array(vectors)

    def calculate_similarity(self, query: str, candidates: List[str]) -> List[float]:
        """쿼리와 후보들 간의 유사도 계산"""
        all_sentences = [query] + candidates
        embeddings = self.encode_sentences(all_sentences)

        query_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]

        # 코사인 유사도 계산
        similarities = []
        for candidate_emb in candidate_embeddings:
            # 정규화
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            candidate_norm = candidate_emb / np.linalg.norm(candidate_emb)

            # 코사인 유사도
            similarity = np.dot(query_norm, candidate_norm.T)[0][0]
            similarities.append(float(similarity))

        return similarities


class SemanticMatcher:
    """🎯 통합 의미 매칭 엔진"""

    def __init__(self):
        # KoSimCSE 매칭기 초기화
        self.kosimcse_matcher = KoSimCSEMatcher() if KOSIMCSE_AVAILABLE else None

        # 의도 템플릿 로드
        self.intent_templates = self._load_intent_templates()

        # 매칭 히스토리
        self.matching_history = []

        print("🎯 Semantic Matcher 초기화 완료")
        print(f"   KoSimCSE: {'✅ 활성화' if KOSIMCSE_AVAILABLE else '❌ 폴백 모드'}")
        print(f"   의도 템플릿: {len(self.intent_templates)}개")

    def match_coding_intent(
        self, user_input: str, threshold: float = 0.6
    ) -> SemanticMatchResult:
        """코딩 의도 매칭"""

        # 1. 템플릿별 매칭 점수 계산
        match_scores = []

        for template in self.intent_templates:
            if template.category == "coding":
                # 예시 문장들과 유사도 계산
                if self.kosimcse_matcher:
                    similarities = self.kosimcse_matcher.calculate_similarity(
                        user_input, template.example_phrases
                    )
                    max_similarity = max(similarities) if similarities else 0.0
                else:
                    # 폴백: 키워드 기반 매칭
                    max_similarity = self._keyword_based_similarity(
                        user_input, template
                    )

                match_scores.append(
                    {
                        "template": template,
                        "similarity": max_similarity,
                        "intent_name": template.intent_name,
                    }
                )

        # 2. 최고 점수 선택
        if not match_scores:
            return self._create_fallback_result(user_input)

        best_match = max(match_scores, key=lambda x: x["similarity"])

        # 3. 신뢰도 계산
        confidence = self._calculate_confidence(best_match["similarity"], match_scores)

        # 4. 대안 매칭 생성
        alternative_matches = sorted(
            [score for score in match_scores if score != best_match],
            key=lambda x: x["similarity"],
            reverse=True,
        )[
            :3
        ]  # 상위 3개

        # 5. 결과 구성
        result = SemanticMatchResult(
            query=user_input,
            best_match=best_match["template"].intent_name,
            similarity_score=best_match["similarity"],
            confidence=confidence,
            matched_category="coding",
            alternative_matches=[
                {
                    "intent": alt["intent_name"],
                    "similarity": alt["similarity"],
                    "signature_preference": alt["template"].signature_preference,
                }
                for alt in alternative_matches
            ],
            matching_method="kosimcse" if self.kosimcse_matcher else "keyword_fallback",
        )

        # 6. 히스토리 기록
        self.matching_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "query": user_input,
                "result": result.best_match,
                "confidence": confidence,
            }
        )

        return result

    def _keyword_based_similarity(
        self, user_input: str, template: IntentTemplate
    ) -> float:
        """키워드 기반 유사도 계산 (폴백)"""
        user_words = set(re.findall(r"\w+", user_input.lower()))
        template_words = set()

        # 키워드 추가
        for keyword in template.keywords:
            template_words.update(re.findall(r"\w+", keyword.lower()))

        # 예시 문장의 단어들도 추가
        for phrase in template.example_phrases:
            template_words.update(re.findall(r"\w+", phrase.lower()))

        # 자카드 유사도 계산
        intersection = len(user_words & template_words)
        union = len(user_words | template_words)

        return intersection / union if union > 0 else 0.0

    def _calculate_confidence(self, best_score: float, all_scores: List[Dict]) -> float:
        """신뢰도 계산"""
        if len(all_scores) < 2:
            return min(best_score, 0.8)  # 단일 매칭은 최대 0.8

        # 상위 2개 점수 차이로 신뢰도 계산
        sorted_scores = sorted(all_scores, key=lambda x: x["similarity"], reverse=True)
        score_gap = sorted_scores[0]["similarity"] - sorted_scores[1]["similarity"]

        # 점수 차이가 클수록 신뢰도 높음
        confidence = best_score * (1 + score_gap)
        return min(confidence, 0.95)  # 최대 0.95

    def _create_fallback_result(self, user_input: str) -> SemanticMatchResult:
        """폴백 결과 생성"""
        return SemanticMatchResult(
            query=user_input,
            best_match="general_coding",
            similarity_score=0.3,
            confidence=0.4,
            matched_category="coding",
            alternative_matches=[],
            matching_method="fallback",
        )

    def _load_intent_templates(self) -> List[IntentTemplate]:
        """의도 템플릿 로드"""
        return [
            IntentTemplate(
                category="coding",
                intent_name="streamlit_app_creation",
                example_phrases=[
                    "스트림릿 앱 만들어줘",
                    "대시보드 개발해줘",
                    "웹 앱 만들어줘",
                    "데이터 시각화 앱 제작해줘",
                    "인터랙티브 차트 앱 만들어줘",
                ],
                keywords=[
                    "스트림릿",
                    "streamlit",
                    "대시보드",
                    "웹앱",
                    "시각화",
                    "차트",
                ],
                signature_preference="Aurora",
                complexity_hint="intermediate",
            ),
            IntentTemplate(
                category="coding",
                intent_name="data_analysis_script",
                example_phrases=[
                    "데이터 분석 스크립트 만들어줘",
                    "CSV 파일 분석해줘",
                    "통계 분석 코드 작성해줘",
                    "데이터 시각화 해줘",
                    "엑셀 데이터 처리해줘",
                ],
                keywords=["데이터", "분석", "csv", "엑셀", "통계", "시각화"],
                signature_preference="Sage",
                complexity_hint="intermediate",
            ),
            IntentTemplate(
                category="coding",
                intent_name="web_scraping_script",
                example_phrases=[
                    "웹 크롤링 스크립트 만들어줘",
                    "웹사이트 데이터 수집해줘",
                    "뉴스 기사 스크래핑해줘",
                    "웹페이지 정보 추출해줘",
                    "사이트 데이터 가져와줘",
                ],
                keywords=["크롤링", "스크래핑", "웹", "수집", "파싱", "추출"],
                signature_preference="Phoenix",
                complexity_hint="advanced",
            ),
            IntentTemplate(
                category="coding",
                intent_name="automation_script",
                example_phrases=[
                    "자동화 스크립트 만들어줘",
                    "반복 작업 자동화해줘",
                    "배치 처리 스크립트 작성해줘",
                    "파일 처리 자동화해줘",
                    "업무 자동화 도구 만들어줘",
                ],
                keywords=["자동화", "반복", "배치", "처리", "스케줄"],
                signature_preference="Companion",
                complexity_hint="intermediate",
            ),
            IntentTemplate(
                category="coding",
                intent_name="interactive_game",
                example_phrases=[
                    "간단한 게임 만들어줘",
                    "텍스트 게임 만들어줘",
                    "퀴즈 게임 개발해줘",
                    "인터랙티브 프로그램 만들어줘",
                    "미니게임 코드 작성해줘",
                ],
                keywords=["게임", "퀴즈", "인터랙티브", "놀이", "엔터테인먼트"],
                signature_preference="Aurora",
                complexity_hint="simple",
            ),
            IntentTemplate(
                category="coding",
                intent_name="api_integration",
                example_phrases=[
                    "API 연동 코드 만들어줘",
                    "REST API 클라이언트 개발해줘",
                    "외부 서비스 연결해줘",
                    "API 호출 스크립트 작성해줘",
                    "웹 서비스 통합해줘",
                ],
                keywords=["api", "rest", "연동", "서비스", "http", "json"],
                signature_preference="Phoenix",
                complexity_hint="advanced",
            ),
            IntentTemplate(
                category="coding",
                intent_name="utility_tool",
                example_phrases=[
                    "유틸리티 도구 만들어줘",
                    "편의 프로그램 개발해줘",
                    "도구 프로그램 작성해줘",
                    "헬퍼 스크립트 만들어줘",
                    "사용자 도구 개발해줘",
                ],
                keywords=["도구", "유틸리티", "헬퍼", "편의", "프로그램"],
                signature_preference="Companion",
                complexity_hint="simple",
            ),
        ]

    def enhance_intent_detection(
        self, user_input: str, existing_intent: str, existing_confidence: float
    ) -> Dict[str, Any]:
        """기존 의도 감지 결과 향상"""
        semantic_result = self.match_coding_intent(user_input)

        # 기존 결과와 의미적 매칭 결과 결합
        enhanced_confidence = (existing_confidence + semantic_result.confidence) / 2

        # 더 나은 매칭이 있으면 업데이트
        if semantic_result.confidence > existing_confidence + 0.1:  # 10% 이상 높으면
            return {
                "enhanced_intent": semantic_result.best_match,
                "enhanced_confidence": semantic_result.confidence,
                "semantic_alternatives": semantic_result.alternative_matches,
                "improvement": "semantic_override",
                "original_intent": existing_intent,
                "original_confidence": existing_confidence,
            }
        else:
            return {
                "enhanced_intent": existing_intent,
                "enhanced_confidence": enhanced_confidence,
                "semantic_alternatives": semantic_result.alternative_matches,
                "improvement": "confidence_boost",
                "original_intent": existing_intent,
                "original_confidence": existing_confidence,
            }

    def get_matching_stats(self) -> Dict[str, Any]:
        """매칭 통계 반환"""
        if not self.matching_history:
            return {"message": "매칭 히스토리 없음"}

        total_matches = len(self.matching_history)
        avg_confidence = (
            sum(h["confidence"] for h in self.matching_history) / total_matches
        )

        intent_distribution = {}
        for history in self.matching_history:
            intent = history["result"]
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1

        return {
            "total_matches": total_matches,
            "average_confidence": avg_confidence,
            "intent_distribution": intent_distribution,
            "kosimcse_enabled": KOSIMCSE_AVAILABLE,
            "recent_matches": self.matching_history[-5:],  # 최근 5개
        }


# 편의 함수들
def create_semantic_matcher() -> SemanticMatcher:
    """의미 매칭기 생성"""
    return SemanticMatcher()


def quick_semantic_match(user_input: str) -> str:
    """빠른 의미 매칭 (결과만 반환)"""
    matcher = create_semantic_matcher()
    result = matcher.match_coding_intent(user_input)
    return result.best_match


# 테스트 실행
if __name__ == "__main__":
    print("🧠 Semantic Matcher KoSimCSE 통합 테스트 시작...")

    matcher = create_semantic_matcher()

    # 테스트 케이스들
    test_queries = [
        "매출 데이터 분석하는 스트림릿 대시보드 만들어줘",
        "뉴스 사이트에서 제목들 크롤링하는 스크립트 필요해",
        "CSV 파일 읽어서 차트 그리는 코드 작성해줘",
        "간단한 계산기 게임 만들어줘",
        "파일들 자동으로 정리하는 프로그램 개발해줘",
        "날씨 API 연결해서 정보 가져오는 코드 만들어줘",
        "일정 관리하는 유틸리티 도구 만들어줘",
    ]

    print("=" * 80)

    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 테스트 {i}: {query}")

        result = matcher.match_coding_intent(query)

        print(f"📊 매칭 결과:")
        print(f"  최적 의도: {result.best_match}")
        print(f"  유사도: {result.similarity_score:.3f}")
        print(f"  신뢰도: {result.confidence:.3f}")
        print(f"  매칭 방법: {result.matching_method}")

        if result.alternative_matches:
            print(f"  대안 매칭:")
            for alt in result.alternative_matches[:2]:  # 상위 2개만
                print(f"    - {alt['intent']}: {alt['similarity']:.3f}")

        print("-" * 60)

    # 통계 출력
    print(f"\n📈 매칭 통계:")
    stats = matcher.get_matching_stats()
    for key, value in stats.items():
        if key == "recent_matches":
            continue
        elif isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        elif isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    print("\n✅ Semantic Matcher 테스트 완료!")

    if KOSIMCSE_AVAILABLE:
        print("🚀 KoSimCSE를 활용한 고정밀도 의미 매칭이 활성화되었습니다!")
    else:
        print(
            "🔄 폴백 모드로 동작 중입니다. 더 정확한 매칭을 위해 PyTorch와 transformers 설치를 권장합니다."
        )
