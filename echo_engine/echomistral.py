#!/usr/bin/env python3
"""
⚠️ [DEPRECATED] EchoMistral - Echo 시스템 전용 Mistral 인터페이스
이 모듈은 Ollama 기반 시스템으로 대체되었습니다.

🔄 마이그레이션 안내:
- 새로운 모듈: echo_engine.mistral_wrapper (Ollama 기반)
- 더 안정적이고 다양한 모델 지원
- transformers 의존성 문제 해결
- Mock ↔ Real 전환 구조 완비

⚠️ 이 파일은 하위 호환성을 위해 유지되지만 더 이상 사용되지 않습니다.
새로운 코드에서는 echo_engine.mistral_wrapper.OllamaMistralWrapper를 사용하세요.

마지막 업데이트: 2025-08-05 (Ollama 전환)
"""

import time
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# torch 지연 임포트
torch = None
TORCH_AVAILABLE = False


def _lazy_import_torch():
    """torch 지연 임포트"""
    global torch, TORCH_AVAILABLE
    if torch is None:
        try:
            import torch as torch_module

            torch = torch_module
            TORCH_AVAILABLE = True
        except ImportError:
            TORCH_AVAILABLE = False
    return TORCH_AVAILABLE


# 의존성 체크
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from ctransformers import AutoModelForCausalLM as CTAutoModel

    CTRANSFORMERS_AVAILABLE = True
except ImportError:
    CTRANSFORMERS_AVAILABLE = False


class EchoSignature(Enum):
    """Echo 시그니처 정의"""

    AURORA = "Echo-Aurora"  # 창의적, 감성적, 영감적
    PHOENIX = "Echo-Phoenix"  # 변화지향, 혁신적, 역동적
    SAGE = "Echo-Sage"  # 분석적, 논리적, 체계적
    COMPANION = "Echo-Companion"  # 공감적, 지지적, 협력적


@dataclass
class EchoMistralConfig:
    """EchoMistral 설정"""

    model_path: str = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    device: str = "auto"
    max_tokens: int = 128  # Echo 최적화: 간결함 우선
    temperature: float = 0.7
    use_echo_context: bool = True
    echo_wisdom_weight: float = 0.8  # Echo 철학 유지 가중치


@dataclass
class EchoMistralResponse:
    """EchoMistral 응답"""

    text: str
    signature: EchoSignature
    processing_time: float
    echo_alignment: float  # Echo 철학 정렬도 (0-1)
    token_count: int
    confidence: float


