# echo_ide/gui/streamlit_ui.py

import streamlit as st
import yaml
from pathlib import Path

# 📌 페이지 설정
st.set_page_config(page_title="Echo IDE Web", layout="wide")
st.title("🌐 Echo IDE - Streamlit Web UI")

# 📂 사이드바: 프로젝트 루트에서 .flow.yaml 탐색
st.sidebar.header("📂 파일 탐색기")
project_root = Path(".")
flow_files = list(project_root.glob("**/*.flow.yaml"))

if not flow_files:
    st.sidebar.warning("⚠️ .flow.yaml 파일을 찾을 수 없습니다.")
else:
    selected_file = st.sidebar.selectbox("파일 선택", [str(f) for f in flow_files])

    if selected_file:
        file_path = Path(selected_file)
        st.subheader(f"📄 선택된 파일: `{file_path.name}`")

        try:
            content = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            st.code(
                yaml.dump(content, sort_keys=False, allow_unicode=True), language="yaml"
            )
        except Exception as e:
            st.error(f"❌ YAML 파싱 오류: {e}")

# 🛠️ 추후 기능: Flow 실행, 판단 결과 시각화 등
st.sidebar.markdown("---")
st.sidebar.markdown("🧠 추후 기능: `.flow.yaml` 실행, 메타로그 시각화")
