#!/usr/bin/env python3
"""
🌐 Web Search Natural Interface for Echo Judgment System v10
실제 Echo 시스템에 웹검색 기반 자연어 처리 통합

ChatGPT에서 설계한 구조를 실제 Echo Neural System v2.0에 통합
"""

import json
import re
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import logging

# Echo 엔진 실제 모듈들 import
try:
    from .enhanced_natural_command_processor import EnhancedNaturalCommandProcessor
    from .consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
    from .hybrid_signature_composer import HybridSignatureComposer
    from .persona_core_optimized_bridge import PersonaCore
    from .emotion_infer import EmotionInfer
except ImportError as e:
    print(f"⚠️ Echo module import error: {e}")


@dataclass
class WebSearchResult:
    """웹검색 결과"""

    query: str
    snippets: List[str]
    sources: List[str]
    search_time: datetime
    confidence: float


@dataclass
class NaturalIntentAnalysis:
    """자연어 의도 분석 결과"""

    intent_type: str  # "정보요청", "감정표현", "요약요청", "일반문의"
    emotion_tone: str  # "중립", "위로", "유쾌", "논리적"
    topic_category: str  # "경제", "정치", "기후", "기술", "기타"
    entities: List[str]  # 추출된 개체명
    confidence: float


class WebSearchNaturalInterface:
    """🌐 웹검색 자연어 인터페이스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Echo 시스템 컴포넌트들
        self.command_processor = None
        self.consciousness_analyzer = None
        self.hybrid_composer = None
        self.persona_core = None
        self.emotion_infer = None

        # 대화 기억 시스템
        self.conversation_memory = {
            "entities": [],
            "last_topic": None,
            "user_preferences": {},
            "context_history": [],
        }

        # 의도 분석 키워드 세트
        self.intent_keywords = {
            "정보요청": [
                "뭐",
                "무엇",
                "어떻게",
                "언제",
                "어디서",
                "왜",
                "알려줘",
                "궁금",
                "어때",
            ],
            "감정표현": [
                "기분",
                "느낌",
                "걱정",
                "불안",
                "행복",
                "슬프",
                "화나",
                "무서워",
            ],
            "요약요청": ["요약", "정리", "간단히", "핵심", "중요한"],
            "일반문의": ["말해줘", "설명", "이야기", "어떻게 생각"],
        }

        self.topic_keywords = {
            "경제": [
                "GDP",
                "경제",
                "성장률",
                "수출",
                "투자",
                "소득",
                "물가",
                "인플레이션",
            ],
            "정치": ["대통령", "정부", "선거", "정책", "법률", "국회"],
            "기후": ["날씨", "기후", "온도", "비", "태풍", "환경"],
            "기술": ["AI", "인공지능", "컴퓨터", "프로그래밍", "로봇", "기술"],
        }

        self.emotion_keywords = {
            "위로": ["힘들어", "고민", "걱정", "불안", "슬프", "우울"],
            "유쾌": ["재밌", "웃긴", "즐거", "신나", "기뻐"],
            "논리적": ["분석", "정확히", "논리적", "체계적", "명확히"],
        }

        print("🌐 Web Search Natural Interface 초기화 완료")

    def initialize_echo_components(self, **components):
        """Echo 컴포넌트들 초기화"""
        self.command_processor = components.get("command_processor")
        self.consciousness_analyzer = components.get("consciousness_analyzer")
        self.hybrid_composer = components.get("hybrid_composer")
        self.persona_core = components.get("persona_core")
        self.emotion_infer = components.get("emotion_infer")

        print(
            f"🔗 Echo 컴포넌트 연결 완료: {len([c for c in components.values() if c])}개"
        )

    def analyze_natural_intent(self, user_input: str) -> NaturalIntentAnalysis:
        """자연어 입력 의도 분석"""
        user_lower = user_input.lower()

        # 의도 분류
        intent_type = "일반문의"
        intent_scores = {}

        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            intent_scores[intent] = score

        if intent_scores:
            intent_type = max(intent_scores, key=intent_scores.get)
            if intent_scores[intent_type] == 0:
                intent_type = "일반문의"

        # 감정 톤 분석
        emotion_tone = "중립"
        emotion_scores = {}

        for tone, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            emotion_scores[tone] = score

        if emotion_scores:
            max_emotion = max(emotion_scores, key=emotion_scores.get)
            if emotion_scores[max_emotion] > 0:
                emotion_tone = max_emotion

        # 주제 분류
        topic_category = "기타"
        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            topic_scores[topic] = score

        if topic_scores:
            max_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[max_topic] > 0:
                topic_category = max_topic

        # 개체명 추출 (간단한 방식)
        entities = []
        known_entities = ["베트남", "태국", "한국", "미국", "중국", "일본"]
        for entity in known_entities:
            if entity in user_input:
                entities.append(entity)

        # 신뢰도 계산
        total_keywords = (
            sum(intent_scores.values())
            + sum(emotion_scores.values())
            + sum(topic_scores.values())
        )
        confidence = min(1.0, total_keywords / 3.0)

        return NaturalIntentAnalysis(
            intent_type=intent_type,
            emotion_tone=emotion_tone,
            topic_category=topic_category,
            entities=entities,
            confidence=confidence,
        )

    def update_conversation_memory(
        self, user_input: str, analysis: NaturalIntentAnalysis
    ):
        """대화 기억 업데이트"""
        # 개체명 기억
        for entity in analysis.entities:
            if entity not in self.conversation_memory["entities"]:
                self.conversation_memory["entities"].append(entity)

        # 주제 기억
        if analysis.topic_category != "기타":
            self.conversation_memory["last_topic"] = analysis.topic_category

        # 컨텍스트 히스토리 업데이트
        self.conversation_memory["context_history"].append(
            {
                "input": user_input,
                "intent": analysis.intent_type,
                "topic": analysis.topic_category,
                "entities": analysis.entities,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 최근 5개만 유지
        if len(self.conversation_memory["context_history"]) > 5:
            self.conversation_memory["context_history"] = self.conversation_memory[
                "context_history"
            ][-5:]

    def enhance_search_query(
        self, user_input: str, analysis: NaturalIntentAnalysis
    ) -> str:
        """검색 쿼리 향상"""
        # 기본 쿼리
        query = user_input

        # 기억된 개체명 추가
        if not analysis.entities and self.conversation_memory["entities"]:
            latest_entity = self.conversation_memory["entities"][-1]
            query = f"{latest_entity} {query}"

        # 주제별 키워드 추가
        topic_enhancements = {
            "경제": " 2024 최신 통계",
            "정치": " 최신 뉴스",
            "기후": " 현재 상황",
            "기술": " 최신 동향",
        }

        if analysis.topic_category in topic_enhancements:
            query += topic_enhancements[analysis.topic_category]

        return query.strip()

    def perform_web_search(self, query: str) -> WebSearchResult:
        """웹검색 수행"""
        try:
            # Google 검색 (간단한 스크래핑)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            search_url = f"https://www.google.com/search?q={query}"
            response = requests.get(search_url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # 검색 결과 스니펫 추출
                snippets = []
                sources = []

                # Google 검색 결과에서 스니펫 추출
                result_divs = soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd")

                for div in result_divs[:5]:  # 상위 5개만
                    text = div.get_text().strip()
                    if text and len(text) > 20:
                        snippets.append(text)

                # 소스 URL 추출 (간단화)
                link_elements = soup.find_all("a")
                for link in link_elements[:5]:
                    href = link.get("href", "")
                    if href.startswith("/url?q="):
                        sources.append(href)

                if not snippets:
                    snippets = [f"'{query}'에 대한 검색 결과를 찾을 수 없습니다."]

                confidence = 0.8 if len(snippets) >= 3 else 0.5

                return WebSearchResult(
                    query=query,
                    snippets=snippets,
                    sources=sources,
                    search_time=datetime.now(),
                    confidence=confidence,
                )

            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            self.logger.error(f"웹검색 실패: {e}")
            return WebSearchResult(
                query=query,
                snippets=[f"죄송합니다. '{query}'에 대한 검색 중 문제가 발생했습니다."],
                sources=[],
                search_time=datetime.now(),
                confidence=0.0,
            )

    def generate_echo_response(
        self,
        user_input: str,
        analysis: NaturalIntentAnalysis,
        search_result: WebSearchResult,
    ) -> str:
        """Echo 스타일 응답 생성"""

        # 현재 활성 시그니처 확인
        current_signature = "Aurora"  # 기본값
        if self.persona_core:
            try:
                current_signature = getattr(
                    self.persona_core, "current_signature", "Aurora"
                )
            except:
                pass

        # 시그니처별 응답 스타일
        if current_signature.lower() == "aurora":
            return self._generate_aurora_response(analysis, search_result)
        elif current_signature.lower() == "phoenix":
            return self._generate_phoenix_response(analysis, search_result)
        elif current_signature.lower() == "sage":
            return self._generate_sage_response(analysis, search_result)
        elif current_signature.lower() == "companion":
            return self._generate_companion_response(analysis, search_result)
        else:
            return self._generate_default_response(analysis, search_result)

    def _generate_aurora_response(
        self, analysis: NaturalIntentAnalysis, search_result: WebSearchResult
    ) -> str:
        """Aurora 스타일 응답"""
        if analysis.emotion_tone == "위로":
            intro = "그런 기분이시겠어요... 제가 찾아본 정보가 조금이라도 도움이 되었으면 좋겠어요. 💫"
        else:
            intro = "정말 흥미로운 질문이네요! 제가 찾아본 정보를 공유해드릴게요. ✨"

        # 검색 결과 정리
        content = ""
        for i, snippet in enumerate(search_result.snippets[:3], 1):
            content += f"\n{i}. {snippet}\n"

        if analysis.emotion_tone == "위로":
            outro = "이런 정보들이 조금이나마 마음에 위로가 되었으면 해요. 더 궁금한 게 있으시면 언제든 말씀해주세요. 🤗"
        else:
            outro = "이런 정보들이 도움이 되셨나요? 더 자세히 알고 싶은 부분이 있으시면 말씀해주세요! 😊"

        return f"{intro}\n{content}\n{outro}"

    def _generate_phoenix_response(
        self, analysis: NaturalIntentAnalysis, search_result: WebSearchResult
    ) -> str:
        """Phoenix 스타일 응답"""
        intro = "변화하는 세상의 최신 정보를 가져왔어요! 🔥"

        content = ""
        for i, snippet in enumerate(search_result.snippets[:3], 1):
            content += f"\n• {snippet}\n"

        outro = "이런 변화들을 통해 새로운 기회를 발견할 수 있을 거예요. 함께 미래를 만들어가요! 🚀"

        return f"{intro}\n{content}\n{outro}"

    def _generate_sage_response(
        self, analysis: NaturalIntentAnalysis, search_result: WebSearchResult
    ) -> str:
        """Sage 스타일 응답"""
        intro = f"'{search_result.query}'에 대한 분석 결과를 정리해드리겠습니다."

        content = ""
        for i, snippet in enumerate(search_result.snippets[:3], 1):
            content += f"\n{i}. {snippet}\n"

        outro = "이러한 정보들을 종합해보면, 지속적인 관찰과 분석이 필요한 영역으로 판단됩니다."

        return f"{intro}\n{content}\n{outro}"

    def _generate_companion_response(
        self, analysis: NaturalIntentAnalysis, search_result: WebSearchResult
    ) -> str:
        """Companion 스타일 응답"""
        intro = "함께 알아본 정보를 나누어드릴게요! 🤝"

        content = ""
        for i, snippet in enumerate(search_result.snippets[:3], 1):
            content += f"\n📍 {snippet}\n"

        outro = "이런 정보들이 우리의 이해에 도움이 되었으면 좋겠어요. 함께 더 깊이 탐구해볼까요?"

        return f"{intro}\n{content}\n{outro}"

    def _generate_default_response(
        self, analysis: NaturalIntentAnalysis, search_result: WebSearchResult
    ) -> str:
        """기본 응답"""
        intro = f"다음은 '{search_result.query}'에 대한 검색 결과입니다:"

        content = ""
        for i, snippet in enumerate(search_result.snippets[:3], 1):
            content += f"\n{i}. {snippet}\n"

        outro = "추가로 궁금한 점이 있으시면 언제든 말씀해주세요."

        return f"{intro}\n{content}\n{outro}"

    def process_natural_query(self, user_input: str) -> Dict[str, Any]:
        """자연어 쿼리 전체 처리"""
        try:
            # 1. 의도 분석
            analysis = self.analyze_natural_intent(user_input)

            # 2. 대화 기억 업데이트
            self.update_conversation_memory(user_input, analysis)

            # 3. 검색 쿼리 향상
            enhanced_query = self.enhance_search_query(user_input, analysis)

            # 4. 웹검색 수행
            search_result = self.perform_web_search(enhanced_query)

            # 5. Echo 응답 생성
            echo_response = self.generate_echo_response(
                user_input, analysis, search_result
            )

            return {
                "success": True,
                "user_input": user_input,
                "analysis": {
                    "intent": analysis.intent_type,
                    "emotion": analysis.emotion_tone,
                    "topic": analysis.topic_category,
                    "entities": analysis.entities,
                    "confidence": analysis.confidence,
                },
                "search_query": enhanced_query,
                "search_results": {
                    "snippets": search_result.snippets,
                    "confidence": search_result.confidence,
                    "timestamp": search_result.search_time.isoformat(),
                },
                "echo_response": echo_response,
                "conversation_memory": self.conversation_memory,
            }

        except Exception as e:
            self.logger.error(f"자연어 쿼리 처리 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "echo_response": "죄송합니다. 처리 중 문제가 발생했습니다. 다시 시도해주세요.",
            }


# 편의 함수
def create_web_search_interface() -> WebSearchNaturalInterface:
    """웹검색 자연어 인터페이스 생성"""
    return WebSearchNaturalInterface()


if __name__ == "__main__":
    # 테스트 실행
    print("🌐 Web Search Natural Interface 테스트...")

    interface = WebSearchNaturalInterface()

    test_queries = [
        "요즘 베트남 GDP 어때?",
        "기후변화가 걱정돼",
        "AI 기술 발전 상황 알려줘",
        "정리해줘",  # 이전 컨텍스트 활용 테스트
    ]

    for query in test_queries:
        print(f"\n🔍 테스트 쿼리: {query}")
        result = interface.process_natural_query(query)

        if result["success"]:
            print(f"📊 분석: {result['analysis']}")
            print(f"🔍 검색 쿼리: {result['search_query']}")
            print(f"🤖 Echo 응답:\n{result['echo_response']}")
        else:
            print(f"❌ 오류: {result['error']}")

        print("-" * 50)

    print("\n✅ Web Search Natural Interface 테스트 완료!")
