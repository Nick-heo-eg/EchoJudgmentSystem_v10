import os
import json

LOG_PATH = "meta_logs/"
KEY_LOG_FILES = [
    "loop_metrics.jsonl",
    "llm_free_judgments.jsonl",
    "unified_meta_logs.jsonl",
]


def find_recent_trace():
    traces = []
    for log_file in KEY_LOG_FILES:
        full_path = os.path.join(LOG_PATH, log_file)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                for line in f.readlines()[-20:]:  # 최근 20줄까지 넉넉히 읽기
                    try:
                        data = json.loads(line.strip())
                        # 판단 로그로 간주할 필수 필드가 모두 있을 경우만 저장
                        if all(
                            k in data
                            for k in [
                                "input_text",
                                "emotion",
                                "signature",
                                "judgment_path",
                            ]
                        ):
                            traces.append(data)
                    except json.JSONDecodeError:
                        continue
    return traces


def extract_trace_summary(trace):
    return {
        "input_text": trace.get("input_text", "<unknown>"),
        "emotion": trace.get("emotion", "neutral"),
        "signature": trace.get("signature", "default"),
        "judgment_path": trace.get("judgment_path", []),
        "final_module": trace.get("final_module", "<unknown>"),
    }


def show_trace_summary():
    traces = find_recent_trace()
    if not traces:
        print(
            "⚠️ 판단 로그를 찾지 못했습니다. `meta_logs/*.jsonl`에 유효한 판단 기록이 필요합니다."
        )
        return

    print("\n📍 최근 판단 흐름 (최대 10개):\n")
    for i, trace in enumerate(traces):
        summary = extract_trace_summary(trace)
        print(f"[{i+1}] 입력: {summary['input_text']}")
        print(f"    🎭 감정: {summary['emotion']}, 🧬 시그니처: {summary['signature']}")
        print(f"    🧠 판단 경로: {' → '.join(summary['judgment_path'])}")
        print(f"    🔚 최종 응답 모듈: {summary['final_module']}\n")


if __name__ == "__main__":
    show_trace_summary()
