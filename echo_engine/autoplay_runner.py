# echo_engine/autoplay_runner.py


# Compatibility: create safe fallback for missing function
def load_judgment_logs(*args, **kwargs):
    """Safe fallback for missing load_judgment_logs function."""
    print(f"[load_judgment_logs] fallback: args={args}, kwargs={kwargs}")
    return []  # Return empty list as safe default


from echo_engine.world_generator.symbol_mapper import (
    map_strategy_to_symbol,
    map_emotion_to_symbol,
)
from echo_engine.world_generator.seed_compiler import compile_seed
from echo_engine.world_generator.world_logic import generate_world
from echo_engine.world_generator.res_parser import parse_emotion_from_reasoning
from echo_engine.action_recommendation import recommend_action
from echo_engine.symbol_story_engine import generate_story
from echo_engine.world_generator.res_logger import save_res_log
from echo_engine.models.judgement import (
    MergedJudgmentResult,
)  # ✅ 수정됨 (spelling: judgement)

import time


def run_autoplay_loop(num_samples: int = 10, delay_sec: float = 0.5):
    print(f"🔁 Autoplay 실행: {num_samples} 회 반복")

    logs = load_judgment_logs(limit=num_samples)
    if not logs:
        print("❌ 판단 로그가 없습니다.")
        return

    for idx, row in enumerate(logs):
        judgment = MergedJudgmentResult(**row)
        print(f"\n▶️ {idx+1}/{num_samples} - {judgment.input_text[:30]}...")

        strategy_symbol = map_strategy_to_symbol(judgment.final_decision)
        emotion = parse_emotion_from_reasoning(judgment.echo_reasoning)
        emotion_symbol = map_emotion_to_symbol(emotion)

        seed = compile_seed(strategy_symbol, emotion_symbol)
        world = generate_world(seed)
        action = recommend_action(world)
        story = generate_story(seed, judgment.final_decision, emotion, action)
        path = save_res_log(judgment, seed, world, action, story)

        print(f"✅ 저장 완료: {path}")
        time.sleep(delay_sec)

    print("\n🎉 Autoplay 루프 완료.")
