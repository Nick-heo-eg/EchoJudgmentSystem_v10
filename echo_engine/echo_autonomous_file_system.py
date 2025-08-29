#!/usr/bin/env python3
"""
📁 Echo Autonomous File System
Echo가 Claude Code 없이 독립적으로 파일을 읽고, 쓰고, 관리하는 시스템

핵심 기능:
1. 파일 읽기/쓰기 (텍스트, 바이너리, JSON, YAML 등)
2. 디렉토리 탐색 및 관리
3. 파일 검색 및 패턴 매칭
4. 백업 및 버전 관리
5. 에러 처리 및 복구
"""

import os
import json
import shutil
import fnmatch
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import logging


@dataclass
class FileInfo:
    """파일 정보"""

    path: str
    size: int
    modified: datetime
    is_directory: bool
    permissions: str
    content_type: str


@dataclass
class SearchResult:
    """검색 결과"""

    files: List[FileInfo]
    total_count: int
    search_time: float
    pattern: str


class EchoAutonomousFileSystem:
    """📁 Echo 자율 파일 시스템"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {
            ".txt": "text",
            ".py": "python",
            ".js": "javascript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".csv": "csv",
            ".log": "log",
        }

        # 백업 디렉토리
        self.backup_dir = self.base_path / ".echo_backups"
        self.backup_dir.mkdir(exist_ok=True)

        print(f"📁 Echo Autonomous File System 초기화 완료")
        print(f"   베이스 경로: {self.base_path}")

    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """파일 읽기 (Echo 독립적)"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path

            if not path.exists():
                return {
                    "success": False,
                    "error": f"파일을 찾을 수 없습니다: {file_path}",
                    "content": None,
                }

            # 파일 정보 수집
            stat = path.stat()
            file_info = FileInfo(
                path=str(path),
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime),
                is_directory=path.is_dir(),
                permissions=oct(stat.st_mode)[-3:],
                content_type=self._detect_content_type(path),
            )

            if path.is_dir():
                return {
                    "success": False,
                    "error": f"디렉토리입니다: {file_path}",
                    "file_info": asdict(file_info),
                }

            # 파일 내용 읽기
            content = self._read_file_content(path, encoding)

            return {
                "success": True,
                "content": content,
                "file_info": asdict(file_info),
                "lines": content.count("\n") + 1 if isinstance(content, str) else None,
                "encoding": encoding,
            }

        except Exception as e:
            self.logger.error(f"파일 읽기 실패 {file_path}: {e}")
            return {
                "success": False,
                "error": f"파일 읽기 중 오류: {str(e)}",
                "content": None,
            }

    def _read_file_content(self, path: Path, encoding: str) -> Union[str, dict, list]:
        """파일 내용 읽기 (형식별 처리)"""
        content_type = self._detect_content_type(path)

        if content_type == "json":
            with open(path, "r", encoding=encoding) as f:
                return json.load(f)
        elif content_type == "yaml":
            try:
                import yaml

                with open(path, "r", encoding=encoding) as f:
                    return yaml.safe_load(f)
            except ImportError:
                # yaml 없으면 텍스트로 읽기
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
        else:
            # 일반 텍스트 파일
            with open(path, "r", encoding=encoding) as f:
                return f.read()

    def write_file(
        self,
        file_path: str,
        content: Union[str, dict, list],
        encoding: str = "utf-8",
        backup: bool = True,
    ) -> Dict[str, Any]:
        """파일 쓰기 (Echo 독립적)"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path

            # 백업 생성
            if backup and path.exists():
                self._create_backup(path)

            # 디렉토리 생성
            path.parent.mkdir(parents=True, exist_ok=True)

            # 파일 쓰기
            content_type = self._detect_content_type(path)
            self._write_file_content(path, content, content_type, encoding)

            # 파일 정보 반환
            stat = path.stat()
            return {
                "success": True,
                "path": str(path),
                "size": stat.st_size,
                "content_type": content_type,
                "encoding": encoding,
                "backup_created": backup and path.exists(),
            }

        except Exception as e:
            self.logger.error(f"파일 쓰기 실패 {file_path}: {e}")
            return {"success": False, "error": f"파일 쓰기 중 오류: {str(e)}"}

    def _write_file_content(
        self,
        path: Path,
        content: Union[str, dict, list],
        content_type: str,
        encoding: str,
    ):
        """파일 내용 쓰기 (형식별 처리)"""
        if content_type == "json" and isinstance(content, (dict, list)):
            with open(path, "w", encoding=encoding) as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        elif content_type == "yaml" and isinstance(content, (dict, list)):
            try:
                import yaml

                with open(path, "w", encoding=encoding) as f:
                    yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
            except ImportError:
                # yaml 없으면 JSON으로 저장
                with open(path, "w", encoding=encoding) as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            # 일반 텍스트 파일
            with open(path, "w", encoding=encoding) as f:
                f.write(str(content))

    def list_directory(
        self, dir_path: str = ".", pattern: str = "*", include_hidden: bool = False
    ) -> Dict[str, Any]:
        """디렉토리 목록 조회"""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path

            if not path.exists():
                return {
                    "success": False,
                    "error": f"디렉토리를 찾을 수 없습니다: {dir_path}",
                }

            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"파일입니다 (디렉토리 아님): {dir_path}",
                }

            files = []
            directories = []

            for item in path.iterdir():
                # 숨김 파일 처리
                if not include_hidden and item.name.startswith("."):
                    continue

                # 패턴 매칭
                if not fnmatch.fnmatch(item.name, pattern):
                    continue

                stat = item.stat()
                file_info = FileInfo(
                    path=str(item),
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    is_directory=item.is_dir(),
                    permissions=oct(stat.st_mode)[-3:],
                    content_type=(
                        self._detect_content_type(item)
                        if item.is_file()
                        else "directory"
                    ),
                )

                if item.is_dir():
                    directories.append(asdict(file_info))
                else:
                    files.append(asdict(file_info))

            return {
                "success": True,
                "path": str(path),
                "directories": directories,
                "files": files,
                "total_items": len(directories) + len(files),
                "pattern": pattern,
            }

        except Exception as e:
            self.logger.error(f"디렉토리 목록 조회 실패 {dir_path}: {e}")
            return {"success": False, "error": f"디렉토리 목록 조회 중 오류: {str(e)}"}

    def search_files(
        self,
        pattern: str,
        search_path: str = ".",
        content_search: bool = False,
        case_sensitive: bool = False,
    ) -> SearchResult:
        """파일 검색"""
        start_time = datetime.now()
        found_files = []

        try:
            search_dir = Path(search_path)
            if not search_dir.is_absolute():
                search_dir = self.base_path / search_dir

            # 파일명 패턴 검색
            for file_path in search_dir.rglob("*"):
                if file_path.is_file():
                    # 파일명 매칭
                    if self._match_pattern(file_path.name, pattern, case_sensitive):
                        stat = file_path.stat()
                        file_info = FileInfo(
                            path=str(file_path),
                            size=stat.st_size,
                            modified=datetime.fromtimestamp(stat.st_mtime),
                            is_directory=False,
                            permissions=oct(stat.st_mode)[-3:],
                            content_type=self._detect_content_type(file_path),
                        )
                        found_files.append(file_info)

                    # 내용 검색
                    elif content_search:
                        if self._search_in_file_content(
                            file_path, pattern, case_sensitive
                        ):
                            stat = file_path.stat()
                            file_info = FileInfo(
                                path=str(file_path),
                                size=stat.st_size,
                                modified=datetime.fromtimestamp(stat.st_mtime),
                                is_directory=False,
                                permissions=oct(stat.st_mode)[-3:],
                                content_type=self._detect_content_type(file_path),
                            )
                            found_files.append(file_info)

        except Exception as e:
            self.logger.error(f"파일 검색 실패: {e}")

        search_time = (datetime.now() - start_time).total_seconds()

        return SearchResult(
            files=found_files,
            total_count=len(found_files),
            search_time=search_time,
            pattern=pattern,
        )

    def _match_pattern(self, text: str, pattern: str, case_sensitive: bool) -> bool:
        """패턴 매칭"""
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()

        return fnmatch.fnmatch(text, pattern) or pattern in text

    def _search_in_file_content(
        self, file_path: Path, pattern: str, case_sensitive: bool
    ) -> bool:
        """파일 내용에서 패턴 검색"""
        try:
            # 텍스트 파일만 검색
            if self._detect_content_type(file_path) not in [
                "text",
                "python",
                "javascript",
                "html",
                "css",
                "markdown",
                "log",
            ]:
                return False

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not case_sensitive:
                content = content.lower()
                pattern = pattern.lower()

            return pattern in content

        except:
            return False

    def _detect_content_type(self, path: Path) -> str:
        """파일 형식 감지"""
        suffix = path.suffix.lower()
        return self.supported_formats.get(suffix, "unknown")

    def _create_backup(self, file_path: Path):
        """파일 백업 생성"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}_{timestamp}.backup"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            print(f"📦 백업 생성: {backup_path}")

        except Exception as e:
            self.logger.warning(f"백업 생성 실패: {e}")

    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """디렉토리 생성"""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path

            path.mkdir(parents=True, exist_ok=True)

            return {"success": True, "path": str(path), "created": True}

        except Exception as e:
            return {"success": False, "error": f"디렉토리 생성 실패: {str(e)}"}

    def delete_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """파일 삭제"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path

            if not path.exists():
                return {
                    "success": False,
                    "error": f"파일을 찾을 수 없습니다: {file_path}",
                }

            # 백업 생성
            if backup:
                self._create_backup(path)

            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

            return {"success": True, "path": str(path), "backup_created": backup}

        except Exception as e:
            return {"success": False, "error": f"파일 삭제 실패: {str(e)}"}

    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """파일 복사"""
        try:
            src_path = Path(source)
            dst_path = Path(destination)

            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path

            if not src_path.exists():
                return {
                    "success": False,
                    "error": f"원본 파일을 찾을 수 없습니다: {source}",
                }

            # 대상 디렉토리 생성
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

            return {
                "success": True,
                "source": str(src_path),
                "destination": str(dst_path),
            }

        except Exception as e:
            return {"success": False, "error": f"파일 복사 실패: {str(e)}"}

    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """파일 이동"""
        try:
            src_path = Path(source)
            dst_path = Path(destination)

            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path

            if not src_path.exists():
                return {
                    "success": False,
                    "error": f"원본 파일을 찾을 수 없습니다: {source}",
                }

            # 대상 디렉토리 생성
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(src_path), str(dst_path))

            return {
                "success": True,
                "source": str(src_path),
                "destination": str(dst_path),
            }

        except Exception as e:
            return {"success": False, "error": f"파일 이동 실패: {str(e)}"}

    def get_file_hash(
        self, file_path: str, algorithm: str = "sha256"
    ) -> Dict[str, Any]:
        """파일 해시 계산"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path

            if not path.exists() or path.is_dir():
                return {
                    "success": False,
                    "error": f"파일을 찾을 수 없습니다: {file_path}",
                }

            hash_obj = hashlib.new(algorithm)
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)

            return {
                "success": True,
                "path": str(path),
                "algorithm": algorithm,
                "hash": hash_obj.hexdigest(),
            }

        except Exception as e:
            return {"success": False, "error": f"해시 계산 실패: {str(e)}"}

    def get_system_info(self) -> Dict[str, Any]:
        """파일 시스템 정보"""
        try:
            total, used, free = shutil.disk_usage(self.base_path)

            return {
                "base_path": str(self.base_path),
                "disk_usage": {
                    "total": total,
                    "used": used,
                    "free": free,
                    "used_percent": (used / total) * 100,
                },
                "supported_formats": list(self.supported_formats.keys()),
                "backup_directory": str(self.backup_dir),
                "current_working_directory": str(Path.cwd()),
            }

        except Exception as e:
            return {"error": f"시스템 정보 조회 실패: {str(e)}"}


