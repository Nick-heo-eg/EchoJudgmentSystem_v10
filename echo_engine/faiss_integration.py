"""
🏗️ FAISS Integration for Echo Vector Search
Real FAISS 인덱스 통합으로 벡터 검색 성능 최적화
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    import faiss

    FAISS_AVAILABLE = True
    print("🚀 FAISS 라이브러리 사용 가능")
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS 라이브러리 없음, Mock 인덱스 사용")


class EchoFAISSIntegration:
    """
    Echo 전용 FAISS 통합 클래스
    실제 FAISS 인덱스 또는 Numpy 기반 fallback 제공
    """

    def __init__(self, dimension: int = 128, index_dir: str = "data/faiss_index"):
        self.dimension = dimension
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # FAISS 인덱스 설정
        self.faiss_index = None
        self.numpy_vectors = []
        self.metadata_list = []

        # 인덱스 설정
        self.index_config = {
            "use_faiss": FAISS_AVAILABLE,
            "index_type": "IndexFlatIP",  # Inner Product for cosine similarity
            "nlist": 100,  # For IVF indices
            "m": 8,  # For PQ indices
            "nbits": 8,  # For PQ indices
        }

        # 통계
        self.stats = {
            "total_vectors": 0,
            "search_count": 0,
            "avg_search_time": 0.0,
            "last_updated": None,
        }

        self.logger = logging.getLogger(__name__)

        # 기존 인덱스 로드 시도
        self._load_existing_index()

        print(
            f"🏗️  Echo FAISS Integration 초기화 (차원: {dimension}, FAISS: {FAISS_AVAILABLE})"
        )

    def add_vectors(
        self, vectors: np.ndarray, metadata: List[Dict[str, Any]]
    ) -> List[int]:
        """벡터들을 인덱스에 추가"""
        if vectors.shape[0] != len(metadata):
            raise ValueError("벡터 수와 메타데이터 수가 일치하지 않습니다")

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"벡터 차원({vectors.shape[1]})이 설정된 차원({self.dimension})과 다릅니다"
            )

        start_idx = self.stats["total_vectors"]
        vector_ids = list(range(start_idx, start_idx + len(vectors)))

        if self.index_config["use_faiss"] and FAISS_AVAILABLE:
            self._add_to_faiss_index(vectors, metadata, vector_ids)
        else:
            self._add_to_numpy_index(vectors, metadata, vector_ids)

        self.stats["total_vectors"] += len(vectors)
        self.stats["last_updated"] = datetime.now().isoformat()

        print(
            f"🔹 벡터 {len(vectors)}개 추가: ID {start_idx}~{start_idx + len(vectors) - 1}"
        )

        return vector_ids

    def add_single_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> int:
        """단일 벡터 추가"""
        vectors = vector.reshape(1, -1)
        metadata_list = [metadata]
        return self.add_vectors(vectors, metadata_list)[0]

    def search(
        self, query_vector: np.ndarray, top_k: int = 5, threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """벡터 검색 수행"""
        if self.stats["total_vectors"] == 0:
            return []

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        start_time = datetime.now()

        if self.index_config["use_faiss"] and FAISS_AVAILABLE:
            results = self._search_faiss_index(query_vector, top_k, threshold)
        else:
            results = self._search_numpy_index(query_vector, top_k, threshold)

        # 통계 업데이트
        search_time = (datetime.now() - start_time).total_seconds()
        self.stats["search_count"] += 1
        current_avg = self.stats["avg_search_time"]
        total_searches = self.stats["search_count"]
        self.stats["avg_search_time"] = (
            (current_avg * (total_searches - 1)) + search_time
        ) / total_searches

        print(f"🔍 검색 완료: {len(results)}개 결과 ({search_time:.3f}초)")

        return results

    def _add_to_faiss_index(
        self, vectors: np.ndarray, metadata: List[Dict[str, Any]], vector_ids: List[int]
    ):
        """FAISS 인덱스에 벡터 추가"""
        # 벡터 정규화 (코사인 유사도를 위해)
        vectors_normalized = self._normalize_vectors(vectors)

        if self.faiss_index is None:
            self._initialize_faiss_index()

        self.faiss_index.add(vectors_normalized)

        # 메타데이터 별도 저장
        for i, meta in enumerate(metadata):
            meta_with_id = {**meta, "vector_id": vector_ids[i]}
            self.metadata_list.append(meta_with_id)

    def _add_to_numpy_index(
        self, vectors: np.ndarray, metadata: List[Dict[str, Any]], vector_ids: List[int]
    ):
        """Numpy 인덱스에 벡터 추가"""
        vectors_normalized = self._normalize_vectors(vectors)

        for i, vector in enumerate(vectors_normalized):
            self.numpy_vectors.append(vector)
            meta_with_id = {**metadata[i], "vector_id": vector_ids[i]}
            self.metadata_list.append(meta_with_id)

    def _initialize_faiss_index(self):
        """FAISS 인덱스 초기화"""
        if not FAISS_AVAILABLE:
            return

        index_type = self.index_config["index_type"]

        if index_type == "IndexFlatIP":
            # Inner Product (코사인 유사도용)
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
        elif index_type == "IndexFlatL2":
            # L2 distance
            self.faiss_index = faiss.IndexFlatL2(self.dimension)
        elif index_type == "IndexIVFFlat":
            # IVF with flat quantizer
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.faiss_index = faiss.IndexIVFFlat(
                quantizer, self.dimension, self.index_config["nlist"]
            )
            self.faiss_index.nprobe = 10  # 검색 시 조사할 클러스터 수
        else:
            # 기본값: Flat IP
            self.faiss_index = faiss.IndexFlatIP(self.dimension)

        print(f"🚀 FAISS {index_type} 인덱스 초기화 완료")

    def _search_faiss_index(
        self, query_vector: np.ndarray, top_k: int, threshold: float
    ) -> List[Dict[str, Any]]:
        """FAISS 인덱스 검색"""
        query_normalized = self._normalize_vectors(query_vector)

        # IVF 인덱스의 경우 학습 필요
        if hasattr(self.faiss_index, "is_trained") and not self.faiss_index.is_trained:
            if self.stats["total_vectors"] >= self.index_config["nlist"]:
                all_vectors = np.array(self.numpy_vectors)
                if len(all_vectors) > 0:
                    self.faiss_index.train(all_vectors)

        # 검색 수행
        scores, indices = self.faiss_index.search(
            query_normalized, min(top_k, self.stats["total_vectors"])
        )

        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:  # FAISS에서 유효하지 않은 인덱스
                continue

            if score >= threshold:
                result = {
                    "vector_id": idx,
                    "similarity": float(score),
                    "metadata": (
                        self.metadata_list[idx] if idx < len(self.metadata_list) else {}
                    ),
                    "rank": i + 1,
                }
                results.append(result)

        return results

    def _search_numpy_index(
        self, query_vector: np.ndarray, top_k: int, threshold: float
    ) -> List[Dict[str, Any]]:
        """Numpy 인덱스 검색"""
        if not self.numpy_vectors:
            return []

        query_normalized = self._normalize_vectors(query_vector)[0]

        # 모든 벡터와 코사인 유사도 계산
        similarities = []
        for i, vector in enumerate(self.numpy_vectors):
            similarity = np.dot(query_normalized, vector)
            similarities.append((similarity, i))

        # 유사도 기준 내림차순 정렬
        similarities.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (similarity, idx) in enumerate(similarities[:top_k]):
            if similarity >= threshold:
                result = {
                    "vector_id": idx,
                    "similarity": float(similarity),
                    "metadata": (
                        self.metadata_list[idx] if idx < len(self.metadata_list) else {}
                    ),
                    "rank": rank + 1,
                }
                results.append(result)

        return results

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """벡터 정규화 (코사인 유사도를 위해)"""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 0 벡터 처리
        return vectors / norms

    def save_index(self, filename_prefix: str = "echo_faiss"):
        """인덱스를 파일에 저장"""
        try:
            if self.index_config["use_faiss"] and FAISS_AVAILABLE and self.faiss_index:
                # FAISS 인덱스 저장
                faiss_file = self.index_dir / f"{filename_prefix}.faiss"
                faiss.write_index(self.faiss_index, str(faiss_file))
                print(f"💾 FAISS 인덱스 저장: {faiss_file}")

            # 메타데이터 저장
            metadata_file = self.index_dir / f"{filename_prefix}_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "metadata_list": self.metadata_list,
                        "stats": self.stats,
                        "config": self.index_config,
                        "dimension": self.dimension,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Numpy 벡터 저장 (fallback용)
            if self.numpy_vectors:
                numpy_file = self.index_dir / f"{filename_prefix}_numpy.pkl"
                with open(numpy_file, "wb") as f:
                    pickle.dump(self.numpy_vectors, f)
                print(f"💾 Numpy 벡터 저장: {numpy_file}")

            print(f"✅ 인덱스 저장 완료: {self.stats['total_vectors']}개 벡터")

        except Exception as e:
            print(f"❌ 인덱스 저장 실패: {e}")

    def _load_existing_index(self, filename_prefix: str = "echo_faiss"):
        """기존 인덱스 로드"""
        try:
            metadata_file = self.index_dir / f"{filename_prefix}_metadata.json"

            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.metadata_list = data.get("metadata_list", [])
                self.stats = data.get("stats", self.stats)
                saved_config = data.get("config", {})
                self.dimension = data.get("dimension", self.dimension)

                # FAISS 인덱스 로드
                if self.index_config["use_faiss"] and FAISS_AVAILABLE:
                    faiss_file = self.index_dir / f"{filename_prefix}.faiss"
                    if faiss_file.exists():
                        self.faiss_index = faiss.read_index(str(faiss_file))
                        print(f"📖 FAISS 인덱스 로드: {faiss_file}")

                # Numpy 벡터 로드
                numpy_file = self.index_dir / f"{filename_prefix}_numpy.pkl"
                if numpy_file.exists():
                    with open(numpy_file, "rb") as f:
                        self.numpy_vectors = pickle.load(f)
                    print(f"📖 Numpy 벡터 로드: {len(self.numpy_vectors)}개")

                print(f"✅ 기존 인덱스 로드 완료: {self.stats['total_vectors']}개 벡터")

        except Exception as e:
            print(f"⚠️  기존 인덱스 로드 실패: {e}, 새 인덱스 생성")

    def get_stats(self) -> Dict[str, Any]:
        """인덱스 통계 반환"""
        stats = self.stats.copy()
        stats["using_faiss"] = self.index_config["use_faiss"] and FAISS_AVAILABLE
        stats["index_type"] = self.index_config["index_type"]
        stats["dimension"] = self.dimension

        return stats

    def rebuild_index(self, new_config: Dict[str, Any] = None):
        """인덱스 재구축"""
        if new_config:
            self.index_config.update(new_config)

        print("🔄 인덱스 재구축 시작...")

        # 기존 데이터 백업
        old_vectors = self.numpy_vectors.copy()
        old_metadata = self.metadata_list.copy()

        # 인덱스 초기화
        self.faiss_index = None
        self.numpy_vectors = []
        self.metadata_list = []
        self.stats["total_vectors"] = 0

        # 데이터 재추가
        if old_vectors:
            vectors_array = np.array(old_vectors)
            self.add_vectors(vectors_array, old_metadata)

        print("✅ 인덱스 재구축 완료")


# 전역 FAISS 통합 인스턴스
faiss_integration = EchoFAISSIntegration()


# 편의 함수들
def add_vector(vector: np.ndarray, metadata: Dict[str, Any]) -> int:
    """벡터 추가 단축 함수"""
    return faiss_integration.add_single_vector(vector, metadata)


def search_vectors(
    query: np.ndarray, top_k: int = 5, threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """벡터 검색 단축 함수"""
    return faiss_integration.search(query, top_k, threshold)


def save_index(filename: str = "echo_faiss"):
    """인덱스 저장 단축 함수"""
    faiss_integration.save_index(filename)


def get_index_stats() -> Dict[str, Any]:
    """인덱스 통계 단축 함수"""
    return faiss_integration.get_stats()


# CLI 테스트
def main():
    print("🏗️  Echo FAISS Integration 테스트")
    print("=" * 50)

    # 테스트 벡터 생성
    print("\n🧪 테스트 벡터 생성:")
    np.random.seed(42)
    test_vectors = np.random.randn(10, 128).astype(np.float32)
    test_metadata = [
        {"id": f"test_{i}", "content": f"테스트 벡터 {i}", "category": f"cat_{i % 3}"}
        for i in range(10)
    ]

    # 벡터 추가
    print("\n➕ 벡터 추가 테스트:")
    vector_ids = faiss_integration.add_vectors(test_vectors, test_metadata)
    print(f"추가된 벡터 ID: {vector_ids}")

    # 검색 테스트
    print("\n🔍 검색 테스트:")
    query_vector = np.random.randn(128).astype(np.float32)
    search_results = faiss_integration.search(query_vector, top_k=5, threshold=0.0)

    for i, result in enumerate(search_results):
        print(f"  {i+1}. ID: {result['vector_id']}, 유사도: {result['similarity']:.3f}")
        print(f"      메타: {result['metadata']['content']}")

    # 통계 출력
    print("\n📊 인덱스 통계:")
    stats = faiss_integration.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 저장 테스트
    print("\n💾 인덱스 저장 테스트:")
    faiss_integration.save_index("test_echo_faiss")

    print("\n✅ Echo FAISS Integration 테스트 완료!")


if __name__ == "__main__":
    main()