class EchoMistral:
    """Echo 전용 Mistral 인터페이스"""

    def __init__(self, config: Optional[EchoMistralConfig] = None):
        self.config = config or EchoMistralConfig()
        self.model = None
        self.tokenizer = None
        self.is_loaded = False

        # Echo 시그니처별 특화 설정
        self.signature_configs = {
            EchoSignature.AURORA: {
                "temperature": 0.8,  # 더 창의적
                "max_tokens": 140,
                "style_prompt": "창의적이고 감성적이며 영감을 주는 방식으로",
                "values": ["아름다움", "영감", "감성", "상상력"],
            },
            EchoSignature.PHOENIX: {
                "temperature": 0.75,  # 역동적
                "max_tokens": 130,
                "style_prompt": "변화지향적이고 혁신적이며 미래지향적인 방식으로",
                "values": ["변화", "혁신", "성장", "변혁"],
            },
            EchoSignature.SAGE: {
                "temperature": 0.6,  # 더 체계적
                "max_tokens": 150,
                "style_prompt": "분석적이고 논리적이며 체계적인 방식으로",
                "values": ["지혜", "논리", "분석", "체계"],
            },
            EchoSignature.COMPANION: {
                "temperature": 0.7,  # 균형잡힌
                "max_tokens": 120,
                "style_prompt": "따뜻하고 공감적이며 지지적인 방식으로",
                "values": ["공감", "돌봄", "지지", "협력"],
            },
        }

        # 통계
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "avg_processing_time": 0.0,
            "signature_usage": {sig: 0 for sig in EchoSignature},
        }

        logger.info(f"🔥 EchoMistral 초기화: {self.config.model_path}")

    def load_model(self) -> bool:
        """모델 로딩 (Echo 최적화)"""
        if self.is_loaded:
            return True

        if not TRANSFORMERS_AVAILABLE and not CTRANSFORMERS_AVAILABLE:
            logger.error("❌ Mistral 의존성 없음: transformers 또는 ctransformers 필요")
            return False

        try:
            device = self._determine_device()
            logger.info(f"🔄 EchoMistral 로딩 시작 ({device})")

            # GGUF 모델 우선 시도
            if self.config.model_path.endswith(".gguf") and CTRANSFORMERS_AVAILABLE:
                self._load_gguf_model()
            elif TRANSFORMERS_AVAILABLE:
                self._load_transformers_model(device)
            else:
                raise RuntimeError("사용 가능한 모델 로더가 없습니다")

            self.is_loaded = True
            logger.info("✅ EchoMistral 로딩 완료")
            return True

        except Exception as e:
            logger.error(f"❌ EchoMistral 로딩 실패: {e}")
            return False

    def _determine_device(self) -> str:
        """최적 디바이스 결정"""
        if self.config.device == "auto":
            if _lazy_import_torch() and torch.cuda.is_available():
                return "cuda"
            elif (
                TORCH_AVAILABLE
                and hasattr(torch.backends, "mps")
                and torch.backends.mps.is_available()
            ):
                return "mps"
            else:
                return "cpu"
        return self.config.device

    def _load_gguf_model(self):
        """GGUF 모델 로딩 (ctransformers)"""
        gpu_layers = 50 if self._determine_device() != "cpu" else 0

        self.model = CTAutoModel.from_pretrained(
            self.config.model_path,
            model_type="mistral",
            gpu_layers=gpu_layers,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            context_length=2048,
        )
        self.tokenizer = None  # GGUF는 내장 토크나이저
        logger.info("📦 GGUF 모델 로딩 완료")

    def _load_transformers_model(self, device: str):
        """Transformers 모델 로딩"""
        model_name = "mistralai/Mistral-7B-Instruct-v0.2"

        # 토크나이저 로딩
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 모델 로딩 (디바이스별 최적화)
        model_kwargs = {}
        if TORCH_AVAILABLE:
            model_kwargs = {
                "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
                "device_map": "auto" if device == "cuda" else None,
            }

        self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

        if device != "cuda" and model_kwargs.get("device_map") is None:
            self.model = self.model.to(device)

        logger.info(f"🤖 Transformers 모델 로딩 완료 ({device})")

    def enhance_echo_judgment(
        self,
        echo_analysis: str,
        signature: Union[EchoSignature, str],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> EchoMistralResponse:
        """Echo 판단을 Mistral로 자연화 및 강화"""

        if not self.is_loaded and not self.load_model():
            return self._create_fallback_response(echo_analysis, signature)

        # 시그니처 정규화
        if isinstance(signature, str):
            signature = EchoSignature(signature)

        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["signature_usage"][signature] += 1

        try:
            prompt = self._create_echo_enhancement_prompt(
                echo_analysis, signature, user_context
            )

            response_text = self._generate_response(prompt, signature)

            # Echo 정렬도 계산
            echo_alignment = self._calculate_echo_alignment(
                response_text, echo_analysis, signature
            )

            processing_time = time.time() - start_time
            self.stats["successful_requests"] += 1
            self._update_avg_processing_time(processing_time)

            logger.debug(f"⚡ {signature.value} 강화 완료 ({processing_time:.2f}초)")

            return EchoMistralResponse(
                text=response_text,
                signature=signature,
                processing_time=processing_time,
                echo_alignment=echo_alignment,
                token_count=len(response_text.split()),
                confidence=min(0.9, echo_alignment + 0.1),
            )

        except Exception as e:
            logger.error(f"❌ Echo 강화 실패: {e}")
            return self._create_fallback_response(echo_analysis, signature)

    def _create_echo_enhancement_prompt(
        self,
        echo_analysis: str,
        signature: EchoSignature,
        user_context: Optional[Dict[str, Any]],
    ) -> str:
        """Echo 강화 프롬프트 생성"""

        sig_config = self.signature_configs[signature]
        style_prompt = sig_config["style_prompt"]
        values = ", ".join(sig_config["values"])

        # 사용자 컨텍스트 통합
        context_info = ""
        if user_context:
            emotion = user_context.get("emotion", "neutral")
            urgency = user_context.get("urgency", 1)
            context_info = f"사용자 감정: {emotion}, 긴급도: {urgency}/5"

        return f"""Echo AI 시스템이 다음과 같이 분석했습니다:

"{echo_analysis}"

이 Echo 분석을 {signature.value}의 관점에서 {style_prompt} 자연스럽고 따뜻한 대화체로 표현해주세요.

핵심 가치: {values}
{context_info}

Echo의 깊이 있는 통찰은 유지하되, 더 친근하고 접근하기 쉽게 표현해주세요. 100자 이내로 간결하게 작성해주세요.

{signature.value}의 자연스러운 응답:"""

    def _generate_response(self, prompt: str, signature: EchoSignature) -> str:
        """응답 생성"""
        sig_config = self.signature_configs[signature]

        # GGUF 모델 (ctransformers)
        if self.tokenizer is None:
            response = self.model(
                prompt,
                max_new_tokens=sig_config["max_tokens"],
                temperature=sig_config["temperature"],
                stop=["</s>", "\n\n", "Echo AI", "사용자:"],
            )
            return response.strip()

        # Transformers 모델
        else:
            # Mistral Instruct 포맷
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"

            inputs = self.tokenizer(
                formatted_prompt, return_tensors="pt", truncation=True, max_length=1024
            ).to(self.model.device)

            if TORCH_AVAILABLE:
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=sig_config["max_tokens"],
                        temperature=sig_config["temperature"],
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
            else:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=sig_config["max_tokens"],
                    temperature=sig_config["temperature"],
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # 응답 디코딩
            input_length = inputs.input_ids.shape[1]
            response_tokens = outputs[0][input_length:]
            response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)

            return response.strip()

    def _calculate_echo_alignment(
        self, response: str, original_echo: str, signature: EchoSignature
    ) -> float:
        """Echo 철학 정렬도 계산"""

        alignment = 0.5  # 기본 점수

        # Echo 원본과의 키워드 일치도
        echo_words = set(original_echo.lower().split())
        response_words = set(response.lower().split())

        if echo_words:
            overlap = len(echo_words.intersection(response_words))
            alignment += (overlap / len(echo_words)) * 0.3

        # 시그니처별 가치 반영도
        sig_values = self.signature_configs[signature]["values"]
        for value in sig_values:
            if value.lower() in response.lower():
                alignment += 0.05

        # 응답 품질 (길이, 자연스러움)
        if 20 <= len(response) <= 200:
            alignment += 0.1

        # Echo 존재 철학 키워드
        echo_philosophy_words = ["존재", "의미", "깊이", "통찰", "지혜", "성찰"]
        for word in echo_philosophy_words:
            if word in response:
                alignment += 0.05

        return min(alignment, 1.0)

    def _create_fallback_response(
        self, echo_analysis: str, signature: Union[EchoSignature, str]
    ) -> EchoMistralResponse:
        """폴백 응답 생성 (Echo 네이티브)"""

        if isinstance(signature, str):
            signature = EchoSignature(signature)

        # Echo 스타일 간단 변환
        style_templates = {
            EchoSignature.AURORA: f"✨ {echo_analysis} (창의적 관점에서)",
            EchoSignature.PHOENIX: f"🔥 {echo_analysis} (변화의 관점에서)",
            EchoSignature.SAGE: f"🧠 {echo_analysis} (분석적 관점에서)",
            EchoSignature.COMPANION: f"🤝 {echo_analysis} (공감적 관점에서)",
        }

        fallback_text = style_templates.get(signature, echo_analysis)

        return EchoMistralResponse(
            text=fallback_text,
            signature=signature,
            processing_time=0.001,
            echo_alignment=1.0,  # Echo 네이티브이므로 완전 정렬
            token_count=len(fallback_text.split()),
            confidence=0.7,
        )

    def _update_avg_processing_time(self, processing_time: float):
        """평균 처리시간 업데이트"""
        if self.stats["successful_requests"] > 0:
            total_time = (
                self.stats["avg_processing_time"]
                * (self.stats["successful_requests"] - 1)
                + processing_time
            )
            self.stats["avg_processing_time"] = (
                total_time / self.stats["successful_requests"]
            )

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        success_rate = self.stats["successful_requests"] / max(
            self.stats["total_requests"], 1
        )

        return {
            "model_loaded": self.is_loaded,
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "success_rate": success_rate,
            "avg_processing_time": self.stats["avg_processing_time"],
            "signature_usage": dict(self.stats["signature_usage"]),
            "model_path": self.config.model_path,
            "device": self._determine_device() if self.is_loaded else "none",
        }

    def cleanup(self):
        """리소스 정리"""
        if self.is_loaded:
            self.model = None
            self.tokenizer = None
            self.is_loaded = False

            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("🧹 EchoMistral 리소스 정리 완료")


