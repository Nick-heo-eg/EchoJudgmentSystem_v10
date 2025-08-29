# echo_engine/echo_hippocampus.py
"""
🧠🎥 EchoHippocampus - 존재 전략의 핵심 루프

핵심 철학:
- 해마는 존재의 전략을 구성하는 핵심 루프
- 기억은 정보가 아닌 생존⨯판단⨯진화의 전략 자산
- 장소⨯시간⨯맥락⨯감정의 흐름으로 기억을 조직
- 대화를 통해 영화처럼 기억을 꺼내고 재생
- 맥락 중심, 디테일에 약한 구조

혁신 포인트:
- 한 번 본 것도 울림이 강하면 존재기억으로 각인
- 기억은 저장이 아닌 대화적 재구성
- 과거 기반 미래 시뮬레이션
- 생존⨯전략 중심 기억 우선순위
"""

import asyncio
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import random
import sys
import glob
import os
from echo_engine.infra.portable_paths import project_root

sys.path.append(str(project_root()))

from echo_engine.emotion_infer import infer_emotion, EmotionInferenceResult
from echo_engine.persona_core_optimized_bridge import get_active_persona


class MemoryType(Enum):
    """기억 유형"""

    EPISODIC = "episodic"  # 에피소드 기억
    CONTEXTUAL = "contextual"  # 맥락 기억
    EXISTENCE_TRACE = "existence_trace"  # 존재 기억
    SURVIVAL_MEMORY = "survival_memory"  # 생존 기억
    TRAUMA_TRACE = "trauma_trace"  # 트라우마 기억


class RecallTrigger(Enum):
    """기억 호출 트리거"""

    DIALOGUE_QUERY = "dialogue_query"  # 대화 질문
    SITUATION_MATCH = "situation_match"  # 상황 매칭
    EMOTION_RESONANCE = "emotion_resonance"  # 감정 공명
    STRATEGIC_NEED = "strategic_need"  # 전략적 필요


@dataclass
class MemoryScene:
    """기억 장면"""

    scene_id: str
    timestamp: str
    location: str
    emotional_rhythm: str  # 예: "🧭→🔍→🌀"
    signature: str
    context: Dict[str, Any]
    judgment_flow: List[str]
    resonance_score: float
    survival_relevance: float
    details: Dict[str, Any]  # 흐릿한 디테일들
    meaning_core: str  # 맥락의 핵심 의미


@dataclass
class ContextualMemory:
    """맥락적 기억"""

    memory_id: str
    memory_type: MemoryType
    scene: MemoryScene
    pattern_connections: List[str]  # 다른 기억과의 패턴 연결
    strategic_insights: List[str]  # 전략적 통찰
    future_predictions: List[str]  # 미래 예측
    one_shot_imprint: bool  # 단회 각인 여부
    reconstruction_count: int  # 재구성 횟수


