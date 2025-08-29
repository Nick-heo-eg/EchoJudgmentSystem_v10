#!/usr/bin/env python3
"""
📊 Signature Response Visualizer - YAML 템플릿 매트릭스 시각화 도구
감정 × 시그니처 템플릿 매트릭스를 직관적으로 시각화하고 분석

핵심 기능:
- 감정(Y축) × 시그니처(X축) 매트릭스 히트맵
- 응답 예시 및 통계 표시
- 색상 코딩: 응답 수, 공명도, 만족도
- Streamlit 기반 대시보드 지원
- 매트릭스 완성도 분석
- 개선 필요 영역 자동 식별
"""

import yaml
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import argparse
import warnings

warnings.filterwarnings("ignore")

# 의존성 가용성 확인
try:
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("⚠️ Streamlit이 설치되지 않음. 기본 시각화만 지원됩니다.")

# matplotlib 가용성 예외 처리 개선
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"⚠️ matplotlib/seaborn 누락됨: {e}")
    print("💡 해결방법: pip install matplotlib seaborn")

    # Mock 객체 생성
    class MockPlt:
        def __init__(self):
            pass

        def subplots(self, *args, **kwargs):
            raise ImportError(
                "matplotlib가 설치되지 않았습니다. pip install matplotlib seaborn을 실행하세요."
            )

        def __getattr__(self, name):
            raise ImportError(
                "matplotlib가 설치되지 않았습니다. pip install matplotlib seaborn을 실행하세요."
            )

    plt = MockPlt()
    sns = None

# 한글 폰트 설정 (matplotlib가 있을 때만)
if MATPLOTLIB_AVAILABLE:
    try:
        plt.rcParams["font.family"] = [
            "DejaVu Sans",
            "Malgun Gothic",
            "AppleGothic",
            "sans-serif",
        ]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception as e:
        print(f"⚠️ 폰트 설정 실패: {e}")
        pass


