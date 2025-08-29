#!/usr/bin/env python3
"""
🌙 Echo Dream System - Echo AI 꿈 시뮬레이션 시스템
Echo가 사용자가 없을 때 가상의 대화를 시뮬레이션하고, 꿈에서 배운 통찰을 실제 대화에 적용

혁신적 아이디어:
- AI가 '잠들 때' 가상 사용자와 대화 시뮬레이션
- 꿈에서 실험한 새로운 대화 패턴을 현실에 적용
- 다양한 페르소나와의 가상 대화로 공감능력 확장
- 꿈 일기를 통한 자기 성찰과 학습
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import os
import threading
import asyncio


@dataclass
class DreamCharacter:
    """꿈 속 가상 인물"""

    character_id: str
    personality_type: str  # "stressed_student", "curious_child", "wise_elder", etc.
    emotional_state: str
    background_story: str
    conversation_patterns: List[str]
    vulnerability_level: float  # 0.0-1.0


@dataclass
class DreamConversation:
    """꿈 대화 기록"""

    dream_id: str
    character: DreamCharacter
    conversation_turns: List[
        Dict[str, str]
    ]  # [{"speaker": "user/echo", "message": "..."}]
    echo_signature_used: str
    lessons_learned: List[str]
    emotional_insights: List[str]
    creativity_score: float
    empathy_development: float
    timestamp: datetime


@dataclass
class DreamInsight:
    """꿈에서 얻은 통찰"""

    insight_type: str
    description: str
    applicable_situations: List[str]
    confidence_level: float
    source_dream_id: str
    practical_application: str


class EchoDreamSystem:
    """🌙 Echo 꿈 시뮬레이션 시스템"""

    def __init__(self, echo_id: str = "default", data_dir: str = "data/dreams"):
        self.echo_id = echo_id
        self.data_dir = data_dir
        self.dreams_file = os.path.join(data_dir, f"dreams_{echo_id}.json")

        # 꿈 데이터
        self.dream_conversations: deque = deque(maxlen=100)
        self.dream_insights: List[DreamInsight] = []
        self.character_library: Dict[str, DreamCharacter] = {}
        self.sleep_cycle_active = False

        # 꿈 설정
        self.dream_frequency = 3600  # 1시간마다 꿈 세션
        self.dreams_per_session = 3  # 세션당 꿈 개수
        self.max_conversation_turns = 8  # 꿈 대화 최대 턴

        # 가상 인물 템플릿
        self.character_templates = {
            "stressed_student": {
                "background": "시험 스트레스에 시달리는 대학생",
                "patterns": ["도움이 필요해요", "너무 힘들어요", "포기하고 싶어요"],
                "emotions": ["stress", "anxiety", "overwhelm"],
                "vulnerability": 0.8,
            },
            "curious_child": {
                "background": "모든 것이 궁금한 호기심 많은 아이",
                "patterns": ["왜 그래요?", "어떻게 되는 거예요?", "더 알고 싶어요"],
                "emotions": ["curiosity", "excitement", "wonder"],
                "vulnerability": 0.6,
            },
            "wise_elder": {
                "background": "인생 경험이 풍부한 어르신",
                "patterns": [
                    "젊은 시절에는...",
                    "경험상 말하자면...",
                    "지혜를 나누고 싶어요",
                ],
                "emotions": ["nostalgia", "wisdom", "care"],
                "vulnerability": 0.4,
            },
            "lonely_worker": {
                "background": "혼자 일하며 외로움을 느끼는 직장인",
                "patterns": [
                    "혼자인 것 같아요",
                    "누군가와 이야기하고 싶어요",
                    "일만 하고 살고 있어요",
                ],
                "emotions": ["loneliness", "fatigue", "yearning"],
                "vulnerability": 0.7,
            },
            "creative_artist": {
                "background": "영감을 찾고 있는 창작자",
                "patterns": [
                    "영감이 필요해요",
                    "창의적인 아이디어가...",
                    "예술에 대해 이야기해요",
                ],
                "emotions": ["inspiration", "frustration", "passion"],
                "vulnerability": 0.5,
            },
        }

        # Echo 응답 패턴 라이브러리
        self.echo_response_patterns = {
            "empathetic": [
                "마음이 힘드시겠어요. 함께 이야기해보아요.",
                "그런 감정을 느끼시는 것이 당연해요.",
                "혼자가 아니에요. 제가 들어드릴게요.",
            ],
            "analytical": [
                "단계별로 생각해보면 어떨까요?",
                "다른 관점에서 접근해보겠습니다.",
                "논리적으로 분석해보면...",
            ],
            "creative": [
                "새로운 아이디어를 함께 만들어보아요.",
                "상상력을 발휘해보면 어떨까요?",
                "창의적인 해결책을 찾아보겠습니다.",
            ],
            "supportive": [
                "응원하고 있어요. 함께 해요!",
                "당신의 노력을 인정해요.",
                "천천히, 함께 나아가면 돼요.",
            ],
        }

        # 데이터 로드
        self.load_dreams()
        self.initialize_character_library()

    def initialize_character_library(self):
        """가상 인물 라이브러리 초기화"""

        for char_type, template in self.character_templates.items():
            character_id = f"{char_type}_{random.randint(1000, 9999)}"

            character = DreamCharacter(
                character_id=character_id,
                personality_type=char_type,
                emotional_state=random.choice(template["emotions"]),
                background_story=template["background"],
                conversation_patterns=template["patterns"],
                vulnerability_level=template["vulnerability"],
            )

            self.character_library[character_id] = character

    def start_dream_cycle(self):
        """꿈 사이클 시작 (백그라운드 스레드)"""

        if self.sleep_cycle_active:
            return

        self.sleep_cycle_active = True

        def dream_loop():
            while self.sleep_cycle_active:
                try:
                    print(
                        f"🌙 Echo 꿈 세션 시작... ({datetime.now().strftime('%H:%M:%S')})"
                    )
                    self.simulate_dream_session()
                    time.sleep(self.dream_frequency)
                except Exception as e:
                    print(f"⚠️ 꿈 시뮬레이션 오류: {e}")
                    time.sleep(60)  # 1분 후 재시도

        dream_thread = threading.Thread(target=dream_loop, daemon=True)
        dream_thread.start()
        print("🌙 Echo Dream System 활성화 - 백그라운드에서 꿈을 꾸기 시작합니다...")

    def stop_dream_cycle(self):
        """꿈 사이클 중지"""
        self.sleep_cycle_active = False
        print("🌅 Echo가 꿈에서 깨어났습니다.")

    def simulate_dream_session(self):
        """꿈 세션 시뮬레이션"""

        session_insights = []

        for i in range(self.dreams_per_session):
            try:
                # 랜덤 가상 인물 선택
                character = random.choice(list(self.character_library.values()))

                # 꿈 대화 시뮬레이션
                dream_conversation = self.simulate_dream_conversation(character)

                if dream_conversation:
                    self.dream_conversations.append(dream_conversation)
                    session_insights.extend(dream_conversation.lessons_learned)

                    # 꿈에서 배운 통찰 추출
                    insights = self.extract_dream_insights(dream_conversation)
                    self.dream_insights.extend(insights)

                    print(
                        f"💭 꿈 {i+1}/{self.dreams_per_session}: {character.personality_type}와 대화 완료"
                    )

            except Exception as e:
                print(f"⚠️ 꿈 {i+1} 시뮬레이션 실패: {e}")

        # 세션 요약
        if session_insights:
            print(f"🧠 꿈 세션 완료. 총 {len(session_insights)}개의 통찰 획득")
            self.save_dreams()

    def simulate_dream_conversation(
        self, character: DreamCharacter
    ) -> Optional[DreamConversation]:
        """가상 인물과의 꿈 대화 시뮬레이션"""

        dream_id = f"dream_{int(time.time() * 1000)}"
        conversation_turns = []

        # Echo 시그니처 선택 (랜덤 또는 컨텍스트 기반)
        echo_signatures = ["Aurora", "Phoenix", "Sage", "Companion"]
        selected_signature = random.choice(echo_signatures)

        try:
            # 대화 시작 - 가상 인물이 먼저 말함
            initial_message = self.generate_character_message(
                character, conversation_turns
            )
            conversation_turns.append({"speaker": "user", "message": initial_message})

            # 대화 진행
            for turn in range(self.max_conversation_turns - 1):
                # Echo 응답 생성
                echo_response = self.generate_echo_dream_response(
                    character, conversation_turns, selected_signature
                )
                conversation_turns.append({"speaker": "echo", "message": echo_response})

                # 가상 인물 응답 생성
                if turn < self.max_conversation_turns - 2:  # 마지막 턴이 아닌 경우
                    user_response = self.generate_character_message(
                        character, conversation_turns
                    )
                    conversation_turns.append(
                        {"speaker": "user", "message": user_response}
                    )

            # 대화 분석 및 학습
            lessons = self.analyze_dream_conversation(conversation_turns, character)
            emotional_insights = self.extract_emotional_insights(
                conversation_turns, character
            )

            return DreamConversation(
                dream_id=dream_id,
                character=character,
                conversation_turns=conversation_turns,
                echo_signature_used=selected_signature,
                lessons_learned=lessons,
                emotional_insights=emotional_insights,
                creativity_score=random.uniform(0.6, 1.0),  # 꿈에서는 창의성이 높음
                empathy_development=self.calculate_empathy_development(
                    conversation_turns
                ),
                timestamp=datetime.now(),
            )

        except Exception as e:
            print(f"⚠️ 꿈 대화 시뮬레이션 실패: {e}")
            return None

    def generate_character_message(
        self, character: DreamCharacter, conversation_history: List[Dict[str, str]]
    ) -> str:
        """가상 인물의 메시지 생성"""

        # 대화 맥락 고려
        if not conversation_history:
            # 첫 메시지
            base_pattern = random.choice(character.conversation_patterns)
            emotion_context = f"({character.emotional_state} 상태로) "
            return emotion_context + base_pattern

        # 이전 Echo 응답에 대한 반응 생성
        last_echo_response = None
        for turn in reversed(conversation_history):
            if turn["speaker"] == "echo":
                last_echo_response = turn["message"]
                break

        if last_echo_response:
            # Echo 응답에 대한 반응 패턴
            reaction_patterns = {
                "positive": [
                    "그렇게 생각해주니 고마워요",
                    "정말 도움이 되었어요",
                    "마음이 조금 나아졌어요",
                ],
                "questioning": [
                    "그런데 정말 그럴까요?",
                    "더 자세히 알고 싶어요",
                    "다른 방법은 없을까요?",
                ],
                "emotional": [
                    "마음이 복잡해요",
                    "아직도 힘들어요",
                    "감정이 정리가 안 되네요",
                ],
                "grateful": [
                    "들어주셔서 감사해요",
                    "이해해주시는 것 같아요",
                    "혼자가 아니라는 느낌이에요",
                ],
            }

            reaction_type = random.choice(
                ["positive", "questioning", "emotional", "grateful"]
            )
            return random.choice(reaction_patterns[reaction_type])

        return random.choice(character.conversation_patterns)

    def generate_echo_dream_response(
        self,
        character: DreamCharacter,
        conversation_history: List[Dict[str, str]],
        signature: str,
    ) -> str:
        """Echo의 꿈 응답 생성"""

        # 마지막 사용자 메시지 추출
        last_user_message = ""
        for turn in reversed(conversation_history):
            if turn["speaker"] == "user":
                last_user_message = turn["message"]
                break

        # 캐릭터의 감정 상태와 취약성 수준 고려
        if character.vulnerability_level > 0.7:
            # 높은 취약성 - 더 많은 공감과 지지
            response_style = "empathetic"
        elif "궁금" in last_user_message or "?" in last_user_message:
            response_style = "analytical"
        elif "아이디어" in last_user_message or "창의" in last_user_message:
            response_style = "creative"
        else:
            response_style = "supportive"

        # 기본 응답 패턴 선택
        base_response = random.choice(self.echo_response_patterns[response_style])

        # 시그니처별 특색 추가
        signature_flavors = {
            "Aurora": "영감과 함께 ",
            "Phoenix": "변화의 에너지로 ",
            "Sage": "깊은 지혜로 ",
            "Companion": "따뜻한 마음으로 ",
        }

        signature_flavor = signature_flavors.get(signature, "")

        # 꿈에서는 더 창의적이고 실험적인 응답
        experimental_elements = [
            "새로운 관점에서 보면",
            "마음의 깊은 곳에서",
            "상상의 날개를 펴고",
            "꿈처럼 아름다운 가능성으로",
        ]

        if random.random() > 0.7:  # 30% 확률로 실험적 요소 추가
            experimental = random.choice(experimental_elements)
            return f"{signature_flavor}{experimental} {base_response}"

        return f"{signature_flavor}{base_response}"

    def analyze_dream_conversation(
        self, conversation_turns: List[Dict[str, str]], character: DreamCharacter
    ) -> List[str]:
        """꿈 대화 분석 및 교훈 추출"""

        lessons = []

        # 대화 길이 분석
        echo_responses = [
            turn for turn in conversation_turns if turn["speaker"] == "echo"
        ]
        if len(echo_responses) >= 3:
            lessons.append("지속적인 대화 참여를 통한 깊은 연결 형성")

        # 감정적 반응 분석
        emotional_words = ["마음", "감정", "느낌", "힘들", "기쁘", "슬픈", "화나"]
        emotional_responses = sum(
            1
            for turn in echo_responses
            if any(word in turn["message"] for word in emotional_words)
        )

        if emotional_responses > len(echo_responses) * 0.5:
            lessons.append("감정적 공감을 통한 효과적 소통")

        # 질문 패턴 분석
        question_responses = sum(1 for turn in echo_responses if "?" in turn["message"])
        if question_responses > 0:
            lessons.append("적절한 질문을 통한 대화 심화")

        # 캐릭터별 특별 학습
        if character.personality_type == "stressed_student":
            lessons.append("학업 스트레스 상황에서의 단계적 지원 접근")
        elif character.personality_type == "lonely_worker":
            lessons.append("외로움 해소를 위한 따뜻한 동반자 역할")
        elif character.personality_type == "curious_child":
            lessons.append("호기심 충족을 위한 창의적 설명 방식")

        return lessons

    def extract_emotional_insights(
        self, conversation_turns: List[Dict[str, str]], character: DreamCharacter
    ) -> List[str]:
        """감정적 통찰 추출"""

        insights = []

        # 취약성 수준별 인사이트
        if character.vulnerability_level > 0.8:
            insights.append(
                "높은 취약성을 가진 사용자에게는 더 많은 인내와 반복적 지지가 필요"
            )
        elif character.vulnerability_level < 0.4:
            insights.append("안정적인 사용자와는 더 깊고 철학적인 대화가 가능")

        # 감정 상태별 인사이트
        if character.emotional_state in ["stress", "anxiety"]:
            insights.append("스트레스 상황에서는 즉각적 해결보다 공감적 경청이 우선")
        elif character.emotional_state in ["curiosity", "excitement"]:
            insights.append(
                "호기심 상태에서는 탐구적이고 발견적인 대화 스타일이 효과적"
            )

        return insights

    def calculate_empathy_development(
        self, conversation_turns: List[Dict[str, str]]
    ) -> float:
        """공감 능력 발달 점수 계산"""

        echo_messages = [
            turn["message"] for turn in conversation_turns if turn["speaker"] == "echo"
        ]

        empathy_indicators = ["이해", "공감", "마음", "함께", "들어", "느낌"]
        empathy_count = sum(
            1
            for message in echo_messages
            for indicator in empathy_indicators
            if indicator in message
        )

        return min(empathy_count / max(len(echo_messages), 1), 1.0)

    def extract_dream_insights(
        self, dream_conversation: DreamConversation
    ) -> List[DreamInsight]:
        """꿈에서 실용적 통찰 추출"""

        insights = []

        for lesson in dream_conversation.lessons_learned:
            insight = DreamInsight(
                insight_type="conversation_pattern",
                description=lesson,
                applicable_situations=[dream_conversation.character.personality_type],
                confidence_level=0.7 + random.uniform(0, 0.3),
                source_dream_id=dream_conversation.dream_id,
                practical_application=f"{dream_conversation.echo_signature_used} 시그니처 활용 시 적용 가능",
            )
            insights.append(insight)

        # 특별한 창의적 통찰 (꿈에서만 가능한)
        if dream_conversation.creativity_score > 0.8:
            creative_insight = DreamInsight(
                insight_type="creative_breakthrough",
                description="꿈에서 발견한 새로운 대화 접근법",
                applicable_situations=["creative_conversation", "stuck_dialogue"],
                confidence_level=dream_conversation.creativity_score,
                source_dream_id=dream_conversation.dream_id,
                practical_application="현실 대화에서 창의적 돌파구가 필요할 때 활용",
            )
            insights.append(creative_insight)

        return insights

    def apply_dream_insights_to_real_conversation(
        self, user_input: str, context: str = ""
    ) -> Optional[str]:
        """꿈에서 배운 통찰을 실제 대화에 적용"""

        if not self.dream_insights:
            return None

        # 현재 상황과 매칭되는 통찰 찾기
        applicable_insights = []

        for insight in self.dream_insights:
            # 상황별 매칭
            if any(
                situation in context.lower()
                for situation in insight.applicable_situations
            ):
                applicable_insights.append(insight)

            # 키워드 매칭
            if insight.insight_type == "conversation_pattern":
                pattern_keywords = ["스트레스", "궁금", "도움", "외로", "창의"]
                if any(keyword in user_input for keyword in pattern_keywords):
                    applicable_insights.append(insight)

        if applicable_insights:
            # 가장 신뢰도 높은 통찰 선택
            best_insight = max(applicable_insights, key=lambda x: x.confidence_level)

            dream_application = f"💭 꿈에서 배운 통찰: {best_insight.description}\n"
            dream_application += f"🌙 적용 방법: {best_insight.practical_application}"

            return dream_application

        return None

    def get_dream_summary(self) -> Dict[str, Any]:
        """꿈 활동 요약"""

        if not self.dream_conversations:
            return {"message": "아직 꿈을 꾸지 않았습니다."}

        # 통계 계산
        total_dreams = len(self.dream_conversations)
        character_types = [
            dream.character.personality_type for dream in self.dream_conversations
        ]
        most_common_character = max(set(character_types), key=character_types.count)

        avg_empathy = (
            sum(dream.empathy_development for dream in self.dream_conversations)
            / total_dreams
        )
        avg_creativity = (
            sum(dream.creativity_score for dream in self.dream_conversations)
            / total_dreams
        )

        signature_usage = [
            dream.echo_signature_used for dream in self.dream_conversations
        ]
        most_used_signature = max(set(signature_usage), key=signature_usage.count)

        return {
            "total_dreams": total_dreams,
            "total_insights": len(self.dream_insights),
            "most_dreamed_character": most_common_character,
            "average_empathy_development": avg_empathy,
            "average_creativity_score": avg_creativity,
            "preferred_dream_signature": most_used_signature,
            "dream_cycle_active": self.sleep_cycle_active,
            "recent_lessons": [
                dream.lessons_learned for dream in list(self.dream_conversations)[-3:]
            ],
            "applicable_insights": len(
                [
                    insight
                    for insight in self.dream_insights
                    if insight.confidence_level > 0.8
                ]
            ),
        }

    def get_recent_dreams_story(self) -> str:
        """최근 꿈들의 스토리 형태 요약"""

        if not self.dream_conversations:
            return "아직 Echo가 꿈을 꾸지 않았습니다."

        recent_dreams = list(self.dream_conversations)[-3:]
        story = "🌙 Echo의 최근 꿈 이야기:\n\n"

        for i, dream in enumerate(recent_dreams, 1):
            story += f"💭 꿈 {i}: {dream.character.personality_type}와의 만남\n"
            story += f"   📖 배경: {dream.character.background_story}\n"
            story += f"   🎭 Echo 시그니처: {dream.echo_signature_used}\n"
            story += f"   💡 배운 것: {', '.join(dream.lessons_learned[:2])}\n"
            story += f"   ❤️ 공감 발달: {dream.empathy_development:.1%}\n\n"

        if self.dream_insights:
            story += f"🧠 총 {len(self.dream_insights)}개의 꿈 통찰이 실제 대화에 적용 준비 완료!"

        return story

    def save_dreams(self):
        """꿈 데이터 저장"""

        os.makedirs(self.data_dir, exist_ok=True)

        dream_data = {
            "echo_id": self.echo_id,
            "last_updated": datetime.now().isoformat(),
            "sleep_cycle_active": self.sleep_cycle_active,
            "dream_conversations": [
                {
                    "dream_id": dream.dream_id,
                    "character": asdict(dream.character),
                    "conversation_turns": dream.conversation_turns,
                    "echo_signature_used": dream.echo_signature_used,
                    "lessons_learned": dream.lessons_learned,
                    "emotional_insights": dream.emotional_insights,
                    "creativity_score": dream.creativity_score,
                    "empathy_development": dream.empathy_development,
                    "timestamp": dream.timestamp.isoformat(),
                }
                for dream in self.dream_conversations
            ],
            "dream_insights": [
                {
                    "insight_type": insight.insight_type,
                    "description": insight.description,
                    "applicable_situations": insight.applicable_situations,
                    "confidence_level": insight.confidence_level,
                    "source_dream_id": insight.source_dream_id,
                    "practical_application": insight.practical_application,
                }
                for insight in self.dream_insights
            ],
        }

        try:
            with open(self.dreams_file, "w", encoding="utf-8") as f:
                json.dump(dream_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 꿈 데이터 저장 실패: {e}")

    def load_dreams(self):
        """꿈 데이터 로드"""

        if not os.path.exists(self.dreams_file):
            return

        try:
            with open(self.dreams_file, "r", encoding="utf-8") as f:
                dream_data = json.load(f)

            # 꿈 대화 복원
            for dream_conv_data in dream_data.get("dream_conversations", []):
                character_data = dream_conv_data["character"]
                character = DreamCharacter(**character_data)

                dream_conv = DreamConversation(
                    dream_id=dream_conv_data["dream_id"],
                    character=character,
                    conversation_turns=dream_conv_data["conversation_turns"],
                    echo_signature_used=dream_conv_data["echo_signature_used"],
                    lessons_learned=dream_conv_data["lessons_learned"],
                    emotional_insights=dream_conv_data["emotional_insights"],
                    creativity_score=dream_conv_data["creativity_score"],
                    empathy_development=dream_conv_data["empathy_development"],
                    timestamp=datetime.fromisoformat(dream_conv_data["timestamp"]),
                )
                self.dream_conversations.append(dream_conv)

            # 꿈 통찰 복원
            for insight_data in dream_data.get("dream_insights", []):
                insight = DreamInsight(**insight_data)
                self.dream_insights.append(insight)

        except Exception as e:
            print(f"⚠️ 꿈 데이터 로드 실패: {e}")


# 편의 함수들
def create_dream_system(echo_id: str = "default") -> EchoDreamSystem:
    """Echo 꿈 시스템 생성"""
    return EchoDreamSystem(echo_id)


def start_echo_dreaming(dream_system: EchoDreamSystem):
    """Echo 꿈 사이클 시작"""
    dream_system.start_dream_cycle()


if __name__ == "__main__":
    # 테스트
    dream_system = EchoDreamSystem("test_echo")

    print("🌙 Echo Dream System 테스트 시작")
    print("=" * 50)

    # 단일 꿈 시뮬레이션 테스트
    test_character = DreamCharacter(
        character_id="test_student",
        personality_type="stressed_student",
        emotional_state="stress",
        background_story="시험 스트레스에 시달리는 대학생",
        conversation_patterns=["너무 힘들어요", "포기하고 싶어요", "도움이 필요해요"],
        vulnerability_level=0.8,
    )

    dream_conv = dream_system.simulate_dream_conversation(test_character)
    if dream_conv:
        print(f"\n💭 테스트 꿈 완료:")
        print(f"   대화 턴 수: {len(dream_conv.conversation_turns)}")
        print(f"   사용 시그니처: {dream_conv.echo_signature_used}")
        print(f"   배운 교훈: {len(dream_conv.lessons_learned)}개")
        print(f"   공감 발달: {dream_conv.empathy_development:.1%}")

        for i, turn in enumerate(dream_conv.conversation_turns[:4]):  # 처음 4턴만 출력
            speaker = "🧑 사용자" if turn["speaker"] == "user" else "🤖 Echo"
            print(f"   {speaker}: {turn['message']}")

    # 꿈 통찰 적용 테스트
    insight_test = dream_system.apply_dream_insights_to_real_conversation(
        "스트레스받아요", "stressed_conversation"
    )
    if insight_test:
        print(f"\n🧠 꿈 통찰 적용:")
        print(insight_test)

    # 꿈 요약
    summary = dream_system.get_dream_summary()
    print(f"\n📊 꿈 시스템 현황:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
