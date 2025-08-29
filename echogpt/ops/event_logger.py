#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Event Logger
Intent analysis event logging for online distillation
"""
import os
import json
import hashlib
import datetime
import re
from typing import Dict, Any, List, Optional
from pathlib import Path


class EventLogger:
    """Intent 분석 이벤트 로거 (Pipeline용)"""

    def __init__(self, cfg: Dict[str, Any], logger=None):
        self.cfg = cfg
        self.logger = logger

        # 설정 추출
        storage_cfg = cfg.get("storage", {})
        privacy_cfg = cfg.get("privacy", {})

        self.events_dir = Path(storage_cfg.get("events_dir", "meta_logs/traces"))
        self.redact_rules = privacy_cfg.get(
            "redact_rules", ["phone", "email", "address"]
        )

        # 디렉토리 생성
        self.events_dir.mkdir(parents=True, exist_ok=True)

        # 리덕션 패턴 컴파일
        self._compile_redact_patterns()

    async def log_async(
        self,
        text: str,
        teacher_result: Optional[Dict[str, Any]],
        student_result: Optional[Dict[str, Any]],
        final_intent: str,
        final_confidence: float,
        latency_ms: int,
        context: Dict[str, Any] = None,
    ) -> None:
        """비동기 이벤트 로깅"""
        try:
            # 텍스트 해시 생성
            text_hash = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

            # 개인정보 마스킹
            text_redacted = self._redact_text(text)

            # 이벤트 레코드 생성
            record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "text_hash": text_hash,
                "text_redacted": text_redacted,
                "text_length": len(text),
                "teacher_result": teacher_result,
                "student_result": student_result,
                "final_intent": final_intent,
                "final_confidence": final_confidence,
                "latency_ms": latency_ms,
                "context": context or {},
                "agreement": self._check_agreement(teacher_result, student_result),
                "confidence_gap": self._calculate_confidence_gap(
                    teacher_result, student_result
                ),
            }

            # 날짜별 파일에 JSONL 형식으로 저장
            today = datetime.date.today().isoformat()
            log_file = self.events_dir / f"{today}.jsonl"

            # 비동기 파일 쓰기 (실제로는 동기지만 래퍼)
            import asyncio

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_record, log_file, record)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Event logging failed: {e}")
            else:
                print(f"⚠️ Event logging failed: {e}")

    def _write_record(self, log_file: Path, record: Dict[str, Any]):
        """레코드 파일 쓰기 (스레드풀용 동기 함수)"""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            raise e

    def _compile_redact_patterns(self):
        """개인정보 마스킹 패턴 컴파일"""
        self.patterns = {}

        # 전화번호 패턴
        if "phone" in self.redact_rules:
            self.patterns["phone"] = [
                re.compile(r"\b\d{3}-\d{3,4}-\d{4}\b"),  # 010-1234-5678
                re.compile(r"\b\d{2,3}\d{3,4}\d{4}\b"),  # 01012345678
            ]

        # 이메일 패턴
        if "email" in self.redact_rules:
            self.patterns["email"] = [
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
            ]

        # 주소 패턴 (간단한 케이스)
        if "address" in self.redact_rules:
            self.patterns["address"] = [
                re.compile(r"\b\d+[동호]\b"),  # 101동, 502호
                re.compile(
                    r"\b[가-힣]+시\s+[가-힣]+구\s+[가-힣]+동\b"
                ),  # 성남시 분당구 정자동
            ]

    def _redact_text(self, text: str) -> str:
        """개인정보 마스킹"""
        redacted = text

        for rule_type, patterns in self.patterns.items():
            for pattern in patterns:
                if rule_type == "phone":
                    redacted = pattern.sub("***-****-****", redacted)
                elif rule_type == "email":
                    redacted = pattern.sub("****@****.***", redacted)
                elif rule_type == "address":
                    redacted = pattern.sub("***", redacted)

        return redacted

    def _check_agreement(
        self, teacher: Optional[Dict], student: Optional[Dict]
    ) -> Optional[bool]:
        """Teacher-Student 일치 여부 확인"""
        if not teacher or not student:
            return None

        teacher_intent = teacher.get("intent", "")
        student_intent = student.get("intent", "")

        return teacher_intent == student_intent

    def _calculate_confidence_gap(
        self, teacher: Optional[Dict], student: Optional[Dict]
    ) -> Optional[float]:
        """신뢰도 차이 계산"""
        if not teacher or not student:
            return None

        teacher_conf = teacher.get("confidence", 0.0)
        student_conf = student.get("confidence", 0.0)

        return abs(teacher_conf - student_conf)

    def log(
        self,
        text: str,
        teacher: Optional[Dict[str, Any]],
        student: Optional[Dict[str, Any]],
        intent: Dict[str, Any],
    ):
        """동기 이벤트 로깅 (호환성용)"""

        # 텍스트 해시 생성
        text_hash = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

        # 개인정보 마스킹
        text_redacted = self._redact_text(text)

        # 이벤트 레코드 생성
        record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "text_hash": text_hash,
            "text_redacted": text_redacted,
            "text_length": len(text),
            "teacher_result": teacher,
            "student_result": student,
            "final_intent": intent,
            "agreement": self._check_agreement(teacher, student),
            "confidence_gap": self._calculate_confidence_gap(teacher, student),
        }

        # 날짜별 파일에 JSONL 형식으로 저장
        today = datetime.date.today().isoformat()
        log_file = self.events_dir / f"{today}.jsonl"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to write event log: {e}")
            else:
                print(f"Failed to write event log: {e}")

    def get_recent_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """최근 이벤트 조회"""
        events = []

        for i in range(days):
            date = datetime.date.today() - datetime.timedelta(days=i)
            log_file = self.events_dir / f"{date.isoformat()}.jsonl"

            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                events.append(json.loads(line))
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Failed to read log file {log_file}: {e}")
                    else:
                        print(f"Failed to read log file {log_file}: {e}")

        # 시간순 정렬 (최신 순)
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return events

    def get_training_data(
        self, days: int = 30, min_confidence: float = 0.8
    ) -> List[Dict[str, Any]]:
        """증류 학습용 데이터 추출"""
        events = self.get_recent_events(days)

        training_data = []
        for event in events:
            teacher = event.get("teacher_result")
            if (
                teacher
                and event.get("agreement")  # Teacher-Student 일치
                and teacher.get("confidence", 0) >= min_confidence
            ):  # 높은 신뢰도

                training_data.append(
                    {
                        "text": event["text_redacted"],
                        "label": teacher["intent"],
                        "confidence": teacher["confidence"],
                    }
                )

        return training_data

    def cleanup_old_logs(self, retention_days: int = 30) -> int:
        """오래된 로그 정리"""
        cutoff_date = datetime.date.today() - datetime.timedelta(days=retention_days)
        cleaned_count = 0

        for log_file in self.events_dir.glob("*.jsonl"):
            try:
                # 파일명에서 날짜 추출 (YYYY-MM-DD.jsonl)
                date_str = log_file.stem
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                if file_date < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1

            except (ValueError, OSError) as e:
                if self.logger:
                    self.logger.error(f"Failed to process log file {log_file}: {e}")
                else:
                    print(f"Failed to process log file {log_file}: {e}")

        return cleaned_count


# 레거시 호환성을 위한 별칭
IntentEventLogger = EventLogger

# CLI 실행 지원
if __name__ == "__main__":
    import asyncio
    import sys
    import yaml

    async def main():
        try:
            # 설정 로드
            with open("config/echogpt.yaml", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            # 로거 초기화
            logger = EventLogger(cfg)

            # 명령어 처리
            command = sys.argv[1] if len(sys.argv) > 1 else "info"

            if command == "info":
                print("📂 Event Logger Info:")
                print(f"  Events dir: {logger.events_dir}")
                print(f"  Redact rules: {logger.redact_rules}")
                print(f"  Directory exists: {logger.events_dir.exists()}")

            elif command == "test" and len(sys.argv) > 2:
                text = " ".join(sys.argv[2:])
                print(f"🧪 Testing event logging with: {text}")

                # Mock 결과로 테스트
                teacher_result = {"intent": "general_chat", "confidence": 0.8}
                student_result = {"intent": "general_chat", "confidence": 0.7}

                await logger.log_async(
                    text=text,
                    teacher_result=teacher_result,
                    student_result=student_result,
                    final_intent="general_chat",
                    final_confidence=0.8,
                    latency_ms=1500,
                )

                print("✅ Event logged successfully")

            elif command == "recent":
                days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
                events = logger.get_recent_events(days)
                print(f"📜 Recent {days} days events: {len(events)} found")

                for i, event in enumerate(events[:5]):  # 최근 5개만 표시
                    print(
                        f"  [{i+1}] {event.get('timestamp', 'N/A')}: {event.get('final_intent', 'N/A')}"
                    )

            elif command == "cleanup":
                retention_days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
                cleaned = logger.cleanup_old_logs(retention_days)
                print(f"🧹 Cleaned up {cleaned} old log files")

            else:
                print(
                    "Usage: python -m ops.event_logger [info|test <text>|recent [days]|cleanup [retention_days]]"
                )

        except Exception as e:
            print(f"❌ CLI error: {e}")
            sys.exit(1)

    asyncio.run(main())
