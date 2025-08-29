#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Distillation Datasets
Data loader for Teacher-Student online distillation
"""
import os
import json
import glob
import datetime
from typing import Iterator, Tuple, Dict, Any, List
from collections import Counter


def _iter_event_files(events_dir: str, max_days: int = 30) -> List[str]:
    """최근 N일의 이벤트 파일들 반환 (YYYY-MM-DD.jsonl 형식)"""
    files = sorted(glob.glob(os.path.join(events_dir, "*.jsonl")))
    if not files:
        return []

    # 느슨하게 최근 N개 파일 사용
    return files[-max_days:]


def iter_training_samples(
    events_dir: str,
    agree_min_conf: float = 0.75,
    teacher_high_conf: float = 0.80,
    student_low_conf: float = 0.50,
) -> Iterator[Tuple[str, str, float]]:
    """
    훈련 샘플 이터레이터

    Returns:
        Iterator[Tuple[str, str, float]]: (text, label(intent), weight)

    증류 규칙:
    1. 동의 학습: teacher.intent == student.intent && teacher.conf >= agree_min_conf
    2. 보정 학습: teacher.conf >= teacher_high_conf && student.conf <= student_low_conf
    3. teacher 없음/파싱 실패 시 제외
    """
    files = _iter_event_files(events_dir)

    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        event = json.loads(line)

                        # Teacher 결과 확인
                        teacher = event.get("teacher_result") or event.get("teacher")
                        student = event.get("student_result", {}) or event.get(
                            "student", {}
                        )

                        if not teacher or "intent" not in teacher:
                            continue

                        # 텍스트 확인
                        text = event.get("text_redacted") or ""
                        if not text.strip():
                            continue

                        # 신뢰도 추출
                        teacher_conf = float(teacher.get("confidence", 0))
                        student_conf = float(student.get("confidence", 1))

                        # 동의 조건: Teacher-Student 일치 + Teacher 고신뢰도
                        teacher_intent = teacher.get("intent", "")
                        student_intent = student.get("intent", "")
                        agreement = (teacher_intent == student_intent) and (
                            teacher_conf >= agree_min_conf
                        )

                        # 보정 조건: Teacher 고신뢰도 + Student 저신뢰도
                        correction = (teacher_conf >= teacher_high_conf) and (
                            student_conf <= student_low_conf
                        )

                        if agreement or correction:
                            intent = teacher["intent"]

                            # 가중치 계산: 신뢰도 기반 + 보정 부스트
                            base_weight = max(0.1, min(1.0, teacher_conf))
                            boost_weight = 1.5 if correction else 1.0
                            final_weight = base_weight * boost_weight

                            yield (text, intent, float(final_weight))

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"⚠️ Error parsing line {line_num} in {file_path}: {e}")
                        continue

        except (OSError, IOError) as e:
            print(f"⚠️ Error reading file {file_path}: {e}")
            continue


def derive_label_space(events_dir: str, top_k: int = 64) -> List[str]:
    """이벤트 데이터에서 라벨 스페이스 유도"""
    counter = Counter()

    # 모든 훈련 샘플에서 라벨 집계
    for _, label, _ in iter_training_samples(events_dir):
        counter[label] += 1

    # 상위 K개 라벨
    labels = [label for label, count in counter.most_common(top_k)]

    # 보수적 기본 클래스 포함 (빠진 것들 추가)
    base_classes = [
        "general_chat",
        "web_query",
        "local_search",
        "medical_support",
        "math",
        "calc",
        "estimate",
        "file_read",
        "doc_summary",
        "sensitive_support",
        "creative_expression",
        "analytical_inquiry",
        "emotional_support",
        "collaborative_task",
        "technical_assistance",
        "math_calculation",
        "file_operation",
    ]

    for base_class in base_classes:
        if base_class not in labels:
            labels.append(base_class)

    return labels


def get_training_stats(events_dir: str) -> Dict[str, Any]:
    """훈련 데이터 통계"""
    stats = {
        "total_samples": 0,
        "label_distribution": Counter(),
        "weight_distribution": {"min": float("inf"), "max": 0, "avg": 0},
        "agreement_rate": 0,
        "correction_rate": 0,
    }

    total_weight = 0
    agreement_count = 0
    correction_count = 0

    for text, label, weight in iter_training_samples(events_dir):
        stats["total_samples"] += 1
        stats["label_distribution"][label] += 1

        total_weight += weight
        stats["weight_distribution"]["min"] = min(
            stats["weight_distribution"]["min"], weight
        )
        stats["weight_distribution"]["max"] = max(
            stats["weight_distribution"]["max"], weight
        )

        # 가중치로 타입 추정 (보정은 1.5 부스트)
        if weight > 1.2:  # 대략 보정 샘플
            correction_count += 1
        else:  # 동의 샘플
            agreement_count += 1

    if stats["total_samples"] > 0:
        stats["weight_distribution"]["avg"] = total_weight / stats["total_samples"]
        stats["agreement_rate"] = agreement_count / stats["total_samples"]
        stats["correction_rate"] = correction_count / stats["total_samples"]
    else:
        stats["weight_distribution"]["min"] = 0

    return stats


def validate_event_format(events_dir: str, sample_size: int = 10) -> Dict[str, Any]:
    """이벤트 파일 형식 검증"""
    files = _iter_event_files(events_dir)

    validation = {
        "valid_files": 0,
        "total_files": len(files),
        "sample_events": [],
        "errors": [],
        "required_fields": [
            "teacher_result",
            "student_result",
            "text_redacted",
            "timestamp",
        ],
        "missing_fields": Counter(),
    }

    sample_count = 0

    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line)

                        # 필수 필드 체크
                        for field in validation["required_fields"]:
                            if field not in event:
                                validation["missing_fields"][field] += 1

                        # 샘플 수집
                        if sample_count < sample_size:
                            validation["sample_events"].append(
                                {
                                    "file": os.path.basename(file_path),
                                    "has_teacher": bool(
                                        event.get("teacher_result")
                                        or event.get("teacher")
                                    ),
                                    "has_student": bool(
                                        event.get("student_result")
                                        or event.get("student")
                                    ),
                                    "has_text": bool(
                                        event.get("text_redacted", "").strip()
                                    ),
                                    "teacher_intent": (
                                        event.get("teacher_result", {}).get("intent")
                                        if event.get("teacher_result")
                                        else None
                                    ),
                                }
                            )
                            sample_count += 1

                    except json.JSONDecodeError as e:
                        validation["errors"].append(
                            f"JSON parse error in {file_path}: {e}"
                        )

            validation["valid_files"] += 1

        except (OSError, IOError) as e:
            validation["errors"].append(f"File read error {file_path}: {e}")

    return validation


# CLI 실행 지원
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m intent.datasets <events_dir> [command]")
        print("Commands: stats, validate, labels")
        sys.exit(1)

    events_dir = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "stats"

    if command == "stats":
        stats = get_training_stats(events_dir)
        print("📊 Training Data Statistics:")
        print(f"Total samples: {stats['total_samples']}")
        print(f"Agreement rate: {stats['agreement_rate']:.1%}")
        print(f"Correction rate: {stats['correction_rate']:.1%}")
        print("\n🏷️ Label distribution:")
        for label, count in stats["label_distribution"].most_common(10):
            print(f"  {label}: {count}")

    elif command == "validate":
        validation = validate_event_format(events_dir)
        print("🔍 Event Format Validation:")
        print(f"Valid files: {validation['valid_files']}/{validation['total_files']}")
        if validation["errors"]:
            print("❌ Errors:")
            for error in validation["errors"][:5]:
                print(f"  {error}")
        if validation["missing_fields"]:
            print("⚠️ Missing fields:")
            for field, count in validation["missing_fields"].most_common():
                print(f"  {field}: {count} times")

    elif command == "labels":
        labels = derive_label_space(events_dir)
        print("🏷️ Derived label space:")
        print(json.dumps(labels, indent=2))
