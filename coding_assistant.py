#!/usr/bin/env python3
"""
Claude Code 전용 실시간 개발 도우미
당장 사용 가능한 실용적 개발 에이전트들
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class CodingAssistant:
    def __init__(self):
        self.project_root = Path.cwd()
        self.agents = {
            "analyze": self.analyze_codebase,
            "refactor": self.smart_refactor,
            "debug": self.debug_code,
            "test": self.generate_tests,
            "doc": self.generate_docs,
            "arch": self.analyze_architecture,
            "perf": self.performance_check,
            "sec": self.security_audit,
        }

    def detect_project_context(self) -> Dict:
        """현재 프로젝트 컨텍스트 자동 감지"""
        context = {
            "language": None,
            "framework": None,
            "build_system": None,
            "files_count": 0,
            "main_files": [],
        }

        # 파일 확장자로 언어 감지
        extensions = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                ignore in str(file_path)
                for ignore in [".git", "node_modules", "__pycache__", ".venv"]
            ):
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
                context["files_count"] += 1

                if file_path.name in [
                    "main.py",
                    "app.py",
                    "index.js",
                    "main.js",
                    "App.tsx",
                    "main.rs",
                    "main.go",
                ]:
                    context["main_files"].append(str(file_path))

        # 주 언어 결정
        if extensions.get(".py", 0) > 0:
            context["language"] = "Python"
            if (self.project_root / "requirements.txt").exists():
                context["build_system"] = "pip"
            elif (self.project_root / "pyproject.toml").exists():
                context["build_system"] = "poetry"
        elif extensions.get(".js", 0) > 0 or extensions.get(".ts", 0) > 0:
            context["language"] = "JavaScript/TypeScript"
            if (self.project_root / "package.json").exists():
                context["build_system"] = "npm/yarn"
        elif extensions.get(".rs", 0) > 0:
            context["language"] = "Rust"
            context["build_system"] = "cargo"
        elif extensions.get(".go", 0) > 0:
            context["language"] = "Go"
            context["build_system"] = "go mod"

        # 프레임워크 감지
        if context["language"] == "Python":
            for file_path in self.project_root.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if "from flask import" in content or "import flask" in content:
                        context["framework"] = "Flask"
                        break
                    elif (
                        "from fastapi import" in content or "import fastapi" in content
                    ):
                        context["framework"] = "FastAPI"
                        break
                    elif "from django" in content or "import django" in content:
                        context["framework"] = "Django"
                        break
                except:
                    continue

        return context

    def analyze_codebase(self, target_path: Optional[str] = None) -> str:
        """코드베이스 종합 분석"""
        context = self.detect_project_context()

        analysis_prompt = f"""
## 프로젝트 코드베이스 종합 분석

**프로젝트 컨텍스트:**
- 언어: {context['language']}
- 프레임워크: {context.get('framework', 'N/A')}
- 빌드 시스템: {context.get('build_system', 'N/A')}  
- 총 파일 수: {context['files_count']}
- 주요 파일: {', '.join(context['main_files']) if context['main_files'] else 'N/A'}

**분석 요청:**
다음 관점에서 코드베이스를 종합 분석해주세요:

1. **아키텍처 구조**
   - 전체 프로젝트 구조 및 모듈 구성
   - 설계 패턴 사용 현황
   - 의존성 관계 분석

2. **코드 품질**
   - 코딩 컨벤션 준수도
   - 중복 코드 및 기술 부채
   - 복잡도 분석

3. **개선 제안**
   - 우선 순위별 리팩터링 대상
   - 성능 최적화 포인트
   - 보안 고려사항

4. **확장성 평가**
   - 새 기능 추가 용이성
   - 유지보수성 평가
   - 팀 개발 적합성

프로젝트 루트: {self.project_root}
분석 대상: {"전체 프로젝트" if not target_path else target_path}
"""
        return analysis_prompt

    def smart_refactor(self, file_path: str) -> str:
        """지능형 리팩터링 제안"""
        if not Path(file_path).exists():
            return f"파일을 찾을 수 없습니다: {file_path}"

        context = self.detect_project_context()

        refactor_prompt = f"""
## 지능형 코드 리팩터링

