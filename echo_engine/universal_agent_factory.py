#!/usr/bin/env python3
"""
🏭 Universal Agent Factory - 전영역 에이전트 자동 생성 시스템
Echo 시스템을 위한 무제한 에이전트 생성 및 배치 엔진

핵심 기능:
- 자연어 요청 기반 에이전트 자동 설계
- 전영역 커버리지 (웹, 앱, 데스크탑, 문서, API, 시뮬레이션 등)
- 에이전트 간 협업 및 루프 통합
- 동적 에이전트 최적화 및 진화
"""

import yaml
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib
import inspect


@dataclass
class AgentBlueprint:
    """에이전트 설계도"""

    agent_id: str
    agent_name: str
    domain: str  # web, mobile, desktop, document, api, simulation 등
    capabilities: List[str]
    dependencies: List[str]
    interfaces: Dict[str, str]
    config_template: Dict[str, Any]
    code_template: str
    test_scenarios: List[str]


@dataclass
class AgentInstance:
    """에이전트 인스턴스"""

    instance_id: str
    blueprint_id: str
    status: str  # active, inactive, error, testing
    performance_metrics: Dict[str, float]
    last_execution: Optional[datetime]
    execution_count: int
    success_rate: float


class UniversalAgentFactory:
    """🏭 범용 에이전트 팩토리"""

    def __init__(
        self, config_path: str = "echo_engine/config/agent_factory_config.yaml"
    ):
        self.config_path = config_path
        self.config = self._load_config()

        # 에이전트 도메인 정의
        self.agent_domains = {
            "web": ["search", "scraping", "automation", "monitoring", "testing"],
            "mobile": ["ui_testing", "automation", "app_analysis", "performance"],
            "desktop": ["file_management", "automation", "monitoring", "backup"],
            "document": ["generation", "parsing", "conversion", "analysis"],
            "api": ["integration", "testing", "monitoring", "documentation"],
            "simulation": ["scenario_testing", "policy_modeling", "prediction"],
            "communication": ["email", "slack", "discord", "social_media"],
            "finance": ["trading", "analysis", "reporting", "risk_assessment"],
            "research": ["data_collection", "analysis", "summarization"],
            "creative": ["content_generation", "design", "music", "video"],
            "security": ["vulnerability_scan", "monitoring", "compliance"],
            "devops": ["deployment", "monitoring", "logging", "scaling"],
        }

        # 에이전트 템플릿 라이브러리
        self.agent_templates = self._load_agent_templates()

        # 활성 에이전트 레지스트리
        self.active_agents: Dict[str, AgentInstance] = {}

        # 에이전트 성능 추적
        self.performance_tracker = {}

    def _load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        return {
            "max_concurrent_agents": 50,
            "auto_cleanup_inactive": True,
            "performance_threshold": 0.7,
            "evolution_enabled": True,
        }

    def _load_agent_templates(self) -> Dict[str, str]:
        """에이전트 코드 템플릿 로드"""
        return {
            "web_agent": '''
class {agent_name}(WebAgent):
    """🌐 {description}"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.capabilities = {capabilities}

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """주요 실행 로직"""
        try:
            # {execution_logic}
            return {{
                "success": True,
                "result": "Task completed",
                "metrics": self.get_performance_metrics()
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e),
                "metrics": self.get_performance_metrics()
            }}

    def validate_input(self, task: str) -> bool:
        """입력 검증"""
        return len(task.strip()) > 0

    def get_performance_metrics(self) -> Dict[str, float]:
        """성능 메트릭 수집"""
        return {{
            "execution_time": 0.0,
            "success_rate": 1.0,
            "resource_usage": 0.1
        }}
''',
            "document_agent": '''
class {agent_name}(DocumentAgent):
    """📄 {description}"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_formats = {supported_formats}

    def process_document(self, doc_path: str, operation: str) -> Dict[str, Any]:
        """문서 처리"""
        try:
            # {processing_logic}
            return {{
                "success": True,
                "output_path": "processed_document.pdf",
                "metrics": self.get_performance_metrics()
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}

    def convert_format(self, source: str, target_format: str) -> str:
        """포맷 변환"""
        # 변환 로직 구현
        return f"converted.{{target_format}}"
''',
            "api_agent": '''
class {agent_name}(APIAgent):
    """🔗 {description}"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoints = {endpoints}

    def call_api(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """API 호출"""
        try:
            # {api_logic}
            return {{
                "success": True,
                "data": {{}},
                "status_code": 200
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e),
                "status_code": 500
            }}

    def authenticate(self) -> bool:
        """인증 처리"""
        return True
''',
            "simulation_agent": '''
class {agent_name}(SimulationAgent):
    """🧪 {description}"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.simulation_type = "{simulation_type}"

    def run_simulation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """시뮬레이션 실행"""
        try:
            # {simulation_logic}
            return {{
                "success": True,
                "results": {{}},
                "insights": [],
                "confidence": 0.85
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}

    def analyze_results(self, results: Dict[str, Any]) -> List[str]:
        """결과 분석"""
        return ["Analysis insight 1", "Analysis insight 2"]
''',
        }

    def analyze_agent_request(self, request: str) -> Dict[str, Any]:
        """자연어 요청 분석하여 에이전트 요구사항 추출"""

        # 키워드 기반 도메인 감지
        domain_keywords = {
            "web": ["웹", "브라우저", "사이트", "크롤링", "스크래핑", "검색"],
            "mobile": ["앱", "모바일", "안드로이드", "iOS", "테스트"],
            "desktop": ["파일", "폴더", "윈도우", "맥", "자동화"],
            "document": ["문서", "PDF", "워드", "엑셀", "변환"],
            "api": ["API", "연동", "호출", "REST", "GraphQL"],
            "simulation": ["시뮬레이션", "모델링", "예측", "시나리오"],
            "communication": ["이메일", "슬랙", "메시지", "알림"],
            "finance": ["투자", "주식", "금융", "거래", "분석"],
            "research": ["조사", "연구", "데이터", "분석"],
            "creative": ["생성", "창작", "디자인", "콘텐츠"],
        }

        detected_domain = "general"
        for domain, keywords in domain_keywords.items():
            if any(keyword in request for keyword in keywords):
                detected_domain = domain
                break

        # 동작 키워드 감지
        action_keywords = {
            "collect": ["수집", "가져오", "크롤링", "스크래핑"],
            "analyze": ["분석", "해석", "평가", "검토"],
            "generate": ["생성", "만들", "작성", "제작"],
            "monitor": ["모니터링", "추적", "감시", "확인"],
            "automate": ["자동화", "자동", "스케줄"],
            "convert": ["변환", "바꾸", "포맷"],
            "test": ["테스트", "검증", "확인"],
            "integrate": ["연동", "통합", "연결"],
        }

        detected_actions = []
        for action, keywords in action_keywords.items():
            if any(keyword in request for keyword in keywords):
                detected_actions.append(action)

        return {
            "domain": detected_domain,
            "actions": detected_actions or ["execute"],
            "complexity": "medium",  # 추후 더 정교한 분석 가능
            "urgency": "normal",
            "requirements": self._extract_requirements(request),
        }

    def _extract_requirements(self, request: str) -> Dict[str, Any]:
        """요청에서 구체적 요구사항 추출"""
        requirements = {
            "input_types": [],
            "output_types": [],
            "constraints": [],
            "dependencies": [],
        }

        # 입력 타입 감지
        if any(word in request for word in ["파일", "문서", "데이터"]):
            requirements["input_types"].append("file")
        if any(word in request for word in ["URL", "웹사이트", "주소"]):
            requirements["input_types"].append("url")
        if any(word in request for word in ["텍스트", "문장", "글"]):
            requirements["input_types"].append("text")

        # 출력 타입 감지
        if any(word in request for word in ["보고서", "리포트"]):
            requirements["output_types"].append("report")
        if any(word in request for word in ["파일", "저장"]):
            requirements["output_types"].append("file")
        if any(word in request for word in ["알림", "메시지"]):
            requirements["output_types"].append("notification")

        return requirements

    def design_agent_blueprint(self, request: str) -> AgentBlueprint:
        """요청 기반 에이전트 설계도 생성"""

        analysis = self.analyze_agent_request(request)
        domain = analysis["domain"]
        actions = analysis["actions"]

        # 고유 ID 생성
        agent_id = f"{domain}_{actions[0]}_{int(datetime.now().timestamp())}"
        agent_name = f"{domain.title()}{actions[0].title()}Agent"

        # 능력 정의
        capabilities = []
        if domain in self.agent_domains:
            capabilities.extend(self.agent_domains[domain])
        capabilities.extend(actions)

        # 의존성 결정
        dependencies = []
        if domain == "web":
            dependencies.extend(["requests", "beautifulsoup4", "selenium"])
        elif domain == "document":
            dependencies.extend(["pypdf2", "python-docx", "openpyxl"])
        elif domain == "api":
            dependencies.extend(["requests", "aiohttp"])

        # 인터페이스 정의
        interfaces = {
            "input": "Dict[str, Any]",
            "output": "Dict[str, Any]",
            "config": "Dict[str, Any]",
        }

        # 설정 템플릿
        config_template = {
            "name": agent_name,
            "domain": domain,
            "version": "1.0.0",
            "timeout": 30,
            "retry_count": 3,
            "log_level": "INFO",
        }

        # 코드 템플릿 선택 및 커스터마이징
        if domain in self.agent_templates:
            code_template = self.agent_templates[domain + "_agent"]
        else:
            code_template = self.agent_templates["web_agent"]  # 기본 템플릿

        # 테스트 시나리오
        test_scenarios = [
            "기본 실행 테스트",
            "오류 처리 테스트",
            "성능 벤치마크 테스트",
        ]

        return AgentBlueprint(
            agent_id=agent_id,
            agent_name=agent_name,
            domain=domain,
            capabilities=capabilities,
            dependencies=dependencies,
            interfaces=interfaces,
            config_template=config_template,
            code_template=code_template,
            test_scenarios=test_scenarios,
        )

    def generate_agent_code(self, blueprint: AgentBlueprint) -> str:
        """설계도 기반 에이전트 코드 생성"""

        template = blueprint.code_template

        # 템플릿 변수 치환
        code = template.format(
            agent_name=blueprint.agent_name,
            description=f"{blueprint.domain} 도메인 에이전트",
            capabilities=blueprint.capabilities,
            execution_logic="# 실행 로직 구현 필요",
            processing_logic="# 처리 로직 구현 필요",
            api_logic="# API 로직 구현 필요",
            simulation_logic="# 시뮬레이션 로직 구현 필요",
            simulation_type=blueprint.domain,
            supported_formats='["pdf", "docx", "xlsx"]',
            endpoints="{}",
        )

        # 필요한 import 문 추가
        imports = self._generate_imports(blueprint)

        full_code = f"""#!/usr/bin/env python3
\"\"\"
🤖 {blueprint.agent_name} - Auto-generated Agent
Domain: {blueprint.domain}
Capabilities: {', '.join(blueprint.capabilities)}
Generated: {datetime.now().isoformat()}
\"\"\"

{imports}

{code}

# Agent Registration
AGENT_INFO = {{
    "id": "{blueprint.agent_id}",
    "name": "{blueprint.agent_name}",
    "domain": "{blueprint.domain}",
    "capabilities": {blueprint.capabilities},
    "version": "1.0.0"
}}

if __name__ == "__main__":
    # 에이전트 테스트 실행
    agent = {blueprint.agent_name}({blueprint.config_template})
    print(f"🤖 {{agent.name}} 에이전트 준비 완료")
"""

        return full_code

    def _generate_imports(self, blueprint: AgentBlueprint) -> str:
        """필요한 import 문 생성"""
        imports = [
            "import os",
            "import json",
            "import yaml",
            "from datetime import datetime",
            "from typing import Dict, Any, List, Optional",
            "from dataclasses import dataclass",
        ]

        # 도메인별 추가 import
        if blueprint.domain == "web":
            imports.extend(
                [
                    "import requests",
                    "from bs4 import BeautifulSoup",
                    "try:",
                    "    from selenium import webdriver",
                    "except ImportError:",
                    "    webdriver = None",
                ]
            )
        elif blueprint.domain == "document":
            imports.extend(
                [
                    "try:",
                    "    import PyPDF2",
                    "    from docx import Document",
                    "    import openpyxl",
                    "except ImportError:",
                    "    pass  # Optional dependencies",
                ]
            )
        elif blueprint.domain == "api":
            imports.extend(
                [
                    "import requests",
                    "import asyncio",
                    "try:",
                    "    import aiohttp",
                    "except ImportError:",
                    "    aiohttp = None",
                ]
            )

        return "\n".join(imports)

    def create_agent(self, request: str) -> Dict[str, Any]:
        """자연어 요청으로부터 에이전트 생성"""

        try:
            # 1. 요청 분석 및 설계도 생성
            blueprint = self.design_agent_blueprint(request)

            # 2. 코드 생성
            agent_code = self.generate_agent_code(blueprint)

            # 3. 파일로 저장
            agent_file_path = f"echo_engine/agents/{blueprint.agent_id}.py"
            os.makedirs(os.path.dirname(agent_file_path), exist_ok=True)

            with open(agent_file_path, "w", encoding="utf-8") as f:
                f.write(agent_code)

            # 4. 설정 파일 저장
            config_file_path = (
                f"echo_engine/agents/config/{blueprint.agent_id}_config.yaml"
            )
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

            with open(config_file_path, "w", encoding="utf-8") as f:
                yaml.dump(blueprint.config_template, f, allow_unicode=True)

            # 5. 에이전트 인스턴스 등록
            instance = AgentInstance(
                instance_id=blueprint.agent_id,
                blueprint_id=blueprint.agent_id,
                status="created",
                performance_metrics={},
                last_execution=None,
                execution_count=0,
                success_rate=0.0,
            )

            self.active_agents[blueprint.agent_id] = instance

            # 6. 에이전트 레지스트리 업데이트
            self._update_agent_registry(blueprint)

            return {
                "success": True,
                "agent_id": blueprint.agent_id,
                "agent_name": blueprint.agent_name,
                "file_path": agent_file_path,
                "config_path": config_file_path,
                "capabilities": blueprint.capabilities,
                "message": f"🤖 {blueprint.agent_name} 에이전트가 성공적으로 생성되었습니다!",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"⚠️ 에이전트 생성 실패: {e}",
            }

    def _update_agent_registry(self, blueprint: AgentBlueprint):
        """에이전트 레지스트리 업데이트"""
        registry_path = "echo_engine/agents/agent_registry.yaml"

        # 기존 레지스트리 로드
        if os.path.exists(registry_path):
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = yaml.safe_load(f) or {}
        else:
            registry = {"agents": {}, "domains": {}, "last_updated": None}

        # 새 에이전트 추가
        registry["agents"][blueprint.agent_id] = {
            "name": blueprint.agent_name,
            "domain": blueprint.domain,
            "capabilities": blueprint.capabilities,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "file_path": f"echo_engine/agents/{blueprint.agent_id}.py",
        }

        # 도메인별 분류 업데이트
        if blueprint.domain not in registry["domains"]:
            registry["domains"][blueprint.domain] = []
        registry["domains"][blueprint.domain].append(blueprint.agent_id)

        registry["last_updated"] = datetime.now().isoformat()

        # 레지스트리 저장
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        with open(registry_path, "w", encoding="utf-8") as f:
            yaml.dump(registry, f, allow_unicode=True, default_flow_style=False)

    def list_available_agents(self) -> Dict[str, Any]:
        """사용 가능한 에이전트 목록 조회"""
        registry_path = "echo_engine/agents/agent_registry.yaml"

        if not os.path.exists(registry_path):
            return {"agents": {}, "domains": {}, "total_count": 0}

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)

        return {
            "agents": registry.get("agents", {}),
            "domains": registry.get("domains", {}),
            "total_count": len(registry.get("agents", {})),
            "last_updated": registry.get("last_updated"),
        }

    def get_agent_suggestions(self, task_description: str) -> List[Dict[str, Any]]:
        """작업 설명에 따른 에이전트 추천"""
        analysis = self.analyze_agent_request(task_description)
        registry = self.list_available_agents()

        suggestions = []

        # 기존 에이전트 중 적합한 것 찾기
        for agent_id, agent_info in registry["agents"].items():
            if agent_info["domain"] == analysis["domain"]:
                match_score = len(
                    set(agent_info["capabilities"]) & set(analysis["actions"])
                ) / len(analysis["actions"])
                suggestions.append(
                    {
                        "agent_id": agent_id,
                        "agent_name": agent_info["name"],
                        "match_score": match_score,
                        "reason": f"{analysis['domain']} 도메인 전문",
                        "existing": True,
                    }
                )

        # 새 에이전트 생성 제안
        if not suggestions or max(s["match_score"] for s in suggestions) < 0.7:
            suggestions.append(
                {
                    "agent_id": "new_agent",
                    "agent_name": f"Custom{analysis['domain'].title()}Agent",
                    "match_score": 1.0,
                    "reason": "맞춤형 새 에이전트 생성 권장",
                    "existing": False,
                }
            )

        return sorted(suggestions, key=lambda x: x["match_score"], reverse=True)

    def execute_agent_creation_flow(self, request: str) -> Dict[str, Any]:
        """에이전트 생성 플로우 실행"""

        print(f"🏭 에이전트 생성 요청 분석 중: {request}")

        # 1. 기존 에이전트 확인
        suggestions = self.get_agent_suggestions(request)

        print(f"💡 적합한 에이전트 후보 {len(suggestions)}개 발견")
        for i, suggestion in enumerate(suggestions[:3]):
            print(
                f"  {i+1}. {suggestion['agent_name']} (적합도: {suggestion['match_score']:.0%})"
            )

        # 2. 새 에이전트 생성 여부 결정
        best_match = suggestions[0] if suggestions else None

        if best_match and best_match["existing"] and best_match["match_score"] > 0.8:
            return {
                "action": "use_existing",
                "agent_id": best_match["agent_id"],
                "agent_name": best_match["agent_name"],
                "message": f"기존 {best_match['agent_name']} 에이전트 사용을 권장합니다.",
            }
        else:
            # 3. 새 에이전트 생성
            creation_result = self.create_agent(request)
            if creation_result["success"]:
                return {"action": "created_new", **creation_result}
            else:
                return creation_result


def create_agent_from_request(request: str) -> Dict[str, Any]:
    """자연어 요청으로부터 에이전트 생성 (편의 함수)"""
    factory = UniversalAgentFactory()
    return factory.execute_agent_creation_flow(request)


if __name__ == "__main__":
    # 테스트 실행
    factory = UniversalAgentFactory()

    # 테스트 요청들
    test_requests = [
        "웹에서 뉴스 수집하는 에이전트 만들어줘",
        "PDF 문서를 워드로 변환하는 에이전트 필요해",
        "주식 가격을 모니터링하는 에이전트 생성해줘",
        "이메일 자동 발송 에이전트 만들어줘",
    ]

    for request in test_requests:
        print(f"\n{'='*60}")
        result = factory.execute_agent_creation_flow(request)
        print(f"결과: {result.get('message', 'Unknown')}")
