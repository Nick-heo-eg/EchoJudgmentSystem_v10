#!/usr/bin/env python3
"""
🌌 MetaLiminalAutomationFramework 최적화 리다이렉션
기존 meta_liminal_automation_framework.py 임포트를 최적화된 버전으로 자동 리다이렉션
"""

try:
    # 최적화된 5개 모듈로 분할된 버전
    from .optimized.configurationmanagementkit import *
    from .optimized.realtimemonitoringkit import *
    from .optimized.metaliminalautodiscovery import *
    from .optimized.liveconfigmanager import *
    from .optimized.metaliminalautomationframework import *
    
    print("🚀 MetaLiminalAutomationFramework 최적화 버전 로드됨 (5개 모듈)")
    
except ImportError as e:
    print(f"⚠️ 최적화 버전 로드 실패: {e}")
    # 레거시 백업 사용
    import sys
    from pathlib import Path
    legacy_path = Path(__file__).parent / "legacy_backup" / "meta_liminal_automation_framework.py"
    
    if legacy_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("legacy_automation", legacy_path)
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        for attr_name in dir(legacy_module):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(legacy_module, attr_name)
        
        print("⚠️ 레거시 백업 버전 로드됨")

__version__ = "10.5-optimized"
__modules__ = [
    "configurationmanagementkit.py",
    "realtimemonitoringkit.py", 
    "metaliminalautodiscovery.py",
    "liveconfigmanager.py",
    "metaliminalautomationframework.py"
]
__optimization__ = "Split into 5 specialized automation modules"