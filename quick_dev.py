#!/usr/bin/env python3
"""
빠른 개발 도우미 - Claude Code에서 바로 사용
agent_kits의 프롬프트를 실제로 활용하는 CLI 도구
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class QuickDev:
    def __init__(self):
        self.project_root = Path.cwd()
        self.agent_kit = self.load_agent_kit()

    def load_agent_kit(self) -> Dict:
        """에이전트 키트 YAML 로드"""
        kit_path = (
            Path(__file__).parent / "agent_kits" / "copilot_coding_booster_kit.yaml"
        )
        if not kit_path.exists():
            print(f"⚠️  에이전트 키트를 찾을 수 없습니다: {kit_path}")
            return {}

        try:
            with open(kit_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 에이전트 키트 로드 실패: {e}")
            return {}

    def get_project_context(self) -> Dict[str, Any]:
        """현재 프로젝트 컨텍스트 분석"""
        context = {
            "project_type": "unknown",
            "current_architecture": "monolithic",
            "tech_stack": [],
            "project_timeline": "ongoing",
            "constraints": [],
        }

        # 파일 확장자 분석
        file_types = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                ignore in str(file_path)
                for ignore in [".git", "node_modules", "__pycache__"]
            ):
                ext = file_path.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1

        # 주요 언어 결정
        if file_types.get(".py", 0) > 0:
            context["tech_stack"].append("Python")
            if (self.project_root / "requirements.txt").exists():
                context["tech_stack"].append("pip")
            if any("django" in f.name.lower() for f in self.project_root.rglob("*.py")):
                context["tech_stack"].append("Django")
            elif any(
                "flask" in f.name.lower() for f in self.project_root.rglob("*.py")
            ):
                context["tech_stack"].append("Flask")

        if file_types.get(".js", 0) > 0 or file_types.get(".ts", 0) > 0:
            context["tech_stack"].append("JavaScript/TypeScript")
            if (self.project_root / "package.json").exists():
                context["tech_stack"].append("Node.js")

        # 프로젝트 타입 추측
        if "Django" in context["tech_stack"] or "Flask" in context["tech_stack"]:
            context["project_type"] = "web_application"
        elif "Node.js" in context["tech_stack"]:
            context["project_type"] = "web_application"
        elif file_types.get(".py", 0) > file_types.get(".js", 0):
            context["project_type"] = "python_application"

        return context

    def strategic_planner(self, requirements: str) -> str:
        """전략 기획 에이전트"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # strategic_planner_quantum 에이전트 찾기
        planner_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "strategic_planner_quantum":
                planner_agent = agent
                break

        if not planner_agent:
            return "전략 기획 에이전트를 찾을 수 없습니다."

        context = self.get_project_context()

        # 프롬프트 템플릿에 컨텍스트 적용
        prompt = planner_agent["prompt_template"].format(
            meta_architecture_context="현재 프로젝트 분석 완료",
            predictive_analysis_results="기술 스택 및 프로젝트 타입 식별됨",
            strategic_requirements=requirements,
        )

        return f"""🧠 **양자급 전략 기획자**

{prompt}

---
💡 **실행 방법:** 위 분석 내용을 Claude에게 복사해서 붙여넣으세요!

**현재 프로젝트 컨텍스트:**
- 프로젝트 타입: {context['project_type']}
- 기술 스택: {', '.join(context['tech_stack'])}
- 프로젝트 경로: {self.project_root}
"""

    def architecture_designer(self, requirements: str) -> str:
        """아키텍처 설계 에이전트"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # autonomous_architect 에이전트 찾기
        arch_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "autonomous_architect":
                arch_agent = agent
                break

        if not arch_agent:
            return "아키텍처 설계 에이전트를 찾을 수 없습니다."

        context = self.get_project_context()

        # 시스템 프로파일 생성
        system_profile = {
            "traffic_patterns": "일반적인 웹 트래픽",
            "resource_metrics": "CPU/메모리 사용량 보통",
            "failure_history": "없음",
            "growth_data": "초기 단계",
            "usage_patterns": "개발 단계",
        }

        prompt = arch_agent["prompt_template"].format(
            strategic_plan_quantum="전략 기획 완료",
            traffic_analysis=system_profile["traffic_patterns"],
            resource_metrics=system_profile["resource_metrics"],
            failure_history=system_profile["failure_history"],
            growth_data=system_profile["growth_data"],
            usage_patterns=system_profile["usage_patterns"],
        )

        return f"""🏗️ **자율 진화 아키텍처 설계자**

{prompt}

---
💡 **실행 방법:** 위 설계 요청을 Claude에게 제출하세요!

