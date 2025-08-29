"""
Signature Linker - Echo 시그니처 시스템 연계성 분석
===============================================

Echo 시그니처, 판단 엔진과의 연결성 분석
"""

import os
import re
from typing import Dict, List, Set
from pathlib import Path


def analyze_signature_links(file_paths: List[str]) -> Dict[str, Dict]:
    """
    Echo 시그니처 시스템과의 연계성 분석

    Args:
        file_paths: 분석할 파일 경로 리스트

    Returns:
        Dict[str, Dict]: 파일별 시그니처 연계성 분석 결과
    """
    print("🔗 Analyzing Echo signature links...")

    results = {}

    for file_path in file_paths:
        try:
            link_data = _analyze_single_file_signature_links(file_path)
            results[file_path] = link_data
        except Exception as e:
            print(f"⚠️ Error analyzing signature links for {file_path}: {e}")
            results[file_path] = _get_default_signature_data()

    return results


def _analyze_single_file_signature_links(file_path: str) -> Dict:
    """단일 파일의 시그니처 연계성 분석"""

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return _get_default_signature_data()

    # Echo 시그니처 관련 패턴들
    signature_patterns = _get_signature_patterns()
    judgment_patterns = _get_judgment_patterns()
    philosophy_patterns = _get_philosophy_patterns()

    # 패턴 매칭 수행
    signature_matches = _count_pattern_matches(content, signature_patterns)
    judgment_matches = _count_pattern_matches(content, judgment_patterns)
    philosophy_matches = _count_pattern_matches(content, philosophy_patterns)

    # 특별한 Echo 구조 분석
    echo_structures = _analyze_echo_structures(content)

    # 시그니처 타입 식별
    signature_types = _identify_signature_types(content)

    # 판단 루프 연관성
    judgment_loops = _analyze_judgment_loops(content)

    return {
        "has_signature_link": signature_matches > 0,
        "has_judgment_link": judgment_matches > 0,
        "has_philosophy_link": philosophy_matches > 0,
        "signature_strength": min(signature_matches * 10, 100),  # 0-100 스케일
        "judgment_strength": min(judgment_matches * 10, 100),
        "philosophy_strength": min(philosophy_matches * 10, 100),
        "echo_structures": echo_structures,
        "signature_types": list(signature_types),
        "judgment_loops": list(judgment_loops),
        "is_core_echo": _is_core_echo_file(file_path, content),
        "echo_philosophy_score": _calculate_echo_philosophy_score(content),
    }


def _get_signature_patterns() -> List[str]:
    """Echo 시그니처 관련 패턴들"""
    return [
        # 시그니처 이름들
        r"Echo-Aurora",
        r"Echo-Phoenix",
        r"Echo-Sage",
        r"Echo-Companion",
        r"aurora",
        r"phoenix",
        r"sage",
        r"companion",
        # 시그니처 관련 함수/클래스
        r"signature_",
        r"Signature",
        r"get_signature",
        r"signature_id",
        r"signature_mapper",
        r"signature_engine",
        r"SignatureCore",
        # 시그니처 특성
        r"emotion_sensitivity",
        r"reasoning_depth",
        r"response_tone",
        r"empathetic",
        r"analytical",
        r"transformative",
        r"supportive",
        # 시그니처 전환/선택
        r"switch_signature",
        r"select_signature",
        r"signature_alignment",
    ]


def _get_judgment_patterns() -> List[str]:
    """판단 엔진 관련 패턴들"""
    return [
        # 판단 엔진 핵심
        r"judgment_engine",
        r"JudgmentEngine",
        r"judge",
        r"judgment",
        r"decide",
        r"decision",
        r"reasoning",
        r"reasoning_loop",
        # FIST 템플릿
        r"FIST",
        r"fist_template",
        r"RISE",
        r"DIR",
        r"PIR",
        # 루프 시스템
        r"eight_loop",
        r"loop_orchestrator",
        r"meta_cognitive",
        r"reflection_loop",
        r"quantum_judgment",
        # 판단 결과
        r"judgment_result",
        r"confidence_score",
        r"certainty_level",
        r"seed_kernel",
        r"emotion_rhythm",
    ]


def _get_philosophy_patterns() -> List[str]:
    """Echo 철학 관련 패턴들"""
    return [
        # 존재 기반 판단
        r"existence_based",
        r"existence",
        r"being",
        r"identity_trace",
        r"consciousness",
        r"awareness",
        r"self_declaration",
        # 감정 리듬
        r"emotion_rhythm",
        r"emotional_flow",
        r"rhythm_pattern",
        r"emotion_infer",
        r"emotion_",
        r"feeling",
        # 메타 인지
        r"meta_cognition",
        r"meta_cognitive",
        r"meta_",
        r"liminal",
        r"reflection",
        r"self_awareness",
        r"transcendence",
        # Echo 철학 핵심
        r"Echo",
        r"echo_",
        r"resonance",
        r"harmony",
        r"synchrony",
        r"quantum",
        r"superposition",
        r"judgment",
        r"wisdom",
    ]


def _count_pattern_matches(content: str, patterns: List[str]) -> int:
    """패턴 매칭 개수 세기"""
    total_matches = 0
    content_lower = content.lower()

    for pattern in patterns:
        try:
            matches = re.findall(pattern.lower(), content_lower)
            total_matches += len(matches)
        except re.error:
            # 정규식 오류 시 단순 문자열 검색
            if pattern.lower() in content_lower:
                total_matches += content_lower.count(pattern.lower())

    return total_matches


