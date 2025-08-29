#!/usr/bin/env python3
"""
🧠 BrainVisualizationAPI 최적화 리다이렉션
기존 brain_visualization_api.py 임포트를 최적화된 버전으로 자동 리다이렉션
"""

# 최적화된 버전으로 자동 리다이렉션
try:
    from .optimized.brainvisualizationapi import *
    print("🚀 BrainVisualizationAPI 최적화 버전 로드됨")
except ImportError:
    print("⚠️ 최적화 버전 로드 실패, 레거시 백업 사용")
    # 레거시 백업에서 복원 (긴급시만)
    import sys
    from pathlib import Path
    legacy_path = Path(__file__).parent / "legacy_backup" / "brain_visualization_api.py"
    
    if legacy_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("legacy_brain_api", legacy_path)
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        # 레거시 모듈의 모든 속성을 현재 모듈로 복사
        for attr_name in dir(legacy_module):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(legacy_module, attr_name)
        
        print("⚠️ 레거시 백업 버전 로드됨 - 성능 최적화되지 않음")

# 메타데이터
__version__ = "10.5-optimized"
__legacy_backup__ = "echo_engine/legacy_backup/brain_visualization_api.py"
__optimization__ = "Modularized and performance optimized"