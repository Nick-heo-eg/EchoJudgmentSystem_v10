#!/usr/bin/env python3
"""
P2: Spec→Test→Code 루프 - 테스트 선행 스캐폴드
새 기능 개발 시 테스트부터 생성하는 자동화 도구
"""
import sys
import pathlib
import textwrap
from datetime import datetime


def create_test_file(name: str, category: str = "unit") -> pathlib.Path:
    """테스트 파일 템플릿 생성"""
    test_dir = pathlib.Path("tests") / category
    test_dir.mkdir(parents=True, exist_ok=True)

    test_file = test_dir / f"test_{name}.py"

    template = f'''"""
Test specification for {name}
Generated: {datetime.now().isoformat()}
Category: {category}

Following Spec→Test→Code methodology:
1. Specification (this docstring)
2. Test cases (below)
3. Minimal implementation (separate file)
"""
import pytest
from typing import Any
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class Test{name.title().replace('_', '')}Spec:
    """
    SPECIFICATION:
    - [ ] TODO: Define what {name} should do
    - [ ] TODO: Define input/output contract
    - [ ] TODO: Define error conditions
    - [ ] TODO: Define performance requirements
    """
    
    def test_{name}_basic_functionality(self):
        """
        Given: <precondition>
        When:  <action> 
        Then:  <expected result>
        """
        # TODO: Replace with actual test implementation
        assert True, "Replace this with real test logic"
    
    def test_{name}_error_handling(self):
        """
        Given: Invalid input
        When:  Function is called
        Then:  Appropriate error is raised
        """
        # TODO: Test error conditions
        pytest.skip("Not implemented yet")
    
    def test_{name}_performance(self):
        """
        Given: Normal input
        When:  Function executes
        Then:  Meets performance requirements
        """
        # TODO: Add performance benchmarks
        pytest.skip("Performance test not implemented")

# Integration test placeholder
class Test{name.title().replace('_', '')}Integration:
    """Integration tests for {name}"""
    
    def test_{name}_integration(self):
        """Test {name} in realistic usage scenario"""
        pytest.skip("Integration test not implemented")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
'''

    test_file.write_text(template.strip() + "\n")
    return test_file


def create_implementation_stub(name: str, module_path: str = None) -> pathlib.Path:
    """최소 구현 스텁 생성"""
    if module_path:
        impl_file = pathlib.Path(module_path)
        impl_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        impl_file = pathlib.Path("src") / f"{name}.py"
        impl_file.parent.mkdir(parents=True, exist_ok=True)

    template = f'''"""
{name} implementation
Generated: {datetime.now().isoformat()}

This is a minimal implementation stub.
Implement functionality to make tests pass.
"""

def main():
    """Main entry point for {name}"""
    raise NotImplementedError("TODO: Implement {name} functionality")

class {name.title().replace('_', '')}:
    """Main class for {name}"""
    
    def __init__(self):
        self.initialized = True
    
    def process(self, data):
        """Process data - replace with actual logic"""
        raise NotImplementedError("TODO: Implement process method")

if __name__ == "__main__":
    main()
'''

    impl_file.write_text(template.strip() + "\n")
    return impl_file


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python scaffold_feature.py <feature_name> [category] [module_path]"
        )
        print(
            "Example: python scaffold_feature.py user_auth integration src/auth/user_auth.py"
        )
        sys.exit(1)

    feature_name = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else "unit"
    module_path = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"🧪 Creating Spec→Test→Code scaffold for '{feature_name}'")

    # 1. Create test file first (Spec→Test)
    test_file = create_test_file(feature_name, category)
    print(f"✅ Test created: {test_file}")

    # 2. Create implementation stub (→Code)
    impl_file = create_implementation_stub(feature_name, module_path)
    print(f"✅ Implementation stub: {impl_file}")

    print(
        f"""
🚀 Next steps:
1. Edit {test_file} - Fill in specifications and test cases
2. Run: pytest {test_file} -v (should fail initially)
3. Edit {impl_file} - Implement minimal functionality
4. Run: pytest {test_file} -v (should pass)
5. Refactor and iterate

📝 Remember:
- Red → Green → Refactor cycle
- Write failing tests first
- Implement minimal code to pass tests
- Refactor when tests are green
"""
    )


if __name__ == "__main__":
    main()