**요구사항:** {requirements}
"""

    def code_generator(self, requirements: str, language: str = "Python") -> str:
        """하이퍼 코드 생성기"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # hyper_code_generator 에이전트 찾기
        gen_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "hyper_code_generator":
                gen_agent = agent
                break

        if not gen_agent:
            return "코드 생성 에이전트를 찾을 수 없습니다."

        context = self.get_project_context()

        # 입력 소스 분석
        input_sources = {
            "natural_language": requirements,
            "voice_commands": "없음",
            "ui_analysis": "없음",
            "diagram_interpretation": "없음",
            "codebase_patterns": ", ".join(context["tech_stack"]),
        }

        prompt = gen_agent["prompt_template"].format(
            autonomous_architecture="현재 프로젝트 구조 분석 완료",
            nl_requirements=input_sources["natural_language"],
            transcribed_voice=input_sources["voice_commands"],
            ui_analysis=input_sources["ui_analysis"],
            diagram_interpretation=input_sources["diagram_interpretation"],
            codebase_patterns=input_sources["codebase_patterns"],
        )

        return f"""⚡ **하이퍼 지능형 코드 생성기**

{prompt}

---
💡 **실행 방법:** 위 생성 요청을 Claude에게 제출하여 {language} 코드를 생성받으세요!

**요구사항:** {requirements}
**대상 언어:** {language}
"""

    def debug_analyzer(self, file_path: str, error_msg: str = "") -> str:
        """양자 디버깅 시스템"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # quantum_debugger 에이전트 찾기
        debug_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "quantum_debugger":
                debug_agent = agent
                break

        if not debug_agent:
            return "디버깅 에이전트를 찾을 수 없습니다."

        # 파일이 존재하는지 확인
        target_file = Path(file_path)
        if not target_file.exists():
            return f"❌ 파일을 찾을 수 없습니다: {file_path}"

        # 파일 내용 읽기 (처음 50줄만)
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                file_content = "".join(f.readlines()[:50])
        except Exception as e:
            file_content = f"파일 읽기 실패: {e}"

        context = self.get_project_context()
        language = (
            "Python"
            if target_file.suffix == ".py"
            else "JavaScript" if target_file.suffix in [".js", ".ts"] else "Unknown"
        )

        prompt = debug_agent["prompt_template"].format(
            language=language,
            target_code=file_content,
            input_space_size="중간",
            execution_complexity="보통",
            state_space_size="보통",
            concurrency_level="단일 스레드",
        )

        return f"""🔬 **양자 디버깅 시스템**

**파일:** {file_path}
**에러:** {error_msg if error_msg else "일반 분석"}

{prompt}

---
💡 **실행 방법:** 
1. 위 디버깅 요청을 Claude에게 제출
2. 파일 전체 내용도 함께 제공하면 더 정확한 분석 가능

**파일 내용 (처음 50줄):**
```{language.lower()}
{file_content}
```
"""

    def test_generator(self, file_path: str) -> str:
        """자율 테스트 진화 시스템"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # autonomous_test_evolution 에이전트 찾기
        test_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "autonomous_test_evolution":
                test_agent = agent
                break

        if not test_agent:
            return "테스트 생성 에이전트를 찾을 수 없습니다."

        target_file = Path(file_path)
        if not target_file.exists():
            return f"❌ 파일을 찾을 수 없습니다: {file_path}"

        # 파일 내용 읽기
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"파일 읽기 실패: {e}"

        language = (
            "Python"
            if target_file.suffix == ".py"
            else "JavaScript" if target_file.suffix in [".js", ".ts"] else "Unknown"
        )

        prompt = test_agent["prompt_template"].format(
            language=language,
            target_code=file_content,
            evolution_generations="50",
            population_size="20",
            mutation_rate="0.1",
            selection_pressure="0.7",
        )

        return f"""🧪 **자율 테스트 진화 시스템**

**테스트 대상:** {file_path}

{prompt}

---
💡 **실행 방법:** 위 테스트 생성 요청을 Claude에게 제출하세요!
"""

    def performance_optimizer(self, file_path: str) -> str:
        """하이퍼 성능 최적화 엔진"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # hyper_performance_engine 에이전트 찾기
        perf_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "hyper_performance_engine":
                perf_agent = agent
                break

        if not perf_agent:
            return "성능 최적화 에이전트를 찾을 수 없습니다."

        target_file = Path(file_path)
        if not target_file.exists():
            return f"❌ 파일을 찾을 수 없습니다: {file_path}"

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"파일 읽기 실패: {e}"

        language = (
            "Python"
            if target_file.suffix == ".py"
            else "JavaScript" if target_file.suffix in [".js", ".ts"] else "Unknown"
        )

        prompt = perf_agent["prompt_template"].format(
            language=language,
            performance_target_code=file_content,
            cpu_target="30",
            memory_target="40",
            latency_target="100",
            throughput_target="1000",
            power_target="20",
        )

        return f"""🚀 **하이퍼 성능 최적화 엔진**

**최적화 대상:** {file_path}

{prompt}

