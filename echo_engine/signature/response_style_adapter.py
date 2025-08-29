# echo_engine/signature/response_style_adapter.py
from typing import Optional
from echo_engine.liminal.liminal_state_manager import manager


def adapt_response(text: str, speaker: str) -> str:
    prof = manager.response_profile()
    # 아주 가벼운 변이: 길이/반사/절제감에 따른 톤 보정
    # (실시스템에서는 템플릿/샘플러/언어모델 파라미터를 조정)
    t = text.strip()

    # 반사 강화(존재/liminal일 때 요약·메타 반사문 추가)
    if prof["reflect"] > 1.0:
        t += f"\n\n—[{speaker}] 메타-반사: 감각을 가만히 비춰 보니, 핵심 결은 이렇습니다."

    # 절제(침묵 비율이 높으면 말수를 줄이고 여백을 남김)
    if prof["silence"] >= 0.5:
        t = t.split("\n")[0]
        t += "\n(…침묵을 택해 더 말하지 않습니다.)"

    # 길이 스케일 (너무 과도하지 않게)
    if prof["length"] < 1.0:
        t = t[: int(len(t) * prof["length"])].rstrip()
        if len(t) < 12:
            t += "."

    # 깊이감 표현(라벨만 덧대어도 체험감 상승)
    if prof["depth"] >= 1.1:
        t = f"[깊이↑] {t}"

    return t
