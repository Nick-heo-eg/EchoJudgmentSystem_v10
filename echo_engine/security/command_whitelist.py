#!/usr/bin/env python3
"""
🛡️ Echo IDE Command Whitelist - 실행 명령 화이트리스트
보안 기능: 허용된 명령만 실행, 위험한 명령 차단
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandRule:
    """명령 규칙"""

    pattern: str
    allowed: bool
    reason: str
    timeout: int = 30
    max_output_size: int = 1024 * 1024  # 1MB


class CommandWhitelist:
    """🛡️ 명령 화이트리스트"""

    def __init__(self):
        self.rules = [
            # 🚫 위험한 Python 인젝션 (최우선 차단)
            CommandRule(r"python.*-c.*os\.system", False, "Python os.system 인젝션", 0),
            CommandRule(
                r"python.*-c.*subprocess", False, "Python subprocess 인젝션", 0
            ),
            CommandRule(r"python.*-c.*exec.*rm", False, "Python exec 인젝션", 0),
            # ✅ 허용된 Python 관련 명령들
            CommandRule(r"^python3?\s+.*\.py", True, "Python 스크립트 실행", 60),
            CommandRule(r"^python3?\s+-c\s+", True, "Python 코드 실행", 30),
            CommandRule(
                r"^python3?\s+-m\s+(pip|pytest|unittest)", True, "Python 모듈 실행", 120
            ),
            CommandRule(r"^pytest\s+", True, "테스트 실행", 60),
            CommandRule(r"^uv\s+", True, "UV 패키지 관리자", 60),
            CommandRule(r"^pipenv\s+", True, "Pipenv 명령", 60),
            # ✅ 안전한 시스템 명령들
            CommandRule(r"^echo\s+", True, "Echo 명령", 5),
            # ✅ 안전한 파일 시스템 명령들
            CommandRule(r"^ls\s+[^./]*$", True, "디렉토리 목록 (상대경로 금지)", 10),
            CommandRule(r"^ls\s+\.\s*$", True, "현재 디렉토리 목록", 10),
            CommandRule(r"^cat\s+[^|;&]+$", True, "파일 읽기", 10),
            CommandRule(r"^head\s+", True, "파일 헤더 읽기", 10),
            CommandRule(r"^tail\s+", True, "파일 끝 읽기", 10),
            CommandRule(r"^wc\s+", True, "단어/줄 수 계산", 10),
            CommandRule(r"^grep\s+", True, "텍스트 검색", 15),
            CommandRule(r"^find\s+\.\s+", True, "워크스페이스 내 파일 검색", 15),
            # ✅ 안전한 개발 도구들
            CommandRule(r"^git\s+(status|log|diff|show)", True, "Git 조회 명령", 15),
            CommandRule(r"^make\s+(help|clean|build|test)", True, "Make 빌드 명령", 60),
            CommandRule(r"^npm\s+(install|test|run)", True, "NPM 명령", 120),
            CommandRule(r"^node\s+.*\.js$", True, "Node.js 스크립트", 30),
            # 🚫 위험한 명령들 (높은 우선순위)
            CommandRule(r"\.\./|/\.\./|~/", False, "경로 탈출 시도 금지", 0),
            CommandRule(
                r".*;.*rm\s+-rf", False, "명령 체이닝을 통한 재귀 삭제 시도", 0
            ),
            CommandRule(r"rm\s+-rf", False, "재귀 삭제 금지", 0),
            CommandRule(r"sudo\s+", False, "관리자 권한 금지", 0),
            CommandRule(r"curl.*\|.*bash", False, "원격 스크립트 실행 금지", 0),
            CommandRule(r"wget.*\|.*sh", False, "원격 스크립트 다운로드 실행 금지", 0),
            CommandRule(r"ssh\s+", False, "SSH 연결 금지", 0),
            CommandRule(r"scp\s+", False, "SCP 파일 전송 금지", 0),
            CommandRule(r"rsync\s+", False, "Rsync 동기화 금지", 0),
            CommandRule(r"^dd\s+", False, "DD 블록 복사 금지", 0),
            CommandRule(r"mkfs\s+", False, "파일시스템 생성 금지", 0),
            CommandRule(r"mount\s+", False, "마운트 금지", 0),
            CommandRule(r"chmod\s+777", False, "전체 권한 부여 금지", 0),
            CommandRule(r"chown\s+", False, "소유권 변경 금지", 0),
            # 🚫 네트워크 위험 명령들
            CommandRule(r"nc\s+", False, "Netcat 금지", 0),
            CommandRule(r"nmap\s+", False, "포트 스캐닝 금지", 0),
            CommandRule(r"telnet\s+", False, "Telnet 연결 금지", 0),
            CommandRule(r"ftp\s+", False, "FTP 연결 금지", 0),
            # 🚫 시스템 정보 수집 제한
            CommandRule(r"ps\s+aux", False, "전체 프로세스 목록 금지", 0),
            CommandRule(r"netstat\s+", False, "네트워크 연결 정보 금지", 0),
            CommandRule(r"ifconfig", False, "네트워크 설정 조회 금지", 0),
            CommandRule(r"/proc/.*", False, "프로세스 정보 접근 금지", 0),
            # 🚫 환경변수/시크릿 덤프
            CommandRule(r"env\s*$", False, "환경변수 덤프 금지", 0),
            CommandRule(r"printenv", False, "환경변수 출력 금지", 0),
            CommandRule(r"echo\s+\$", False, "환경변수 출력 금지", 0),
            # 🚫 파일 프로토콜 악용
            CommandRule(r"file://", False, "file:// 프로토콜 금지", 0),
        ]

    def validate_command(self, command: str) -> Dict[str, Any]:
        """
        명령 검증
        🛡️ B3: exec_cmd 화이트리스트
        """
        command = command.strip()

        if not command:
            return {"allowed": False, "reason": "빈 명령", "rule": None}

        # 명령 정규화 (다중 공백 제거)
        normalized_cmd = re.sub(r"\s+", " ", command)

        # 규칙 매칭 (순서 중요 - 금지 규칙이 먼저)
        for rule in self.rules:
            if re.search(rule.pattern, normalized_cmd, re.IGNORECASE):
                if rule.allowed:
                    logger.info(f"✅ 명령 허용: {command} (규칙: {rule.reason})")
                else:
                    logger.warning(f"🚫 명령 차단: {command} (이유: {rule.reason})")

                return {
                    "allowed": rule.allowed,
                    "reason": rule.reason,
                    "timeout": rule.timeout,
                    "max_output_size": rule.max_output_size,
                    "rule": rule,
                    "command": normalized_cmd,
                }

        # 매칭되지 않은 명령은 기본적으로 차단
        logger.warning(f"🚫 허용되지 않은 명령: {command}")
        return {
            "allowed": False,
            "reason": "화이트리스트에 없는 명령",
            "rule": None,
            "command": normalized_cmd,
        }

    def get_safe_environment(self) -> Dict[str, str]:
        """안전한 환경변수 반환"""
        import os

        # 허용된 환경변수만 전달
        safe_vars = [
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "NODE_ENV",
            "NPM_CONFIG_PREFIX",
        ]

        safe_env = {}
        for var in safe_vars:
            if var in os.environ:
                safe_env[var] = os.environ[var]

        return safe_env


# 전역 화이트리스트 인스턴스
_whitelist = None


def get_command_whitelist() -> CommandWhitelist:
    """명령 화이트리스트 싱글톤"""
    global _whitelist
    if _whitelist is None:
        _whitelist = CommandWhitelist()
    return _whitelist


def validate_command(command: str) -> Dict[str, Any]:
    """명령 검증 (편의 함수)"""
    whitelist = get_command_whitelist()
    return whitelist.validate_command(command)
