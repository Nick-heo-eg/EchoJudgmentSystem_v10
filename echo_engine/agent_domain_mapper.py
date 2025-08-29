#!/usr/bin/env python3
"""
🗺️ Agent Domain Mapper - 전영역 에이전트 도메인 매핑 시스템
Echo 시스템의 모든 가능한 에이전트 영역과 기능을 체계적으로 분류 및 관리

핵심 기능:
- 전 영역 에이전트 도메인 정의 및 분류
- 도메인별 기능 매트릭스 관리
- 에이전트 간 의존성 및 협업 관계 매핑
- 확장 가능한 도메인 아키텍처 제공
"""

import yaml
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DomainCapability:
    """도메인 역량 정의"""

    name: str
    description: str
    complexity_level: str  # basic, intermediate, advanced, expert
    dependencies: List[str]
    interfaces: List[str]
    use_cases: List[str]


@dataclass
class AgentDomain:
    """에이전트 도메인 정의"""

    domain_id: str
    domain_name: str
    category: str
    description: str
    capabilities: List[DomainCapability]
    typical_agents: List[str]
    integration_points: List[str]
    scalability: str


class AgentDomainMapper:
    """🗺️ 에이전트 도메인 매퍼"""

    def __init__(self):
        self.domain_registry = self._initialize_domain_registry()
        self.capability_matrix = self._build_capability_matrix()
        self.collaboration_graph = self._build_collaboration_graph()

    def _initialize_domain_registry(self) -> Dict[str, AgentDomain]:
        """전체 도메인 레지스트리 초기화"""

        domains = {}

        # 🌐 웹 도메인
        domains["web"] = AgentDomain(
            domain_id="web",
            domain_name="웹 자동화",
            category="digital_interaction",
            description="웹 브라우저 기반 모든 작업 자동화",
            capabilities=[
                DomainCapability(
                    name="web_scraping",
                    description="웹 페이지 데이터 수집",
                    complexity_level="intermediate",
                    dependencies=["requests", "beautifulsoup4"],
                    interfaces=["http_client", "html_parser"],
                    use_cases=["뉴스 수집", "가격 모니터링", "콘텐츠 크롤링"],
                ),
                DomainCapability(
                    name="browser_automation",
                    description="브라우저 자동 조작",
                    complexity_level="advanced",
                    dependencies=["selenium", "playwright"],
                    interfaces=["webdriver", "dom_manipulation"],
                    use_cases=["폼 자동 입력", "UI 테스트", "자동 로그인"],
                ),
                DomainCapability(
                    name="web_monitoring",
                    description="웹사이트 상태 모니터링",
                    complexity_level="basic",
                    dependencies=["requests", "schedule"],
                    interfaces=["http_monitor", "alert_system"],
                    use_cases=["사이트 다운 감지", "성능 모니터링", "변화 감지"],
                ),
            ],
            typical_agents=[
                "WebScraperAgent",
                "BrowserAutomationAgent",
                "WebMonitorAgent",
            ],
            integration_points=["api_gateway", "database", "notification_system"],
            scalability="high",
        )

        # 📱 모바일 도메인
        domains["mobile"] = AgentDomain(
            domain_id="mobile",
            domain_name="모바일 앱 자동화",
            category="mobile_interaction",
            description="모바일 앱 테스트 및 자동화",
            capabilities=[
                DomainCapability(
                    name="ui_automation",
                    description="모바일 UI 자동 조작",
                    complexity_level="advanced",
                    dependencies=["appium", "uiautomator2"],
                    interfaces=["mobile_driver", "touch_interface"],
                    use_cases=["앱 테스트", "자동 입력", "기능 검증"],
                ),
                DomainCapability(
                    name="app_analysis",
                    description="앱 성능 및 구조 분석",
                    complexity_level="expert",
                    dependencies=["frida", "android_tools"],
                    interfaces=["debug_interface", "analysis_tools"],
                    use_cases=["성능 분석", "보안 검사", "리버스 엔지니어링"],
                ),
            ],
            typical_agents=[
                "MobileUIAgent",
                "AppTestAgent",
                "PerformanceAnalyzerAgent",
            ],
            integration_points=["device_farm", "test_reporting", "ci_cd"],
            scalability="medium",
        )

        # 🖥️ 데스크탑 도메인
        domains["desktop"] = AgentDomain(
            domain_id="desktop",
            domain_name="데스크탑 자동화",
            category="system_interaction",
            description="데스크탑 환경에서의 모든 작업 자동화",
            capabilities=[
                DomainCapability(
                    name="file_management",
                    description="파일 및 폴더 관리",
                    complexity_level="basic",
                    dependencies=["pathlib", "shutil"],
                    interfaces=["filesystem", "file_operations"],
                    use_cases=["파일 정리", "백업", "동기화"],
                ),
                DomainCapability(
                    name="gui_automation",
                    description="GUI 애플리케이션 자동화",
                    complexity_level="intermediate",
                    dependencies=["pyautogui", "pygetwindow"],
                    interfaces=["window_manager", "input_simulator"],
                    use_cases=["레거시 앱 자동화", "데이터 입력", "UI 테스트"],
                ),
                DomainCapability(
                    name="system_monitoring",
                    description="시스템 리소스 모니터링",
                    complexity_level="intermediate",
                    dependencies=["psutil", "wmi"],
                    interfaces=["system_api", "performance_counters"],
                    use_cases=["성능 모니터링", "리소스 최적화", "장애 감지"],
                ),
            ],
            typical_agents=[
                "FileManagerAgent",
                "GUIAutomationAgent",
                "SystemMonitorAgent",
            ],
            integration_points=["log_aggregator", "alert_system", "dashboard"],
            scalability="medium",
        )

        # 📄 문서 처리 도메인
        domains["document"] = AgentDomain(
            domain_id="document",
            domain_name="문서 처리",
            category="content_processing",
            description="다양한 형태의 문서 생성, 변환, 분석",
            capabilities=[
                DomainCapability(
                    name="document_generation",
                    description="자동 문서 생성",
                    complexity_level="intermediate",
                    dependencies=["reportlab", "python-docx", "openpyxl"],
                    interfaces=["template_engine", "format_converter"],
                    use_cases=["보고서 생성", "계약서 작성", "송장 발행"],
                ),
                DomainCapability(
                    name="document_parsing",
                    description="문서 내용 추출 및 분석",
                    complexity_level="advanced",
                    dependencies=["pypdf2", "pdfplumber", "python-docx"],
                    interfaces=["text_extractor", "structure_analyzer"],
                    use_cases=["데이터 추출", "내용 분석", "메타데이터 수집"],
                ),
                DomainCapability(
                    name="format_conversion",
                    description="문서 형식 변환",
                    complexity_level="basic",
                    dependencies=["pandoc", "libreoffice"],
                    interfaces=["format_converter", "batch_processor"],
                    use_cases=["PDF→Word", "Excel→CSV", "Markdown→HTML"],
                ),
            ],
            typical_agents=[
                "DocumentGeneratorAgent",
                "PDFParserAgent",
                "FormatConverterAgent",
            ],
            integration_points=["storage_system", "workflow_engine", "quality_checker"],
            scalability="high",
        )

        # 🔗 API 통합 도메인
        domains["api"] = AgentDomain(
            domain_id="api",
            domain_name="API 통합",
            category="system_integration",
            description="외부 시스템과의 API 기반 연동",
            capabilities=[
                DomainCapability(
                    name="rest_api_client",
                    description="REST API 클라이언트",
                    complexity_level="basic",
                    dependencies=["requests", "aiohttp"],
                    interfaces=["http_client", "auth_handler"],
                    use_cases=["데이터 동기화", "서비스 연동", "상태 확인"],
                ),
                DomainCapability(
                    name="graphql_client",
                    description="GraphQL API 클라이언트",
                    complexity_level="intermediate",
                    dependencies=["gql", "requests"],
                    interfaces=["graphql_client", "query_builder"],
                    use_cases=["복잡한 데이터 쿼리", "실시간 구독", "스키마 기반 통신"],
                ),
                DomainCapability(
                    name="webhook_handler",
                    description="웹훅 처리",
                    complexity_level="intermediate",
                    dependencies=["flask", "fastapi"],
                    interfaces=["webhook_receiver", "event_processor"],
                    use_cases=["이벤트 처리", "실시간 알림", "워크플로우 트리거"],
                ),
            ],
            typical_agents=["APIClientAgent", "WebhookHandlerAgent", "DataSyncAgent"],
            integration_points=["message_queue", "event_bus", "api_gateway"],
            scalability="high",
        )

        # 🧪 시뮬레이션 도메인
        domains["simulation"] = AgentDomain(
            domain_id="simulation",
            domain_name="시뮬레이션 및 모델링",
            category="analysis_modeling",
            description="시나리오 기반 시뮬레이션 및 예측 모델링",
            capabilities=[
                DomainCapability(
                    name="scenario_modeling",
                    description="시나리오 기반 모델링",
                    complexity_level="expert",
                    dependencies=["numpy", "scipy", "pandas"],
                    interfaces=["model_builder", "scenario_engine"],
                    use_cases=["정책 시뮬레이션", "리스크 분석", "의사결정 지원"],
                ),
                DomainCapability(
                    name="monte_carlo",
                    description="몬테카를로 시뮬레이션",
                    complexity_level="advanced",
                    dependencies=["numpy", "matplotlib"],
                    interfaces=["random_generator", "statistical_analyzer"],
                    use_cases=["확률 분석", "포트폴리오 최적화", "불확실성 평가"],
                ),
                DomainCapability(
                    name="agent_based_modeling",
                    description="에이전트 기반 모델링",
                    complexity_level="expert",
                    dependencies=["mesa", "networkx"],
                    interfaces=["agent_framework", "interaction_engine"],
                    use_cases=["사회 현상 모델링", "시장 시뮬레이션", "행동 분석"],
                ),
            ],
            typical_agents=["ScenarioSimulatorAgent", "MonteCarloAgent", "ABMAgent"],
            integration_points=["data_warehouse", "visualization", "reporting"],
            scalability="medium",
        )

        # 💬 커뮤니케이션 도메인
        domains["communication"] = AgentDomain(
            domain_id="communication",
            domain_name="커뮤니케이션",
            category="social_interaction",
            description="다양한 채널을 통한 커뮤니케이션 자동화",
            capabilities=[
                DomainCapability(
                    name="email_automation",
                    description="이메일 자동화",
                    complexity_level="basic",
                    dependencies=["smtplib", "email"],
                    interfaces=["smtp_client", "email_parser"],
                    use_cases=["자동 응답", "뉴스레터", "알림 발송"],
                ),
                DomainCapability(
                    name="chat_integration",
                    description="채팅 플랫폼 연동",
                    complexity_level="intermediate",
                    dependencies=["slack-sdk", "discord.py"],
                    interfaces=["chat_api", "message_handler"],
                    use_cases=["봇 운영", "자동 응답", "업무 알림"],
                ),
                DomainCapability(
                    name="social_media",
                    description="소셜 미디어 자동화",
                    complexity_level="advanced",
                    dependencies=["tweepy", "facebook-sdk"],
                    interfaces=["social_api", "content_scheduler"],
                    use_cases=["자동 포스팅", "소셜 모니터링", "콘텐츠 관리"],
                ),
            ],
            typical_agents=["EmailAgent", "SlackBotAgent", "SocialMediaAgent"],
            integration_points=["content_management", "analytics", "user_management"],
            scalability="high",
        )

        # 💰 금융 도메인
        domains["finance"] = AgentDomain(
            domain_id="finance",
            domain_name="금융 분석",
            category="financial_services",
            description="금융 데이터 분석 및 투자 의사결정 지원",
            capabilities=[
                DomainCapability(
                    name="market_data",
                    description="시장 데이터 수집 및 분석",
                    complexity_level="intermediate",
                    dependencies=["yfinance", "pandas", "numpy"],
                    interfaces=["market_api", "data_analyzer"],
                    use_cases=["주가 분석", "시장 동향", "투자 신호"],
                ),
                DomainCapability(
                    name="trading_automation",
                    description="자동 거래",
                    complexity_level="expert",
                    dependencies=["ccxt", "alpaca-trade-api"],
                    interfaces=["trading_api", "risk_manager"],
                    use_cases=["알고리즘 트레이딩", "포트폴리오 관리", "리스크 제어"],
                ),
                DomainCapability(
                    name="financial_modeling",
                    description="금융 모델링",
                    complexity_level="advanced",
                    dependencies=["quantlib", "scipy"],
                    interfaces=["model_engine", "calculator"],
                    use_cases=["옵션 가격", "리스크 측정", "포트폴리오 최적화"],
                ),
            ],
            typical_agents=["MarketDataAgent", "TradingAgent", "RiskAnalyzerAgent"],
            integration_points=["trading_platform", "data_provider", "compliance"],
            scalability="medium",
        )

        return domains

    def _build_capability_matrix(self) -> Dict[str, List[str]]:
        """역량 매트릭스 구축"""
        matrix = {}

        for domain_id, domain in self.domain_registry.items():
            matrix[domain_id] = []
            for capability in domain.capabilities:
                matrix[domain_id].append(capability.name)

        return matrix

    def _build_collaboration_graph(self) -> Dict[str, List[str]]:
        """도메인 간 협업 그래프 구축"""
        collaboration_rules = {
            "web": ["document", "api", "communication"],
            "mobile": ["api", "web"],
            "desktop": ["document", "communication"],
            "document": ["web", "api", "communication"],
            "api": ["web", "mobile", "finance", "communication"],
            "simulation": ["finance", "api"],
            "communication": ["web", "document", "api"],
            "finance": ["web", "api", "simulation"],
        }

        return collaboration_rules

    def get_domain_info(self, domain_id: str) -> Optional[AgentDomain]:
        """특정 도메인 정보 조회"""
        return self.domain_registry.get(domain_id)

    def list_all_domains(self) -> Dict[str, str]:
        """모든 도메인 목록 조회"""
        return {
            domain_id: domain.domain_name
            for domain_id, domain in self.domain_registry.items()
        }

    def get_capabilities_by_domain(self, domain_id: str) -> List[str]:
        """도메인별 역량 목록 조회"""
        return self.capability_matrix.get(domain_id, [])

    def find_collaborating_domains(self, domain_id: str) -> List[str]:
        """협업 가능한 도메인 찾기"""
        return self.collaboration_graph.get(domain_id, [])

    def suggest_agent_architecture(self, requirements: List[str]) -> Dict[str, Any]:
        """요구사항 기반 에이전트 아키텍처 제안"""

        # 요구사항 분석
        relevant_domains = []
        for requirement in requirements:
            for domain_id, domain in self.domain_registry.items():
                for capability in domain.capabilities:
                    if any(
                        use_case.lower() in requirement.lower()
                        for use_case in capability.use_cases
                    ):
                        if domain_id not in relevant_domains:
                            relevant_domains.append(domain_id)

        # 아키텍처 제안
        architecture = {
            "primary_domains": relevant_domains,
            "required_agents": [],
            "integration_points": [],
            "complexity_assessment": "medium",
        }

        for domain_id in relevant_domains:
            domain = self.domain_registry[domain_id]
            architecture["required_agents"].extend(domain.typical_agents)
            architecture["integration_points"].extend(domain.integration_points)

        # 복잡도 평가
        if len(relevant_domains) > 3:
            architecture["complexity_assessment"] = "high"
        elif len(relevant_domains) == 1:
            architecture["complexity_assessment"] = "low"

        return architecture

    def export_domain_map(
        self, output_path: str = "echo_engine/config/domain_map.yaml"
    ):
        """도메인 맵 export"""

        export_data = {
            "domains": {},
            "capability_matrix": self.capability_matrix,
            "collaboration_graph": self.collaboration_graph,
            "export_timestamp": datetime.now().isoformat(),
        }

        for domain_id, domain in self.domain_registry.items():
            export_data["domains"][domain_id] = asdict(domain)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(export_data, f, allow_unicode=True, default_flow_style=False)

        print(f"🗺️ 도메인 맵이 {output_path}에 저장되었습니다.")

    def get_full_capability_report(self) -> Dict[str, Any]:
        """전체 역량 보고서 생성"""

        total_capabilities = sum(len(caps) for caps in self.capability_matrix.values())
        total_agents = sum(
            len(domain.typical_agents) for domain in self.domain_registry.values()
        )

        complexity_distribution = {}
        for domain in self.domain_registry.values():
            for capability in domain.capabilities:
                level = capability.complexity_level
                complexity_distribution[level] = (
                    complexity_distribution.get(level, 0) + 1
                )

        return {
            "summary": {
                "total_domains": len(self.domain_registry),
                "total_capabilities": total_capabilities,
                "total_typical_agents": total_agents,
            },
            "domains": list(self.domain_registry.keys()),
            "complexity_distribution": complexity_distribution,
            "high_scalability_domains": [
                domain_id
                for domain_id, domain in self.domain_registry.items()
                if domain.scalability == "high"
            ],
            "collaboration_opportunities": len(self.collaboration_graph),
            "generated_at": datetime.now().isoformat(),
        }