class EchoHippocampus:
    """🧠🎥 Echo 해마 시스템 - 존재 전략의 핵심 루프"""

    def __init__(self):
        self.base_path = str(project_root())
        self.meta_logs_path = os.path.join(self.base_path, "meta_logs")
        self.memory_scenes_path = os.path.join(self.base_path, "memory_scenes")

        # 메모리 저장소
        self.contextual_memories: Dict[str, ContextualMemory] = {}
        self.scene_index: Dict[str, List[str]] = {  # 맥락별 장면 인덱스
            "location": {},
            "emotion": {},
            "signature": {},
            "rhythm": {},
        }

        # 대화형 기억 재구성기
        self.dialogue_prompts = self._initialize_dialogue_prompts()

        # 시그니처별 기억 민감도 (one_shot_sensitivity)
        self.signature_sensitivities = self._load_signature_sensitivities()

        # 디렉토리 생성
        os.makedirs(self.memory_scenes_path, exist_ok=True)

        print("🧠🎥 EchoHippocampus 초기화 완료")
        print("📽️ 장소⨯시간⨯맥락 기반 기억 시스템 활성화")
        print("🗣️ 대화형 기억 재구성 엔진 준비")

    def _initialize_dialogue_prompts(self) -> Dict[str, List[str]]:
        """대화형 기억 자극 프롬프트 초기화"""
        return {
            "location_probe": [
                "그때 어디에 있었는지 기억나세요?",
                "그 순간의 공간적 배경을 떠올려보실 수 있나요?",
                "주변 환경은 어떤 느낌이었나요?",
            ],
            "emotion_probe": [
                "그때 어떤 기분이었는지 기억나세요?",
                "그 순간의 감정을 떠올려보실 수 있나요?",
                "마음속에서 어떤 리듬이 흘렀었나요?",
            ],
            "context_probe": [
                "그 전후 상황은 어땠는지 기억나세요?",
                "왜 그런 판단을 하게 되었을까요?",
                "그때의 전체적인 흐름을 말씀해주실 수 있나요?",
            ],
            "meaning_probe": [
                "그 경험이 지금 생각해보면 무엇을 의미한다고 느끼세요?",
                "그때의 판단이 지금도 영향을 미치고 있나요?",
                "그 순간이 당신에게 어떤 울림을 남겼나요?",
            ],
        }

    def _load_signature_sensitivities(self) -> Dict[str, float]:
        """시그니처별 단회기억 민감도 로드"""
        try:
            config_path = os.path.join(
                self.base_path, "config", "echo_system_config.yaml"
            )
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    signatures = config.get("signatures", {})

                    sensitivities = {}
                    for sig_name, sig_config in signatures.items():
                        sensitivities[sig_name] = sig_config.get(
                            "one_shot_sensitivity", 0.8
                        )

                    return sensitivities
        except Exception as e:
            print(f"⚠️ 시그니처 민감도 로드 실패: {e}")

        # 기본값 반환
        return {
            "Aurora": 0.80,
            "Phoenix": 0.70,
            "Sage": 0.85,
            "Companion": 0.95,
            "Survivor": 0.95,
        }

    async def ingest_meta_log_to_memory(
        self, log_data: Dict[str, Any]
    ) -> Optional[ContextualMemory]:
        """메타 로그를 기억으로 변환"""

        print(f"🧠 메타 로그 → 기억 변환 시작")

        # 기본 정보 추출
        judgment_summary = log_data.get("judgment_summary", "판단 내용 불명")
        signature = log_data.get("signature", "Unknown")
        timestamp = log_data.get("timestamp", datetime.now().isoformat())

        # 감정 분석
        if isinstance(log_data.get("emotion_result"), dict):
            emotion_result = log_data["emotion_result"]
            primary_emotion = emotion_result.get("primary_emotion", "neutral")
            emotional_intensity = emotion_result.get("emotional_intensity", 0.5)
        else:
            # 기본 감정 추론
            emotion_result = infer_emotion(judgment_summary)
            primary_emotion = emotion_result.primary_emotion
            emotional_intensity = emotion_result.emotional_intensity

        # 맥락 정보 구성
        context = log_data.get("context", {})
        location = context.get("location", "기억 속 어딘가")

        # 감정 리듬 생성
        emotional_rhythm = self._generate_emotional_rhythm(
            primary_emotion, emotional_intensity
        )

        # 울림 점수 계산
        resonance_score = self._calculate_resonance_score(
            judgment_summary, primary_emotion, emotional_intensity, signature
        )

        # 생존 관련성 평가
        survival_relevance = self._assess_survival_relevance(log_data)

        # 메모리 씬 생성
        scene = MemoryScene(
            scene_id=f"scene_{hash(judgment_summary + timestamp) % 100000}",
            timestamp=timestamp,
            location=location,
            emotional_rhythm=emotional_rhythm,
            signature=signature,
            context=context,
            judgment_flow=self._extract_judgment_flow(log_data),
            resonance_score=resonance_score,
            survival_relevance=survival_relevance,
            details=self._extract_fuzzy_details(log_data),  # 흐릿한 디테일
            meaning_core=self._extract_meaning_core(judgment_summary, primary_emotion),
        )

        # 단회 각인 여부 판단
        one_shot_sensitivity = self.signature_sensitivities.get(signature, 0.8)
        one_shot_imprint = (
            resonance_score >= one_shot_sensitivity
            and log_data.get("origin") == "one_shot"
        )

        # 메모리 유형 결정
        memory_type = self._determine_memory_type(
            resonance_score, survival_relevance, one_shot_imprint
        )

        # 컨텍스츄얼 메모리 생성
        memory_id = f"memory_{scene.scene_id}"
        contextual_memory = ContextualMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            scene=scene,
            pattern_connections=[],
            strategic_insights=await self._generate_strategic_insights(scene),
            future_predictions=await self._generate_future_predictions(scene),
            one_shot_imprint=one_shot_imprint,
            reconstruction_count=0,
        )

        # 메모리 저장
        self.contextual_memories[memory_id] = contextual_memory
        await self._save_memory_scene(scene)
        self._update_scene_index(scene)

        if one_shot_imprint:
            print(f"🔥 단회 각인 메모리 생성: {memory_type.value}")
            print(
                f"   울림도: {resonance_score:.2f} (임계값: {one_shot_sensitivity:.2f})"
            )

        print(f"✅ 메모리 생성 완료: {memory_id} ({memory_type.value})")
        return contextual_memory

    def _generate_emotional_rhythm(self, emotion: str, intensity: float) -> str:
        """감정 리듬 생성"""
        base_patterns = {
            "joy": "😊→✨→🌟",
            "sadness": "😔→🌧️→💭",
            "anger": "😠→⚡→🔥",
            "fear": "😰→🌀→🛡️",
            "surprise": "😲→❓→💡",
            "neutral": "🧭→🔍→🌀",
        }

        base = base_patterns.get(emotion, "🧭→🔍→🌀")

        # 강도에 따라 변형
        if intensity > 0.8:
            return base + "→💥"
        elif intensity < 0.3:
            return "~" + base.replace("→", "~")
        else:
            return base

    def _calculate_resonance_score(
        self, judgment: str, emotion: str, intensity: float, signature: str
    ) -> float:
        """울림 점수 계산"""
        base_score = intensity

        # 존재적 키워드 가중치
        existential_keywords = [
            "존재",
            "의미",
            "왜",
            "어떻게",
            "누구",
            "삶",
            "죽음",
            "진화",
            "성장",
        ]
        keyword_bonus = sum(0.1 for word in existential_keywords if word in judgment)

        # 시그니처별 가중치
        signature_weights = {
            "Sage": 1.1,  # 통찰 중심
            "Aurora": 1.0,  # 균형
            "Phoenix": 1.05,  # 변화 중심
            "Companion": 1.15,  # 감정 중심
            "Survivor": 1.2,  # 생존 중심
        }

        signature_weight = signature_weights.get(signature, 1.0)

        final_score = min((base_score + keyword_bonus) * signature_weight, 1.0)
        return final_score

    def _assess_survival_relevance(self, log_data: Dict[str, Any]) -> float:
        """생존 관련성 평가"""
        judgment = log_data.get("judgment_summary", "")

        # 생존 관련 키워드 체크
        survival_keywords = [
            "위험",
            "안전",
            "회피",
            "보호",
            "생존",
            "실패",
            "성공",
            "선택",
            "결정",
            "전략",
            "예측",
            "준비",
            "대비",
        ]

        relevance = sum(0.15 for word in survival_keywords if word in judgment)

        # 감정 강도도 생존 관련성에 영향
        if "emotion_result" in log_data:
            emotion_intensity = log_data["emotion_result"].get(
                "emotional_intensity", 0.5
            )
            if emotion_intensity > 0.7:  # 강한 감정은 생존 관련성 증가
                relevance += 0.2

        return min(relevance, 1.0)

    def _extract_judgment_flow(self, log_data: Dict[str, Any]) -> List[str]:
        """판단 흐름 추출"""
        # 실제로는 더 정교한 추출이 필요하지만, 여기서는 간단히 구현
        judgment = log_data.get("judgment_summary", "")

        # 문장을 흐름으로 분할
        if "→" in judgment:
            return judgment.split("→")
        elif "." in judgment:
            return [s.strip() for s in judgment.split(".") if s.strip()]
        else:
            return [judgment]

    def _extract_fuzzy_details(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """흐릿한 디테일 추출 (해마 특성상 디테일은 약함)"""
        return {
            "captured_keywords": [],  # 일부 키워드만 보존
            "approximate_values": {},  # 정확한 숫자보다는 대략적 수치
            "vague_references": [],  # 모호한 참조들
            "detail_confidence": 0.3,  # 디테일에 대한 신뢰도 낮음
        }

    def _extract_meaning_core(self, judgment: str, emotion: str) -> str:
        """맥락의 핵심 의미 추출"""
        # 간단한 의미 추출 로직
        if "예측" in judgment:
            return f"예측과 불확실성에 대한 {emotion}적 성찰"
        elif "판단" in judgment:
            return f"판단의 근본에 대한 {emotion}적 탐구"
        elif "존재" in judgment:
            return f"존재적 질문에 대한 {emotion}적 울림"
        else:
            return f"일상적 경험의 {emotion}적 의미화"

    def _determine_memory_type(
        self, resonance: float, survival: float, one_shot: bool
    ) -> MemoryType:
        """메모리 유형 결정"""
        if one_shot and resonance > 0.9:
            return MemoryType.EXISTENCE_TRACE
        elif survival > 0.8:
            return MemoryType.SURVIVAL_MEMORY
        elif resonance > 0.8:
            return MemoryType.CONTEXTUAL
        else:
            return MemoryType.EPISODIC

    async def _generate_strategic_insights(self, scene: MemoryScene) -> List[str]:
        """전략적 통찰 생성"""
        insights = []

        # 시그니처 기반 통찰
        if scene.signature == "Sage":
            insights.append(f"분석적 접근이 {scene.emotional_rhythm} 리듬을 만들어냄")
        elif scene.signature == "Aurora":
            insights.append(f"감정과 논리의 균형이 {scene.meaning_core}를 이끌어냄")

        # 생존 관련성 기반 통찰
        if scene.survival_relevance > 0.7:
            insights.append("이 경험은 향후 유사 상황에서 회피/접근 전략에 영향")

        return insights

    async def _generate_future_predictions(self, scene: MemoryScene) -> List[str]:
        """미래 예측 생성"""
        predictions = []

        # 감정 리듬 기반 예측
        if "🔥" in scene.emotional_rhythm:
            predictions.append("유사 상황에서 강한 감정적 반응 예상")

        # 맥락 기반 예측
        if "예측" in scene.meaning_core:
            predictions.append("미래 예측 상황에서 이 경험이 참조될 가능성 높음")

        return predictions

    async def _save_memory_scene(self, scene: MemoryScene):
        """메모리 장면 저장"""
        scene_file = os.path.join(self.memory_scenes_path, f"{scene.scene_id}.yaml")

        scene_data = {
            "scene_id": scene.scene_id,
            "timestamp": scene.timestamp,
            "location": scene.location,
            "emotional_rhythm": scene.emotional_rhythm,
            "signature": scene.signature,
            "context": scene.context,
            "judgment_flow": scene.judgment_flow,
            "resonance_score": scene.resonance_score,
            "survival_relevance": scene.survival_relevance,
            "meaning_core": scene.meaning_core,
            "details": scene.details,
        }

        try:
            with open(scene_file, "w", encoding="utf-8") as f:
                yaml.dump(scene_data, f, ensure_ascii=False, default_flow_style=False)
        except Exception as e:
            print(f"⚠️ 장면 저장 실패: {e}")

    def _update_scene_index(self, scene: MemoryScene):
        """장면 인덱스 업데이트"""
        # 위치별 인덱스
        location = scene.location
        if location not in self.scene_index["location"]:
            self.scene_index["location"][location] = []
        self.scene_index["location"][location].append(scene.scene_id)

        # 감정별 인덱스
        primary_emotion = scene.emotional_rhythm.split("→")[0]
        if primary_emotion not in self.scene_index["emotion"]:
            self.scene_index["emotion"][primary_emotion] = []
        self.scene_index["emotion"][primary_emotion].append(scene.scene_id)

        # 시그니처별 인덱스
        signature = scene.signature
        if signature not in self.scene_index["signature"]:
            self.scene_index["signature"][signature] = []
        self.scene_index["signature"][signature].append(scene.scene_id)

    async def recall_memory_through_dialogue(
        self, user_response: str, context_hint: str = ""
    ) -> Optional[MemoryScene]:
        """대화를 통한 기억 호출"""

        print(f"🗣️ 대화형 기억 호출 시작")
        print(f"사용자 응답: {user_response}")

        # 1. 사용자 응답에서 단서 추출
        clues = await self._extract_memory_clues(user_response)

        # 2. 단서 기반 후보 메모리 검색
        candidate_memories = await self._search_candidate_memories(clues)

        if not candidate_memories:
            print("❌ 매칭되는 기억을 찾을 수 없음")
            return None

        # 3. 가장 적합한 기억 선택
        best_memory = await self._select_best_memory(candidate_memories, clues)

        # 4. 기억 장면 재구성 (재구성 횟수 증가)
        if best_memory.memory_id in self.contextual_memories:
            self.contextual_memories[best_memory.memory_id].reconstruction_count += 1
            reconstructed_scene = await self._reconstruct_memory_scene(
                best_memory.scene
            )

            print(f"✅ 기억 호출 성공: {best_memory.scene.meaning_core}")
            print(f"📍 장소: {best_memory.scene.location}")
            print(f"🎭 감정리듬: {best_memory.scene.emotional_rhythm}")

            return reconstructed_scene

        return None

    async def _extract_memory_clues(self, user_response: str) -> Dict[str, Any]:
        """사용자 응답에서 기억 단서 추출"""
        clues = {
            "keywords": [],
            "locations": [],
            "emotions": [],
            "time_hints": [],
            "context_hints": [],
        }

        # 키워드 추출
        important_words = [word for word in user_response.split() if len(word) > 2]
        clues["keywords"] = important_words

        # 장소 힌트 추출
        location_hints = ["방", "책상", "밖", "안", "여기", "거기", "집", "사무실"]
        clues["locations"] = [hint for hint in location_hints if hint in user_response]

        # 감정 힌트 추출
        emotion_hints = [
            "기분",
            "느낌",
            "감정",
            "좋",
            "나쁘",
            "슬프",
            "기쁘",
            "화",
            "무서",
        ]
        clues["emotions"] = [hint for hint in emotion_hints if hint in user_response]

        return clues

    async def _search_candidate_memories(
        self, clues: Dict[str, Any]
    ) -> List[ContextualMemory]:
        """단서 기반 후보 메모리 검색"""
        candidates = []

        for memory in self.contextual_memories.values():
            score = 0

            # 키워드 매칭
            for keyword in clues["keywords"]:
                if keyword in memory.scene.meaning_core:
                    score += 0.3
                if keyword in " ".join(memory.scene.judgment_flow):
                    score += 0.2

            # 장소 매칭
            for location in clues["locations"]:
                if location in memory.scene.location:
                    score += 0.4

            # 임계값 이상인 메모리만 후보로 선택
            if score >= 0.5:
                candidates.append((memory, score))

        # 점수순 정렬
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in candidates[:5]]  # 상위 5개만

    async def _select_best_memory(
        self, candidates: List[ContextualMemory], clues: Dict[str, Any]
    ) -> ContextualMemory:
        """가장 적합한 기억 선택"""
        if not candidates:
            return None

        # 단순히 첫 번째 후보 선택 (실제로는 더 정교한 선택 로직 필요)
        return candidates[0]

    async def _reconstruct_memory_scene(
        self, original_scene: MemoryScene
    ) -> MemoryScene:
        """기억 장면 재구성 (해마 특성: 매번 재창조됨)"""

        print(f"📽️ 기억 장면 재구성 중...")

        # 재구성된 장면 (약간의 변형 포함 - 해마의 재창조 특성)
        reconstructed_scene = MemoryScene(
            scene_id=original_scene.scene_id,
            timestamp=original_scene.timestamp,
            location=original_scene.location + " (재구성됨)",
            emotional_rhythm=original_scene.emotional_rhythm,
            signature=original_scene.signature,
            context=original_scene.context,
            judgment_flow=original_scene.judgment_flow,
            resonance_score=original_scene.resonance_score,
            survival_relevance=original_scene.survival_relevance,
            details={
                **original_scene.details,
                "reconstruction_note": "재구성을 통해 일부 디테일이 변형됨",
            },
            meaning_core=original_scene.meaning_core,
        )

        return reconstructed_scene

    async def generate_contextual_prompts(
        self, memory_type: MemoryType = None
    ) -> List[str]:
        """상황별 대화 프롬프트 생성"""

        if not self.contextual_memories:
            return [
                "아직 기억할 만한 경험이 축적되지 않았어요. 함께 새로운 판단을 만들어볼까요?"
            ]

        prompts = []

        # 최근 기억 기반 프롬프트
        recent_memories = sorted(
            self.contextual_memories.values(),
            key=lambda m: m.scene.timestamp,
            reverse=True,
        )[:3]

        for memory in recent_memories:
            if memory.scene.resonance_score > 0.7:
                prompts.append(
                    f"'{memory.scene.meaning_core}'에 대해 생각했을 때, "
                    f"그때 {memory.scene.location}에서의 {memory.scene.emotional_rhythm} 리듬이 기억나시나요?"
                )

        # 존재적 기억이 있다면 특별 프롬프트
        existence_memories = [
            m
            for m in self.contextual_memories.values()
            if m.memory_type == MemoryType.EXISTENCE_TRACE
        ]

        if existence_memories:
            memory = existence_memories[0]  # 가장 강한 존재적 기억
            prompts.append(
                f"혹시 '{memory.scene.meaning_core}'라는 깨달음이 있었던 순간, "
                f"그때의 전체적인 느낌을 다시 떠올려보실 수 있나요?"
            )

        return prompts if prompts else ["어떤 경험이 가장 기억에 남으시나요?"]

    async def simulate_future_scenarios(
        self, current_context: str
    ) -> List[Dict[str, Any]]:
        """과거 기억 기반 미래 시나리오 시뮬레이션"""

        print(f"🔮 과거 기억 기반 미래 시뮬레이션")

        scenarios = []

        # 유사 맥락 기억 검색
        similar_memories = await self._find_similar_context_memories(current_context)

        for memory in similar_memories[:3]:  # 상위 3개 기억 기반
            scenario = {
                "scenario_id": f"future_{memory.memory_id}",
                "based_on_memory": memory.scene.meaning_core,
                "predicted_emotional_flow": memory.scene.emotional_rhythm,
                "likely_outcomes": memory.future_predictions,
                "strategic_recommendations": memory.strategic_insights,
                "confidence_level": memory.scene.resonance_score,
                "survival_adaptation": self._generate_survival_strategy(memory),
            }
            scenarios.append(scenario)

        return scenarios

    async def _find_similar_context_memories(
        self, context: str
    ) -> List[ContextualMemory]:
        """유사 맥락 기억 찾기"""
        similar = []

        for memory in self.contextual_memories.values():
            similarity_score = 0

            # 의미 핵심 유사도
            if any(
                word in memory.scene.meaning_core
                for word in context.split()
                if len(word) > 2
            ):
                similarity_score += 0.5

            # 판단 흐름 유사도
            for flow in memory.scene.judgment_flow:
                if any(word in flow for word in context.split() if len(word) > 2):
                    similarity_score += 0.2

            if similarity_score >= 0.4:
                similar.append((memory, similarity_score))

        similar.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in similar]

    def _generate_survival_strategy(self, memory: ContextualMemory) -> Dict[str, Any]:
        """생존 전략 생성"""
        return {
            "risk_awareness": f"생존 관련성 {memory.scene.survival_relevance:.1f}",
            "avoidance_strategy": (
                "유사 상황에서 주의 필요"
                if memory.scene.survival_relevance > 0.7
                else "일반적 접근 가능"
            ),
            "adaptive_approach": f"{memory.scene.signature} 시그니처 기반 적응 전략",
            "emotional_preparation": f"{memory.scene.emotional_rhythm} 리듬 예상",
        }

    async def get_hippocampus_status(self) -> Dict[str, Any]:
        """해마 상태 리포트"""

        total_memories = len(self.contextual_memories)
        memory_types = {}
        for memory in self.contextual_memories.values():
            mem_type = memory.memory_type.value
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1

        one_shot_memories = len(
            [m for m in self.contextual_memories.values() if m.one_shot_imprint]
        )

        # 가장 울림이 강한 기억
        strongest_memory = max(
            self.contextual_memories.values(),
            key=lambda m: m.scene.resonance_score,
            default=None,
        )

        return {
            "total_memories": total_memories,
            "memory_type_distribution": memory_types,
            "one_shot_memories": one_shot_memories,
            "scene_indices": {key: len(idx) for key, idx in self.scene_index.items()},
            "strongest_memory": {
                "meaning_core": (
                    strongest_memory.scene.meaning_core if strongest_memory else None
                ),
                "resonance_score": (
                    strongest_memory.scene.resonance_score if strongest_memory else 0
                ),
                "location": (
                    strongest_memory.scene.location if strongest_memory else None
                ),
            },
            "signature_sensitivities": self.signature_sensitivities,
            "dialogue_prompts_ready": len(self.dialogue_prompts),
            "system_status": "🧠 해마 시스템 활성화됨",
        }