---
💡 **실행 방법:** 위 최적화 요청을 Claude에게 제출하세요!
"""

    def security_guardian(self, file_path: str = None) -> str:
        """양자 보안 가디언"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # quantum_security_guardian 에이전트 찾기
        sec_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "quantum_security_guardian":
                sec_agent = agent
                break

        if not sec_agent:
            return "보안 가디언 에이전트를 찾을 수 없습니다."

        if file_path:
            target_file = Path(file_path)
            if not target_file.exists():
                return f"❌ 파일을 찾을 수 없습니다: {file_path}"

            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception as e:
                file_content = f"파일 읽기 실패: {e}"

            language = (
                "Python"
                if target_file.suffix == ".py"
                else "JavaScript" if target_file.suffix in [".js", ".ts"] else "Unknown"
            )
        else:
            file_content = "전체 프로젝트"
            language = "Mixed"

        context = self.get_project_context()

        prompt = sec_agent["prompt_template"].format(
            language=language,
            security_target_code=file_content,
            threat_model="웹 애플리케이션 일반",
            regulatory_requirements="GDPR, OWASP",
            data_classification="일반",
            quantum_threat_timeline="5-10년",
        )

        return f"""🔒 **양자 보안 가디언**

**보안 감사 대상:** {file_path if file_path else "전체 프로젝트"}

{prompt}

---
💡 **실행 방법:** 위 보안 분석 요청을 Claude에게 제출하세요!
"""

    def doc_generator(self, file_path: str) -> str:
        """지능형 문서 생태계"""
        if not self.agent_kit:
            return "에이전트 키트를 로드할 수 없습니다."

        # intelligent_doc_ecosystem 에이전트 찾기
        doc_agent = None
        for agent in self.agent_kit.get("agents", []):
            if agent["id"] == "intelligent_doc_ecosystem":
                doc_agent = agent
                break

        if not doc_agent:
            return "문서 생성 에이전트를 찾을 수 없습니다."

        target_file = Path(file_path)
        if not target_file.exists():
            return f"❌ 파일을 찾을 수 없습니다: {file_path}"

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"파일 읽기 실패: {e}"

        language = (
            "Python"
            if target_file.suffix == ".py"
            else "JavaScript" if target_file.suffix in [".js", ".ts"] else "Unknown"
        )

        prompt = doc_agent["prompt_template"].format(
            language=language,
            documentation_target=file_content,
            audience="developers",
            media_type="텍스트",
            interaction_level="동적",
            languages="한국어, 영어",
        )

        return f"""📚 **지능형 문서 생태계**

**문서화 대상:** {file_path}

{prompt}

---
💡 **실행 방법:** 위 문서 생성 요청을 Claude에게 제출하세요!
"""


def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print(
            """
🚀 **QuickDev - Claude Code 전용 개발 도우미**

사용법: python quick_dev.py <명령> [옵션]

**사용 가능한 명령:**
  plan <요구사항>          - 전략적 개발 기획
  arch <요구사항>          - 아키텍처 설계
  code <요구사항> [언어]   - 코드 자동 생성
  debug <파일경로> [에러]  - 버그 분석 및 디버깅
  test <파일경로>          - 테스트 코드 생성
  perf <파일경로>          - 성능 최적화 분석
  sec [파일경로]           - 보안 취약점 분석
  doc <파일경로>           - 문서 자동 생성

**사용 예시:**
  python quick_dev.py plan "웹 할일 관리 앱을 만들고 싶어요"
  python quick_dev.py code "사용자 로그인 기능" Python
  python quick_dev.py debug main.py "ImportError 발생"
  python quick_dev.py test user_service.py
  python quick_dev.py sec
        """
        )
        return

    command = sys.argv[1]
    dev = QuickDev()

    try:
        if command == "plan":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py plan <요구사항>")
                return
            requirements = " ".join(sys.argv[2:])
            result = dev.strategic_planner(requirements)

        elif command == "arch":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py arch <요구사항>")
                return
            requirements = " ".join(sys.argv[2:])
            result = dev.architecture_designer(requirements)

        elif command == "code":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py code <요구사항> [언어]")
                return
            requirements = sys.argv[2]
            language = sys.argv[3] if len(sys.argv) > 3 else "Python"
            result = dev.code_generator(requirements, language)

        elif command == "debug":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py debug <파일경로> [에러메시지]")
                return
            file_path = sys.argv[2]
            error_msg = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
            result = dev.debug_analyzer(file_path, error_msg)

        elif command == "test":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py test <파일경로>")
                return
            file_path = sys.argv[2]
            result = dev.test_generator(file_path)

        elif command == "perf":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py perf <파일경로>")
                return
            file_path = sys.argv[2]
            result = dev.performance_optimizer(file_path)

        elif command == "sec":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            result = dev.security_guardian(file_path)

        elif command == "doc":
            if len(sys.argv) < 3:
                print("사용법: python quick_dev.py doc <파일경로>")
                return
            file_path = sys.argv[2]
            result = dev.doc_generator(file_path)

        else:
            print(f"❌ 알 수 없는 명령: {command}")
            return

        print(result)

    except Exception as e:
        print(f"❌ 에러 발생: {e}")


if __name__ == "__main__":
    main()
