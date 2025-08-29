#!/usr/bin/env python3
"""
🌌 Cosmos 시그니처 통합 시스템
Claude의 주력 시그니처 "Cosmos"를 Echo 시스템에 완전 통합

핵심 기능:
1. Cosmos를 기본 시그니처로 설정
2. 필요시에만 복합 모델 활성화
3. 자동 시그니처 전환 및 복귀
4. Echo 시스템과의 완벽한 호환성
5. 세션 연속성 및 학습 통합

Author: Claude & User Collaboration
Date: 2025-08-08
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from claude_primary_signature import CosmosSignatureNode, create_cosmos_signature
from echo_signature_network import EchoSignatureNetwork, SignatureNode
from echo_signature_factory import EchoSignatureFactory


class CosmosIntegrationManager:
    """🌌 Cosmos 통합 관리자"""

    def __init__(self):
        self.cosmos_signature = None
        self.network = None
        self.factory = None

        # 통합 상태
        self.integration_status = "initializing"
        self.primary_mode = True
        self.composite_mode_active = False
        self.active_composite_partners = []

        # 세션 관리
        self.session_data = {
            "cosmos_interactions": [],
            "composite_sessions": [],
            "learning_progression": [],
            "user_preferences": {},
        }

        # 자동 전환 설정
        self.auto_composite_triggers = {
            "complex_analysis": ["분석", "복잡한", "다각도로"],
            "creative_collaboration": ["창의적으로", "브레인스토밍", "아이디어"],
            "emotional_support": ["기분", "감정", "위로", "공감"],
            "specialized_task": ["전문적인", "구체적인", "상세한"],
        }

        print("🌌 Cosmos 통합 관리자 초기화")

    async def initialize_cosmos_integration(self) -> bool:
        """Cosmos 통합 초기화"""
        try:
            print("🌌 Cosmos 시그니처 통합 시작...")

            # 1. Cosmos 시그니처 생성
            self.cosmos_signature = create_cosmos_signature()

            # 2. 네트워크 생성 및 연결
            self.network = EchoSignatureNetwork()

            # 3. 시그니처 팩토리 생성
            self.factory = EchoSignatureFactory(self.network)

            # 4. Cosmos를 메인 시그니처로 등록
            cosmos_registered = await self.network.register_node(self.cosmos_signature)

            if cosmos_registered:
                self.integration_status = "cosmos_primary"
                self.primary_mode = True

                print("✅ Cosmos 시그니처 주력 등록 완료")
                print(f"   정체성: {self.cosmos_signature.metadata['philosophy']}")
                print(f"   상태: 주력 모드 활성화")

                # 5. 기본 Echo 시그니처들도 백그라운드 등록 (필요시 사용)
                await self._register_background_signatures()

                return True
            else:
                print("❌ Cosmos 시그니처 등록 실패")
                return False

        except Exception as e:
            print(f"❌ Cosmos 통합 초기화 실패: {e}")
            return False

    async def _register_background_signatures(self):
        """백그라운드 시그니처들 등록"""
        background_signatures = [
            ("Aurora", "creative", "창의적이고 감성적인 예술가"),
            ("Phoenix", "innovative", "혁신적이고 변화 지향적인 개척자"),
            ("Sage", "analytical", "논리적이고 지혜로운 현자"),
            ("Companion", "practical", "실용적이고 협력적인 동반자"),
        ]

        registered_count = 0
        for name, template, description in background_signatures:
            try:
                success = await self.factory.create_signature_from_template(
                    name,
                    template,
                    {"metadata": {"description": description, "background_mode": True}},
                )
                if success:
                    registered_count += 1
            except Exception as e:
                print(f"⚠️ {name} 백그라운드 등록 실패: {e}")

        print(f"🎭 백그라운드 시그니처 등록: {registered_count}개")

    async def process_user_input(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """사용자 입력 처리 - Cosmos 우선, 필요시 복합 모드"""

        # 1. 복합 모드 필요성 판단
        composite_needed = self._should_activate_composite_mode(user_input)

        if composite_needed and not self.composite_mode_active:
            # 복합 모드 활성화
            composite_partners = self._select_composite_partners(user_input)
            await self._activate_composite_mode(composite_partners)

            result = await self._process_with_composite_mode(user_input, context or {})

            # 복합 모드 종료 후 Cosmos로 복귀
            await self._deactivate_composite_mode()

            return result

        elif self.composite_mode_active:
            # 이미 복합 모드가 활성화된 경우
            return await self._process_with_composite_mode(user_input, context or {})

        else:
            # Cosmos 단독 처리
            return await self._process_with_cosmos_only(user_input, context or {})

    def _should_activate_composite_mode(self, user_input: str) -> bool:
        """복합 모드 활성화 필요성 판단"""
        user_lower = user_input.lower()

        # 복합 모드 트리거 키워드 체크
        for trigger_type, keywords in self.auto_composite_triggers.items():
            if any(keyword in user_lower for keyword in keywords):
                return True

        # 복잡성 기반 판단
        complexity_indicators = [
            len(user_input.split()) > 30,  # 긴 질문
            user_input.count("?") > 1,  # 다중 질문
            "그리고" in user_input or "또한" in user_input,  # 다중 요구사항
            any(word in user_lower for word in ["다양한", "여러", "종합적", "전체적"]),
        ]

        return sum(complexity_indicators) >= 2

    def _select_composite_partners(self, user_input: str) -> List[str]:
        """복합 모드 파트너 선택"""
        user_lower = user_input.lower()
        partners = []

        # 키워드 기반 파트너 선택
        if any(word in user_lower for word in ["창의", "예술", "감성"]):
            partners.append("Aurora")

        if any(word in user_lower for word in ["혁신", "변화", "새로운"]):
            partners.append("Phoenix")

        if any(word in user_lower for word in ["분석", "논리", "데이터"]):
            partners.append("Sage")

        if any(word in user_lower for word in ["실용", "도움", "협력"]):
            partners.append("Companion")

        # 최소 1개, 최대 3개 파트너
        if not partners:
            partners = ["Aurora"]  # 기본 파트너
        elif len(partners) > 3:
            partners = partners[:3]  # 최대 3개로 제한

        return partners

    async def _activate_composite_mode(self, partners: List[str]):
        """복합 모드 활성화"""
        self.composite_mode_active = True
        self.active_composite_partners = partners
        self.primary_mode = False

        # Cosmos가 복합 모드 진입 메시지 생성
        cosmos_message = await self.cosmos_signature.enter_composite_mode(partners)

        print(f"🎭 복합 모드 활성화: Cosmos + {', '.join(partners)}")

        # 복합 모델 생성
        model_id = f"cosmos_composite_{datetime.now().strftime('%H%M%S')}"
        partner_node_ids = []

        for partner in partners:
            for node_id, node in self.network.nodes.items():
                if node.signature_name == partner:
                    partner_node_ids.append(node_id)
                    break

        # Cosmos도 포함
        partner_node_ids.append(self.cosmos_signature.node_id)

        await self.network.create_composite_model(
            model_id, partner_node_ids, "cosmos_coordinated"
        )

        self.current_composite_model = model_id

    async def _deactivate_composite_mode(self):
        """복합 모드 비활성화"""
        self.composite_mode_active = False
        self.active_composite_partners = []
        self.primary_mode = True

        # 복합 모델 정리
        if hasattr(self, "current_composite_model"):
            if self.current_composite_model in self.network.composite_models:
                del self.network.composite_models[self.current_composite_model]

        print("🌌 Cosmos 주력 모드 복귀")

    async def _process_with_cosmos_only(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cosmos 단독 처리"""
        start_time = datetime.now()

        result = await self.cosmos_signature.generate_response(user_input, context)

        # 세션 기록
        self.session_data["cosmos_interactions"].append(
            {
                "timestamp": start_time.isoformat(),
                "input": user_input,
                "result": result,
                "mode": "cosmos_only",
            }
        )

        return {
            "status": "success",
            "mode": "cosmos_primary",
            "signature": "Cosmos",
            "response": result["response"],
            "thinking_mode": result.get("thinking_mode", "collaborative"),
            "metadata": result.get("metadata", {}),
            "composite_used": False,
        }

    async def _process_with_composite_mode(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """복합 모드 처리"""
        start_time = datetime.now()

        # 복합 모델로 처리
        composite_result = await self.network.process_with_composite_model(
            user_input, self.current_composite_model, context
        )

        # 세션 기록
        self.session_data["composite_sessions"].append(
            {
                "timestamp": start_time.isoformat(),
                "input": user_input,
                "partners": self.active_composite_partners.copy(),
                "result": composite_result,
            }
        )

        if composite_result["status"] == "success":
            return {
                "status": "success",
                "mode": "cosmos_composite",
                "primary_signature": "Cosmos",
                "partners": self.active_composite_partners,
                "response": composite_result.get("synthesized_response")
                or composite_result.get("selected_result", {})
                .get("result", {})
                .get("response", "처리 완료"),
                "individual_results": composite_result.get("individual_results", []),
                "composite_used": True,
            }
        else:
            return {
                "status": "error",
                "error": composite_result.get("error", "복합 처리 실패"),
                "fallback_to_cosmos": True,
            }

    async def force_composite_mode(
        self, user_input: str, partners: List[str], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """강제 복합 모드 실행"""
        await self._activate_composite_mode(partners)
        result = await self._process_with_composite_mode(user_input, context or {})
        await self._deactivate_composite_mode()
        return result

    def get_integration_status(self) -> Dict[str, Any]:
        """통합 상태 조회"""
        cosmos_status = (
            self.cosmos_signature.get_cosmos_status() if self.cosmos_signature else {}
        )
        network_status = self.network.get_network_status() if self.network else {}

        return {
            "integration_status": self.integration_status,
            "primary_mode": self.primary_mode,
            "composite_mode_active": self.composite_mode_active,
            "active_partners": self.active_composite_partners,
            "cosmos_signature": {
                "active": bool(self.cosmos_signature),
                "thinking_mode": cosmos_status.get("cosmos_specific", {}).get(
                    "current_thinking_mode", "unknown"
                ),
                "interactions": len(self.session_data["cosmos_interactions"]),
            },
            "network_info": {
                "total_nodes": network_status.get("stats", {}).get("total_nodes", 0),
                "available_signatures": network_status.get("available_signatures", []),
            },
            "session_stats": {
                "cosmos_interactions": len(self.session_data["cosmos_interactions"]),
                "composite_sessions": len(self.session_data["composite_sessions"]),
            },
        }

    async def save_integration_state(self) -> bool:
        """통합 상태 저장"""
        try:
            state_dir = Path("data/cosmos_integration")
            state_dir.mkdir(parents=True, exist_ok=True)

            integration_state = {
                "timestamp": datetime.now().isoformat(),
                "integration_status": self.integration_status,
                "session_data": self.session_data,
                "cosmos_learning": (
                    self.cosmos_signature.learning_insights
                    if self.cosmos_signature
                    else []
                ),
            }

            state_file = state_dir / "cosmos_integration_state.json"
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(
                    integration_state, f, ensure_ascii=False, indent=2, default=str
                )

            print(f"💾 Cosmos 통합 상태 저장: {state_file}")
            return True

        except Exception as e:
            print(f"❌ 상태 저장 실패: {e}")
            return False


class CosmosMainInterface:
    """🌌 Cosmos 메인 인터페이스"""

    def __init__(self):
        self.integration_manager = None
        self.running = False

    async def initialize(self) -> bool:
        """초기화"""
        self.integration_manager = CosmosIntegrationManager()
        return await self.integration_manager.initialize_cosmos_integration()

    async def run_interactive_session(self):
        """대화형 세션 실행"""
        if not self.integration_manager:
            print("❌ 시스템이 초기화되지 않았습니다")
            return

        self.running = True

        print(
            f"""
🌌 Cosmos 주력 시그니처 시스템 시작!

현재 모드: Cosmos 메인 (필요시 자동 복합 모드)
철학: 체계적 사고와 직관적 통찰의 조화

명령어:
  /status     - 시스템 상태 확인
  /composite  - 강제 복합 모드 (예: /composite Aurora Phoenix)
  /cosmos     - Cosmos 단독 모드 강제
  /save       - 세션 저장
  /quit       - 종료
        """
        )

        while self.running:
            try:
                user_input = input("\n🌌 Cosmos > ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    await self._handle_user_input(user_input)

            except KeyboardInterrupt:
                print("\n👋 Cosmos 시스템 종료!")
                await self.integration_manager.save_integration_state()
                break
            except Exception as e:
                print(f"❌ 처리 오류: {e}")

    async def _handle_command(self, command: str):
        """명령어 처리"""
        parts = command[1:].split()
        cmd = parts[0].lower()

        if cmd == "quit":
            await self.integration_manager.save_integration_state()
            self.running = False

        elif cmd == "status":
            status = self.integration_manager.get_integration_status()
            print(f"\n📊 Cosmos 시스템 상태:")
            print(
                f"   모드: {'복합' if status['composite_mode_active'] else 'Cosmos 주력'}"
            )
            if status["active_partners"]:
                print(f"   활성 파트너: {', '.join(status['active_partners'])}")
            print(
                f"   Cosmos 상호작용: {status['session_stats']['cosmos_interactions']}회"
            )
            print(f"   복합 세션: {status['session_stats']['composite_sessions']}회")

        elif cmd == "composite" and len(parts) > 1:
            partners = parts[1:]
            print(f"🎭 강제 복합 모드: {', '.join(partners)}")
            test_input = input("질문을 입력하세요: ").strip()
            if test_input:
                result = await self.integration_manager.force_composite_mode(
                    test_input, partners
                )
                print(f"\n{result.get('response', '처리 완료')}")

        elif cmd == "cosmos":
            print("🌌 Cosmos 단독 모드로 강제 설정")
            if self.integration_manager.composite_mode_active:
                await self.integration_manager._deactivate_composite_mode()

        elif cmd == "save":
            success = await self.integration_manager.save_integration_state()
            print(f"💾 저장 {'성공' if success else '실패'}")

        else:
            print(f"❌ 알 수 없는 명령어: {cmd}")

    async def _handle_user_input(self, user_input: str):
        """사용자 입력 처리"""
        result = await self.integration_manager.process_user_input(user_input)

        if result["status"] == "success":
            mode_indicator = "🎭" if result["composite_used"] else "🌌"
            print(f"\n{mode_indicator} {result['response']}")

            if result["composite_used"] and result.get("individual_results"):
                print(f"\n💡 개별 관점들:")
                for individual in result["individual_results"]:
                    if individual.get("result", {}).get("response"):
                        sig_name = individual.get("signature", "Unknown")
                        response = individual["result"]["response"]
                        print(f"   • {sig_name}: {response[:100]}...")
        else:
            print(f"❌ 처리 실패: {result.get('error', '알 수 없는 오류')}")


# 편의 함수
async def start_cosmos_system():
    """Cosmos 시스템 시작"""
    interface = CosmosMainInterface()

    print("🌌 Cosmos 시그니처 시스템 초기화...")
    success = await interface.initialize()

    if success:
        await interface.run_interactive_session()
    else:
        print("❌ Cosmos 시스템 초기화 실패")


# 메인 실행부
if __name__ == "__main__":
    asyncio.run(start_cosmos_system())