**리팩터링 대상:** {file_path}
**프로젝트 컨텍스트:** {context['language']} ({context.get('framework', 'N/A')})

**리팩터링 체크리스트:**

1. **코드 품질 개선**
   - 가독성 향상 (명확한 변수명, 함수 분리)
   - DRY 원칙 적용 (중복 코드 제거)
   - SOLID 원칙 준수 확인

2. **성능 최적화**
   - 알고리즘 복잡도 개선
   - 메모리 사용량 최적화
   - 불필요한 연산 제거

3. **유지보수성 강화**
   - 함수 크기 적절성 (15줄 이하 권장)
   - 책임 분리 (단일 책임 원칙)
   - 에러 처리 강화

4. **현대적 패턴 적용**
   - {context['language']} 최신 문법 활용
   - 타입 힌트/어노테이션 추가
   - 비동기 처리 최적화 (필요시)

**요청사항:**
- 현재 코드의 문제점 진단
- 구체적인 리팩터링 방안 제시
- 개선된 코드 예시 제공
- 변경으로 인한 영향도 분석

파일 내용을 분석하여 최적화된 코드를 제안해주세요.
"""
        return refactor_prompt

    def debug_code(self, file_path: str, error_description: str = "") -> str:
        """AI 기반 디버깅 지원"""
        if not Path(file_path).exists():
            return f"파일을 찾을 수 없습니다: {file_path}"

        context = self.detect_project_context()

        debug_prompt = f"""
## AI 디버깅 전문가

**디버깅 대상:** {file_path}
**언어/프레임워크:** {context['language']} ({context.get('framework', 'N/A')})
**에러 설명:** {error_description if error_description else "일반적인 코드 검토"}

**디버깅 프로세스:**

1. **에러 패턴 분석**
   - 구문 오류 (Syntax Errors) 검사
   - 논리 오류 (Logic Errors) 탐지
   - 런타임 오류 (Runtime Errors) 예측
   - 타입 관련 오류 확인

2. **잠재적 문제 발굴**
   - 널 포인터/언디파인드 접근
   - 메모리 누수 가능성
   - 무한 루프 위험
   - 레이스 컨디션 (멀티스레딩)

3. **근본 원인 분석**
   - 데이터 플로우 추적
   - 함수 호출 체인 분석
   - 의존성 문제 확인
   - 환경 설정 이슈

4. **해결 방안 제시**
   - 즉시 수정 방안 (Hot Fix)
   - 구조적 개선 방안 (Long-term)
   - 예방 코드 패턴 제안
   - 테스트 케이스 추천

**디버깅 도구 활용:**
- 정적 분석 도구 추천
- 프로파일링 방법 제안
- 로깅 전략 개선
- 모니터링 포인트 설정

코드를 자세히 분석하여 문제점과 해결책을 제시해주세요.
"""
        return debug_prompt

    def generate_tests(self, file_path: str, test_type: str = "unit") -> str:
        """테스트 코드 자동 생성"""
        if not Path(file_path).exists():
            return f"파일을 찾을 수 없습니다: {file_path}"

        context = self.detect_project_context()

        test_prompt = f"""
## 자동 테스트 생성 시스템

**테스트 대상:** {file_path}
**언어/프레임워크:** {context['language']} ({context.get('framework', 'N/A')})
**테스트 타입:** {test_type}

**테스트 생성 전략:**

1. **단위 테스트 (Unit Tests)**
   - 각 함수/메서드별 독립 테스트
   - 정상 케이스 + 경계값 테스트
   - 예외 상황 처리 검증
   - Mock/Stub 활용 방안

2. **통합 테스트 (Integration Tests)**
   - 모듈 간 상호작용 검증
   - 데이터베이스 연동 테스트
   - API 엔드포인트 테스트
   - 외부 서비스 연동 검증

3. **테스트 프레임워크별 구현**
   - Python: pytest, unittest
   - JavaScript: Jest, Mocha
   - Rust: cargo test
   - Go: go test

**테스트 케이스 설계:**

### 1. 해피 패스 (Happy Path)
- 정상적인 입력값으로 예상 결과 검증
- 일반적인 사용 시나리오 테스트