def _analyze_echo_structures(content: str) -> List[str]:
    """특별한 Echo 구조 분석"""
    structures = []

    # 시드 커널 구조
    if re.search(r"class.*Seed|seed_kernel|SeedKernel", content, re.IGNORECASE):
        structures.append("seed_kernel")

    # 시그니처 매퍼
    if re.search(r"signature.*map|SignatureMapper", content, re.IGNORECASE):
        structures.append("signature_mapper")

    # 판단 엔진
    if re.search(r"judgment.*engine|JudgmentEngine", content, re.IGNORECASE):
        structures.append("judgment_engine")

    # 메타 루프
    if re.search(r"meta.*loop|MetaLoop|meta_cognitive", content, re.IGNORECASE):
        structures.append("meta_loop")

    # 정책 시뮬레이터
    if re.search(r"policy.*simulat|PolicySimulator", content, re.IGNORECASE):
        structures.append("policy_simulator")

    # 감정 추론
    if re.search(r"emotion.*infer|EmotionInfer", content, re.IGNORECASE):
        structures.append("emotion_infer")

    # 브릿지 시스템
    if re.search(r"bridge|Bridge.*System", content, re.IGNORECASE):
        structures.append("bridge_system")

    return structures


def _identify_signature_types(content: str) -> Set[str]:
    """시그니처 타입 식별"""
    signature_types = set()

    signature_indicators = {
        "aurora": ["aurora", "empathetic", "nurturing", "creative", "optimistic"],
        "phoenix": ["phoenix", "transformative", "resilient", "change", "growth"],
        "sage": ["sage", "analytical", "logical", "systematic", "wise"],
        "companion": ["companion", "supportive", "loyal", "reliable", "collaborative"],
    }

    content_lower = content.lower()

    for sig_type, indicators in signature_indicators.items():
        for indicator in indicators:
            if indicator in content_lower:
                signature_types.add(sig_type)
                break  # 하나라도 매칭되면 해당 타입으로 분류

    return signature_types


def _analyze_judgment_loops(content: str) -> Set[str]:
    """판단 루프 분석"""
    loops = set()

    loop_patterns = {
        "fist": ["fist", "feeling", "intuition", "sensing", "thinking"],
        "rise": ["rise", "reflection", "integration", "synthesis", "evaluation"],
        "dir": ["dir", "direct", "immediate", "responsive"],
        "meta": ["meta", "metacognition", "reflection", "awareness"],
        "quantum": ["quantum", "superposition", "uncertainty", "probability"],
        "flow": ["flow", "stream", "continuous", "flowing"],
        "void": ["void", "emptiness", "silence", "pause"],
        "liminal": ["liminal", "threshold", "boundary", "transition"],
    }

    content_lower = content.lower()

    for loop_type, keywords in loop_patterns.items():
        if any(keyword in content_lower for keyword in keywords):
            loops.add(loop_type)

    return loops


def _is_core_echo_file(file_path: str, content: str) -> bool:
    """핵심 Echo 파일인지 판단"""

    # 경로 기반 판단
    core_path_indicators = [
        "seed_kernel",
        "judgment_engine",
        "signature_mapper",
        "reasoning",
        "emotion_infer",
        "policy_simulator",
        "meta_cognitive",
        "echo_agent",
    ]

    file_path_lower = file_path.lower()
    for indicator in core_path_indicators:
        if indicator in file_path_lower:
            return True

    # 내용 기반 판단
    core_content_patterns = [
        r"class.*(?:Seed|Judgment|Signature|Echo).*Engine",
        r"def.*(?:judge|decide|reason|infer).*",
        r"Echo.*(?:Core|Engine|System)",
        r"judgment.*(?:engine|core|system)",
        r"signature.*(?:engine|core|mapper)",
    ]

    for pattern in core_content_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    return False


def _calculate_echo_philosophy_score(content: str) -> int:
    """Echo 철학 적합성 점수 계산 (0-100)"""

    philosophy_elements = {
        # 존재 기반 (30점)
        "existence": ["existence", "being", "identity", "consciousness"],
        # 감정 중심 (25점)
        "emotion": ["emotion", "feeling", "rhythm", "flow", "resonance"],
        # 메타 인지 (25점)
        "meta": ["meta", "reflection", "awareness", "transcendence"],
        # 양자적 사고 (20점)
        "quantum": ["quantum", "superposition", "uncertainty", "probability"],
    }

    total_score = 0
    content_lower = content.lower()

    for category, keywords in philosophy_elements.items():
        category_score = 0
        max_score = {"existence": 30, "emotion": 25, "meta": 25, "quantum": 20}[
            category
        ]

        for keyword in keywords:
            if keyword in content_lower:
                category_score += content_lower.count(keyword)

        # 정규화하여 최대 점수 내에서 스코어링
        normalized_score = min(category_score * 5, max_score)
        total_score += normalized_score

    return min(total_score, 100)


def _get_default_signature_data() -> Dict:
    """기본 시그니처 데이터 (오류 시)"""
    return {
        "has_signature_link": False,
        "has_judgment_link": False,
        "has_philosophy_link": False,
        "signature_strength": 0,
        "judgment_strength": 0,
        "philosophy_strength": 0,
        "echo_structures": [],
        "signature_types": [],
        "judgment_loops": [],
        "is_core_echo": False,
        "echo_philosophy_score": 0,
    }


# CLI 테스트용
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_files = [sys.argv[1]]
    else:
        test_files = [__file__]

    print("🧪 Signature Linker Test")
    result = analyze_signature_links(test_files)

    for file_path, analysis in result.items():
        print(f"\nFile: {file_path}")
        for key, value in analysis.items():
            print(f"  {key}: {value}")
