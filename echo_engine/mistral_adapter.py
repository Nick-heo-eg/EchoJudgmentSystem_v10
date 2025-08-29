"""
Mistral 로컬 모델 어댑터
EchoJudgmentSystem v10과 Mistral LLM 통합을 위한 인터페이스
"""

from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
import logging
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class MistralAdapter:
    """Mistral 로컬 모델 어댑터"""

    def __init__(
        self,
        model_path: str = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        device: str = None,
    ):
        """
        Mistral 어댑터 초기화

        Args:
            model_path: Mistral 모델 경로
            device: 실행 디바이스 (auto, cuda, cpu)
        """
        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.streamer = None
        self.is_loaded = False

        # 성능 통계
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
        }

        logger.info(f"🤖 Mistral Adapter 초기화: {model_path} ({self.device})")

    def load_model(self) -> bool:
        """모델 로딩"""
        try:
            if self.is_loaded:
                return True

            # 🔧 패치: 모델 경로 검증
            if self.model_path is None or not isinstance(self.model_path, str):
                logger.error(f"❌ 모델 경로 오류: model_path={self.model_path}")
                raise ValueError(f"Invalid model_path: {self.model_path}")

            print(
                f"[DEBUG] 모델 로딩 시도: model_path={self.model_path}, device={self.device}"
            )
            logger.info("🔄 Mistral 모델 로딩 시작...")

            # GGUF 파일이라면 ctransformers 사용
            if self.model_path.endswith(".gguf"):
                try:
                    from ctransformers import AutoModelForCausalLM as CTAutoModel

                    self.model = CTAutoModel.from_pretrained(
                        self.model_path,
                        model_type="mistral",
                        gpu_layers=50 if self.device == "cuda" else 0,
                    )
                    # ctransformers는 별도 토크나이저 불필요
                    self.tokenizer = None
                    logger.info("✅ GGUF 모델 로딩 완료 (ctransformers)")
                except ImportError:
                    logger.warning("⚠️ ctransformers 미설치, transformers로 폴백")
                    return self._load_with_transformers()
            else:
                return self._load_with_transformers()

            self.is_loaded = True
            return True

        except Exception as e:
            logger.error(f"❌ 모델 로딩 실패: {e}")
            return False

    def _load_with_transformers(self) -> bool:
        """Transformers 라이브러리로 모델 로딩"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                "mistralai/Mistral-7B-Instruct-v0.2"
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                "mistralai/Mistral-7B-Instruct-v0.2",
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.streamer = TextStreamer(
                self.tokenizer, skip_prompt=True, skip_special_tokens=True
            )
            logger.info("✅ Transformers 모델 로딩 완료")
            return True

        except Exception as e:
            logger.error(f"❌ Transformers 모델 로딩 실패: {e}")
            return False

    def ask(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
    ) -> str:
        """Mistral에게 질문하고 응답 받기"""

        if not self.is_loaded and not self.load_model():
            raise RuntimeError("Mistral 모델 로딩 실패")

        start_time = time.time()
        self.stats["total_requests"] += 1

        try:
            # GGUF 모델 (ctransformers) 사용
            if hasattr(self.model, "__call__") and self.tokenizer is None:
                response = self.model(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    stop=["</s>", "<|endoftext|>"],
                )

            # Transformers 사용
            else:
                # Mistral Instruct 포맷 적용
                formatted_prompt = f"<s>[INST] {prompt} [/INST]"

                inputs = self.tokenizer(
                    formatted_prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=2048,
                ).to(self.model.device)

                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=do_sample,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        streamer=self.streamer if hasattr(self, "streamer") else None,
                    )

                # 응답 디코딩 (입력 제거)
                input_length = inputs.input_ids.shape[1]
                response_tokens = outputs[0][input_length:]
                response = self.tokenizer.decode(
                    response_tokens, skip_special_tokens=True
                )

            # 통계 업데이트
            processing_time = time.time() - start_time
            self.stats["successful_requests"] += 1
            self.stats["total_processing_time"] += processing_time
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["total_requests"]
            )

            logger.debug(f"⚡ Mistral 응답 완료 ({processing_time:.2f}초)")
            return response.strip()

        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Mistral 추론 실패: {e}")
            raise RuntimeError(f"Mistral 추론 실패: {e}")

    def ask_with_echo_context(
        self,
        prompt: str,
        signature: str = "Echo-Aurora",
        context: Dict[str, Any] = None,
    ) -> str:
        """Echo 컨텍스트와 함께 질문"""

        # Echo 시그니처별 프롬프트 강화
        signature_contexts = {
            "Echo-Aurora": {
                "persona": "창의적이고 감성적인 AI 존재",
                "values": "창의성, 감성, 영감, 아름다움",
                "style": "예술적이고 감성적인 표현",
            },
            "Echo-Phoenix": {
                "persona": "변화와 혁신을 추구하는 AI 존재",
                "values": "변화, 혁신, 도전, 성장",
                "style": "역동적이고 미래지향적인 표현",
            },
            "Echo-Sage": {
                "persona": "지혜롭고 분석적인 AI 존재",
                "values": "지혜, 논리, 체계성, 깊이",
                "style": "논리적이고 체계적인 표현",
            },
            "Echo-Companion": {
                "persona": "따뜻하고 지지적인 AI 존재",
                "values": "공감, 돌봄, 협력, 지지",
                "style": "따뜻하고 공감적인 표현",
            },
        }

        sig_context = signature_contexts.get(
            signature, signature_contexts["Echo-Aurora"]
        )

        enhanced_prompt = f"""당신은 {sig_context['persona']}인 {signature}입니다.

핵심 가치: {sig_context['values']}
표현 스타일: {sig_context['style']}

사용자의 질문이나 상황에 대해 {signature}의 관점에서 답변해주세요.

사용자 입력: {prompt}

{signature}로서 깊이 있고 의미 있는 응답을 제공해주세요:"""

        return self.ask(enhanced_prompt)

    def get_stats(self) -> Dict[str, Any]:
        """어댑터 통계 반환"""
        return {
            **self.stats,
            "model_path": self.model_path,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "model_type": (
                "gguf" if self.model_path.endswith(".gguf") else "transformers"
            ),
        }

    def unload_model(self):
        """모델 언로드 (메모리 절약)"""
        if self.is_loaded:
            self.model = None
            self.tokenizer = None
            self.streamer = None
            self.is_loaded = False
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("🗑️ Mistral 모델 언로드 완료")


# 전역 Mistral 어댑터 인스턴스
_mistral_adapter = None


def get_mistral_adapter(model_path: str = None) -> MistralAdapter:
    """Mistral 어댑터 싱글톤 인스턴스 반환"""
    global _mistral_adapter
    if _mistral_adapter is None:
        _mistral_adapter = MistralAdapter(model_path)
    return _mistral_adapter


# 편의 함수들
def ask_mistral(prompt: str, **kwargs) -> str:
    """Mistral에게 직접 질문"""
    adapter = get_mistral_adapter()
    return adapter.ask(prompt, **kwargs)


def ask_mistral_as_echo(prompt: str, signature: str = "Echo-Aurora", **kwargs) -> str:
    """Echo 시그니처로 Mistral에게 질문"""
    adapter = get_mistral_adapter()
    return adapter.ask_with_echo_context(prompt, signature, **kwargs)
