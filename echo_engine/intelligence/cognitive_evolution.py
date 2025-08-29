#!/usr/bin/env python3
"""
🧬 CognitiveEvolution 최적화 리다이렉션
기존 cognitive_evolution.py 임포트를 최적화된 버전으로 자동 리다이렉션
"""

try:
    from .optimized.cognitiveevolutiontracker import *
    print("🚀 CognitiveEvolution 최적화 버전 로드됨")
    
except ImportError as e:
    print(f"⚠️ 최적화 버전 로드 실패: {e}")
    # 레거시 백업 사용
    import sys
    from pathlib import Path
    legacy_path = Path(__file__).parent.parent / "legacy_backup" / "cognitive_evolution.py"
    
    if legacy_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("legacy_cognitive", legacy_path)
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        for attr_name in dir(legacy_module):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(legacy_module, attr_name)
        
        print("⚠️ 레거시 백업 버전 로드됨")

__version__ = "10.5-optimized"
__legacy_backup__ = "echo_engine/legacy_backup/cognitive_evolution.py"  
__optimization__ = "Cognitive evolution tracking optimized"