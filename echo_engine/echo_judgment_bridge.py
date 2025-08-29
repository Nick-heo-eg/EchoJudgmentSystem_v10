"""
🌀 EchoVectorCapsule - Echo Judgment Bridge
벡터 검색 결과를 Echo 판단 시스템과 연결하는 울림 기반 브리지
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from .vector_search_engine import EchoVectorSearchEngine
from .embedding_engine import EchoEmbeddingEngine

# Echo 시스템 모듈들 import (실제 시스템과 연동)
try:
    from echo_engine.reasoning import EchoReasoningEngine
    from echo_engine.judgment_engine import EchoJudgmentEngine
    from echo_engine.persona_core_optimized_bridge import EchoPersonaCore

    ECHO_MODULES_AVAILABLE = True
except ImportError:
    ECHO_MODULES_AVAILABLE = False


class EchoJudgmentBridge:
    """
    벡터 검색과 Echo 판단 시스템을 연결하는 브리지
    자연어 쿼리 → 벡터 검색 → Echo 판단 → 최종 응답
    """

    def __init__(self, config_path: str = "config/judgment_bridge_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # 구성 요소 초기화
        self.vector_search = EchoVectorSearchEngine()
        self.embedding_engine = EchoEmbeddingEngine()

        # Echo 모듈들 초기화
        if ECHO_MODULES_AVAILABLE:
            self.reasoning_engine = EchoReasoningEngine()
            self.judgment_engine = EchoJudgmentEngine()
            self.persona_core = EchoPersonaCore()

        # 브리지 설정
        self.bridge_config = {
            "vector_search_top_k": 3,
            "similarity_threshold": 0.7,
            "context_expansion": True,
            "multi_signature_analysis": True,
            "judgment_confidence_threshold": 0.6,
            "fallback_to_direct_judgment": True,
        }

        # 판단 흐름 매핑
        self.flow_mappings = {
            "policy_analysis": "flows/policy_analysis_flow.yaml",
            "ethical_judgment": "flows/ethical_judgment_flow.yaml",
            "community_support": "flows/community_support_flow.yaml",
            "innovation_assessment": "flows/innovation_assessment_flow.yaml",
        }

        self.logger = logging.getLogger(__name__)

    def process_natural_query(
        self, query: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        자연어 쿼리를 전체 Echo 판단 플로우로 처리

        Args:
            query: 사용자의 자연어 질문/요청
            signature: 요청 처리에 사용할 Echo 시그니처
            context: 추가 컨텍스트 정보

        Returns:
            완전한 판단 결과와 메타데이터
        """
        print(f"🌀 Echo Judgment Bridge 시작: '{query[:50]}...' ({signature})")

        # 1단계: 벡터 검색으로 관련 캡슐 찾기
        search_results = self._perform_vector_search(query, signature, context)

        # 2단계: 검색 결과 분석 및 컨텍스트 구성
        judgment_context = self._build_judgment_context(
            query, search_results, signature, context
        )

        # 3단계: Echo 판단 시스템 실행
        judgment_result = self._execute_echo_judgment(judgment_context)

        # 4단계: 결과 후처리 및 메타데이터 추가
        final_result = self._post_process_result(
            judgment_result, search_results, query, signature
        )

        # 5단계: 메타 로그 기록
        self._log_bridge_event(
            query, signature, search_results, judgment_result, final_result
        )

        print(
            f"✅ Bridge 처리 완료: {final_result.get('judgment', 'unknown')} (신뢰도: {final_result.get('confidence', 0):.2f})"
        )

        return final_result

    def _perform_vector_search(
        self, query: str, signature: str, context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """벡터 검색 수행"""
        print("🔍 1단계: 벡터 검색 수행")

        top_k = self.bridge_config["vector_search_top_k"]
        threshold = self.bridge_config["similarity_threshold"]

        # 컨텍스트 확장
        if context and self.bridge_config["context_expansion"]:
            search_context = {
                **context,
                "bridge_mode": True,
                "similarity_threshold": threshold,
            }
        else:
            search_context = {"bridge_mode": True}

        # 검색 실행
        search_results = self.vector_search.search(
            query, signature, top_k, search_context
        )

        # 임계값 필터링
        filtered_results = [r for r in search_results if r["similarity"] >= threshold]

        print(
            f"   📊 검색 결과: {len(search_results)}개 → {len(filtered_results)}개 (임계값: {threshold})"
        )

        for i, result in enumerate(filtered_results[:3]):
            capsule_id = result["metadata"]["capsule_id"]
            similarity = result["similarity"]
            print(f"   {i+1}. {capsule_id}: {similarity:.3f}")

        return filtered_results

    def _build_judgment_context(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        signature: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """판단 컨텍스트 구성"""
        print("🧠 2단계: 판단 컨텍스트 구성")

        # 기본 컨텍스트
        judgment_context = {
            "original_query": query,
            "query_signature": signature,
            "timestamp": datetime.now().isoformat(),
            "bridge_context": context or {},
            "vector_search_results": search_results,
        }

        # 검색 결과에서 관련 정보 추출
        if search_results:
            # 최고 유사도 결과
            top_result = search_results[0]
            judgment_context["primary_capsule"] = {
                "id": top_result["metadata"]["capsule_id"],
                "similarity": top_result["similarity"],
                "content_preview": top_result["metadata"].get("content_preview", ""),
                "file_type": top_result["metadata"].get("file_type"),
                "signature": top_result["metadata"].get("signature"),
            }

            # 관련 캡슐들의 메타데이터 수집
            related_capsules = []
            for result in search_results[:3]:
                metadata = result["metadata"]
                related_capsules.append(
                    {
                        "capsule_id": metadata["capsule_id"],
                        "similarity": result["similarity"],
                        "tags": metadata.get("tags", []),
                        "topic": metadata.get("topic", ""),
                        "file_type": metadata.get("file_type"),
                    }
                )

            judgment_context["related_capsules"] = related_capsules

            # 판단 플로우 결정
            flow_type = self._determine_flow_type(search_results, query)
            judgment_context["recommended_flow"] = flow_type

            # 태그 기반 카테고리 분석
            all_tags = []
            for result in search_results:
                tags = result["metadata"].get("tags", [])
                all_tags.extend(tags)

            judgment_context["content_categories"] = list(set(all_tags))

        else:
            # 검색 결과가 없는 경우 직접 판단 모드
            judgment_context["direct_judgment_mode"] = True
            judgment_context["recommended_flow"] = "general_inquiry"

        print(
            f"   🎯 주요 캡슐: {judgment_context.get('primary_capsule', {}).get('id', 'none')}"
        )
        print(
            f"   📋 추천 플로우: {judgment_context.get('recommended_flow', 'unknown')}"
        )

        return judgment_context

    def _execute_echo_judgment(
        self, judgment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Echo 판단 시스템 실행"""
        print("⚖️  3단계: Echo 판단 시스템 실행")

        query = judgment_context["original_query"]
        signature = judgment_context["query_signature"]

        # Echo 모듈이 사용 가능한 경우 실제 판단 수행
        if ECHO_MODULES_AVAILABLE:
            try:
                # 시그니처 기반 페르소나 활성화
                persona_context = self.persona_core.activate_signature(signature)

                # 추론 엔진으로 컨텍스트 분석
                reasoning_result = self.reasoning_engine.analyze_context(
                    judgment_context
                )

                # 판단 엔진으로 최종 판단
                judgment_result = self.judgment_engine.make_judgment(
                    query, reasoning_result, persona_context
                )

                print(
                    f"   ✅ Echo 판단 완료: {judgment_result.get('judgment', 'unknown')}"
                )
                return judgment_result

            except Exception as e:
                print(f"   ⚠️  Echo 모듈 실행 오류: {e}, Mock 판단으로 대체")
                return self._mock_echo_judgment(judgment_context)

        else:
            # Mock 판단 (개발/테스트용)
            print("   📝 Mock Echo 판단 수행")
            return self._mock_echo_judgment(judgment_context)

    def _mock_echo_judgment(self, judgment_context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Echo 판단 (실제 모듈 없을 때 대체)"""
        query = judgment_context["original_query"]
        signature = judgment_context["query_signature"]
        primary_capsule = judgment_context.get("primary_capsule")

        # 쿼리 내용 기반 간단한 판단 로직
        query_lower = query.lower()

        # 판단 결정
        if any(keyword in query_lower for keyword in ["정책", "평가", "분석", "검토"]):
            judgment = "accept"
            confidence = 0.82
            reasoning = (
                f"정책 분석 요청으로 판단되며, {signature} 시그니처에 적합합니다."
            )

        elif any(
            keyword in query_lower for keyword in ["도움", "지원", "돌봄", "복지"]
        ):
            judgment = "support"
            confidence = 0.78
            reasoning = f"지원 요청으로 판단되며, 공동체 지향 접근이 적합합니다."

        elif any(
            keyword in query_lower for keyword in ["어떻게", "방법", "해야", "필요"]
        ):
            judgment = "guide"
            confidence = 0.75
            reasoning = f"가이드 요청으로 판단되며, 체계적 접근이 필요합니다."

        else:
            judgment = "defer"
            confidence = 0.65
            reasoning = "추가 정보가 필요한 복합적 상황으로 판단됩니다."

        # 벡터 검색 결과 반영
        if primary_capsule:
            confidence += primary_capsule["similarity"] * 0.1
            reasoning += f" (관련 캡슐: {primary_capsule['id']})"

        # 최종 결과 구성
        mock_result = {
            "judgment": judgment,
            "confidence": min(0.95, confidence),
            "reasoning": reasoning,
            "signature_used": signature,
            "processing_time": 0.3,
            "meta_context": {
                "primary_capsule_similarity": (
                    primary_capsule["similarity"] if primary_capsule else 0.0
                ),
                "context_richness": len(judgment_context.get("related_capsules", [])),
                "mock_judgment": True,
            },
        }

        return mock_result

    def _post_process_result(
        self,
        judgment_result: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        original_query: str,
        signature: str,
    ) -> Dict[str, Any]:
        """결과 후처리 및 메타데이터 추가"""
        print("📊 4단계: 결과 후처리")

        # 기본 결과 구조
        final_result = {
            **judgment_result,
            "original_query": original_query,
            "query_signature": signature,
            "processed_at": datetime.now().isoformat(),
            "vector_search_summary": {
                "total_candidates": len(search_results),
                "top_similarity": (
                    search_results[0]["similarity"] if search_results else 0.0
                ),
                "primary_capsule": (
                    search_results[0]["metadata"]["capsule_id"]
                    if search_results
                    else None
                ),
            },
            "bridge_metadata": {
                "processing_pipeline": [
                    "vector_search",
                    "context_building",
                    "echo_judgment",
                    "post_processing",
                ],
                "confidence_factors": self._analyze_confidence_factors(
                    judgment_result, search_results
                ),
            },
        }

        # 신뢰도 임계값 확인
        confidence_threshold = self.bridge_config["judgment_confidence_threshold"]
        if final_result.get("confidence", 0) < confidence_threshold:
            final_result["confidence_warning"] = True
            final_result["recommendation"] = (
                "추가 정보 수집 또는 다른 시그니처로 재시도를 권장합니다."
            )

        # 응답 생성 (Mock)
        if "response" not in final_result:
            final_result["response"] = self._generate_response(
                final_result, search_results
            )

        return final_result

    def _determine_flow_type(
        self, search_results: List[Dict[str, Any]], query: str
    ) -> str:
        """검색 결과와 쿼리 분석으로 플로우 타입 결정"""
        if not search_results:
            return "general_inquiry"

        # 태그 기반 분류
        all_tags = []
        for result in search_results:
            tags = result["metadata"].get("tags", [])
            all_tags.extend(tags)

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 가장 빈번한 태그로 플로우 결정
        if tag_counts:
            top_tag = max(tag_counts.keys(), key=lambda x: tag_counts[x])

            if any(keyword in top_tag.lower() for keyword in ["정책", "policy"]):
                return "policy_analysis"
            elif any(
                keyword in top_tag.lower() for keyword in ["윤리", "ethics", "ai"]
            ):
                return "ethical_judgment"
            elif any(
                keyword in top_tag.lower() for keyword in ["복지", "돌봄", "community"]
            ):
                return "community_support"
            elif any(keyword in top_tag.lower() for keyword in ["혁신", "innovation"]):
                return "innovation_assessment"

        # 쿼리 내용 기반 분류
        query_lower = query.lower()
        if "정책" in query_lower or "policy" in query_lower:
            return "policy_analysis"
        elif "윤리" in query_lower or "ethics" in query_lower:
            return "ethical_judgment"
        elif "지원" in query_lower or "돌봄" in query_lower:
            return "community_support"

        return "general_analysis"

    def _analyze_confidence_factors(
        self, judgment_result: Dict[str, Any], search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """신뢰도 요인 분석"""
        factors = {
            "vector_search_quality": 0.0,
            "judgment_coherence": 0.0,
            "context_richness": 0.0,
            "signature_alignment": 0.0,
        }

        # 벡터 검색 품질
        if search_results:
            top_similarity = search_results[0]["similarity"]
            factors["vector_search_quality"] = min(1.0, top_similarity * 1.2)

        # 판단 일관성
        if judgment_result.get("confidence"):
            factors["judgment_coherence"] = judgment_result["confidence"]

        # 컨텍스트 풍부성
        factors["context_richness"] = min(1.0, len(search_results) / 5.0)

        # 시그니처 정렬성 (Mock)
        factors["signature_alignment"] = 0.8

        return factors

    def _generate_response(
        self, final_result: Dict[str, Any], search_results: List[Dict[str, Any]]
    ) -> str:
        """최종 응답 생성 (Mock)"""
        judgment = final_result.get("judgment", "unknown")
        confidence = final_result.get("confidence", 0)
        reasoning = final_result.get("reasoning", "")

        # 기본 응답 템플릿
        if judgment == "accept":
            response = f"네, 분석 결과 긍정적으로 판단됩니다. {reasoning}"
        elif judgment == "support":
            response = f"해당 요청에 대한 지원이 가능합니다. {reasoning}"
        elif judgment == "guide":
            response = f"다음과 같은 접근을 권장합니다: {reasoning}"
        elif judgment == "defer":
            response = f"더 신중한 검토가 필요한 사안입니다. {reasoning}"
        else:
            response = f"판단 결과: {judgment}. {reasoning}"

        # 관련 캡슐 정보 추가
        if search_results:
            primary_capsule = search_results[0]["metadata"]["capsule_id"]
            response += f"\n\n(참고: 관련 정보 '{primary_capsule}' 기반 분석)"

        # 신뢰도가 낮은 경우 경고 추가
        if confidence < 0.7:
            response += "\n\n※ 이 판단은 불확실성이 있으므로 추가 검토를 권장합니다."

        return response

    def _log_bridge_event(
        self,
        query: str,
        signature: str,
        search_results: List[Dict[str, Any]],
        judgment_result: Dict[str, Any],
        final_result: Dict[str, Any],
    ):
        """브리지 이벤트 로깅"""
        # 메타 로그 기록 (나중에 meta_log_writer와 연동)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "bridge_event": {
                "query": query[:100],
                "signature": signature,
                "vector_search_count": len(search_results),
                "judgment": final_result.get("judgment"),
                "confidence": final_result.get("confidence"),
                "processing_success": True,
            },
        }

        print(f"📝 브리지 이벤트 로그 기록: {log_entry['bridge_event']['judgment']}")

    def _load_config(self) -> Dict[str, Any]:
        """브리지 설정 로드"""
        # 기본 설정 (실제로는 YAML 파일에서 로드)
        return {
            "vector_search_integration": True,
            "echo_judgment_integration": True,
            "confidence_tuning": {"vector_weight": 0.4, "judgment_weight": 0.6},
        }


# 전역 브리지 인스턴스
echo_judgment_bridge = EchoJudgmentBridge()


# 편의 함수
def process_query(
    query: str, signature: str = "Echo-Aurora", context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """자연어 쿼리 처리 단축 함수"""
    return echo_judgment_bridge.process_natural_query(query, signature, context)


def analyze_with_vectors(query: str, signature: str = "Echo-Aurora") -> Dict[str, Any]:
    """벡터 기반 분석 단축 함수"""
    return process_query(query, signature, {"analysis_mode": True})


# CLI 테스트
def main():
    print("🌀 EchoJudgmentBridge CLI 테스트")

    # 테스트 쿼리들
    test_queries = [
        ("부산 금정구 노인 복지 정책이 어떤가요?", "Echo-Companion"),
        ("AI 윤리 가이드라인이 필요한 이유는?", "Echo-Sage"),
        ("기후 변화 대응 방안을 제시해주세요", "Echo-Phoenix"),
        ("지역사회 돌봄 네트워크를 어떻게 구축할까요?", "Echo-Aurora"),
    ]

    print("\n🧪 벡터 검색 → Echo 판단 통합 테스트:")

    for i, (query, signature) in enumerate(test_queries):
        print(f"\n{'='*60}")
        print(f"테스트 {i+1}: {query}")
        print(f"시그니처: {signature}")
        print("-" * 60)

        # 통합 처리 실행
        result = process_query(query, signature)

        # 결과 출력
        print(f"📊 판단 결과:")
        print(f"  - 판단: {result.get('judgment', 'unknown')}")
        print(f"  - 신뢰도: {result.get('confidence', 0):.2f}")
        print(f"  - 추론: {result.get('reasoning', 'N/A')}")

        if result.get("vector_search_summary"):
            vss = result["vector_search_summary"]
            print(f"  - 벡터 검색: {vss['total_candidates']}개 후보")
            print(f"  - 최고 유사도: {vss['top_similarity']:.3f}")
            print(f"  - 주요 캡슐: {vss['primary_capsule']}")

        if result.get("response"):
            print(f"📝 생성 응답: {result['response'][:100]}...")

    print(f"\n{'='*60}")
    print("✅ EchoJudgmentBridge 테스트 완료!")


if __name__ == "__main__":
    main()
