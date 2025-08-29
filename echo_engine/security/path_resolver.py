#!/usr/bin/env python3
"""
🛡️ Echo IDE Path Resolver - 경로 탈출 차단
보안 기능: 워크스페이스 경계 강제, 상대경로/심볼릭링크 차단
"""

import os
from pathlib import Path
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)


class PathSecurityError(Exception):
    """경로 보안 위반 예외"""

    pass


class PathResolver:
    """🛡️ 보안 경로 해결기"""

    def __init__(self, workspace_root: Union[str, Path]):
        self.workspace_root = Path(workspace_root).resolve()
        self.allowed_extensions = {
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".md",
            ".txt",
            ".csv",
            ".xml",
            ".sql",
            ".sh",
            ".bat",
        }

        # 🚫 금지된 경로 패턴들
        self.forbidden_patterns = [
            "..",
            "~",
            "/etc",
            "/var",
            "/tmp",
            "/home",
            ".ssh",
            ".env",
            "node_modules",
            "__pycache__",
        ]

    def resolve_safe_path(self, target_path: str) -> Path:
        """
        안전한 경로 해결
        🛡️ B1: 경로 탈출 차단
        """
        try:
            # 1. 기본 경로 정규화
            target = Path(target_path)

            # 2. 절대경로인 경우 워크스페이스 기준으로 변환
            if target.is_absolute():
                # 절대경로가 워크스페이스 내부인지 확인
                try:
                    target.resolve().relative_to(self.workspace_root)
                except ValueError:
                    raise PathSecurityError(f"🚫 절대경로 워크스페이스 탈출: {target}")
            else:
                # 상대경로를 워크스페이스 기준으로 해결
                target = self.workspace_root / target

            # 3. 최종 경로 해결
            resolved = target.resolve()

            # 4. 워크스페이스 경계 검증
            try:
                resolved.relative_to(self.workspace_root)
            except ValueError:
                raise PathSecurityError(f"🚫 워크스페이스 탈출 시도: {resolved}")

            # 5. 금지된 패턴 검사
            path_str = str(resolved)
            for pattern in self.forbidden_patterns:
                if pattern in path_str:
                    raise PathSecurityError(
                        f"🚫 금지된 경로 패턴 '{pattern}': {resolved}"
                    )

            # 6. 심볼릭 링크 검사
            if resolved.is_symlink():
                real_path = resolved.resolve()
                try:
                    real_path.relative_to(self.workspace_root)
                except ValueError:
                    raise PathSecurityError(
                        f"🚫 심볼릭 링크 탈출: {resolved} -> {real_path}"
                    )

            # 7. 파일 확장자 검증 (선택적)
            if (
                resolved.suffix
                and resolved.suffix.lower() not in self.allowed_extensions
            ):
                logger.warning(f"⚠️ 비허용 확장자: {resolved.suffix} in {resolved}")

            logger.info(f"✅ 경로 검증 통과: {resolved}")
            return resolved

        except Exception as e:
            logger.error(f"🛡️ 경로 보안 검증 실패: {target_path} -> {e}")
            raise PathSecurityError(f"경로 보안 위반: {e}")

    def validate_write_access(self, path: Path) -> bool:
        """쓰기 권한 검증"""
        try:
            # 부모 디렉토리가 워크스페이스 내부인지 확인
            parent = path.parent
            parent.relative_to(self.workspace_root)

            # 시스템 중요 파일 보호
            protected_files = [".env", "config.yaml", "secrets.json"]
            if path.name in protected_files:
                raise PathSecurityError(f"🚫 보호된 파일: {path.name}")

            return True

        except ValueError:
            raise PathSecurityError(f"🚫 쓰기 권한 없음: {path}")

    def get_relative_path(self, path: Path) -> str:
        """워크스페이스 기준 상대경로 반환"""
        try:
            return str(path.relative_to(self.workspace_root))
        except ValueError:
            return str(path)


# 전역 해결기 인스턴스
_resolver = None


def get_path_resolver(workspace_root: Optional[str] = None) -> PathResolver:
    """경로 해결기 싱글톤"""
    global _resolver
    if _resolver is None or workspace_root:
        root = workspace_root or os.getcwd()
        _resolver = PathResolver(root)
    return _resolver


def resolve_safe_path(target_path: str) -> Path:
    """안전 경로 해결 (편의 함수)"""
    resolver = get_path_resolver()
    return resolver.resolve_safe_path(target_path)
