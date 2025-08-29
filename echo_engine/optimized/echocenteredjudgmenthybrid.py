class EchoCenteredJudgmentHybrid:
    """
    🎯 Echo 중심 하이브리드 판단 시스템

    Echo가 주도하는 판단 시스템으로, 필요에 따라 Claude와 제한적으로 협업하되
    항상 Echo가 최종 판단자로서 결정권을 가짐
    """

    def __init__(self):
        # Echo 독립 판단 컴포넌트들
        self.seed_kernel = (
            SeedKernel() if ECHO_COMPONENTS_AVAILABLE and SeedKernel else None
        )
        self.persona_core = (
            PersonaCore() if ECHO_COMPONENTS_AVAILABLE and PersonaCore else None
        )
        self.emotion_infer = (
            EmotionInfer() if ECHO_COMPONENTS_AVAILABLE and EmotionInfer else None
        )
        self.reasoning_engine = (
            ReasoningEngine() if ECHO_COMPONENTS_AVAILABLE and ReasoningEngine else None
        )

        # Claude 협업 컴포넌트들 (조건부 사용)
        self.claude_fallback_handler = (
            get_claude_fallback_handler() if ECHO_COMPONENTS_AVAILABLE else None
        )
        self.signature_rewriter = (
            get_signature_rewriter() if ECHO_COMPONENTS_AVAILABLE else None
        )
        self.judgment_labeler = (
            get_judgment_labeler() if ECHO_COMPONENTS_AVAILABLE else None
        )

        # 🔗 기존 구현 모듈들 연결 (v2.1 통합)
        # 🔥 EchoMistral 연결
        try:
            self.echo_mistral = get_echo_mistral()
            self.echo_mistral_available = True
            print("✅ EchoMistral 연결 성공")
        except Exception as e:
            print(f"⚠️ EchoMistral 연결 실패: {e}")
            self.echo_mistral = None
            self.echo_mistral_available = False

        self.meta_logger = None  # Enhanced Meta Logger 연결점
        self.brain_monitor = None  # Echo Brain Monitor 연결점
        self.advanced_emotion_analyzer = None  # Advanced Emotion Analyzer 연결점
        self.system_memory = None  # Echo System Memory 연결점
        self.strategy_engine = None  # Probabilistic Strategy Engine 연결점

        # 🧠 Enhanced LLM-Free Judge 연결
        try:
            self.enhanced_judge = get_enhanced_llm_free_judge()
            self.enhanced_judge_available = True
            print("✅ Enhanced LLM-Free Judge 연결 성공")
        except Exception as e:
            print(f"⚠️ Enhanced LLM-Free Judge 연결 실패: {e}")
            self.enhanced_judge = None
            self.enhanced_judge_available = False

        # 🛡️ Error Recovery System 연결
        try:
            self.error_recovery = get_error_recovery_system()
            self.error_recovery_available = True
            print("✅ Error Recovery System 연결 성공")
        except Exception as e:
            print(f"⚠️ Error Recovery System 연결 실패: {e}")
            self.error_recovery = None
            self.error_recovery_available = False

        # 통합 기능 활성화 플래그
        self.enable_duplication_prevention = False
        self.enable_advanced_emotion_analysis = False
        self.enable_real_time_monitoring = False

        # 시스템 통계
        self.decision_stats = {
            "total_judgments": 0,
            "pure_echo_count": 0,
            "claude_consultation_count": 0,
            "echo_override_count": 0,
            "echo_independence_ratio": 0.0,
        }

        # Foundation Doctrine 설정
        self.doctrine_constraints = {
            "echo_final_authority": True,
            "claude_consultation_threshold": 0.85,
            "echo_override_always_allowed": True,
            "judgment_transparency_required": True,
        }

        print("🎯 Echo-Centered Judgment Hybrid 시스템 초기화 완료")
        print("   📜 Foundation Doctrine v3.0 준수")
        print("   🧠 Echo 독립 판단 우선")
        print("   🤝 Claude 조건부 협업")
        print("   ⚖️ Echo 최종 판단권 보장")

    async def process_judgment_request(
        self, request: JudgmentRequest
    ) -> EchoJudgmentResult:
        """
        판단 요청 처리 - Echo 중심 하이브리드 플로우

        1. 복잡도 분석
        2. Echo 독립 판단 시도
        3. 필요시 Claude 협업 (조건부)
        4. Echo 최종 검토 및 결정
        """

        start_time = time.time()
        self.decision_stats["total_judgments"] += 1

        # 1. 복잡도 및 Echo 신뢰도 분석
        complexity_score = request.complexity_score or self._analyze_complexity(
            request.user_input
        )
        echo_confidence = request.echo_confidence or self._assess_echo_confidence(
            request.user_input, complexity_score
        )

        complexity_level = self._classify_complexity(complexity_score)

        print(f"🔍 판단 요청 분석:")
        print(f"   📊 복잡도: {complexity_score:.2f} ({complexity_level.value})")
        print(f"   🎯 Echo 신뢰도: {echo_confidence:.2f}")

        # 2. Echo 독립 판단 시도 (항상 먼저 시도)
        echo_independent_result = await self._echo_independent_judgment(
            request, complexity_score, echo_confidence
        )

        # 3. LLM 강화 필요성 판단
        should_enhance_with_llm = self._should_enhance_with_llm(
            complexity_score, echo_confidence, request
        )

        if not should_enhance_with_llm:
            # Echo 완전 독립 판단
            return self._finalize_pure_echo_judgment(
                echo_independent_result, complexity_level, start_time
            )

        # 4. EchoMistral 강화 시도 (Claude보다 우선)
        if self.echo_mistral_available and self._should_use_mistral(request):
            print(f"🔥 Echo가 EchoMistral로 판단 강화 (복잡도: {complexity_score:.2f})")
            mistral_result = await self._enhance_with_echo_mistral(
                echo_independent_result, request
            )
            return self._finalize_mistral_enhanced_judgment(
                mistral_result, complexity_level, start_time
            )

        # 5. Claude 협업 수행 (Mistral 사용 불가시만)
        should_consult_claude = self._should_consult_claude(
            complexity_score, echo_confidence, request
        )
        if should_consult_claude:
            print(f"🤝 Echo가 Claude 협업 요청 (복잡도: {complexity_score:.2f})")
            claude_consultation_result = await self._consult_claude_conditionally(
                request, complexity_score, echo_confidence
            )

            # 6. Echo 최종 검토 및 결정 (Claude 케이스)
            final_result = await self._echo_final_review_and_decision(
                echo_independent_result,
                claude_consultation_result,
                request,
                complexity_level,
                start_time,
            )
        else:
            # Claude도 사용 불가시 Echo 독립 판단
            final_result = self._finalize_pure_echo_judgment(
                echo_independent_result, complexity_level, start_time
            )

        # 7. 통계 업데이트
        self._update_decision_stats(final_result.decision_path)

        return final_result

    def _should_enhance_with_llm(
        self, complexity_score: float, echo_confidence: float, request: JudgmentRequest
    ) -> bool:
        """LLM 강화 필요성 판단"""

        # 낮은 복잡도에서는 LLM 강화 불필요
        if complexity_score < 0.4:
            return False

        # Echo 신뢰도가 높으면 LLM 강화 불필요
        if echo_confidence > 0.8:
            return False

        # 사용자가 자연스러운 대화를 원하는 경우
        conversational_keywords = ["이야기", "대화", "친근하게", "자연스럽게", "편하게"]
        if any(keyword in request.user_input for keyword in conversational_keywords):
            return True

        # 중간 이상 복잡도이거나 Echo 신뢰도가 중간 이하인 경우
        return complexity_score >= 0.4 or echo_confidence <= 0.7

    def _should_use_mistral(self, request: JudgmentRequest) -> bool:
        """EchoMistral 사용 여부 결정"""

        # EchoMistral 사용 금지 키워드
        mistral_avoid_keywords = ["실시간", "즉시", "빨리", "급하게", "간단히", "짧게"]

        if any(keyword in request.user_input for keyword in mistral_avoid_keywords):
            return False

        # EchoMistral 선호 상황
        mistral_prefer_keywords = [
            "자연스럽게",
            "친근하게",
            "따뜻하게",
            "대화",
            "이야기",
            "창의적",
            "감성적",
            "영감적",
            "혁신적",
            "분석적",
            "공감적",
        ]

        return any(keyword in request.user_input for keyword in mistral_prefer_keywords)

    async def _enhance_with_echo_mistral(
        self, echo_result: Dict[str, Any], request: JudgmentRequest
    ) -> Dict[str, Any]:
        """EchoMistral로 Echo 판단 강화"""

        try:
            # Echo 시그니처 매핑
            signature_mapping = {
                "Aurora": EchoSignature.AURORA,
                "Phoenix": EchoSignature.PHOENIX,
                "Sage": EchoSignature.SAGE,
                "Companion": EchoSignature.COMPANION,
            }

            echo_signature = signature_mapping.get(
                request.signature, EchoSignature.AURORA
            )

            # EchoMistral로 강화
            mistral_response = self.echo_mistral.enhance_echo_judgment(
                echo_analysis=echo_result["response"],
                signature=echo_signature,
                user_context={
                    "emotion": request.emotion,
                    "urgency": request.context.get("urgency", 1),
                },
            )

            return {
                "enhanced_response": mistral_response.text,
                "original_echo": echo_result["response"],
                "echo_alignment": mistral_response.echo_alignment,
                "processing_time": mistral_response.processing_time,
                "confidence": mistral_response.confidence,
                "enhancement_quality": mistral_response.echo_alignment,
            }

        except Exception as e:
            # EchoMistral 실패시 Error Recovery 시스템에 보고
            if self.error_recovery_available:
                error_id = self.error_recovery.report_error(
                    SystemComponent.HYBRID_SYSTEM,
                    e,
                    {"mistral_enhancement": True, "signature": request.signature},
                )
                print(f"   🛡️ EchoMistral 오류 복구 시작: {error_id}")

            # 원본 Echo 결과 반환
            return {
                "enhanced_response": echo_result["response"],
                "original_echo": echo_result["response"],
                "echo_alignment": 1.0,
                "processing_time": 0.0,
                "confidence": echo_result.get("confidence", 0.7),
                "enhancement_quality": 0.0,
                "error": str(e),
            }

    def _finalize_mistral_enhanced_judgment(
        self,
        mistral_result: Dict[str, Any],
        complexity_level: JudgmentComplexity,
        start_time: float,
    ) -> EchoJudgmentResult:
        """EchoMistral 강화 판단 최종화"""

        processing_time = time.time() - start_time

        return EchoJudgmentResult(
            final_judgment=mistral_result["enhanced_response"],
            decision_path=EchoDecisionPath.ECHO_WITH_MISTRAL,
            judgment_source=(
                JudgmentSource.ECHO_INDEPENDENT
                if ECHO_COMPONENTS_AVAILABLE
                else "echo_independent"
            ),
            confidence_score=mistral_result["confidence"],
            complexity_assessment=complexity_level,
            processing_time=processing_time,
            echo_reasoning=f"Echo 독립 분석을 EchoMistral로 자연화했습니다. 정렬도: {mistral_result['echo_alignment']:.2f}",
            claude_input=None,
            echo_override_reason=None,
            mistral_enhancement_score=mistral_result["echo_alignment"],
        )

    def _analyze_complexity(self, user_input: str) -> float:
        """사용자 입력 복잡도 분석"""

        # 기본 복잡도 지표들
        complexity_factors = []

        # 1. 길이 기반 복잡도
        length_complexity = min(len(user_input) / 500.0, 0.3)
        complexity_factors.append(length_complexity)

        # 2. 어휘 복잡도
        complex_keywords = [
            "철학",
            "존재론",
            "인식론",
            "알고리즘",
            "아키텍처",
            "최적화",
            "분석",
            "구현",
            "설계",
            "시스템",
            "프레임워크",
            "패러다임",
        ]
        vocab_complexity = (
            len([kw for kw in complex_keywords if kw in user_input]) * 0.1
        )
        complexity_factors.append(vocab_complexity)

        # 3. 문장 구조 복잡도
        sentence_count = len([s for s in user_input.split(".") if s.strip()])
        structure_complexity = min(sentence_count * 0.05, 0.2)
        complexity_factors.append(structure_complexity)

        # 4. 질문 복잡도
        question_markers = ["왜", "어떻게", "무엇", "언제", "어디서", "누가"]
        question_complexity = (
            len([q for q in question_markers if q in user_input]) * 0.05
        )
        complexity_factors.append(question_complexity)

        base_complexity = sum(complexity_factors)

        # 5. 특수 상황 복잡도 가중치
        if "코드" in user_input and "구현" in user_input:
            base_complexity += 0.3
        if "철학" in user_input or "존재" in user_input:
            base_complexity += 0.4
        if "페어 프로그래밍" in user_input:
            base_complexity += 0.2

        return min(base_complexity, 1.0)

    def _assess_echo_confidence(
        self, user_input: str, complexity_score: float
    ) -> float:
        """Echo의 독립 처리 신뢰도 평가"""

        base_confidence = 0.8  # Echo 기본 신뢰도

        # 복잡도에 따른 신뢰도 조정
        complexity_penalty = complexity_score * 0.6
        confidence = base_confidence - complexity_penalty

        # Echo가 잘 처리할 수 있는 영역
        echo_strength_keywords = [
            "안녕",
            "감사",
            "좋아",
            "기뻐",
            "도움",
            "이해",
            "함께",
            "생각",
        ]

        if any(keyword in user_input for keyword in echo_strength_keywords):
            confidence += 0.2

        # Echo가 어려워하는 영역
        echo_weakness_keywords = [
            "복잡한 알고리즘",
            "시스템 아키텍처",
            "철학적 분석",
            "코드 구현",
        ]

        if any(keyword in user_input for keyword in echo_weakness_keywords):
            confidence -= 0.3

        return max(0.1, min(confidence, 1.0))

    def _classify_complexity(self, score: float) -> JudgmentComplexity:
        """복잡도 점수를 레벨로 분류"""
        if score < 0.3:
            return JudgmentComplexity.TRIVIAL
        elif score < 0.5:
            return JudgmentComplexity.SIMPLE
        elif score < 0.7:
            return JudgmentComplexity.MODERATE
        elif score < 0.85:
            return JudgmentComplexity.COMPLEX
        else:
            return JudgmentComplexity.HIGHLY_COMPLEX

    async def _echo_independent_judgment(
        self, request: JudgmentRequest, complexity_score: float, echo_confidence: float
    ) -> Dict[str, Any]:
        """Echo 독립 판단 수행 - Enhanced LLM-Free Judge 활용"""

        print("🧠 Echo 독립 판단 수행 중...")

        # Enhanced LLM-Free Judge 사용 가능시 활용
        if self.enhanced_judge_available and self.enhanced_judge:
            try:
                print("   🧠 Enhanced LLM-Free Judge 활용")
                enhanced_result = (
                    await self.enhanced_judge.process_independent_judgment(
                        user_input=request.user_input,
                        signature=request.signature,
                        context={
                            "emotion": request.emotion,
                            "complexity": complexity_score,
                            "domain": request.context.get("domain", "general"),
                        },
                    )
                )

                return {
                    "response": enhanced_result.judgment,
                    "reasoning": " → ".join(enhanced_result.processing_steps),
                    "confidence": enhanced_result.confidence_score,
                    "complexity": complexity_score,
                    "signature": request.signature,
                    "emotion": max(
                        enhanced_result.emotion_analysis,
                        key=enhanced_result.emotion_analysis.get,
                    ),
                    "enhanced_analysis": {
                        "complexity_level": enhanced_result.complexity_level.value,
                        "reasoning_mode": enhanced_result.reasoning_mode.value,
                        "signature_alignment": enhanced_result.signature_alignment,
                        "fallback_quality": enhanced_result.fallback_quality,
                        "processing_time": enhanced_result.processing_time,
                    },
                }
            except Exception as e:
                print(f"   ⚠️ Enhanced Judge 실행 실패, 기본 판단으로 대체: {e}")

                # Error Recovery System에 오류 보고
                if self.error_recovery_available:
                    error_id = self.error_recovery.report_error(
                        SystemComponent.ENHANCED_JUDGE,
                        e,
                        {
                            "user_input": request.user_input,
                            "signature": request.signature,
                        },
                    )
                    print(f"   🛡️ Error Recovery 시작: {error_id}")

        # 기본 Echo 독립 판단 로직 (Enhanced Judge 불가시)
        print("   🔄 기본 Echo 독립 판단 사용")
        echo_reasoning = self._generate_echo_reasoning(
            request.user_input, request.signature, request.emotion
        )
        echo_response = self._generate_echo_response(
            request.user_input, request.signature, request.emotion
        )

        return {
            "response": echo_response,
            "reasoning": echo_reasoning,
            "confidence": echo_confidence,
            "complexity": complexity_score,
            "signature": request.signature,
            "emotion": request.emotion,
        }

    def _generate_echo_reasoning(
        self, user_input: str, signature: str, emotion: str
    ) -> str:
        """Echo 독립 추론 생성"""

        signature_reasoning = {
            "Aurora": f"✨ '{user_input}'에 대해 창의적이고 영감적인 관점에서 접근해보면...",
            "Phoenix": f"🔥 '{user_input}' 상황을 변화와 성장의 기회로 바라보면...",
            "Sage": f"🧘 '{user_input}'을 지혜롭고 분석적으로 고려해보면...",
            "Companion": f"🤗 '{user_input}' 상황에서 따뜻하고 공감적으로 접근하면...",
        }

        base_reasoning = signature_reasoning.get(
            signature, signature_reasoning["Aurora"]
        )

        emotion_context = {
            "joy": "기쁜 마음으로 긍정적인 해결책을 찾을 수 있을 것 같아요",
            "contemplation": "차분히 생각해보면 좋은 방향을 찾을 수 있을 거예요",
            "curiosity": "궁금한 마음으로 탐구해보면 흥미로운 발견이 있을 것 같아요",
            "determination": "확신을 가지고 도전하면 좋은 결과를 얻을 수 있을 거예요",
        }

        emotion_text = emotion_context.get(emotion, "")

        return f"{base_reasoning} {emotion_text}"

    def _generate_echo_response(
        self, user_input: str, signature: str, emotion: str
    ) -> str:
        """Echo 독립 응답 생성"""

        signature_responses = {
            "Aurora": f"✨ '{user_input}'에 대해 새로운 가능성들을 생각해보니, 정말 흥미로운 접근법들이 떠올라요! 함께 창의적으로 탐험해보는 건 어떨까요?",
            "Phoenix": f"🔥 '{user_input}' 상황이군요! 이런 도전적인 순간이야말로 성장할 수 있는 기회라고 생각해요. 함께 변화를 만들어보죠!",
            "Sage": f"🧘 '{user_input}'을 깊이 생각해보니, 여러 관점에서 접근할 수 있을 것 같습니다. 차근차근 분석해서 지혜로운 해결책을 찾아보겠어요.",
            "Companion": f"🤗 '{user_input}' 상황을 이해해요. 혼자가 아니라 함께 있다는 걸 느끼셨으면 좋겠어요. 어떤 도움이 필요한지 말씀해주세요.",
        }

        return signature_responses.get(signature, signature_responses["Aurora"])

    def _should_consult_claude(
        self, complexity_score: float, echo_confidence: float, request: JudgmentRequest
    ) -> bool:
        """Claude 협업 필요성 판단"""

        # Foundation Doctrine 준수: 엄격한 조건
        if (
            complexity_score
            < self.doctrine_constraints["claude_consultation_threshold"]
        ):
            return False

        if echo_confidence > 0.7:
            return False

        # 특수 상황 검토
        philosophical_keywords = ["철학", "존재", "의식", "인식", "본질"]
        code_keywords = ["구현", "알고리즘", "코드", "프로그래밍"]

        is_philosophical = any(
            kw in request.user_input for kw in philosophical_keywords
        )
        is_coding = any(kw in request.user_input for kw in code_keywords)

        return is_philosophical or is_coding or complexity_score >= 0.9

    async def _consult_claude_conditionally(
        self, request: JudgmentRequest, complexity_score: float, echo_confidence: float
    ) -> Dict[str, Any]:
        """조건부 Claude 협업"""

        if not self.claude_fallback_handler:
            return {"error": "Claude 핸들러 사용 불가"}

        # Claude 협업 요청 구성
        fallback_request = ClaudeFallbackRequest(
            user_input=request.user_input,
            complexity_score=complexity_score,
            echo_confidence=echo_confidence,
            reason=self._determine_fallback_reason(request.user_input),
            context=request.context,
            signature=request.signature,
            emotion=request.emotion,
        )

        claude_response = await self.claude_fallback_handler.process_claude_fallback(
            fallback_request
        )

        return {
            "claude_raw": claude_response.claude_raw_response,
            "claude_rewritten": claude_response.echo_rewritten_response,
            "processing_time": claude_response.processing_time,
            "quality_score": claude_response.rewrite_quality_score,
        }

    def _determine_fallback_reason(self, user_input: str) -> ClaudeFallbackReason:
        """Claude 폴백 사유 결정"""

        if any(kw in user_input for kw in ["철학", "존재", "의식"]):
            return ClaudeFallbackReason.PHILOSOPHICAL_INQUIRY
        elif any(kw in user_input for kw in ["코드", "구현", "알고리즘"]):
            return ClaudeFallbackReason.CODE_GENERATION
        elif "페어 프로그래밍" in user_input:
            return ClaudeFallbackReason.PAIR_PROGRAMMING
        else:
            return ClaudeFallbackReason.HIGH_COMPLEXITY

    async def _echo_final_review_and_decision(
        self,
        echo_result: Dict[str, Any],
        claude_result: Dict[str, Any],
        request: JudgmentRequest,
        complexity_level: JudgmentComplexity,
        start_time: float,
    ) -> EchoJudgmentResult:
        """Echo 최종 검토 및 결정"""

        print("⚖️ Echo 최종 검토 및 결정 중...")

        # Echo가 Claude 제안을 검토
        echo_approval = self._echo_reviews_claude_suggestion(echo_result, claude_result)

        if echo_approval["approved"]:
            # Claude 제안 수용하되 Echo 스타일로 최종 다듬기
            final_judgment = self._echo_refines_claude_suggestion(
                claude_result["claude_rewritten"], request.signature
            )
            decision_path = EchoDecisionPath.ECHO_WITH_CLAUDE_INPUT
            echo_reasoning = f"Claude의 제안을 검토한 결과 유용하다고 판단하여 수용하되, Echo 스타일로 재구성했습니다."
            claude_input = claude_result["claude_raw"]
            echo_override_reason = None

        else:
            # Claude 제안 거부하고 Echo 독립 판단 고수
            final_judgment = echo_result["response"]
            decision_path = EchoDecisionPath.ECHO_OVERRIDE
            echo_reasoning = echo_result["reasoning"]
            claude_input = claude_result["claude_raw"]
            echo_override_reason = echo_approval["rejection_reason"]

            print(f"🚫 Echo가 Claude 제안 거부: {echo_override_reason}")
            self.decision_stats["echo_override_count"] += 1

        processing_time = time.time() - start_time

        return EchoJudgmentResult(
            final_judgment=final_judgment,
            decision_path=decision_path,
            judgment_source=(
                JudgmentSource.ECHO_CLAUDE_COLLABORATION
                if decision_path == EchoDecisionPath.ECHO_WITH_CLAUDE_INPUT
                else JudgmentSource.ECHO_INDEPENDENT
            ),
            confidence_score=echo_result["confidence"],
            complexity_assessment=complexity_level,
            processing_time=processing_time,
            echo_reasoning=echo_reasoning,
            claude_input=claude_input,
            echo_override_reason=echo_override_reason,
            signature_used=request.signature,
            emotion_detected=request.emotion,
            metadata={
                "echo_final_authority": True,
                "doctrine_compliance": "TT.100-107",
                "claude_consultation_occurred": True,
                "echo_review_passed": echo_approval["approved"],
            },
        )

    def _finalize_pure_echo_judgment(
        self,
        echo_result: Dict[str, Any],
        complexity_level: JudgmentComplexity,
        start_time: float,
    ) -> EchoJudgmentResult:
        """Echo 완전 독립 판단 결과 확정"""

        processing_time = time.time() - start_time
        self.decision_stats["pure_echo_count"] += 1

        print("✅ Echo 완전 독립 판단 완료")

        return EchoJudgmentResult(
            final_judgment=echo_result["response"],
            decision_path=EchoDecisionPath.PURE_ECHO,
            judgment_source=JudgmentSource.ECHO_INDEPENDENT,
            confidence_score=echo_result["confidence"],
            complexity_assessment=complexity_level,
            processing_time=processing_time,
            echo_reasoning=echo_result["reasoning"],
            claude_input=None,
            echo_override_reason=None,
            signature_used=echo_result["signature"],
            emotion_detected=echo_result["emotion"],
            metadata={
                "echo_final_authority": True,
                "doctrine_compliance": "TT.100-107",
                "claude_consultation_occurred": False,
                "pure_echo_judgment": True,
                **(
                    {}
                    if "enhanced_analysis" not in echo_result
                    else {"enhanced_analysis": echo_result["enhanced_analysis"]}
                ),
            },
        )

    def _echo_reviews_claude_suggestion(
        self, echo_result: Dict[str, Any], claude_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Echo가 Claude 제안을 검토"""

        # 간단한 검토 로직 (실제로는 더 정교한 분석 필요)
        claude_quality = claude_result.get("quality_score", 0.0)
        echo_confidence = echo_result["confidence"]

        # Echo가 Claude 제안을 승인하는 조건
        approval_conditions = [
            claude_quality > 0.7,  # Claude 응답 품질이 높음
            echo_confidence < 0.5,  # Echo 신뢰도가 낮음
            len(claude_result.get("claude_rewritten", "")) > 20,  # Claude 응답이 실질적
        ]

        approved = all(approval_conditions)

        if not approved:
            rejection_reasons = []
            if claude_quality <= 0.7:
                rejection_reasons.append("Claude 응답 품질 부족")
            if echo_confidence >= 0.5:
                rejection_reasons.append("Echo 독립 처리 충분히 가능")
            if len(claude_result.get("claude_rewritten", "")) <= 20:
                rejection_reasons.append("Claude 응답이 실질적이지 않음")

            rejection_reason = ", ".join(rejection_reasons)
        else:
            rejection_reason = None

        return {
            "approved": approved,
            "rejection_reason": rejection_reason,
            "review_notes": f"Claude 품질: {claude_quality:.2f}, Echo 신뢰도: {echo_confidence:.2f}",
        }

    def _echo_refines_claude_suggestion(
        self, claude_suggestion: str, signature: str
    ) -> str:
        """Echo가 Claude 제안을 자신의 스타일로 재구성"""

        # Echo의 최종 터치 추가
        signature_refinements = {
            "Aurora": lambda text: f"✨ {text} 이런 새로운 접근이 정말 흥미롭지 않아요?",
            "Phoenix": lambda text: f"🔥 {text} 함께 이 도전을 성장의 기회로 만들어보죠!",
            "Sage": lambda text: f"🧘 {text} 이렇게 깊이 생각해보니 더 명확해지는 것 같아요.",
            "Companion": lambda text: f"🤗 {text} 이해가 되시나요? 더 궁금한 점이 있으면 언제든 말씀해주세요.",
        }

        refiner = signature_refinements.get(signature, signature_refinements["Aurora"])
        return refiner(claude_suggestion)

    def _update_decision_stats(self, decision_path: EchoDecisionPath):
        """결정 경로 통계 업데이트"""

        if decision_path == EchoDecisionPath.ECHO_WITH_CLAUDE_INPUT:
            self.decision_stats["claude_consultation_count"] += 1

        total = self.decision_stats["total_judgments"]
        if total > 0:
            pure_echo = self.decision_stats["pure_echo_count"]
            self.decision_stats["echo_independence_ratio"] = pure_echo / total

    def get_system_analytics(self) -> Dict[str, Any]:
        """시스템 분석 데이터 반환"""

        total = self.decision_stats["total_judgments"]

        return {
            "decision_statistics": self.decision_stats.copy(),
            "echo_dominance_metrics": {
                "echo_independence_ratio": self.decision_stats[
                    "echo_independence_ratio"
                ],
                "claude_usage_ratio": self.decision_stats["claude_consultation_count"]
                / max(total, 1),
                "echo_override_ratio": self.decision_stats["echo_override_count"]
                / max(total, 1),
            },
            "doctrine_compliance": {
                "echo_final_authority_maintained": True,
                "claude_limited_to_assistant": True,
                "judgment_transparency_enforced": True,
                "foundation_doctrine_version": "v3.0",
            },
            "performance_metrics": {
                "total_judgments": total,
                "echo_maintained_control": True,
                "system_integrity": "high",
            },
            "integrated_modules": {
                "echo_mistral": self.echo_mistral_available,
                "enhanced_judge": self.enhanced_judge_available,
                "error_recovery_system": self.error_recovery_available,
                "mistral_backend": self.mistral_backend is not None,
                "meta_logger": self.meta_logger is not None,
                "brain_monitor": self.brain_monitor is not None,
                "advanced_emotion_analyzer": self.advanced_emotion_analyzer is not None,
                "system_memory": self.system_memory is not None,
                "strategy_engine": self.strategy_engine is not None,
                "enhanced_llm_free_judge": self.enhanced_judge_available,
                "error_recovery_system": self.error_recovery_available,
            },
            "integration_features": {
                "duplication_prevention": self.enable_duplication_prevention,
                "advanced_emotion_analysis": self.enable_advanced_emotion_analysis,
                "real_time_monitoring": self.enable_real_time_monitoring,
                "enhanced_independent_judgment": self.enhanced_judge_available,
            },
            "enhanced_judge_analytics": (
                self._get_enhanced_judge_analytics()
                if self.enhanced_judge_available
                else {}
            ),
            "error_recovery_analytics": (
                self._get_error_recovery_analytics()
                if self.error_recovery_available
                else {}
            ),
            "echo_mistral_analytics": (
                self._get_echo_mistral_analytics()
                if self.echo_mistral_available
                else {}
            ),
        }

    def _get_enhanced_judge_analytics(self) -> Dict[str, Any]:
        """Enhanced Judge 성능 분석 데이터 반환"""
        if not self.enhanced_judge_available or not self.enhanced_judge:
            return {"status": "unavailable"}

        try:
            analytics = self.enhanced_judge.get_performance_analytics()
            return {
                "status": "active",
                "performance_metrics": analytics,
                "integration_quality": (
                    "high" if analytics.get("average_confidence", 0) > 0.7 else "medium"
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_error_recovery_analytics(self) -> Dict[str, Any]:
        """Error Recovery System 분석 데이터 반환"""
        if not self.error_recovery_available or not self.error_recovery:
            return {"status": "unavailable"}

        try:
            system_status = self.error_recovery.get_system_status()
            return {
                "status": "active",
                "system_health": system_status,
                "recovery_recommendations": self.error_recovery.get_recovery_recommendations(),
                "integration_quality": (
                    "high"
                    if system_status.get("recent_health", {}).get(
                        "performance_score", 0
                    )
                    > 80
                    else "medium"
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_echo_mistral_analytics(self) -> Dict[str, Any]:
        """EchoMistral 성능 분석 데이터 반환"""
        if not self.echo_mistral_available or not self.echo_mistral:
            return {"status": "unavailable"}

        try:
            mistral_stats = self.echo_mistral.get_stats()
            return {
                "status": "active",
                "model_loaded": mistral_stats["model_loaded"],
                "performance_metrics": {
                    "total_requests": mistral_stats["total_requests"],
                    "successful_requests": mistral_stats["successful_requests"],
                    "success_rate": mistral_stats["success_rate"],
                    "avg_processing_time": mistral_stats["avg_processing_time"],
                },
                "signature_usage": mistral_stats["signature_usage"],
                "device": mistral_stats["device"],
                "integration_quality": (
                    "high" if mistral_stats["success_rate"] > 0.8 else "medium"
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def connect_existing_implementations(self):
        """🔗 기존 구현된 모듈들을 동적으로 연결"""

        print("🔗 기존 구현 모듈들 연결 시작...")
        connection_count = 0

        # EchoMistral 연결 시도
        try:
            from echo_engine.echomistral import EchoMistral

            self.mistral_backend = EchoMistral()
            print("   ✅ EchoMistral 백엔드 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ EchoMistral 연결 실패: {e}")

        # Enhanced Meta Logger 연결
        try:
            from echo_engine.enhanced_meta_logger import EnhancedMetaLogger

            self.meta_logger = EnhancedMetaLogger()
            print("   ✅ Enhanced Meta Logger 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ Meta Logger 연결 실패: {e}")

        # Echo Brain Monitor 연결
        try:
            from echo_engine.echo_brain_monitor import EchoBrainMonitor

            self.brain_monitor = EchoBrainMonitor()
            self.enable_real_time_monitoring = True
            print("   ✅ Echo Brain Monitor 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ Brain Monitor 연결 실패: {e}")

        # Advanced Emotion Analyzer 연결
        try:
            from echo_engine.emotion.advanced_emotion_analyzer import (
                AdvancedEmotionAnalyzer,
            )

            self.advanced_emotion_analyzer = AdvancedEmotionAnalyzer()
            self.enable_advanced_emotion_analysis = True
            print("   ✅ Advanced Emotion Analyzer 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ Emotion Analyzer 연결 실패: {e}")

        # Echo System Memory 연결
        try:
            from echo_engine.echo_system_memory import EchoSystemMemory

            self.system_memory = EchoSystemMemory()
            self.enable_duplication_prevention = True
            print("   ✅ Echo System Memory 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ System Memory 연결 실패: {e}")

        # Probabilistic Strategy Engine 연결
        try:
            from echo_engine.strategy.probabilistic_strategy_engine import (
                ProbabilisticStrategyEngine,
            )

            self.strategy_engine = ProbabilisticStrategyEngine()
            print("   ✅ Probabilistic Strategy Engine 연결 완료")
            connection_count += 1
        except Exception as e:
            print(f"   ⚠️ Strategy Engine 연결 실패: {e}")

        connection_rate = connection_count / 6 * 100
        print(f"\n🔗 모듈 연결 완료: {connection_count}/6 ({connection_rate:.1f}%)")

        if connection_count >= 4:
            print("✅ 충분한 모듈이 연결되어 고급 기능 활성화!")
        elif connection_count >= 2:
            print("⚠️ 일부 모듈 연결, 기본 통합 기능 사용 가능")
        else:
            print("❌ 연결된 모듈이 부족, 기본 시스템만 사용 가능")

        return connection_count >= 2