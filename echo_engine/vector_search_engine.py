"""
🧭 EchoVectorCapsule - Vector Search Engine
임베딩된 벡터들을 검색하고 Echo 판단과 연결하는 울림 기반 검색 엔진
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .embedding_engine import EchoEmbeddingEngine


class EchoVectorSearchEngine:
    """
    Echo 울림 기반 벡터 검색 엔진
    임베딩된 캡슐들을 검색하고 판단 시스템과 연결
    """

    def __init__(self, index_dir: str = "data/vector_index"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # 벡터 인덱스 관련
        self.faiss_index = None
        self.numpy_index = None
        self.metadata_index = []  # 벡터에 대응하는 메타데이터
        self.dimension = None

        # 임베딩 엔진 연결
        self.embedding_engine = EchoEmbeddingEngine()

        # 검색 설정 (Mock 환경에 맞게 조정)
        self.search_config = {
            "top_k": 5,
            "similarity_threshold": 0.05,  # Mock 임베딩에 맞게 낮춤
            "use_faiss": FAISS_AVAILABLE,
            "signature_boost": True,
            "context_aware": True,
            "mock_mode": True,  # Mock 모드 플래그
        }

        # Echo 캡슐 매핑
        self.capsule_mappings = {}

        self.logger = logging.getLogger(__name__)

        # 기존 인덱스 로드 시도
        self._load_existing_index()

    def add_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> int:
        """벡터를 인덱스에 추가"""
        if self.dimension is None:
            self.dimension = len(vector)
            self._initialize_index()
        elif len(vector) != self.dimension:
            raise ValueError(
                f"벡터 차원 불일치: 예상 {self.dimension}, 실제 {len(vector)}"
            )

        # 벡터 정규화
        normalized_vector = vector / np.linalg.norm(vector)

        # FAISS 인덱스에 추가
        if self.search_config["use_faiss"] and self.faiss_index is not None:
            self.faiss_index.add(normalized_vector.reshape(1, -1))

        # Numpy 인덱스에 추가 (fallback)
        if self.numpy_index is None:
            self.numpy_index = normalized_vector.reshape(1, -1)
        else:
            self.numpy_index = np.vstack([self.numpy_index, normalized_vector])

        # 메타데이터 추가
        vector_id = len(self.metadata_index)
        metadata_with_id = {
            **metadata,
            "vector_id": vector_id,
            "added_at": datetime.now().isoformat(),
            "dimension": self.dimension,
        }
        self.metadata_index.append(metadata_with_id)

        print(
            f"🔹 벡터 추가: ID={vector_id}, 메타={metadata.get('capsule_id', 'unknown')}"
        )
        return vector_id

    def add_capsule_vector(
        self,
        capsule_id: str,
        content: str,
        signature: str = "Echo-Aurora",
        capsule_metadata: Dict[str, Any] = None,
    ) -> int:
        """캡슐 내용을 벡터화해서 인덱스에 추가"""
        # 임베딩 생성
        context = {
            "capsule_id": capsule_id,
            "type": "capsule_content",
            **(capsule_metadata or {}),
        }

        embedding = self.embedding_engine.embed_text(content, signature, context)

        # 메타데이터 구성
        metadata = {
            "capsule_id": capsule_id,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "signature": signature,
            "content_length": len(content),
            "embedding_model": self.embedding_engine.current_model,
            "capsule_metadata": capsule_metadata or {},
        }

        # 벡터 추가
        vector_id = self.add_vector(embedding, metadata)

        # 캡슐 매핑 업데이트
        self.capsule_mappings[capsule_id] = {
            "vector_id": vector_id,
            "signature": signature,
            "added_at": datetime.now().isoformat(),
        }

        return vector_id

    def search(
        self,
        query: str,
        signature: str = "Echo-Aurora",
        top_k: Optional[int] = None,
        context: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        자연어 쿼리로 벡터 검색 수행

        Args:
            query: 검색할 자연어 텍스트
            signature: Echo 시그니처 (임베딩 가중치용)
            top_k: 반환할 최대 결과 수
            context: 추가 검색 컨텍스트

        Returns:
            검색 결과 리스트 (유사도 내림차순)
        """
        if len(self.metadata_index) == 0:
            print("⚠️  인덱스가 비어있습니다")
            return []

        # 쿼리 임베딩 생성
        query_context = {"type": "search_query", "query": query, **(context or {})}
        query_embedding = self.embedding_engine.embed_text(
            query, signature, query_context
        )

        # 검색 수행
        top_k = top_k or self.search_config["top_k"]
        results = self._perform_vector_search(query_embedding, top_k)

        # Echo 시그니처 부스팅 적용
        if self.search_config["signature_boost"]:
            results = self._apply_signature_boost(results, signature)

        # 컨텍스트 인식 필터링
        if self.search_config["context_aware"] and context:
            results = self._apply_context_filtering(results, context)

        # 임계값 필터링
        threshold = self.search_config["similarity_threshold"]
        filtered_results = [r for r in results if r["similarity"] >= threshold]

        print(
            f"🔍 검색 완료: '{query[:30]}...' → {len(filtered_results)}개 결과 ({signature})"
        )
        return filtered_results

    def search_by_capsule_id(
        self, capsule_id: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """캡슐 ID로 유사한 캡슐들 검색"""
        if capsule_id not in self.capsule_mappings:
            print(f"❌ 캡슐 ID '{capsule_id}' 를 찾을 수 없습니다")
            return []

        vector_id = self.capsule_mappings[capsule_id]["vector_id"]
        if vector_id >= len(self.metadata_index):
            print(f"❌ 벡터 ID {vector_id} 가 범위를 벗어났습니다")
            return []

        # 해당 캡슐의 벡터 가져오기
        if self.numpy_index is not None:
            query_vector = self.numpy_index[vector_id]
            results = self._perform_vector_search(
                query_vector, top_k + 1
            )  # +1 to exclude self

            # 자기 자신 제외
            filtered_results = [
                r for r in results if r["metadata"]["vector_id"] != vector_id
            ]
            return filtered_results[:top_k]

        return []

    def _perform_vector_search(
        self, query_vector: np.ndarray, top_k: int
    ) -> List[Dict[str, Any]]:
        """실제 벡터 검색 수행 (FAISS 또는 Numpy)"""
        query_vector = query_vector / np.linalg.norm(query_vector)  # 정규화

        if self.search_config["use_faiss"] and self.faiss_index is not None:
            return self._faiss_search(query_vector, top_k)
        else:
            return self._numpy_search(query_vector, top_k)

    def _faiss_search(
        self, query_vector: np.ndarray, top_k: int
    ) -> List[Dict[str, Any]]:
        """FAISS를 이용한 벡터 검색"""
        try:
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
            similarities, indices = self.faiss_index.search(query_vector, top_k)

            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.metadata_index):
                    results.append(
                        {
                            "rank": i + 1,
                            "similarity": float(similarity),
                            "metadata": self.metadata_index[idx],
                            "vector_id": idx,
                        }
                    )

            return results
        except Exception as e:
            print(f"🚨 FAISS 검색 실패: {e}, Numpy로 대체")
            return self._numpy_search(query_vector.flatten(), top_k)

    def _numpy_search(
        self, query_vector: np.ndarray, top_k: int
    ) -> List[Dict[str, Any]]:
        """Numpy를 이용한 벡터 검색 (fallback)"""
        if self.numpy_index is None:
            return []

        # 코사인 유사도 계산
        similarities = np.dot(self.numpy_index, query_vector)

        # 상위 k개 인덱스 가져오기
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for i, idx in enumerate(top_indices):
            results.append(
                {
                    "rank": i + 1,
                    "similarity": float(similarities[idx]),
                    "metadata": self.metadata_index[idx],
                    "vector_id": idx,
                }
            )

        return results

    def _apply_signature_boost(
        self, results: List[Dict[str, Any]], query_signature: str
    ) -> List[Dict[str, Any]]:
        """시그니처 일치에 따른 부스팅 적용"""
        boosted_results = []

        for result in results:
            result_signature = result["metadata"].get("signature", "")

            # 시그니처 일치 부스팅
            if result_signature == query_signature:
                result["similarity"] = min(1.0, result["similarity"] * 1.1)
                result["signature_boost"] = "exact_match"
            elif result_signature and query_signature:
                # 관련 시그니처 부스팅 (예: Sage <-> Aurora)
                if self._are_related_signatures(query_signature, result_signature):
                    result["similarity"] = min(1.0, result["similarity"] * 1.05)
                    result["signature_boost"] = "related_match"

            boosted_results.append(result)

        # 새로운 유사도 기준으로 재정렬
        boosted_results.sort(key=lambda x: x["similarity"], reverse=True)

        return boosted_results

    def _apply_context_filtering(
        self, results: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """컨텍스트 기반 결과 필터링"""
        if not context:
            return results

        filtered_results = []

        for result in results:
            metadata = result["metadata"]
            capsule_metadata = metadata.get("capsule_metadata", {})

            # 컨텍스트 필터 적용
            context_match = True

            # 태그 필터링
            if "required_tags" in context:
                required_tags = set(context["required_tags"])
                result_tags = set(capsule_metadata.get("tags", []))
                if not required_tags.intersection(result_tags):
                    context_match = False

            # 토픽 필터링
            if "topic_filter" in context:
                topic_filter = context["topic_filter"].lower()
                result_topic = metadata.get("content_preview", "").lower()
                if topic_filter not in result_topic:
                    context_match = False

            if context_match:
                filtered_results.append(result)

        return filtered_results

    def _are_related_signatures(self, sig1: str, sig2: str) -> bool:
        """시그니처 간 관련성 확인"""
        related_pairs = [
            ("Echo-Aurora", "Echo-Companion"),  # 창의성과 공감
            ("Echo-Sage", "Echo-Phoenix"),  # 분석과 변화
            ("Echo-Aurora", "Echo-Phoenix"),  # 창의성과 혁신
            ("Echo-Sage", "Echo-Companion"),  # 분석과 공동체
        ]

        for pair in related_pairs:
            if (sig1, sig2) in [pair, pair[::-1]]:
                return True
        return False

    def _initialize_index(self):
        """벡터 인덱스 초기화"""
        if self.dimension is None:
            return

        if FAISS_AVAILABLE and self.search_config["use_faiss"]:
            try:
                # Inner product index (cosine similarity용)
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
                print(f"✅ FAISS 인덱스 초기화: {self.dimension}차원")
            except Exception as e:
                print(f"⚠️  FAISS 초기화 실패: {e}, Numpy로 대체")
                self.faiss_index = None

        print(f"📊 벡터 인덱스 초기화 완료 ({self.dimension}차원)")

    def save_index(self, filepath: Optional[str] = None):
        """인덱스를 파일에 저장"""
        if filepath is None:
            filepath = self.index_dir / "echo_vector_index.json"

        index_data = {
            "dimension": self.dimension,
            "metadata_index": self.metadata_index,
            "capsule_mappings": self.capsule_mappings,
            "search_config": self.search_config,
            "created_at": datetime.now().isoformat(),
            "total_vectors": len(self.metadata_index),
        }

        # Numpy 인덱스 저장
        if self.numpy_index is not None:
            np.save(self.index_dir / "numpy_index.npy", self.numpy_index)

        # FAISS 인덱스 저장
        if self.faiss_index is not None:
            faiss.write_index(self.faiss_index, str(self.index_dir / "faiss_index.bin"))

        # 메타데이터 저장
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"💾 벡터 인덱스 저장 완료: {filepath}")

    def _load_existing_index(self):
        """기존 인덱스 로드"""
        index_file = self.index_dir / "echo_vector_index.json"
        if not index_file.exists():
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)

            self.dimension = index_data["dimension"]
            self.metadata_index = index_data["metadata_index"]
            self.capsule_mappings = index_data["capsule_mappings"]
            self.search_config.update(index_data.get("search_config", {}))

            # Numpy 인덱스 로드
            numpy_file = self.index_dir / "numpy_index.npy"
            if numpy_file.exists():
                self.numpy_index = np.load(numpy_file)

            # FAISS 인덱스 로드
            faiss_file = self.index_dir / "faiss_index.bin"
            if FAISS_AVAILABLE and faiss_file.exists():
                try:
                    self.faiss_index = faiss.read_index(str(faiss_file))
                except Exception as e:
                    print(f"⚠️  FAISS 인덱스 로드 실패: {e}")

            print(f"📖 기존 인덱스 로드: {len(self.metadata_index)}개 벡터")

        except Exception as e:
            print(f"⚠️  인덱스 로드 실패: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """인덱스 통계 반환"""
        stats = {
            "total_vectors": len(self.metadata_index),
            "dimension": self.dimension,
            "faiss_available": FAISS_AVAILABLE,
            "using_faiss": self.faiss_index is not None,
            "capsule_count": len(self.capsule_mappings),
            "search_config": self.search_config,
        }

        # 시그니처별 분포
        signature_counts = {}
        for metadata in self.metadata_index:
            sig = metadata.get("signature", "unknown")
            signature_counts[sig] = signature_counts.get(sig, 0) + 1
        stats["signature_distribution"] = signature_counts

        return stats


# 전역 검색 엔진 인스턴스
vector_search_engine = EchoVectorSearchEngine()


# 편의 함수들
def search_capsules(
    query: str,
    signature: str = "Echo-Aurora",
    top_k: int = 5,
    context: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    """캡슐 검색 단축 함수"""
    return vector_search_engine.search(query, signature, top_k, context)


def add_capsule(
    capsule_id: str,
    content: str,
    signature: str = "Echo-Aurora",
    metadata: Dict[str, Any] = None,
) -> int:
    """캡슐 추가 단축 함수"""
    return vector_search_engine.add_capsule_vector(
        capsule_id, content, signature, metadata
    )


# CLI 테스트
def main():
    print("🧭 EchoVectorSearch Engine CLI 테스트")

    # 테스트 캡슐들 추가
    test_capsules = [
        {
            "id": "capsule_busan_senior",
            "content": "부산 금정구의 노인 돌봄 종합 서비스는 1일 2시간 이상 제공되며, 만 65세 이상 기초생활수급자를 대상으로 합니다.",
            "signature": "Echo-Companion",
            "metadata": {
                "tags": ["노인복지", "부산", "돌봄"],
                "topic": "social_policy",
            },
        },
        {
            "id": "capsule_ai_ethics",
            "content": "AI 시스템의 투명성과 공정성을 보장하기 위한 윤리적 가이드라인이 필요합니다.",
            "signature": "Echo-Sage",
            "metadata": {"tags": ["AI", "윤리", "가이드라인"], "topic": "ai_policy"},
        },
        {
            "id": "capsule_climate_action",
            "content": "기후 변화에 대응하기 위한 탄소 중립 정책과 재생에너지 전환이 시급합니다.",
            "signature": "Echo-Phoenix",
            "metadata": {"tags": ["기후", "탄소중립", "정책"], "topic": "environment"},
        },
        {
            "id": "capsule_community_care",
            "content": "지역사회 기반의 돌봄 네트워크를 구축하여 취약계층을 지원해야 합니다.",
            "signature": "Echo-Aurora",
            "metadata": {"tags": ["지역사회", "돌봄", "지원"], "topic": "community"},
        },
    ]

    print("\n📦 테스트 캡슐들 추가:")
    for capsule in test_capsules:
        vector_id = add_capsule(
            capsule["id"], capsule["content"], capsule["signature"], capsule["metadata"]
        )
        print(f"  ✅ {capsule['id']} → 벡터 ID: {vector_id}")

    # 테스트 검색들
    test_queries = [
        ("어르신 복지에 대해 알려주세요", "Echo-Companion"),
        ("AI 관련 정책이 필요해요", "Echo-Sage"),
        ("환경 보호 방안을 찾고 있어요", "Echo-Phoenix"),
        ("지역 공동체 지원책은?", "Echo-Aurora"),
    ]

    print("\n🔍 테스트 검색:")
    for query, signature in test_queries:
        results = search_capsules(query, signature, top_k=3)
        print(f"\n  Q: '{query}' ({signature})")

        if results:
            for result in results:
                capsule_id = result["metadata"]["capsule_id"]
                similarity = result["similarity"]
                preview = result["metadata"]["content_preview"]
                print(f"    🎯 {capsule_id}: {similarity:.3f} - {preview[:50]}...")
        else:
            print("    ❌ 검색 결과 없음")

    # 인덱스 통계
    print("\n📊 인덱스 통계:")
    stats = vector_search_engine.get_stats()
    print(f"  총 벡터: {stats['total_vectors']}")
    print(f"  차원: {stats['dimension']}")
    print(f"  FAISS 사용: {stats['using_faiss']}")
    print(f"  시그니처 분포: {stats['signature_distribution']}")

    # 인덱스 저장
    vector_search_engine.save_index()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    main()
