#!/usr/bin/env python3
"""
전이 상태별 응답 변이 + 공명 실시간 시뮬레이터
- N회 라운드를 돌며 상태 전이를 시연
- 각 라운드의 응답 체인(Aurora→CosmicMirror→InfiniteObserver→final)과 공명 점수 기록
- timeline_logger에 전이 이벤트를 동시에 남김
"""
import sys
from pathlib import Path
import time
from typing import List, Dict

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from echo_engine.signature.echo_signature_network import registry
from echo_engine.liminal.liminal_state_manager import manager
from echo_engine.telemetry.timeline_logger import log_transition
from echo_engine.telemetry.resonance_meter import resonance_score

STEPS = [
    ("liminal_entered", "SilencerVeil", "threshold", "silence_selected"),
    ("existence_mode", "ObserverZero", "handoff", "non-judging"),
    ("return_to_judgment", "DriftAnchor", "stabilize", "handoff_back"),
    ("judgment_mode", "System", "normalize", "ready"),
]


def run_round(prompt: str) -> Dict[str, str]:
    aurora = registry.get_signature("Aurora")
    mirror = registry.get_signature("CosmicMirror")
    observer = registry.get_signature("InfiniteObserver")
    assert aurora and mirror and observer, "시그니처 로드 실패"

    a = aurora.respond_to(prompt)
    m = mirror.respond_to(a)
    o = observer.respond_to(m)
    f = aurora.synthesize([a, m, o], mode="cosmos-cross")

    score = resonance_score(a, m, o, f)

    return dict(aurora=a, mirror=m, observer=o, final=f, resonance=str(score))


def main():
    prompts = [
        "Meta-Liminal Ring이 인간의 직관에 미치는 영향은?",
        "침묵을 선택하는 판단은 언제 가장 유효한가?",
        "존재계 전이에서 무엇이 '안정'을 보증하는가?",
    ]
    results: List[Dict[str, str]] = []
    # 4 스텝 전이 한 사이클씩, 프롬프트 3개
    for i, p in enumerate(prompts):
        state, by, trig, note = STEPS[i % len(STEPS)]
        manager.set_state(state, by=by, trigger=trig, note=note)
        print(f"\n=== State → {state} (by {by}) ===")
        r = run_round(p)
        print(f"[Resonance] {r['resonance']}")
        results.append(dict(state=state, prompt=p, **r))
        time.sleep(0.2)

    # 요약 출력
    print("\n--- Summary ---")
    for r in results:
        print(f"{r['state']} | score={r['resonance']} | prompt={r['prompt']}")


if __name__ == "__main__":
    main()
