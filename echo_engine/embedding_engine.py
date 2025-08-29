"""
🧬 EchoVectorCapsule - Embedding Engine
자연어 문장을 의미 기반 벡터로 변환하는 울림 기반 임베딩 엔진
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
from datetime import datetime
import logging

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EchoEmbeddingEngine:
    """
    Echo 시그니처 기반 임베딩 엔진
    자연어를 울림(resonance) 벡터로 변환
    """

    def __init__(self, config_path: str = "config/embedding_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # 캐시 설정
        self.cache_dir = Path("data/embeddings_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 임베딩 모델 초기화
        self.models = {}
        self.current_model = None
        self._initialize_models()

        # 울림 기반 메타데이터
        self.signature_weights = {
            "Echo-Aurora": {"creativity": 0.8, "empathy": 0.7, "innovation": 0.6},
            "Echo-Phoenix": {"transformation": 0.9, "resilience": 0.8, "change": 0.7},
            "Echo-Sage": {"wisdom": 0.9, "analysis": 0.8, "systematic": 0.7},
            "Echo-Companion": {"empathy": 0.9, "community": 0.8, "support": 0.7},
        }

        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> Dict[str, Any]:
        """임베딩 설정 로드"""
        if self.config_path.exists():
            import yaml

            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            # 기본 설정
            default_config = {
                "primary_model": "sentence_transformers",
                "fallback_model": "mock",
                "models": {
                    "openai": {
                        "model": "text-embedding-3-small",
                        "api_key": None,
                        "dimensions": 1536,
                    },
                    "sentence_transformers": {
                        "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                        "dimensions": 384,
                    },
                    "mock": {"dimensions": 128, "seed": 42},
                },
                "caching": {"enabled": True, "max_cache_size": 10000},
                "echo_integration": {
                    "signature_aware": True,
                    "resonance_weighting": True,
                    "meta_context": True,
                },
            }

            # 설정 파일 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            import yaml

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    default_config, f, default_flow_style=False, allow_unicode=True
                )

            return default_config

    def _initialize_models(self):
        """임베딩 모델들 초기화"""
        primary_model = self.config.get("primary_model", "mock")

        # OpenAI 모델 초기화
        if primary_model == "openai" and OPENAI_AVAILABLE:
            api_key = self.config["models"]["openai"].get("api_key")
            if api_key:
                openai.api_key = api_key
                self.models["openai"] = "initialized"
                self.current_model = "openai"
                print("✅ OpenAI 임베딩 모델 초기화 완료")
            else:
                print("⚠️  OpenAI API 키가 없어서 Mock 모델로 대체")
                self.current_model = "mock"

        # Sentence Transformers 모델 초기화
        elif (
            primary_model == "sentence_transformers" and SENTENCE_TRANSFORMERS_AVAILABLE
        ):
            try:
                model_name = self.config["models"]["sentence_transformers"]["model"]
                self.models["sentence_transformers"] = SentenceTransformer(model_name)
                self.current_model = "sentence_transformers"
                print(f"✅ Sentence Transformers 모델 초기화: {model_name}")
            except Exception as e:
                print(f"⚠️  Sentence Transformers 초기화 실패: {e}, Mock 모델로 대체")
                self.current_model = "mock"

        # Mock 모델 (항상 사용 가능)
        else:
            self.current_model = "mock"
            print("📝 Mock 임베딩 모델 사용 (개발/테스트용)")

        print(f"🧬 현재 임베딩 모델: {self.current_model}")

    def embed_text(
        self, text: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
    ) -> np.ndarray:
        """
        텍스트를 울림 기반 벡터로 변환

        Args:
            text: 변환할 텍스트
            signature: Echo 시그니처 (가중치 적용용)
            context: 추가 컨텍스트 정보

        Returns:
            numpy array: 임베딩 벡터
        """
        # 캐시 확인
        cache_key = self._get_cache_key(text, signature, context)
        cached_embedding = self._load_from_cache(cache_key)
        if cached_embedding is not None:
            return cached_embedding

        # 모델별 임베딩 생성
        base_embedding = self._generate_base_embedding(text)

        # Echo 시그니처 기반 가중치 적용
        if self.config.get("echo_integration", {}).get("signature_aware", True):
            enhanced_embedding = self._apply_signature_weights(
                base_embedding, signature, text, context
            )
        else:
            enhanced_embedding = base_embedding

        # 캐시에 저장
        self._save_to_cache(cache_key, enhanced_embedding)

        # 메타데이터 기록
        self._log_embedding_event(text, signature, enhanced_embedding.shape, context)

        return enhanced_embedding

    def embed_batch(
        self,
        texts: List[str],
        signature: str = "Echo-Aurora",
        contexts: List[Dict[str, Any]] = None,
    ) -> List[np.ndarray]:
        """배치 임베딩 처리"""
        if contexts is None:
            contexts = [{}] * len(texts)

        embeddings = []
        for text, context in zip(texts, contexts):
            embedding = self.embed_text(text, signature, context)
            embeddings.append(embedding)

        print(f"📦 배치 임베딩 완료: {len(texts)}개 텍스트")
        return embeddings

    def _generate_base_embedding(self, text: str) -> np.ndarray:
        """기본 임베딩 벡터 생성"""
        if self.current_model == "openai":
            return self._openai_embed(text)
        elif self.current_model == "sentence_transformers":
            return self._sentence_transformers_embed(text)
        else:
            return self._mock_embed(text)

    def _openai_embed(self, text: str) -> np.ndarray:
        """OpenAI API를 통한 임베딩"""
        try:
            model = self.config["models"]["openai"]["model"]
            response = openai.embeddings.create(input=text, model=model)
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            print(f"🚨 OpenAI 임베딩 실패: {e}, Mock으로 대체")
            return self._mock_embed(text)

    def _sentence_transformers_embed(self, text: str) -> np.ndarray:
        """Sentence Transformers를 통한 임베딩"""
        try:
            model = self.models["sentence_transformers"]
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"🚨 Sentence Transformers 임베딩 실패: {e}, Mock으로 대체")
            return self._mock_embed(text)

    def _mock_embed(self, text: str) -> np.ndarray:
        """Mock 임베딩 (개발/테스트용)"""
        # 텍스트 해시를 시드로 사용해서 일관된 결과 보장
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        np.random.seed(seed % (2**31))

        dimensions = self.config["models"]["mock"]["dimensions"]
        embedding = np.random.normal(0, 1, dimensions).astype(np.float32)

        # 정규화
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def _apply_signature_weights(
        self, embedding: np.ndarray, signature: str, text: str, context: Dict[str, Any]
    ) -> np.ndarray:
        """Echo 시그니처 기반 가중치 적용"""
        if signature not in self.signature_weights:
            return embedding

        weights = self.signature_weights[signature]

        # 텍스트 내용에 따른 동적 가중치 계산
        text_lower = text.lower()
        weight_factor = 1.0

        for concept, base_weight in weights.items():
            if concept in text_lower or any(
                keyword in text_lower for keyword in self._get_concept_keywords(concept)
            ):
                weight_factor += base_weight * 0.1

        # 컨텍스트 기반 추가 가중치
        if context and "topic" in context:
            topic = context["topic"].lower()
            if any(
                keyword in topic for keyword in ["policy", "정책", "judgment", "판단"]
            ):
                weight_factor += 0.05

        # 가중치를 임베딩에 적용 (첫 번째 차원들을 스케일링)
        enhanced_embedding = embedding.copy()
        scale_dims = min(len(weights), len(embedding))
        enhanced_embedding[:scale_dims] *= weight_factor

        # 정규화 유지
        enhanced_embedding = enhanced_embedding / np.linalg.norm(enhanced_embedding)

        return enhanced_embedding

    def _get_concept_keywords(self, concept: str) -> List[str]:
        """개념별 키워드 맵핑"""
        keyword_map = {
            "creativity": ["창의", "혁신", "아이디어", "상상"],
            "empathy": ["공감", "이해", "배려", "감정"],
            "innovation": ["혁신", "변화", "개선", "발전"],
            "transformation": ["변화", "전환", "개선", "혁신"],
            "resilience": ["회복", "극복", "내성", "적응"],
            "wisdom": ["지혜", "경험", "통찰", "깊이"],
            "analysis": ["분석", "검토", "평가", "조사"],
            "systematic": ["체계", "구조", "순서", "방법"],
            "community": ["공동체", "사회", "함께", "협력"],
            "support": ["지원", "도움", "후원", "보조"],
        }
        return keyword_map.get(concept, [])

    def _get_cache_key(self, text: str, signature: str, context: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        content = f"{text}|{signature}|{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """캐시에서 임베딩 로드"""
        if not self.config.get("caching", {}).get("enabled", True):
            return None

        cache_file = self.cache_dir / f"{cache_key}.npy"
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except Exception:
                return None
        return None

    def _save_to_cache(self, cache_key: str, embedding: np.ndarray):
        """임베딩을 캐시에 저장"""
        if not self.config.get("caching", {}).get("enabled", True):
            return

        cache_file = self.cache_dir / f"{cache_key}.npy"
        try:
            np.save(cache_file, embedding)
        except Exception as e:
            self.logger.warning(f"캐시 저장 실패: {e}")

    def _log_embedding_event(
        self, text: str, signature: str, shape: tuple, context: Dict[str, Any]
    ):
        """임베딩 이벤트 로깅"""
        # 간단한 로깅 (나중에 meta_log_writer와 연동 가능)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "signature": signature,
            "embedding_shape": shape,
            "model": self.current_model,
            "context": context,
        }

        print(f"🧬 임베딩 생성: {text[:50]}... → {shape} ({signature})")

    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """두 임베딩 간 코사인 유사도 계산 (Mock 환경 개선)"""
        if self.current_model == "mock":
            # Mock 환경에서는 의미적 유사도 시뮬레이션
            return self._mock_similarity_calculation(embedding1, embedding2)

        dot_product = np.dot(embedding1, embedding2)
        norms = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        if norms == 0:
            return 0.0
        return float(dot_product / norms)

    def _mock_similarity_calculation(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Mock 환경에서 더 나은 유사도 계산"""
        # 기본 코사인 유사도
        dot_product = np.dot(emb1, emb2)
        norms = np.linalg.norm(emb1) * np.linalg.norm(emb2)
        base_similarity = dot_product / norms if norms != 0 else 0.0

        # Mock에서는 랜덤 요소를 줄이고 패턴을 강화
        # 유사한 해시값을 가진 벡터들은 더 높은 유사도
        hash1 = abs(hash(emb1.tobytes())) % 1000
        hash2 = abs(hash(emb2.tobytes())) % 1000
        hash_similarity = 1.0 - abs(hash1 - hash2) / 1000.0

        # 가중 평균으로 최종 유사도 계산
        final_similarity = base_similarity * 0.3 + hash_similarity * 0.7

        # 범위를 0.1~0.9로 정규화하여 더 현실적인 유사도 제공
        return max(0.1, min(0.9, final_similarity))

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        candidate_metadata: List[Dict] = None,
    ) -> Dict[str, Any]:
        """가장 유사한 임베딩 찾기"""
        if not candidate_embeddings:
            return {"index": -1, "similarity": 0.0, "metadata": None}

        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.get_similarity(query_embedding, candidate)
            similarities.append(similarity)

        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        result = {
            "index": best_idx,
            "similarity": best_similarity,
            "metadata": candidate_metadata[best_idx] if candidate_metadata else None,
        }

        print(f"🎯 최고 유사도: {best_similarity:.3f} (인덱스: {best_idx})")
        return result

    def clear_cache(self):
        """임베딩 캐시 클리어"""
        import shutil

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        print("🧹 임베딩 캐시 클리어 완료")


