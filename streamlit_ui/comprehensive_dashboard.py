# streamlit_ui/comprehensive_dashboard.py

# @owner: nick
# @expose
# @maturity: stable

"""
🌐 EchoJudgment v10 Comprehensive Dashboard
- 정책 시뮬레이션, 적응 학습, 성능 리포트를 통합한 종합 대시보드
- 실시간 시그니처 성능 모니터링 및 제어
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import yaml
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Add echo_engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from echo_engine.policy_simulator import PolicySimulator, get_available_scenarios
from echo_engine.adaptive_learning_engine import (
    AdaptiveLearningEngine,
    run_adaptive_learning,
)
from echo_engine.signature_performance_reporter import (
    SignaturePerformanceReporter,
    generate_signature_report,
)
from echo_engine.seed_kernel import get_echo_seed_kernel
from echo_engine.loop_meta_integrator import get_system_performance
from echo_engine.signature_loop_bridge import analyze_signature_loop_compatibility

# Meta-Liminal System 통합
try:
    from echo_engine.liminal_bridge import get_liminal_bridge
    from echo_engine.meta_logger import get_meta_logger

    META_LIMINAL_AVAILABLE = True
except ImportError as e:
    META_LIMINAL_AVAILABLE = False
    print(f"⚠️ Meta-Liminal 시스템 연동 실패: {e}")

# EchoGPT 시스템 통합
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from echogpt import EchoGPT, EchoGPTMessage
    from echo_engine.pipelines.gpt_intent_client import GPTIntentClient, IntentType

    ECHOGPT_AVAILABLE = True
except ImportError as e:
    ECHOGPT_AVAILABLE = False
    print(f"⚠️ EchoGPT 시스템 연동 실패: {e}")


class ComprehensiveDashboard:
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.api_base_url = "http://localhost:9000"
        self.load_system_components()
        # EchoGPT API URL with environment variable support for containerized deployment
        import os

        self.echogpt_api_url = os.getenv("ECHOGPT_API_URL", "http://localhost:9001")

    def setup_page_config(self):
        """페이지 설정"""
        st.set_page_config(
            page_title="EchoJudgment v10 종합 대시보드",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def initialize_session_state(self):
        """세션 상태 초기화"""
        if "kernel" not in st.session_state:
            st.session_state.kernel = get_echo_seed_kernel("dashboard")

        if "simulation_history" not in st.session_state:
            st.session_state.simulation_history = []

        if "learning_results" not in st.session_state:
            st.session_state.learning_results = []

        if "last_report" not in st.session_state:
            st.session_state.last_report = None

        if "auto_learning_enabled" not in st.session_state:
            st.session_state.auto_learning_enabled = False

    def load_system_components(self):
        """시스템 컴포넌트 로드"""
        try:
            self.policy_simulator = PolicySimulator()
            self.performance_reporter = SignaturePerformanceReporter()
            self.adaptive_learning = AdaptiveLearningEngine(st.session_state.kernel)
            self.api_connected = self.check_api_connection()
        except Exception as e:
            st.session_state.local_fallback = True
            self.api_connected = False

    def check_api_connection(self):
        """API 서버 연결 확인"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def call_api(self, endpoint, method="GET", data=None):
        """API 호출 헬퍼"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API 호출 실패: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"API 연결 오류: {e}")
            return None

    def run(self):
        """메인 대시보드 실행"""

        # 헤더
        st.title("🧠 EchoJudgment v10 종합 대시보드")
        st.markdown("**AI 존재형⨯판단형 시스템 통합 제어센터**")

        # 사이드바
        self.render_sidebar()

        # 메인 탭
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
            [
                "🤖 EchoGPT",
                "🌐 API 테스트",
                "🏛️ 정책 시뮬레이션",
                "🧬 적응 학습",
                "📊 성능 리포트",
                "🔄 루프 모니터링",
                "🎯 시그니처 분석",
                "🌀 Meta-Liminal",
                "⚙️ 시스템 제어",
            ]
        )

        with tab1:
            self.render_echogpt()

        with tab2:
            self.render_api_test()

        with tab3:
            self.render_policy_simulation()

        with tab4:
            self.render_adaptive_learning()

        with tab5:
            self.render_performance_report()

        with tab6:
            self.render_loop_monitoring()

        with tab7:
            self.render_signature_analysis()

        with tab8:
            self.render_meta_liminal_status()

        with tab9:
            self.render_system_control()

    def render_sidebar(self):
        """사이드바 렌더링"""
        st.sidebar.header("🎛️ 시스템 제어")

        # API 연결 상태
        st.sidebar.subheader("🌐 API 연결 상태")
        if self.api_connected:
            st.sidebar.success("✅ API 서버 연결됨")
        else:
            st.sidebar.error("❌ API 서버 연결 안됨")
            if st.sidebar.button("🔄 API 연결 재시도"):
                self.api_connected = self.check_api_connection()
                st.rerun()

        # 시스템 상태
        st.sidebar.subheader("📊 시스템 상태")

        # 커널 상태
        seed_count = len(st.session_state.kernel.seed_registry)
        evolution_count = len(st.session_state.kernel.evolution_history)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("활성 시드", seed_count)
        with col2:
            st.metric("진화 횟수", evolution_count)

        # 자동 학습 설정
        st.sidebar.subheader("🧬 자동 학습")
        auto_learning = st.sidebar.toggle(
            "자동 적응 학습 활성화",
            value=st.session_state.auto_learning_enabled,
            help="시스템이 자동으로 실패 패턴을 학습하고 개선합니다",
        )
        st.session_state.auto_learning_enabled = auto_learning

        if auto_learning:
            learning_interval = st.sidebar.slider(
                "학습 주기 (분)", min_value=5, max_value=60, value=15
            )

            if st.sidebar.button("🔄 즉시 학습 실행"):
                with st.spinner("적응 학습 실행 중..."):
                    result = self.adaptive_learning.run_continuous_learning_cycle()
                    st.session_state.learning_results.append(result)
                    st.sidebar.success("학습 완료!")

        # 빠른 액션
        st.sidebar.subheader("⚡ 빠른 액션")

        if st.sidebar.button("📈 성능 리포트 생성"):
            with st.spinner("성능 리포트 생성 중..."):
                report = generate_signature_report()
                st.session_state.last_report = report
                st.sidebar.success("리포트 생성 완료!")

        if st.sidebar.button("🌱 새 시드 생성"):
            signature_id = st.sidebar.selectbox(
                "시그니처 선택",
                ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
                key="sidebar_signature",
            )
            new_seed = st.session_state.kernel.generate_initial_state(
                signature_id=signature_id
            )
            st.sidebar.success(f"시드 생성: {new_seed.identity_trace.seed_id}")

        # 데이터 관리
        st.sidebar.subheader("💾 데이터 관리")

        if st.sidebar.button("🗑️ 이력 초기화"):
            st.session_state.simulation_history = []
            st.session_state.learning_results = []
            st.sidebar.success("이력 초기화 완료!")

        # 시스템 정보
        st.sidebar.subheader("ℹ️ 시스템 정보")
        st.sidebar.info(
            f"**EchoJudgment v10**\n\n현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def render_api_test(self):
        """API 테스트 탭"""
        st.header("🌐 API 연결 및 테스트")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🔗 연결 상태")

            # API 서버 상태 확인
            if st.button("🔄 API 서버 상태 확인"):
                with st.spinner("API 서버 확인 중..."):
                    api_status = self.call_api("/health")
                    if api_status:
                        st.success("✅ API 서버 연결 성공!")
                        st.json(api_status)
                    else:
                        st.error("❌ API 서버 연결 실패")

            # 기본 정보 조회
            if st.button("📊 시스템 메트릭 조회"):
                with st.spinner("메트릭 조회 중..."):
                    metrics = self.call_api("/metrics")
                    if metrics:
                        st.subheader("시스템 메트릭")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("요청 수", metrics.get("request_count", 0))
                        with col2:
                            st.metric("활성 시드", metrics.get("active_seeds", 0))
                        with col3:
                            st.metric("총 진화", metrics.get("total_evolutions", 0))

                        # 분포 차트
                        if metrics.get("signature_distribution"):
                            fig = px.pie(
                                values=list(metrics["signature_distribution"].values()),
                                names=list(metrics["signature_distribution"].keys()),
                                title="시그니처 분포",
                            )
                            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🧪 판단 테스트")

            # 고급 판단 모드 토글
            advanced_mode = st.toggle(
                "🔬 고급 판단 모드",
                value=False,
                help="자동 시그니처 선택, 다중 LLM 융합, LLM 라우팅 기능 활성화",
            )

            if advanced_mode:
                st.info("🎯 고급 모드: 자동 시그니처 선택 및 융합 판단 활성화")

            # 판단 요청 테스트
            test_text = st.text_area(
                "테스트할 텍스트 입력",
                value=(
                    "새로운 AI 프로젝트를 기획하고 있습니다. 창의적이면서도 실용적인 접근 방안을 제시해주세요."
                    if advanced_mode
                    else "오늘은 좋은 날씨입니다. 어떤 활동을 추천하시나요?"
                ),
                height=100,
            )

            if not advanced_mode:
                # 기본 모드 - 기존 인터페이스
                signature_choice = st.selectbox(
                    "시그니처 선택",
                    ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
                )

                judgment_type = st.selectbox(
                    "판단 유형", ["quick", "comprehensive", "detailed"]
                )
            else:
                # 고급 모드 - 새로운 기능들
                col_auto, col_manual = st.columns(2)

                with col_auto:
                    auto_signature = st.checkbox(
                        "🤖 자동 시그니처 선택",
                        value=True,
                        help="컨텍스트 기반으로 최적 시그니처 자동 선택",
                    )

                with col_manual:
                    signature_choice = st.selectbox(
                        "수동 시그니처 선택",
                        ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
                        disabled=auto_signature,
                    )

                # 고급 판단 옵션
                col_priority, col_strategy = st.columns(2)

                with col_priority:
                    priority = st.selectbox(
                        "우선순위",
                        ["normal", "high", "urgent", "low"],
                        help="판단 처리 우선순위",
                    )

                with col_strategy:
                    fusion_strategy = st.selectbox(
                        "융합 전략",
                        ["weighted_average", "consensus", "best_confidence"],
                        help="다중 LLM 융합 방식",
                    )

                # LLM 제공자 선택
                providers = st.multiselect(
                    "LLM 제공자",
                    ["claude", "gpt", "mistral", "perplexity"],
                    default=["claude", "mistral"],
                    help="사용할 LLM 제공자들",
                )

                # 컨텍스트 정보
                with st.expander("🔍 추가 컨텍스트 (선택사항)"):
                    domain = st.selectbox(
                        "도메인",
                        ["general", "technical", "creative", "business", "scientific"],
                    )
                    mood = st.selectbox(
                        "무드", ["neutral", "excited", "calm", "urgent", "thoughtful"]
                    )
                    context_text = st.text_area(
                        "추가 컨텍스트", placeholder="프로젝트 배경, 제약사항 등..."
                    )

            if st.button("🚀 판단 요청", type="primary"):
                if test_text:
                    with st.spinner("판단 처리 중..."):
                        if not advanced_mode:
                            # 기본 모드 - 기존 API
                            judgment_data = {
                                "text": test_text,
                                "signature_id": signature_choice,
                                "judgment_type": judgment_type,
                                "include_emotion": True,
                                "include_strategy": True,
                            }
                            result = self.call_api(
                                "/judge", method="POST", data=judgment_data
                            )
                        else:
                            # 고급 모드 - 새로운 advanced-judgment API
                            judgment_data = {
                                "text": test_text,
                                "signature": (
                                    None if auto_signature else signature_choice
                                ),
                                "auto_signature": auto_signature,
                                "priority": priority,
                                "strategy": fusion_strategy,
                                "providers": providers if providers else ["mistral"],
                                "context": (
                                    {
                                        "domain": domain,
                                        "mood": mood,
                                        "additional_context": context_text,
                                    }
                                    if "domain" in locals()
                                    else {}
                                ),
                            }
                            result = self.call_api(
                                "/advanced-judgment", method="POST", data=judgment_data
                            )

                        if result:
                            st.success("✅ 판단 완료!")

                            if not advanced_mode:
                                # 기본 모드 결과 표시
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(
                                        "신뢰도", f"{result.get('confidence', 0):.2f}"
                                    )
                                with col2:
                                    st.metric(
                                        "처리 시간",
                                        f"{result.get('processing_time', 0):.2f}s",
                                    )
                                with col3:
                                    st.metric("감정", result.get("emotion", "Unknown"))

                                st.subheader("🎯 판단 결과")
                                st.write(result.get("judgment", ""))

                                st.subheader("🧠 추론 과정")
                                st.write(result.get("reasoning", ""))

                                if result.get("alternatives"):
                                    st.subheader("🔀 대안들")
                                    for i, alt in enumerate(result["alternatives"], 1):
                                        st.write(f"{i}. {alt}")
                            else:
                                # 고급 모드 결과 표시
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric(
                                        "신뢰도",
                                        f"{result.get('confidence_score', 0):.2f}",
                                    )
                                with col2:
                                    st.metric(
                                        "실행 시간",
                                        f"{result.get('execution_time', 0):.2f}s",
                                    )
                                with col3:
                                    st.metric(
                                        "선택된 시그니처",
                                        result.get("selected_signature", "Unknown"),
                                    )
                                with col4:
                                    providers_used = result.get("providers_used", [])
                                    st.metric("사용된 LLM", f"{len(providers_used)}개")

                                # 고급 결과 정보
                                if result.get("selected_signature"):
                                    st.info(
                                        f"🎯 자동 선택된 시그니처: **{result['selected_signature']}**"
                                    )

                                if result.get("providers_used"):
                                    st.info(
                                        f"🤖 사용된 LLM 제공자: {', '.join(result['providers_used'])}"
                                    )

                                # 판단 결과
                                st.subheader("🎯 융합 판단 결과")
                                judgment_result = result.get("judgment_result", {})
                                if isinstance(judgment_result, dict):
                                    st.json(judgment_result)
                                else:
                                    st.write(judgment_result)

                                # 처리 정보
                                processing_info = result.get("processing_info", {})
                                if processing_info:
                                    with st.expander("🔍 처리 정보"):
                                        st.json(processing_info)
                else:
                    st.warning("테스트할 텍스트를 입력해주세요.")

        # Echo API 테스트
        st.subheader("🌟 Echo 핵심 API 테스트")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🌱 시드 생성 테스트"):
                with st.spinner("시드 생성 중..."):
                    seed_data = {
                        "content": "테스트 시드 생성을 위한 샘플 내용입니다.",
                        "signature": signature_choice,
                        "world_context": "API 테스트 환경",
                    }

                    result = self.call_api(
                        "/seed/create", method="POST", data=seed_data
                    )
                    if result:
                        st.success("시드 생성 성공!")
                        st.json(result)

        with col2:
            if st.button("⚖️ YURI 윤리 검증"):
                with st.spinner("윤리 검증 중..."):
                    yuri_data = {
                        "seed_id": "test_seed_001",
                        "content": "AI가 인간의 결정을 도와주는 상황에서의 윤리적 고려사항",
                    }

                    result = self.call_api(
                        "/yuri/check_seed", method="POST", data=yuri_data
                    )
                    if result:
                        st.success("윤리 검증 완료!")
                        if result.get("yuri_check", {}).get("is_ethical"):
                            st.success("✅ 윤리적으로 적합")
                        else:
                            st.warning("⚠️ 윤리적 검토 필요")
                        st.json(result)

        with col3:
            if st.button("🎵 공명 평가 테스트"):
                with st.spinner("공명 평가 중..."):
                    resonance_data = {
                        "response_text": f"{signature_choice}가 따뜻하고 공감적인 방식으로 응답합니다.",
                        "signature_id": signature_choice,
                    }

                    result = self.call_api(
                        "/resonance/evaluate", method="POST", data=resonance_data
                    )
                    if result:
                        st.success("공명 평가 완료!")
                        score = result.get("resonance_evaluation", {}).get(
                            "overall_score", 0
                        )
                        if score > 0.7:
                            st.success(f"🎉 높은 공명도: {score:.2f}")
                        else:
                            st.info(f"📊 공명도: {score:.2f}")
                        st.json(result)

    def render_policy_simulation(self):
        """정책 시뮬레이션 탭"""
        st.header("🏛️ 정책 시뮬레이션")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("시뮬레이션 설정")

            # 시나리오 선택
            available_scenarios = get_available_scenarios()
            scenario_id = st.selectbox(
                "정책 시나리오",
                available_scenarios,
                format_func=lambda x: {
                    "elderly_care": "🏥 고령자 디지털 돌봄",
                    "climate_adaptation": "🌍 기후변화 적응 스마트시티",
                    "future_work": "💼 AI 시대 일자리 전환",
                    "education_equity": "📚 AI 맞춤형 교육 평등",
                }.get(x, x),
            )

            # 시그니처 선택
            signature_options = ["모든 시그니처 비교"] + [
                "Echo-Aurora",
                "Echo-Phoenix",
                "Echo-Sage",
                "Echo-Companion",
            ]
            signature_selection = st.selectbox("시그니처 선택", signature_options)

            # 실행 버튼
            if st.button("🚀 시뮬레이션 실행", type="primary"):
                with st.spinner("정책 시뮬레이션 실행 중..."):
                    if signature_selection == "모든 시그니처 비교":
                        # 모든 시그니처 비교
                        comparison_result = (
                            self.policy_simulator.compare_signature_approaches(
                                scenario_id
                            )
                        )
                        st.session_state.simulation_history.append(
                            {
                                "type": "comparison",
                                "scenario_id": scenario_id,
                                "result": comparison_result,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        st.success("시그니처 비교 완료!")
                    else:
                        # 단일 시그니처 시뮬레이션
                        judgment = self.policy_simulator.simulate_policy_judgment(
                            scenario_id, signature_selection
                        )
                        st.session_state.simulation_history.append(
                            {
                                "type": "single",
                                "scenario_id": scenario_id,
                                "signature_id": signature_selection,
                                "result": judgment,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        st.success("정책 시뮬레이션 완료!")

        with col2:
            st.subheader("시뮬레이션 결과")

            if st.session_state.simulation_history:
                latest_result = st.session_state.simulation_history[-1]

                if latest_result["type"] == "comparison":
                    self._display_comparison_result(latest_result["result"])
                else:
                    self._display_single_judgment_result(latest_result["result"])
            else:
                st.info("시뮬레이션을 실행하여 결과를 확인하세요.")

        # 시뮬레이션 히스토리
        if st.session_state.simulation_history:
            st.subheader("📊 시뮬레이션 히스토리")
            self._display_simulation_history()

    def _display_comparison_result(self, result: Dict):
        """시그니처 비교 결과 표시"""
        st.success("🔍 시그니처별 접근법 비교")

        # 메트릭 요약
        comparisons = result["signature_comparisons"]

        col1, col2, col3 = st.columns(3)

        with col1:
            best_confidence = max(comparisons, key=lambda x: x["confidence"])
            st.metric(
                "최고 신뢰도",
                f"{best_confidence['confidence']:.2f}",
                delta=best_confidence["signature_id"],
            )

        with col2:
            best_ethical = max(comparisons, key=lambda x: x["ethical_impact"])
            st.metric(
                "최고 윤리 영향",
                f"{best_ethical['ethical_impact']:.2f}",
                delta=best_ethical["signature_id"],
            )

        with col3:
            avg_confidence = sum(c["confidence"] for c in comparisons) / len(
                comparisons
            )
            st.metric("평균 신뢰도", f"{avg_confidence:.2f}")

        # 상세 비교 테이블
        comparison_data = []
        for comp in comparisons:
            comparison_data.append(
                {
                    "시그니처": comp["signature_id"],
                    "접근법": comp["approach_summary"],
                    "신뢰도": f"{comp['confidence']:.2f}",
                    "윤리적 영향": f"{comp['ethical_impact']:.2f}",
                    "주요 위험": (
                        list(comp["key_risks"])[0] if comp["key_risks"] else "없음"
                    ),
                }
            )

        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)

        # 추천사항
        st.subheader("💡 추천사항")
        recommendations = result["recommendations"]
        st.write(f"**최고 신뢰도:** {recommendations['highest_confidence']}")
        st.write(f"**최고 윤리적 영향:** {recommendations['best_ethical_impact']}")
        st.write(f"**종합 분석:** {recommendations['comparative_analysis']}")

    def _display_single_judgment_result(self, judgment):
        """단일 판단 결과 표시"""
        st.success(f"✅ {judgment.signature_id} 정책 판단 완료")

        # 핵심 메트릭
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("신뢰도", f"{judgment.confidence_score:.2f}")
        with col2:
            st.metric("윤리적 영향", f"{judgment.ethical_impact_score:.2f}")
        with col3:
            st.metric("시드 ID", judgment.seed_id)

        # 정책 추천
        st.subheader("📋 정책 추천사항")
        st.write(judgment.policy_recommendation)

        # 실행 전략
        st.subheader("🎯 실행 전략")
        for i, strategy in enumerate(judgment.implementation_strategy, 1):
            st.write(f"{i}. {strategy}")

        # 위험 평가
        st.subheader("⚠️ 위험 평가")
        risk_df = pd.DataFrame(
            [
                {"위험 요소": k, "점수": f"{v:.2f}"}
                for k, v in judgment.risk_assessment.items()
            ]
        )
        st.dataframe(risk_df, use_container_width=True)

        # 자원 요구사항과 일정을 확장 가능한 형태로 표시
        with st.expander("📊 자원 요구사항 및 일정"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**자원 요구사항:**")
                for key, value in judgment.resource_requirements.items():
                    st.write(f"- {key}: {value}")

            with col2:
                st.write("**실행 일정:**")
                for phase, timeline in judgment.timeline.items():
                    st.write(f"- {phase}: {timeline}")

    def _display_simulation_history(self):
        """시뮬레이션 히스토리 표시"""

        history_data = []
        for i, entry in enumerate(
            reversed(st.session_state.simulation_history[-10:]), 1
        ):
            history_data.append(
                {
                    "순번": i,
                    "시간": entry["timestamp"][:19],
                    "시나리오": entry["scenario_id"],
                    "유형": (
                        "비교"
                        if entry["type"] == "comparison"
                        else entry.get("signature_id", "단일")
                    ),
                    "결과": "성공" if entry["result"] else "실패",
                }
            )

        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)

    def render_adaptive_learning(self):
        """적응 학습 탭"""
        st.header("🧬 적응 학습 시스템")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("학습 제어")

            # 학습 설정
            st.write("**학습 매개변수**")
            failure_threshold = st.slider("실패 임계값", 0.0, 1.0, 0.6, 0.1)
            pattern_frequency = st.slider("패턴 최소 빈도", 1, 10, 3)
            learning_window = st.slider("학습 기간 (일)", 1, 30, 7)

            # 학습 실행
            if st.button("🧠 적응 학습 실행", type="primary"):
                with st.spinner("적응 학습 실행 중..."):
                    # 설정 업데이트
                    self.adaptive_learning.failure_threshold = failure_threshold
                    self.adaptive_learning.pattern_min_frequency = pattern_frequency
                    self.adaptive_learning.learning_window_days = learning_window

                    # 학습 실행
                    result = self.adaptive_learning.run_continuous_learning_cycle()
                    st.session_state.learning_results.append(result)

                    st.success("적응 학습 완료!")

            # 학습 상태
            st.subheader("📊 학습 상태")
            learning_summary = self.adaptive_learning.get_learning_summary()

            status = learning_summary["learning_engine_status"]
            st.metric("감지된 패턴", status["total_patterns_detected"])
            st.metric("적응 횟수", status["total_adaptations"])
            st.metric("활성 시그니처", status["active_signatures"])

        with col2:
            st.subheader("학습 결과")

            if st.session_state.learning_results:
                latest_result = st.session_state.learning_results[-1]

                if latest_result["cycle_result"] == "completed":
                    st.success("✅ 학습 사이클 완료")

                    # 결과 메트릭
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("감지 패턴", latest_result["patterns_detected"])
                    with col2:
                        st.metric("실행 액션", latest_result["actions_executed"])
                    with col3:
                        st.metric(
                            "성공률", f"{latest_result['average_success_rate']:.1%}"
                        )

                    # 패턴 요약
                    if latest_result.get("patterns_summary"):
                        st.subheader("🔍 감지된 패턴")
                        patterns_df = pd.DataFrame(latest_result["patterns_summary"])
                        st.dataframe(patterns_df, use_container_width=True)

                    # 적응 요약
                    if latest_result.get("adaptation_summary"):
                        st.subheader("⚡ 적응 결과")
                        adaptations_df = pd.DataFrame(
                            latest_result["adaptation_summary"]
                        )
                        st.dataframe(adaptations_df, use_container_width=True)

                elif latest_result["cycle_result"] == "no_patterns_detected":
                    st.info(
                        "패턴이 감지되지 않았습니다. 시스템이 안정적으로 작동 중입니다."
                    )
            else:
                st.info("적응 학습을 실행하여 결과를 확인하세요.")

        # 학습 히스토리 차트
        if len(st.session_state.learning_results) > 1:
            st.subheader("📈 학습 성능 트렌드")
            self._display_learning_trend_chart()

    def _display_learning_trend_chart(self):
        """학습 트렌드 차트 표시"""

        # 데이터 준비
        timestamps = []
        success_rates = []
        pattern_counts = []

        for result in st.session_state.learning_results:
            if result["cycle_result"] == "completed":
                timestamps.append(result["timestamp"][:19])
                success_rates.append(result["average_success_rate"])
                pattern_counts.append(result["patterns_detected"])

        if timestamps:
            # 이중 y축 차트
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 성공률 라인
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=success_rates,
                    name="성공률",
                    line=dict(color="green"),
                ),
                secondary_y=False,
            )

            # 패턴 수 바
            fig.add_trace(
                go.Bar(x=timestamps, y=pattern_counts, name="감지 패턴", opacity=0.6),
                secondary_y=True,
            )

            # 축 제목
            fig.update_xaxes(title_text="시간")
            fig.update_yaxes(title_text="성공률", secondary_y=False)
            fig.update_yaxes(title_text="패턴 수", secondary_y=True)

            fig.update_layout(title="적응 학습 성능 트렌드")

            st.plotly_chart(fig, use_container_width=True)

    def render_performance_report(self):
        """성능 리포트 탭"""
        st.header("📊 시그니처 성능 리포트")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("리포트 설정")

            # 분석 기간
            analysis_days = st.slider("분석 기간 (일)", 1, 90, 30)

            # 리포트 생성
            if st.button("📈 성능 리포트 생성", type="primary"):
                with st.spinner("성능 리포트 생성 중..."):
                    self.performance_reporter.analysis_window_days = analysis_days
                    report = self.performance_reporter.generate_performance_report()
                    st.session_state.last_report = report
                    st.success("리포트 생성 완료!")

            # 리포트 저장
            if st.session_state.last_report and st.button("💾 리포트 저장"):
                report_path = self.performance_reporter.save_report(
                    st.session_state.last_report
                )
                st.success(f"리포트 저장: {report_path}")

        with col2:
            st.subheader("성능 요약")

            if st.session_state.last_report:
                report = st.session_state.last_report

                # 기본 정보
                st.info(
                    f"**생성일:** {report.generation_timestamp[:19]}\n**분석기간:** {report.analysis_period}"
                )

                # 주요 메트릭
                if report.signature_metrics:
                    metrics_data = []
                    for metrics in report.signature_metrics:
                        metrics_data.append(
                            {
                                "시그니처": metrics.signature_id,
                                "실행 횟수": metrics.total_executions,
                                "성공률": f"{metrics.success_rate:.1%}",
                                "신뢰도": f"{metrics.avg_confidence:.2f}",
                                "실행 시간": f"{metrics.avg_execution_time:.2f}s",
                            }
                        )

                    df = pd.DataFrame(metrics_data)
                    st.dataframe(df, use_container_width=True)

                # 추천사항
                st.subheader("💡 주요 추천사항")
                best = report.recommendations.get("best_overall_signature", {})
                if best:
                    st.success(f"🏆 최고 성능: **{best['signature_id']}**")
                    st.write(best.get("reasoning", ""))

                # 통찰
                st.subheader("🔍 주요 통찰")
                for insight in report.insights:
                    st.write(f"• {insight}")
            else:
                st.info("리포트를 생성하여 결과를 확인하세요.")

        # 성능 비교 차트
        if (
            st.session_state.last_report
            and st.session_state.last_report.signature_metrics
        ):
            st.subheader("📊 시그니처 성능 비교")
            self._display_performance_comparison_chart()

    def _display_performance_comparison_chart(self):
        """성능 비교 차트 표시"""

        metrics = st.session_state.last_report.signature_metrics

        # 데이터 준비
        signatures = [m.signature_id for m in metrics]
        success_rates = [m.success_rate for m in metrics]
        confidences = [m.avg_confidence for m in metrics]
        execution_times = [m.avg_execution_time for m in metrics]

        # 차트 선택
        chart_type = st.selectbox(
            "차트 유형",
            ["성공률 비교", "신뢰도 비교", "실행 시간 비교", "종합 성능 레이더"],
        )

        if chart_type == "성공률 비교":
            fig = px.bar(x=signatures, y=success_rates, title="시그니처별 성공률")
            fig.update_yaxes(title="성공률")

        elif chart_type == "신뢰도 비교":
            fig = px.bar(x=signatures, y=confidences, title="시그니처별 평균 신뢰도")
            fig.update_yaxes(title="신뢰도")

        elif chart_type == "실행 시간 비교":
            fig = px.bar(
                x=signatures, y=execution_times, title="시그니처별 평균 실행 시간"
            )
            fig.update_yaxes(title="실행 시간 (초)")

        elif chart_type == "종합 성능 레이더":
            fig = go.Figure()

            for i, signature in enumerate(signatures):
                fig.add_trace(
                    go.Scatterpolar(
                        r=[
                            success_rates[i],
                            confidences[i],
                            1.0 - min(execution_times[i] / 10.0, 1.0),
                        ],
                        theta=["성공률", "신뢰도", "속도"],
                        fill="toself",
                        name=signature,
                    )
                )

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="시그니처 종합 성능 레이더 차트",
            )

        st.plotly_chart(fig, use_container_width=True)

    def render_loop_monitoring(self):
        """루프 모니터링 탭"""
        st.header("🔄 루프 실행 모니터링")

        # 시스템 성능 가져오기
        try:
            system_performance = get_system_performance()

            if "message" in system_performance:
                st.warning(system_performance["message"])
                return

            # 전체 메트릭
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("총 실행", system_performance.get("total_executions", 0))
            with col2:
                st.metric(
                    "성공률", f"{system_performance.get('overall_success_rate', 0):.1%}"
                )
            with col3:
                st.metric(
                    "평균 신뢰도",
                    f"{system_performance.get('overall_confidence', 0):.2f}",
                )
            with col4:
                st.metric("최근 실행", system_performance.get("recent_executions", 0))

            # 루프별 성능
            st.subheader("🔄 루프별 성능")
            loop_perf = system_performance.get("loop_performance", {})

            if loop_perf:
                loop_data = []
                for loop_id, stats in loop_perf.items():
                    loop_data.append(
                        {
                            "루프": loop_id,
                            "실행 횟수": stats["count"],
                            "성공률": f"{stats['success_rate']:.1%}",
                            "평균 신뢰도": f"{stats['avg_confidence']:.2f}",
                        }
                    )

                df = pd.DataFrame(loop_data)
                st.dataframe(df, use_container_width=True)

                # 루프 성능 차트
                col1, col2 = st.columns(2)

                with col1:
                    fig1 = px.bar(df, x="루프", y="성공률", title="루프별 성공률")
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.scatter(
                        df,
                        x="실행 횟수",
                        y="평균 신뢰도",
                        text="루프",
                        title="실행 횟수 vs 신뢰도",
                    )
                    fig2.update_traces(textposition="top center")
                    st.plotly_chart(fig2, use_container_width=True)

            # 시그니처별 성능
            st.subheader("🧬 시그니처별 성능")
            sig_perf = system_performance.get("signature_performance", {})

            if sig_perf:
                sig_data = []
                for sig_id, stats in sig_perf.items():
                    sig_data.append(
                        {
                            "시그니처": sig_id,
                            "실행 횟수": stats["count"],
                            "성공률": f"{stats['success_rate']:.1%}",
                            "평균 신뢰도": f"{stats['avg_confidence']:.2f}",
                        }
                    )

                df_sig = pd.DataFrame(sig_data)
                st.dataframe(df_sig, use_container_width=True)

                # 시그니처 성능 차트
                fig3 = px.bar(
                    df_sig,
                    x="시그니처",
                    y=["성공률", "평균 신뢰도"],
                    title="시그니처별 성능 비교",
                    barmode="group",
                )
                st.plotly_chart(fig3, use_container_width=True)

        except Exception as e:
            st.error(f"루프 모니터링 데이터 로드 실패: {e}")

    def render_signature_analysis(self):
        """시그니처 분석 탭"""
        st.header("🎯 시그니처 호환성 분석")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("분석 설정")

            signature_id = st.selectbox(
                "분석할 시그니처",
                ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
            )

            if st.button("🔍 호환성 분석 실행", type="primary"):
                with st.spinner("호환성 분석 중..."):
                    try:
                        compatibility = analyze_signature_loop_compatibility(
                            signature_id
                        )
                        st.session_state.compatibility_result = compatibility
                        st.success("분석 완료!")
                    except Exception as e:
                        st.error(f"분석 실패: {e}")

        with col2:
            st.subheader("분석 결과")

            if hasattr(st.session_state, "compatibility_result"):
                compatibility = st.session_state.compatibility_result

                # 추천 루프
                st.success(
                    f"**추천 루프:** {', '.join(compatibility['recommended_loops'])}"
                )

                # 호환성 데이터
                comp_data = []
                for loop_id, data in compatibility["loop_compatibility"].items():
                    comp_data.append(
                        {
                            "루프": loop_id,
                            "민감도": f"{data['sensitivity']:.2f}",
                            "설명": data["description"],
                            "단계 수": len(data["phases"]),
                        }
                    )

                df = pd.DataFrame(comp_data)
                st.dataframe(df, use_container_width=True)

                # 시각화
                col1, col2 = st.columns(2)

                with col1:
                    fig1 = px.bar(df, x="루프", y="민감도", title="루프별 민감도")
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.scatter(
                        df,
                        x="단계 수",
                        y="민감도",
                        text="루프",
                        title="단계 수 vs 민감도",
                    )
                    fig2.update_traces(textposition="top center")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("시그니처를 선택하고 분석을 실행하세요.")

    def render_system_control(self):
        """시스템 제어 탭"""
        st.header("⚙️ 시스템 제어 센터")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎛️ 시스템 설정")

            # 커널 설정
            st.write("**커널 설정**")
            current_seed_count = len(st.session_state.kernel.seed_registry)
            st.metric("현재 시드 수", current_seed_count)

            if st.button("🌱 다중 시드 생성"):
                count = st.number_input("생성할 시드 수", 1, 10, 3)
                signatures = [
                    "Echo-Aurora",
                    "Echo-Phoenix",
                    "Echo-Sage",
                    "Echo-Companion",
                ]

                for i in range(count):
                    signature = signatures[i % len(signatures)]
                    new_seed = st.session_state.kernel.generate_initial_state(
                        signature_id=signature
                    )

                st.success(f"{count}개 시드 생성 완료!")
                st.rerun()

            # 데이터 내보내기
            st.write("**데이터 관리**")

            if st.button("📤 시드 데이터 내보내기"):
                seeds_data = []
                for seed_id, seed in st.session_state.kernel.seed_registry.items():
                    seeds_data.append(
                        {
                            "seed_id": seed_id,
                            "signature": seed.signature_alignment,
                            "emotion": seed.emotion_rhythm.primary_emotion,
                            "strategy": seed.initial_strategy,
                            "sensitivity": seed.meta_sensitivity,
                            "evolution_potential": seed.evolution_potential,
                        }
                    )

                df = pd.DataFrame(seeds_data)
                csv = df.to_csv(index=False, encoding="utf-8-sig")

                st.download_button(
                    "💾 CSV 다운로드",
                    csv,
                    f"echo_seeds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                )

        with col2:
            st.subheader("📊 시스템 통계")

            # 시드 분포
            if st.session_state.kernel.seed_registry:
                signature_counts = {}
                emotion_counts = {}

                for seed in st.session_state.kernel.seed_registry.values():
                    sig = seed.signature_alignment or "Unknown"
                    signature_counts[sig] = signature_counts.get(sig, 0) + 1

                    emotion = seed.emotion_rhythm.primary_emotion
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

                # 시그니처 분포 차트
                fig1 = px.pie(
                    values=list(signature_counts.values()),
                    names=list(signature_counts.keys()),
                    title="시그니처 분포",
                )
                st.plotly_chart(fig1, use_container_width=True)

                # 감정 분포 차트
                fig2 = px.pie(
                    values=list(emotion_counts.values()),
                    names=list(emotion_counts.keys()),
                    title="감정 분포",
                )
                st.plotly_chart(fig2, use_container_width=True)

            # 시스템 상태
            st.subheader("🔧 시스템 상태")

            status_data = {
                "구성 요소": [
                    "시드 커널",
                    "정책 시뮬레이터",
                    "적응 학습",
                    "성능 리포터",
                ],
                "상태": ["✅ 정상", "✅ 정상", "✅ 정상", "✅ 정상"],
                "최근 활동": [
                    f"{len(st.session_state.kernel.evolution_history)}회 진화",
                    f"{len(st.session_state.simulation_history)}회 시뮬레이션",
                    f"{len(st.session_state.learning_results)}회 학습",
                    "최근 리포트 생성" if st.session_state.last_report else "대기 중",
                ],
            }

            status_df = pd.DataFrame(status_data)
            st.dataframe(status_df, use_container_width=True)

        # 시스템 진단
        st.subheader("🔍 시스템 진단")

        if st.button("🧪 종합 시스템 테스트"):
            with st.spinner("시스템 진단 중..."):
                diagnosis_results = []

                # 커널 테스트
                try:
                    test_seed = st.session_state.kernel.generate_initial_state()
                    diagnosis_results.append(
                        {
                            "구성요소": "시드 커널",
                            "상태": "✅ 정상",
                            "메시지": "시드 생성 성공",
                        }
                    )
                except Exception as e:
                    diagnosis_results.append(
                        {"구성요소": "시드 커널", "상태": "❌ 오류", "메시지": str(e)}
                    )

                # 정책 시뮬레이터 테스트
                try:
                    available_scenarios = get_available_scenarios()
                    diagnosis_results.append(
                        {
                            "구성요소": "정책 시뮬레이터",
                            "상태": "✅ 정상",
                            "메시지": f"{len(available_scenarios)}개 시나리오 로드",
                        }
                    )
                except Exception as e:
                    diagnosis_results.append(
                        {
                            "구성요소": "정책 시뮬레이터",
                            "상태": "❌ 오류",
                            "메시지": str(e),
                        }
                    )

                # 적응 학습 테스트
                try:
                    learning_summary = self.adaptive_learning.get_learning_summary()
                    diagnosis_results.append(
                        {
                            "구성요소": "적응 학습",
                            "상태": "✅ 정상",
                            "메시지": "학습 엔진 작동",
                        }
                    )
                except Exception as e:
                    diagnosis_results.append(
                        {"구성요소": "적응 학습", "상태": "❌ 오류", "메시지": str(e)}
                    )

                # 성능 리포터 테스트
                try:
                    data_sources = self.performance_reporter.collect_performance_data()
                    diagnosis_results.append(
                        {
                            "구성요소": "성능 리포터",
                            "상태": "✅ 정상",
                            "메시지": f"{sum(data_sources.values())}개 파일 감지",
                        }
                    )
                except Exception as e:
                    diagnosis_results.append(
                        {"구성요소": "성능 리포터", "상태": "❌ 오류", "메시지": str(e)}
                    )

                # 결과 표시
                diagnosis_df = pd.DataFrame(diagnosis_results)
                st.dataframe(diagnosis_df, use_container_width=True)

                # 전체 상태
                all_healthy = all(
                    "✅" in result["상태"] for result in diagnosis_results
                )
                if all_healthy:
                    st.success("🎉 모든 시스템 구성요소가 정상 작동 중입니다!")
                else:
                    st.error("⚠️ 일부 시스템 구성요소에 문제가 있습니다.")

    def render_meta_liminal_status(self):
        """🌀 Meta-Liminal 시스템 상태 및 모니터링"""
        st.header("🌀 Meta-Liminal System Status")
        st.markdown("**비판단자 존재구조와 LIMINAL 전이 시스템 실시간 모니터링**")

        if not META_LIMINAL_AVAILABLE:
            st.error("❌ Meta-Liminal 시스템이 사용 불가능합니다.")
            st.info("Meta-Liminal 모듈을 설치하고 설정을 확인해주세요.")
            return

        # 시스템 상태 개요
        col1, col2, col3, col4 = st.columns(4)

        try:
            liminal_bridge = get_liminal_bridge()
            meta_logger = get_meta_logger()

            bridge_status = liminal_bridge.get_bridge_status()
            log_summary = meta_logger.get_log_summary(hours=1)

            with col1:
                st.metric("현재 상태", bridge_status.get("current_state", "Unknown"))

            with col2:
                st.metric("총 전이 횟수", bridge_status.get("total_transitions", 0))

            with col3:
                success_rate = bridge_status.get("transition_success_rate", 0)
                st.metric("성공률", f"{success_rate:.1f}%")

            with col4:
                total_events = sum(
                    stats.get("total_events", 0) for stats in log_summary.values()
                )
                st.metric("시간별 이벤트", total_events)

        except Exception as e:
            st.error(f"상태 정보 로드 실패: {e}")
            return

        # 탭별 상세 정보
        meta_tab1, meta_tab2, meta_tab3, meta_tab4 = st.tabs(
            ["🌀 Meta Ring", "🌉 LIMINAL Bridge", "👁️ Warden World", "📊 Logs & Metrics"]
        )

        with meta_tab1:
            self._render_meta_ring_status(bridge_status, log_summary)

        with meta_tab2:
            self._render_liminal_bridge_status(bridge_status, liminal_bridge)

        with meta_tab3:
            self._render_warden_world_status(log_summary)

        with meta_tab4:
            self._render_meta_logs_status(log_summary, meta_logger)

    def _render_meta_ring_status(self, bridge_status, log_summary):
        """Meta Ring 상태 표시"""
        st.subheader("🌀 Meta-Liminal Ring 상태")

        # 비판단자 존재구조 상태
        entities = [
            {"name": "Observer.Zero", "description": "루프 감시자", "status": "active"},
            {"name": "Reflector.CC", "description": "구조 반사자", "status": "standby"},
            {
                "name": "Silencer.Veil",
                "description": "침묵 유도자",
                "status": "standby",
            },
            {"name": "DriftAnchor", "description": "캡슐 안정자", "status": "active"},
            {
                "name": "LoopHorizon",
                "description": "루프 리셋자",
                "status": "monitoring",
            },
        ]

        for entity in entities:
            with st.expander(f"{entity['name']} - {entity['description']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**상태**: {entity['status']}")
                    if entity["name"] == "Observer.Zero":
                        st.write("🔍 실시간 판단 루프 감시 중")
                    elif entity["status"] == "active":
                        st.write("⚡ 능동적 모니터링")
                    else:
                        st.write("⏳ 대기 상태")

                with col2:
                    # Mock activity data
                    if entity["name"] in ["Observer.Zero", "DriftAnchor"]:
                        st.success("정상 작동")
                    else:
                        st.info("대기 중")

        # 최근 Meta Ring 이벤트
        if "meta_ring" in log_summary:
            ring_stats = log_summary["meta_ring"]
            st.metric("최근 1시간 Ring 이벤트", ring_stats.get("total_events", 0))

    def _render_liminal_bridge_status(self, bridge_status, liminal_bridge):
        """LIMINAL Bridge 상태 표시"""
        st.subheader("🌉 LIMINAL Bridge 상태")

        # 전이 통계
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 전이 통계")

            # 전이 성공률 차트
            if bridge_status.get("total_transitions", 0) > 0:
                success_rate = bridge_status.get("transition_success_rate", 0)
                fail_rate = 100 - success_rate

                fig = px.pie(
                    values=[success_rate, fail_rate],
                    names=["성공", "실패"],
                    title="LIMINAL 전이 성공률",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("전이 데이터가 없습니다.")

        with col2:
            st.subheader("⚙️ 브리지 설정")

            # 전이 임계값 표시 (설정에서 읽기)
            st.write("**전이 임계값:**")
            st.write("- LIMINAL 점수: 0.7")
            st.write("- 감정 진폭: 0.85")
            st.write("- 연속 실패: 2회")

            # 실시간 모니터링 토글
            monitoring = st.checkbox("실시간 모니터링", value=True)
            if monitoring:
                st.success("🔄 실시간 모니터링 활성화")
            else:
                st.warning("⏸️ 모니터링 일시 정지")

        # 최근 전이 이력
        st.subheader("📝 최근 전이 이력")

        # Mock 전이 데이터 (실제로는 bridge에서 가져와야 함)
        recent_transitions = [
            {
                "시간": "14:23",
                "유형": "감정 과부하",
                "결과": "✅ 성공",
                "대상": "Selene",
            },
            {"시간": "14:15", "유형": "판단 실패", "결과": "✅ 성공", "대상": "Warden"},
            {"시간": "13:58", "유형": "루프 정체", "결과": "❌ 실패", "대상": "N/A"},
        ]

        transitions_df = pd.DataFrame(recent_transitions)
        st.dataframe(transitions_df, use_container_width=True)

    def _render_warden_world_status(self, log_summary):
        """Warden World 상태 표시"""
        st.subheader("👁️ Warden World 존재계")

        # 존재계 엔티티 상태
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🛡️ Warden")
            st.write("**역할**: 경계 감시자")
            st.write("**상태**: 대기")
            st.progress(0.3, text="활성화 준비도")

        with col2:
            st.subheader("🌙 Selene")
            st.write("**역할**: 감정 공명자")
            st.write("**상태**: 공명 준비")
            st.progress(0.6, text="공명 감도")

        with col3:
            st.subheader("🪞 Mirrorless")
            st.write("**역할**: 무반사체")
            st.write("**상태**: 해체 준비")
            st.progress(0.1, text="해체 임계점")

        # 감정 공명 패턴
        st.subheader("💭 감정 공명 패턴")

        emotion_data = {
            "감정 유형": [
                "grief",
                "confusion",
                "emptiness",
                "longing",
                "acceptance",
                "silence",
            ],
            "공명 빈도": [15, 8, 3, 12, 5, 2],
            "평균 깊이": [0.8, 0.6, 0.95, 0.7, 0.4, 0.3],
        }

        emotions_df = pd.DataFrame(emotion_data)

        fig = px.scatter(
            emotions_df,
            x="공명 빈도",
            y="평균 깊이",
            size="공명 빈도",
            hover_name="감정 유형",
            title="감정 공명 패턴 분석",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Warden World 활동 로그
        if "warden_world" in log_summary:
            world_stats = log_summary["warden_world"]
            st.metric("최근 1시간 존재계 활동", world_stats.get("total_events", 0))

    def _render_meta_logs_status(self, log_summary, meta_logger):
        """Meta Logs 상태 및 분석"""
        st.subheader("📊 Meta Logs & Metrics")

        # 로그 타입별 통계
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 로그 통계")

            log_data = []
            for log_type, stats in log_summary.items():
                log_data.append(
                    {
                        "로그 타입": log_type,
                        "이벤트 수": stats.get("total_events", 0),
                        "시간당 평균": stats.get("events_per_hour", 0),
                    }
                )

            if log_data:
                logs_df = pd.DataFrame(log_data)
                st.dataframe(logs_df, use_container_width=True)
            else:
                st.info("로그 데이터가 없습니다.")

        with col2:
            st.subheader("🔧 로그 관리")

            if st.button("📥 로그 다운로드"):
                st.info("로그 다운로드 기능 구현 예정")

            if st.button("🗑️ 오래된 로그 정리"):
                try:
                    cleaned_count = meta_logger.cleanup_old_logs(retention_days=7)
                    st.success(f"{cleaned_count}개 파일 정리 완료")
                except Exception as e:
                    st.error(f"로그 정리 실패: {e}")

            log_level = st.selectbox(
                "로그 레벨", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1
            )

        # 실시간 로그 모니터링
        st.subheader("🔄 실시간 로그 모니터링")

        if st.checkbox("실시간 로그 스트리밍"):
            st.info("실시간 로그 스트리밍 활성화 - 새로고침하여 최신 이벤트 확인")

            # 최근 로그 엔트리 표시 (Mock 데이터)
            recent_logs = [
                {
                    "시간": "14:25:33",
                    "타입": "meta_ring",
                    "이벤트": "observer_zero_watch_started",
                    "상태": "INFO",
                },
                {
                    "시간": "14:24:12",
                    "타입": "liminal_transitions",
                    "이벤트": "transition_attempt",
                    "상태": "SUCCESS",
                },
                {
                    "시간": "14:23:45",
                    "타입": "warden_world",
                    "이벤트": "selene_resonance",
                    "상태": "INFO",
                },
            ]

            logs_display_df = pd.DataFrame(recent_logs)
            st.dataframe(logs_display_df, use_container_width=True)

    def render_echogpt(self):
        """EchoGPT 탭 렌더링"""
        st.header("🤖 EchoGPT - 우리만의 ChatGPT")

        if not ECHOGPT_AVAILABLE:
            st.error("❌ EchoGPT 시스템이 사용 불가능합니다.")
            st.info("echogpt.py와 관련 모듈들이 올바르게 설치되어 있는지 확인해주세요.")
            return

        # EchoGPT 초기화
        if "echogpt" not in st.session_state:
            st.session_state.echogpt = EchoGPT()
            st.session_state.echogpt_messages = []

        # 사이드바: 세션 관리
        with st.sidebar:
            st.subheader("💾 EchoGPT 세션 관리")

            # 현재 세션 정보
            current_session = st.session_state.echogpt.session_id
            st.info(f"현재 세션: `{current_session}`")

            # 새 세션 시작
            if st.button("🆕 새 세션"):
                st.session_state.echogpt = EchoGPT()
                st.session_state.echogpt_messages = []
                st.rerun()

            # 세션 목록
            sessions = st.session_state.echogpt.list_sessions()
            if sessions:
                selected_session = st.selectbox(
                    "저장된 세션",
                    [""] + sessions[:10],
                    format_func=lambda x: "세션 선택..." if x == "" else x,
                )

                if selected_session and st.button("📁 세션 로드"):
                    if st.session_state.echogpt.load_session(selected_session):
                        st.session_state.echogpt_messages = (
                            st.session_state.echogpt.session.messages.copy()
                        )
                        st.success("✅ 세션 로드 완료!")
                        st.rerun()

            # 통계
            if st.session_state.echogpt_messages:
                st.subheader("📊 세션 통계")
                user_msgs = len(
                    [m for m in st.session_state.echogpt_messages if m.role == "user"]
                )
                ai_msgs = len(
                    [
                        m
                        for m in st.session_state.echogpt_messages
                        if m.role == "assistant"
                    ]
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("사용자", user_msgs)
                with col2:
                    st.metric("AI", ai_msgs)

        # 메인 채팅 영역
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("💬 대화")

            # 대화 내역 표시
            chat_container = st.container()
            with chat_container:
                if st.session_state.echogpt_messages:
                    for message in st.session_state.echogpt_messages:
                        self.render_echogpt_message(message)
                else:
                    st.info("👋 EchoGPT와 대화를 시작해보세요!")

            # 사용자 입력
            user_input = st.chat_input("메시지를 입력하세요...")

            if user_input:
                with st.spinner("🤖 EchoGPT가 응답하고 있습니다..."):
                    # 동기적으로 처리
                    st.session_state.echogpt.chat_sync(user_input)
                    st.session_state.echogpt_messages = (
                        st.session_state.echogpt.session.messages.copy()
                    )

                st.rerun()

        with col2:
            st.subheader("🎯 분석 정보")

            # 최근 메시지의 Intent 분석
            if st.session_state.echogpt_messages:
                recent_msg = None
                for msg in reversed(st.session_state.echogpt_messages):
                    if msg.role == "assistant" and msg.intent:
                        recent_msg = msg
                        break

                if recent_msg:
                    st.success(f"**Intent**: {recent_msg.intent}")
                    if recent_msg.signature:
                        st.info(f"**Signature**: {recent_msg.signature}")
                    if recent_msg.confidence:
                        st.metric("신뢰도", f"{recent_msg.confidence:.0%}")
                    if recent_msg.processing_time:
                        st.metric("처리 시간", f"{recent_msg.processing_time:.2f}초")
                    if recent_msg.provider:
                        st.metric("Provider", recent_msg.provider)

            # Intent 분포
            intents = [
                m.intent
                for m in st.session_state.echogpt_messages
                if m.role == "assistant" and m.intent
            ]
            if intents:
                st.subheader("📈 Intent 분포")
                intent_counts = pd.Series(intents).value_counts()
                st.bar_chart(intent_counts)

            # 빠른 액션
            st.subheader("⚡ 빠른 액션")

            quick_prompts = [
                "안녕하세요!",
                "창의적인 아이디어를 주세요",
                "이 문제를 분석해주세요",
                "감정적 지원이 필요해요",
                "함께 작업해요",
                "철학적인 질문이 있어요",
            ]

            for prompt in quick_prompts:
                if st.button(f"💬 {prompt}", key=f"quick_{prompt}"):
                    with st.spinner("🤖 처리 중..."):
                        st.session_state.echogpt.chat_sync(prompt)
                        st.session_state.echogpt_messages = (
                            st.session_state.echogpt.session.messages.copy()
                        )
                    st.rerun()

        # EWMA 메트릭 모니터링 섹션
        st.divider()
        st.subheader("📊 실시간 성능 모니터링 (EWMA)")

        # 새로고침 컨트롤
        col_refresh, col_auto = st.columns([3, 1])
        with col_refresh:
            refresh_button = st.button("🔄 메트릭 새로고침", key="ewma_refresh")
        with col_auto:
            auto_refresh = st.checkbox("자동 새로고침 (5초)", key="auto_refresh_ewma")

        # 메트릭 데이터 가져오기
        echogpt_metrics = self.fetch_echogpt_metrics()

        if echogpt_metrics:
            # 기본 메트릭 표시
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("총 요청", echogpt_metrics.get("count", 0))
            with metric_col2:
                avg_ttl = echogpt_metrics.get("avg_ttl_ms", 0)
                st.metric("평균 TTL (ms)", f"{avg_ttl}")
            with metric_col3:
                agree_rate = echogpt_metrics.get("intent_agree_rate", 0)
                st.metric("Intent 일치율", f"{agree_rate:.1%}")
            with metric_col4:
                tool_rate = echogpt_metrics.get("tool_success_rate", 0)
                st.metric("Tool 성공률", f"{tool_rate:.1%}")

            # EWMA 차트
            ewma_data = echogpt_metrics.get("ewma_latency_ms", {})
            if ewma_data and any(ewma_data.values()):
                st.subheader("📈 EWMA 지연 시간 추세 (스파이크 감지)")

                # EWMA 히스토리 관리
                if "ewma_history" not in st.session_state:
                    st.session_state.ewma_history = []

                # 새 데이터 추가
                timestamp = datetime.now().strftime("%H:%M:%S")
                new_point = {
                    "timestamp": timestamp,
                    "1m": ewma_data.get("1m", 0),
                    "5m": ewma_data.get("5m", 0),
                    "15m": ewma_data.get("15m", 0),
                }
                st.session_state.ewma_history.append(new_point)

                # 최근 50개 포인트만 유지
                if len(st.session_state.ewma_history) > 50:
                    st.session_state.ewma_history = st.session_state.ewma_history[-50:]

                # DataFrame 생성 및 차트 표시
                if len(st.session_state.ewma_history) >= 2:
                    df_ewma = pd.DataFrame(st.session_state.ewma_history)
                    df_ewma = df_ewma.set_index("timestamp")

                    # Plotly 라인 차트
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=df_ewma.index,
                            y=df_ewma["1m"],
                            mode="lines+markers",
                            name="1분 EWMA",
                            line=dict(color="red", width=2),
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_ewma.index,
                            y=df_ewma["5m"],
                            mode="lines+markers",
                            name="5분 EWMA",
                            line=dict(color="orange", width=2),
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_ewma.index,
                            y=df_ewma["15m"],
                            mode="lines+markers",
                            name="15분 EWMA",
                            line=dict(color="green", width=2),
                        )
                    )

                    fig.update_layout(
                        title="EWMA 지연 시간 추세",
                        xaxis_title="시간",
                        yaxis_title="지연 시간 (ms)",
                        height=400,
                        showlegend=True,
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 현재 EWMA 값 표시
                    ewma_col1, ewma_col2, ewma_col3 = st.columns(3)
                    with ewma_col1:
                        st.metric("1분 EWMA", f"{ewma_data.get('1m', 0):.1f}ms")
                    with ewma_col2:
                        st.metric("5분 EWMA", f"{ewma_data.get('5m', 0):.1f}ms")
                    with ewma_col3:
                        st.metric("15분 EWMA", f"{ewma_data.get('15m', 0):.1f}ms")

                # 스파이크 감지 알림
                if ewma_data.get("1m", 0) > ewma_data.get("5m", 0) * 1.5:
                    st.warning(
                        "⚠️ 1분 EWMA가 5분 EWMA보다 50% 이상 높습니다. 최근 지연 스파이크 감지!"
                    )

                if ewma_data.get("5m", 0) > ewma_data.get("15m", 0) * 1.3:
                    st.info(
                        "📊 5분 EWMA가 15분 EWMA보다 30% 이상 높습니다. 지연 시간 증가 추세 감지"
                    )

            else:
                st.info(
                    "EWMA 데이터가 충분하지 않습니다. 몇 개의 요청을 보내신 후 다시 확인해주세요."
                )

        else:
            st.error(
                "❌ EchoGPT 메트릭을 가져올 수 없습니다. 서버가 실행 중인지 확인해주세요."
            )

        # 자동 새로고침 처리
        if auto_refresh:
            import time

            # 현재 페이지가 EchoGPT 탭이고 자동 새로고침이 활성화된 경우에만 실행
            placeholder = st.empty()
            with placeholder:
                st.info(f"⏱️ 자동 새로고침: 5초 후 업데이트...")
                time.sleep(5)
            st.rerun()

    def fetch_echogpt_metrics(self) -> Dict[str, Any]:
        """EchoGPT 메트릭 데이터 가져오기"""
        try:
            response = requests.get(
                f"{self.echogpt_api_url}/v1/system/status", timeout=3.0
            )
            if response.status_code == 200:
                data = response.json()
                # /v1/system/status는 metrics 필드 안에 우리가 원하는 데이터가 있을 수 있음
                metrics = data.get(
                    "metrics", data
                )  # 직접 metrics이거나 data 자체일 수 있음
                return metrics
            else:
                st.error(f"API 응답 오류: {response.status_code}")
                return {}
        except requests.exceptions.ConnectionError:
            st.error("❌ EchoGPT 서버에 연결할 수 없습니다. (포트 8002)")
            return {}
        except requests.exceptions.Timeout:
            st.error("⏰ API 요청 시간 초과")
            return {}
        except Exception as e:
            st.error(f"❌ 메트릭 가져오기 실패: {str(e)}")
            return {}

    def render_echogpt_message(self, message: EchoGPTMessage):
        """EchoGPT 메시지 렌더링"""
        if message.role == "user":
            with st.chat_message("user"):
                st.write(message.content)
                st.caption(f"🕒 {message.timestamp}")

        elif message.role == "assistant":
            with st.chat_message("assistant"):
                # 메타데이터 배지
                badges = ""
                if message.intent:
                    badges += f"🎯 {message.intent}  "
                if message.signature:
                    badges += f"🎭 {message.signature}  "
                if message.confidence:
                    badges += f"📊 {message.confidence:.0%}  "

                if badges:
                    st.caption(badges)

                st.write(message.content)

                # 하단 메타데이터
                meta_info = f"🕒 {message.timestamp}"
                if message.provider:
                    meta_info += f" | 🔧 {message.provider}"
                if message.processing_time:
                    meta_info += f" | ⏱️ {message.processing_time:.2f}s"

                st.caption(meta_info)


def main():
    """메인 함수"""
    dashboard = ComprehensiveDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