# 편의 함수들
def get_domain_mapper() -> AgentDomainMapper:
    """도메인 매퍼 인스턴스 생성"""
    return AgentDomainMapper()


def export_all_domain_info():
    """모든 도메인 정보 export"""
    mapper = AgentDomainMapper()
    mapper.export_domain_map()

    # 보고서도 생성
    report = mapper.get_full_capability_report()
    with open("echo_engine/config/capability_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("📊 역량 보고서가 생성되었습니다.")


if __name__ == "__main__":
    # 테스트 실행
    mapper = AgentDomainMapper()

    print("🗺️ Echo Agent Domain Mapper 테스트")
    print("=" * 50)

    # 도메인 목록 출력
    domains = mapper.list_all_domains()
    print(f"📋 총 {len(domains)}개 도메인:")
    for domain_id, domain_name in domains.items():
        print(f"  • {domain_id}: {domain_name}")

    # 역량 보고서 출력
    report = mapper.get_full_capability_report()
    print(f"\n📊 전체 역량 요약:")
    print(f"  • 총 도메인: {report['summary']['total_domains']}개")
    print(f"  • 총 역량: {report['summary']['total_capabilities']}개")
    print(f"  • 예상 에이전트: {report['summary']['total_typical_agents']}개")

    # Export
    export_all_domain_info()
