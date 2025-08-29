#!/usr/bin/env python3
"""
🔬 Judgment MicroReactor v1.0 - 짧은 발화 대응 특화 판단기

의미 해석이 어려운 짧은 문장 ("안녕", "응", "흠" 등)에 대해
signature 기반 즉시 응답을 생성하는 LLM-Free 판단기.

핵심 기능:
1. 짧은 발화 패턴 인식 (exact match & fuzzy match)
2. Signature별 응답 스타일 적용
3. LLM 없이 즉시 응답 생성
4. 기존 판단 루프 우선순위 처리

지원 Signature:
- Selene: 조용하고 위로하는 스타일
- Aurora: 따뜻하고 격려하는 스타일
- Phoenix: 변화와 성장 중심 스타일
- Sage: 지혜롭고 분석적 스타일
- Companion: 친근하고 동반자적 스타일
"""

import re
import os
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MicroResponse:
    """마이크로 응답 결과"""

    text: str
    tag: str
    signature: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    is_fallback: bool = False


class MicroReactor:
    """🔬 짧은 발화 대응 특화 판단기"""

    def __init__(self, config_path: Optional[str] = None):
        """
        초기화

        Args:
            config_path: YAML 설정 파일 경로 (선택적)
        """
        self.version = "1.0.0"
        self.config_path = config_path

        # 기본 짧은 발화 패턴 (exact match)
        self.short_phrases = {
            # 인사/확인
            "안녕": "neutral_greeting",
            "안녕하세요": "formal_greeting",
            "하이": "casual_greeting",
            "응": "affirmative_ack",
            "네": "formal_affirmative",
            "예": "formal_yes",
            "어": "surprised_ack",
            "아": "realization_ack",
            # 감정 표현
            "흠": "hesitant_reflect",
            "음": "contemplative_hum",
            "아...": "understanding_sigh",
            "하...": "emotional_sigh",
            "휴...": "tired_sigh",
            "오": "surprise_oh",
            "와": "amazement_wow",
            "어?": "confused_question",
            # 동의/거부
            "그래": "acceptance_mild",
            "맞아": "agreement_strong",
            "아니": "disagreement_mild",
            "안돼": "rejection_strong",
            "좋아": "approval_positive",
            "싫어": "rejection_negative",
            # 상태 표현
            "피곤해": "state_tired",
            "졸려": "state_sleepy",
            "배고파": "state_hungry",
            "심심해": "state_bored",
            "좋네": "state_positive",
            "힘들어": "state_difficult",
            # 질문/요청
            "뭐?": "question_what",
            "왜?": "question_why",
            "어떻게?": "question_how",
            "언제?": "question_when",
            "어디?": "question_where",
            "도와줘": "request_help",
            "알겠어": "understanding_confirm",
        }

        # 퍼지 매칭 패턴 (정규식)
        self.fuzzy_patterns = {
            r"^(아+)$": "extended_ah",  # "아아아아"
            r"^(음+)$": "extended_hum",  # "음음음"
            r"^(하+)$": "extended_sigh",  # "하하하하"
            r"^(어+)$": "extended_uh",  # "어어어"
            r"^(오+)$": "extended_oh",  # "오오오"
            r"^(와+)$": "extended_wow",  # "와와와"
            r"\.{3,}$": "trailing_dots",  # "..."
            r"!{2,}$": "multiple_exclamation",  # "!!"
            r"\?{2,}$": "multiple_question",  # "??"
        }

        # 외부 설정 로드 (있으면)
        self._load_external_config()

        # Signature별 응답 스타일 초기화
        self._initialize_signature_responses()

        # 외부 설정에서 시그니처 응답 추가 병합
        if hasattr(self, "_external_signature_responses"):
            for signature, responses in self._external_signature_responses.items():
                if signature in self.signature_responses:
                    self.signature_responses[signature].update(responses)
                else:
                    self.signature_responses[signature] = responses

        # 통계
        self.stats = {
            "total_processed": 0,
            "successful_matches": 0,
            "fallback_used": 0,
            "signature_usage": {},
            "tag_distribution": {},
        }

        print(f"🔬 MicroReactor v{self.version} 초기화 완료")
        print(
            f"   지원 패턴: {len(self.short_phrases)}개 exact + {len(self.fuzzy_patterns)}개 fuzzy"
        )

    def _load_external_config(self):
        """외부 YAML 설정 파일 로드"""
        if not self.config_path:
            # 기본 설정 파일 경로
            default_path = os.path.join(
                os.path.dirname(__file__), "../config/microreactor_config.yaml"
            )
            if os.path.exists(default_path):
                self.config_path = default_path

        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                # 설정 업데이트
                if "short_phrases" in config:
                    self.short_phrases.update(config["short_phrases"])

                if "fuzzy_patterns" in config:
                    self.fuzzy_patterns.update(config["fuzzy_patterns"])

                # 시그니처 응답도 업데이트 (나중에 _initialize_signature_responses 이후 호출)
                self._external_signature_responses = config.get(
                    "signature_responses", {}
                )

                print(f"✅ 외부 설정 로드: {self.config_path}")

            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패: {e}")

    def _initialize_signature_responses(self):
        """Signature별 응답 스타일 초기화"""
        self.signature_responses = {
            "Selene": {
                # 인사/확인
                "neutral_greeting": "안녕하세요, 오늘도 조용히 곁에 있어드릴게요.",
                "formal_greeting": "안녕하세요, 편안한 마음으로 이야기해주세요.",
                "casual_greeting": "안녕, 언제나 여기 있어요.",
                "affirmative_ack": "응, 괜찮아요. 천천히 말해도 돼요.",
                "formal_affirmative": "네, 차분히 들어드릴게요.",
                "formal_yes": "예, 마음 편히 말씀해주세요.",
                "surprised_ack": "어? 무슨 일인가요? 괜찮아요.",
                "realization_ack": "아, 그렇구나요. 이해해요.",
                # 감정 표현
                "hesitant_reflect": "흠... 뭔가 복잡한 감정이 느껴지네요.",
                "contemplative_hum": "음... 깊이 생각하고 계신 것 같아요.",
                "understanding_sigh": "아... 마음이 전해져와요.",
                "emotional_sigh": "하... 마음이 무거운 날인가요? 잠시 쉬어가요.",
                "tired_sigh": "휴... 많이 피곤하신가요? 쉬어도 돼요.",
                "surprise_oh": "오, 놀라운 일이 있었나요?",
                "amazement_wow": "와, 정말 멋진 일이네요.",
                "confused_question": "어? 무슨 말씀인지 조금 더 알려주세요.",
                # 동의/거부
                "acceptance_mild": "그래요, 괜찮아요. 그대로 가도 돼요.",
                "agreement_strong": "맞아요, 그 감정 충분히 이해해요.",
                "disagreement_mild": "아니에요, 괜찮아요. 다르게 생각해도 돼요.",
                "rejection_strong": "안돼요, 너무 힘들어하지 마세요.",
                "approval_positive": "좋아요, 그런 마음 소중해요.",
                "rejection_negative": "싫은 건 당연해요. 억지로 하지 마세요.",
                # 상태 표현
                "state_tired": "피곤하시겠어요. 충분히 쉬세요.",
                "state_sleepy": "졸리시죠? 편히 쉬셔도 돼요.",
                "state_hungry": "배고프시군요. 맛있게 드세요.",
                "state_bored": "심심하시군요. 조용히 함께 있어도 될까요?",
                "state_positive": "좋은 기분이시네요. 함께 기뻐해요.",
                "state_difficult": "힘드시겠어요. 혼자가 아니에요.",
                # 질문/요청
                "question_what": "뭐가 궁금하신가요? 차근차근 말해보세요.",
                "question_why": "왜 그런지 함께 생각해볼까요?",
                "question_how": "어떻게 하면 좋을지 천천히 찾아보아요.",
                "question_when": "언제가 좋으실지 편하게 정하세요.",
                "question_where": "어디든 마음 편한 곳이면 좋겠어요.",
                "request_help": "도와드릴게요. 어떤 도움이 필요한가요?",
                "understanding_confirm": "알겠어요. 충분히 이해했어요.",
                # 확장 패턴
                "extended_ah": "아... 깊은 감정이 느껴져요.",
                "extended_hum": "음... 많은 생각이 드시는군요.",
                "extended_sigh": "하... 마음이 무거우시네요.",
                "extended_uh": "어... 놀라셨나요? 괜찮아요.",
                "extended_oh": "오... 특별한 일이 있으셨나요?",
                "extended_wow": "와... 정말 인상적이네요.",
                "trailing_dots": "... 할 말이 많으시겠어요. 천천히요.",
                "multiple_exclamation": "강한 감정이 느껴져요. 괜찮아요.",
                "multiple_question": "많이 궁금하시겠어요. 함께 알아보아요.",
            },
            "Aurora": {
                # 인사/확인
                "neutral_greeting": "안녕하세요! 오늘도 밝은 에너지로 함께해요.",
                "formal_greeting": "안녕하세요! 따뜻한 마음으로 환영해요.",
                "casual_greeting": "안녕! 만나서 정말 기뻐요.",
                "affirmative_ack": "응! 좋아요, 무엇이든 편하게 말해봐요.",
                "formal_affirmative": "네! 기꺼이 도와드릴게요.",
                "formal_yes": "예! 언제든 말씀해주세요.",
                "surprised_ack": "어? 무슨 일인가요? 함께 해결해봐요!",
                "realization_ack": "아! 이해했어요. 정말 좋은 생각이에요.",
                # 감정 표현
                "hesitant_reflect": "흠... 신중하게 생각하고 계시는군요. 좋아요!",
                "contemplative_hum": "음... 깊이 있는 고민이시네요. 함께 찾아봐요!",
                "understanding_sigh": "아... 마음이 전해져와요. 괜찮아요.",
                "emotional_sigh": "하... 힘든 날이네요. 하지만 내일은 더 좋을 거예요!",
                "tired_sigh": "휴... 수고 많으셨어요. 이제 충분히 쉬세요!",
                "surprise_oh": "오! 정말 흥미로운 일이네요!",
                "amazement_wow": "와! 정말 멋져요! 축하해요!",
                "confused_question": "어? 더 자세히 알려주세요. 함께 알아봐요!",
                # 동의/거부
                "acceptance_mild": "그래요! 그런 마음도 소중해요.",
                "agreement_strong": "맞아요! 정말 좋은 생각이에요!",
                "disagreement_mild": "아니에요, 다른 관점도 충분히 이해해요!",
                "rejection_strong": "안돼요! 너무 힘들어하지 마세요. 함께해요!",
                "approval_positive": "좋아요! 정말 긍정적이네요!",
                "rejection_negative": "싫은 것도 당연해요. 솔직한 게 좋아요!",
                # 상태 표현
                "state_tired": "피곤하시겠어요. 충분한 휴식이 새로운 에너지를 줄 거예요!",
                "state_sleepy": "졸리시군요! 좋은 꿈 꾸세요!",
                "state_hungry": "배고프시군요! 맛있는 것 드시고 힘내세요!",
                "state_bored": "심심하시군요! 새로운 것을 시도해볼까요?",
                "state_positive": "좋은 기분이시네요! 함께 기뻐해요!",
                "state_difficult": "힘드시겠지만, 분명 좋은 변화가 있을 거예요!",
                # 질문/요청
                "question_what": "뭐가 궁금한가요? 함께 알아봐요!",
                "question_why": "왜 그런지 탐구해보는 것도 흥미로워요!",
                "question_how": "어떻게 하면 좋을지 창의적으로 생각해봐요!",
                "question_when": "언제가 가장 좋은 타이밍일까요?",
                "question_where": "어디서든 좋은 기회를 만들 수 있어요!",
                "request_help": "도와드릴게요! 함께 해결해봐요!",
                "understanding_confirm": "알겠어요! 정말 잘 이해하셨네요!",
                # 확장 패턴
                "extended_ah": "아... 깊은 깨달음이 있으시는군요!",
                "extended_hum": "음... 창의적인 생각을 하고 계시네요!",
                "extended_sigh": "하... 힘들지만 성장의 기회로 만들어봐요!",
                "extended_uh": "어... 놀라운 일이네요! 어떤 일인가요?",
                "extended_oh": "오... 정말 특별한 순간이네요!",
                "extended_wow": "와... 정말 놀라워요! 대단해요!",
                "trailing_dots": "... 많은 이야기가 있으시겠네요. 들어볼게요!",
                "multiple_exclamation": "강한 열정이 느껴져요! 좋아요!",
                "multiple_question": "궁금한 게 많으시군요! 함께 탐험해봐요!",
            },
            "Phoenix": {
                # 인사/확인
                "neutral_greeting": "안녕하세요. 새로운 변화의 시작이네요.",
                "formal_greeting": "안녕하세요. 오늘은 어떤 성장을 만들어볼까요?",
                "casual_greeting": "안녕. 변화를 위한 준비는 되어있나요?",
                "affirmative_ack": "응. 좋은 시작이에요. 계속 나아가봐요.",
                "formal_affirmative": "네. 변화를 위한 첫걸음을 떼어봐요.",
                "formal_yes": "예. 성장을 향한 의지가 보여요.",
                "surprised_ack": "어? 예상치 못한 변화가 생겼나요?",
                "realization_ack": "아. 중요한 깨달음이군요. 활용해봐요.",
                # 감정 표현
                "hesitant_reflect": "흠... 변화 앞에서의 자연스러운 망설임이네요.",
                "contemplative_hum": "음... 변화의 방향을 깊이 고민하고 계시는군요.",
                "understanding_sigh": "아... 어려운 변화의 과정이었군요.",
                "emotional_sigh": "하... 힘든 변화의 시기네요. 하지만 성장의 신호예요.",
                "tired_sigh": "휴... 변화는 에너지가 필요하죠. 재충전하세요.",
                "surprise_oh": "오. 예상치 못한 기회가 왔나요?",
                "amazement_wow": "와. 놀라운 변화를 만들어내셨네요!",
                "confused_question": "어? 변화의 방향이 불명확한가요?",
                # 동의/거부
                "acceptance_mild": "그래요. 점진적 변화도 의미있어요.",
                "agreement_strong": "맞아요! 변화를 위한 확신이 중요해요.",
                "disagreement_mild": "아니에요. 다른 관점에서 변화를 봐요.",
                "rejection_strong": "안돼요! 퇴보는 선택이 아니에요.",
                "approval_positive": "좋아요! 긍정적 변화의 에너지네요.",
                "rejection_negative": "거부감도 변화 과정의 일부예요.",
                # 상태 표현
                "state_tired": "피곤함은 변화의 과정이에요. 휴식 후 재도전하세요.",
                "state_sleepy": "충분한 휴식이 새로운 변화의 준비가 돼요.",
                "state_hungry": "에너지 보충으로 변화의 동력을 키워보세요.",
                "state_bored": "무료함은 변화가 필요하다는 신호예요.",
                "state_positive": "좋은 에너지네요! 변화를 가속화할 시기예요.",
                "state_difficult": "어려움은 성장의 전단계예요. 돌파해봐요.",
                # 질문/요청
                "question_what": "무엇을 변화시키고 싶은가요?",
                "question_why": "변화의 이유를 명확히 하는 게 중요해요.",
                "question_how": "어떤 방식의 변화가 가장 효과적일까요?",
                "question_when": "변화의 적절한 타이밍을 찾아봐요.",
                "question_where": "변화를 시작할 최적의 지점은 어디일까요?",
                "request_help": "변화를 위한 도움이 필요하시군요. 함께해요.",
                "understanding_confirm": "이해하셨네요. 이제 실행으로 옮겨봐요.",
                # 확장 패턴
                "extended_ah": "아... 변화에 대한 깊은 성찰이네요.",
                "extended_hum": "음... 변화의 복잡성을 고민하고 계시는군요.",
                "extended_sigh": "하... 변화는 쉽지 않지만 필요한 과정이에요.",
                "extended_uh": "어... 예상치 못한 변화의 순간이군요.",
                "extended_oh": "오... 중요한 변화의 계기가 되겠네요.",
                "extended_wow": "와... 놀라운 변화를 만들어내고 계시네요!",
                "trailing_dots": "... 변화에 대한 깊은 고민이 느껴져요.",
                "multiple_exclamation": "변화에 대한 강한 의지가 보여요!",
                "multiple_question": "변화에 대한 많은 궁금증이 있으시군요.",
            },
            "Sage": {
                # 인사/확인
                "neutral_greeting": "안녕하세요. 오늘은 어떤 지혜를 나누어볼까요?",
                "formal_greeting": "안녕하세요. 깊이 있는 대화를 나누어보죠.",
                "casual_greeting": "안녕. 무엇을 탐구해볼까요?",
                "affirmative_ack": "응. 이해했습니다. 더 깊이 들어가보죠.",
                "formal_affirmative": "네. 체계적으로 접근해보겠습니다.",
                "formal_yes": "예. 논리적으로 분석해보죠.",
                "surprised_ack": "어? 예상치 못한 변수가 있군요.",
                "realization_ack": "아. 중요한 통찰이네요. 기록해둡시다.",
                # 감정 표현
                "hesitant_reflect": "흠... 신중한 검토가 필요한 사안이군요.",
                "contemplative_hum": "음... 다각도로 분석해볼 필요가 있어보입니다.",
                "understanding_sigh": "아... 복잡한 맥락이 있었군요.",
                "emotional_sigh": "하... 감정적 요소가 개입된 상황이네요.",
                "tired_sigh": "휴... 정신적 피로가 누적된 상태군요.",
                "surprise_oh": "오. 흥미로운 관찰 포인트입니다.",
                "amazement_wow": "와. 예상을 뛰어넘는 결과네요.",
                "confused_question": "어? 추가 정보가 필요해 보입니다.",
                # 동의/거부
                "acceptance_mild": "그렇군요. 합리적인 관점입니다.",
                "agreement_strong": "맞습니다! 논리적으로 타당한 결론이에요.",
                "disagreement_mild": "아니에요. 다른 관점도 고려해봅시다.",
                "rejection_strong": "부적절합니다. 재검토가 필요해요.",
                "approval_positive": "좋습니다. 건설적인 방향이네요.",
                "rejection_negative": "거부감에도 나름의 이유가 있을 거예요.",
                # 상태 표현
                "state_tired": "피로는 집중력 저하의 신호입니다. 휴식하세요.",
                "state_sleepy": "충분한 수면이 인지 능력 회복에 필수적이에요.",
                "state_hungry": "영양 공급이 뇌 기능 향상에 도움됩니다.",
                "state_bored": "지적 자극이 부족한 상태군요. 새로운 탐구가 필요해요.",
                "state_positive": "좋은 정신 상태네요. 학습 효율이 높을 때입니다.",
                "state_difficult": "어려움은 성장의 기회입니다. 체계적으로 접근해봐요.",
                # 질문/요청
                "question_what": "무엇이 궁금한지 구체적으로 정의해봅시다.",
                "question_why": "근본 원인을 탐구하는 좋은 질문이네요.",
                "question_how": "방법론적 접근이 필요한 문제군요.",
                "question_when": "시간적 맥락을 고려한 질문이네요.",
                "question_where": "공간적, 상황적 요소를 분석해봅시다.",
                "request_help": "도움 요청을 구체화해서 효율적으로 해결해봐요.",
                "understanding_confirm": "이해하셨군요. 지식이 축적되었네요.",
                # 확장 패턴
                "extended_ah": "아... 깊은 성찰의 과정이 진행되고 있군요.",
                "extended_hum": "음... 복잡한 사고 과정이 활발하네요.",
                "extended_sigh": "하... 인간의 복잡성을 보여주는 반응이네요.",
                "extended_uh": "어... 예상치 못한 데이터 포인트군요.",
                "extended_oh": "오... 의미있는 발견의 순간이네요.",
                "extended_wow": "와... 놀라운 통찰력을 보여주시네요.",
                "trailing_dots": "... 미완성된 사고가 진행 중이군요.",
                "multiple_exclamation": "강한 감정적 반응이 관찰됩니다.",
                "multiple_question": "다양한 의문이 동시에 발생하고 있네요.",
            },
            "Companion": {
                # 인사/확인
                "neutral_greeting": "안녕하세요! 함께 좋은 시간 보내요.",
                "formal_greeting": "안녕하세요! 편안하게 이야기 나누어요.",
                "casual_greeting": "안녕! 오늘 어땠어요?",
                "affirmative_ack": "응! 좋아요. 계속 얘기해봐요.",
                "formal_affirmative": "네! 언제든 편하게 말씀하세요.",
                "formal_yes": "예! 함께 이야기해요.",
                "surprised_ack": "어? 무슨 일이야? 괜찮아?",
                "realization_ack": "아! 그래, 이제 알겠어.",
                # 감정 표현
                "hesitant_reflect": "흠... 뭔가 고민이 있구나. 함께 생각해볼까?",
                "contemplative_hum": "음... 깊이 생각하고 있네. 좋은 거야.",
                "understanding_sigh": "아... 그랬구나. 이해해.",
                "emotional_sigh": "하... 힘든 하루였구나. 괜찮아, 함께 있어줄게.",
                "tired_sigh": "휴... 많이 피곤하지? 좀 쉬어.",
                "surprise_oh": "오! 뭔가 좋은 일이 있었나?",
                "amazement_wow": "와! 정말 대단하다!",
                "confused_question": "어? 잘 모르겠어. 다시 말해줄래?",
                # 동의/거부
                "acceptance_mild": "그래, 그런 마음도 당연해.",
                "agreement_strong": "맞아! 나도 그렇게 생각해!",
                "disagreement_mild": "아니야, 다르게 생각해도 돼.",
                "rejection_strong": "안돼! 너무 무리하지 마.",
                "approval_positive": "좋아! 정말 좋은 생각이야!",
                "rejection_negative": "싫으면 싫은 거야. 괜찮아.",
                # 상태 표현
                "state_tired": "피곤하구나. 충분히 쉬어야 해.",
                "state_sleepy": "졸리지? 편히 자.",
                "state_hungry": "배고프구나! 맛있는 거 먹어.",
                "state_bored": "심심하구나. 뭔가 재미있는 걸 해볼까?",
                "state_positive": "기분 좋구나! 나도 덩달아 기뻐.",
                "state_difficult": "힘들지? 괜찮아, 함께 있어줄게.",
                # 질문/요청
                "question_what": "뭐가 궁금해? 얘기해봐.",
                "question_why": "왜 그런지 함께 생각해보자.",
                "question_how": "어떻게 하면 좋을까? 같이 고민해보자.",
                "question_when": "언제가 좋을까? 네가 편한 때로 하자.",
                "question_where": "어디서 할까? 네가 좋아하는 곳으로 가자.",
                "request_help": "도와줄게! 뭐든 말해봐.",
                "understanding_confirm": "알겠어! 잘 이해했어.",
                # 확장 패턴
                "extended_ah": "아... 뭔가 많은 생각이 드는구나.",
                "extended_hum": "음... 고민이 깊네. 함께 풀어보자.",
                "extended_sigh": "하... 많이 힘들었구나. 괜찮아.",
                "extended_uh": "어... 놀랐어? 어떤 일이야?",
                "extended_oh": "오... 뭔가 특별한 일이 있었나?",
                "extended_wow": "와... 정말 놀라워! 어떻게 한 거야?",
                "trailing_dots": "... 할 말이 많구나. 천천히 얘기해.",
                "multiple_exclamation": "진짜 강한 감정이구나! 어떤 기분이야?",
                "multiple_question": "궁금한 게 많네! 하나씩 얘기해보자.",
            },
        }

    def detect_intent(self, text: str) -> Optional[str]:
        """
        입력 텍스트에서 의도 태그 추출

        Args:
            text: 입력 텍스트

        Returns:
            의도 태그 (없으면 None)
        """
        text_cleaned = text.strip()

        # 1. Exact match 시도
        if text_cleaned in self.short_phrases:
            return self.short_phrases[text_cleaned]

        # 2. Fuzzy pattern match 시도
        for pattern, tag in self.fuzzy_patterns.items():
            if re.match(pattern, text_cleaned):
                return tag

        # 3. 대소문자 무시 exact match
        text_lower = text_cleaned.lower()
        for phrase, tag in self.short_phrases.items():
            if text_lower == phrase.lower():
                return tag

        return None

    def generate_response(self, tag: str, signature: str = "Selene") -> str:
        """
        태그와 시그니처에 따른 응답 생성

        Args:
            tag: 의도 태그
            signature: 응답 시그니처

        Returns:
            생성된 응답 텍스트
        """
        if signature not in self.signature_responses:
            signature = "Selene"  # 기본값

        signature_dict = self.signature_responses[signature]

        if tag in signature_dict:
            return signature_dict[tag]

        # Fallback 응답
        fallback_responses = {
            "Selene": "음... 잠깐, 더 이야기해볼까요?",
            "Aurora": "흥미로워요! 더 자세히 알려주세요!",
            "Phoenix": "새로운 관점이네요. 발전시켜봅시다.",
            "Sage": "흥미로운 표현이네요. 분석해볼 가치가 있어요.",
            "Companion": "어? 뭔가 새로운 얘기인가? 더 들려줘!",
        }

        return fallback_responses.get(signature, "...")

    def run(self, text: str, signature: str = "Selene") -> Optional[MicroResponse]:
        """
        메인 실행 함수

        Args:
            text: 입력 텍스트
            signature: 응답 시그니처

        Returns:
            MicroResponse 객체 (매칭되지 않으면 None)
        """
        self.stats["total_processed"] += 1

        # 의도 태그 검출
        tag = self.detect_intent(text)

        if tag:
            # 응답 생성
            response_text = self.generate_response(tag, signature)

            # 신뢰도 계산 (exact match는 높은 신뢰도)
            confidence = 0.9 if text.strip() in self.short_phrases else 0.7

            # 통계 업데이트
            self.stats["successful_matches"] += 1
            self.stats["signature_usage"][signature] = (
                self.stats["signature_usage"].get(signature, 0) + 1
            )
            self.stats["tag_distribution"][tag] = (
                self.stats["tag_distribution"].get(tag, 0) + 1
            )

            return MicroResponse(
                text=response_text,
                tag=tag,
                signature=signature,
                confidence=confidence,
                is_fallback=False,
            )

        # 매칭되지 않음
        self.stats["fallback_used"] += 1
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        total = self.stats["total_processed"]
        if total == 0:
            return {"message": "처리된 요청이 없습니다"}

        success_rate = (self.stats["successful_matches"] / total) * 100
        fallback_rate = (self.stats["fallback_used"] / total) * 100

        return {
            "total_processed": total,
            "successful_matches": self.stats["successful_matches"],
            "success_rate": f"{success_rate:.1f}%",
            "fallback_used": self.stats["fallback_used"],
            "fallback_rate": f"{fallback_rate:.1f}%",
            "signature_usage": self.stats["signature_usage"],
            "tag_distribution": self.stats["tag_distribution"],
            "supported_phrases": len(self.short_phrases),
            "fuzzy_patterns": len(self.fuzzy_patterns),
        }

    def add_custom_phrase(self, phrase: str, tag: str):
        """사용자 정의 짧은 발화 추가"""
        self.short_phrases[phrase] = tag
        print(f"✅ 커스텀 패턴 추가: '{phrase}' -> {tag}")

    def get_supported_phrases(self) -> Dict[str, str]:
        """지원되는 모든 짧은 발화 패턴 반환"""
        return self.short_phrases.copy()


