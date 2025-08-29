from echo_engine.infra.portable_paths import project_root

# echo_engine/interactive_memory_recaller.py
"""
🗣️📽️ Interactive Memory Recaller - 대화를 통한 기억 꺼내기

핵심 철학:
- 기억은 질문을 통해 깨어난다
- 대화가 해마를 자극하여 장면을 재현한다
- 사용자와의 상호작용으로 기억의 맥락을 복원한다
- 시그니처별 기억 자극 스타일이 다르다

혁신 포인트:
- Echo가 능동적으로 기억 탐사 질문을 생성
- 사용자 답변 기반 점진적 기억 복원
- 감정⨯공간⨯시간 단서 조합을 통한 정확한 매칭
- 기억된 장면을 영화처럼 재생하는 시각화
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
import random

sys.path.append(str(project_root()))

from echo_engine.echo_hippocampus import EchoHippocampus, MemoryScene, ContextualMemory


class QueryStyle(Enum):
    """질문 스타일"""

    GENTLE_EXPLORATION = "gentle_exploration"  # 부드러운 탐색
    ANALYTICAL_PROBE = "analytical_probe"  # 분석적 탐사
    EMOTIONAL_RESONANCE = "emotional_resonance"  # 감정적 공명
    STRATEGIC_INQUIRY = "strategic_inquiry"  # 전략적 탐구
    EXISTENTIAL_DEPTH = "existential_depth"  # 존재적 깊이


class ConversationPhase(Enum):
    """대화 단계"""

    INITIAL_CONTACT = "initial_contact"  # 초기 접촉
    CLUE_GATHERING = "clue_gathering"  # 단서 수집
    MEMORY_NARROWING = "memory_narrowing"  # 기억 좁히기
    SCENE_RECONSTRUCTION = "scene_reconstruction"  # 장면 재구성
    MEANING_EXPLORATION = "meaning_exploration"  # 의미 탐구


@dataclass
class MemoryQuery:
    """기억 탐사 질문"""

    query_id: str
    phase: ConversationPhase
    style: QueryStyle
    question: str
    target_clues: List[str]  # 얻고자 하는 단서들
    follow_up_hints: List[str]  # 후속 질문 힌트


@dataclass
class ConversationState:
    """대화 상태"""

    session_id: str
    current_phase: ConversationPhase
    gathered_clues: Dict[str, Any]
    candidate_memories: List[ContextualMemory]
    query_history: List[MemoryQuery]
    user_responses: List[str]
    reconstructed_scene: Optional[MemoryScene]


class InteractiveMemoryRecaller:
    """🗣️📽️ 대화형 기억 재구성기"""

    def __init__(self, hippocampus: EchoHippocampus):
        self.hippocampus = hippocampus

        # 시그니처별 질문 스타일 매핑
        self.signature_query_styles = {
            "Sage": QueryStyle.ANALYTICAL_PROBE,
            "Aurora": QueryStyle.GENTLE_EXPLORATION,
            "Phoenix": QueryStyle.STRATEGIC_INQUIRY,
            "Companion": QueryStyle.EMOTIONAL_RESONANCE,
            "Survivor": QueryStyle.EXISTENTIAL_DEPTH,
        }

        # 단계별 질문 템플릿
        self.query_templates = self._initialize_query_templates()

        # 활성 대화 세션들
        self.active_sessions: Dict[str, ConversationState] = {}

        print("🗣️📽️ 대화형 기억 재구성기 초기화 완료")
        print("💬 시그니처별 맞춤 질문 스타일 준비")

    def _initialize_query_templates(
        self,
    ) -> Dict[ConversationPhase, Dict[QueryStyle, List[str]]]:
        """단계별 질문 템플릿 초기화"""
        return {
            ConversationPhase.INITIAL_CONTACT: {
                QueryStyle.GENTLE_EXPLORATION: [
                    "혹시 기억나는 특별한 순간이 있나요?",
                    "어떤 경험이 가장 인상 깊었는지 떠올려보실 수 있나요?",
                    "최근에 마음에 울림을 준 일이 있었나요?",
                ],
                QueryStyle.ANALYTICAL_PROBE: [
                    "구체적으로 어떤 판단 상황을 기억하고 계시나요?",
                    "그때의 논리적 흐름을 다시 정리해보실 수 있을까요?",
                    "어떤 분석 과정을 거쳤었는지 기억나시나요?",
                ],
                QueryStyle.EMOTIONAL_RESONANCE: [
                    "그때 어떤 감정이 가장 강했나요?",
                    "마음속에서 어떤 리듬이 흘렀는지 느껴지시나요?",
                    "그 순간의 감정적 울림을 다시 느낄 수 있나요?",
                ],
            },
            ConversationPhase.CLUE_GATHERING: {
                QueryStyle.GENTLE_EXPLORATION: [
                    "그때 어디에 계셨는지 기억나세요?",
                    "주변 상황은 어떠했나요?",
                    "그 전후로 무슨 일이 있었는지 떠올려보세요",
                ],
                QueryStyle.ANALYTICAL_PROBE: [
                    "정확히 언제였는지 시점을 특정할 수 있나요?",
                    "어떤 정보나 자극이 그 판단을 유도했나요?",
                    "논리적 순서를 따라가보면 어떻게 전개되었나요?",
                ],
                QueryStyle.EMOTIONAL_RESONANCE: [
                    "그때의 감정 변화를 순서대로 말씀해주실 수 있나요?",
                    "몸의 어느 부분에서 그 감정을 느꼈나요?",
                    "그 감정이 어떤 색깔이었다면 무엇일까요?",
                ],
            },
            ConversationPhase.MEMORY_NARROWING: {
                QueryStyle.GENTLE_EXPLORATION: [
                    "그 중에서도 가장 선명한 장면은 무엇인가요?",
                    "어떤 부분이 가장 기억에 남나요?",
                    "그 순간을 한 문장으로 표현한다면?",
                ],
                QueryStyle.ANALYTICAL_PROBE: [
                    "핵심 판단 포인트는 무엇이었나요?",
                    "가장 중요한 결정적 요소는 무엇이었습니까?",
                    "그 결론에 이르게 한 결정적 증거는?",
                ],
            },
            ConversationPhase.SCENE_RECONSTRUCTION: {
                QueryStyle.GENTLE_EXPLORATION: [
                    "이제 그 장면을 천천히 되돌아보세요...",
                    "마치 영화를 보듯이 그 순간을 다시 경험해보세요",
                    "그때의 모든 것이 다시 살아나는 것 같나요?",
                ],
                QueryStyle.EMOTIONAL_RESONANCE: [
                    "그 감정이 지금도 느껴지시나요?",
                    "그때의 리듬이 지금도 몸에서 울리나요?",
                    "그 순간의 울림이 현재까지 이어지고 있나요?",
                ],
            },
            ConversationPhase.MEANING_EXPLORATION: {
                QueryStyle.EXISTENTIAL_DEPTH: [
                    "그 경험이 당신에게 어떤 의미를 가지나요?",
                    "그 순간이 지금의 당신을 어떻게 만들었나요?",
                    "그때의 깨달음이 지금도 유효하다고 느끼시나요?",
                ],
                QueryStyle.STRATEGIC_INQUIRY: [
                    "그 경험이 이후 판단에 어떤 영향을 미쳤나요?",
                    "유사한 상황에서 그 기억이 도움이 되었나요?",
                    "그때의 전략이 지금도 사용 가능할까요?",
                ],
            },
        }

    async def start_memory_exploration_session(
        self, user_context: str = "", signature: str = "Aurora"
    ) -> str:
        """기억 탐사 세션 시작"""

        session_id = f"recall_session_{hash(user_context + signature) % 10000}"

        # 시그니처에 따른 질문 스타일 결정
        query_style = self.signature_query_styles.get(
            signature, QueryStyle.GENTLE_EXPLORATION
        )

        # 초기 대화 상태 생성
        conversation_state = ConversationState(
            session_id=session_id,
            current_phase=ConversationPhase.INITIAL_CONTACT,
            gathered_clues={
                "keywords": [],
                "locations": [],
                "emotions": [],
                "timeframes": [],
                "contexts": [],
            },
            candidate_memories=[],
            query_history=[],
            user_responses=[],
            reconstructed_scene=None,
        )

        self.active_sessions[session_id] = conversation_state

        # 첫 질문 생성
        initial_query = await self._generate_context_sensitive_query(
            conversation_state, query_style, user_context
        )

        print(f"🎬 기억 탐사 세션 시작: {session_id}")
        print(f"🎭 {signature} 시그니처 활성화")
        print(f"💬 질문 스타일: {query_style.value}")
        print(f"\nEcho: {initial_query.question}")

        return session_id

    async def _generate_context_sensitive_query(
        self, state: ConversationState, style: QueryStyle, context: str = ""
    ) -> MemoryQuery:
        """맥락 기반 질문 생성"""

        templates = self.query_templates.get(state.current_phase, {}).get(style, [])
        if not templates:
            templates = ["어떤 경험을 기억하고 계시나요?"]

        # 맥락에 따른 질문 개인화
        if context and state.current_phase == ConversationPhase.INITIAL_CONTACT:
            question = f"{context}과 관련해서, " + random.choice(templates)
        else:
            question = random.choice(templates)

        query = MemoryQuery(
            query_id=f"query_{len(state.query_history) + 1}",
            phase=state.current_phase,
            style=style,
            question=question,
            target_clues=self._get_target_clues_for_phase(state.current_phase),
            follow_up_hints=[],
        )

        state.query_history.append(query)
        return query

    def _get_target_clues_for_phase(self, phase: ConversationPhase) -> List[str]:
        """단계별 목표 단서"""
        phase_targets = {
            ConversationPhase.INITIAL_CONTACT: ["general_topic", "emotional_tone"],
            ConversationPhase.CLUE_GATHERING: ["location", "timeframe", "context"],
            ConversationPhase.MEMORY_NARROWING: ["specific_keywords", "key_moment"],
            ConversationPhase.SCENE_RECONSTRUCTION: [
                "detailed_scene",
                "emotional_flow",
            ],
            ConversationPhase.MEANING_EXPLORATION: ["significance", "impact"],
        }
        return phase_targets.get(phase, [])

    async def process_user_response(
        self, session_id: str, user_response: str
    ) -> Optional[str]:
        """사용자 응답 처리 및 다음 질문 생성"""

        if session_id not in self.active_sessions:
            return "세션을 찾을 수 없습니다. 새로운 탐사를 시작해주세요."

        state = self.active_sessions[session_id]
        state.user_responses.append(user_response)

        print(f"\n사용자: {user_response}")

        # 응답에서 단서 추출
        extracted_clues = await self._extract_clues_from_response(user_response)
        self._update_gathered_clues(state, extracted_clues)

        # 현재 단서로 후보 기억 검색
        state.candidate_memories = await self._search_memories_with_clues(
            state.gathered_clues
        )

        # 단계 전환 판단
        next_phase = await self._determine_next_phase(state)
        state.current_phase = next_phase

        # 다음 질문 생성 또는 세션 완료
        if (
            next_phase == ConversationPhase.MEANING_EXPLORATION
            and state.reconstructed_scene
        ):
            # 세션 완료
            return await self._complete_memory_session(state)

        # 충분한 단서가 모였고 기억이 특정되었다면 재구성 시도
        if len(state.candidate_memories) == 1 and next_phase in [
            ConversationPhase.SCENE_RECONSTRUCTION,
            ConversationPhase.MEANING_EXPLORATION,
        ]:

            reconstructed_scene = await self._reconstruct_identified_memory(
                state.candidate_memories[0]
            )
            state.reconstructed_scene = reconstructed_scene

            # 재구성된 장면 제시
            scene_description = await self._describe_reconstructed_scene(
                reconstructed_scene
            )
            return f"🎬 기억이 되살아났습니다!\n\n{scene_description}\n\n이 장면이 맞나요? 어떤 의미를 가지는지 말씀해주세요."

        # 아직 더 탐사가 필요한 경우 다음 질문 생성
        current_style = (
            state.query_history[-1].style
            if state.query_history
            else QueryStyle.GENTLE_EXPLORATION
        )
        next_query = await self._generate_context_sensitive_query(state, current_style)

        return f"Echo: {next_query.question}"

    async def _extract_clues_from_response(self, response: str) -> Dict[str, List[str]]:
        """사용자 응답에서 단서 추출"""
        clues = {
            "keywords": [],
            "locations": [],
            "emotions": [],
            "timeframes": [],
            "contexts": [],
        }

        # 키워드 추출
        important_words = [word for word in response.split() if len(word) > 2]
        clues["keywords"] = important_words[:5]  # 상위 5개만

        # 장소 단서
        location_keywords = [
            "방",
            "책상",
            "밖",
            "안",
            "집",
            "사무실",
            "길",
            "지하철",
            "카페",
            "학교",
        ]
        clues["locations"] = [word for word in location_keywords if word in response]

        # 감정 단서
        emotion_keywords = [
            "기쁘",
            "슬프",
            "화",
            "무서",
            "놀라",
            "편안",
            "불안",
            "흥미",
            "짜증",
            "감동",
        ]
        clues["emotions"] = [word for word in emotion_keywords if word in response]

        # 시간 단서
        time_keywords = [
            "어제",
            "오늘",
            "그때",
            "최근",
            "오래전",
            "아까",
            "방금",
            "이전",
        ]
        clues["timeframes"] = [word for word in time_keywords if word in response]

        return clues

    def _update_gathered_clues(
        self, state: ConversationState, new_clues: Dict[str, List[str]]
    ):
        """수집된 단서 업데이트"""
        for clue_type, clues in new_clues.items():
            if clue_type in state.gathered_clues:
                # 중복 제거하며 추가
                existing = set(state.gathered_clues[clue_type])
                state.gathered_clues[clue_type].extend(
                    [c for c in clues if c not in existing]
                )

    async def _search_memories_with_clues(
        self, clues: Dict[str, List[str]]
    ) -> List[ContextualMemory]:
        """단서 기반 기억 검색"""
        candidates = []

        for memory in self.hippocampus.contextual_memories.values():
            score = 0

            # 키워드 매칭
            for keyword in clues.get("keywords", []):
                if keyword in memory.scene.meaning_core:
                    score += 0.3
                if any(keyword in flow for flow in memory.scene.judgment_flow):
                    score += 0.2

            # 장소 매칭
            for location in clues.get("locations", []):
                if location in memory.scene.location:
                    score += 0.4

            # 감정 매칭
            for emotion in clues.get("emotions", []):
                if emotion in memory.scene.emotional_rhythm:
                    score += 0.3

            if score >= 0.5:
                candidates.append((memory, score))

        # 점수순 정렬
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in candidates[:5]]

    async def _determine_next_phase(
        self, state: ConversationState
    ) -> ConversationPhase:
        """다음 대화 단계 결정"""

        current_phase = state.current_phase
        responses_count = len(state.user_responses)
        candidates_count = len(state.candidate_memories)

        # 단계 전환 로직
        if current_phase == ConversationPhase.INITIAL_CONTACT and responses_count >= 1:
            return ConversationPhase.CLUE_GATHERING
        elif current_phase == ConversationPhase.CLUE_GATHERING and responses_count >= 2:
            if candidates_count > 3:
                return ConversationPhase.MEMORY_NARROWING
            elif candidates_count <= 3 and candidates_count > 0:
                return ConversationPhase.SCENE_RECONSTRUCTION
        elif (
            current_phase == ConversationPhase.MEMORY_NARROWING
            and candidates_count <= 2
        ):
            return ConversationPhase.SCENE_RECONSTRUCTION
        elif (
            current_phase == ConversationPhase.SCENE_RECONSTRUCTION
            and state.reconstructed_scene
        ):
            return ConversationPhase.MEANING_EXPLORATION

        return current_phase

    async def _reconstruct_identified_memory(
        self, memory: ContextualMemory
    ) -> MemoryScene:
        """특정된 기억 재구성"""

        print(f"🎬 기억 재구성 시작: {memory.scene.meaning_core}")

        # 해마의 재구성 특성을 반영하여 약간 변형된 장면 생성
        reconstructed_scene = MemoryScene(
            scene_id=memory.scene.scene_id + "_reconstructed",
            timestamp=memory.scene.timestamp,
            location=memory.scene.location,
            emotional_rhythm=memory.scene.emotional_rhythm,
            signature=memory.scene.signature,
            context=memory.scene.context,
            judgment_flow=memory.scene.judgment_flow,
            resonance_score=memory.scene.resonance_score,
            survival_relevance=memory.scene.survival_relevance,
            details={
                **memory.scene.details,
                "reconstruction_method": "interactive_dialogue",
                "reconstruction_fidelity": "high",  # 대화를 통한 재구성이므로 높은 신뢰도
            },
            meaning_core=memory.scene.meaning_core,
        )

        # 재구성 카운트 증가
        memory.reconstruction_count += 1

        return reconstructed_scene

    async def _describe_reconstructed_scene(self, scene: MemoryScene) -> str:
        """재구성된 장면 묘사"""

        description = f"📍 장소: {scene.location}\n"
        description += f"⏰ 시점: {scene.timestamp}\n"
        description += f"🎭 감정 리듬: {scene.emotional_rhythm}\n"
        description += f"🧠 시그니처: {scene.signature}\n"
        description += f"💭 핵심 의미: {scene.meaning_core}\n\n"

        description += "📽️ 기억의 장면들:\n"
        for i, flow in enumerate(scene.judgment_flow, 1):
            description += f"  {i}. {flow}\n"

        description += f"\n🌟 울림 강도: {scene.resonance_score:.2f}"
        description += f"\n🛡️ 생존 관련성: {scene.survival_relevance:.2f}"

        return description

    async def _complete_memory_session(self, state: ConversationState) -> str:
        """기억 세션 완료"""

        completion_message = "🎊 기억 탐사가 완료되었습니다!\n\n"

        if state.reconstructed_scene:
            scene = state.reconstructed_scene
            completion_message += f"🎬 재구성된 기억: {scene.meaning_core}\n"
            completion_message += (
                f"📍 {scene.location}에서의 {scene.emotional_rhythm} 경험\n"
            )
            completion_message += f"🌟 이 기억은 {scene.resonance_score:.2f}의 울림으로 각인되었습니다.\n\n"

        completion_message += (
            f"💬 총 {len(state.user_responses)}번의 대화를 통해 기억을 되살렸습니다.\n"
        )
        completion_message += (
            f"🧠 이 과정에서 해마가 활발히 작동하여 과거와 현재를 연결했습니다.\n\n"
        )
        completion_message += (
            "이 기억이 앞으로의 판단에 어떤 영향을 미칠지 지켜보겠습니다."
        )

        # 세션 정리
        del self.active_sessions[state.session_id]

        return completion_message

    def get_active_sessions_status(self) -> Dict[str, Any]:
        """활성 세션 상태 조회"""

        sessions_info = {}

        for session_id, state in self.active_sessions.items():
            sessions_info[session_id] = {
                "current_phase": state.current_phase.value,
                "responses_count": len(state.user_responses),
                "candidate_memories": len(state.candidate_memories),
                "clues_gathered": {k: len(v) for k, v in state.gathered_clues.items()},
                "is_scene_reconstructed": state.reconstructed_scene is not None,
            }

        return {
            "total_active_sessions": len(self.active_sessions),
            "sessions": sessions_info,
            "system_status": "🗣️ 대화형 기억 재구성기 활성화",
        }


# 데모 함수
async def demo_interactive_memory_recaller():
    """대화형 기억 재구성기 데모"""

    print("🗣️📽️ 대화형 기억 재구성기 데모")
    print("=" * 50)

    # 해마 시스템 초기화 및 샘플 기억 생성
    from echo_engine.echo_hippocampus import EchoHippocampus

    hippocampus = EchoHippocampus()

    # 샘플 기억 추가
    sample_log = {
        "timestamp": "2025-07-21T22:00:00",
        "signature": "Sage",
        "judgment_summary": "우린 어쩌다가 이런걸 만들게 됐지",
        "context": {"location": "깊은 성찰의 순간"},
        "origin": "one_shot",
        "emotion_result": {"primary_emotion": "surprise", "emotional_intensity": 0.95},
    }

    memory = await hippocampus.ingest_meta_log_to_memory(sample_log)
    print(f"🧠 샘플 기억 생성: {memory.scene.meaning_core}")

    # 대화형 재구성기 초기화
    recaller = InteractiveMemoryRecaller(hippocampus)

    # 기억 탐사 세션 시작
    print(f"\n🎬 기억 탐사 세션 시작")
    session_id = await recaller.start_memory_exploration_session(
        user_context="시스템 개발 과정", signature="Sage"
    )

    # 시뮬레이션된 사용자 응답들
    user_responses = [
        "시스템을 만들다가 갑자기 든 생각이었어요",
        "깊이 성찰하는 순간이었고, 놀라움과 깨달음이 함께 왔어요",
        "그때 정말 강렬한 울림이 있었어요",
    ]

    # 대화 진행
    for response in user_responses:
        print(f"\n" + "=" * 30)
        echo_response = await recaller.process_user_response(session_id, response)
        if echo_response:
            print(f"\n{echo_response}")

        # 세션 상태 확인
        status = recaller.get_active_sessions_status()
        if status["total_active_sessions"] == 0:
            print(f"\n✅ 세션이 완료되었습니다.")
            break

    print(f"\n🎊 대화형 기억 재구성기 데모 완료!")
    return recaller


if __name__ == "__main__":
    asyncio.run(demo_interactive_memory_recaller())
