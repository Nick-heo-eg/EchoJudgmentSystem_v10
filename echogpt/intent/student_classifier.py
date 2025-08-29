#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Student Classifier
Local intent classifier (Student in Teacher-Student architecture)
"""
import os
import threading
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import joblib

    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


class StudentClassifier:
    """로컬 Intent 분류기 (Student) - 핫스왑 지원"""

    def __init__(self, model_dir: str = "models/intent_student"):
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "student.joblib"
        self.pipe = None
        self._lock = threading.RLock()  # 핫스왑을 위한 스레드 세이프

        # 초기 모델 로드 시도
        self._load_model()

    def _load_model(self) -> bool:
        """모델 로드"""
        if not JOBLIB_AVAILABLE:
            # joblib이 없으면 모델 로딩 건너뛰기
            self.pipe = None
            return False

        try:
            if self.model_path.exists():
                with self._lock:
                    self.pipe = joblib.load(self.model_path)
                return True
        except Exception as e:
            print(f"⚠️ Failed to load student model: {e}")

        self.pipe = None
        return False

    def classify(self, text: str) -> Dict[str, Any]:
        """텍스트 분류"""
        with self._lock:
            if self.pipe is None:
                # 모델이 없으면 기본값 반환
                return {
                    "intent": "general_chat",
                    "confidence": 0.33,
                    "summary": "No trained model available",
                    "tags": [],
                    "safety": [],
                    "_source": "student",
                    "_model_available": False,
                }

            try:
                # 예측 실행
                predicted_label = self.pipe.predict([text])[0]

                # 신뢰도 계산 (predict_proba 사용 가능한 경우)
                confidence = self._calculate_confidence(text, predicted_label)

                return {
                    "intent": predicted_label,
                    "confidence": confidence,
                    "summary": f"Local classification: {predicted_label}",
                    "tags": self._extract_tags(text, predicted_label),
                    "safety": self._check_safety(predicted_label),
                    "_source": "student",
                    "_model_available": True,
                }

            except Exception as e:
                print(f"⚠️ Student classification failed: {e}")
                return {
                    "intent": "general_chat",
                    "confidence": 0.33,
                    "summary": f"Classification error: {str(e)[:50]}",
                    "tags": [],
                    "safety": [],
                    "_source": "student",
                    "_model_available": True,
                    "_error": str(e),
                }

    def _calculate_confidence(self, text: str, predicted_label: str) -> float:
        """신뢰도 계산"""
        try:
            if hasattr(self.pipe.named_steps.get("clf", None), "predict_proba"):
                # 확률 기반 신뢰도
                X_vec = self.pipe.named_steps["tfidf"].transform([text])
                probabilities = self.pipe.named_steps["clf"].predict_proba(X_vec)[0]
                max_prob = probabilities.max()
                return float(max_prob)
            else:
                # 결정 함수 기반 신뢰도 (SGD의 경우)
                if hasattr(self.pipe.named_steps.get("clf", None), "decision_function"):
                    X_vec = self.pipe.named_steps["tfidf"].transform([text])
                    decision_scores = self.pipe.named_steps["clf"].decision_function(
                        X_vec
                    )[0]

                    if len(decision_scores.shape) > 0 and decision_scores.shape[0] > 1:
                        # 다중 클래스: 최대 점수를 시그모이드로 변환
                        max_score = decision_scores.max()
                        confidence = 1 / (1 + abs(max_score) ** -1)
                    else:
                        # 이진 분류: 절댓값을 시그모이드로 변환
                        score = (
                            decision_scores
                            if hasattr(decision_scores, "__len__")
                            else decision_scores
                        )
                        confidence = 1 / (1 + abs(float(score)) ** -1)

                    return min(0.99, max(0.01, confidence))
        except Exception:
            pass

        # 폴백: 텍스트 길이와 키워드 기반 휴리스틱 신뢰도
        return self._heuristic_confidence(text, predicted_label)

    def _heuristic_confidence(self, text: str, predicted_label: str) -> float:
        """휴리스틱 신뢰도 계산"""
        base_confidence = 0.6

        # 텍스트 길이 기반 조정
        if len(text) < 10:
            base_confidence -= 0.2
        elif len(text) > 50:
            base_confidence += 0.1

        # 라벨별 키워드 매칭 기반 조정
        text_lower = text.lower()
        label_keywords = {
            "medical_support": ["의사", "병원", "아프", "증상", "치료"],
            "local_search": ["근처", "지도", "위치", "찾아", "어디"],
            "web_query": ["검색", "찾아", "알려", "정보"],
            "math": ["계산", "수학", "더하기", "빼기", "+", "-", "*", "/"],
            "technical_assistance": ["코딩", "프로그래밍", "코드", "함수", "버그"],
            "creative_expression": ["창의", "아이디어", "만들어", "디자인", "글"],
            "emotional_support": ["힘들어", "슬퍼", "위로", "도움", "기분"],
        }

        if predicted_label in label_keywords:
            keywords = label_keywords[predicted_label]
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                base_confidence += min(0.3, matches * 0.1)

        return min(0.95, max(0.1, base_confidence))

    def _extract_tags(self, text: str, predicted_label: str) -> list:
        """태그 추출"""
        tags = []
        text_lower = text.lower()

        # 라벨 기반 태그
        if predicted_label == "local_search":
            location_terms = ["동", "구", "시", "역", "병원", "학교", "카페"]
            for term in location_terms:
                if term in text_lower:
                    tags.append(f"location:{term}")

        elif predicted_label == "medical_support":
            medical_terms = ["소아과", "내과", "외과", "응급", "약국"]
            for term in medical_terms:
                if term in text_lower:
                    tags.append(f"medical:{term}")

        # 긴급도 태그
        urgency_keywords = ["급해", "빨리", "응급", "지금", "당장"]
        if any(keyword in text_lower for keyword in urgency_keywords):
            tags.append("urgency:high")

        return tags

    def _check_safety(self, predicted_label: str) -> list:
        """안전성 플래그 확인"""
        safety_flags = []

        # 라벨 기반 안전성 플래그
        if predicted_label == "medical_support":
            safety_flags.append("medical")
        elif predicted_label == "sensitive_support":
            safety_flags.append("sensitive")

        return safety_flags

    def reload(self) -> bool:
        """모델 핫스왑 (무중단 모델 교체)"""
        old_model_available = self.pipe is not None
        success = self._load_model()
        new_model_available = self.pipe is not None

        if success and new_model_available:
            if old_model_available:
                print("🔄 Student model hot-swapped successfully")
            else:
                print("✅ Student model loaded successfully")
            return True
        elif not success and old_model_available:
            print("⚠️ Hot-swap failed, keeping existing model")
            return False
        else:
            print("❌ No model available after reload attempt")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 조회"""
        with self._lock:
            info = {
                "model_available": self.pipe is not None,
                "model_path": str(self.model_path),
                "model_exists": self.model_path.exists(),
            }

            if info["model_exists"]:
                try:
                    stat = self.model_path.stat()
                    info["model_size_kb"] = stat.st_size // 1024
                    info["model_modified"] = stat.st_mtime
                except:
                    pass

            if self.pipe is not None:
                try:
                    # 파이프라인 정보
                    info["pipeline_steps"] = list(self.pipe.named_steps.keys())

                    # 클래스 정보
                    clf = self.pipe.named_steps.get("clf")
                    if clf and hasattr(clf, "classes_"):
                        info["classes"] = list(clf.classes_)
                        info["n_classes"] = len(clf.classes_)

                    # TF-IDF 정보
                    tfidf = self.pipe.named_steps.get("tfidf")
                    if tfidf and hasattr(tfidf, "vocabulary_"):
                        info["vocabulary_size"] = len(tfidf.vocabulary_)

                except Exception as e:
                    info["model_info_error"] = str(e)

            return info

    def is_available(self) -> bool:
        """모델 사용 가능 여부"""
        with self._lock:
            return self.pipe is not None


