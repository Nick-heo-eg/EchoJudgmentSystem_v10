class AdaptiveLearningMemory:
    """GPT-5 수준의 적응적 학습 메모리 시스템

    핵심 기능:
    1. 맥락 인식 기억 형성 - 상황에 맞는 기억 저장 및 조직화
    2. 경험 기반 패턴 학습 - 성공/실패 경험에서 패턴 추출 및 학습
    3. 동적 기억 통합 - 관련 기억들의 자동 통합 및 강화
    4. 도메인 간 지식 전이 - 학습된 패턴의 다른 영역으로의 적용
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/adaptive_memory")
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.config = config or self._default_config()

        # 메모리 저장소
        self.memory_traces: Dict[str, MemoryTrace] = {}
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.consolidation_events: List[ConsolidationEvent] = []

        # 작업 메모리 (임시)
        self.working_memory: deque = deque(
            maxlen=self.config["working_memory_capacity"]
        )

        # 인덱싱 시스템
        self.content_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # 키워드 -> 메모리 ID들
        self.context_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # 컨텍스트 -> 메모리 ID들
        self.pattern_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # 패턴 -> 메모리 ID들

        # 메모리 관리
        self.last_consolidation: float = 0.0
        self.last_cleanup: float = 0.0

        # 성능 추적
        self.retrieval_stats: Dict[str, Any] = defaultdict(int)
        self.learning_stats: Dict[str, Any] = defaultdict(int)

        # 초기화
        self._load_memory_data()
        self._initialize_base_patterns()

        logger.info("AdaptiveLearningMemory initialized with GPT-5 level capabilities")

    def store_experience(
        self,
        experience: Dict[str, Any],
        context: Dict[str, Any],
        outcome: Optional[Dict[str, Any]] = None,
    ) -> str:
        """경험을 기억으로 저장"""

        memory_id = self._generate_memory_id(experience, context)

        # 중요도 결정
        importance = self._assess_importance(experience, context, outcome)

        # 기억 유형 결정
        memory_type = self._determine_memory_type(experience, context)

        # 기억 생성
        memory_trace = MemoryTrace(
            memory_id=memory_id,
            memory_type=memory_type,
            content=experience.copy(),
            context=context.copy(),
            created_at=time.time(),
            last_accessed=time.time(),
            importance=importance,
            strength=self._calculate_initial_strength(importance, outcome),
            decay_rate=self._calculate_decay_rate(importance, memory_type),
            success_correlation=(
                self._calculate_success_correlation(outcome) if outcome else 0.0
            ),
            tags=self._extract_tags(experience, context),
            confidence=context.get("confidence", 0.8),
        )

        # 저장
        self.memory_traces[memory_id] = memory_trace

        # 인덱싱
        self._index_memory(memory_trace)

        # 작업 메모리에 추가
        self.working_memory.append(memory_id)

        # 관련 패턴 학습
        self._learn_from_experience(memory_trace, outcome)

        # 연관 기억 찾기 및 연결
        related_memories = self._find_related_memories(memory_trace)
        memory_trace.related_memories.update(related_memories)

        # 주기적 통합 확인
        if (
            time.time() - self.last_consolidation
            > self.config["consolidation_interval"]
        ):
            self._consolidate_memories()

        logger.info(
            f"Experience stored: {memory_id}, type={memory_type.value}, importance={importance.value}"
        )
        return memory_id

    def retrieve_relevant_memories(
        self, query: Dict[str, Any], context: Dict[str, Any], max_results: int = 10
    ) -> List[Tuple[MemoryTrace, float]]:
        """관련 기억 검색"""

        # 검색 키워드 추출
        keywords = self._extract_query_keywords(query, context)

        # 후보 기억들 수집
        candidate_memories = self._collect_candidate_memories(keywords, context)

        # 관련성 점수 계산
        scored_memories = []
        for memory_id in candidate_memories:
            memory = self.memory_traces.get(memory_id)
            if memory:
                relevance_score = self._calculate_relevance_score(
                    memory, query, context
                )
                if relevance_score > self.config["relevance_threshold"]:
                    scored_memories.append((memory, relevance_score))

        # 정렬 및 필터링
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = scored_memories[:max_results]

        # 접근 기록 업데이트
        for memory, score in top_memories:
            self._update_access_stats(memory, score)

        self.retrieval_stats["total_retrievals"] += 1
        self.retrieval_stats["avg_results"] = (
            self.retrieval_stats["avg_results"]
            * (self.retrieval_stats["total_retrievals"] - 1)
            + len(top_memories)
        ) / self.retrieval_stats["total_retrievals"]

        logger.info(f"Retrieved {len(top_memories)} relevant memories")
        return top_memories

    def learn_from_feedback(
        self, memory_ids: List[str], feedback: Dict[str, Any]
    ) -> None:
        """피드백을 통한 학습"""

        success_score = feedback.get("success_score", 0.5)
        feedback_type = feedback.get("type", "general")

        for memory_id in memory_ids:
            memory = self.memory_traces.get(memory_id)
            if memory:
                # 성공 상관관계 업데이트
                old_correlation = memory.success_correlation
                memory.success_correlation = (old_correlation + success_score) / 2

                # 중요도 조정
                if success_score > 0.8:
                    memory.importance = MemoryImportance(
                        min(5, memory.importance.value + 1)
                    )
                elif success_score < 0.3:
                    memory.importance = MemoryImportance(
                        max(1, memory.importance.value - 1)
                    )

                # 강도 조정
                if success_score > 0.7:
                    memory.strength = min(1.0, memory.strength + 0.1)
                elif success_score < 0.4:
                    memory.strength = max(0.1, memory.strength - 0.05)

                # 관련 패턴 강화/약화
                self._update_patterns_from_feedback(memory, feedback)

        self.learning_stats["feedback_sessions"] += 1
        logger.info(f"Learned from feedback for {len(memory_ids)} memories")

    def extract_learned_patterns(
        self, pattern_types: Optional[List[str]] = None
    ) -> List[LearningPattern]:
        """학습된 패턴 추출"""

        if pattern_types is None:
            return list(self.learning_patterns.values())

        filtered_patterns = []
        for pattern in self.learning_patterns.values():
            if pattern.pattern_type in pattern_types:
                filtered_patterns.append(pattern)

        # 신뢰도 순으로 정렬
        filtered_patterns.sort(key=lambda x: x.confidence_level, reverse=True)

        logger.info(f"Extracted {len(filtered_patterns)} learned patterns")
        return filtered_patterns

    def transfer_knowledge_to_domain(
        self, source_domain: str, target_domain: str, similarity_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """도메인 간 지식 전이"""

        # 소스 도메인의 패턴들 찾기
        source_patterns = []
        for pattern in self.learning_patterns.values():
            if self._pattern_belongs_to_domain(pattern, source_domain):
                source_patterns.append(pattern)

        # 전이 가능한 패턴들 식별
        transferable_patterns = []
        for pattern in source_patterns:
            if pattern.transferability > similarity_threshold:
                transfer_adaptation = self._adapt_pattern_for_domain(
                    pattern, target_domain
                )
                if transfer_adaptation:
                    transferable_patterns.append(
                        {
                            "source_pattern": pattern,
                            "adapted_pattern": transfer_adaptation,
                            "transfer_confidence": pattern.transferability
                            * transfer_adaptation.get("confidence", 0.5),
                        }
                    )

        # 전이된 패턴들을 새 도메인에 등록
        for transfer in transferable_patterns:
            adapted = transfer["adapted_pattern"]
            new_pattern_id = (
                f"transfer_{source_domain}_{target_domain}_{int(time.time())}"
            )

            new_pattern = LearningPattern(
                pattern_id=new_pattern_id,
                pattern_type=adapted["pattern_type"],
                pattern_signature=adapted["pattern_signature"],
                pattern_conditions=adapted["pattern_conditions"],
                success_rate=transfer["source_pattern"].success_rate
                * 0.8,  # 보수적 추정
                confidence_level=transfer["transfer_confidence"],
                transferability=0.7,  # 전이된 패턴의 재전이 가능성
                generalization_level=transfer["source_pattern"].generalization_level
                + 0.1,
            )

            self.learning_patterns[new_pattern_id] = new_pattern

        logger.info(
            f"Transferred {len(transferable_patterns)} patterns from {source_domain} to {target_domain}"
        )
        return transferable_patterns

    def consolidate_memories_now(self) -> Dict[str, Any]:
        """즉시 메모리 통합 실행"""
        return self._consolidate_memories()

    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계 정보"""

        total_memories = len(self.memory_traces)

        # 유형별 분포
        type_distribution = defaultdict(int)
        importance_distribution = defaultdict(int)

        total_strength = 0.0
        high_confidence_count = 0

        for memory in self.memory_traces.values():
            type_distribution[memory.memory_type.value] += 1
            importance_distribution[memory.importance.value] += 1
            total_strength += memory.strength
            if memory.confidence > 0.8:
                high_confidence_count += 1

        avg_strength = total_strength / max(total_memories, 1)

        # 패턴 통계
        pattern_stats = {
            "total_patterns": len(self.learning_patterns),
            "high_confidence_patterns": len(
                [p for p in self.learning_patterns.values() if p.confidence_level > 0.8]
            ),
            "transferable_patterns": len(
                [p for p in self.learning_patterns.values() if p.transferability > 0.7]
            ),
        }

        return {
            "total_memories": total_memories,
            "type_distribution": dict(type_distribution),
            "importance_distribution": dict(importance_distribution),
            "average_strength": avg_strength,
            "high_confidence_ratio": high_confidence_count / max(total_memories, 1),
            "working_memory_usage": len(self.working_memory),
            "pattern_statistics": pattern_stats,
            "retrieval_statistics": dict(self.retrieval_stats),
            "learning_statistics": dict(self.learning_stats),
            "last_consolidation": self.last_consolidation,
            "memory_efficiency": self._calculate_memory_efficiency(),
        }

    # === 내부 메서드들 ===

    def _generate_memory_id(
        self, experience: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """메모리 ID 생성"""
        content_str = json.dumps(experience, sort_keys=True)
        context_str = json.dumps(context, sort_keys=True)
        combined = f"{content_str}_{context_str}_{time.time()}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _assess_importance(
        self,
        experience: Dict[str, Any],
        context: Dict[str, Any],
        outcome: Optional[Dict[str, Any]],
    ) -> MemoryImportance:
        """중요도 평가"""

        # 기본 중요도
        importance_score = 3.0  # MEDIUM

        # 컨텍스트 기반 조정
        if context.get("critical", False):
            importance_score += 2
        if context.get("complexity", 0.5) > 0.8:
            importance_score += 1
        if context.get("novel", False):
            importance_score += 1

        # 결과 기반 조정
        if outcome:
            success_score = outcome.get("success_score", 0.5)
            if success_score > 0.9:
                importance_score += 2
            elif success_score > 0.7:
                importance_score += 1
            elif success_score < 0.3:
                importance_score += 0.5  # 실패도 학습에 중요

        # 경험 유형별 조정
        if experience.get("type") == "breakthrough":
            importance_score += 2
        elif experience.get("type") == "error":
            importance_score += 1

        # 범위 제한
        importance_score = max(1, min(5, importance_score))

        return MemoryImportance(int(importance_score))

    def _determine_memory_type(
        self, experience: Dict[str, Any], context: Dict[str, Any]
    ) -> MemoryType:
        """메모리 유형 결정"""

        experience_type = experience.get("type", "general")

        if experience_type in ["event", "interaction", "experience"]:
            return MemoryType.EPISODIC
        elif experience_type in ["fact", "knowledge", "concept"]:
            return MemoryType.SEMANTIC
        elif experience_type in ["method", "procedure", "technique"]:
            return MemoryType.PROCEDURAL
        elif experience_type in ["learning", "meta", "strategy"]:
            return MemoryType.META
        else:
            # 컨텍스트로 추론
            if context.get("temporary", False):
                return MemoryType.WORKING
            elif "method" in str(experience).lower():
                return MemoryType.PROCEDURAL
            else:
                return MemoryType.EPISODIC  # 기본값

    def _calculate_initial_strength(
        self, importance: MemoryImportance, outcome: Optional[Dict[str, Any]]
    ) -> float:
        """초기 기억 강도 계산"""

        base_strength = importance.value / 5.0  # 0.2 - 1.0

        if outcome:
            success_score = outcome.get("success_score", 0.5)
            emotional_impact = outcome.get("emotional_impact", 0.5)

            # 성공도와 감정적 임팩트가 강도에 영향
            strength = base_strength * (
                0.5 + 0.3 * success_score + 0.2 * emotional_impact
            )
        else:
            strength = base_strength

        return max(0.1, min(1.0, strength))

    def _calculate_decay_rate(
        self, importance: MemoryImportance, memory_type: MemoryType
    ) -> float:
        """망각 속도 계산"""

        # 중요도가 높을수록 망각 속도 낮음
        base_decay = 0.15 - (importance.value - 1) * 0.02

        # 메모리 유형별 조정
        type_adjustments = {
            MemoryType.EPISODIC: 1.0,
            MemoryType.SEMANTIC: 0.8,  # 의미 기억은 더 오래 지속
            MemoryType.PROCEDURAL: 0.7,  # 절차 기억은 가장 오래 지속
            MemoryType.WORKING: 2.0,  # 작업 기억은 빠르게 소멸
            MemoryType.META: 0.6,  # 메타 기억은 매우 오래 지속
        }

        decay_rate = base_decay * type_adjustments.get(memory_type, 1.0)
        return max(0.01, min(0.5, decay_rate))

    def _calculate_success_correlation(self, outcome: Dict[str, Any]) -> float:
        """성공 상관관계 계산"""
        if not outcome:
            return 0.0

        success_score = outcome.get("success_score", 0.5)
        confidence = outcome.get("confidence", 0.7)

        # 신뢰도로 가중평균
        correlation = (success_score - 0.5) * 2 * confidence  # -1 to 1 범위
        return max(-1.0, min(1.0, correlation))

    def _extract_tags(
        self, experience: Dict[str, Any], context: Dict[str, Any]
    ) -> Set[str]:
        """태그 추출"""
        tags = set()

        # 경험에서 태그 추출
        if "tags" in experience:
            tags.update(experience["tags"])

        # 컨텍스트에서 태그 추출
        if "domain" in context:
            tags.add(f"domain_{context['domain']}")
        if "task_type" in context:
            tags.add(f"task_{context['task_type']}")

        # 키워드 기반 태그 생성
        content_str = str(experience)
        keywords = [
            "problem",
            "solution",
            "error",
            "success",
            "failure",
            "creative",
            "analytical",
        ]
        for keyword in keywords:
            if keyword in content_str.lower():
                tags.add(keyword)

        return tags

    def _index_memory(self, memory: MemoryTrace) -> None:
        """메모리 인덱싱"""

        # 내용 기반 인덱싱
        content_words = self._extract_content_words(memory.content)
        for word in content_words:
            self.content_index[word].add(memory.memory_id)

        # 컨텍스트 기반 인덱싱
        for key, value in memory.context.items():
            context_key = f"{key}_{value}"
            self.context_index[context_key].add(memory.memory_id)

        # 태그 기반 인덱싱
        for tag in memory.tags:
            self.content_index[tag].add(memory.memory_id)

    def _extract_content_words(self, content: Dict[str, Any]) -> Set[str]:
        """내용에서 키워드 추출"""
        words = set()

        def extract_from_value(value):
            if isinstance(value, str):
                words.update(value.lower().split())
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)

        extract_from_value(content)

        # 불용어 제거 및 최소 길이 필터링
        stopwords = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "but"}
        filtered_words = {
            word for word in words if len(word) > 2 and word not in stopwords
        }

        return filtered_words

    def _learn_from_experience(
        self, memory: MemoryTrace, outcome: Optional[Dict[str, Any]]
    ) -> None:
        """경험에서 패턴 학습"""

        if not outcome:
            return

        success_score = outcome.get("success_score", 0.5)

        # 성공/실패 패턴 식별
        pattern_signature = self._create_pattern_signature(memory, outcome)
        pattern_type = (
            "success"
            if success_score > 0.7
            else "failure" if success_score < 0.3 else "neutral"
        )

        pattern_id = self._generate_pattern_id(pattern_signature, pattern_type)

        if pattern_id in self.learning_patterns:
            # 기존 패턴 강화
            pattern = self.learning_patterns[pattern_id]
            pattern.occurrence_count += 1
            pattern.success_rate = (
                pattern.success_rate * (pattern.occurrence_count - 1) + success_score
            ) / pattern.occurrence_count
            pattern.last_reinforcement = time.time()

            # 신뢰도 조정
            pattern.confidence_level = min(0.95, pattern.confidence_level + 0.02)
        else:
            # 새 패턴 생성
            new_pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                pattern_signature=pattern_signature,
                pattern_conditions=self._extract_pattern_conditions(memory, outcome),
                success_rate=success_score,
                confidence_level=0.6,
                transferability=self._estimate_transferability(memory, outcome),
                generalization_level=self._estimate_generalization_level(memory),
            )
            self.learning_patterns[pattern_id] = new_pattern

        # 메모리에 패턴 연결
        memory.associated_patterns.add(pattern_id)
        self.pattern_index[pattern_id].add(memory.memory_id)

        self.learning_stats["patterns_learned"] += 1

    def _create_pattern_signature(
        self, memory: MemoryTrace, outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """패턴 서명 생성"""
        signature = {
            "memory_type": memory.memory_type.value,
            "context_domain": memory.context.get("domain", "general"),
            "task_complexity": memory.context.get("complexity", 0.5),
            "approach_type": memory.content.get("approach", "unknown"),
            "key_features": list(memory.tags)[:5],  # 상위 5개 태그
        }

        # 결과 특성 추가
        signature["outcome_type"] = outcome.get("type", "general")
        signature["confidence_range"] = self._discretize_confidence(memory.confidence)

        return signature

    def _discretize_confidence(self, confidence: float) -> str:
        """신뢰도를 구간으로 나누기"""
        if confidence > 0.8:
            return "high"
        elif confidence > 0.6:
            return "medium"
        else:
            return "low"

    def _generate_pattern_id(self, signature: Dict[str, Any], pattern_type: str) -> str:
        """패턴 ID 생성"""
        signature_str = json.dumps(signature, sort_keys=True)
        combined = f"{pattern_type}_{signature_str}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]

    def _extract_pattern_conditions(
        self, memory: MemoryTrace, outcome: Dict[str, Any]
    ) -> List[str]:
        """패턴 발생 조건 추출"""
        conditions = []

        # 컨텍스트 조건
        if memory.context.get("complexity", 0) > 0.7:
            conditions.append("high_complexity")
        if memory.context.get("pressure", 0) > 0.6:
            conditions.append("high_pressure")
        if memory.context.get("novel", False):
            conditions.append("novel_situation")

        # 메모리 특성 조건
        if memory.importance.value >= 4:
            conditions.append("high_importance")
        if memory.confidence > 0.8:
            conditions.append("high_confidence")

        # 결과 기반 조건
        if outcome.get("unexpected", False):
            conditions.append("unexpected_outcome")

        return conditions

    def _estimate_transferability(
        self, memory: MemoryTrace, outcome: Dict[str, Any]
    ) -> float:
        """전이 가능성 추정"""

        # 기본 전이 가능성
        base_transferability = 0.5

        # 일반성이 높은 패턴은 전이 가능성 높음
        if "general" in memory.tags:
            base_transferability += 0.2
        if "principle" in memory.tags:
            base_transferability += 0.3

        # 도메인 특화적인 경우 전이 가능성 낮음
        if "specific" in memory.tags:
            base_transferability -= 0.2

        # 성공한 경험일수록 전이 가능성 높음
        success_score = outcome.get("success_score", 0.5)
        if success_score > 0.8:
            base_transferability += 0.2

        return max(0.1, min(0.9, base_transferability))

    def _estimate_generalization_level(self, memory: MemoryTrace) -> float:
        """일반화 수준 추정"""

        generalization = 0.3  # 기본값

        # 추상적 개념일수록 일반화 수준 높음
        if memory.memory_type == MemoryType.SEMANTIC:
            generalization += 0.2
        elif memory.memory_type == MemoryType.META:
            generalization += 0.3

        # 복잡도가 적당한 경우 일반화하기 좋음
        complexity = memory.context.get("complexity", 0.5)
        if 0.4 <= complexity <= 0.7:
            generalization += 0.2

        return max(0.1, min(0.8, generalization))

    def _find_related_memories(
        self, memory: MemoryTrace, max_related: int = 5
    ) -> Set[str]:
        """관련 기억 찾기"""

        related = set()

        # 태그 기반 연관성
        for tag in memory.tags:
            related.update(self.content_index[tag])

        # 컨텍스트 기반 연관성
        for key, value in memory.context.items():
            context_key = f"{key}_{value}"
            related.update(self.context_index[context_key])

        # 자기 제외
        related.discard(memory.memory_id)

        # 관련성 점수 계산 및 상위 선택
        scored_related = []
        for related_id in related:
            related_memory = self.memory_traces.get(related_id)
            if related_memory:
                similarity = self._calculate_memory_similarity(memory, related_memory)
                if similarity > 0.3:  # 임계값
                    scored_related.append((related_id, similarity))

        scored_related.sort(key=lambda x: x[1], reverse=True)
        return {item[0] for item in scored_related[:max_related]}

    def _calculate_memory_similarity(
        self, memory1: MemoryTrace, memory2: MemoryTrace
    ) -> float:
        """메모리 간 유사도 계산"""

        # 태그 유사도
        tag_intersection = len(memory1.tags & memory2.tags)
        tag_union = len(memory1.tags | memory2.tags)
        tag_similarity = tag_intersection / max(tag_union, 1)

        # 컨텍스트 유사도
        context_matches = 0
        context_total = 0
        for key in set(memory1.context.keys()) | set(memory2.context.keys()):
            context_total += 1
            if memory1.context.get(key) == memory2.context.get(key):
                context_matches += 1
        context_similarity = context_matches / max(context_total, 1)

        # 메모리 유형 유사도
        type_similarity = 1.0 if memory1.memory_type == memory2.memory_type else 0.3

        # 가중 평균
        overall_similarity = (
            tag_similarity * 0.4 + context_similarity * 0.4 + type_similarity * 0.2
        )

        return overall_similarity

    # === 검색 관련 메서드들 ===

    def _extract_query_keywords(
        self, query: Dict[str, Any], context: Dict[str, Any]
    ) -> Set[str]:
        """쿼리에서 키워드 추출"""
        keywords = set()

        # 쿼리 내용에서 추출
        keywords.update(self._extract_content_words(query))

        # 컨텍스트에서 추출
        for key, value in context.items():
            if isinstance(value, str):
                keywords.add(value.lower())
            keywords.add(f"{key}_{value}")

        return keywords

    def _collect_candidate_memories(
        self, keywords: Set[str], context: Dict[str, Any]
    ) -> Set[str]:
        """후보 기억들 수집"""
        candidates = set()

        # 키워드 기반 후보 수집
        for keyword in keywords:
            candidates.update(self.content_index.get(keyword, set()))

        # 컨텍스트 기반 후보 추가
        for key, value in context.items():
            context_key = f"{key}_{value}"
            candidates.update(self.context_index.get(context_key, set()))

        # 작업 메모리의 최근 기억들 포함
        candidates.update(self.working_memory)

        return candidates

    def _calculate_relevance_score(
        self, memory: MemoryTrace, query: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """관련성 점수 계산"""

        score = 0.0

        # 키워드 매칭 점수
        query_keywords = self._extract_query_keywords(query, context)
        memory_keywords = self._extract_content_words(memory.content) | memory.tags

        keyword_overlap = len(query_keywords & memory_keywords)
        keyword_total = len(query_keywords | memory_keywords)
        keyword_score = keyword_overlap / max(keyword_total, 1)
        score += keyword_score * 0.3

        # 컨텍스트 매칭 점수
        context_matches = 0
        context_total = 0
        for key, value in context.items():
            if key in memory.context:
                context_total += 1
                if memory.context[key] == value:
                    context_matches += 1
        context_score = (
            context_matches / max(context_total, 1) if context_total > 0 else 0.5
        )
        score += context_score * 0.3

        # 성공 상관관계 점수
        success_score = (memory.success_correlation + 1) / 2  # -1~1 → 0~1
        score += success_score * 0.2

        # 기억 강도 점수
        score += memory.strength * 0.1

        # 시간 가중치 (최근일수록 높음)
        time_weight = math.exp(
            -(time.time() - memory.last_accessed) / (86400 * 30)
        )  # 30일 기준
        score += time_weight * 0.1

        return score

    def _update_access_stats(self, memory: MemoryTrace, relevance_score: float) -> None:
        """접근 통계 업데이트"""
        memory.last_accessed = time.time()
        memory.access_count += 1

        # 관련성이 높을수록 강도 증가
        if relevance_score > 0.8:
            memory.strength = min(1.0, memory.strength + 0.02)

    # === 통합 관련 메서드들 ===

    def _consolidate_memories(self) -> Dict[str, Any]:
        """메모리 통합"""

        consolidation_start = time.time()

        # 약한 기억들 정리
        weak_memories_removed = self._cleanup_weak_memories()

        # 유사한 기억들 병합
        merged_memories = self._merge_similar_memories()

        # 중요한 기억들 강화
        strengthened_memories = self._strengthen_important_memories()

        # 패턴 업데이트
        updated_patterns = self._update_learning_patterns()

        # 통합 이벤트 기록
        consolidation_event = ConsolidationEvent(
            event_id=f"consolidation_{int(time.time())}",
            timestamp=consolidation_start,
            consolidation_type="comprehensive",
            source_memories=list(self.memory_traces.keys()),
            target_memories=[],
            consolidation_outcome={
                "weak_removed": weak_memories_removed,
                "merged": merged_memories,
                "strengthened": strengthened_memories,
                "patterns_updated": updated_patterns,
            },
            effectiveness_score=self._calculate_consolidation_effectiveness(),
        )

        self.consolidation_events.append(consolidation_event)
        self.last_consolidation = time.time()

        logger.info(
            f"Memory consolidation completed: {len(consolidation_event.consolidation_outcome)} operations"
        )

        return consolidation_event.consolidation_outcome

    def _cleanup_weak_memories(self) -> int:
        """약한 기억들 정리"""

        removed_count = 0
        current_time = time.time()

        memories_to_remove = []
        for memory_id, memory in self.memory_traces.items():
            # 자연 망각 적용
            time_since_last_access = current_time - memory.last_accessed
            decay_factor = math.exp(
                -memory.decay_rate * time_since_last_access / 86400
            )  # 일 단위
            memory.strength *= decay_factor

            # 매우 약한 기억 제거
            if memory.strength < 0.1 and memory.importance.value <= 2:
                memories_to_remove.append(memory_id)

        for memory_id in memories_to_remove:
            self._remove_memory(memory_id)
            removed_count += 1

        return removed_count

    def _merge_similar_memories(self) -> int:
        """유사한 기억들 병합"""

        merged_count = 0
        processed = set()

        for memory_id, memory in list(self.memory_traces.items()):
            if memory_id in processed:
                continue

            # 유사한 기억들 찾기
            similar_memories = []
            for other_id, other_memory in self.memory_traces.items():
                if other_id != memory_id and other_id not in processed:
                    similarity = self._calculate_memory_similarity(memory, other_memory)
                    if similarity > 0.8:  # 매우 유사한 경우
                        similar_memories.append((other_id, other_memory, similarity))

            if similar_memories:
                # 가장 유사한 것과 병합
                best_match = max(similar_memories, key=lambda x: x[2])
                merged_memory = self._merge_two_memories(memory, best_match[1])

                # 기존 기억들 제거하고 병합된 기억 추가
                self._remove_memory(memory_id)
                self._remove_memory(best_match[0])
                self.memory_traces[merged_memory.memory_id] = merged_memory
                self._index_memory(merged_memory)

                processed.add(memory_id)
                processed.add(best_match[0])
                merged_count += 1

        return merged_count

    def _merge_two_memories(
        self, memory1: MemoryTrace, memory2: MemoryTrace
    ) -> MemoryTrace:
        """두 기억 병합"""

        # 더 강한 기억을 기반으로 병합
        if memory1.strength >= memory2.strength:
            base_memory = memory1
            merge_memory = memory2
        else:
            base_memory = memory2
            merge_memory = memory1

        merged = MemoryTrace(
            memory_id=f"merged_{base_memory.memory_id}_{merge_memory.memory_id}",
            memory_type=base_memory.memory_type,
            content={**base_memory.content, **merge_memory.content},
            context={**base_memory.context, **merge_memory.context},
            created_at=min(base_memory.created_at, merge_memory.created_at),
            last_accessed=max(base_memory.last_accessed, merge_memory.last_accessed),
            access_count=base_memory.access_count + merge_memory.access_count,
            importance=MemoryImportance(
                max(base_memory.importance.value, merge_memory.importance.value)
            ),
            strength=(base_memory.strength + merge_memory.strength)
            / 2
            * 1.1,  # 병합 보너스
            decay_rate=min(base_memory.decay_rate, merge_memory.decay_rate),
            related_memories=base_memory.related_memories
            | merge_memory.related_memories,
            associated_patterns=base_memory.associated_patterns
            | merge_memory.associated_patterns,
            success_correlation=(
                base_memory.success_correlation + merge_memory.success_correlation
            )
            / 2,
            tags=base_memory.tags | merge_memory.tags,
            confidence=(base_memory.confidence + merge_memory.confidence) / 2,
        )

        return merged

    def _strengthen_important_memories(self) -> int:
        """중요한 기억들 강화"""

        strengthened_count = 0

        for memory in self.memory_traces.values():
            if memory.importance.value >= 4:  # HIGH 또는 CRITICAL
                old_strength = memory.strength
                memory.strength = min(1.0, memory.strength + 0.05)
                if memory.strength > old_strength:
                    strengthened_count += 1

        return strengthened_count

    def _update_learning_patterns(self) -> int:
        """학습 패턴 업데이트"""

        updated_count = 0
        current_time = time.time()

        for pattern in self.learning_patterns.values():
            # 오래된 패턴의 신뢰도 감소
            time_since_reinforcement = current_time - pattern.last_reinforcement
            if time_since_reinforcement > 86400 * 7:  # 7일 이상
                old_confidence = pattern.confidence_level
                pattern.confidence_level *= 0.95
                if pattern.confidence_level != old_confidence:
                    updated_count += 1

        return updated_count

    def _remove_memory(self, memory_id: str) -> None:
        """메모리 제거"""

        if memory_id not in self.memory_traces:
            return

        memory = self.memory_traces[memory_id]

        # 인덱스에서 제거
        for word in self._extract_content_words(memory.content) | memory.tags:
            self.content_index[word].discard(memory_id)

        for key, value in memory.context.items():
            context_key = f"{key}_{value}"
            self.context_index[context_key].discard(memory_id)

        for pattern_id in memory.associated_patterns:
            self.pattern_index[pattern_id].discard(memory_id)

        # 메모리 제거
        del self.memory_traces[memory_id]

    def _calculate_consolidation_effectiveness(self) -> float:
        """통합 효과성 계산"""
        return 0.8  # 간소화된 구현

    def _calculate_memory_efficiency(self) -> float:
        """메모리 효율성 계산"""

        if not self.memory_traces:
            return 0.0

        total_strength = sum(memory.strength for memory in self.memory_traces.values())
        avg_strength = total_strength / len(self.memory_traces)

        high_confidence_ratio = len(
            [m for m in self.memory_traces.values() if m.confidence > 0.8]
        ) / len(self.memory_traces)

        efficiency = (avg_strength + high_confidence_ratio) / 2
        return efficiency

    # === 피드백 및 패턴 업데이트 메서드들 ===

    def _update_patterns_from_feedback(
        self, memory: MemoryTrace, feedback: Dict[str, Any]
    ) -> None:
        """피드백으로부터 패턴 업데이트"""

        success_score = feedback.get("success_score", 0.5)

        for pattern_id in memory.associated_patterns:
            pattern = self.learning_patterns.get(pattern_id)
            if pattern:
                # 성공률 업데이트
                pattern.occurrence_count += 1
                pattern.success_rate = (
                    pattern.success_rate * (pattern.occurrence_count - 1)
                    + success_score
                ) / pattern.occurrence_count

                # 신뢰도 조정
                if success_score > 0.8:
                    pattern.confidence_level = min(
                        0.95, pattern.confidence_level + 0.03
                    )
                elif success_score < 0.3:
                    pattern.confidence_level = max(0.1, pattern.confidence_level - 0.05)

                pattern.last_reinforcement = time.time()

    # === 도메인 전이 메서드들 ===

    def _pattern_belongs_to_domain(self, pattern: LearningPattern, domain: str) -> bool:
        """패턴이 특정 도메인에 속하는지 확인"""
        return pattern.pattern_signature.get("context_domain") == domain

    def _adapt_pattern_for_domain(
        self, pattern: LearningPattern, target_domain: str
    ) -> Optional[Dict[str, Any]]:
        """패턴을 대상 도메인에 맞게 적응"""

        if pattern.transferability < 0.5:
            return None

        adapted = {
            "pattern_type": pattern.pattern_type,
            "pattern_signature": pattern.pattern_signature.copy(),
            "pattern_conditions": pattern.pattern_conditions.copy(),
            "confidence": pattern.transferability * 0.8,
        }

        # 도메인 특화 적응
        adapted["pattern_signature"]["context_domain"] = target_domain

        return adapted

    # === 데이터 저장/로드 ===

    def _load_memory_data(self) -> None:
        """메모리 데이터 로드 (간소화)"""
        pass  # 실제 구현에서는 파일에서 로드

    def _initialize_base_patterns(self) -> None:
        """기본 패턴 초기화 (간소화)"""
        pass  # 실제 구현에서는 기본 학습 패턴들 로드

    def _default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "working_memory_capacity": 20,
            "consolidation_interval": 3600,  # 1시간
            "relevance_threshold": 0.3,
            "similarity_threshold": 0.8,
            "max_memory_traces": 10000,
            "cleanup_interval": 86400,  # 24시간
            "pattern_confidence_threshold": 0.6,
        }