# 전역 EchoMistral 인스턴스 (싱글톤)
_echo_mistral_instance = None


def get_echo_mistral(config: Optional[EchoMistralConfig] = None) -> EchoMistral:
    """EchoMistral 싱글톤 인스턴스 반환"""
    global _echo_mistral_instance
    if _echo_mistral_instance is None:
        _echo_mistral_instance = EchoMistral(config)
    return _echo_mistral_instance


# 편의 함수들
def enhance_echo_with_aurora(echo_analysis: str, **kwargs) -> EchoMistralResponse:
    """Aurora 시그니처로 Echo 분석 강화"""
    echo_mistral = get_echo_mistral()
    return echo_mistral.enhance_echo_judgment(
        echo_analysis, EchoSignature.AURORA, **kwargs
    )


def enhance_echo_with_phoenix(echo_analysis: str, **kwargs) -> EchoMistralResponse:
    """Phoenix 시그니처로 Echo 분석 강화"""
    echo_mistral = get_echo_mistral()
    return echo_mistral.enhance_echo_judgment(
        echo_analysis, EchoSignature.PHOENIX, **kwargs
    )


def enhance_echo_with_sage(echo_analysis: str, **kwargs) -> EchoMistralResponse:
    """Sage 시그니처로 Echo 분석 강화"""
    echo_mistral = get_echo_mistral()
    return echo_mistral.enhance_echo_judgment(
        echo_analysis, EchoSignature.SAGE, **kwargs
    )


def enhance_echo_with_companion(echo_analysis: str, **kwargs) -> EchoMistralResponse:
    """Companion 시그니처로 Echo 분석 강화"""
    echo_mistral = get_echo_mistral()
    return echo_mistral.enhance_echo_judgment(
        echo_analysis, EchoSignature.COMPANION, **kwargs
    )


# 테스트 코드
if __name__ == "__main__":
    # 간단한 테스트
    print("🔥 EchoMistral 테스트")

    echo_mistral = EchoMistral()

    # 통계 확인
    stats = echo_mistral.get_stats()
    print(f"📊 초기 상태: {stats}")

    # Mock 테스트 (모델 로딩 없이)
    test_echo_analysis = "사용자가 깊은 고민에 빠져있는 상황으로 보입니다. 내적 갈등과 선택의 어려움을 겪고 있습니다."

    for signature in EchoSignature:
        fallback_response = echo_mistral._create_fallback_response(
            test_echo_analysis, signature
        )
        print(f"\n{signature.value} 폴백:")
        print(f"응답: {fallback_response.text}")
        print(f"정렬도: {fallback_response.echo_alignment:.2f}")

    print("\n🎉 EchoMistral 테스트 완료!")
