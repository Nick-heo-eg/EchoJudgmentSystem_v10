#!/usr/bin/env python3
"""
🧹 Text Sanitization Utilities
UTF-8 인코딩 오류 방지 및 텍스트 정규화 도구

주요 기능:
1. 고아 서러게이트(lone surrogate) 제거
2. 안전한 파일명 생성
3. 텍스트 정규화 및 안전화
4. WSL/Windows 경로 호환성
"""

import unicodedata
import re
from typing import Optional


def strip_surrogates(s: str) -> str:
    """
    고아 서러게이트 문자 제거
    D800-DFFF 범위의 서러게이트 코드포인트를 모두 제거
    """
    if not s:
        return s

    try:
        # 서러게이트 범위(0xD800-0xDFFF) 문자 제거
        return "".join(ch for ch in s if not (0xD800 <= ord(ch) <= 0xDFFF))
    except Exception:
        # 예외 발생 시 바이트 레벨에서 처리
        return s.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


def normalize_safe(s: str) -> str:
    """
    안전한 텍스트 정규화
    NFC 정규화 → 서러게이트 제거 → UTF-8 재구성
    """
    if not s:
        return s

    try:
        # 1단계: NFC 정규화
        s = unicodedata.normalize("NFC", s)

        # 2단계: 서러게이트 제거
        s = strip_surrogates(s)

        # 3단계: UTF-8 재구성 (깨지는 건 대체문자로)
        s = s.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

        return s

    except Exception:
        # 최후 수단: 강제 UTF-8 변환
        try:
            return (
                str(s)
                .encode("utf-8", errors="replace")
                .decode("utf-8", errors="replace")
            )
        except Exception:
            return "safe_text"


def safe_filename(name: str, allow_korean: bool = True, max_len: int = 80) -> str:
    """
    안전한 파일명 생성
    WSL/Windows 환경에서 안전하게 사용할 수 있는 파일명으로 변환

    Args:
        name: 원본 파일명
        allow_korean: 한글 허용 여부
        max_len: 최대 길이

    Returns:
        안전한 파일명
    """
    if not name:
        return "default_file"

    # 1단계: 텍스트 정규화
    name = normalize_safe(name)

    # 2단계: 허용된 문자만 유지
    if allow_korean:
        # 한글, 영문, 숫자, 기본 구두점만 허용
        name = re.sub(r"[^0-9A-Za-z가-힣 _\-\.\(\)\[\]]+", "_", name)
    else:
        # 영문, 숫자, 기본 구두점만 허용
        name = re.sub(r"[^0-9A-Za-z _\-\.\(\)\[\]]+", "_", name)

    # 3단계: 공백 및 특수문자 정리
    name = name.strip().strip(". ")

    # 4단계: 연속 언더스코어 제거
    name = re.sub(r"_+", "_", name)

    # 5단계: 빈 문자열 처리
    if not name:
        name = "project"

    # 6단계: 길이 제한
    return name[:max_len]


def safe_project_name(name: str) -> str:
    """
    프로젝트명을 위한 안전한 이름 생성
    """
    safe_name = safe_filename(name, allow_korean=True, max_len=50)

    # 프로젝트명은 더 엄격하게
    safe_name = re.sub(r"[^\w가-힣_-]", "_", safe_name)

    return safe_name or "echo_project"


def sanitize_user_input(text: str) -> str:
    """
    사용자 입력 텍스트 안전화
    CLI에서 받은 입력을 안전하게 처리
    """
    if not text:
        return ""

    # 1단계: 기본 정규화
    text = normalize_safe(text)

    # 2단계: 제어문자 제거 (개행/탭 제외)
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\t\r")

    # 3단계: 과도한 공백 정리
    text = re.sub(r"\s+", " ", text).strip()

    return text


def safe_file_write(filepath: str, content: str, encoding: str = "utf-8") -> bool:
    """
    안전한 파일 쓰기
    UTF-8 인코딩 오류를 방지하며 파일 저장

    Args:
        filepath: 파일 경로
        content: 파일 내용
        encoding: 인코딩 (기본: utf-8)

    Returns:
        성공 여부
    """
    try:
        # 내용 안전화
        content = normalize_safe(content)

        # 파일 저장 (errors='replace'로 안전하게)
        with open(filepath, "w", encoding=encoding, errors="replace") as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return False


def debug_text_encoding(text: str, label: str = "텍스트") -> None:
    """
    텍스트 인코딩 상태 디버그 출력
    개발/디버깅용 함수
    """
    print(f"🔍 {label} 인코딩 분석:")
    print(f"   길이: {len(text)}")
    print(f"   타입: {type(text)}")

    # 서러게이트 검사
    surrogates = [ch for ch in text if 0xD800 <= ord(ch) <= 0xDFFF]
    if surrogates:
        print(f"   ⚠️ 서러게이트 발견: {len(surrogates)}개")
        for i, ch in enumerate(surrogates[:5]):  # 최대 5개만 표시
            print(f"      {i+1}: {repr(ch)} (U+{ord(ch):04X})")
    else:
        print(f"   ✅ 서러게이트 없음")

    # UTF-8 인코딩 가능성 검사
    try:
        text.encode("utf-8")
        print(f"   ✅ UTF-8 인코딩 가능")
    except UnicodeEncodeError as e:
        print(f"   ❌ UTF-8 인코딩 불가: {e}")


if __name__ == "__main__":
    # 테스트 코드
    test_cases = [
        "에코시스템에 어울리는 신규기능을 개발해보자",
        "Hello World! 안녕하세요~",
        "파일명/특수:문자*테스트",
        "test\udcecfile.py",  # 의도적 서러게이트
    ]

    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"원본: {repr(test)}")
        debug_text_encoding(test, "원본")

        normalized = normalize_safe(test)
        print(f"정규화: {repr(normalized)}")

        filename = safe_filename(test)
        print(f"파일명: {repr(filename)}")
