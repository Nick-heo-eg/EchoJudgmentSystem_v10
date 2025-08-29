#!/usr/bin/env python3
"""
문서 RAG 인덱서
- 다양한 문서를 벡터 데이터베이스에 인덱싱
- FAISS/pgvector 지원
- 로컬 임베딩 모델 사용 (KoSimCSE/E5)
"""

import argparse
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# 문서 처리
import PyPDF2
import docx
from markdown import markdown
from bs4 import BeautifulSoup

# 벡터 검색
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIndexer:
    """문서 RAG 인덱서"""

    def __init__(
        self,
        model_name: str = "jhgan/ko-sroberta-multitask",
        vector_store_path: str = "echo_engine/rag/vector_store",
        chunk_size: int = 500,
    ):

        self.model_name = model_name
        self.vector_store_path = Path(vector_store_path)
        self.chunk_size = chunk_size

        # 벡터 저장소 디렉토리 생성
        self.vector_store_path.mkdir(exist_ok=True, parents=True)

        # 임베딩 모델 로드
        self.embedding_model = self._load_embedding_model()
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # FAISS 인덱스
        self.index = None
        self.documents = []  # 문서 메타데이터

        logger.info(f"DocumentIndexer 초기화 완료: {model_name}")

    def _load_embedding_model(self) -> SentenceTransformer:
        """임베딩 모델 로드"""
        try:
            # 한국어 모델 우선 시도
            model = SentenceTransformer(self.model_name)
            logger.info(f"임베딩 모델 로드 성공: {self.model_name}")
            return model
        except Exception as e:
            logger.warning(f"모델 로드 실패, 기본 모델 사용: {e}")
            # 기본 영어 모델로 폴백
            return SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> np.ndarray:
        """텍스트 임베딩 생성"""
        return self.embedding_model.encode([text])[0]

    def build_index(self, document_paths: List[str]):
        """문서들을 인덱싱하여 벡터 저장소 구축"""
        logger.info(f"인덱스 구축 시작: {len(document_paths)}개 경로")

        all_chunks = []
        all_metadata = []

        for path_str in document_paths:
            path = Path(path_str)

            if path.is_file():
                chunks, metadata = self._process_file(path)
                all_chunks.extend(chunks)
                all_metadata.extend(metadata)
            elif path.is_dir():
                for file_path in self._find_documents(path):
                    chunks, metadata = self._process_file(file_path)
                    all_chunks.extend(chunks)
                    all_metadata.extend(metadata)

        if not all_chunks:
            logger.warning("처리할 문서가 없습니다")
            return

        # 임베딩 생성
        logger.info(f"임베딩 생성 중: {len(all_chunks)}개 청크")
        embeddings = self.embedding_model.encode(all_chunks)

        # FAISS 인덱스 생성
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # 코사인 유사도
        faiss.normalize_L2(embeddings)  # 정규화
        self.index.add(embeddings.astype("float32"))

        # 문서 메타데이터 저장
        self.documents = all_metadata

        # 인덱스 저장
        self._save_index()

        logger.info(
            f"인덱스 구축 완료: {len(all_chunks)}개 청크, {len(set(m['file_path'] for m in all_metadata))}개 파일"
        )

    def _find_documents(self, directory: Path) -> List[Path]:
        """디렉토리에서 문서 파일 찾기"""
        supported_extensions = {
            ".txt",
            ".md",
            ".pdf",
            ".docx",
            ".json",
            ".yaml",
            ".yml",
            ".py",
        }

        documents = []
        for ext in supported_extensions:
            documents.extend(directory.rglob(f"*{ext}"))

        return documents

    def _process_file(self, file_path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
        """파일을 청크로 분할하고 메타데이터 생성"""
        try:
            # 파일 내용 읽기
            content = self._read_file(file_path)
            if not content:
                return [], []

            # 청크 분할
            chunks = self._split_into_chunks(content, self.chunk_size)

            # 메타데이터 생성
            metadata = []
            for i, chunk in enumerate(chunks):
                metadata.append(
                    {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "chunk_index": i,
                        "content": chunk,
                        "file_type": file_path.suffix.lower(),
                        "file_size": (
                            file_path.stat().st_size if file_path.exists() else 0
                        ),
                    }
                )

            logger.debug(f"파일 처리 완료: {file_path.name} ({len(chunks)}개 청크)")
            return chunks, metadata

        except Exception as e:
            logger.error(f"파일 처리 실패: {file_path} - {e}")
            return [], []

    def _read_file(self, file_path: Path) -> str:
        """파일 타입별로 내용 읽기"""
        ext = file_path.suffix.lower()

        try:
            if ext == ".pdf":
                return self._read_pdf(file_path)
            elif ext == ".docx":
                return self._read_docx(file_path)
            elif ext == ".md":
                return self._read_markdown(file_path)
            elif ext in [".txt", ".py", ".yaml", ".yml", ".json"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                logger.warning(f"지원하지 않는 파일 형식: {ext}")
                return ""
        except Exception as e:
            logger.error(f"파일 읽기 실패: {file_path} - {e}")
            return ""

    def _read_pdf(self, file_path: Path) -> str:
        """PDF 파일 읽기"""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"PDF 읽기 실패: {e}")
            return ""

    def _read_docx(self, file_path: Path) -> str:
        """DOCX 파일 읽기"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX 읽기 실패: {e}")
            return ""

    def _read_markdown(self, file_path: Path) -> str:
        """마크다운 파일 읽기"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # 마크다운을 HTML로 변환 후 텍스트 추출
            html = markdown(md_content)
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()
        except Exception as e:
            logger.error(f"마크다운 읽기 실패: {e}")
            return ""

    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """텍스트를 청크로 분할"""
        if not text:
            return []

        # 문장 단위로 분할
        sentences = text.replace("\n", " ").split(".")

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 청크 크기 초과 시 새 청크 시작
            if len(current_chunk) + len(sentence) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def search_topk(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """상위 k개 유사 문서 검색"""
        if not self.index or not self.documents:
            self._load_index()

        if not self.index:
            logger.warning("인덱스가 없습니다")
            return []

        # 쿼리 임베딩 생성
        query_embedding = self.embed(query)
        query_embedding = query_embedding.reshape(1, -1).astype("float32")
        faiss.normalize_L2(query_embedding)

        # 검색 실행
        scores, indices = self.index.search(query_embedding, k)

        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["similarity_score"] = float(score)
                doc["rank"] = i + 1
                results.append(doc)

        return results

    def _save_index(self):
        """인덱스와 메타데이터 저장"""
        # FAISS 인덱스 저장
        index_path = self.vector_store_path / "faiss.index"
        faiss.write_index(self.index, str(index_path))

        # 문서 메타데이터 저장
        metadata_path = self.vector_store_path / "documents.pkl"
        with open(metadata_path, "wb") as f:
            pickle.dump(self.documents, f)

        # 설정 정보 저장
        config = {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "chunk_size": self.chunk_size,
            "document_count": len(self.documents),
        }
        config_path = self.vector_store_path / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        logger.info(f"인덱스 저장 완료: {self.vector_store_path}")

    def _load_index(self):
        """저장된 인덱스 로드"""
        try:
            index_path = self.vector_store_path / "faiss.index"
            metadata_path = self.vector_store_path / "documents.pkl"
            config_path = self.vector_store_path / "config.json"

            if not all(
                [index_path.exists(), metadata_path.exists(), config_path.exists()]
            ):
                logger.warning("인덱스 파일이 없습니다")
                return

            # 설정 로드
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # FAISS 인덱스 로드
            self.index = faiss.read_index(str(index_path))

            # 문서 메타데이터 로드
            with open(metadata_path, "rb") as f:
                self.documents = pickle.load(f)

            logger.info(f"인덱스 로드 완료: {len(self.documents)}개 문서")

        except Exception as e:
            logger.error(f"인덱스 로드 실패: {e}")
            self.index = None
            self.documents = []

    def get_index_stats(self) -> Dict[str, Any]:
        """인덱스 통계 정보"""
        if not self.index:
            self._load_index()

        if not self.index:
            return {"status": "no_index"}

        file_types = {}
        for doc in self.documents:
            file_type = doc.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1

        unique_files = len(set(doc["file_path"] for doc in self.documents))

        return {
            "status": "ready",
            "total_chunks": len(self.documents),
            "unique_files": unique_files,
            "file_types": file_types,
            "embedding_model": self.model_name,
            "embedding_dim": self.embedding_dim,
            "vector_store_path": str(self.vector_store_path),
        }


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="문서 RAG 인덱스 구축")
    parser.add_argument("--build", nargs="+", help="인덱싱할 문서 경로들")
    parser.add_argument(
        "--model", default="jhgan/ko-sroberta-multitask", help="임베딩 모델"
    )
    parser.add_argument(
        "--output", default="echo_engine/rag/vector_store", help="벡터 저장소 경로"
    )
    parser.add_argument("--chunk-size", type=int, default=500, help="청크 크기")
    parser.add_argument("--search", help="검색 테스트 쿼리")

    args = parser.parse_args()

    indexer = DocumentIndexer(
        model_name=args.model, vector_store_path=args.output, chunk_size=args.chunk_size
    )

    if args.build:
        # 인덱스 구축
        indexer.build_index(args.build)

        # 통계 출력
        stats = indexer.get_index_stats()
        print(f"\n✅ 인덱스 구축 완료:")
        print(f"   총 청크: {stats['total_chunks']}개")
        print(f"   파일 수: {stats['unique_files']}개")
        print(f"   파일 타입: {stats['file_types']}")

    if args.search:
        # 검색 테스트
        results = indexer.search_topk(args.search, k=3)
        print(f"\n🔍 검색 결과 ('{args.search}'):")
        for i, result in enumerate(results, 1):
            print(
                f"{i}. {result['file_name']} (유사도: {result['similarity_score']:.3f})"
            )
            print(f"   {result['content'][:100]}...")


if __name__ == "__main__":
    main()
