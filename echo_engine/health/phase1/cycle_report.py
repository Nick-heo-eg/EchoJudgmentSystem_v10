# echo_engine/health/phase1/cycle_report.py
from __future__ import annotations
import os
from typing import Dict, Set, List, Tuple

# graph: {module: set(deps)}
def sccs(graph: Dict[str, Set[str]], nodes: List[str]) -> List[List[str]]:
    index = 0
    indices = {}
    low = {}
    st: List[str] = []
    on = set()
    comps: List[List[str]] = []

    def strong(v: str):
        nonlocal index
        indices[v] = index; low[v] = index; index += 1
        st.append(v); on.add(v)
        for w in graph.get(v, set()):
            if w not in nodes: continue
            if w not in indices:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w)
                comp.append(w)
                if w == v: break
            if len(comp) > 1:
                comps.append(comp)

    for v in nodes:
        if v not in indices:
            strong(v)
    return comps

def find_cycle_paths(graph: Dict[str, Set[str]], comp: List[str], limit: int = 5) -> List[List[str]]:
    # comp 하위에서 단순 DFS로 짧은 사이클 경로를 몇 개 수집
    comp_set = set(comp)
    paths: List[List[str]] = []
    seen_edges = set()

    def dfs(start: str, cur: str, path: List[str]):
        if len(paths) >= limit:
            return
        for nxt in graph.get(cur, set()):
            if nxt not in comp_set:
                continue
            edge = (cur, nxt)
            if edge in seen_edges:
                continue
            if nxt == start and len(path) >= 2:
                paths.append(path + [nxt])
                seen_edges.add(edge)
                if len(paths) >= limit:
                    return
            elif nxt not in path:
                dfs(start, nxt, path + [nxt])

    for v in comp:
        if len(paths) >= limit:
            break
        dfs(v, v, [v])
    return paths