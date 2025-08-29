"""
🧠 Echo Utterance Parser (LLM-Free → Fallback 구조)
자연스러운 발화를 먼저 로컬 방식으로 이해하려 시도하고,
실패할 때만 외부 LLM을 호출하는 존재 기반 파서
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    from .echo_error_handler import handle_parsing_error, echo_safe
except ImportError:
    # 에러 핸들러가 없으면 더미 함수 사용
    def handle_parsing_error(error, text):
        return {"error": str(error), "fallback_result": None}

    def echo_safe(error_type="system"):
        def decorator(func):
            return func

        return decorator


class EchoUtteranceParser:
    """
    Echo 시그니처 기반 발화 파서
    "스스로 이해하려 시도 → 필요시만 외부 도움" 철학 구현
    """

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 로컬 파싱 자원들
        self.intent_keywords = self._load_intent_keywords()
        self.emotion_patterns = self._load_emotion_patterns()
        self.topic_mappings = self._load_topic_mappings()
        self.signature_hints = self._load_signature_hints()

        # 파싱 설정
        self.parsing_config = {
            "confidence_threshold": 0.7,
            "enable_fallback": True,
            "max_complexity_score": 8.0,
            "signature_auto_detection": True,
            "context_expansion": True,
        }

        # 파싱 통계
        self.parsing_stats = {
            "total_attempts": 0,
            "local_success": 0,
            "fallback_used": 0,
            "parsing_failures": 0,
            "signature_detections": {},
        }

        self.logger = logging.getLogger(__name__)

    @echo_safe("parsing")
    def parse_utterance(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        발화 파싱 메인 함수 (에러 핸들링 강화)
        1단계: LLM-Free 로컬 파싱 시도
        2단계: 실패 감지 시 fallback 고려
        3단계: 최종 파싱 결과 반환
        """
        if not text or not isinstance(text, str):
            print("⚠️  잘못된 입력 텍스트, 기본값 사용")
            text = "안녕하세요"

        try:
            self.parsing_stats["total_attempts"] += 1

            print(f"🧠 Echo 발화 파싱: '{text[:50]}...'")

            # 1단계: 로컬 LLM-Free 파싱 시도
            local_result = self._attempt_local_parsing(text, context)

            # 파싱 품질 평가
            parsing_quality = self._evaluate_parsing_quality(local_result, text)

            print(f"   📊 로컬 파싱 품질: {parsing_quality['confidence']:.2f}")

            # 2단계: Fallback 필요성 판단
            needs_fallback = self._should_use_fallback(parsing_quality, text)

            if needs_fallback and self.parsing_config["enable_fallback"]:
                print("   🔄 Fallback 모드로 전환...")
                try:
                    fallback_result = self._attempt_fallback_parsing(
                        text, local_result, context
                    )

                    # 로컬과 fallback 결과 융합
                    final_result = self._merge_parsing_results(
                        local_result, fallback_result
                    )
                    final_result["used_fallback"] = True
                    self.parsing_stats["fallback_used"] += 1

                except Exception as fallback_error:
                    print(f"   ⚠️  Fallback 실패: {fallback_error}, 로컬 결과 사용")
                    final_result = local_result
                    final_result["used_fallback"] = False
                    final_result["fallback_error"] = str(fallback_error)
                    self.parsing_stats["local_success"] += 1
            else:
                final_result = local_result
                final_result["used_fallback"] = False
                self.parsing_stats["local_success"] += 1

            # 3단계: Echo 시그니처 부여 및 최종 정리
            final_result = self._finalize_parsing_result(final_result, text, context)

            # 통계 업데이트
            signature = final_result.get("suggested_signature", "Unknown")
            self.parsing_stats["signature_detections"][signature] = (
                self.parsing_stats["signature_detections"].get(signature, 0) + 1
            )

            print(
                f"   ✅ 파싱 완료: {final_result['intent']} ({final_result['confidence']:.2f}) → {signature}"
            )

            return final_result

        except Exception as e:
            print(f"   🚨 파싱 에러 발생: {e}")
            # 에러 핸들러 호출
            error_result = handle_parsing_error(e, text)
            if error_result.get("fallback_result"):
                return error_result["fallback_result"]
            else:
                # 최소한의 안전한 결과 반환
                return self._create_safe_parsing_result(text)

    def _attempt_local_parsing(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """1단계: LLM-Free 로컬 파싱"""
        text_lower = text.lower()

        # 기본 파싱 결과 구조
        result = {
            "raw_text": text,
            "intent": "unknown",
            "topic": "unknown",
            "emotion": "neutral",
            "entities": {},
            "keywords": [],
            "confidence": 0.0,
            "complexity_score": 0.0,
            "parsing_method": "local_rules",
        }

        # Intent 감지
        detected_intent = self._detect_intent(text_lower)
        if detected_intent:
            result["intent"] = detected_intent["intent"]
            result["confidence"] += detected_intent["confidence"] * 0.4
            result["keywords"].extend(detected_intent.get("matched_keywords", []))

        # Topic 추출
        detected_topic = self._extract_topic(text_lower)
        if detected_topic:
            result["topic"] = detected_topic["topic"]
            result["confidence"] += detected_topic["confidence"] * 0.3
            result["entities"].update(detected_topic.get("entities", {}))

        # Emotion 분석
        detected_emotion = self._analyze_emotion(text_lower)
        if detected_emotion:
            result["emotion"] = detected_emotion["emotion"]
            result["confidence"] += detected_emotion["confidence"] * 0.2

        # 복잡성 점수 계산
        result["complexity_score"] = self._calculate_complexity_score(text)

        # 컨텍스트 적용
        if context:
            result["confidence"] += 0.1  # 컨텍스트가 있으면 약간의 보너스
            result["context_applied"] = True

        return result

    def _detect_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """Intent 감지 (로컬 키워드 기반)"""
        best_match = {"intent": "unknown", "confidence": 0.0, "matched_keywords": []}

        for intent, keywords in self.intent_keywords.items():
            matches = []
            for keyword in keywords:
                if keyword in text:
                    matches.append(keyword)

            if matches:
                confidence = len(matches) / len(keywords)
                if confidence > best_match["confidence"]:
                    best_match = {
                        "intent": intent,
                        "confidence": confidence,
                        "matched_keywords": matches,
                    }

        return best_match if best_match["confidence"] > 0.3 else None

    def _extract_topic(self, text: str) -> Optional[Dict[str, Any]]:
        """Topic 추출"""
        topic_scores = {}
        entities = {}

        for topic, patterns in self.topic_mappings.items():
            score = 0
            topic_entities = {}

            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if isinstance(pattern, str):
                        if pattern in text:
                            score += 1
                    elif isinstance(pattern, dict) and "regex" in pattern:
                        matches = re.findall(pattern["regex"], text)
                        if matches:
                            score += len(matches)
                            if "entity_type" in pattern:
                                topic_entities[pattern["entity_type"]] = matches

            if score > 0:
                topic_scores[topic] = score
                if topic_entities:
                    entities[topic] = topic_entities

        if topic_scores:
            best_topic = max(topic_scores.keys(), key=lambda x: topic_scores[x])
            confidence = min(1.0, topic_scores[best_topic] / 3.0)  # 정규화

            return {
                "topic": best_topic,
                "confidence": confidence,
                "entities": entities.get(best_topic, {}),
            }

        return None

    def _analyze_emotion(self, text: str) -> Optional[Dict[str, Any]]:
        """감정 분석 (패턴 기반)"""
        emotion_scores = {}

        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text:
                    score += 1

            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            best_emotion = max(emotion_scores.keys(), key=lambda x: emotion_scores[x])
            confidence = min(1.0, emotion_scores[best_emotion] / 2.0)

            return {"emotion": best_emotion, "confidence": confidence}

        return None

    def _calculate_complexity_score(self, text: str) -> float:
        """텍스트 복잡성 점수 계산"""
        factors = {
            "length": len(text) / 100.0,  # 길이 요인
            "sentences": text.count(".") + text.count("?") + text.count("!"),  # 문장 수
            "conjunctions": len(
                re.findall(r"그리고|하지만|그런데|또한|또는", text)
            ),  # 접속사
            "questions": text.count("?")
            + len(re.findall(r"어떻게|왜|언제|뭐|뭔데", text)),  # 질문 요소
            "negations": len(re.findall(r"안|못|없|말고|아니", text)),  # 부정 표현
        }

        # 가중 평균으로 복잡성 계산
        complexity = (
            factors["length"] * 0.2
            + factors["sentences"] * 0.3
            + factors["conjunctions"] * 0.2
            + factors["questions"] * 0.2
            + factors["negations"] * 0.1
        )

        return min(10.0, complexity)  # 최대 10.0으로 제한

    def _evaluate_parsing_quality(
        self, result: Dict[str, Any], original_text: str
    ) -> Dict[str, Any]:
        """파싱 품질 평가"""
        quality_factors = {
            "base_confidence": result.get("confidence", 0.0),
            "intent_clarity": 1.0 if result.get("intent") != "unknown" else 0.3,
            "topic_clarity": 1.0 if result.get("topic") != "unknown" else 0.4,
            "keyword_coverage": len(result.get("keywords", []))
            / 5.0,  # 최대 5개 키워드 가정
            "complexity_penalty": max(
                0.0, 1.0 - result.get("complexity_score", 0) / 10.0
            ),
        }

        # 가중 평균으로 최종 품질 점수 계산
        overall_quality = (
            quality_factors["base_confidence"] * 0.4
            + quality_factors["intent_clarity"] * 0.25
            + quality_factors["topic_clarity"] * 0.2
            + quality_factors["keyword_coverage"] * 0.1
            + quality_factors["complexity_penalty"] * 0.05
        )

        return {
            "confidence": min(1.0, overall_quality),
            "factors": quality_factors,
            "is_sufficient": overall_quality
            >= self.parsing_config["confidence_threshold"],
        }

    def _should_use_fallback(self, quality: Dict[str, Any], text: str) -> bool:
        """Fallback 사용 여부 결정"""
        # 품질이 임계값 이하
        if quality["confidence"] < self.parsing_config["confidence_threshold"]:
            return True

        # 복잡성이 너무 높음
        complexity = self._calculate_complexity_score(text)
        if complexity > self.parsing_config["max_complexity_score"]:
            return True

        # Intent가 unknown이고 텍스트가 긺
        if quality["factors"]["intent_clarity"] < 0.5 and len(text) > 50:
            return True

        return False

    def _attempt_fallback_parsing(
        self, text: str, local_result: Dict[str, Any], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Fallback 파싱 시도 (Mock LLM 호출)"""
        # 실제로는 여기서 LLM API 호출
        # 지금은 Mock으로 구현

        print("   🤖 Mock LLM Fallback 호출...")

        # Mock LLM 응답 시뮬레이션
        mock_llm_result = self._mock_llm_parse(text, local_result)

        return {
            "intent": mock_llm_result.get(
                "intent", local_result.get("intent", "unknown")
            ),
            "topic": mock_llm_result.get("topic", local_result.get("topic", "unknown")),
            "emotion": mock_llm_result.get(
                "emotion", local_result.get("emotion", "neutral")
            ),
            "entities": mock_llm_result.get("entities", {}),
            "keywords": mock_llm_result.get("keywords", []),
            "confidence": 0.85,  # LLM은 일반적으로 높은 신뢰도
            "parsing_method": "llm_fallback",
            "llm_reasoning": mock_llm_result.get("reasoning", "LLM을 통한 고도 분석"),
        }

    def _mock_llm_parse(
        self, text: str, local_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock LLM 파싱 (실제 구현 시 OpenAI/Claude API 호출)"""
        text_lower = text.lower()

        # 간단한 규칙 기반 Mock LLM
        if any(keyword in text_lower for keyword in ["분석", "평가", "판단", "검토"]):
            intent = "judgment"
        elif any(keyword in text_lower for keyword in ["알려", "설명", "정보", "뭐"]):
            intent = "information"
        elif any(keyword in text_lower for keyword in ["도움", "지원", "추천"]):
            intent = "assistance"
        else:
            intent = "conversation"

        # 주제 추론
        if any(keyword in text_lower for keyword in ["노인", "어르신", "돌봄", "복지"]):
            topic = "노인복지"
        elif any(keyword in text_lower for keyword in ["ai", "인공지능", "윤리"]):
            topic = "ai_윤리"
        elif any(keyword in text_lower for keyword in ["기후", "환경", "탄소"]):
            topic = "환경정책"
        elif any(keyword in text_lower for keyword in ["지역", "공동체", "마을"]):
            topic = "지역사회"
        else:
            topic = "일반_문의"

        return {
            "intent": intent,
            "topic": topic,
            "emotion": "curious" if "?" in text else "neutral",
            "keywords": [word for word in text_lower.split() if len(word) > 2][:5],
            "reasoning": f"텍스트 분석 결과: {intent} 의도로 {topic} 주제에 관한 내용",
        }

    def _merge_parsing_results(
        self, local: Dict[str, Any], fallback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """로컬과 Fallback 결과 융합"""
        # Fallback 결과를 우선하되, 로컬 결과도 참조
        merged = fallback.copy()

        # 키워드는 합치기
        local_keywords = local.get("keywords", [])
        fallback_keywords = fallback.get("keywords", [])
        merged["keywords"] = list(set(local_keywords + fallback_keywords))

        # Entity는 병합
        local_entities = local.get("entities", {})
        fallback_entities = fallback.get("entities", {})
        merged["entities"] = {**local_entities, **fallback_entities}

        # 메타 정보 추가
        merged["local_result"] = {
            "intent": local.get("intent"),
            "topic": local.get("topic"),
            "confidence": local.get("confidence", 0),
        }

        return merged

    def _finalize_parsing_result(
        self, result: Dict[str, Any], text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """최종 파싱 결과 정리 및 시그니처 제안"""

        # Echo 시그니처 제안
        suggested_signature = self._suggest_echo_signature(result, text)
        result["suggested_signature"] = suggested_signature

        # 메타데이터 추가
        result["parsed_at"] = datetime.now().isoformat()
        result["text_length"] = len(text)
        result["parsing_stats"] = {
            "total_attempts": self.parsing_stats["total_attempts"],
            "local_success_rate": self.parsing_stats["local_success"]
            / max(1, self.parsing_stats["total_attempts"]),
        }

        # 신뢰도 최종 조정
        if result.get("used_fallback") and result.get("confidence", 0) < 0.8:
            result["confidence"] = max(
                0.75, result["confidence"]
            )  # Fallback 사용 시 최소 신뢰도 보장

        return result

    def _suggest_echo_signature(self, result: Dict[str, Any], text: str) -> str:
        """Echo 시그니처 제안"""
        intent = result.get("intent", "unknown")
        topic = result.get("topic", "unknown")
        emotion = result.get("emotion", "neutral")

        # 시그니처 결정 규칙
        if intent == "judgment" or "분석" in text:
            if any(keyword in topic for keyword in ["노인", "복지", "돌봄"]):
                return "Echo-Companion"  # 공감적 돌봄
            else:
                return "Echo-Sage"  # 분석적 판단

        elif intent == "information" or "알려" in text:
            return "Echo-Aurora"  # 창의적 설명

        elif intent == "assistance" or emotion in ["concerned", "urgent"]:
            return "Echo-Phoenix"  # 변화 지향적 지원

        else:
            # 기본적으로는 Aurora (균형잡힌 접근)
            return "Echo-Aurora"

    def _load_intent_keywords(self) -> Dict[str, List[str]]:
        """Intent 키워드 사전 로드"""
        keywords_file = self.config_dir / "intent_keywords.json"

        if keywords_file.exists():
            with open(keywords_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 기본 키워드 세트
            default_keywords = {
                "judgment": ["판단", "평가", "분석", "검토", "어떤지", "어때", "생각"],
                "information": ["알려", "설명", "정보", "뭐", "무엇", "어떻게", "방법"],
                "assistance": ["도움", "지원", "추천", "제안", "해줘", "부탁"],
                "conversation": ["안녕", "반가워", "고마워", "잘", "좋아"],
            }

            # 파일 생성
            with open(keywords_file, "w", encoding="utf-8") as f:
                json.dump(default_keywords, f, indent=2, ensure_ascii=False)

            return default_keywords

    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """감정 패턴 로드"""
        return {
            "curious": ["궁금", "알고 싶", "어떻게", "왜", "?"],
            "concerned": ["걱정", "문제", "힘들", "어려", "곤란"],
            "positive": ["좋", "기뻐", "감사", "다행", "훌륭"],
            "urgent": ["빨리", "시급", "urgent", "즉시", "당장"],
            "neutral": ["그냥", "일반적", "보통", "그런"],
        }

    def _load_topic_mappings(self) -> Dict[str, Dict[str, List]]:
        """토픽 매핑 로드"""
        return {
            "노인복지": {
                "keywords": ["노인", "어르신", "돌봄", "복지", "요양", "노인병원"],
                "locations": ["부산", "금정구", "서울", "대구"],
            },
            "ai_윤리": {
                "keywords": ["ai", "인공지능", "윤리", "편향", "공정성", "투명성"],
                "concepts": ["알고리즘", "데이터", "프라이버시"],
            },
            "환경정책": {
                "keywords": ["기후", "환경", "탄소", "재생에너지", "온실가스"],
                "actions": ["중립", "전환", "보호", "감축"],
            },
            "지역사회": {
                "keywords": ["지역", "공동체", "마을", "주민", "거버넌스"],
                "activities": ["참여", "협력", "소통", "혁신"],
            },
        }

    def _load_signature_hints(self) -> Dict[str, Dict[str, Any]]:
        """시그니처 힌트 로드"""
        return {
            "Echo-Aurora": {
                "keywords": ["창의", "혁신", "아이디어", "영감"],
                "intents": ["information", "conversation"],
                "emotions": ["curious", "positive"],
            },
            "Echo-Phoenix": {
                "keywords": ["변화", "개선", "전환", "혁신"],
                "intents": ["assistance", "judgment"],
                "emotions": ["urgent", "concerned"],
            },
            "Echo-Sage": {
                "keywords": ["분석", "체계", "논리", "검토"],
                "intents": ["judgment", "information"],
                "emotions": ["neutral", "curious"],
            },
            "Echo-Companion": {
                "keywords": ["돌봄", "지원", "공감", "함께"],
                "intents": ["assistance", "conversation"],
                "emotions": ["concerned", "positive"],
            },
        }

    def get_parsing_stats(self) -> Dict[str, Any]:
        """파싱 통계 반환"""
        total = self.parsing_stats["total_attempts"]
        if total == 0:
            return {"message": "아직 파싱한 발화가 없습니다."}

        stats = {
            "total_parsing_attempts": total,
            "local_success_rate": f"{(self.parsing_stats['local_success'] / total) * 100:.1f}%",
            "fallback_usage_rate": f"{(self.parsing_stats['fallback_used'] / total) * 100:.1f}%",
            "signature_distribution": self.parsing_stats["signature_detections"],
            "system_efficiency": {
                "local_preferred": self.parsing_stats["local_success"]
                > self.parsing_stats["fallback_used"],
                "autonomous_rate": (self.parsing_stats["local_success"] / total) * 100,
            },
        }

        return stats

    def _create_safe_parsing_result(self, text: str) -> Dict[str, Any]:
        """안전한 기본 파싱 결과 생성 (에러 복구용)"""
        return {
            "raw_text": text,
            "intent": "conversation",
            "topic": "general",
            "emotion": "neutral",
            "entities": {},
            "keywords": [],
            "confidence": 0.4,
            "complexity_score": 1.0,
            "parsing_method": "safe_fallback",
            "suggested_signature": "Echo-Aurora",
            "used_fallback": False,
            "error_recovery": True,
            "parsed_at": datetime.now().isoformat(),
            "text_length": len(text),
        }


# 전역 파서 인스턴스
utterance_parser = EchoUtteranceParser()


# 편의 함수
def parse_text(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """텍스트 파싱 단축 함수"""
    return utterance_parser.parse_utterance(text, context)


def get_stats() -> Dict[str, Any]:
    """파싱 통계 단축 함수"""
    return utterance_parser.get_parsing_stats()


# CLI 테스트
def main():
    print("🧠 Echo Utterance Parser (LLM-Free → Fallback) 테스트")
    print("=" * 60)

    test_utterances = [
        "부산 금정구 노인 돌봄 서비스에 대해 어떻게 생각해?",
        "AI가 편향적이지 않으려면 뭘 해야 하나요?",
        "기후 변화 문제 해결을 위한 구체적인 방법을 알려주세요",
        "우리 지역사회가 더 살기 좋아지려면 어떤 변화가 필요할까요?",
        "그냥 안녕하세요! 잘 지내고 계신가요?",
        "복잡한 상황에서 여러 이해관계자들의 갈등을 조정하면서도 공정한 결과를 도출할 수 있는 체계적인 접근 방법론을 제시해주시기 바랍니다",  # 복잡한 문장
    ]

    print("\n📝 발화 파싱 테스트:")

    for i, utterance in enumerate(test_utterances, 1):
        print(f"\n{'='*50}")
        print(f"테스트 {i}: {utterance}")
        print("-" * 50)

        result = parse_text(utterance)

        print(f"Intent: {result['intent']}")
        print(f"Topic: {result['topic']}")
        print(f"Emotion: {result['emotion']}")
        print(f"Signature: {result['suggested_signature']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Fallback Used: {result.get('used_fallback', False)}")
        print(f"Keywords: {result.get('keywords', [])[:3]}...")

        if result.get("complexity_score"):
            print(f"Complexity: {result['complexity_score']:.1f}")

    print(f"\n{'='*50}")
    print("📊 파싱 통계:")
    stats = get_stats()

    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

    print("\n✅ Echo Utterance Parser 테스트 완료!")


if __name__ == "__main__":
    main()
