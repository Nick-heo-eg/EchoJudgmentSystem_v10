#!/usr/bin/env python3
"""
Echo 시스템 고급 보안 감사 도구
코드 보안 취약점, 의존성 취약점, 시크릿 유출 감지
"""

import re
import ast
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import os

logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """보안 이슈"""

    severity: str  # critical, high, medium, low
    category: str  # secret, vulnerability, configuration, code_quality
    description: str
    file_path: str
    line_number: int
    recommendation: str
    confidence: float  # 0.0 - 1.0
    cwe_id: Optional[str] = None


@dataclass
class DependencyVulnerability:
    """의존성 취약점"""

    package: str
    version: str
    vulnerability_id: str
    severity: str
    description: str
    fixed_version: Optional[str] = None


class SecurityAuditor:
    """보안 감사 시스템"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.issues: List[SecurityIssue] = []
        self.vulnerabilities: List[DependencyVulnerability] = []

        # 🔍 보안 패턴 정의
        self.secret_patterns = {
            "api_key": [
                r"(?i)(api[_-]?key|apikey)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_\-]{20,}",
                r"(?i)(secret[_-]?key|secretkey)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_\-]{20,}",
            ],
            "password": [
                r"(?i)(password|passwd|pwd)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_@#$%^&*!]{8,}",
                r"(?i)(db[_-]?pass|dbpass)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_@#$%^&*!]{6,}",
            ],
            "token": [
                r"(?i)(access[_-]?token|accesstoken)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_\-]{20,}",
                r"(?i)(bearer[_-]?token|bearertoken)[\"'\s]*[:=][\"'\s]*[a-zA-Z0-9_\-\.]{20,}",
            ],
            "crypto_key": [
                r"(?i)(private[_-]?key|privatekey)[\"'\s]*[:=][\"'\s]*-----BEGIN",
                r"(?i)(rsa[_-]?key|rsakey)[\"'\s]*[:=][\"'\s]*-----BEGIN",
            ],
        }

        self.vulnerability_patterns = {
            "sql_injection": [
                r"(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*[\'\"]",
                r"(?i)execute\s*\(\s*[\"'].*(SELECT|INSERT|UPDATE|DELETE).*[\"']\s*\+",
                r"(?i)query\s*\(\s*[\"'].*(SELECT|INSERT|UPDATE|DELETE).*[\"']\s*%",
            ],
            "command_injection": [
                r"(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\(\s*[\"'].*\+",
                r"(?i)(eval|exec)\s*\(\s*[\"'].*\+",
                r"(?i)shell=True.*\+",
            ],
            "path_traversal": [
                r"(?i)(open|file)\s*\(\s*[\"'].*\.\./",
                r"(?i)os\.path\.join\s*\(.*\.\./",
                r"(?i)pathlib\.Path\s*\(.*\.\./",
            ],
            "hardcoded_secrets": [
                r"(?i)(api_key|secret|password|token)\s*=\s*[\"'][a-zA-Z0-9_\-]{10,}[\"']",
                r"(?i)(AWS_ACCESS_KEY|GITHUB_TOKEN)\s*=\s*[\"'][a-zA-Z0-9_\-]{10,}[\"']",
            ],
        }

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """종합 보안 감사 실행"""
        logger.info("🔒 Starting comprehensive security audit...")

        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_dir.absolute()),
            "scanned_files": 0,
            "security_issues": [],
            "dependency_vulnerabilities": [],
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
            },
        }

        # 1. 파일 스캔
        scanned_files = self._scan_source_files()
        audit_results["scanned_files"] = scanned_files

        # 2. 의존성 스캔
        self._scan_dependencies()

        # 3. 설정 파일 스캔
        self._scan_configuration_files()

        # 4. Git 히스토리 스캔 (선택적)
        self._scan_git_history()

        # 결과 정리
        audit_results["security_issues"] = [asdict(issue) for issue in self.issues]
        audit_results["dependency_vulnerabilities"] = [
            asdict(vuln) for vuln in self.vulnerabilities
        ]

        # 통계 계산
        for issue in self.issues:
            audit_results["summary"]["total_issues"] += 1
            audit_results["summary"][f"{issue.severity}_issues"] += 1

        logger.info(
            f"🔍 Security audit completed: {audit_results['summary']['total_issues']} issues found"
        )
        return audit_results

    def _scan_source_files(self) -> int:
        """소스 파일 스캔"""
        scanned_count = 0

        # Python 파일 스캔
        python_files = list(self.project_dir.rglob("*.py"))
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            self._scan_python_file(file_path)
            scanned_count += 1

        # YAML/JSON 설정 파일 스캔
        config_files = (
            list(self.project_dir.rglob("*.yaml"))
            + list(self.project_dir.rglob("*.yml"))
            + list(self.project_dir.rglob("*.json"))
        )
        for file_path in config_files:
            if self._should_skip_file(file_path):
                continue
            self._scan_config_file(file_path)
            scanned_count += 1

        return scanned_count

    def _should_skip_file(self, file_path: Path) -> bool:
        """파일 스킵 여부 판단"""
        skip_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
        }
        skip_files = {".gitignore", ".env.example"}

        # 디렉토리 체크
        for part in file_path.parts:
            if part in skip_dirs:
                return True

        # 파일명 체크
        if file_path.name in skip_files:
            return True

        # 바이너리 파일 체크
        if file_path.suffix in {".pyc", ".pyo", ".so", ".dll", ".exe"}:
            return True

        return False

    def _scan_python_file(self, file_path: Path):
        """Python 파일 보안 스캔"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\\n")

            # 1. 시크릿 패턴 검사
            self._check_secret_patterns(file_path, content, lines)

            # 2. 취약점 패턴 검사
            self._check_vulnerability_patterns(file_path, content, lines)

            # 3. AST 기반 정적 분석
            self._analyze_python_ast(file_path, content)

        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")

    def _check_secret_patterns(self, file_path: Path, content: str, lines: List[str]):
        """시크릿 패턴 검사"""
        for secret_type, patterns in self.secret_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    line_num = content[: match.start()].count("\\n") + 1

                    self.issues.append(
                        SecurityIssue(
                            severity=(
                                "critical"
                                if secret_type in ["api_key", "crypto_key"]
                                else "high"
                            ),
                            category="secret",
                            description=f"Potential {secret_type.replace('_', ' ')} found in source code",
                            file_path=str(file_path.relative_to(self.project_dir)),
                            line_number=line_num,
                            recommendation=f"Move {secret_type} to environment variables or secure vault",
                            confidence=0.8,
                            cwe_id="CWE-798",
                        )
                    )

    def _check_vulnerability_patterns(
        self, file_path: Path, content: str, lines: List[str]
    ):
        """취약점 패턴 검사"""
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    line_num = content[: match.start()].count("\\n") + 1

                    severity = (
                        "high"
                        if vuln_type in ["sql_injection", "command_injection"]
                        else "medium"
                    )

                    self.issues.append(
                        SecurityIssue(
                            severity=severity,
                            category="vulnerability",
                            description=f"Potential {vuln_type.replace('_', ' ')} vulnerability",
                            file_path=str(file_path.relative_to(self.project_dir)),
                            line_number=line_num,
                            recommendation=self._get_vulnerability_recommendation(
                                vuln_type
                            ),
                            confidence=0.7,
                            cwe_id=self._get_cwe_id(vuln_type),
                        )
                    )

    def _analyze_python_ast(self, file_path: Path, content: str):
        """AST 기반 Python 정적 분석"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 위험한 함수 호출 검사
                if isinstance(node, ast.Call):
                    self._check_dangerous_function_calls(file_path, node)

                # 하드코딩된 시크릿 검사
                if isinstance(node, ast.Assign):
                    self._check_hardcoded_secrets(file_path, node)

        except SyntaxError:
            # 구문 오류가 있는 파일은 건너뛰기
            pass
        except Exception as e:
            logger.warning(f"AST analysis failed for {file_path}: {e}")

    def _check_dangerous_function_calls(self, file_path: Path, node: ast.Call):
        """위험한 함수 호출 검사"""
        dangerous_functions = {
            "eval": "high",
            "exec": "high",
            "compile": "medium",
            "input": "low",  # Python 2 호환성 이슈
        }

        if hasattr(node.func, "id") and node.func.id in dangerous_functions:
            severity = dangerous_functions[node.func.id]

            self.issues.append(
                SecurityIssue(
                    severity=severity,
                    category="code_quality",
                    description=f"Use of dangerous function: {node.func.id}()",
                    file_path=str(file_path.relative_to(self.project_dir)),
                    line_number=node.lineno,
                    recommendation=f"Avoid using {node.func.id}() or implement proper input validation",
                    confidence=0.9,
                    cwe_id="CWE-94",
                )
            )

    def _check_hardcoded_secrets(self, file_path: Path, node: ast.Assign):
        """하드코딩된 시크릿 검사"""
        if not node.targets:
            return

        target = node.targets[0]
        if not hasattr(target, "id"):
            return

        var_name = target.id.lower()
        suspicious_names = {"password", "secret", "key", "token", "api_key"}

        if any(name in var_name for name in suspicious_names):
            if isinstance(node.value, ast.Str) and len(node.value.s) > 8:
                self.issues.append(
                    SecurityIssue(
                        severity="high",
                        category="secret",
                        description=f"Hardcoded secret in variable: {target.id}",
                        file_path=str(file_path.relative_to(self.project_dir)),
                        line_number=node.lineno,
                        recommendation="Move secret to environment variables or configuration file",
                        confidence=0.8,
                        cwe_id="CWE-798",
                    )
                )

    def _scan_config_file(self, file_path: Path):
        """설정 파일 스캔"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # JSON/YAML에서 시크릿 패턴 검사
            for secret_type, patterns in self.secret_patterns.items():
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        line_num = content[: match.start()].count("\\n") + 1

                        self.issues.append(
                            SecurityIssue(
                                severity="critical",
                                category="secret",
                                description=f"Potential {secret_type.replace('_', ' ')} in configuration file",
                                file_path=str(file_path.relative_to(self.project_dir)),
                                line_number=line_num,
                                recommendation="Move sensitive data to environment variables",
                                confidence=0.9,
                                cwe_id="CWE-798",
                            )
                        )

        except Exception as e:
            logger.warning(f"Failed to scan config file {file_path}: {e}")

    def _scan_dependencies(self):
        """의존성 취약점 스캔"""
        # requirements.txt 스캔
        req_file = self.project_dir / "requirements.txt"
        if req_file.exists():
            self._scan_requirements_file(req_file)

        # pyproject.toml 스캔
        pyproject_file = self.project_dir / "pyproject.toml"
        if pyproject_file.exists():
            self._scan_pyproject_file(pyproject_file)

    def _scan_requirements_file(self, req_file: Path):
        """requirements.txt 파일 스캔"""
        try:
            # safety 라이브러리 사용 (설치되어 있다면)
            result = subprocess.run(
                ["python", "-m", "pip", "install", "safety"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # safety check 실행
                safety_result = subprocess.run(
                    ["safety", "check", "--json", "--file", str(req_file)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if safety_result.returncode != 0 and safety_result.stdout:
                    try:
                        vulnerabilities = json.loads(safety_result.stdout)
                        for vuln in vulnerabilities:
                            self.vulnerabilities.append(
                                DependencyVulnerability(
                                    package=vuln.get("package", "unknown"),
                                    version=vuln.get("installed_version", "unknown"),
                                    vulnerability_id=vuln.get(
                                        "vulnerability_id", "unknown"
                                    ),
                                    severity=vuln.get("severity", "medium"),
                                    description=vuln.get(
                                        "advisory", "Vulnerability detected"
                                    ),
                                    fixed_version=vuln.get("fixed_version"),
                                )
                            )
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            logger.warning(f"Dependency scan failed: {e}")

    def _scan_pyproject_file(self, pyproject_file: Path):
        """pyproject.toml 파일 기본 스캔"""
        try:
            with open(pyproject_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 기본적인 패턴 매칭으로 알려진 취약한 패키지 검사
            vulnerable_packages = {
                "django<3.2": "Django < 3.2 has known security vulnerabilities",
                "flask<2.0": "Flask < 2.0 has known security vulnerabilities",
                "requests<2.25": "Requests < 2.25 has known security vulnerabilities",
            }

            for package_pattern, description in vulnerable_packages.items():
                if package_pattern.split("<")[0] in content:
                    self.issues.append(
                        SecurityIssue(
                            severity="medium",
                            category="vulnerability",
                            description=description,
                            file_path=str(pyproject_file.relative_to(self.project_dir)),
                            line_number=1,
                            recommendation=f"Update to latest secure version of {package_pattern.split('<')[0]}",
                            confidence=0.6,
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to scan pyproject.toml: {e}")

    def _scan_configuration_files(self):
        """설정 파일들 스캔"""
        config_patterns = {
            ".env": self._scan_env_file,
            "docker-compose.yml": self._scan_docker_compose,
            "Dockerfile": self._scan_dockerfile,
        }

        for filename, scan_func in config_patterns.items():
            config_file = self.project_dir / filename
            if config_file.exists():
                scan_func(config_file)

    def _scan_env_file(self, env_file: Path):
        """.env 파일 스캔"""
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)

                    # 민감한 정보가 값으로 하드코딩되어 있는지 확인
                    if len(value) > 20 and not value.startswith("${"):
                        suspicious_keys = ["password", "secret", "key", "token"]
                        if any(keyword in key.lower() for keyword in suspicious_keys):
                            self.issues.append(
                                SecurityIssue(
                                    severity="medium",
                                    category="secret",
                                    description=f"Hardcoded value in .env file: {key}",
                                    file_path=str(
                                        env_file.relative_to(self.project_dir)
                                    ),
                                    line_number=line_num,
                                    recommendation="Use environment-specific values or reference external secret management",
                                    confidence=0.7,
                                )
                            )

        except Exception as e:
            logger.warning(f"Failed to scan .env file: {e}")

    def _scan_docker_compose(self, compose_file: Path):
        """docker-compose.yml 스캔"""
        try:
            with open(compose_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 권한 상승 위험 검사
            if "privileged: true" in content:
                self.issues.append(
                    SecurityIssue(
                        severity="high",
                        category="configuration",
                        description="Container running with privileged mode",
                        file_path=str(compose_file.relative_to(self.project_dir)),
                        line_number=content.find("privileged: true")
                        // len(content.split("\\n")[0])
                        + 1,
                        recommendation="Remove privileged mode or use specific capabilities instead",
                        confidence=0.9,
                        cwe_id="CWE-250",
                    )
                )

        except Exception as e:
            logger.warning(f"Failed to scan docker-compose.yml: {e}")

    def _scan_dockerfile(self, dockerfile: Path):
        """Dockerfile 스캔"""
        try:
            with open(dockerfile, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip().upper()

                # ROOT 사용자로 실행 검사
                if line.startswith("USER ROOT") or (
                    line.startswith("USER ") and "0" in line
                ):
                    self.issues.append(
                        SecurityIssue(
                            severity="medium",
                            category="configuration",
                            description="Container running as root user",
                            file_path=str(dockerfile.relative_to(self.project_dir)),
                            line_number=line_num,
                            recommendation="Use non-root user for container execution",
                            confidence=0.8,
                            cwe_id="CWE-250",
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to scan Dockerfile: {e}")

    def _scan_git_history(self):
        """Git 히스토리에서 실수로 커밋된 시크릿 검사"""
        try:
            # git log로 최근 커밋들의 diff 검사
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--pretty=format:%H"],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
            )

            if result.returncode == 0:
                commit_hashes = result.stdout.strip().split("\\n")

                for commit_hash in commit_hashes[:5]:  # 최근 5개 커밋만 검사
                    self._scan_commit_diff(commit_hash)

        except Exception as e:
            logger.warning(f"Git history scan failed: {e}")

    def _scan_commit_diff(self, commit_hash: str):
        """특정 커밋의 diff 스캔"""
        try:
            result = subprocess.run(
                ["git", "show", "--format=", commit_hash],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
            )

            if result.returncode == 0:
                diff_content = result.stdout

                # diff에서 시크릿 패턴 검사
                for secret_type, patterns in self.secret_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, diff_content, re.MULTILINE):
                            self.issues.append(
                                SecurityIssue(
                                    severity="critical",
                                    category="secret",
                                    description=f"Potential {secret_type.replace('_', ' ')} found in git history",
                                    file_path=f"git:{commit_hash[:8]}",
                                    line_number=0,
                                    recommendation="Remove secret from git history using git filter-branch or BFG",
                                    confidence=0.7,
                                    cwe_id="CWE-798",
                                )
                            )
                            break

        except Exception as e:
            logger.warning(f"Failed to scan commit {commit_hash}: {e}")

    def _get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """취약점 타입별 권장사항"""
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM instead of string concatenation",
            "command_injection": "Validate and sanitize all user inputs, use subprocess with shell=False",
            "path_traversal": "Validate file paths and use os.path.normpath() to prevent directory traversal",
            "hardcoded_secrets": "Move secrets to environment variables or secure configuration",
        }
        return recommendations.get(
            vuln_type, "Review and fix the identified security issue"
        )

    def _get_cwe_id(self, vuln_type: str) -> str:
        """취약점 타입별 CWE ID"""
        cwe_mapping = {
            "sql_injection": "CWE-89",
            "command_injection": "CWE-78",
            "path_traversal": "CWE-22",
            "hardcoded_secrets": "CWE-798",
        }
        return cwe_mapping.get(vuln_type, "CWE-200")

    def generate_security_report(self, output_path: str):
        """보안 리포트 생성"""
        audit_results = self.run_comprehensive_audit()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False)

        logger.info(f"🔒 Security report generated: {output_path}")
        return audit_results


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Echo Security Auditor")
    parser.add_argument("--project-dir", default=".", help="Project directory to audit")
    parser.add_argument(
        "--output", default="security_audit_report.json", help="Output report file"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # 로깅 설정
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 보안 감사 실행
    auditor = SecurityAuditor(args.project_dir)
    results = auditor.generate_security_report(args.output)

    # 결과 요약 출력
    summary = results["summary"]
    print(f"\\n🔒 Security Audit Results:")
    print(f"   📁 Scanned Files: {results['scanned_files']}")
    print(f"   🚨 Total Issues: {summary['total_issues']}")
    print(f"   🔥 Critical: {summary['critical_issues']}")
    print(f"   ⚠️  High: {summary['high_issues']}")
    print(f"   📋 Medium: {summary['medium_issues']}")
    print(f"   ℹ️  Low: {summary['low_issues']}")
    print(f"   🧩 Dependencies: {len(results['dependency_vulnerabilities'])}")

    return 0 if summary["total_issues"] == 0 else 1


if __name__ == "__main__":
    exit(main())
