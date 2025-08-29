# api/routers/meta_liminal.py
from fastapi import APIRouter
from meta_liminal_cosmos_integration import CosmosMetaLiminalIntegration
from echo_engine.liminal.liminal_state_manager import manager
from echo_engine.telemetry.resonance_meter import resonance_score
from echo_engine.signature.echo_signature_network import registry

router = APIRouter(prefix="/meta-liminal", tags=["meta-liminal"])
engine = CosmosMetaLiminalIntegration()  # 내부에서 Echo와 레지스트리 참조


@router.get("/status")
def status():
    return {
        "liminal_state": manager.get_state(),
        "response_profile": manager.response_profile(),
        "signatures": registry.list_signatures(),
    }


@router.post("/transition")
def transition(payload: dict):
    text = payload.get("text", "")
    mode = payload.get("mode", "auto")
    result = engine.test_transition(text=text, mode=mode)
    return {"liminal_state": manager.get_state(), **result}


@router.post("/cross-session")
def cross_session(payload: dict):
    prompt = payload.get("prompt", "")

    # Aurora → CosmicMirror → InfiniteObserver → Final 체인 실행
    aurora = registry.get_signature("Aurora")
    mirror = registry.get_signature("CosmicMirror")
    observer = registry.get_signature("InfiniteObserver")

    if not (aurora and mirror and observer):
        return {"error": "시그니처 로드 실패"}

    aurora_reply = aurora.respond_to(prompt)
    cosmic_reflection = mirror.respond_to(aurora_reply)
    infinite_observation = observer.respond_to(cosmic_reflection)
    final_synthesis = aurora.synthesize(
        [aurora_reply, cosmic_reflection, infinite_observation], mode="cosmos-cross"
    )

    # 공명 점수 계산
    resonance = resonance_score(
        aurora_reply, cosmic_reflection, infinite_observation, final_synthesis
    )

    return {
        "state": manager.get_state(),
        "resonance": resonance,
        "prompt": prompt,
        "aurora_reply": aurora_reply,
        "cosmic_reflection": cosmic_reflection,
        "infinite_observation": infinite_observation,
        "final_synthesis": final_synthesis,
    }