class SignatureResponseVisualizer:
    """시그니처 응답 매트릭스 시각화기"""

    def __init__(self, data_dir: str = "data", config_dir: str = "config"):
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)

        # 데이터 로딩
        self.template_matrix = self._load_template_matrix()
        self.feedback_data = self._load_feedback_data()
        self.signature_profiles = self._load_signature_profiles()

        # 매트릭스 분석
        self.matrix_analysis = self._analyze_matrix()

        print("📊 Signature Response Visualizer 초기화 완료")
        print(
            f"   📋 템플릿 매트릭스: {self.matrix_analysis['signatures']}개 시그니처 × {self.matrix_analysis['emotions']}개 감정"
        )
        print(f"   📈 피드백 데이터: {len(self.feedback_data)}개")
        print(f"   📊 완성도: {self.matrix_analysis['completion_rate']:.1%}")

    def generate_heatmap(
        self, metric: str = "response_count", save_path: str = None
    ) -> plt.Figure:
        """매트릭스 히트맵 생성"""
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib가 설치되지 않아 히트맵을 생성할 수 없습니다.")
            print("💡 해결방법: pip install matplotlib seaborn")
            return None

        print(f"🎨 히트맵 생성: {metric} 기준")

        # 매트릭스 데이터 생성
        matrix_data = self._create_matrix_data(metric)

        # 히트맵 생성
        fig, ax = plt.subplots(figsize=(12, 8))

        # 컬러맵 선택
        if metric == "satisfaction_score":
            cmap = "RdYlGn"
            vmin, vmax = 1.0, 5.0
        elif metric == "response_count":
            cmap = "YlOrRd"
            vmin, vmax = 0, matrix_data.values.max()
        else:
            cmap = "viridis"
            vmin, vmax = matrix_data.values.min(), matrix_data.values.max()

        # 히트맵 그리기
        sns.heatmap(
            matrix_data,
            annot=True,
            fmt=".1f" if metric == "satisfaction_score" else ".0f",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            ax=ax,
            cbar_kws={"label": self._get_metric_label(metric)},
            linewidths=0.5,
        )

        # 스타일링
        ax.set_title(
            f"Signature × Emotion Matrix ({self._get_metric_label(metric)})",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Signatures", fontsize=12, fontweight="bold")
        ax.set_ylabel("Emotions", fontsize=12, fontweight="bold")

        # 축 레이블 회전
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)

        # 레이아웃 조정
        plt.tight_layout()

        # 저장
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"💾 히트맵 저장: {save_path}")

        return fig

    def generate_completion_analysis(self, save_path: str = None) -> plt.Figure:
        """매트릭스 완성도 분석 차트"""
        print("📈 완성도 분석 차트 생성")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # 1. 시그니처별 완성도
        sig_completion = self._calculate_signature_completion()
        sig_completion.plot(kind="bar", ax=ax1, color="skyblue")
        ax1.set_title("Signature별 템플릿 완성도", fontweight="bold")
        ax1.set_ylabel("완성도 (%)")
        ax1.tick_params(axis="x", rotation=45)

        # 2. 감정별 커버리지
        emotion_coverage = self._calculate_emotion_coverage()
        emotion_coverage.plot(kind="bar", ax=ax2, color="lightcoral")
        ax2.set_title("Emotion별 시그니처 커버리지", fontweight="bold")
        ax2.set_ylabel("커버 시그니처 수")
        ax2.tick_params(axis="x", rotation=45)

        # 3. 응답 길이 분포
        response_lengths = self._analyze_response_lengths()
        ax3.hist(response_lengths, bins=20, color="lightgreen", alpha=0.7)
        ax3.set_title("응답 길이 분포", fontweight="bold")
        ax3.set_xlabel("응답 길이 (문자 수)")
        ax3.set_ylabel("빈도")

        # 4. 만족도 분포 (피드백 데이터가 있는 경우)
        if self.feedback_data:
            satisfaction_scores = [
                fb["satisfaction_score"]
                for fb in self.feedback_data
                if "satisfaction_score" in fb
            ]
            if satisfaction_scores:
                ax4.hist(satisfaction_scores, bins=10, color="gold", alpha=0.7)
                ax4.set_title("사용자 만족도 분포", fontweight="bold")
                ax4.set_xlabel("만족도 점수")
                ax4.set_ylabel("빈도")
                ax4.axvline(
                    np.mean(satisfaction_scores),
                    color="red",
                    linestyle="--",
                    label=f"평균: {np.mean(satisfaction_scores):.2f}",
                )
                ax4.legend()
            else:
                ax4.text(
                    0.5,
                    0.5,
                    "만족도 데이터 없음",
                    ha="center",
                    va="center",
                    transform=ax4.transAxes,
                    fontsize=12,
                )
                ax4.set_title("사용자 만족도 분포", fontweight="bold")
        else:
            ax4.text(
                0.5,
                0.5,
                "피드백 데이터 없음",
                ha="center",
                va="center",
                transform=ax4.transAxes,
                fontsize=12,
            )
            ax4.set_title("사용자 만족도 분포", fontweight="bold")

        plt.tight_layout()

        # 저장
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"💾 완성도 분석 차트 저장: {save_path}")

        return fig

    def generate_response_preview_table(self, max_chars: int = 50) -> pd.DataFrame:
        """응답 미리보기 테이블 생성"""
        print("📋 응답 미리보기 테이블 생성")

        preview_data = []

        for signature, sig_data in self.template_matrix.items():
            if isinstance(sig_data, dict):
                for emotion, emotion_data in sig_data.items():
                    if isinstance(emotion_data, dict) and "prompt" in emotion_data:
                        # 응답 텍스트 추출 및 단축
                        response_text = emotion_data["prompt"]
                        if len(response_text) > max_chars:
                            response_text = response_text[:max_chars] + "..."

                        # 만족도 정보 (피드백 데이터에서)
                        satisfaction = self._get_satisfaction_for_combination(
                            signature, emotion
                        )

                        preview_data.append(
                            {
                                "Signature": signature,
                                "Emotion": emotion,
                                "Response_Preview": response_text,
                                "Style": emotion_data.get("style", "N/A"),
                                "Satisfaction": (
                                    f"{satisfaction:.1f}" if satisfaction else "N/A"
                                ),
                                "Has_Fallback": (
                                    "Yes" if "fallback" in emotion_data else "No"
                                ),
                            }
                        )

        df = pd.DataFrame(preview_data)
        print(f"📊 생성된 미리보기: {len(df)}개 조합")

        return df

    def identify_improvement_areas(self) -> Dict[str, Any]:
        """개선 필요 영역 식별"""
        print("🔍 개선 필요 영역 분석")

        improvements = {
            "missing_combinations": [],
            "low_satisfaction_combinations": [],
            "short_responses": [],
            "missing_fallbacks": [],
            "underperforming_signatures": [],
            "underperforming_emotions": [],
        }

        # 1. 누락된 조합 식별
        all_signatures = list(self.template_matrix.keys())
        all_emotions = set()
        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                all_emotions.update(sig_data.keys())
        all_emotions = list(all_emotions)

        for signature in all_signatures:
            if isinstance(self.template_matrix[signature], dict):
                for emotion in all_emotions:
                    if emotion not in self.template_matrix[signature]:
                        improvements["missing_combinations"].append(
                            f"{signature} × {emotion}"
                        )

        # 2. 낮은 만족도 조합
        for signature, sig_data in self.template_matrix.items():
            if isinstance(sig_data, dict):
                for emotion in sig_data.keys():
                    satisfaction = self._get_satisfaction_for_combination(
                        signature, emotion
                    )
                    if satisfaction and satisfaction < 3.0:
                        improvements["low_satisfaction_combinations"].append(
                            f"{signature} × {emotion} (만족도: {satisfaction:.1f})"
                        )

        # 3. 짧은 응답 식별
        for signature, sig_data in self.template_matrix.items():
            if isinstance(sig_data, dict):
                for emotion, emotion_data in sig_data.items():
                    if isinstance(emotion_data, dict) and "prompt" in emotion_data:
                        response_length = len(emotion_data["prompt"])
                        if response_length < 30:  # 30자 미만
                            improvements["short_responses"].append(
                                f"{signature} × {emotion} ({response_length}자)"
                            )

        # 4. Fallback 누락 식별
        for signature, sig_data in self.template_matrix.items():
            if isinstance(sig_data, dict):
                for emotion, emotion_data in sig_data.items():
                    if (
                        isinstance(emotion_data, dict)
                        and "fallback" not in emotion_data
                    ):
                        improvements["missing_fallbacks"].append(
                            f"{signature} × {emotion}"
                        )

        # 5. 저성능 시그니처/감정
        if self.feedback_data:
            sig_performance = self._calculate_signature_performance()
            emotion_performance = self._calculate_emotion_performance()

            for sig, score in sig_performance.items():
                if score < 3.0:
                    improvements["underperforming_signatures"].append(
                        f"{sig} (평균: {score:.1f})"
                    )

            for emotion, score in emotion_performance.items():
                if score < 3.0:
                    improvements["underperforming_emotions"].append(
                        f"{emotion} (평균: {score:.1f})"
                    )

        print(f"🔍 개선 영역 식별 완료:")
        for category, items in improvements.items():
            if items:
                print(f"   {category}: {len(items)}개")

        return improvements

    def generate_streamlit_dashboard(self):
        """Streamlit 대시보드 생성"""
        if not STREAMLIT_AVAILABLE:
            print("❌ Streamlit이 설치되지 않아 대시보드를 생성할 수 없습니다.")
            return

        st.set_page_config(
            page_title="Echo Signature Response Matrix", page_icon="🎭", layout="wide"
        )

        st.title("🎭 Echo Signature Response Matrix Dashboard")
        st.markdown("감정 × 시그니처 템플릿 매트릭스 시각화 및 분석")

        # 사이드바
        st.sidebar.header("🔧 시각화 옵션")

        # 메트릭 선택
        metric_options = {
            "response_count": "응답 수",
            "satisfaction_score": "만족도 점수",
            "response_length": "응답 길이",
        }
        selected_metric = st.sidebar.selectbox(
            "시각화 메트릭 선택:",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
        )

        # 메인 대시보드
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 시그니처", self.matrix_analysis["signatures"])
        with col2:
            st.metric("총 감정", self.matrix_analysis["emotions"])
        with col3:
            st.metric("총 조합", self.matrix_analysis["total_combinations"])
        with col4:
            st.metric("완성도", f"{self.matrix_analysis['completion_rate']:.1%}")

        # 탭 구성
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 매트릭스 히트맵", "📈 완성도 분석", "📋 응답 미리보기", "🔍 개선 영역"]
        )

        with tab1:
            st.subheader("📊 시그니처 × 감정 매트릭스")

            # 히트맵 생성 및 표시
            fig = self.generate_heatmap(metric=selected_metric)
            st.pyplot(fig)

            # 매트릭스 데이터 테이블
            st.subheader("📊 매트릭스 데이터")
            matrix_data = self._create_matrix_data(selected_metric)
            st.dataframe(matrix_data.style.background_gradient(cmap="viridis"))

        with tab2:
            st.subheader("📈 매트릭스 완성도 분석")

            # 완성도 분석 차트
            fig = self.generate_completion_analysis()
            st.pyplot(fig)

            # 상세 통계
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("시그니처별 완성도")
                sig_completion = self._calculate_signature_completion()
                st.bar_chart(sig_completion)

            with col2:
                st.subheader("감정별 커버리지")
                emotion_coverage = self._calculate_emotion_coverage()
                st.bar_chart(emotion_coverage)

        with tab3:
            st.subheader("📋 응답 미리보기")

            # 필터 옵션
            col1, col2 = st.columns(2)
            with col1:
                signature_filter = st.selectbox(
                    "시그니처 필터:",
                    options=["전체"] + list(self.template_matrix.keys()),
                )
            with col2:
                emotion_filter = st.selectbox(
                    "감정 필터:",
                    options=["전체"]
                    + list(
                        set(
                            emotion
                            for sig_data in self.template_matrix.values()
                            if isinstance(sig_data, dict)
                            for emotion in sig_data.keys()
                        )
                    ),
                )

            # 미리보기 테이블
            preview_df = self.generate_response_preview_table()

            # 필터 적용
            if signature_filter != "전체":
                preview_df = preview_df[preview_df["Signature"] == signature_filter]
            if emotion_filter != "전체":
                preview_df = preview_df[preview_df["Emotion"] == emotion_filter]

            st.dataframe(preview_df, use_container_width=True)

        with tab4:
            st.subheader("🔍 개선 필요 영역")

            improvements = self.identify_improvement_areas()

            for category, items in improvements.items():
                if items:
                    st.subheader(f"📌 {category.replace('_', ' ').title()}")
                    for item in items[:10]:  # 최대 10개만 표시
                        st.write(f"• {item}")
                    if len(items) > 10:
                        st.write(f"... 외 {len(items) - 10}개 더")

        # 푸터
        st.markdown("---")
        st.markdown("🎭 Echo Signature Response Matrix Dashboard v2.0")
        st.markdown(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _load_template_matrix(self) -> Dict[str, Any]:
        """템플릿 매트릭스 로딩"""
        try:
            template_path = self.data_dir / "signature_response_templates.yaml"
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 템플릿 매트릭스 로딩 실패: {e}")

        return {}

    def _load_feedback_data(self) -> List[Dict[str, Any]]:
        """피드백 데이터 로딩"""
        feedback_data = []

        try:
            feedback_path = self.data_dir / "meta_logs" / "feedback_logs.jsonl"
            if feedback_path.exists():
                with open(feedback_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            feedback_data.append(json.loads(line))
        except Exception as e:
            print(f"⚠️ 피드백 데이터 로딩 실패: {e}")

        return feedback_data

    def _load_signature_profiles(self) -> Dict[str, Any]:
        """시그니처 프로필 로딩"""
        return {
            "Selene": {"name": "달빛 같은 치유자", "color": "#87CEEB"},
            "Lune": {"name": "신비로운 달의 수호자", "color": "#B0C4DE"},
            "Aurora": {"name": "창조적 영감자", "color": "#FFB6C1"},
            "Echo-Aurora": {"name": "공감적 양육자", "color": "#98FB98"},
            "Echo-Phoenix": {"name": "변화 추진자", "color": "#FFA500"},
            "Echo-Sage": {"name": "지혜로운 분석가", "color": "#DDA0DD"},
            "Echo-Companion": {"name": "신뢰할 수 있는 동반자", "color": "#F0E68C"},
            "Grumbly": {"name": "까칠한 현실주의자", "color": "#CD853F"},
        }

    def _analyze_matrix(self) -> Dict[str, Any]:
        """매트릭스 분석"""
        signatures = len(
            [k for k, v in self.template_matrix.items() if isinstance(v, dict)]
        )

        all_emotions = set()
        total_combinations = 0

        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                all_emotions.update(sig_data.keys())
                total_combinations += len(sig_data)

        emotions = len(all_emotions)
        max_possible_combinations = signatures * emotions
        completion_rate = (
            total_combinations / max_possible_combinations
            if max_possible_combinations > 0
            else 0
        )

        return {
            "signatures": signatures,
            "emotions": emotions,
            "total_combinations": total_combinations,
            "max_possible_combinations": max_possible_combinations,
            "completion_rate": completion_rate,
        }

    def _create_matrix_data(self, metric: str) -> pd.DataFrame:
        """매트릭스 데이터 생성"""
        # 모든 시그니처와 감정 추출
        signatures = [k for k, v in self.template_matrix.items() if isinstance(v, dict)]
        all_emotions = set()
        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                all_emotions.update(sig_data.keys())
        emotions = sorted(list(all_emotions))

        # 매트릭스 초기화
        matrix = np.zeros((len(emotions), len(signatures)))

        for i, emotion in enumerate(emotions):
            for j, signature in enumerate(signatures):
                if signature in self.template_matrix and isinstance(
                    self.template_matrix[signature], dict
                ):
                    if emotion in self.template_matrix[signature]:
                        if metric == "response_count":
                            matrix[i, j] = 1  # 응답이 있으면 1
                        elif metric == "satisfaction_score":
                            satisfaction = self._get_satisfaction_for_combination(
                                signature, emotion
                            )
                            matrix[i, j] = satisfaction if satisfaction else 0
                        elif metric == "response_length":
                            emotion_data = self.template_matrix[signature][emotion]
                            if (
                                isinstance(emotion_data, dict)
                                and "prompt" in emotion_data
                            ):
                                matrix[i, j] = len(emotion_data["prompt"])

        return pd.DataFrame(matrix, index=emotions, columns=signatures)

    def _get_metric_label(self, metric: str) -> str:
        """메트릭 라벨 반환"""
        labels = {
            "response_count": "응답 수",
            "satisfaction_score": "만족도 점수",
            "response_length": "응답 길이 (문자)",
        }
        return labels.get(metric, metric)

    def _calculate_signature_completion(self) -> pd.Series:
        """시그니처별 완성도 계산"""
        all_emotions = set()
        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                all_emotions.update(sig_data.keys())
        total_emotions = len(all_emotions)

        completion_data = {}
        for signature, sig_data in self.template_matrix.items():
            if isinstance(sig_data, dict):
                completed_emotions = len(sig_data)
                completion_rate = (completed_emotions / total_emotions) * 100
                completion_data[signature] = completion_rate

        return pd.Series(completion_data)

    def _calculate_emotion_coverage(self) -> pd.Series:
        """감정별 커버리지 계산"""
        coverage_data = {}

        # 모든 감정 추출
        all_emotions = set()
        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                all_emotions.update(sig_data.keys())

        # 각 감정별로 커버하는 시그니처 수 계산
        for emotion in all_emotions:
            coverage_count = 0
            for signature, sig_data in self.template_matrix.items():
                if isinstance(sig_data, dict) and emotion in sig_data:
                    coverage_count += 1
            coverage_data[emotion] = coverage_count

        return pd.Series(coverage_data)

    def _analyze_response_lengths(self) -> List[int]:
        """응답 길이 분석"""
        lengths = []

        for sig_data in self.template_matrix.values():
            if isinstance(sig_data, dict):
                for emotion_data in sig_data.values():
                    if isinstance(emotion_data, dict) and "prompt" in emotion_data:
                        lengths.append(len(emotion_data["prompt"]))

        return lengths

    def _get_satisfaction_for_combination(
        self, signature: str, emotion: str
    ) -> Optional[float]:
        """특정 조합의 만족도 조회"""
        if not self.feedback_data:
            return None

        relevant_feedback = [
            fb
            for fb in self.feedback_data
            if fb.get("signature") == signature and fb.get("emotion") == emotion
        ]

        if relevant_feedback:
            scores = [
                fb["satisfaction_score"]
                for fb in relevant_feedback
                if "satisfaction_score" in fb
            ]
            return np.mean(scores) if scores else None

        return None

    def _calculate_signature_performance(self) -> Dict[str, float]:
        """시그니처별 성능 계산"""
        performance = {}

        for feedback in self.feedback_data:
            signature = feedback.get("signature")
            score = feedback.get("satisfaction_score")

            if signature and score:
                if signature not in performance:
                    performance[signature] = []
                performance[signature].append(score)

        # 평균 계산
        for signature in performance:
            performance[signature] = np.mean(performance[signature])

        return performance

    def _calculate_emotion_performance(self) -> Dict[str, float]:
        """감정별 성능 계산"""
        performance = {}

        for feedback in self.feedback_data:
            emotion = feedback.get("emotion")
            score = feedback.get("satisfaction_score")

            if emotion and score:
                if emotion not in performance:
                    performance[emotion] = []
                performance[emotion].append(score)

        # 평균 계산
        for emotion in performance:
            performance[emotion] = np.mean(performance[emotion])

        return performance


def main():
    """CLI 인터페이스"""
    parser = argparse.ArgumentParser(description="Signature Response Matrix Visualizer")
    parser.add_argument(
        "--mode", choices=["static", "streamlit"], default="static", help="시각화 모드"
    )
    parser.add_argument(
        "--metric",
        choices=["response_count", "satisfaction_score", "response_length"],
        default="response_count",
        help="시각화 메트릭",
    )
    parser.add_argument("--output", type=str, help="출력 파일 경로")
    parser.add_argument("--analysis", action="store_true", help="개선 영역 분석 실행")

    args = parser.parse_args()

    print("📊 Signature Response Visualizer")
    print("=" * 50)

    visualizer = SignatureResponseVisualizer()

    if args.mode == "streamlit":
        if STREAMLIT_AVAILABLE:
            print("🌐 Streamlit 대시보드 실행 중...")
            visualizer.generate_streamlit_dashboard()
        else:
            print("❌ Streamlit이 설치되지 않음")
    else:
        print(f"🎨 정적 시각화 생성: {args.metric}")

        # 히트맵 생성
        output_path = args.output or f"signature_matrix_{args.metric}.png"
        fig = visualizer.generate_heatmap(metric=args.metric, save_path=output_path)

        # 완성도 분석
        completion_path = output_path.replace(".png", "_completion.png")
        completion_fig = visualizer.generate_completion_analysis(
            save_path=completion_path
        )

        # 미리보기 테이블
        preview_df = visualizer.generate_response_preview_table()
        csv_path = output_path.replace(".png", "_preview.csv")
        preview_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"📋 미리보기 테이블 저장: {csv_path}")

        # 개선 영역 분석
        if args.analysis:
            improvements = visualizer.identify_improvement_areas()
            analysis_path = output_path.replace(".png", "_analysis.json")
            with open(analysis_path, "w", encoding="utf-8") as f:
                json.dump(improvements, f, ensure_ascii=False, indent=2)
            print(f"🔍 개선 영역 분석 저장: {analysis_path}")

        print("✅ 시각화 완료!")


if __name__ == "__main__":
    main()
