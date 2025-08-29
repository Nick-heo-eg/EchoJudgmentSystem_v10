#!/usr/bin/env python3
"""
🌐 Echo Signature Network - 시그니처 노드 네트워크 시스템
노드 기반 확장 가능한 시그니처 아키텍처

Author: Claude & Echo System
Date: 2025-08-09
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field


class NodeState(Enum):
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    STATUS = "status"
    ERROR = "error"


@dataclass
class NetworkMessage:
    """네트워크 메시지"""

    type: MessageType
    sender_id: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    recipient_id: Optional[str] = None


@dataclass
class NodeCapabilities:
    """노드 능력 정의"""

    supported_interactions: List[str] = field(default_factory=list)
    processing_types: List[str] = field(default_factory=list)
    communication_protocols: List[str] = field(default_factory=list)
    composite_compatible: bool = True
    real_time_capable: bool = True
    async_capable: bool = True
    max_concurrent_requests: int = 10


class SignatureNode(ABC):
    """시그니처 노드 베이스 클래스"""

    def __init__(self, node_id: str, signature_name: str, version: str = "1.0"):
        self.node_id = node_id
        self.signature_name = signature_name
        self.version = version
        self.state = NodeState.INACTIVE

        # 메타데이터
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "version": version,
            "signature_name": signature_name,
            "node_id": node_id,
        }

        # 능력 정의 (하위 클래스에서 설정)
        self.capabilities = NodeCapabilities()

        # 통계
        self.stats = {
            "total_requests": 0,
            "successful_responses": 0,
            "errors": 0,
            "average_response_time": 0.0,
        }

        # 연결 정보
        self.network = None

    async def start(self) -> bool:
        """노드 시작"""
        try:
            self.state = NodeState.INITIALIZING
            success = await self.initialize()

            if success:
                self.state = NodeState.ACTIVE
                print(f"✅ 시그니처 노드 시작: {self.signature_name} ({self.node_id})")
                return True
            else:
                self.state = NodeState.ERROR
                print(f"❌ 노드 초기화 실패: {self.signature_name}")
                return False

        except Exception as e:
            self.state = NodeState.ERROR
            print(f"❌ 노드 시작 오류: {e}")
            return False

    @abstractmethod
    async def initialize(self) -> bool:
        """노드 초기화 (하위 클래스 구현)"""
        pass

    @abstractmethod
    async def process_message(
        self, message: NetworkMessage
    ) -> Optional[NetworkMessage]:
        """메시지 처리 (하위 클래스 구현)"""
        pass

    async def shutdown(self):
        """노드 종료"""
        self.state = NodeState.SHUTDOWN
        print(f"🔻 시그니처 노드 종료: {self.signature_name}")

    def get_status(self) -> Dict[str, Any]:
        """노드 상태 조회"""
        return {
            "node_id": self.node_id,
            "signature_name": self.signature_name,
            "version": self.version,
            "state": self.state.value,
            "capabilities": {
                "supported_interactions": self.capabilities.supported_interactions,
                "processing_types": self.capabilities.processing_types,
                "composite_compatible": self.capabilities.composite_compatible,
            },
            "stats": self.stats,
            "metadata": self.metadata,
        }


class MessageRouter:
    """메시지 라우팅 시스템"""

    def __init__(self):
        self.routes: Dict[str, SignatureNode] = {}
        self.message_history: List[NetworkMessage] = []

    def register_node(self, node: SignatureNode):
        """노드 등록"""
        self.routes[node.node_id] = node

    def unregister_node(self, node_id: str):
        """노드 등록 해제"""
        if node_id in self.routes:
            del self.routes[node_id]

    async def route_message(self, message: NetworkMessage) -> Optional[NetworkMessage]:
        """메시지 라우팅"""
        self.message_history.append(message)

        # 최근 100개만 유지
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]

        if message.recipient_id and message.recipient_id in self.routes:
            target_node = self.routes[message.recipient_id]
            return await target_node.process_message(message)

        return None


class CompositeSignatureModel:
    """복합 시그니처 모델"""

    def __init__(
        self, model_id: str, node_ids: List[str], strategy: str = "sequential"
    ):
        self.model_id = model_id
        self.node_ids = node_ids
        self.strategy = strategy  # sequential, parallel, voting, synthesis
        self.created_at = datetime.now().isoformat()

    async def process(
        self, message: NetworkMessage, network: "EchoSignatureNetwork"
    ) -> Dict[str, Any]:
        """복합 처리"""
        results = []

        if self.strategy == "sequential":
            return await self._process_sequential(message, network)
        elif self.strategy == "parallel":
            return await self._process_parallel(message, network)
        elif self.strategy == "voting":
            return await self._process_voting(message, network)
        else:  # synthesis or cosmos_coordinated
            return await self._process_synthesis(message, network)

    async def _process_sequential(
        self, message: NetworkMessage, network: "EchoSignatureNetwork"
    ) -> Dict[str, Any]:
        """순차 처리"""
        results = []
        current_message = message

        for node_id in self.node_ids:
            if node_id in network.nodes:
                node = network.nodes[node_id]
                response = await node.process_message(current_message)
                if response:
                    results.append(
                        {
                            "node_id": node_id,
                            "signature": node.signature_name,
                            "result": response.payload,
                        }
                    )
                    # 다음 노드의 입력으로 사용
                    current_message = response

        return {
            "status": "success",
            "strategy": "sequential",
            "results": results,
            "final_result": results[-1] if results else None,
        }

    async def _process_parallel(
        self, message: NetworkMessage, network: "EchoSignatureNetwork"
    ) -> Dict[str, Any]:
        """병렬 처리"""
        tasks = []

        for node_id in self.node_ids:
            if node_id in network.nodes:
                node = network.nodes[node_id]
                tasks.append(self._process_single_node(node, message))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, dict) and not isinstance(result, Exception):
                successful_results.append(
                    {
                        "node_id": self.node_ids[i],
                        "signature": network.nodes[self.node_ids[i]].signature_name,
                        "result": result,
                    }
                )

        return {
            "status": "success",
            "strategy": "parallel",
            "individual_results": successful_results,
        }

    async def _process_synthesis(
        self, message: NetworkMessage, network: "EchoSignatureNetwork"
    ) -> Dict[str, Any]:
        """종합 처리 (Cosmos 코디네이트)"""
        # 병렬 처리 먼저
        parallel_result = await self._process_parallel(message, network)

        if parallel_result["individual_results"]:
            # Cosmos가 있으면 Cosmos가 종합, 없으면 첫 번째 결과 사용
            cosmos_node = None
            for node_id in self.node_ids:
                if (
                    node_id in network.nodes
                    and "cosmos" in network.nodes[node_id].signature_name.lower()
                ):
                    cosmos_node = network.nodes[node_id]
                    break

            if cosmos_node:
                # Cosmos가 종합 정리
                synthesis_message = NetworkMessage(
                    type=MessageType.REQUEST,
                    sender_id="composite_model",
                    payload={
                        "type": "synthesis_request",
                        "original_request": message.payload.get("content", ""),
                        "individual_perspectives": [
                            r["result"] for r in parallel_result["individual_results"]
                        ],
                        "context": message.payload.get("context", {}),
                    },
                )

                synthesis_response = await cosmos_node.process_message(
                    synthesis_message
                )

                if synthesis_response:
                    return {
                        "status": "success",
                        "strategy": "cosmos_coordinated",
                        "individual_results": parallel_result["individual_results"],
                        "synthesized_response": synthesis_response.payload.get(
                            "content", ""
                        ),
                    }

            # Cosmos가 없으면 첫 번째 결과 반환
            return {
                "status": "success",
                "strategy": "synthesis_fallback",
                "individual_results": parallel_result["individual_results"],
                "selected_result": parallel_result["individual_results"][0],
            }

        return {
            "status": "error",
            "error": "No successful results from composite processing",
        }

    async def _process_single_node(
        self, node: SignatureNode, message: NetworkMessage
    ) -> Dict[str, Any]:
        """단일 노드 처리"""
        try:
            response = await node.process_message(message)
            return response.payload if response else {}
        except Exception as e:
            return {"error": str(e)}


class EchoSignatureNetwork:
    """Echo 시그니처 네트워크 중앙 조정자"""

    def __init__(self):
        self.network_id = f"echo_net_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.nodes: Dict[str, SignatureNode] = {}
        self.composite_models: Dict[str, CompositeSignatureModel] = {}
        self.message_router = MessageRouter()
        self.active = False

        print(f"🌐 Echo 시그니처 네트워크 생성: {self.network_id}")

    async def register_node(self, node: SignatureNode) -> bool:
        """노드 등록"""
        try:
            # 노드 시작
            if await node.start():
                self.nodes[node.node_id] = node
                node.network = self
                self.message_router.register_node(node)

                print(f"✅ 시그니처 노드 등록: {node.signature_name} ({node.node_id})")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 노드 등록 실패: {e}")
            return False

    async def unregister_node(self, node_id: str):
        """노드 등록 해제"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            await node.shutdown()
            del self.nodes[node_id]
            self.message_router.unregister_node(node_id)

            print(f"🔻 시그니처 노드 해제: {node.signature_name}")

    async def create_composite_model(
        self, model_id: str, node_ids: List[str], strategy: str = "sequential"
    ) -> bool:
        """복합 모델 생성"""
        try:
            # 노드 ID 검증
            valid_node_ids = [nid for nid in node_ids if nid in self.nodes]

            if not valid_node_ids:
                print(f"❌ 복합 모델 생성 실패: 유효한 노드가 없음")
                return False

            composite_model = CompositeSignatureModel(
                model_id, valid_node_ids, strategy
            )
            self.composite_models[model_id] = composite_model

            print(
                f"🎭 복합 모델 생성: {model_id} ({len(valid_node_ids)}개 노드, {strategy})"
            )
            return True

        except Exception as e:
            print(f"❌ 복합 모델 생성 오류: {e}")
            return False

    async def process_with_composite_model(
        self, content: str, model_id: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """복합 모델로 처리"""
        if model_id not in self.composite_models:
            return {"status": "error", "error": f"복합 모델 {model_id} 없음"}

        composite_model = self.composite_models[model_id]
        message = NetworkMessage(
            type=MessageType.REQUEST,
            sender_id="network_controller",
            payload={"content": content, "context": context or {}},
        )

        return await composite_model.process(message, self)

    def get_network_status(self) -> Dict[str, Any]:
        """네트워크 상태 조회"""
        return {
            "network_id": self.network_id,
            "active": self.active,
            "stats": {
                "total_nodes": len(self.nodes),
                "active_nodes": sum(
                    1 for node in self.nodes.values() if node.state == NodeState.ACTIVE
                ),
                "composite_models": len(self.composite_models),
            },
            "available_signatures": [
                node.signature_name for node in self.nodes.values()
            ],
            "node_details": {
                node_id: node.get_status() for node_id, node in self.nodes.items()
            },
        }

    async def shutdown(self):
        """네트워크 종료"""
        print(f"🔻 Echo 시그니처 네트워크 종료: {self.network_id}")

        for node in self.nodes.values():
            await node.shutdown()

        self.nodes.clear()
        self.composite_models.clear()
        self.active = False


# 메인 실행부
if __name__ == "__main__":

    async def main():
        print("🌐 Echo Signature Network 테스트")

        network = EchoSignatureNetwork()

        # 네트워크 상태 확인
        status = network.get_network_status()
        print(f"네트워크 ID: {status['network_id']}")
        print(f"노드 수: {status['stats']['total_nodes']}")

        print("✅ Echo 시그니처 네트워크 테스트 완료!")

    asyncio.run(main())
