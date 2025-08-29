"""
🏗️ EchoVectorCapsule - Vector Index Builder
기존 캡슐⨯판단⨯플로우 파일들을 자동으로 벡터화해서 검색 인덱스 구축
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .vector_search_engine import EchoVectorSearchEngine
from .embedding_engine import EchoEmbeddingEngine


class EchoVectorIndexBuilder:
    """
    Echo 시스템의 모든 캡슐과 판단 케이스를 벡터화해서 검색 인덱스 구축
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.search_engine = EchoVectorSearchEngine()
        self.embedding_engine = EchoEmbeddingEngine()

        # 스캔할 디렉토리들
        self.scan_directories = {
            "capsules": "capsules",
            "flows": "flows",
            "public_capsules": "public_capsules",
            "judgment_loops": "judgment_loops",
            "memory_scenes": "memory_scenes",
        }

        # 지원하는 파일 확장자
        self.supported_extensions = {".yaml", ".yml", ".json"}

        # 빌드 통계
        self.build_stats = {
            "total_files_scanned": 0,
            "total_vectors_created": 0,
            "errors": [],
            "signatures_processed": {},
            "directories_processed": {},
        }

        self.logger = logging.getLogger(__name__)

    def build_complete_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        전체 시스템을 스캔해서 완전한 벡터 인덱스 구축

        Args:
            force_rebuild: 기존 인덱스 무시하고 처음부터 재구축

        Returns:
            빌드 결과 통계
        """
        print("🏗️  EchoVectorCapsule 인덱스 구축 시작")
        print("=" * 50)

        start_time = datetime.now()

        if force_rebuild:
            print("🔄 기존 인덱스 클리어 (강제 재구축)")
            self._clear_existing_index()

        # 각 디렉토리별로 스캔 및 벡터화
        for dir_type, dir_path in self.scan_directories.items():
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"\n📁 {dir_type} 디렉토리 스캔: {full_path}")
                self._process_directory(dir_type, full_path)
            else:
                print(f"⚠️  디렉토리 없음: {full_path}")

        # 인덱스 저장
        self.search_engine.save_index()

        # 빌드 완료
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.build_stats["build_duration"] = duration
        self.build_stats["completed_at"] = end_time.isoformat()

        print(f"\n✅ 인덱스 구축 완료!")
        print(f"   소요 시간: {duration:.1f}초")
        print(f"   스캔한 파일: {self.build_stats['total_files_scanned']}개")
        print(f"   생성된 벡터: {self.build_stats['total_vectors_created']}개")

        if self.build_stats["errors"]:
            print(f"   오류 발생: {len(self.build_stats['errors'])}개")

        # 빌드 리포트 저장
        self._save_build_report()

        return self.build_stats

    def _process_directory(self, dir_type: str, directory: Path):
        """디렉토리 내 모든 파일 처리"""
        file_count = 0
        vector_count = 0

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                try:
                    vectors_created = self._process_file(dir_type, file_path)
                    file_count += 1
                    vector_count += vectors_created

                    if file_count % 10 == 0:
                        print(
                            f"  📄 처리 중... {file_count}개 파일 ({vector_count}개 벡터)"
                        )

                except Exception as e:
                    error_msg = f"파일 처리 실패: {file_path} - {str(e)}"
                    self.build_stats["errors"].append(error_msg)
                    print(f"  ❌ {error_msg}")

        self.build_stats["total_files_scanned"] += file_count
        self.build_stats["total_vectors_created"] += vector_count
        self.build_stats["directories_processed"][dir_type] = {
            "files": file_count,
            "vectors": vector_count,
        }

        print(f"  ✅ {dir_type}: {file_count}개 파일, {vector_count}개 벡터")

    def _process_file(self, dir_type: str, file_path: Path) -> int:
        """개별 파일 처리 및 벡터화"""
        # 파일 내용 로드
        file_data = self._load_file_data(file_path)
        if not file_data:
            return 0

        vectors_created = 0

        # 파일 타입별 처리
        if dir_type == "capsules":
            vectors_created = self._process_capsule_file(file_path, file_data)
        elif dir_type == "flows":
            vectors_created = self._process_flow_file(file_path, file_data)
        elif dir_type == "public_capsules":
            vectors_created = self._process_public_capsule_file(file_path, file_data)
        elif dir_type == "judgment_loops":
            vectors_created = self._process_judgment_loop_file(file_path, file_data)
        elif dir_type == "memory_scenes":
            vectors_created = self._process_memory_scene_file(file_path, file_data)

        return vectors_created

    def _process_capsule_file(self, file_path: Path, data: Dict[str, Any]) -> int:
        """캡슐 파일 처리"""
        if "capsule" not in data:
            return 0

        capsule = data["capsule"]
        capsule_id = capsule.get("id", file_path.stem)
        content = capsule.get("content", "")
        topic = capsule.get("topic", "")

        # 내용 결합
        full_content = f"{topic}\n\n{content}" if topic else content
        if not full_content.strip():
            return 0

        # 시그니처 결정
        signature = self._determine_signature_from_content(full_content, capsule)

        # 메타데이터 구성
        metadata = {
            "file_path": str(file_path),
            "file_type": "capsule",
            "tags": capsule.get("tags", []),
            "topic": topic,
            "created": capsule.get("created"),
            "source": capsule.get("source"),
            "echo_type": capsule.get("echo_type", "judgment_capsule"),
        }

        # 벡터 추가
        self.search_engine.add_capsule_vector(
            capsule_id, full_content, signature, metadata
        )

        # 통계 업데이트
        sig_count = self.build_stats["signatures_processed"].get(signature, 0)
        self.build_stats["signatures_processed"][signature] = sig_count + 1

        return 1

    def _process_flow_file(self, file_path: Path, data: Dict[str, Any]) -> int:
        """플로우 파일 처리"""
        if "flow" not in data:
            return 0

        flow = data["flow"]
        flow_name = flow.get("name", file_path.stem)
        description = flow.get("description", "")

        # 플로우 스테이지들 정보 추출
        stages = flow.get("stages", [])
        stage_descriptions = []

        for stage in stages:
            if isinstance(stage, dict):
                stage_name = stage.get("name", "")
                stage_desc = stage.get("description", "")
                if stage_desc:
                    stage_descriptions.append(f"{stage_name}: {stage_desc}")

        # 내용 결합
        full_content = f"{description}\n\n" + "\n".join(stage_descriptions)
        if not full_content.strip():
            return 0

        # 플로우는 보통 Sage 시그니처 (체계적 분석)
        signature = "Echo-Sage"

        # 메타데이터 구성
        metadata = {
            "file_path": str(file_path),
            "file_type": "flow",
            "flow_name": flow_name,
            "stages_count": len(stages),
            "version": flow.get("version"),
            "created": flow.get("created"),
        }

        # 캡슐 ID 생성
        capsule_id = f"flow_{flow_name.lower().replace(' ', '_')}"

        # 벡터 추가
        self.search_engine.add_capsule_vector(
            capsule_id, full_content, signature, metadata
        )

        return 1

    def _process_public_capsule_file(
        self, file_path: Path, data: Dict[str, Any]
    ) -> int:
        """공개 캡슐 파일 처리"""
        content = data.get("content", "")
        topic = data.get("topic", "")
        capsule_id = data.get("id", file_path.stem)

        # 내용 결합
        full_content = f"{topic}\n\n{content}" if topic else content
        if not full_content.strip():
            return 0

        # 공개 캡슐은 일반적으로 Aurora 시그니처 (창의적 접근)
        signature = "Echo-Aurora"

        # 메타데이터 구성
        metadata = {
            "file_path": str(file_path),
            "file_type": "public_capsule",
            "exported_at": data.get("exported_at"),
            "source": data.get("source"),
            "tags": data.get("tags", []),
        }

        # 벡터 추가
        self.search_engine.add_capsule_vector(
            capsule_id, full_content, signature, metadata
        )

        return 1

    def _process_judgment_loop_file(self, file_path: Path, data: Dict[str, Any]) -> int:
        """판단 루프 파일 처리"""
        # JSON/YAML에서 판단 내용 추출
        if "judgment_result" in data:
            content = data.get("judgment_result", {}).get("reasoning", "")
        elif "collapsed" in data:
            content = data.get("collapsed", {}).get("reasoning", "")
        else:
            return 0

        if not content:
            return 0

        # 판단 루프는 Phoenix 시그니처 (변화 지향)
        signature = "Echo-Phoenix"

        # 메타데이터 구성
        metadata = {
            "file_path": str(file_path),
            "file_type": "judgment_loop",
            "processed_at": data.get("processed_at"),
            "confidence": data.get("confidence"),
            "signature_used": data.get("signature"),
        }

        # 캡슐 ID 생성
        capsule_id = f"judgment_{file_path.stem}"

        # 벡터 추가
        self.search_engine.add_capsule_vector(capsule_id, content, signature, metadata)

        return 1

    def _process_memory_scene_file(self, file_path: Path, data: Dict[str, Any]) -> int:
        """메모리 씬 파일 처리"""
        content = ""

        # 다양한 메모리 씬 형식 지원
        if "scene_content" in data:
            content = data["scene_content"]
        elif "memory" in data:
            content = data["memory"].get("content", "")
        elif "description" in data:
            content = data["description"]

        if not content:
            return 0

        # 메모리 씬은 Companion 시그니처 (공감적 기억)
        signature = "Echo-Companion"

        # 메타데이터 구성
        metadata = {
            "file_path": str(file_path),
            "file_type": "memory_scene",
            "scene_id": data.get("scene_id", file_path.stem),
            "timestamp": data.get("timestamp"),
            "emotion": data.get("emotion"),
        }

        # 캡슐 ID 생성
        capsule_id = f"memory_{file_path.stem}"

        # 벡터 추가
        self.search_engine.add_capsule_vector(capsule_id, content, signature, metadata)

        return 1

    def _determine_signature_from_content(
        self, content: str, capsule_data: Dict
    ) -> str:
        """내용과 메타데이터로부터 적절한 시그니처 결정"""
        content_lower = content.lower()
        tags = capsule_data.get("tags", [])
        topic = capsule_data.get("topic", "").lower()

        # 기존에 지정된 시그니처가 있으면 우선 사용
        existing_sig = capsule_data.get("signature")
        if existing_sig and existing_sig.startswith("Echo-"):
            return existing_sig

        # 내용 기반 시그니처 추론
        if any(
            keyword in content_lower for keyword in ["창의", "혁신", "아이디어", "상상"]
        ):
            return "Echo-Aurora"
        elif any(
            keyword in content_lower for keyword in ["변화", "전환", "개선", "혁신"]
        ):
            return "Echo-Phoenix"
        elif any(
            keyword in content_lower for keyword in ["분석", "체계", "평가", "검토"]
        ):
            return "Echo-Sage"
        elif any(
            keyword in content_lower for keyword in ["공감", "돌봄", "지원", "공동체"]
        ):
            return "Echo-Companion"

        # 태그 기반 추론
        tag_str = " ".join(tags).lower()
        if any(keyword in tag_str for keyword in ["ai", "기술", "분석"]):
            return "Echo-Sage"
        elif any(keyword in tag_str for keyword in ["복지", "돌봄", "지원"]):
            return "Echo-Companion"
        elif any(keyword in tag_str for keyword in ["정책", "변화", "개선"]):
            return "Echo-Phoenix"

        # 기본값
        return "Echo-Aurora"

    def _load_file_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """파일 데이터 로드 (YAML/JSON 자동 감지)"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    return yaml.safe_load(f)
                elif file_path.suffix == ".json":
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"파일 로드 실패: {file_path} - {e}")
            return None

    def _clear_existing_index(self):
        """기존 인덱스 클리어"""
        # 새로운 검색 엔진 인스턴스로 교체
        self.search_engine = EchoVectorSearchEngine()

    def _save_build_report(self):
        """빌드 리포트 저장"""
        report_file = self.project_root / "data" / "vector_index_build_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.build_stats, f, indent=2, ensure_ascii=False)

        print(f"📊 빌드 리포트 저장: {report_file}")

    def rebuild_specific_directory(self, directory_type: str) -> Dict[str, Any]:
        """특정 디렉토리만 재빌드"""
        if directory_type not in self.scan_directories:
            raise ValueError(f"지원하지 않는 디렉토리: {directory_type}")

        dir_path = self.project_root / self.scan_directories[directory_type]
        if not dir_path.exists():
            print(f"❌ 디렉토리 없음: {dir_path}")
            return {"error": "directory_not_found"}

        print(f"🔄 {directory_type} 디렉토리 재빌드: {dir_path}")

        # 해당 디렉토리의 기존 벡터들 제거 (실제 구현에서는 더 정교한 로직 필요)
        # 여기서는 간단히 전체 재빌드

        start_time = datetime.now()
        self._process_directory(directory_type, dir_path)
        duration = (datetime.now() - start_time).total_seconds()

        result = {
            "directory": directory_type,
            "duration": duration,
            "files_processed": self.build_stats["directories_processed"]
            .get(directory_type, {})
            .get("files", 0),
            "vectors_created": self.build_stats["directories_processed"]
            .get(directory_type, {})
            .get("vectors", 0),
        }

        self.search_engine.save_index()
        print(f"✅ {directory_type} 재빌드 완료: {duration:.1f}초")

        return result