### 2. 엣지 케이스 (Edge Cases)  
- 경계값 테스트 (0, 1, MAX_VALUE 등)
- 빈 값, null, undefined 처리
- 극한 상황 (메모리 부족, 네트워크 장애)

### 3. 오류 처리 (Error Handling)
- 잘못된 입력값 처리
- 예외 발생 시나리오
- 에러 메시지 검증

**결과물 요청:**
- 실행 가능한 테스트 코드
- 테스트 커버리지 90%+ 목표
- 테스트 실행 방법 가이드
- CI/CD 파이프라인 통합 방안

대상 코드를 분석하여 포괄적인 테스트 수트를 생성해주세요.
"""
        return test_prompt

    def generate_docs(self, file_path: str, doc_type: str = "api") -> str:
        """문서 자동 생성"""
        if not Path(file_path).exists():
            return f"파일을 찾을 수 없습니다: {file_path}"

        context = self.detect_project_context()

        doc_prompt = f"""
## 지능형 문서 자동 생성

**문서화 대상:** {file_path}
**언어/프레임워크:** {context['language']} ({context.get('framework', 'N/A')})
**문서 타입:** {doc_type}

**문서 생성 체계:**

1. **API 문서 ({doc_type})**
   - 함수/클래스별 상세 설명
   - 파라미터 및 반환값 명세
   - 사용 예제 코드
   - 에러 케이스 및 처리 방법

2. **코드 주석 (Inline Comments)**
   - 복잡한 로직 단계별 설명
   - 알고리즘 설명 및 시간복잡도
   - TODO, FIXME 항목 정리
   - 의존성 및 제약사항 명시

3. **README 생성**
   - 프로젝트 개요 및 목적
   - 설치 및 실행 방법
   - 사용법 및 예제
   - 기여 방법 가이드

4. **아키텍처 문서**
   - 시스템 구조도 (Mermaid)
   - 컴포넌트 관계도
   - 데이터 플로우 다이어그램
   - 설계 의사결정 배경

**문서 품질 기준:**

### 명확성 (Clarity)
- 기술적 용어 쉬운 설명
- 단계별 가이드 제공
- 시각적 다이어그램 활용

### 완전성 (Completeness)
- 모든 public 함수/클래스 문서화
- 에러 시나리오 포함
- 성능 특성 명시

### 최신성 (Currency)
- 코드 변경 시 자동 업데이트 방안
- 버전별 변경사항 추적
- 마이그레이션 가이드

**결과물:**
- 마크다운 형식 문서
- 인터랙티브 API 문서 (필요시)
- 코드 내 주석 개선안
- 문서 유지보수 가이드

코드를 분석하여 개발자와 사용자 모두에게 유용한 문서를 생성해주세요.
"""
        return doc_prompt

    def analyze_architecture(self) -> str:
        """시스템 아키텍처 분석"""
        context = self.detect_project_context()

        arch_prompt = f"""
## 시스템 아키텍처 심층 분석

**프로젝트 컨텍스트:**
- 언어: {context['language']}
- 프레임워크: {context.get('framework', 'N/A')}
- 총 파일 수: {context['files_count']}
- 프로젝트 경로: {self.project_root}

**아키텍처 분석 요청:**

1. **현재 아키텍처 패턴 식별**
   - MVC, MVP, MVVM 등 패턴 적용 현황
   - 레이어드 아키텍처 구조 분석
   - 마이크로서비스 vs 모놀리식 판단
   - 디자인 패턴 사용 현황

2. **모듈 구조 및 의존성**
   - 핵심 모듈 식별 및 역할 정의
   - 모듈 간 의존성 관계도
   - 순환 의존성 문제 탐지
   - 결합도/응집도 분석

3. **확장성 및 유지보수성**
   - 새 기능 추가 시 영향도
   - 코드 변경의 파급 효과
   - 테스트 용이성 평가
   - 팀 개발 적합성

4. **성능 및 확장성**
   - 병목점 예상 지점 식별
   - 수평/수직 확장 가능성
   - 캐싱 전략 적합성
   - 데이터베이스 설계 효율성

**개선 제안:**

