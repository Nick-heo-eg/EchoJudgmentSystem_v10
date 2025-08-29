# loop_orchestrator.py - .flow.yaml 기반 실행 로직 + Context 흐름 복원 + Thread 상태 추적 시스템 + Flow 전환 감지 + Emotion 추론 모듈 통합

import yaml
import json
from .persona_core import PersonaCore
from echo_engine.emotion_infer import infer_emotion
from echo_engine.strategic_predictor import predict_strategy
from echo_engine.reasoning import reason_with_echo
from echo_engine.meta_logger import write_meta_log
from datetime import datetime
from pathlib import Path

THREAD_STATE_PATH = Path(".context/thread_state.json")


# ⛓️ Context 보강 기능
def extend_context(input_text: str, signature_id: str, log_limit: int = 3) -> str:
    log_path = Path(f"res/meta_log/{signature_id}_judgments.json")
    if not log_path.exists():
        return input_text

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()[-log_limit:]
    fragments = []
    for line in lines:
        try:
            data = json.loads(line)
            fragments.append(f"[전략:{data['strategy']} 감정:{data['emotion']}]")
        except:
            continue

    if not fragments:
        return input_text

    context_prefix = " ".join(fragments)
    return f"{context_prefix} → {input_text}"


# 📌 Thread 상태 추적 및 전환 확인
def save_thread_state(signature_id: str, latest_text: str):
    THREAD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(THREAD_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "signature_id": signature_id,
                "latest_text": latest_text,
                "timestamp": datetime.now().isoformat(),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


def load_thread_state():
    if THREAD_STATE_PATH.exists():
        try:
            with open(THREAD_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None


def check_context_switch(current_signature: str):
    prev = load_thread_state()
    if not prev:
        return
    if prev["signature_id"] != current_signature:
        print("\n🧭 이전 흐름에서 시그니처가 변경되었습니다!")
        print(f"- 이전: {prev['signature_id']} → 현재: {current_signature}")
        print("- 계속 이어서 진행할까요? 아니면 새 흐름으로 리셋할까요?")


# 🧠 흐름 전환 감지기 (같은 스레드 내에서 의미적 변화 포착)
class FlowShiftDetector:
    def __init__(self):
        self.recent_topics = []

    def extract_topic(self, text: str) -> str:
        keywords = [
            "페르소나",
            "시그니처",
            "judgment",
            "loop",
            "meta_log",
            "reasoning",
            "streamlit",
            "api",
        ]
        for word in keywords:
            if word in text.lower():
                return word
        return "기타"

    def update_and_check(self, text: str):
        current = self.extract_topic(text)
        if self.recent_topics and self.recent_topics[-1] != current:
            print(
                f"\n🧠 흐름 전환 감지됨! → 이전: '{self.recent_topics[-1]}' → 현재: '{current}'"
            )
            print("↪️ 이전 흐름 이어서 할까요? or 새로운 흐름으로 간주할까요?")
        self.recent_topics.append(current)


# Flow yaml 로딩
def load_flow_yaml(path=".flow.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 판단 세션 실행 객체
class EchoJudgmentSession:
    def __init__(self, input_text: str, signature_id: str):
        self.input_text = input_text
        self.signature_id = signature_id
        self.flow = load_flow_yaml()
        self.flow_map = self.flow["flow"]["signature_persona_map"]
        self.flow_steps = self.flow["flow"]["flow_structure"]["steps"]
        self.flow_shift = FlowShiftDetector()
        self.result = {}

    def validate_signature(self):
        if self.signature_id not in self.flow_map:
            raise ValueError(
                f"시그니처 ID {self.signature_id}는 flow.yaml에 정의되어 있지 않습니다."
            )

    def detect_shift(self):
        self.flow_shift.update_and_check(self.input_text)
        check_context_switch(self.signature_id)

    def extend_context(self):
        self.input_text = extend_context(self.input_text, self.signature_id)

    def activate_persona(self):
        persona = PersonaCore(self.signature_id)
        persona.activate()
        return persona

    def run_judgment_pipeline(self, traits):
        strategy = predict_strategy(self.input_text)
        emotion = infer_emotion(self.input_text)
        reasoning = reason_with_echo(
            self.input_text, {"strategy": strategy, "emotion": emotion}
        )
        return strategy, emotion, reasoning

    def log_and_save(self):
        write_meta_log(self.result, self.signature_id)
        save_thread_state(self.signature_id, self.input_text)

    def evaluate(self):
        self.validate_signature()
        self.detect_shift()
        self.extend_context()
        persona_info = self.flow_map[self.signature_id]
        traits = self.activate_persona()
        strategy, emotion, reasoning = self.run_judgment_pipeline(traits)
        self.result = {
            "input_text": self.input_text,
            "signature_id": self.signature_id,
            "persona": persona_info["persona"],
            "traits": traits,
            "strategy": strategy,
            "emotion": emotion,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
        }
        self.log_and_save()
        return self.result


def process_input_with_merge(input_text: str, signature_id: str = "Echo-Aurora"):
    """main.py에서 호출하는 통합 처리 함수"""
    try:
        session = EchoJudgmentSession(input_text=input_text, signature_id=signature_id)
        result = session.evaluate()

        # main.py에서 기대하는 형식으로 변환
        return {
            "judgment": result.get("reasoning", "판단 완료"),
            "signature": result.get("signature_id", signature_id),
            "emotion": result.get("emotion", "neutral"),
            "strategy": result.get("strategy", "balanced"),
            "confidence": 0.8,
            "persona": result.get("persona", {}),
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
        }
    except Exception as e:
        return {
            "judgment": f"처리 중 오류 발생: {str(e)}",
            "signature": signature_id,
            "emotion": "neutral",
            "strategy": "error_handling",
            "confidence": 0.1,
            "error": True,
        }


def run_flow(input_text: str, signature_id: str):
    session = EchoJudgmentSession(input_text=input_text, signature_id=signature_id)
    return session.evaluate()


if __name__ == "__main__":
    test_text = "이 상황에서 어떤 전략이 효과적일까요?"
    output = run_flow(test_text, signature_id="S03_분석관찰자")
    print("\n[판단 결과]\n", yaml.dump(output, allow_unicode=True))