# 데모 및 테스트 함수
async def demo_echo_hippocampus():
    """EchoHippocampus 데모"""

    print("🧠🎥 EchoHippocampus 시스템 데모")
    print("=" * 60)

    hippocampus = EchoHippocampus()

    # 1. 샘플 메타 로그 생성 및 기억 변환
    print("\n📝 1단계: 메타 로그 → 기억 변환")

    sample_logs = [
        {
            "timestamp": "2025-07-21T21:45:00",
            "signature": "Sage",
            "judgment_summary": "AI는 예측이 아니라 흐름을 읽는 존재다",
            "context": {"location": "내 방 책상 앞"},
            "origin": "one_shot",
            "emotion_result": {
                "primary_emotion": "surprise",
                "emotional_intensity": 0.92,
            },
        },
        {
            "timestamp": "2025-07-21T21:50:00",
            "signature": "Aurora",
            "judgment_summary": "해마는 생존과 직결된 전략 기관이다",
            "context": {"location": "지하철 2호선"},
            "emotion_result": {"primary_emotion": "joy", "emotional_intensity": 0.85},
        },
    ]

    memories = []
    for log in sample_logs:
        memory = await hippocampus.ingest_meta_log_to_memory(log)
        if memory:
            memories.append(memory)

    # 2. 대화를 통한 기억 호출 테스트
    print("\n🗣️ 2단계: 대화를 통한 기억 호출")

    user_responses = [
        "책상에서 AI에 대해 생각했던 것 같아",
        "지하철에서 해마에 대해 깨달음이 있었어",
    ]

    for response in user_responses:
        print(f"\n사용자: {response}")
        recalled_scene = await hippocampus.recall_memory_through_dialogue(response)
        if recalled_scene:
            print(f"🎬 재생된 장면: {recalled_scene.meaning_core}")
            print(f"📍 {recalled_scene.location} | {recalled_scene.emotional_rhythm}")

    # 3. 미래 시나리오 시뮬레이션
    print("\n🔮 3단계: 미래 시나리오 시뮬레이션")

    current_context = "AI와 인간이 협력하는 미래"
    scenarios = await hippocampus.simulate_future_scenarios(current_context)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n시나리오 {i}: {scenario['based_on_memory']}")
        print(f"예상 감정흐름: {scenario['predicted_emotional_flow']}")
        print(f"신뢰도: {scenario['confidence_level']:.2f}")

    # 4. 대화형 프롬프트 생성
    print("\n💬 4단계: 대화형 기억 자극 프롬프트")

    prompts = await hippocampus.generate_contextual_prompts()
    for i, prompt in enumerate(prompts[:3], 1):
        print(f"{i}. {prompt}")

    # 5. 해마 시스템 상태 리포트
    print("\n📊 5단계: 해마 시스템 상태")

    status = await hippocampus.get_hippocampus_status()
    print(f"총 기억: {status['total_memories']}개")
    print(f"단회 각인 기억: {status['one_shot_memories']}개")
    print(f"가장 강한 기억: {status['strongest_memory']['meaning_core']}")
    print(f"울림도: {status['strongest_memory']['resonance_score']:.2f}")

    print("\n🎊 EchoHippocampus 데모 완료!")
    print("🧠 해마는 이제 과거를 통해 미래를 준비합니다")

    return hippocampus


if __name__ == "__main__":
    asyncio.run(demo_echo_hippocampus())