### 즉시 개선 가능 (Quick Wins)
- 간단한 리팩터링으로 개선되는 부분
- 설정 변경으로 해결되는 이슈
- 라이브러리 업데이트 필요 사항

### 중기 개선 계획 (Medium-term)
- 모듈 구조 재설계
- 데이터베이스 스키마 최적화
- API 인터페이스 개선

### 장기 전략적 개선 (Long-term)
- 아키텍처 패턴 전환
- 마이크로서비스 분할
- 클라우드 네이티브 마이그레이션

**결과물:**
- 현재 아키텍처 다이어그램 (Mermaid)
- 의존성 관계도
- 개선 로드맵 (우선순위별)
- 마이그레이션 가이드

전체 프로젝트 구조를 분석하여 최적화 방안을 제시해주세요.
"""
        return arch_prompt

    def performance_check(self, file_path: str = None) -> str:
        """성능 분석 및 최적화"""
        context = self.detect_project_context()
        target = file_path if file_path else "전체 프로젝트"

        perf_prompt = f"""
## 성능 최적화 전문 분석

**분석 대상:** {target}
**언어/프레임워크:** {context['language']} ({context.get('framework', 'N/A')})

**성능 분석 체크리스트:**

1. **알고리즘 복잡도 분석**
   - 시간 복잡도 (Big O) 평가
   - 공간 복잡도 최적화 포인트
   - 중복 연산 제거 기회
   - 효율적 자료구조 활용

2. **메모리 사용 최적화**
   - 메모리 누수 위험 지점
   - 객체 생성/소멸 패턴 분석
   - 캐싱 전략 개선 방안
   - 가비지 컬렉션 최적화

3. **I/O 성능 개선**
   - 파일 읽기/쓰기 최적화
   - 네트워크 통신 효율성
   - 데이터베이스 쿼리 성능
   - 비동기 처리 적용 포인트

4. **언어별 특화 최적화**

### Python 최적화
- List comprehension 활용
- Generator 사용으로 메모리 절약
- NumPy/Pandas 벡터화 연산
- multiprocessing/asyncio 활용

### JavaScript/TypeScript 최적화
- 이벤트 루프 최적화
- Promise/async-await 효율적 사용
- 번들 사이즈 최소화
- 브라우저 캐싱 전략

### 공통 최적화 패턴
- 지연 로딩 (Lazy Loading)
- 연결 풀링 (Connection Pooling)
- 배치 처리 (Batch Processing)
- 인덱싱 전략

**성능 측정 도구:**
- 프로파일링 도구 추천
- 벤치마킹 방법론
- 모니터링 설정 가이드
- 성능 테스트 자동화

**최적화 우선순위:**
1. 병목점 해결 (80/20 법칙)
2. 사용자 경험 직접 영향
3. 서버 리소스 절약 효과
4. 개발 생산성 향상

**결과 요청:**
- 현재 성능 이슈 진단
- 구체적 최적화 코드 제안
- 성능 개선 효과 예측
- 모니터링 및 측정 방안

코드를 분석하여 성능 병목을 찾고 최적화 방안을 제시해주세요.
"""
        return perf_prompt

    def security_audit(self, file_path: str = None) -> str:
        """보안 감사 및 취약점 분석"""
        context = self.detect_project_context()
        target = file_path if file_path else "전체 프로젝트"

        security_prompt = f"""
## 종합 보안 감사 시스템

**감사 대상:** {target}
**언어/프레임워크:** {context['language']} ({context.get('framework', 'N/A')})

**보안 취약점 체크리스트:**

1. **OWASP Top 10 검사 (2021)**
   - A01: 접근 제어 취약점 (Broken Access Control)
   - A02: 암호화 오류 (Cryptographic Failures)
   - A03: 인젝션 공격 (Injection)
   - A04: 안전하지 않은 설계 (Insecure Design)
   - A05: 보안 구성 오류 (Security Misconfiguration)
   - A06: 취약한 구성요소 (Vulnerable Components)
   - A07: 인증/인가 실패 (Auth Failures)
   - A08: 소프트웨어 무결성 실패 (Software Integrity)
   - A09: 로깅/모니터링 부족 (Logging Failures)
   - A10: 서버사이드 요청 위조 (SSRF)

