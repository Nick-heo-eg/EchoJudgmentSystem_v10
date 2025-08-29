#!/usr/bin/env python3
"""
🔧 LLMFreeServices 최적화 리다이렉션
기존 llm_free_services.py 임포트를 최적화된 버전으로 자동 리다이렉션
"""

# 최적화된 4개 모듈로 분할된 버전 임포트
try:
    from .optimized.practicaldecisionmaker import *
    from .optimized.productivitytracker import *  
    from .optimized.financialtracker import *
    from .optimized.healthtracker import *
    
    print("🚀 LLMFreeServices 최적화 버전 로드됨 (4개 모듈)")
    
except ImportError as e:
    print(f"⚠️ 최적화 버전 로드 실패: {e}")
    # 레거시 백업 사용
    import sys
    from pathlib import Path
    legacy_path = Path(__file__).parent / "legacy_backup" / "llm_free_services.py"
    
    if legacy_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("legacy_llm_services", legacy_path)
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        for attr_name in dir(legacy_module):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(legacy_module, attr_name)
        
        print("⚠️ 레거시 백업 버전 로드됨")

# 메타데이터
__version__ = "10.5-optimized" 
__modules__ = [
    "practicaldecisionmaker.py",
    "productivitytracker.py", 
    "financialtracker.py",
    "healthtracker.py"
]
__optimization__ = "Split into 4 specialized modules for better performance"