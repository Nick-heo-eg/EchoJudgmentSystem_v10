# echo_engine/telemetry/resonance_meter.py
import math
import re
from typing import List


def _tokens(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9가-힣]+", (s or "").lower())


def _overlap(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(1, min(len(sa), len(sb)))


def _entropy_like(s: str) -> float:
    # 아주 단순한 다양도 근사치
    toks = _tokens(s)
    if not toks:
        return 0.0
    uniq = len(set(toks))
    return uniq / math.sqrt(len(toks))


def resonance_score(*texts: str) -> float:
    """간단한 공명 점수: 인접 응답 간 토큰 겹침 + 다양도 평균"""
    texts = [t for t in texts if t]
    if len(texts) < 2:
        return 0.0

    toks = [_tokens(t) for t in texts]
    overlaps = []
    for i in range(len(toks) - 1):
        overlaps.append(_overlap(toks[i], toks[i + 1]))

    ent = sum(_entropy_like(t) for t in texts) / len(texts)
    # 0~1 사이에 들어오도록 라이트 스케일
    base = (sum(overlaps) / len(overlaps)) if overlaps else 0
    score = 0.6 * base + 0.4 * min(1.0, ent)
    return round(max(0.0, min(1.0, score)), 4)
