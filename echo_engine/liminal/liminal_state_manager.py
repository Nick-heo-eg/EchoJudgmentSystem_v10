# echo_engine/liminal/liminal_state_manager.py
from typing import Literal, Dict, Any
from dataclasses import dataclass, field
from echo_engine.telemetry.timeline_logger import log_transition

LiminalState = Literal[
    "judgment_mode", "liminal_entered", "existence_mode", "return_to_judgment"
]


@dataclass
class LiminalStateManager:
    state: LiminalState = "judgment_mode"
    meta: Dict[str, Any] = field(default_factory=dict)

    def set_state(self, new_state: LiminalState, by: str, trigger: str, note: str = ""):
        self.state = new_state
        log_transition(state=new_state, trigger=trigger, by=by, note=note)

    def get_state(self) -> LiminalState:
        return self.state

    # 상태별 가중치(말투 강도/깊이/응답 길이 등 조절용)
    def response_profile(self) -> Dict[str, float]:
        table = {
            "judgment_mode": dict(
                depth=0.9, restraint=0.3, silence=0.0, reflect=0.5, length=1.0
            ),
            "liminal_entered": dict(
                depth=0.7, restraint=0.8, silence=0.6, reflect=0.9, length=0.8
            ),
            "existence_mode": dict(
                depth=1.2, restraint=0.6, silence=0.2, reflect=1.3, length=1.2
            ),
            "return_to_judgment": dict(
                depth=1.0, restraint=0.5, silence=0.0, reflect=0.8, length=1.0
            ),
        }
        return table.get(self.state, table["judgment_mode"])


# 싱글톤적으로 쓰기
manager = LiminalStateManager()
