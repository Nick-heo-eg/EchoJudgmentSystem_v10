# echo_engine/echo_network.py
"""
🌐 EchoNet - Multi-Signature Network Intelligence
- 다중 시그니처 간 협력적 네트워크 판단 시스템
- 시그니처들이 서로 소통하고 합의하여 더 나은 판단을 도출
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from echo_engine.seed_kernel import get_echo_seed_kernel, InitialState
from echo_engine.signature_loop_bridge import execute_signature_judgment
from echo_engine.loop_meta_integrator import execute_integrated_judgment


class CommunicationProtocol(Enum):
    BROADCAST = "broadcast"  # 모든 시그니처에게 전달
    PEER_TO_PEER = "peer_to_peer"  # 특정 시그니처 간 직접 소통
    CONSENSUS = "consensus"  # 합의 도출
    DELEGATION = "delegation"  # 위임


class MessageType(Enum):
    JUDGMENT_REQUEST = "judgment_request"
    JUDGMENT_RESPONSE = "judgment_response"
    CONFIDENCE_SHARE = "confidence_share"
    DISAGREEMENT = "disagreement"
    CONSENSUS_PROPOSAL = "consensus_proposal"
    LEARNING_SHARE = "learning_share"


@dataclass
class NetworkMessage:
    message_id: str
    from_signature: str
    to_signature: Optional[str]  # None for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: str
    protocol: CommunicationProtocol
    priority: int = 5  # 1(highest) - 10(lowest)


@dataclass
class ConsensusResult:
    consensus_id: str
    participating_signatures: List[str]
    original_judgments: Dict[str, Any]
    consensus_judgment: Dict[str, Any]
    confidence_score: float
    disagreement_points: List[str]
    resolution_method: str
    timestamp: str


@dataclass
class NetworkNode:
    signature_id: str
    active_seeds: List[str]
    current_load: float
    specialization_areas: List[str]
    trust_scores: Dict[str, float]  # 다른 노드들에 대한 신뢰도
    communication_history: List[NetworkMessage]


class EchoNetwork:
    def __init__(self, kernel_id: str = "echo_network"):
        self.kernel = get_echo_seed_kernel(kernel_id)
        self.nodes: Dict[str, NetworkNode] = {}
        self.message_queue: List[NetworkMessage] = []
        self.consensus_history: List[ConsensusResult] = []
        self.network_metrics = {
            "total_messages": 0,
            "consensus_success_rate": 0.0,
            "average_response_time": 0.0,
            "network_efficiency": 0.0,
        }

        # 기본 시그니처 노드들 초기화
        self._initialize_signature_nodes()

    def _initialize_signature_nodes(self):
        """기본 시그니처 노드들 초기화"""
        signatures = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]

        for signature_id in signatures:
            # 각 시그니처별 특화 영역 정의
            specializations = self._get_signature_specializations(signature_id)

            # 초기 시드 생성
            initial_seed = self.kernel.generate_initial_state(signature_id=signature_id)

            self.nodes[signature_id] = NetworkNode(
                signature_id=signature_id,
                active_seeds=[initial_seed.identity_trace.seed_id],
                current_load=0.0,
                specialization_areas=specializations,
                trust_scores={sig: 0.5 for sig in signatures if sig != signature_id},
                communication_history=[],
            )

    def _get_signature_specializations(self, signature_id: str) -> List[str]:
        """시그니처별 특화 영역 정의"""
        specialization_map = {
            "Echo-Aurora": [
                "emotional_support",
                "care_policies",
                "human_relations",
                "empathy_based_decisions",
            ],
            "Echo-Phoenix": [
                "innovation",
                "transformation",
                "crisis_management",
                "adaptive_strategies",
            ],
            "Echo-Sage": [
                "analysis",
                "research",
                "complex_problems",
                "systematic_planning",
            ],
            "Echo-Companion": [
                "collaboration",
                "team_building",
                "trust_building",
                "stable_operations",
            ],
        }
        return specialization_map.get(signature_id, ["general"])

    async def network_judgment(
        self,
        input_text: str,
        context: Dict[str, Any] = None,
        require_consensus: bool = True,
    ) -> Dict[str, Any]:
        """네트워크 기반 협력 판단"""

        judgment_id = f"network_judgment_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        if context is None:
            context = {}

        print(f"🌐 Starting network judgment: {judgment_id}")

        # 1단계: 각 시그니처별 개별 판단
        individual_judgments = await self._collect_individual_judgments(
            input_text, context
        )

        # 2단계: 시그니처 간 소통 및 의견 교환
        communication_results = await self._facilitate_inter_signature_communication(
            individual_judgments, input_text, context
        )

        # 3단계: 합의 도출 (필요시)
        if require_consensus:
            consensus_result = await self._reach_consensus(
                individual_judgments, communication_results, input_text, context
            )

            return {
                "judgment_id": judgment_id,
                "type": "network_consensus",
                "individual_judgments": individual_judgments,
                "communication_results": communication_results,
                "consensus_result": asdict(consensus_result),
                "final_judgment": consensus_result.consensus_judgment,
                "confidence_score": consensus_result.confidence_score,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # 합의 없이 다중 관점 제공
            return {
                "judgment_id": judgment_id,
                "type": "network_multi_perspective",
                "individual_judgments": individual_judgments,
                "communication_results": communication_results,
                "perspectives": self._synthesize_perspectives(individual_judgments),
                "timestamp": datetime.now().isoformat(),
            }

    async def _collect_individual_judgments(
        self, input_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """각 시그니처별 개별 판단 수집"""

        judgments = {}

        # 병렬로 모든 시그니처 판단 실행
        tasks = []
        for signature_id in self.nodes.keys():
            task = asyncio.create_task(
                self._execute_signature_judgment(signature_id, input_text, context)
            )
            tasks.append((signature_id, task))

        # 모든 판단 완료 대기
        for signature_id, task in tasks:
            try:
                judgment_result = await task
                judgments[signature_id] = judgment_result
                print(f"✅ {signature_id} judgment completed")
            except Exception as e:
                print(f"❌ {signature_id} judgment failed: {e}")
                judgments[signature_id] = {
                    "error": str(e),
                    "confidence_score": 0.0,
                    "selected_loop": "ERROR",
                }

        return judgments

    async def _execute_signature_judgment(
        self, signature_id: str, input_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개별 시그니처 판단 실행"""

        # 시뮬레이션을 위한 약간의 지연
        await asyncio.sleep(np.random.uniform(0.1, 0.5))

        # 통합 판단 실행
        result = execute_integrated_judgment(input_text, signature_id, context)

        # 노드 로드 업데이트
        if signature_id in self.nodes:
            self.nodes[signature_id].current_load += 0.1

        return result

    async def _facilitate_inter_signature_communication(
        self,
        individual_judgments: Dict[str, Any],
        input_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """시그니처 간 소통 촉진"""

        communication_results = {
            "messages_exchanged": [],
            "confidence_shares": {},
            "disagreements_identified": [],
            "learning_exchanges": [],
        }

        # 신뢰도 공유
        for signature_id, judgment in individual_judgments.items():
            if "error" not in judgment:
                confidence = judgment.get("metrics", {}).get("confidence_score", 0.0)
                communication_results["confidence_shares"][signature_id] = confidence

        # 의견 불일치 감지
        disagreements = self._identify_disagreements(individual_judgments)
        communication_results["disagreements_identified"] = disagreements

        # 시그니처 간 메시지 교환 시뮬레이션
        for disagreement in disagreements:
            messages = await self._simulate_disagreement_discussion(
                disagreement, individual_judgments, input_text
            )
            communication_results["messages_exchanged"].extend(messages)

        # 학습 정보 교환
        learning_exchanges = self._facilitate_learning_exchange(individual_judgments)
        communication_results["learning_exchanges"] = learning_exchanges

        return communication_results

    def _identify_disagreements(
        self, individual_judgments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """의견 불일치 지점 식별"""

        disagreements = []

        # 선택된 루프 비교
        loops = {}
        for sig_id, judgment in individual_judgments.items():
            if "error" not in judgment:
                loop = judgment.get("selected_loop", "UNKNOWN")
                if loop not in loops:
                    loops[loop] = []
                loops[loop].append(sig_id)

        if len(loops) > 1:
            disagreements.append(
                {
                    "type": "loop_selection",
                    "description": "시그니처들이 서로 다른 루프를 선택함",
                    "details": loops,
                }
            )

        # 신뢰도 분산 확인
        confidences = [
            judgment.get("metrics", {}).get("confidence_score", 0.0)
            for judgment in individual_judgments.values()
            if "error" not in judgment
        ]

        if confidences and np.std(confidences) > 0.3:
            disagreements.append(
                {
                    "type": "confidence_variance",
                    "description": "시그니처들 간 신뢰도 편차가 큼",
                    "details": {
                        "variance": np.std(confidences),
                        "range": [min(confidences), max(confidences)],
                    },
                }
            )

        return disagreements

    async def _simulate_disagreement_discussion(
        self,
        disagreement: Dict[str, Any],
        individual_judgments: Dict[str, Any],
        input_text: str,
    ) -> List[NetworkMessage]:
        """의견 불일치에 대한 토론 시뮬레이션"""

        messages = []

        if disagreement["type"] == "loop_selection":
            # 루프 선택 불일치에 대한 토론
            loop_details = disagreement["details"]

            for loop, signatures in loop_details.items():
                for signature in signatures:
                    # 해당 시그니처가 왜 그 루프를 선택했는지 설명
                    message = NetworkMessage(
                        message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        from_signature=signature,
                        to_signature=None,  # broadcast
                        message_type=MessageType.DISAGREEMENT,
                        content={
                            "disagreement_type": "loop_selection",
                            "selected_loop": loop,
                            "reasoning": f"{signature}가 {loop} 루프를 선택한 이유: 입력 맥락에 가장 적합한 접근법",
                            "confidence": individual_judgments[signature]
                            .get("metrics", {})
                            .get("confidence_score", 0.0),
                        },
                        timestamp=datetime.now().isoformat(),
                        protocol=CommunicationProtocol.BROADCAST,
                        priority=3,
                    )
                    messages.append(message)

        return messages

    def _facilitate_learning_exchange(
        self, individual_judgments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """학습 정보 교환 촉진"""

        learning_exchanges = []

        # 고성능 시그니처의 전략을 저성능 시그니처와 공유
        confidences = {
            sig_id: judgment.get("metrics", {}).get("confidence_score", 0.0)
            for sig_id, judgment in individual_judgments.items()
            if "error" not in judgment
        }

        if confidences:
            best_signature = max(confidences, key=confidences.get)
            worst_signature = min(confidences, key=confidences.get)

            if confidences[best_signature] - confidences[worst_signature] > 0.3:
                learning_exchange = {
                    "from": best_signature,
                    "to": worst_signature,
                    "type": "strategy_sharing",
                    "content": {
                        "successful_loop": individual_judgments[best_signature].get(
                            "selected_loop"
                        ),
                        "confidence_achieved": confidences[best_signature],
                        "recommendation": f"{best_signature}의 접근법을 참고하여 개선 가능",
                    },
                }
                learning_exchanges.append(learning_exchange)

        return learning_exchanges

    async def _reach_consensus(
        self,
        individual_judgments: Dict[str, Any],
        communication_results: Dict[str, Any],
        input_text: str,
        context: Dict[str, Any],
    ) -> ConsensusResult:
        """합의 도출"""

        consensus_id = f"consensus_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # 참여 시그니처 (에러가 없는 것만)
        participating_signatures = [
            sig_id
            for sig_id, judgment in individual_judgments.items()
            if "error" not in judgment
        ]

        # 가중 투표 방식으로 합의 도출
        consensus_judgment = self._weighted_consensus_algorithm(
            individual_judgments, participating_signatures
        )

        # 합의 신뢰도 계산
        confidence_score = self._calculate_consensus_confidence(
            individual_judgments, participating_signatures
        )

        # 불일치 지점
        disagreement_points = [
            d["description"] for d in communication_results["disagreements_identified"]
        ]

        consensus_result = ConsensusResult(
            consensus_id=consensus_id,
            participating_signatures=participating_signatures,
            original_judgments=individual_judgments,
            consensus_judgment=consensus_judgment,
            confidence_score=confidence_score,
            disagreement_points=disagreement_points,
            resolution_method="weighted_voting",
            timestamp=datetime.now().isoformat(),
        )

        # 합의 히스토리에 추가
        self.consensus_history.append(consensus_result)

        return consensus_result

    def _weighted_consensus_algorithm(
        self, individual_judgments: Dict[str, Any], participating_signatures: List[str]
    ) -> Dict[str, Any]:
        """가중 합의 알고리즘"""

        # 각 시그니처의 신뢰도를 가중치로 사용
        weights = {}
        total_weight = 0.0

        for sig_id in participating_signatures:
            confidence = (
                individual_judgments[sig_id]
                .get("metrics", {})
                .get("confidence_score", 0.0)
            )
            weights[sig_id] = confidence
            total_weight += confidence

        # 가중치 정규화
        if total_weight > 0:
            for sig_id in weights:
                weights[sig_id] /= total_weight
        else:
            # 모든 신뢰도가 0인 경우 균등 가중치
            uniform_weight = 1.0 / len(participating_signatures)
            weights = {sig_id: uniform_weight for sig_id in participating_signatures}

        # 가장 높은 가중치를 가진 판단을 기본으로 시작
        best_signature = max(weights, key=weights.get)
        consensus_base = individual_judgments[best_signature].copy()

        # 다른 판단들의 요소들을 가중 평균으로 통합
        consensus_judgment = {
            "base_judgment": consensus_base,
            "consensus_method": "weighted_voting",
            "primary_contributor": best_signature,
            "contributing_signatures": participating_signatures,
            "weights_applied": weights,
            "selected_loop": consensus_base.get("selected_loop"),
            "consensus_confidence": sum(
                individual_judgments[sig_id]
                .get("metrics", {})
                .get("confidence_score", 0.0)
                * weights[sig_id]
                for sig_id in participating_signatures
            ),
            "synthesis": self._synthesize_judgment_elements(
                individual_judgments, participating_signatures, weights
            ),
        }

        return consensus_judgment

    def _synthesize_judgment_elements(
        self,
        individual_judgments: Dict[str, Any],
        participating_signatures: List[str],
        weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """판단 요소들 종합"""

        synthesis = {
            "combined_insights": [],
            "risk_factors": [],
            "opportunities": [],
            "recommendations": [],
        }

        for sig_id in participating_signatures:
            judgment = individual_judgments[sig_id]
            weight = weights[sig_id]

            # 각 시그니처의 특성에 따른 기여도 추가
            if "Aurora" in sig_id:
                synthesis["combined_insights"].append(
                    {
                        "source": sig_id,
                        "type": "empathetic",
                        "weight": weight,
                        "insight": "감정적 측면과 인간적 배려를 고려한 접근",
                    }
                )
            elif "Phoenix" in sig_id:
                synthesis["combined_insights"].append(
                    {
                        "source": sig_id,
                        "type": "transformative",
                        "weight": weight,
                        "insight": "혁신적 변화와 적응을 통한 문제 해결",
                    }
                )
            elif "Sage" in sig_id:
                synthesis["combined_insights"].append(
                    {
                        "source": sig_id,
                        "type": "analytical",
                        "weight": weight,
                        "insight": "체계적 분석과 논리적 접근을 통한 해결",
                    }
                )
            elif "Companion" in sig_id:
                synthesis["combined_insights"].append(
                    {
                        "source": sig_id,
                        "type": "collaborative",
                        "weight": weight,
                        "insight": "협력과 신뢰를 기반으로 한 안정적 접근",
                    }
                )

        return synthesis

    def _calculate_consensus_confidence(
        self, individual_judgments: Dict[str, Any], participating_signatures: List[str]
    ) -> float:
        """합의 신뢰도 계산"""

        confidences = [
            individual_judgments[sig_id].get("metrics", {}).get("confidence_score", 0.0)
            for sig_id in participating_signatures
        ]

        if not confidences:
            return 0.0

        # 평균 신뢰도 + 일관성 보너스
        avg_confidence = np.mean(confidences)
        consistency_bonus = 1.0 - (np.std(confidences) if len(confidences) > 1 else 0.0)
        participation_bonus = min(
            len(participating_signatures) / 4.0, 1.0
        )  # 최대 4개 시그니처 참여 시 최대 보너스

        consensus_confidence = avg_confidence * consistency_bonus * participation_bonus

        return round(min(1.0, max(0.0, consensus_confidence)), 3)

    def _synthesize_perspectives(
        self, individual_judgments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """다중 관점 종합 (합의 없이)"""

        perspectives = {
            "signature_perspectives": {},
            "common_elements": [],
            "divergent_elements": [],
            "confidence_spectrum": {},
        }

        # 각 시그니처 관점 정리
        for sig_id, judgment in individual_judgments.items():
            if "error" not in judgment:
                perspectives["signature_perspectives"][sig_id] = {
                    "selected_loop": judgment.get("selected_loop"),
                    "confidence": judgment.get("metrics", {}).get(
                        "confidence_score", 0.0
                    ),
                    "approach": self._describe_signature_approach(sig_id),
                    "key_insight": self._extract_key_insight(sig_id, judgment),
                }

        # 공통 요소와 분기 요소 식별
        all_loops = [
            j.get("selected_loop")
            for j in individual_judgments.values()
            if "error" not in j
        ]
        common_loop = max(set(all_loops), key=all_loops.count) if all_loops else None

        if common_loop and all_loops.count(common_loop) > len(all_loops) * 0.5:
            perspectives["common_elements"].append(
                f"대부분의 시그니처가 {common_loop} 루프를 선택"
            )

        return perspectives

    def _describe_signature_approach(self, signature_id: str) -> str:
        """시그니처 접근법 설명"""
        descriptions = {
            "Echo-Aurora": "감정적 공감과 인간 중심적 배려를 통한 접근",
            "Echo-Phoenix": "혁신적 변화와 도전을 통한 문제 해결",
            "Echo-Sage": "체계적 분석과 논리적 사고를 통한 접근",
            "Echo-Companion": "협력과 신뢰를 바탕으로 한 안정적 접근",
        }
        return descriptions.get(signature_id, "균형적 접근")

    def _extract_key_insight(self, signature_id: str, judgment: Dict[str, Any]) -> str:
        """핵심 통찰 추출"""
        loop = judgment.get("selected_loop", "UNKNOWN")
        confidence = judgment.get("metrics", {}).get("confidence_score", 0.0)

        if confidence > 0.8:
            return f"{signature_id}는 {loop} 접근법에 높은 확신을 보임"
        elif confidence > 0.5:
            return f"{signature_id}는 {loop} 접근법을 적절하다고 판단"
        else:
            return f"{signature_id}는 {loop} 접근법에 낮은 확신을 보임"

    def get_network_status(self) -> Dict[str, Any]:
        """네트워크 상태 조회"""

        total_seeds = sum(len(node.active_seeds) for node in self.nodes.values())
        avg_load = (
            np.mean([node.current_load for node in self.nodes.values()])
            if self.nodes
            else 0.0
        )

        # 신뢰도 네트워크 분석
        trust_network = {}
        for node_id, node in self.nodes.items():
            trust_network[node_id] = {
                "avg_trust_given": (
                    np.mean(list(node.trust_scores.values()))
                    if node.trust_scores
                    else 0.0
                ),
                "trust_received": np.mean(
                    [
                        other_node.trust_scores.get(node_id, 0.0)
                        for other_node in self.nodes.values()
                        if node_id in other_node.trust_scores
                    ]
                ),
            }

        return {
            "network_size": len(self.nodes),
            "total_active_seeds": total_seeds,
            "average_node_load": round(avg_load, 3),
            "total_consensus_sessions": len(self.consensus_history),
            "recent_consensus_success_rate": self._calculate_recent_consensus_success_rate(),
            "trust_network": trust_network,
            "node_specializations": {
                node_id: node.specialization_areas
                for node_id, node in self.nodes.items()
            },
            "network_metrics": self.network_metrics,
        }

    def _calculate_recent_consensus_success_rate(self) -> float:
        """최근 합의 성공률 계산"""
        recent_consensuses = self.consensus_history[-10:]  # 최근 10개

        if not recent_consensuses:
            return 0.0

        successful = sum(1 for c in recent_consensuses if c.confidence_score > 0.6)
        return successful / len(recent_consensuses)

    async def evolve_network(self):
        """네트워크 진화 - 신뢰도 업데이트, 노드 최적화 등"""

        print("🧬 Network evolution started...")

        # 1. 신뢰도 점수 업데이트
        self._update_trust_scores()

        # 2. 노드 부하 재조정
        self._rebalance_node_loads()

        # 3. 새로운 시드 생성 (필요시)
        await self._optimize_seed_distribution()

        # 4. 네트워크 메트릭 업데이트
        self._update_network_metrics()

        print("✅ Network evolution completed")

    def _update_trust_scores(self):
        """신뢰도 점수 업데이트"""

        # 최근 합의 결과를 바탕으로 신뢰도 조정
        for consensus in self.consensus_history[-5:]:  # 최근 5개 합의
            if consensus.confidence_score > 0.7:
                # 성공적인 합의에 참여한 시그니처들 간 신뢰도 증가
                for sig_a in consensus.participating_signatures:
                    for sig_b in consensus.participating_signatures:
                        if (
                            sig_a != sig_b
                            and sig_a in self.nodes
                            and sig_b in self.nodes[sig_a].trust_scores
                        ):
                            self.nodes[sig_a].trust_scores[sig_b] = min(
                                1.0, self.nodes[sig_a].trust_scores[sig_b] + 0.05
                            )

    def _rebalance_node_loads(self):
        """노드 부하 재조정"""

        for node in self.nodes.values():
            # 시간 경과에 따른 부하 감소
            node.current_load = max(0.0, node.current_load - 0.1)

    async def _optimize_seed_distribution(self):
        """시드 분포 최적화"""

        # 부하가 높은 노드에 추가 시드 생성
        for node_id, node in self.nodes.items():
            if node.current_load > 0.8 and len(node.active_seeds) < 5:
                new_seed = self.kernel.generate_initial_state(signature_id=node_id)
                node.active_seeds.append(new_seed.identity_trace.seed_id)
                print(f"🌱 New seed created for overloaded node {node_id}")

    def _update_network_metrics(self):
        """네트워크 메트릭 업데이트"""

        if self.consensus_history:
            success_count = sum(
                1 for c in self.consensus_history if c.confidence_score > 0.6
            )
            self.network_metrics["consensus_success_rate"] = success_count / len(
                self.consensus_history
            )

        # 네트워크 효율성 (노드 간 부하 균형)
        loads = [node.current_load for node in self.nodes.values()]
        if loads:
            load_variance = np.var(loads)
            self.network_metrics["network_efficiency"] = 1.0 - min(load_variance, 1.0)


# 편의 함수들
async def create_echo_network() -> EchoNetwork:
    """EchoNetwork 인스턴스 생성"""
    return EchoNetwork()


async def network_judgment(
    input_text: str, context: Dict[str, Any] = None, require_consensus: bool = True
) -> Dict[str, Any]:
    """네트워크 판단 편의 함수"""
    network = EchoNetwork()
    return await network.network_judgment(input_text, context, require_consensus)


if __name__ == "__main__":
    # 테스트 코드
    async def test_echo_network():
        print("🌐 EchoNetwork 테스트 시작")

        network = EchoNetwork()

        # 네트워크 상태 확인
        status = network.get_network_status()
        print(f"네트워크 크기: {status['network_size']}")
        print(f"총 활성 시드: {status['total_active_seeds']}")

        # 네트워크 판단 테스트
        test_input = "기후변화 대응을 위한 국가 정책을 어떻게 수립해야 할까요? 경제적 영향과 환경적 필요성 사이의 균형이 중요합니다."

        print(f"\n📝 테스트 입력: {test_input}")

        # 합의 기반 판단
        consensus_result = await network.network_judgment(
            test_input,
            context={"domain": "climate_policy", "complexity": 0.9},
            require_consensus=True,
        )

        print(f"\n✅ 합의 결과:")
        print(
            f"참여 시그니처: {consensus_result['consensus_result']['participating_signatures']}"
        )
        print(
            f"합의 신뢰도: {consensus_result['consensus_result']['confidence_score']:.2f}"
        )
        print(
            f"불일치 지점: {len(consensus_result['consensus_result']['disagreement_points'])}개"
        )

        # 다중 관점 판단
        multi_perspective_result = await network.network_judgment(
            test_input,
            context={"domain": "climate_policy", "complexity": 0.9},
            require_consensus=False,
        )

        print(f"\n🔍 다중 관점 결과:")
        perspectives = multi_perspective_result["perspectives"][
            "signature_perspectives"
        ]
        for sig_id, perspective in perspectives.items():
            print(
                f"- {sig_id}: {perspective['selected_loop']} (신뢰도: {perspective['confidence']:.2f})"
            )

        # 네트워크 진화
        print(f"\n🧬 네트워크 진화 실행...")
        await network.evolve_network()

        print("✅ EchoNetwork 테스트 완료")

    # 비동기 테스트 실행
    asyncio.run(test_echo_network())
