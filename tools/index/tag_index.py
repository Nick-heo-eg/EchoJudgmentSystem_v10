#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 2 수술: Tag I/O 집중 감축 시스템
mtime 기반 태그 캐싱으로 반복 파일 읽기 제거
# @owner: nick
# @expose
# @maturity: stable
"""
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "tools" / "cache"
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class TagCacheEntry:
    file_path: str
    mtime: float
    tags: Dict[str, Any]
    file_size: int


class TagIndex:
    """mtime 기반 태그 캐싱 시스템 - Stage 2 혈관 수술"""

    def __init__(self):
        self.cache_file = CACHE_DIR / "tag_index.pkl"
        self.cache: Dict[str, TagCacheEntry] = self._load_cache()
        self.hits = 0  # 캐시 히트
        self.misses = 0  # 캐시 미스

    def _load_cache(self) -> Dict[str, TagCacheEntry]:
        """캐시 로드 (바이너리 pickle 사용으로 I/O 최소화)"""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, "rb") as f:
                data = pickle.load(f)
                return {k: TagCacheEntry(**v) for k, v in data.items()}
        except Exception:
            return {}

    def _save_cache(self):
        """캐시 저장 (비동기적 백그라운드 저장 고려)"""
        try:
            data = {k: asdict(v) for k, v in self.cache.items()}
            with open(self.cache_file, "wb") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(f"태그 캐시 저장 실패: {e}")

    def get_tags(self, file_path: Path) -> Dict[str, Any]:
        """태그 조회 - mtime 기반 캐시 우선 검사"""
        key = str(file_path.relative_to(ROOT))

        try:
            stat = file_path.stat()
            current_mtime = stat.st_mtime
            current_size = stat.st_size
        except (OSError, ValueError):
            return {}

        # 캐시 히트 검사
        if key in self.cache:
            cached = self.cache[key]
            if cached.mtime == current_mtime and cached.file_size == current_size:
                self.hits += 1
                return cached.tags.copy()

        # 캐시 미스 - 실제 파일 읽기
        self.misses += 1
        tags = self._extract_tags_from_file(file_path)

        # 캐시 업데이트
        self.cache[key] = TagCacheEntry(
            file_path=key, mtime=current_mtime, tags=tags, file_size=current_size
        )

        return tags

    def _extract_tags_from_file(self, path: Path) -> Dict[str, Any]:
        """실제 파일에서 태그 추출 (기존 로직)"""
        try:
            txt = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return {}

        head = "\n".join(txt.splitlines()[:80])  # 상단 80줄만 스캔
        tags: Dict[str, Any] = {}

        import re

        if re.search(r"^\s*#\s*@expose\b", head, re.M):
            tags["expose"] = True
        m_owner = re.search(r"^\s*#\s*@owner:\s*([A-Za-z0-9_\-\.]+)", head, re.M)
        if m_owner:
            tags["owner"] = m_owner.group(1)
        m_maturity = re.search(
            r"^\s*#\s*@maturity:\s*(stable|beta|experimental|deprecated)",
            head,
            re.I | re.M,
        )
        if m_maturity:
            tags["maturity"] = m_maturity.group(1).lower()

        return tags

    def batch_update(self, file_paths: list[Path]):
        """배치 업데이트 - 여러 파일의 태그를 한번에 처리"""
        for path in file_paths:
            self.get_tags(path)  # 캐시 갱신

    def get_stats(self) -> Dict[str, Any]:
        """캐시 성능 통계"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_entries": len(self.cache),
            "cache_size_kb": (
                self.cache_file.stat().st_size // 1024
                if self.cache_file.exists()
                else 0
            ),
        }

    def cleanup_stale(self):
        """존재하지 않는 파일의 캐시 엔트리 정리"""
        stale_keys = []
        for key in self.cache.keys():
            file_path = ROOT / key
            if not file_path.exists():
                stale_keys.append(key)

        for key in stale_keys:
            del self.cache[key]

        if stale_keys:
            self._save_cache()

    def flush(self):
        """캐시를 디스크에 강제 저장"""
        self._save_cache()


# 전역 태그 인덱스 인스턴스
_tag_index: Optional[TagIndex] = None


def get_tag_index() -> TagIndex:
    """태그 인덱스 싱글톤 접근"""
    global _tag_index
    if _tag_index is None:
        _tag_index = TagIndex()
    return _tag_index


def extract_tags_cached(path: Path) -> Dict[str, Any]:
    """캐싱된 태그 추출 - feature_mapper.py에서 사용할 함수"""
    return get_tag_index().get_tags(path)


if __name__ == "__main__":
    # 태그 인덱스 성능 테스트
    from rich.console import Console

    console = Console()

    index = get_tag_index()

    # 모든 Python 파일에 대해 캐시 성능 테스트
    test_files = list(ROOT.rglob("*.py"))[:100]  # 100개 파일로 제한

    console.print(f"[blue]🧪 태그 캐시 성능 테스트: {len(test_files)}개 파일[/blue]")

    # 첫 번째 실행 (캐시 미스)
    for path in test_files:
        index.get_tags(path)

    stats1 = index.get_stats()
    console.print(f"[yellow]1차 실행 (캐시 구축): {stats1}[/yellow]")

    # 두 번째 실행 (캐시 히트)
    for path in test_files:
        index.get_tags(path)

    stats2 = index.get_stats()
    console.print(f"[green]2차 실행 (캐시 활용): {stats2}[/green]")

    index.flush()
    console.print("[cyan]✅ 캐시 디스크 저장 완료[/cyan]")
