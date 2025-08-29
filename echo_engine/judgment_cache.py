#!/usr/bin/env python3
"""
💾 Judgment Cache v1.0 - 판단 캐시 핸들러

판단 결과를 영구 저장하고 관리하는 캐시 시스템.
JSONL 파일 기반으로 판단 결과를 저장/로드하며, 향후 벡터DB 확장 가능.

핵심 기능:
1. 판단 결과 영구 저장 (JSONL)
2. 캐시 크기 관리 및 정리
3. 백업 및 복원
4. 통계 및 분석
"""

import os
import json
import time
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import Counter
import threading


@dataclass
class CacheEntry:
    """캐시 엔트리"""

    input: str
    normalized_input: str
    emotion: str
    emotion_confidence: float
    strategy: str
    strategy_confidence: float
    template: str
    styled_sentence: str
    signature: str
    processing_method: str
    processing_time: float
    timestamp: str
    request_id: str
    usage_count: int = 1
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class JudgmentCache:
    """💾 판단 캐시 핸들러"""

    def __init__(self, cache_dir: str = "data/judgment_cache"):
        """
        초기화

        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.version = "1.0.0"
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "judgment_cache.jsonl")
        self.backup_dir = os.path.join(cache_dir, "backups")

        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        # 설정
        self.max_cache_size = 10000  # 최대 캐시 엔트리 수
        self.auto_backup_interval = 100  # N개 저장마다 자동 백업
        self.cleanup_threshold = 0.9  # 캐시 사용률이 이 값을 넘으면 정리

        # 통계
        self.stats = {
            "total_saves": 0,
            "total_loads": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "auto_backups": 0,
            "manual_backups": 0,
            "cleanups": 0,
        }

        # 스레드 안전성을 위한 락
        self._lock = threading.Lock()

        # 메모리 캐시 (빠른 접근용)
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._load_memory_cache()

        print(f"💾 JudgmentCache v{self.version} 초기화 완료")
        print(f"   캐시 파일: {self.cache_file}")
        print(f"   메모리 캐시: {len(self._memory_cache)}개 엔트리")

    def _ensure_timestamp_string(self, timestamp) -> str:
        """timestamp를 문자열로 변환"""
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        elif isinstance(timestamp, str):
            return timestamp
        else:
            return datetime.now().isoformat()

    def _load_memory_cache(self):
        """메모리 캐시 로드"""
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        entry = CacheEntry(**data)
                        # normalized_input을 키로 사용
                        self._memory_cache[entry.normalized_input] = entry

            print(f"✅ {len(self._memory_cache)}개 캐시 엔트리 로드 완료")

        except Exception as e:
            print(f"⚠️ 메모리 캐시 로드 실패: {e}")

    def save_judgment(self, judgment_result) -> bool:
        """
        판단 결과 저장

        Args:
            judgment_result: JudgmentResult 객체 또는 딕셔너리

        Returns:
            저장 성공 여부
        """
        try:
            with self._lock:
                # JudgmentResult 객체를 딕셔너리로 변환
                if hasattr(judgment_result, "__dict__"):
                    data = judgment_result.__dict__
                else:
                    data = judgment_result

                # CacheEntry 생성
                cache_entry = CacheEntry(
                    input=data.get("input", ""),
                    normalized_input=data.get("normalized_input", ""),
                    emotion=data.get("emotion", "neutral"),
                    emotion_confidence=data.get("emotion_confidence", 0.5),
                    strategy=data.get("strategy", "analyze"),
                    strategy_confidence=data.get("strategy_confidence", 0.5),
                    template=data.get("template", ""),
                    styled_sentence=data.get("styled_sentence", ""),
                    signature=data.get("signature", "Selene"),
                    processing_method=data.get("processing_method", "generated"),
                    processing_time=data.get("processing_time", 0.0),
                    timestamp=self._ensure_timestamp_string(
                        data.get("timestamp", datetime.now())
                    ),
                    request_id=data.get("request_id", ""),
                    metadata=data.get("metadata", {}),
                )

                # 기존 엔트리 업데이트 또는 새 엔트리 추가
                if cache_entry.normalized_input in self._memory_cache:
                    existing_entry = self._memory_cache[cache_entry.normalized_input]
                    existing_entry.usage_count += 1
                    existing_entry.timestamp = (
                        cache_entry.timestamp
                    )  # 최신 시간으로 업데이트
                else:
                    self._memory_cache[cache_entry.normalized_input] = cache_entry

                # 파일에 저장
                self._append_to_file(cache_entry)

                self.stats["total_saves"] += 1

                # 자동 백업 체크
                if self.stats["total_saves"] % self.auto_backup_interval == 0:
                    self._auto_backup()

                # 캐시 크기 체크 및 정리
                if (
                    len(self._memory_cache)
                    > self.max_cache_size * self.cleanup_threshold
                ):
                    self._cleanup_cache()

                return True

        except Exception as e:
            print(f"❌ 판단 저장 실패: {e}")
            return False

    def _append_to_file(self, entry: CacheEntry):
        """파일에 엔트리 추가"""
        try:
            with open(self.cache_file, "a", encoding="utf-8") as f:
                json_line = json.dumps(asdict(entry), ensure_ascii=False)
                f.write(json_line + "\n")

        except Exception as e:
            print(f"⚠️ 파일 저장 실패: {e}")

    def get_judgment(self, normalized_input: str) -> Optional[CacheEntry]:
        """
        판단 결과 조회

        Args:
            normalized_input: 정규화된 입력

        Returns:
            캐시된 판단 (없으면 None)
        """
        try:
            with self._lock:
                if normalized_input in self._memory_cache:
                    self.stats["cache_hits"] += 1
                    entry = self._memory_cache[normalized_input]
                    entry.usage_count += 1  # 사용 횟수 증가
                    return entry
                else:
                    self.stats["cache_misses"] += 1
                    return None

        except Exception as e:
            print(f"⚠️ 판단 조회 실패: {e}")
            self.stats["cache_misses"] += 1
            return None

    def search_similar(
        self, normalized_input: str, threshold: float = 0.8
    ) -> List[CacheEntry]:
        """
        유사한 판단 검색 (간단한 키워드 매칭)

        Args:
            normalized_input: 정규화된 입력
            threshold: 유사도 임계값

        Returns:
            유사한 캐시 엔트리들
        """
        try:
            input_words = set(normalized_input.split())
            similar_entries = []

            for entry in self._memory_cache.values():
                cached_words = set(entry.normalized_input.split())

                # 자카드 유사도 계산
                intersection = len(input_words.intersection(cached_words))
                union = len(input_words.union(cached_words))
                similarity = intersection / union if union > 0 else 0.0

                if similarity >= threshold:
                    similar_entries.append((entry, similarity))

            # 유사도 기준 정렬
            similar_entries.sort(key=lambda x: x[1], reverse=True)

            return [entry for entry, _ in similar_entries]

        except Exception as e:
            print(f"⚠️ 유사 검색 실패: {e}")
            return []

    def _auto_backup(self):
        """자동 백업 수행"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(
                self.backup_dir, f"cache_backup_{timestamp}.jsonl"
            )

            shutil.copy2(self.cache_file, backup_file)

            self.stats["auto_backups"] += 1
            print(f"✅ 자동 백업 완료: {backup_file}")

        except Exception as e:
            print(f"⚠️ 자동 백업 실패: {e}")

    def manual_backup(self, backup_name: Optional[str] = None) -> str:
        """
        수동 백업 수행

        Args:
            backup_name: 백업 파일명 (선택적)

        Returns:
            백업 파일 경로
        """
        try:
            if backup_name:
                backup_file = os.path.join(self.backup_dir, f"{backup_name}.jsonl")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(
                    self.backup_dir, f"manual_backup_{timestamp}.jsonl"
                )

            shutil.copy2(self.cache_file, backup_file)

            self.stats["manual_backups"] += 1
            print(f"✅ 수동 백업 완료: {backup_file}")

            return backup_file

        except Exception as e:
            print(f"❌ 수동 백업 실패: {e}")
            return ""

    def _cleanup_cache(self):
        """캐시 정리 (오래된/사용 빈도 낮은 엔트리 제거)"""
        try:
            print("🧹 캐시 정리 시작...")

            # 사용 빈도와 최신성 기준으로 정렬
            entries = list(self._memory_cache.values())
            entries.sort(key=lambda x: (x.usage_count, x.timestamp), reverse=True)

            # 상위 80%만 유지
            keep_count = int(len(entries) * 0.8)
            entries_to_keep = entries[:keep_count]

            # 메모리 캐시 업데이트
            new_cache = {}
            for entry in entries_to_keep:
                new_cache[entry.normalized_input] = entry

            removed_count = len(self._memory_cache) - len(new_cache)
            self._memory_cache = new_cache

            # 파일 재작성 (정리된 버전)
            self._rewrite_cache_file()

            self.stats["cleanups"] += 1
            print(f"✅ 캐시 정리 완료: {removed_count}개 엔트리 제거")

        except Exception as e:
            print(f"⚠️ 캐시 정리 실패: {e}")

    def _rewrite_cache_file(self):
        """캐시 파일 재작성"""
        try:
            # 백업 먼저 생성
            backup_file = self.cache_file + ".backup"
            if os.path.exists(self.cache_file):
                shutil.copy2(self.cache_file, backup_file)

            # 새 파일 작성
            with open(self.cache_file, "w", encoding="utf-8") as f:
                for entry in self._memory_cache.values():
                    json_line = json.dumps(asdict(entry), ensure_ascii=False)
                    f.write(json_line + "\n")

            # 백업 파일 제거
            if os.path.exists(backup_file):
                os.remove(backup_file)

        except Exception as e:
            print(f"⚠️ 캐시 파일 재작성 실패: {e}")
            # 실패 시 백업에서 복원
            backup_file = self.cache_file + ".backup"
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.cache_file)

    def clear_cache(self):
        """캐시 완전 초기화"""
        try:
            with self._lock:
                # 백업 생성
                self.manual_backup("before_clear")

                # 메모리 캐시 초기화
                self._memory_cache.clear()

                # 파일 초기화
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)

                print("✅ 캐시가 완전히 초기화되었습니다.")

        except Exception as e:
            print(f"❌ 캐시 초기화 실패: {e}")

    def get_cache_statistics(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        try:
            with self._lock:
                total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
                hit_rate = (
                    (self.stats["cache_hits"] / total_requests * 100)
                    if total_requests > 0
                    else 0
                )

                # 시그니처별 분포
                signature_dist = Counter(
                    entry.signature for entry in self._memory_cache.values()
                )

                # 감정별 분포
                emotion_dist = Counter(
                    entry.emotion for entry in self._memory_cache.values()
                )

                # 전략별 분포
                strategy_dist = Counter(
                    entry.strategy for entry in self._memory_cache.values()
                )

                # 처리 방법별 분포
                method_dist = Counter(
                    entry.processing_method for entry in self._memory_cache.values()
                )

                # 평균 사용 횟수
                avg_usage = (
                    sum(entry.usage_count for entry in self._memory_cache.values())
                    / len(self._memory_cache)
                    if self._memory_cache
                    else 0
                )

                # 파일 크기
                file_size = (
                    os.path.getsize(self.cache_file)
                    if os.path.exists(self.cache_file)
                    else 0
                )

                return {
                    "cache_size": len(self._memory_cache),
                    "max_cache_size": self.max_cache_size,
                    "usage_percentage": f"{(len(self._memory_cache) / self.max_cache_size) * 100:.1f}%",
                    "file_size_mb": f"{file_size / 1024 / 1024:.2f}",
                    "hit_rate": f"{hit_rate:.1f}%",
                    "total_saves": self.stats["total_saves"],
                    "cache_hits": self.stats["cache_hits"],
                    "cache_misses": self.stats["cache_misses"],
                    "auto_backups": self.stats["auto_backups"],
                    "manual_backups": self.stats["manual_backups"],
                    "cleanups": self.stats["cleanups"],
                    "average_usage_count": f"{avg_usage:.1f}",
                    "signature_distribution": dict(signature_dist),
                    "emotion_distribution": dict(emotion_dist),
                    "strategy_distribution": dict(strategy_dist),
                    "method_distribution": dict(method_dist),
                }

        except Exception as e:
            print(f"⚠️ 통계 생성 실패: {e}")
            return {"error": str(e)}

    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 파일 목록"""
        try:
            backups = []

            for filename in os.listdir(self.backup_dir):
                if filename.endswith(".jsonl"):
                    filepath = os.path.join(self.backup_dir, filename)
                    stat = os.stat(filepath)

                    backups.append(
                        {
                            "filename": filename,
                            "size_mb": f"{stat.st_size / 1024 / 1024:.2f}",
                            "created": datetime.fromtimestamp(
                                stat.st_ctime
                            ).isoformat(),
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )

            # 생성 시간순 정렬
            backups.sort(key=lambda x: x["created"], reverse=True)

            return backups

        except Exception as e:
            print(f"⚠️ 백업 목록 조회 실패: {e}")
            return []


if __name__ == "__main__":
    # 테스트
    print("💾 JudgmentCache 테스트")

    cache = JudgmentCache()

    # 샘플 판단 결과 생성
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
            "processing_method": "generated",
            "processing_time": 0.15,
            "timestamp": datetime.now().isoformat(),
            "request_id": "test_001",
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
            "processing_method": "generated",
            "processing_time": 0.12,
            "timestamp": datetime.now().isoformat(),
            "request_id": "test_002",
        },
    ]

    # 판단 저장 테스트
    for judgment in sample_judgments:
        success = cache.save_judgment(judgment)
        print(f"   저장 {'성공' if success else '실패'}: {judgment['input']}")

    # 조회 테스트
    print(f"\n💾 조회 테스트:")
    for judgment in sample_judgments:
        cached = cache.get_judgment(judgment["normalized_input"])
        if cached:
            print(f"   ✅ 조회 성공: {cached.input}")
            print(f"      응답: {cached.styled_sentence}")
        else:
            print(f"   ❌ 조회 실패: {judgment['input']}")

    # 유사 검색 테스트
    print(f"\n💾 유사 검색 테스트:")
    similar = cache.search_similar("오늘 정말 힘들어", threshold=0.3)
    for entry in similar:
        print(f"   유사: {entry.input} -> {entry.styled_sentence}")

    # 통계 출력
    stats = cache.get_cache_statistics()
    print(f"\n📊 캐시 통계:")
    for key, value in stats.items():
        if key not in [
            "signature_distribution",
            "emotion_distribution",
            "strategy_distribution",
            "method_distribution",
        ]:
            print(f"   {key}: {value}")