2. **데이터 보호**
   - 개인정보 처리 방식 검토
   - 민감 정보 암호화 상태
   - 데이터 전송 보안 (HTTPS/TLS)
   - 저장 데이터 보안 (Encryption at Rest)

3. **인증/인가 시스템**
   - 패스워드 정책 및 해싱
   - 세션 관리 보안성
   - JWT 토큰 보안 구현
   - 다중 인증 (2FA/MFA) 적용

4. **입력 검증 및 출력 인코딩**
   - SQL 인젝션 방지
   - XSS (Cross-Site Scripting) 차단
   - CSRF (Cross-Site Request Forgery) 보호
   - 파일 업로드 보안

**언어별 특화 보안**

### Python 보안
- pickle 사용 시 보안 위험
- eval(), exec() 함수 사용 검토
- Django/Flask 보안 설정
- 의존성 취약점 (pip audit)

### JavaScript/Node.js 보안
- npm 패키지 취약점 스캔
- eval() 및 동적 코드 실행 위험
- 프로토타입 오염 공격
- 환경변수 노출 위험

### 공통 보안 패턴
- 최소 권한 원칙 적용
- 디폴트 거부 (Default Deny)
- 심층 방어 전략
- 보안 헤더 설정

**규정 준수 검토:**
- GDPR 개인정보보호
- CCPA 캘리포니아 소비자 보호법
- HIPAA 의료정보 보호 (해당시)
- SOX 재무보고 투명성 (해당시)

**보안 도구 활용:**
- 정적 분석 도구 (SAST)
- 동적 분석 도구 (DAST)
- 의존성 취약점 스캔
- 컨테이너 보안 검사

**결과 요청:**
- 발견된 취약점 우선순위별 정리
- 구체적 수정 방안 코드 제공
- 보안 강화 가이드라인
- 정기 보안 감사 체크리스트

코드와 설정을 종합 분석하여 보안 취약점과 개선 방안을 제시해주세요.
"""
        return security_prompt

    def run_agent(self, agent_name: str, *args) -> str:
        """에이전트 실행"""
        if agent_name not in self.agents:
            available = ", ".join(self.agents.keys())
            return (
                f"알 수 없는 에이전트: {agent_name}\n사용 가능한 에이전트: {available}"
            )

        return self.agents[agent_name](*args)


def main():
    parser = argparse.ArgumentParser(description="Claude Code 전용 개발 도우미")
    parser.add_argument(
        "agent",
        choices=["analyze", "refactor", "debug", "test", "doc", "arch", "perf", "sec"],
        help="실행할 에이전트",
    )
    parser.add_argument("--file", "-f", help="대상 파일 경로")
    parser.add_argument(
        "--type", "-t", default="unit", help="테스트 타입 또는 문서 타입"
    )
    parser.add_argument("--error", "-e", default="", help="디버깅 시 에러 설명")

    args = parser.parse_args()

    assistant = CodingAssistant()

    # 에이전트별 파라미터 처리
    if args.agent == "analyze":
        result = assistant.run_agent(args.agent, args.file)
    elif args.agent == "refactor":
        if not args.file:
            print("리팩터링할 파일을 지정해주세요: --file <파일경로>")
            return
        result = assistant.run_agent(args.agent, args.file)
    elif args.agent == "debug":
        if not args.file:
            print("디버깅할 파일을 지정해주세요: --file <파일경로>")
            return
        result = assistant.run_agent(args.agent, args.file, args.error)
    elif args.agent == "test":
        if not args.file:
            print("테스트할 파일을 지정해주세요: --file <파일경로>")
            return
        result = assistant.run_agent(args.agent, args.file, args.type)
    elif args.agent == "doc":
        if not args.file:
            print("문서화할 파일을 지정해주세요: --file <파일경로>")
            return
        result = assistant.run_agent(args.agent, args.file, args.type)
    elif args.agent == "arch":
        result = assistant.run_agent(args.agent)
    elif args.agent in ["perf", "sec"]:
        result = assistant.run_agent(args.agent, args.file)

    print(result)


if __name__ == "__main__":
    main()