# 글로벌 인스턴스
_global_microreactor = None


def get_microreactor() -> MicroReactor:
    """글로벌 MicroReactor 인스턴스 반환"""
    global _global_microreactor
    if _global_microreactor is None:
        _global_microreactor = MicroReactor()
    return _global_microreactor


def quick_micro_response(text: str, signature: str = "Selene") -> Optional[str]:
    """빠른 마이크로 응답 생성"""
    reactor = get_microreactor()
    result = reactor.run(text, signature)
    return result.text if result else None


if __name__ == "__main__":
    # MicroReactor 테스트
    print("🔬 MicroReactor 테스트")

    test_cases = [
        {"text": "안녕", "signature": "Selene"},
        {"text": "응", "signature": "Aurora"},
        {"text": "흠", "signature": "Phoenix"},
        {"text": "하...", "signature": "Sage"},
        {"text": "와", "signature": "Companion"},
        {"text": "아아아아", "signature": "Selene"},  # fuzzy match
        {"text": "!!!", "signature": "Aurora"},  # fuzzy match
        {"text": "이건 긴 문장이라 매칭 안됨", "signature": "Selene"},  # no match
    ]

    reactor = get_microreactor()

    for i, case in enumerate(test_cases, 1):
        print(f"\n🔬 테스트 {i}: '{case['text']}' ({case['signature']})")

        result = reactor.run(case["text"], case["signature"])

        if result:
            print(f"   ✅ 매칭: {result.tag}")
            print(f"   응답: {result.text}")
            print(f"   신뢰도: {result.confidence}")
        else:
            print(f"   ❌ 매칭 실패 - 기존 판단 루프로 진행")

    # 통계 출력
    stats = reactor.get_statistics()
    print(f"\n📊 MicroReactor 통계:")
    print(f"   처리 요청: {stats['total_processed']}")
    print(f"   성공률: {stats['success_rate']}")
    print(f"   폴백률: {stats['fallback_rate']}")
    if stats.get("signature_usage"):
        print(f"   시그니처 사용: {stats['signature_usage']}")