# 전역 인스턴스 (싱글톤 패턴)
_global_classifier = None
_global_lock = threading.Lock()


def get_global_classifier(
    model_dir: str = "models/intent_student",
) -> StudentClassifier:
    """전역 분류기 인스턴스 반환 (싱글톤)"""
    global _global_classifier

    with _global_lock:
        if _global_classifier is None:
            _global_classifier = StudentClassifier(model_dir)
        return _global_classifier


def reload_global_classifier() -> bool:
    """전역 분류기 리로드"""
    global _global_classifier

    with _global_lock:
        if _global_classifier is not None:
            return _global_classifier.reload()
        else:
            # 새로 생성
            _global_classifier = StudentClassifier()
            return _global_classifier.is_available()


# CLI 실행 지원
if __name__ == "__main__":
    import sys
    import json

    classifier = StudentClassifier()

    if len(sys.argv) < 2:
        print("Usage: python -m intent.student_classifier <command> [text]")
        print("Commands: info, classify, reload")
        sys.exit(1)

    command = sys.argv[1]

    if command == "info":
        info = classifier.get_model_info()
        print("🤖 Student Classifier Info:")
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif command == "classify" and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        result = classifier.classify(text)
        print("🎯 Classification Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "reload":
        success = classifier.reload()
        print(f"🔄 Reload {'successful' if success else 'failed'}")

    else:
        print("Invalid command or missing text argument")