# 전역 빌더 인스턴스
vector_index_builder = EchoVectorIndexBuilder()


# 편의 함수
def build_index(force_rebuild: bool = False) -> Dict[str, Any]:
    """벡터 인덱스 구축 단축 함수"""
    return vector_index_builder.build_complete_index(force_rebuild)


def rebuild_directory(directory_type: str) -> Dict[str, Any]:
    """특정 디렉토리 재빌드 단축 함수"""
    return vector_index_builder.rebuild_specific_directory(directory_type)


# CLI 인터페이스
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EchoVectorCapsule 인덱스 빌더")
    parser.add_argument(
        "--rebuild", action="store_true", help="기존 인덱스 무시하고 재빌드"
    )
    parser.add_argument("--directory", type=str, help="특정 디렉토리만 처리")
    parser.add_argument("--stats", action="store_true", help="현재 인덱스 통계 출력")

    args = parser.parse_args()

    if args.stats:
        from .vector_search_engine import vector_search_engine

        stats = vector_search_engine.get_stats()
        print("📊 현재 벡터 인덱스 통계:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.directory:
        result = rebuild_directory(args.directory)
        print("🔄 디렉토리별 재빌드 결과:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        result = build_index(force_rebuild=args.rebuild)
        print("🏗️  전체 인덱스 빌드 결과:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