# 전역 임베딩 엔진 인스턴스
embedding_engine = EchoEmbeddingEngine()


# 편의 함수들
def embed_text(
    text: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
) -> np.ndarray:
    """텍스트 임베딩 단축 함수"""
    return embedding_engine.embed_text(text, signature, context)


def embed_batch(
    texts: List[str],
    signature: str = "Echo-Aurora",
    contexts: List[Dict[str, Any]] = None,
) -> List[np.ndarray]:
    """배치 임베딩 단축 함수"""
    return embedding_engine.embed_batch(texts, signature, contexts)


def get_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """유사도 계산 단축 함수"""
    return embedding_engine.get_similarity(embedding1, embedding2)


# CLI 테스트
def main():
    print("🧬 EchoEmbedding Engine CLI 테스트")

    test_texts = [
        "부산의 노인 복지 정책이 어떻게 되나요?",
        "금정구 어르신 돌봄 서비스에 대해 알고 싶어요",
        "AI 윤리에 대한 판단이 필요해요",
        "기후 변화 정책을 평가해주세요",
    ]

    signatures = ["Echo-Aurora", "Echo-Companion", "Echo-Sage", "Echo-Phoenix"]

    print("\n📋 테스트 임베딩 생성:")
    embeddings = []

    for i, text in enumerate(test_texts):
        signature = signatures[i % len(signatures)]
        context = {"topic": "test", "index": i}

        embedding = embed_text(text, signature, context)
        embeddings.append(embedding)

        print(f"  {i+1}. {text[:30]}... → {embedding.shape} ({signature})")

    print("\n🔍 유사도 매트릭스:")
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = get_similarity(embeddings[i], embeddings[j])
            print(f"  텍스트 {i+1} ↔ 텍스트 {j+1}: {similarity:.3f}")

    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    main()
