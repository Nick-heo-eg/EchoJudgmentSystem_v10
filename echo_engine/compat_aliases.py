# -*- coding: utf-8 -*-
"""
호환 별칭 (지연 로딩) - import 시점에만 매핑 적용
무한 import 루프 방지 + 재진입 가드 + 캐시
"""
from __future__ import annotations
import sys
import importlib
import importlib.abc
import importlib.util
import types
from pathlib import Path

# 1) 문자열 매핑만 가진다. 여기서 echo_engine.* 모듈을 import하지 않는다.
ALIASES = {
    # 과거 단일모듈 → 현재 패키지
    "meta_log_writer": "meta.meta_log_writer",  # meta 디렉토리로 수정
    "meta_infection_logger": "echo_engine.meta_infection_logger",
    "resonance_evaluator": "echo_engine.resonance_evaluator",
    "signature_mapper": "echo_engine.signature_mapper",
    "judgment_engine": "echo_engine.judgment_engine",
    "capsule_core": "echo_engine.capsule_core",
    "claude_interface": "echo_engine.claude_interface",
    "completion_metrics": "echo_engine.completion_metrics",
    "emotion_infer": "echo_engine.emotion_infer",
    # 하위 패키지 계열
    "amoeba_manager": "echo_engine.amoeba.amoeba_manager",
    "schemas": "echo_engine.inspectors.asset_value_judger.schemas",
    # 벤더/철자 호환
    "models.judgement": "echo_engine.models.judgement",  # 실제 경로로 수정
    "models.judgment": "echo_engine.models.judgement",  # 철자차 호환
    # echo infection 계열
    "echo_signature_loader": "echo_engine.echo_signature_loader",
    "claude_api_wrapper": "echo_engine.claude_api_wrapper",
    "prompt_mutator": "echo_engine.prompt_mutator",
    "flow_writer": "echo_engine.flow_writer",
    "echo_infection_loop": "echo_engine.echo_infection_loop",
    # meta 계열 추가
    "meta_log": "echo_engine.meta_logger",
    # 추가 확장 (저위험)
    "models": "echo_engine",  # 일부 코드가 models.*로 착각하여 import할 때 우회
    # meta.* 계열 촘촘한 봉합 (저위험 확장)
    "meta.meta_log_writer": "echo_engine.meta_log_writer",
    "meta.meta_logger": "echo_engine.meta_logger",
    "meta.resonance_evaluator": "echo_engine.resonance_evaluator",
    "meta.signature_mapper": "echo_engine.signature_mapper",
}

# 접두사 기반 확장된 별칭 - models.*, world_generator.* 같은 접두사 패턴 대응
PREFIX_ALIASES = {
    "models.": "echo_engine.",
    "world_generator.": "echo_engine.world_generator.",
}


def _load_prefix_aliases_from_env():
    """환경변수에서 접두사 별칭 로드"""
    spec = os.environ.get("ECHO_PREFIX_ALIASES", "").strip()
    # 예: ECHO_PREFIX_ALIASES="src.echo_foundation.:echo_engine.foundation.,resonance.:echo_engine.resonance."
    out = {}
    if spec:
        for pair in spec.split(","):
            if ":" in pair:
                old, new = pair.split(":", 1)
                if old.strip() and new.strip():
                    out[old.strip()] = new.strip()
    return out


_INSTALLED = False
_IN_PROGRESS: set[str] = set()

# Stub 모듈 시스템 (환경변수 기반 + 기본 세트)
import os

_DEFAULT_STUBS = {
    "echo_existence_manifest",
    "three_way_existence_mode",
    "claude_continuity_helper",
    "claude_memory_system",
    "main",
    "echo_advanced_main",
    "src.echo_foundation.doctrine",
    "meta_log_writer",  # 자주 실패하는 모듈 추가
}
_ENV_STUBS = {
    s.strip() for s in os.environ.get("ECHO_STUB_MODULES", "").split(",") if s.strip()
}
_STUBS = _DEFAULT_STUBS | _ENV_STUBS


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """개념 모듈용 Stub Finder"""

    def find_spec(self, fullname, path=None, target=None):
        if fullname in _STUBS and fullname not in _IN_PROGRESS:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        name = module.__name__
        if name in _IN_PROGRESS:
            return
        _IN_PROGRESS.add(name)
        try:
            m = types.ModuleType(name)
            m.__doc__ = "⚠️ Stub module (provided by ECHO_STUB_MODULES)."

            def _missing(*a, **k):
                raise NotImplementedError(
                    f"Stub module '{name}' attribute accessed at runtime"
                )

            m.__getattr__ = lambda _attr: _missing
            sys.modules[name] = m
        finally:
            _IN_PROGRESS.discard(name)


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """지연 로딩 기반 별칭 finder"""

    def find_spec(self, fullname, path, target=None):
        modern = ALIASES.get(fullname)
        if not modern:
            # 접두사 매칭 확인
            for prefix, replacement in PREFIX_ALIASES.items():
                if fullname.startswith(prefix):
                    modern = fullname.replace(prefix, replacement, 1)
                    break
            if not modern:
                return None
        # 루프 방지
        if fullname in _IN_PROGRESS:
            return None
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return None  # default module creation

    def exec_module(self, module):
        fullname = module.__name__
        modern = ALIASES.get(fullname)
        if not modern:
            # 접두사 매칭으로 변환
            for prefix, replacement in PREFIX_ALIASES.items():
                if fullname.startswith(prefix):
                    modern = fullname.replace(prefix, replacement, 1)
                    break
        if not modern or fullname in _IN_PROGRESS:
            return
        _IN_PROGRESS.add(fullname)
        try:
            real = importlib.import_module(modern)
            # alias 이름과 modern 이름 모두 sys.modules에 동일 객체로 고정
            sys.modules[fullname] = real
        finally:
            _IN_PROGRESS.discard(fullname)


def install_compat_aliases() -> None:
    """지연 로딩 기반 별칭 설치 (멱등)"""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    # meta 디렉토리 접근용 path 보강 (루트만 추가; import는 하지 않음)
    project_root = Path(__file__).resolve().parents[1]
    meta_path = project_root / "meta"
    if meta_path.exists() and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # jsonlines 가벼운 Mock (필요 시)
    if "jsonlines" not in sys.modules:
        jl = types.ModuleType("jsonlines")

        class Writer:
            def __init__(self, fp):
                self.fp = fp

            def write(self, obj):
                import json

                self.fp.write(json.dumps(obj) + "\n")

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        class Reader:
            def __init__(self, fp):
                self.fp = fp

            def __iter__(self):
                import json

                for line in self.fp:
                    if line.strip():
                        yield json.loads(line.strip())

        jl.Writer, jl.Reader = Writer, Reader
        jl.open = lambda f, mode="r": (
            Writer(open(f, "w")) if "w" in mode else Reader(open(f, "r"))
        )
        sys.modules["jsonlines"] = jl

    # 환경변수 기반 접두사 별칭 병합
    env_prefix_aliases = _load_prefix_aliases_from_env()
    if env_prefix_aliases:
        PREFIX_ALIASES.update(env_prefix_aliases)

    # meta-path finder 장착 (가장 앞이 아니라, 0~1번째 사이에 얹어도 충분)
    if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _AliasFinder())

    # Stub 로더 추가 (환경변수 기반)
    if not any(isinstance(f, _StubFinder) for f in sys.meta_path):
        sys.meta_path.append(_StubFinder())
