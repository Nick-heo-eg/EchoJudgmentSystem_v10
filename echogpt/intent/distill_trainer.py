#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Online Distillation Trainer
Teacher(GPT) → Student(Local) online learning system
"""
import os
import json
import joblib
import random
import warnings
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

# Scikit-learn imports (with fallback)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score, accuracy_score, classification_report
    from sklearn.exceptions import UndefinedMetricWarning

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ sklearn not available - DistillTrainer will be disabled")

# Local imports
from intent.datasets import iter_training_samples, derive_label_space

# Suppress sklearn warnings for partial_fit
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)


class DistillTrainer:
    """온라인 증류 트레이너 - Teacher(GPT)에서 Student(Local)로 지식 전이"""

    def __init__(self, cfg: Dict[str, Any], logger):
        self.cfg = cfg
        self.logger = logger

        # 경로 설정
        self.events_dir = cfg["storage"]["events_dir"]
        self.model_dir = cfg["storage"]["model_dir"]
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "student.joblib")

        # 증류 설정
        distill_cfg = cfg.get("distill", {})
        self.agree_min_conf = distill_cfg.get("agree_min_conf", 0.75)
        self.teacher_high_conf = distill_cfg.get("teacher_high_conf", 0.80)
        self.student_low_conf = distill_cfg.get("student_low_conf", 0.50)
        self.batch_size = distill_cfg.get("batch_size", 128)
        self.hot_swap_min_f1 = distill_cfg.get("hot_swap_min_f1", 0.85)
        self.max_days = distill_cfg.get("max_days", 30)

        # 라벨 스페이스 로드/유도
        self.labels = self._load_label_space()

        # 파이프라인
        self.pipe: Optional[Pipeline] = None

        self.logger.info(f"DistillTrainer initialized with {len(self.labels)} labels")

    def _load_label_space(self) -> List[str]:
        """라벨 스페이스 로드 (설정 파일 우선, 없으면 데이터 기반 유도)"""
        labels_path = os.path.join("config", "intent_labels.json")

        if os.path.exists(labels_path):
            try:
                with open(labels_path, encoding="utf-8") as f:
                    labels = json.load(f)
                    self.logger.info(f"Loaded {len(labels)} labels from config")
                    return labels
            except Exception as e:
                self.logger.warning(f"Failed to load labels config: {e}")

        # 데이터 기반 라벨 유도
        labels = derive_label_space(self.events_dir)
        self.logger.info(f"Derived {len(labels)} labels from data")
        return labels

    def _init_or_load_pipe(self):
        """기존 모델 로드 또는 새 파이프라인 초기화"""
        if self.pipe is None and os.path.exists(self.model_path):
            try:
                self.pipe = joblib.load(self.model_path)
                self.logger.info("Loaded existing student model")
                return
            except Exception as e:
                self.logger.warning(f"Failed to load existing model: {e}")
                self.pipe = None

        if self.pipe is None:
            # 새 파이프라인 생성
            vectorizer = TfidfVectorizer(
                analyzer="char",
                ngram_range=(2, 5),
                min_df=3,
                max_df=0.95,
                max_features=10000,
            )

            classifier = SGDClassifier(
                loss="log_loss", alpha=1e-5, max_iter=5, random_state=42
            )

            self.pipe = Pipeline([("tfidf", vectorizer), ("clf", classifier)])

            # partial_fit을 위한 클래스 설정 - 정렬된 라벨 사용
            sorted_labels = sorted(self.labels)
            self.pipe.named_steps["clf"].classes_ = sorted_labels
            self.logger.info("Created new student model pipeline")

    def _gather_training_data(self) -> Tuple[List[str], List[str], List[float]]:
        """훈련 데이터 수집"""
        X, y, weights = [], [], []
        sample_count = 0

        for text, label, weight in iter_training_samples(
            self.events_dir,
            agree_min_conf=self.agree_min_conf,
            teacher_high_conf=self.teacher_high_conf,
            student_low_conf=self.student_low_conf,
        ):
            X.append(text)
            y.append(label)
            weights.append(weight)
            sample_count += 1

            # 배치 사이즈 제한
            if self.batch_size and sample_count >= self.batch_size:
                break

        self.logger.info(f"Gathered {len(X)} training samples")
        return X, y, weights

    def train_once(self) -> Dict[str, Any]:
        """한 번의 훈련 실행"""
        try:
            self._init_or_load_pipe()
            X, y, weights = self._gather_training_data()

            if not X:
                return {
                    "trained": False,
                    "reason": "no_samples",
                    "message": "No training samples available",
                }

            # 홀드아웃 검증 (작게)
            X_train, X_test, y_train, y_test, w_train, w_test = (
                None,
                None,
                None,
                None,
                None,
                None,
            )

            try:
                if len(X) >= 10:  # 최소 검증 세트 크기
                    split_data = train_test_split(
                        X, y, weights, test_size=0.2, random_state=42, stratify=y
                    )
                    X_train, X_test, y_train, y_test, w_train, w_test = split_data
                else:
                    # 데이터가 적으면 전체를 훈련에 사용
                    X_train, y_train, w_train = X, y, weights
                    X_test, y_test = [], []

            except ValueError as e:
                # 라벨 다양성 부족 등으로 stratify 실패 시
                self.logger.warning(f"Stratified split failed: {e}, using random split")
                if len(X) >= 10:
                    split_data = train_test_split(
                        X, y, weights, test_size=0.2, random_state=42
                    )
                    X_train, X_test, y_train, y_test, w_train, w_test = split_data
                else:
                    X_train, y_train, w_train = X, y, weights
                    X_test, y_test = [], []

            # 훈련 실행
            tfidf = self.pipe.named_steps["tfidf"]
            clf = self.pipe.named_steps["clf"]

            # TF-IDF 벡터화 (fit_transform으로 벡터라이저 학습)
            X_train_vec = tfidf.fit_transform(X_train)

            # 분류기 partial_fit (온라인 학습) - 정렬된 클래스 사용
            sorted_labels = sorted(self.labels)
            import numpy as np

            w_train_array = np.array(w_train) if w_train else None
            clf.partial_fit(
                X_train_vec, y_train, classes=sorted_labels, sample_weight=w_train_array
            )

            # 평가
            f1_macro, accuracy = None, None
            if X_test and len(X_test) > 0 and y_test and len(y_test) > 0:
                X_test_vec = tfidf.transform(X_test)
                y_pred = clf.predict(X_test_vec)

                f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
                accuracy = accuracy_score(y_test, y_pred)

                self.logger.info(
                    f"Validation - F1: {f1_macro:.3f}, Accuracy: {accuracy:.3f}"
                )
            else:
                self.logger.info("No validation set - using all data for training")

            # 임시 모델 저장
            tmp_path = self.model_path + ".tmp"
            joblib.dump(self.pipe, tmp_path)

            # 핫스왑 결정
            should_swap = (f1_macro is None) or (f1_macro >= self.hot_swap_min_f1)

            if should_swap:
                os.replace(tmp_path, self.model_path)
                status = "hotswapped"
                self.logger.info(f"Model hotswapped - F1: {f1_macro or 'N/A'}")
            else:
                os.remove(tmp_path)
                status = "kept_old"
                self.logger.info(
                    f"Kept old model - F1 {f1_macro:.3f} < threshold {self.hot_swap_min_f1}"
                )

            # 라벨 분포 통계
            from collections import Counter

            label_dist = Counter(y_train)

            return {
                "trained": True,
                "samples": len(X),
                "labels": len(set(y_train)),
                "unique_labels": list(set(y_train)),
                "label_distribution": dict(label_dist),
                "f1_macro": f1_macro,
                "accuracy": accuracy,
                "status": status,
                "model_path": self.model_path,
                "hot_swap_threshold": self.hot_swap_min_f1,
            }

        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            return {"trained": False, "reason": "training_error", "error": str(e)}

    def evaluate_current_model(self, test_size: int = 100) -> Dict[str, Any]:
        """현재 모델 성능 평가"""
        if not os.path.exists(self.model_path):
            return {"error": "No trained model found"}

        try:
            # 모델 로드
            pipe = joblib.load(self.model_path)

            # 테스트 데이터 수집
            X_test, y_test, _ = [], [], []
            for text, label, weight in iter_training_samples(self.events_dir):
                X_test.append(text)
                y_test.append(label)
                if len(X_test) >= test_size:
                    break

            if not X_test:
                return {"error": "No test samples available"}

            # 예측
            y_pred = pipe.predict(X_test)

            # 메트릭 계산
            f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
            f1_micro = f1_score(y_test, y_pred, average="micro", zero_division=0)
            accuracy = accuracy_score(y_test, y_pred)

            # 분류 리포트
            report = classification_report(
                y_test, y_pred, output_dict=True, zero_division=0
            )

            return {
                "test_samples": len(X_test),
                "f1_macro": f1_macro,
                "f1_micro": f1_micro,
                "accuracy": accuracy,
                "classification_report": report,
            }

        except Exception as e:
            return {"error": f"Evaluation failed: {e}"}

    def get_training_info(self) -> Dict[str, Any]:
        """훈련 정보 조회"""
        info = {
            "model_exists": os.path.exists(self.model_path),
            "events_dir": self.events_dir,
            "model_path": self.model_path,
            "label_count": len(self.labels),
            "labels": self.labels,
            "config": {
                "agree_min_conf": self.agree_min_conf,
                "teacher_high_conf": self.teacher_high_conf,
                "student_low_conf": self.student_low_conf,
                "batch_size": self.batch_size,
                "hot_swap_min_f1": self.hot_swap_min_f1,
                "max_days": self.max_days,
            },
        }

        if info["model_exists"]:
            try:
                stat = os.stat(self.model_path)
                info["model_size_kb"] = stat.st_size // 1024
                info["model_modified"] = stat.st_mtime
            except:
                pass

        return info


# CLI 실행 지원
if __name__ == "__main__":
    import logging
    import yaml
    import sys

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger("echogpt.trainer")

    # 설정 로드
    try:
        with open("config/echogpt.yaml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # 트레이너 실행
    trainer = DistillTrainer(cfg, logger)

    # 명령어 처리
    command = sys.argv[1] if len(sys.argv) > 1 else "train"

    if command == "train":
        result = trainer.train_once()
        print("🎯 Training Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "info":
        info = trainer.get_training_info()
        print("ℹ️ Training Info:")
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif command == "eval":
        evaluation = trainer.evaluate_current_model()
        print("📊 Model Evaluation:")
        print(json.dumps(evaluation, indent=2, ensure_ascii=False))

    else:
        print("Usage: python -m intent.distill_trainer [train|info|eval]")