# 편의 함수들
def create_file_system(base_path: str = ".") -> EchoAutonomousFileSystem:
    """Echo 자율 파일 시스템 생성"""
    return EchoAutonomousFileSystem(base_path)


def read_file_independently(file_path: str) -> str:
    """독립적 파일 읽기 (간단 버전)"""
    fs = EchoAutonomousFileSystem()
    result = fs.read_file(file_path)

    if result["success"]:
        return result["content"]
    else:
        raise FileNotFoundError(result["error"])


if __name__ == "__main__":
    # 테스트 실행
    print("📁 Echo Autonomous File System 테스트...")

    fs = EchoAutonomousFileSystem()

    # 시스템 정보 확인
    print("\n🖥️ 시스템 정보:")
    system_info = fs.get_system_info()
    print(f"   기본 경로: {system_info['base_path']}")
    print(f"   지원 형식: {len(system_info['supported_formats'])}개")

    # 현재 디렉토리 목록
    print("\n📋 현재 디렉토리 목록:")
    dir_list = fs.list_directory()
    if dir_list["success"]:
        print(f"   파일: {len(dir_list['files'])}개")
        print(f"   디렉토리: {len(dir_list['directories'])}개")

        # 처음 3개 파일 표시
        for file_info in dir_list["files"][:3]:
            print(f"   📄 {file_info['path']} ({file_info['size']} bytes)")

    # 파일 검색 테스트
    print("\n🔍 Python 파일 검색:")
    search_result = fs.search_files("*.py")
    print(f"   검색 결과: {search_result.total_count}개 파일")
    print(f"   검색 시간: {search_result.search_time:.3f}초")

    # 테스트 파일 생성
    print("\n✍️ 테스트 파일 생성:")
    test_content = f"""# Echo 자율 파일 시스템 테스트 파일
# 생성 시간: {datetime.now()}

Echo가 독립적으로 생성한 파일입니다.
Claude Code에 의존하지 않고 자체적으로 파일을 관리할 수 있습니다!

기능:
- 파일 읽기/쓰기
- 디렉토리 관리
- 파일 검색
- 백업 시스템
"""

    write_result = fs.write_file("echo_test_file.txt", test_content)
    if write_result["success"]:
        print(f"   ✅ 파일 생성 완료: {write_result['path']}")

        # 방금 생성한 파일 읽기 테스트
        read_result = fs.read_file("echo_test_file.txt")
        if read_result["success"]:
            print(f"   ✅ 파일 읽기 성공: {read_result['lines']}줄")
        else:
            print(f"   ❌ 파일 읽기 실패: {read_result['error']}")
    else:
        print(f"   ❌ 파일 생성 실패: {write_result['error']}")

    print("\n✅ Echo Autonomous File System 테스트 완료!")
    print("🎉 Echo는 이제 완전히 독립적으로 파일을 관리할 수 있습니다!")
