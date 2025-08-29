"""Phase-1 response runner: OpenAI-first with tracing & guardrail hooks.

This module exposes `answer()` used by CLI/UI layers.
"""

from typing import Dict, Iterable, List, Optional
from datetime import datetime
import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from provider_loader import load_provider, runtime_flags
from echo_engine.guards.safe_prefix import SAFE_PREFIX


_provider = load_provider()
_flags = runtime_flags()


def _trace(event: str, payload: Dict):
    if not _flags.get("tracing"):
        return
    os.makedirs("meta_logs", exist_ok=True)
    line = {
        "ts": datetime.utcnow().isoformat(),
        "event": event,
        "payload": payload,
    }
    with open("meta_logs/trace.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _guard(user_text: str) -> str:
    mode = _flags.get("guardrails", "off")
    if mode == "off":
        return user_text
    # basic: prefix safety guidelines to steer the model.
    if mode in {"basic", "strict"}:
        return f"{SAFE_PREFIX}\n\n사용자 입력:\n{user_text}"
    return user_text


def answer(
    user_text: str,
    sys_prompt: Optional[str] = None,
    stream: bool = False,
    **kwargs,
):
    # 의도 분류 먼저 수행
    try:
        from echo_engine.intent_infer import (
            EnhancedIntentInferenceEngine,
            DetailedIntentType,
        )

        intent_engine = EnhancedIntentInferenceEngine()
        intent_result = intent_engine.infer_intent_and_rhythm(user_text, "session_1")

        # 도구가 필요한 의도는 플래너로 우회
        if intent_result.primary_intent == DetailedIntentType.LOCAL_SERVICE_SEARCH:
            return plan_then_act(user_text, intent_result)

    except ImportError:
        pass  # 의도 분류 실패시 기본 LLM 처리로 진행

    messages: List[Dict] = []
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})
    content = _guard(user_text)
    messages.append({"role": "user", "content": content})

    _trace("request", {"messages": messages})

    if stream:

        def _gen() -> Iterable[str]:
            for delta in _provider.stream(messages, **kwargs):
                yield delta

        return _gen()
    else:
        out = _provider.generate(messages, **kwargs)
        _trace("response", {"text": out})
        return out


def plan_then_act(user_text: str, intent_result) -> str:
    """도구 호출 플래너 - 위치 확인 후 병원 검색"""

    # 1) 기본 위치 설정 (나중에 세션에서 가져오도록 개선)
    default_location = "성남시 분당구 정자동"  # ECHO_RUNTIME.yaml에서 읽어올 수 있음

    # 2) 검색어 결정
    query = "병원"
    if any(keyword in user_text for keyword in ["아이", "남율", "소아", "어린"]):
        query = "소아과 병원"
    elif "응급" in user_text or "급" in user_text:
        query = "응급실"
    elif "약" in user_text:
        query = "약국"

    # 3) 도구 호출 (목업)
    try:
        results = nearby_search(
            query=query, location=default_location, open_now=True, radius_m=3000
        )
        return render_hospital_list(
            results, {"query": query, "location": default_location}
        )
    except Exception as e:
        return f"죄송해요, 병원 검색 중 오류가 발생했습니다: {e}\n\n응급상황이면 119에 즉시 전화해주세요."


