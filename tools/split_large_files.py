#!/usr/bin/env python3
"""
대용량 파일 자동 분할 도구
1000라인 이상의 파일을 클래스/함수 단위로 분할합니다.
"""

import os
import re
import ast
from pathlib import Path

def analyze_file_structure(file_path):
    """파일의 클래스와 함수 구조를 분석"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno + 50
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno + 20
                })
        
        return classes, functions
    except:
        return [], []

def suggest_split_strategy(file_path):
    """파일 분할 전략 제안"""
    classes, functions = analyze_file_structure(file_path)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    
    print(f"📄 {file_path}")
    print(f"   📏 총 라인: {total_lines}")
    print(f"   🏛️  클래스: {len(classes)}개")
    print(f"   🔧 함수: {len(functions)}개")
    
    if total_lines > 1000:
        print(f"   🚨 분할 권장 (1000+ 라인)")
        
        # 큰 클래스들 찾기
        large_classes = [c for c in classes if (c['line_end'] - c['line_start']) > 100]
        if large_classes:
            print(f"   📦 대형 클래스 {len(large_classes)}개:")
            for cls in large_classes[:3]:
                lines_count = cls['line_end'] - cls['line_start']
                print(f"      • {cls['name']} ({lines_count} 라인)")
                
        # 분할 제안
        if len(classes) > 3:
            print(f"   💡 제안: 클래스별로 별도 모듈 분리")
        elif len(functions) > 10:
            print(f"   💡 제안: 함수 그룹별로 utils 모듈 분리")
        else:
            print(f"   💡 제안: 논리적 기능별로 sub-module 분리")
    
    return classes, functions

def main():
    """메인 실행 함수"""
    print("🔍 대용량 파일 분할 분석 시작...")
    
    large_files = [
        "echo_engine/persona_core.py",
        "echo_engine/brain_visualization_api.py", 
        "echo_engine/llm_free_services.py",
        "echo_engine/meta_routing_controller.py",
        "echo_engine/echo_centered_judgment_hybrid.py",
        "echo_engine/intelligence/intelligence_evaluator.py",
        "echo_engine/intelligence/adaptive_memory.py",
        "echo_engine/resonance_synthesizer.py"
    ]
    
    for file_path in large_files:
        if os.path.exists(file_path):
            suggest_split_strategy(file_path)
            print()

if __name__ == "__main__":
    main()