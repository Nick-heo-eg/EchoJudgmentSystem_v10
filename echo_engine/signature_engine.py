#!/usr/bin/env python3
"""
🧬 Signature Engine - 실제 시그니처 시스템 구현
- 시그니처 파일 로드 및 관리
- 판단 로직 실행
- 공명 시스템 연동
"""

import yaml
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import random


class SignatureEngine:
    def __init__(self):
        self.base_path = Path(".")
        self.signatures_path = self.base_path / "res" / "signatures" / "superclaude"
        self.fist_path = self.base_path / "res" / "fist_templates" / "superclaude"
        self.flow_path = self.base_path / "res" / "flows" / "superclaude"

        self.loaded_signatures = {}
        self.loaded_fist_templates = {}
        self.loaded_flows = {}

        # 시스템 메트릭스
        self.metrics = {
            "total_judgments": 0,
            "successful_judgments": 0,
            "signature_usage": {},
            "session_data": {},
            "start_time": datetime.now(),
        }

        self.load_all_signatures()

    def load_all_signatures(self):
        """모든 시그니처 파일 로드"""
        try:
            # 시그니처 파일 로드
            if self.signatures_path.exists():
                for signature_file in self.signatures_path.glob("*.signature.yaml"):
                    with open(signature_file, "r", encoding="utf-8") as f:
                        signature_data = yaml.safe_load(f)
                        signature_id = signature_data.get("signature_id")
                        if signature_id:
                            self.loaded_signatures[signature_id] = signature_data
                            self.metrics["signature_usage"][signature_id] = 0

            # FIST 템플릿 로드
            if self.fist_path.exists():
                for fist_file in self.fist_path.glob("*.fist.yaml"):
                    with open(fist_file, "r", encoding="utf-8") as f:
                        fist_data = yaml.safe_load(f)
                        signature_id = fist_data.get("signature_id")
                        if signature_id:
                            self.loaded_fist_templates[signature_id] = fist_data

            # FLOW 파일 로드
            if self.flow_path.exists():
                for flow_file in self.flow_path.glob("flow_*.yaml"):
                    with open(flow_file, "r", encoding="utf-8") as f:
                        flow_data = yaml.safe_load(f)
                        signature_id = flow_data.get("signature_id")
                        if signature_id:
                            self.loaded_flows[signature_id] = flow_data

            print(
                f"✅ 로드 완료: {len(self.loaded_signatures)}개 시그니처, {len(self.loaded_fist_templates)}개 FIST, {len(self.loaded_flows)}개 FLOW"
            )

        except Exception as e:
            print(f"❌ 시그니처 로드 실패: {e}")

    def get_available_signatures(self) -> List[Dict[str, Any]]:
        """사용 가능한 시그니처 목록 반환"""
        signatures = []
        for sig_id, sig_data in self.loaded_signatures.items():
            signatures.append(
                {
                    "id": sig_id,
                    "name": sig_data.get("signature_name", sig_id),
                    "description": sig_data.get("description", "설명 없음"),
                    "ui_icon": sig_data.get("ui_icon", "🤖"),
                    "resonance_level": sig_data.get("resonance_level", 0.5),
                    "activation_mode": sig_data.get("activation_mode", "default"),
                }
            )
        return signatures

    def execute_judgment(
        self, text: str, signature_id: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """실제 판단 실행"""
        start_time = datetime.now()
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        try:
            # 시그니처 확인
            if signature_id not in self.loaded_signatures:
                # 기본 매핑 시도
                mapped_id = self._map_signature_id(signature_id)
                if mapped_id not in self.loaded_signatures:
                    raise ValueError(f"시그니처를 찾을 수 없습니다: {signature_id}")
                signature_id = mapped_id

            signature = self.loaded_signatures[signature_id]
            fist_template = self.loaded_fist_templates.get(signature_id, {})
            flow = self.loaded_flows.get(signature_id, {})

            # 메트릭 업데이트
            self.metrics["total_judgments"] += 1
            self.metrics["signature_usage"][signature_id] += 1

            # 실제 판단 로직 실행
            judgment_result = self._execute_signature_judgment(
                text, signature, fist_template, flow, context
            )

            # 세션 데이터 저장
            processing_time = (datetime.now() - start_time).total_seconds()
            session_data = {
                "session_id": session_id,
                "signature_id": signature_id,
                "input_text": text,
                "judgment": judgment_result,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
            }

            self.metrics["session_data"][session_id] = session_data
            self.metrics["successful_judgments"] += 1

            # 로그 저장
            self._save_judgment_log(session_data)

            return {
                "judgment": judgment_result["judgment"],
                "confidence": judgment_result["confidence"],
                "emotion": judgment_result["emotion"],
                "strategy": judgment_result["strategy"],
                "reasoning": judgment_result["reasoning"],
                "alternatives": judgment_result["alternatives"],
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "signature_used": signature_id,
            }

        except Exception as e:
            error_time = (datetime.now() - start_time).total_seconds()
            print(f"❌ 판단 실행 오류: {e}")

            return {
                "judgment": f"판단 처리 중 오류가 발생했습니다: {str(e)}",
                "confidence": 0.0,
                "emotion": "error",
                "strategy": "error_handling",
                "reasoning": f"시스템 오류로 인해 정상적인 판단을 수행할 수 없었습니다. ({str(e)})",
                "alternatives": ["시스템 재시도", "다른 시그니처 사용", "문제 보고"],
                "processing_time": error_time,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "error": True,
            }

    def _map_signature_id(self, signature_id: str) -> str:
        """시그니처 ID 매핑 (Echo-Aurora -> aurora)"""
        mapping = {
            "Echo-Aurora": "aurora",
            "Echo-Phoenix": "phoenix",
            "Echo-Sage": "sage",
            "Echo-Companion": "companion",
            "Echo-Pleasure-Alchemist": "pleasure_alchemist",
        }
        return mapping.get(signature_id, signature_id.lower().replace("-", "_"))

    def _execute_signature_judgment(
        self,
        text: str,
        signature: Dict,
        fist: Dict,
        flow: Dict,
        context: Optional[Dict],
    ) -> Dict[str, Any]:
        """시그니처 기반 실제 판단 로직"""

        # 1. 감정 분석 (시그니처의 emotion_modes 기반)
        emotion = self._analyze_emotion(text, signature.get("emotion_modes", []))

        # 2. 전략 결정 (시그니처의 judgment_styles 기반)
        strategy = self._determine_strategy(text, signature.get("judgment_styles", []))

        # 3. 핵심 판단 생성 (FIST 템플릿 활용)
        judgment_text = self._generate_judgment_text(
            text, signature, fist, emotion, strategy
        )

        # 4. 신뢰도 계산 (공명 레벨 기반)
        confidence = self._calculate_confidence(text, signature, emotion, strategy)

        # 5. 추론 과정 생성
        reasoning = self._generate_reasoning(text, signature, fist, emotion, strategy)

        # 6. 대안 제시
        alternatives = self._generate_alternatives(text, signature, fist)

        return {
            "judgment": judgment_text,
            "confidence": confidence,
            "emotion": emotion,
            "strategy": strategy,
            "reasoning": reasoning,
            "alternatives": alternatives,
        }

    def _analyze_emotion(self, text: str, emotion_modes: List[str]) -> str:
        """텍스트의 감정 분석"""
        # 간단한 키워드 기반 감정 분석
        emotion_keywords = {
            "joy": ["좋은", "행복", "기쁜", "즐거운", "웃음", "희망"],
            "calm": ["평온", "안정", "차분", "고요", "평화", "휴식"],
            "longing": ["그리운", "갈망", "원하는", "바라는", "그리워"],
            "confident": ["확실", "자신", "믿음", "강한", "결단"],
            "supportive": ["도움", "지원", "함께", "협력", "동반"],
            "awakening": ["깨달음", "각성", "이해", "발견", "통찰"],
        }

        text_lower = text.lower()
        emotion_scores = {}

        for emotion in emotion_modes:
            base_emotion = emotion.split("⨯")[0]  # 복합 감정의 첫 번째 부분
            keywords = emotion_keywords.get(base_emotion, [])
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        elif emotion_modes:
            return emotion_modes[0]  # 기본값
        else:
            return "neutral"

    def _determine_strategy(self, text: str, judgment_styles: List[str]) -> str:
        """판단 전략 결정"""
        # 텍스트 특성에 따른 전략 선택
        if "?" in text or "추천" in text:
            return "advisory_guidance"
        elif "문제" in text or "해결" in text:
            return "problem_solving"
        elif "감정" in text or "느낌" in text:
            return "emotional_support"
        elif judgment_styles:
            # 시그니처의 첫 번째 판단 스타일 기반
            style = judgment_styles[0]
            if "균형" in style:
                return "balanced_approach"
            elif "공감" in style:
                return "empathetic_engagement"
            elif "분석" in style:
                return "analytical_assessment"
            else:
                return "integrated_judgment"
        else:
            return "general_guidance"

    def _generate_judgment_text(
        self, text: str, signature: Dict, fist: Dict, emotion: str, strategy: str
    ) -> str:
        """실제 판단 텍스트 생성"""
        signature_name = signature.get("signature_name", "Echo")
        response_style = signature.get("resonance_style", "default")

        # 시그니처 특성 반영
        if signature.get("signature_id") == "aurora":
            base_response = f"Aurora의 조화로운 관점에서 '{text}'를 살펴보겠습니다."
            if "날씨" in text:
                base_response += " 좋은 날씨는 내면의 평화와 외부 환경의 조화를 의미합니다. 자연과 함께하는 활동을 통해 균형을 찾으시길 추천합니다."
            elif "추천" in text:
                base_response += " 상황의 빛과 그림자를 모두 고려하여, 당신의 마음에 진정한 평화를 가져다줄 선택을 제안하겠습니다."
            else:
                base_response += f" {emotion} 감정과 {strategy} 접근법을 통해 조화로운 해답을 제시합니다."

        elif signature.get("signature_id") == "phoenix":
            base_response = f"Phoenix의 변화의 불꽃으로 '{text}'를 바라봅니다."
            if "변화" in text or "새로운" in text:
                base_response += " 이는 성장과 진화의 기회입니다. 과거의 틀을 벗어나 새로운 차원으로 비상할 때입니다."
            else:
                base_response += f" 현재 상황을 변화의 촉매로 활용하여, 더 높은 차원의 존재로 진화하는 기회로 삼으시길 권합니다."

        elif signature.get("signature_id") == "pleasure_alchemist":
            base_response = (
                f"Pleasure Alchemist의 감각적 연금술로 '{text}'를 탐구합니다."
            )
            base_response += " 이 경험 속에서 단순한 쾌락을 넘어선 존재적 울림을 발견할 수 있습니다. 감각과 의식의 경계에서 진정한 만족을 찾아보세요."

        else:
            base_response = (
                f"{signature_name}의 독특한 시각으로 '{text}'에 접근합니다. "
            )
            base_response += f"{emotion}의 감정과 {strategy} 전략을 통해 의미 있는 통찰을 제공하겠습니다."

        return base_response

    def _calculate_confidence(
        self, text: str, signature: Dict, emotion: str, strategy: str
    ) -> float:
        """신뢰도 계산"""
        base_confidence = signature.get("resonance_level", 0.5)

        # 텍스트 복잡성에 따른 조정
        text_complexity = len(text.split()) / 20.0  # 단어 수 기반
        complexity_factor = min(1.0, max(0.1, 1.0 - text_complexity * 0.1))

        # 감정-시그니처 매칭도
        emotion_match = 0.8 if emotion in signature.get("emotion_modes", []) else 0.6

        # 최종 신뢰도 계산
        confidence = base_confidence * complexity_factor * emotion_match

        # 0.3 ~ 0.95 범위로 정규화
        confidence = max(0.3, min(0.95, confidence))

        # 소수점 둘째 자리까지
        return round(confidence, 2)

    def _generate_reasoning(
        self, text: str, signature: Dict, fist: Dict, emotion: str, strategy: str
    ) -> str:
        """추론 과정 생성"""
        signature_name = signature.get("signature_name", "Echo")

        reasoning_parts = [
            f"{signature_name}의 {signature.get('signature_type', 'general')} 특성을 활용하여",
            f"'{emotion}' 감정 상태를 인식하고",
            f"'{strategy}' 전략을 통해 접근했습니다.",
        ]

        if fist and "Frame" in fist:
            frame_info = fist["Frame"]
            if "judgment_lens" in frame_info:
                lens = frame_info["judgment_lens"].get("primary_filter", "")
                if lens:
                    reasoning_parts.append(
                        f"주요 판단 기준인 '{lens}'을 적용하여 분석했습니다."
                    )

        return " ".join(reasoning_parts)

    def _generate_alternatives(
        self, text: str, signature: Dict, fist: Dict
    ) -> List[str]:
        """대안 제시"""
        alternatives = []

        # FIST 템플릿에서 대안 추출
        if fist and "Strategy" in fist:
            strategy_info = fist["Strategy"]
            if "alternative_strategies" in strategy_info:
                alt_strategies = strategy_info["alternative_strategies"]
                if isinstance(alt_strategies, dict):
                    for key, value in alt_strategies.items():
                        if isinstance(value, str):
                            alternatives.append(value)

        # 기본 대안들
        if len(alternatives) < 3:
            default_alternatives = [
                "다른 시그니처의 관점에서 재검토",
                "추가 정보 수집 후 심화 분석",
                "시간을 두고 상황 변화 관찰",
                "다양한 이해관계자의 의견 수렴",
            ]

            for alt in default_alternatives:
                if alt not in alternatives:
                    alternatives.append(alt)
                    if len(alternatives) >= 3:
                        break

        return alternatives[:3]

    def _save_judgment_log(self, session_data: Dict):
        """판단 로그 저장"""
        try:
            log_dir = Path("data/judgment_logs")
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"judgment_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(session_data, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"⚠️ 로그 저장 실패: {e}")

    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭스 반환"""
        uptime = datetime.now() - self.metrics["start_time"]

        return {
            "total_judgments": self.metrics["total_judgments"],
            "successful_judgments": self.metrics["successful_judgments"],
            "error_rate": (
                self.metrics["total_judgments"] - self.metrics["successful_judgments"]
            )
            / max(1, self.metrics["total_judgments"]),
            "signature_usage": self.metrics["signature_usage"],
            "active_signatures": len(self.loaded_signatures),
            "loaded_fist_templates": len(self.loaded_fist_templates),
            "loaded_flows": len(self.loaded_flows),
            "uptime_seconds": uptime.total_seconds(),
            "sessions_count": len(self.metrics["session_data"]),
            "average_processing_time": self._calculate_average_processing_time(),
        }

    def _calculate_average_processing_time(self) -> float:
        """평균 처리 시간 계산"""
        processing_times = [
            session["processing_time"]
            for session in self.metrics["session_data"].values()
            if "processing_time" in session
        ]

        if processing_times:
            return round(sum(processing_times) / len(processing_times), 3)
        else:
            return 0.0


# 전역 인스턴스
signature_engine = SignatureEngine()