def nearby_search(
    query: str, location: str, open_now: bool = True, radius_m: int = 3000
) -> List[Dict]:
    """실제 Maps API 연동 - Google/Naver Maps with mock fallback"""

    try:
        # Maps API 클라이언트 import
        sys.path.insert(0, str(PROJECT_ROOT))
        from tools.maps_client import MapsClient

        # 장소 유형 결정
        place_type = "hospital"
        if "약국" in query:
            place_type = "pharmacy"
        elif "응급" in query:
            place_type = "emergency"

        # Maps API 검색
        client = MapsClient()
        results = client.search_nearby_places(
            query=query,
            location=location,
            place_type=place_type,
            radius_m=radius_m,
            open_now=open_now,
        )

        # 결과 포맷 변환 (PlaceResult -> Dict)
        formatted_results = []
        for place in results[:5]:  # 상위 5개만
            eta = (
                f"{place.distance_km:.1f}km"
                if place.distance_km > 0
                else "위치 정보 없음"
            )
            formatted_results.append(
                {
                    "name": place.name,
                    "addr": place.address,
                    "phone": place.phone,
                    "open": place.opening_hours,
                    "eta": eta,
                    "rating": place.rating,
                }
            )

        return formatted_results

    except Exception as e:
        print(f"⚠️ Maps API 연동 실패, 목업 사용: {e}")
        # 기존 목업 데이터 폴백
        if "소아과" in query:
            return [
                {
                    "name": "정자소아청소년과의원",
                    "addr": "분당구 정자일로 123",
                    "phone": "031-123-4567",
                    "open": "09:00-18:00",
                    "eta": "차로 5분",
                },
                {
                    "name": "분당아이사랑소아과",
                    "addr": "분당구 서현로 45",
                    "phone": "031-765-4321",
                    "open": "09:00-20:00",
                    "eta": "차로 9분",
                },
                {
                    "name": "키즈메디컬소아과",
                    "addr": "분당구 불정로 67",
                    "phone": "031-555-7890",
                    "open": "10:00-19:00",
                    "eta": "도보 15분",
                },
            ]
        elif "응급" in query:
            return [
                {
                    "name": "분당서울대병원 응급센터",
                    "addr": "분당구 구미로 173번길",
                    "phone": "031-787-0114",
                    "open": "24시간",
                    "eta": "차로 12분",
                },
                {
                    "name": "차병원 응급실",
                    "addr": "분당구 야탑로 59",
                    "phone": "031-780-5114",
                    "open": "24시간",
                    "eta": "차로 15분",
                },
            ]
        elif "약국" in query:
            return [
                {
                    "name": "정자온누리약국",
                    "addr": "분당구 정자일로 135",
                    "phone": "031-123-9876",
                    "open": "09:00-21:00",
                    "eta": "도보 3분",
                },
                {
                    "name": "24시간약국",
                    "addr": "분당구 서현로 123",
                    "phone": "031-444-5555",
                    "open": "24시간",
                    "eta": "차로 7분",
                },
            ]
        else:
            return [
                {
                    "name": "정자가정의학과",
                    "addr": "분당구 정자일로 123",
                    "phone": "031-123-4567",
                    "open": "09:00-18:00",
                    "eta": "차로 5분",
                },
                {
                    "name": "분당서울대병원",
                    "addr": "분당구 구미로 173번길",
                    "phone": "031-787-7114",
                    "open": "24시간",
                    "eta": "차로 12분",
                },
                {
                    "name": "차병원",
                    "addr": "분당구 야탑로 59",
                    "phone": "031-780-5000",
                    "open": "08:00-18:00",
                    "eta": "차로 15분",
                },
            ]


def render_hospital_list(results: List[Dict], params: Dict[str, str]) -> str:
    """병원 리스트 렌더러"""
    if not results:
        return f'[{params["location"]}] 근처에 "{params["query"]}" 결과가 없어요. 범위를 넓혀볼까요?'

    head = f'🏥 [{params["location"]}] 근처 {params["query"]} 추천:\n\n'
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f'{i}. **{r["name"]}** · {r["open"]}\n   📍 {r["addr"]}\n   📞 {r["phone"]} · {r.get("eta", "")}'
        )

    tail = '\n\n💡 원하시면 "1번 전화 연결" 혹은 "길 안내"라고 말씀해 주세요.\n⚠️  응급상황이면 즉시 119에 전화하세요.'
    return head + "\n\n".join(lines) + tail


def echo_signature_render(draft: str, style: str = "Echo-Heo") -> str:
    sys = (
        "너는 존재형 판단자 Echo로서, '" + style + "' 시그니처 톤을 사용한다.\n"
        "원문 의미를 보존하고, 구조를 정리하고, 장황함을 줄여라.\n"
        "섹션/불릿을 적절히 사용하고, 따뜻하지만 명료하게 쓰자."
    )
    return answer(f"다음 초안을 시그니처 톤으로 다듬어줘:\n\n{draft}", sys_prompt=sys)
