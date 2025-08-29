# streamlit_ui/components/world_panel.py

# streamlit_ui/components/world_panel.py

import streamlit as st
from world_generator.symbol_mapper import map_strategy_to_symbol, map_emotion_to_symbol
from world_generator.seed_compiler import compile_seed
from world_generator.world_logic import generate_world
from world_generator.res_parser import parse_emotion_from_reasoning
from echo_engine.action_recommendation import recommend_action
from echo_engine.symbol_story_engine import generate_story
from world_generator.res_logger import save_res_log  # ✅ 여기 추가!
from models.judgment import MergedJudgmentResult


def render_world_panel(judgment: MergedJudgmentResult):
    strategy_symbol = map_strategy_to_symbol(judgment.final_decision)
    emotion = parse_emotion_from_reasoning(judgment.echo_reasoning)
    emotion_symbol = map_emotion_to_symbol(emotion)

    seed = compile_seed(strategy_symbol, emotion_symbol)
    world = generate_world(seed)
    action = recommend_action(world)

    st.markdown(f"### 🌍 생성된 세계: `{world['id']}`")
    st.markdown(f"**전략 상징**: {strategy_symbol} / **감정 상징**: {emotion_symbol}")
    st.json(world["state"])

    st.markdown(f"### 🎯 추천 행동")
    st.success(action)

    # ✅ 여기서 이야기 생성
    story = generate_story(seed, judgment.final_decision, emotion, action)
    st.markdown("### 📝 이야기 생성")
    st.info(story)

    # ✅ 선택 보상
    if st.button("👍 이 행동 선택합니다"):
        from echo_engine.reinforcement_engine import reward_selected_action

        reward = reward_selected_action(judgment.final_decision)
        st.success(f"보상 {reward:+.2f} 이(가) 적용되었습니다.")

    # ✅ .res 저장 버튼
    if st.button("💾 이 결과를 .res 파일로 저장"):
        path = save_res_log(judgment, seed, world, action, story)
        st.success(f"저장 완료! `{path}`")
