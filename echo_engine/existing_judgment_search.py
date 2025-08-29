#!/usr/bin/env python3
"""
🔍 Existing Judgment Search v1.0 - 기존 판단 탐색기

저장된 판단 결과에서 유사한 판단을 찾아 재사용하는 모듈.
벡터 유사도 기반 탐색과 키워드 매칭을 통해 효율적인 판단 재활용.

핵심 기능:
1. 텍스트 유사도 기반 판단 탐색
2. 키워드 매칭 보조 탐색
3. 시그니처별 필터링
4. 신뢰도 기반 결과 반환
"""

import os
import json
import re
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import Counter

# 유사도 계산을 위한 임포트 (선택적)
EMBEDDING_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False


@dataclass
class CachedJudgment:
    """캐시된 판단 정보"""

    input: str
    normalized_input: str
    emotion: str
    emotion_confidence: float
    strategy: str
    strategy_confidence: float
    template: str
    styled_sentence: str
    signature: str
    timestamp: datetime
    usage_count: int = 1
    similarity_score: float = 0.0


class ExistingJudgmentSearcher:
    """🔍 기존 판단 탐색기"""

    def __init__(self, cache_dir: str = "data/judgment_cache"):
        """
        초기화

        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.version = "1.0.0"
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "judgment_cache.jsonl")

        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)

        # 임베딩 모델 (사용 가능한 경우)
        self.embedding_model = None
        global EMBEDDING_AVAILABLE
        if EMBEDDING_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(
                    "BM-K/KoSimCSE-roberta-multitask"
                )
                print("✅ 유사도 임베딩 모델 로드 완료")
            except Exception as e:
                print(f"⚠️ 임베딩 모델 로드 실패: {e}")
                EMBEDDING_AVAILABLE = False

        # 캐시된 판단 로드
        self.cached_judgments: List[CachedJudgment] = []
        self._load_cached_judgments()

        # 통계
        self.stats = {
            "total_searches": 0,
            "successful_matches": 0,
            "cache_size": len(self.cached_judgments),
            "embedding_searches": 0,
            "keyword_searches": 0,
        }

        print(f"🔍 ExistingJudgmentSearcher v{self.version} 초기화 완료")
        print(f"   캐시된 판단: {len(self.cached_judgments)}개")
        print(f"   임베딩 유사도: {'✅' if EMBEDDING_AVAILABLE else '❌'}")

    def _load_cached_judgments(self):
        """캐시된 판단 로드"""
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())

                        # datetime 파싱
                        timestamp = datetime.fromisoformat(
                            data.get("timestamp", datetime.now().isoformat())
                        )

                        judgment = CachedJudgment(
                            input=data.get("input", ""),
                            normalized_input=data.get("normalized_input", ""),
                            emotion=data.get("emotion", "neutral"),
                            emotion_confidence=data.get("emotion_confidence", 0.5),
                            strategy=data.get("strategy", "analyze"),
                            strategy_confidence=data.get("strategy_confidence", 0.5),
                            template=data.get("template", ""),
                            styled_sentence=data.get("styled_sentence", ""),
                            signature=data.get("signature", "Selene"),
                            timestamp=timestamp,
                            usage_count=data.get("usage_count", 1),
                        )

                        self.cached_judgments.append(judgment)

            print(f"✅ {len(self.cached_judgments)}개 캐시된 판단 로드 완료")

        except Exception as e:
            print(f"⚠️ 캐시 로드 실패: {e}")

    def search_similar_judgment(
        self, normalized_input: str, signature: str = "Selene", threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        유사한 판단 탐색

        Args:
            normalized_input: 정규화된 입력
            signature: 시그니처
            threshold: 유사도 임계값

        Returns:
            유사한 판단 결과 (없으면 None)
        """
        self.stats["total_searches"] += 1

        if not self.cached_judgments:
            return None

        # 시그니처별 필터링 (선택적)
        signature_filtered = [
            j for j in self.cached_judgments if j.signature == signature
        ]

        candidates = signature_filtered if signature_filtered else self.cached_judgments

        # 1차: 임베딩 기반 유사도 탐색
        global EMBEDDING_AVAILABLE
        if EMBEDDING_AVAILABLE and self.embedding_model:
            best_match = self._embedding_similarity_search(
                normalized_input, candidates, threshold
            )
            if best_match:
                self.stats["successful_matches"] += 1
                self.stats["embedding_searches"] += 1
                return self._judgment_to_dict(best_match)

        # 2차: 키워드 기반 유사도 탐색 (fallback)
        best_match = self._keyword_similarity_search(
            normalized_input, candidates, threshold
        )
        if best_match:
            self.stats["successful_matches"] += 1
            self.stats["keyword_searches"] += 1
            return self._judgment_to_dict(best_match)

        return None

    def _embedding_similarity_search(
        self, input_text: str, candidates: List[CachedJudgment], threshold: float
    ) -> Optional[CachedJudgment]:
        """임베딩 기반 유사도 탐색"""
        try:
            # 입력 텍스트 임베딩
            input_embedding = self.embedding_model.encode([input_text])[0]

            best_match = None
            best_score = 0.0

            for judgment in candidates:
                # 캐시된 텍스트 임베딩
                cached_embedding = self.embedding_model.encode(
                    [judgment.normalized_input]
                )[0]

                # 코사인 유사도 계산
                similarity = np.dot(input_embedding, cached_embedding) / (
                    np.linalg.norm(input_embedding) * np.linalg.norm(cached_embedding)
                )

                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = judgment
                    best_match.similarity_score = similarity

            return best_match

        except Exception as e:
            print(f"⚠️ 임베딩 유사도 탐색 실패: {e}")
            return None

    def _keyword_similarity_search(
        self, input_text: str, candidates: List[CachedJudgment], threshold: float
    ) -> Optional[CachedJudgment]:
        """키워드 기반 유사도 탐색 (fallback)"""
        try:
            input_tokens = self._tokenize_korean(input_text)

            best_match = None
            best_score = 0.0

            for judgment in candidates:
                cached_tokens = self._tokenize_korean(judgment.normalized_input)

                # 자카드 유사도 계산
                similarity = self._jaccard_similarity(input_tokens, cached_tokens)

                # 길이 보정 (비슷한 길이일수록 가중치)
                length_ratio = min(len(input_tokens), len(cached_tokens)) / max(
                    len(input_tokens), len(cached_tokens)
                )
                adjusted_similarity = similarity * (0.7 + 0.3 * length_ratio)

                if (
                    adjusted_similarity > best_score
                    and adjusted_similarity >= threshold
                ):
                    best_score = adjusted_similarity
                    best_match = judgment
                    best_match.similarity_score = adjusted_similarity

            return best_match

        except Exception as e:
            print(f"⚠️ 키워드 유사도 탐색 실패: {e}")
            return None

    def _tokenize_korean(self, text: str) -> List[str]:
        """한국어 텍스트 토큰화 (간단한 방식)"""
        # 공백으로 분리
        tokens = text.split()

        # 추가 전처리 (필요한 경우)
        tokens = [token.strip(".,!?") for token in tokens if len(token.strip()) > 0]

        return tokens

    def _jaccard_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """자카드 유사도 계산"""
        set1 = set(tokens1)
        set2 = set(tokens2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _judgment_to_dict(self, judgment: CachedJudgment) -> Dict[str, Any]:
        """CachedJudgment를 dict로 변환"""
        return {
            "input": judgment.input,
            "normalized_input": judgment.normalized_input,
            "emotion": judgment.emotion,
            "emotion_confidence": judgment.emotion_confidence,
            "strategy": judgment.strategy,
            "strategy_confidence": judgment.strategy_confidence,
            "template": judgment.template,
            "styled_sentence": judgment.styled_sentence,
            "signature": judgment.signature,
            "timestamp": judgment.timestamp.isoformat(),
            "usage_count": judgment.usage_count,
            "similarity_score": judgment.similarity_score,
        }

    def add_judgment(self, judgment_data: Dict[str, Any]):
        """새로운 판단을 캐시에 추가"""
        try:
            timestamp = datetime.fromisoformat(
                judgment_data.get("timestamp", datetime.now().isoformat())
            )

            cached_judgment = CachedJudgment(
                input=judgment_data.get("input", ""),
                normalized_input=judgment_data.get("normalized_input", ""),
                emotion=judgment_data.get("emotion", "neutral"),
                emotion_confidence=judgment_data.get("emotion_confidence", 0.5),
                strategy=judgment_data.get("strategy", "analyze"),
                strategy_confidence=judgment_data.get("strategy_confidence", 0.5),
                template=judgment_data.get("template", ""),
                styled_sentence=judgment_data.get("styled_sentence", ""),
                signature=judgment_data.get("signature", "Selene"),
                timestamp=timestamp,
                usage_count=1,
            )

            self.cached_judgments.append(cached_judgment)
            self.stats["cache_size"] = len(self.cached_judgments)

        except Exception as e:
            print(f"⚠️ 캐시 추가 실패: {e}")

    def update_usage_count(self, judgment_input: str):
        """사용 횟수 업데이트"""
        for judgment in self.cached_judgments:
            if judgment.input == judgment_input:
                judgment.usage_count += 1
                break

    def get_cache_statistics(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        if not self.cached_judgments:
            return {"message": "캐시된 판단이 없습니다"}

        # 시그니처별 분포
        signature_dist = Counter(j.signature for j in self.cached_judgments)

        # 감정별 분포
        emotion_dist = Counter(j.emotion for j in self.cached_judgments)

        # 전략별 분포
        strategy_dist = Counter(j.strategy for j in self.cached_judgments)

        # 평균 사용 횟수
        avg_usage = sum(j.usage_count for j in self.cached_judgments) / len(
            self.cached_judgments
        )

        return {
            "total_cached_judgments": len(self.cached_judgments),
            "total_searches": self.stats["total_searches"],
            "successful_matches": self.stats["successful_matches"],
            "hit_rate": f"{(self.stats['successful_matches'] / max(self.stats['total_searches'], 1)) * 100:.1f}%",
            "average_usage_count": f"{avg_usage:.1f}",
            "signature_distribution": dict(signature_dist),
            "emotion_distribution": dict(emotion_dist),
            "strategy_distribution": dict(strategy_dist),
            "embedding_searches": self.stats["embedding_searches"],
            "keyword_searches": self.stats["keyword_searches"],
            "embedding_available": EMBEDDING_AVAILABLE,
        }

    def cleanup_old_judgments(self, days: int = 30):
        """오래된 판단 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)

        before_count = len(self.cached_judgments)
        self.cached_judgments = [
            j
            for j in self.cached_judgments
            if j.timestamp > cutoff_date or j.usage_count > 5  # 자주 사용된 것은 보존
        ]
        after_count = len(self.cached_judgments)

        removed_count = before_count - after_count
        if removed_count > 0:
            print(f"✅ {removed_count}개의 오래된 판단을 정리했습니다.")

        self.stats["cache_size"] = len(self.cached_judgments)


if __name__ == "__main__":
    # 테스트
    print("🔍 ExistingJudgmentSearcher 테스트")

    searcher = ExistingJudgmentSearcher()

    # 샘플 판단 추가
    sample_judgments = [
        {
            "input": "오늘 너무 피곤해",
            "normalized_input": "오늘 너무 피곤해",
            "emotion": "sadness",
            "emotion_confidence": 0.8,
            "strategy": "retreat",
            "strategy_confidence": 0.7,
            "template": "sadness_retreat",
            "styled_sentence": "많이 피곤하시겠어요. 충분히 쉬세요.",
            "signature": "Selene",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "input": "새로운 아이디어가 필요해",
            "normalized_input": "새로운 아이디어가 필요해",
            "emotion": "joy",
            "emotion_confidence": 0.6,
            "strategy": "initiate",
            "strategy_confidence": 0.8,
            "template": "joy_initiate",
            "styled_sentence": "새로운 아이디어를 함께 만들어봐요!",
            "signature": "Aurora",
            "timestamp": datetime.now().isoformat(),
        },
    ]

    for judgment in sample_judgments:
        searcher.add_judgment(judgment)

    # 유사도 테스트
    test_queries = [
        "오늘 정말 힘들어",  # "오늘 너무 피곤해"와 유사
        "창의적인 생각이 필요해",  # "새로운 아이디어가 필요해"와 유사
        "완전히 다른 주제",  # 매칭되지 않을 것
    ]

    for query in test_queries:
        print(f"\n🔍 테스트 쿼리: '{query}'")
        result = searcher.search_similar_judgment(query, threshold=0.3)

        if result:
            print(f"   ✅ 매칭: {result['input']}")
            print(f"   응답: {result['styled_sentence']}")
            print(f"   유사도: {result.get('similarity_score', 0):.3f}")
        else:
            print(f"   ❌ 매칭 실패")

    # 통계 출력
    stats = searcher.get_cache_statistics()
    print(f"\n📊 캐시 통계:")
    for key, value in stats.items():
        if key not in [
            "signature_distribution",
            "emotion_distribution",
            "strategy_distribution",
        ]:
            print(f"   {key}: {value}")
