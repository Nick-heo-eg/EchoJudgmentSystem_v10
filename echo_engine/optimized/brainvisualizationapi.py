class BrainVisualizationAPI:
    """🧠 뇌 시각화 API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Echo 컴포넌트들
        self.neural_atlas_builder = None
        self.consciousness_analyzer = None
        self.emotion_mapper = None
        self.resonance_mapper = None

        # 시각화 설정
        self.brain_template = self._initialize_brain_template()
        self.color_palettes = self._initialize_color_palettes()
        self.visualization_cache = {}

        # 뇌 영역 좌표 매핑
        self.brain_coordinates = self._initialize_brain_coordinates()

        # 활성 시각화 세션
        self.active_sessions = {}

        print("🧠 Brain Visualization API 초기화 완료")

    def initialize_components(self, **components):
        """Echo 컴포넌트 초기화"""
        self.neural_atlas_builder = components.get("neural_atlas_builder")
        self.consciousness_analyzer = components.get("consciousness_analyzer")
        self.emotion_mapper = components.get("emotion_mapper")
        self.resonance_mapper = components.get("resonance_mapper")

        print(
            f"🔗 {len([c for c in [self.neural_atlas_builder, self.consciousness_analyzer, self.emotion_mapper, self.resonance_mapper] if c])} 개 컴포넌트 연결 완료"
        )

    def _initialize_brain_template(self) -> Dict[str, Any]:
        """뇌 템플릿 초기화"""
        return {
            "regions": {
                # 전두엽 (Frontal Lobe)
                "prefrontal_cortex": {
                    "position": (0.0, 0.4, 0.3),
                    "size": 0.2,
                    "color": "#FF6B6B",
                },
                "motor_cortex": {
                    "position": (0.0, 0.1, 0.4),
                    "size": 0.15,
                    "color": "#4ECDC4",
                },
                "broca_area": {
                    "position": (-0.3, 0.2, 0.2),
                    "size": 0.1,
                    "color": "#45B7D1",
                },
                # 두정엽 (Parietal Lobe)
                "somatosensory_cortex": {
                    "position": (0.0, -0.1, 0.4),
                    "size": 0.15,
                    "color": "#96CEB4",
                },
                "posterior_parietal": {
                    "position": (0.0, -0.3, 0.3),
                    "size": 0.12,
                    "color": "#FFEAA7",
                },
                # 측두엽 (Temporal Lobe)
                "auditory_cortex": {
                    "position": (-0.4, 0.0, 0.1),
                    "size": 0.1,
                    "color": "#DDA0DD",
                },
                "wernicke_area": {
                    "position": (-0.35, -0.2, 0.1),
                    "size": 0.08,
                    "color": "#F7DC6F",
                },
                "hippocampus": {
                    "position": (-0.25, -0.1, -0.1),
                    "size": 0.06,
                    "color": "#85C1E9",
                },
                # 후두엽 (Occipital Lobe)
                "visual_cortex": {
                    "position": (0.0, -0.4, 0.2),
                    "size": 0.12,
                    "color": "#F8C471",
                },
                # 뇌간 (Brainstem)
                "thalamus": {
                    "position": (0.0, 0.0, 0.0),
                    "size": 0.08,
                    "color": "#CD6155",
                },
                "hypothalamus": {
                    "position": (0.0, 0.1, -0.05),
                    "size": 0.05,
                    "color": "#AF7AC5",
                },
                "brainstem": {
                    "position": (0.0, 0.0, -0.3),
                    "size": 0.06,
                    "color": "#5DADE2",
                },
                # 소뇌 (Cerebellum)
                "cerebellum": {
                    "position": (0.0, -0.3, -0.2),
                    "size": 0.18,
                    "color": "#58D68D",
                },
                # 변연계 (Limbic System)
                "amygdala": {
                    "position": (-0.2, 0.0, -0.05),
                    "size": 0.04,
                    "color": "#EC7063",
                },
                "cingulate_cortex": {
                    "position": (0.0, 0.0, 0.2),
                    "size": 0.1,
                    "color": "#F4D03F",
                },
            },
            "connections": [
                # 주요 신경 연결
                {"from": "prefrontal_cortex", "to": "motor_cortex", "strength": 0.8},
                {"from": "somatosensory_cortex", "to": "motor_cortex", "strength": 0.9},
                {"from": "thalamus", "to": "prefrontal_cortex", "strength": 0.7},
                {"from": "hippocampus", "to": "prefrontal_cortex", "strength": 0.6},
                {"from": "amygdala", "to": "prefrontal_cortex", "strength": 0.5},
                {"from": "visual_cortex", "to": "posterior_parietal", "strength": 0.8},
                {"from": "auditory_cortex", "to": "wernicke_area", "strength": 0.9},
                {"from": "broca_area", "to": "wernicke_area", "strength": 0.7},
            ],
        }

    def _initialize_color_palettes(self) -> Dict[str, List[str]]:
        """색상 팔레트 초기화"""
        return {
            "emotion_flow": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
            "consciousness_levels": [
                "#2C3E50",
                "#34495E",
                "#7F8C8D",
                "#BDC3C7",
                "#ECF0F1",
                "#F8F9FA",
            ],
            "signature_resonance": [
                "#E74C3C",
                "#F39C12",
                "#F1C40F",
                "#27AE60",
                "#3498DB",
                "#9B59B6",
            ],
            "neural_activity": [
                "#000080",
                "#0066CC",
                "#00AAFF",
                "#66CCFF",
                "#CCEEff",
                "#FFFFFF",
            ],
            "brain_structure": [
                "#8B4513",
                "#D2691E",
                "#DEB887",
                "#F4A460",
                "#FAD5A5",
                "#FFF8DC",
            ],
        }

    def _initialize_brain_coordinates(self) -> Dict[str, BrainCoordinate]:
        """뇌 영역 좌표 매핑 초기화"""
        coordinates = {}

        # 전두엽 영역들
        coordinates["prefrontal_cortex"] = BrainCoordinate(
            0.0, 0.4, 0.3, "prefrontal_cortex", "bilateral"
        )
        coordinates["motor_cortex"] = BrainCoordinate(
            0.0, 0.1, 0.4, "motor_cortex", "bilateral"
        )
        coordinates["broca_area"] = BrainCoordinate(
            -0.3, 0.2, 0.2, "broca_area", "left"
        )

        # 두정엽 영역들
        coordinates["somatosensory_cortex"] = BrainCoordinate(
            0.0, -0.1, 0.4, "somatosensory_cortex", "bilateral"
        )
        coordinates["posterior_parietal"] = BrainCoordinate(
            0.0, -0.3, 0.3, "posterior_parietal", "bilateral"
        )

        # 측두엽 영역들
        coordinates["auditory_cortex"] = BrainCoordinate(
            -0.4, 0.0, 0.1, "auditory_cortex", "bilateral"
        )
        coordinates["wernicke_area"] = BrainCoordinate(
            -0.35, -0.2, 0.1, "wernicke_area", "left"
        )
        coordinates["hippocampus"] = BrainCoordinate(
            -0.25, -0.1, -0.1, "hippocampus", "bilateral"
        )

        # 후두엽 영역들
        coordinates["visual_cortex"] = BrainCoordinate(
            0.0, -0.4, 0.2, "visual_cortex", "bilateral"
        )

        # 피질하 구조들
        coordinates["thalamus"] = BrainCoordinate(
            0.0, 0.0, 0.0, "thalamus", "bilateral"
        )
        coordinates["hypothalamus"] = BrainCoordinate(
            0.0, 0.1, -0.05, "hypothalamus", "bilateral"
        )
        coordinates["amygdala"] = BrainCoordinate(
            -0.2, 0.0, -0.05, "amygdala", "bilateral"
        )
        coordinates["cerebellum"] = BrainCoordinate(
            0.0, -0.3, -0.2, "cerebellum", "bilateral"
        )

        return coordinates

    def create_visualization(
        self, request: BrainVisualizationRequest
    ) -> BrainVisualizationResponse:
        """뇌 시각화 생성"""
        start_time = datetime.now()
        request_id = (
            f"viz_{int(start_time.timestamp())}_{request.visualization_type.value}"
        )

        try:
            # 시각화 타입별 처리
            if request.visualization_type == VisualizationType.BRAIN_STRUCTURE:
                visualization_data, elements = (
                    self._create_brain_structure_visualization(request)
                )
            elif request.visualization_type == VisualizationType.NEURAL_ACTIVITY:
                visualization_data, elements = (
                    self._create_neural_activity_visualization(request)
                )
            elif request.visualization_type == VisualizationType.EMOTION_FLOW:
                visualization_data, elements = self._create_emotion_flow_visualization(
                    request
                )
            elif request.visualization_type == VisualizationType.CONSCIOUSNESS_MAP:
                visualization_data, elements = (
                    self._create_consciousness_map_visualization(request)
                )
            elif request.visualization_type == VisualizationType.SIGNATURE_RESONANCE:
                visualization_data, elements = (
                    self._create_signature_resonance_visualization(request)
                )
            else:
                visualization_data, elements = self._create_default_visualization(
                    request
                )

            # 렌더링 포맷 적용
            rendered_data = self._apply_render_format(
                visualization_data, elements, request.render_format
            )

            generation_time = (datetime.now() - start_time).total_seconds() * 1000

            response = BrainVisualizationResponse(
                request_id=request_id,
                timestamp=datetime.now(),
                visualization_data=rendered_data,
                render_format=request.render_format,
                elements=elements,
                metadata={
                    "signature_context": request.signature_context,
                    "resolution": request.resolution,
                    "element_count": len(elements),
                    "visualization_type": request.visualization_type.value,
                },
                generation_time_ms=generation_time,
            )

            # 캐시에 저장
            if not request.real_time:
                self.visualization_cache[request_id] = response

            return response

        except Exception as e:
            self.logger.error(f"시각화 생성 실패: {e}")
            # 오류 시 기본 시각화 반환
            return self._create_error_visualization(request_id, str(e))

    def _create_brain_structure_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """뇌 구조 시각화 생성"""
        elements = []

        # 기본 뇌 구조 시각화
        for region_name, region_data in self.brain_template["regions"].items():
            element = VisualizationElement(
                element_id=f"region_{region_name}",
                element_type="region",
                position=region_data["position"],
                size=region_data["size"],
                color=region_data["color"],
                intensity=0.8,
                metadata={"region_name": region_name, "type": "brain_region"},
            )
            elements.append(element)

        # 신경 연결 추가
        for i, connection in enumerate(self.brain_template["connections"]):
            from_region = self.brain_template["regions"].get(connection["from"])
            to_region = self.brain_template["regions"].get(connection["to"])

            if from_region and to_region:
                # 연결선 중점 계산
                mid_point = (
                    (from_region["position"][0] + to_region["position"][0]) / 2,
                    (from_region["position"][1] + to_region["position"][1]) / 2,
                    (from_region["position"][2] + to_region["position"][2]) / 2,
                )

                element = VisualizationElement(
                    element_id=f"connection_{i}",
                    element_type="connection",
                    position=mid_point,
                    size=0.02,
                    color="#CCCCCC",
                    intensity=connection["strength"],
                    metadata={
                        "from": connection["from"],
                        "to": connection["to"],
                        "strength": connection["strength"],
                    },
                )
                elements.append(element)

        visualization_data = {
            "type": "brain_structure",
            "regions": len(self.brain_template["regions"]),
            "connections": len(self.brain_template["connections"]),
            "signature": request.signature_context,
        }

        return visualization_data, elements

    def _create_neural_activity_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """신경 활동 시각화 생성"""
        elements = []

        # 기본 뇌 구조에 활동 데이터 오버레이
        for region_name, region_data in self.brain_template["regions"].items():
            # 모의 신경 활동 데이터 생성
            activity_level = np.random.uniform(0.2, 1.0)

            # 활동 수준에 따른 색상 변화
            base_color = region_data["color"]
            intensity_color = self._apply_activity_intensity(base_color, activity_level)

            element = VisualizationElement(
                element_id=f"activity_{region_name}",
                element_type="region",
                position=region_data["position"],
                size=region_data["size"]
                * (0.8 + 0.4 * activity_level),  # 활동에 따른 크기 변화
                color=intensity_color,
                intensity=activity_level,
                metadata={
                    "region_name": region_name,
                    "activity_level": activity_level,
                    "type": "neural_activity",
                },
            )
            elements.append(element)

        # 활성 연결 시각화
        for i, connection in enumerate(self.brain_template["connections"]):
            activity_strength = np.random.uniform(0.1, connection["strength"])

            from_region = self.brain_template["regions"].get(connection["from"])
            to_region = self.brain_template["regions"].get(connection["to"])

            if from_region and to_region:
                mid_point = (
                    (from_region["position"][0] + to_region["position"][0]) / 2,
                    (from_region["position"][1] + to_region["position"][1]) / 2,
                    (from_region["position"][2] + to_region["position"][2]) / 2,
                )

                element = VisualizationElement(
                    element_id=f"active_connection_{i}",
                    element_type="connection",
                    position=mid_point,
                    size=0.02 * (1 + activity_strength),
                    color=self._activity_color(activity_strength),
                    intensity=activity_strength,
                    metadata={
                        "from": connection["from"],
                        "to": connection["to"],
                        "activity_strength": activity_strength,
                        "type": "active_connection",
                    },
                )
                elements.append(element)

        visualization_data = {
            "type": "neural_activity",
            "timestamp": datetime.now().isoformat(),
            "average_activity": np.mean(
                [e.intensity for e in elements if e.element_type == "region"]
            ),
            "signature": request.signature_context,
        }

        return visualization_data, elements

    def _create_emotion_flow_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """감정 흐름 시각화 생성"""
        elements = []

        # 감정 관련 뇌 영역들
        emotion_regions = [
            "amygdala",
            "hippocampus",
            "prefrontal_cortex",
            "cingulate_cortex",
            "hypothalamus",
        ]
        emotion_colors = self.color_palettes["emotion_flow"]

        for i, region_name in enumerate(emotion_regions):
            if region_name in self.brain_template["regions"]:
                region_data = self.brain_template["regions"][region_name]
                emotion_intensity = np.random.uniform(0.3, 1.0)

                element = VisualizationElement(
                    element_id=f"emotion_{region_name}",
                    element_type="region",
                    position=region_data["position"],
                    size=region_data["size"] * (1 + 0.5 * emotion_intensity),
                    color=emotion_colors[i % len(emotion_colors)],
                    intensity=emotion_intensity,
                    metadata={
                        "region_name": region_name,
                        "emotion_type": ["joy", "fear", "anger", "sadness", "surprise"][
                            i % 5
                        ],
                        "emotion_intensity": emotion_intensity,
                    },
                )
                elements.append(element)

        # 감정 흐름 경로 시각화
        emotion_pathways = [
            ("amygdala", "prefrontal_cortex"),
            ("hippocampus", "amygdala"),
            ("hypothalamus", "cingulate_cortex"),
        ]

        for i, (from_region, to_region) in enumerate(emotion_pathways):
            from_data = self.brain_template["regions"].get(from_region)
            to_data = self.brain_template["regions"].get(to_region)

            if from_data and to_data:
                flow_strength = np.random.uniform(0.4, 0.9)

                # 흐름 방향을 나타내는 여러 점들
                for j in range(3):
                    t = (j + 1) / 4  # 0.25, 0.5, 0.75
                    flow_point = (
                        from_data["position"][0]
                        + t * (to_data["position"][0] - from_data["position"][0]),
                        from_data["position"][1]
                        + t * (to_data["position"][1] - from_data["position"][1]),
                        from_data["position"][2]
                        + t * (to_data["position"][2] - from_data["position"][2]),
                    )

                    element = VisualizationElement(
                        element_id=f"flow_{i}_{j}",
                        element_type="flow",
                        position=flow_point,
                        size=0.03 * flow_strength,
                        color=emotion_colors[i % len(emotion_colors)],
                        intensity=flow_strength * (1 - 0.2 * j),  # 점진적 감소
                        metadata={
                            "pathway": f"{from_region} -> {to_region}",
                            "flow_strength": flow_strength,
                            "flow_position": t,
                        },
                    )
                    elements.append(element)

        visualization_data = {
            "type": "emotion_flow",
            "emotion_regions": len(emotion_regions),
            "flow_pathways": len(emotion_pathways),
            "average_emotion_intensity": np.mean(
                [e.intensity for e in elements if e.element_type == "region"]
            ),
            "signature": request.signature_context,
        }

        return visualization_data, elements

    def _create_consciousness_map_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """의식 맵 시각화 생성"""
        elements = []

        # 의식 수준별 색상
        consciousness_colors = self.color_palettes["consciousness_levels"]

        # 의식과 관련된 뇌 영역들과 수준
        consciousness_mapping = {
            "brainstem": 0,  # 무의식
            "thalamus": 1,  # 전의식
            "cingulate_cortex": 2,  # 의식
            "prefrontal_cortex": 3,  # 자각
            "posterior_parietal": 4,  # 고차 인식
            "motor_cortex": 2,  # 의식 (운동 제어)
        }

        for region_name, consciousness_level in consciousness_mapping.items():
            if region_name in self.brain_template["regions"]:
                region_data = self.brain_template["regions"][region_name]

                # 의식 수준에 따른 활성도
                consciousness_intensity = (consciousness_level + 1) / 6  # 0~1 정규화

                element = VisualizationElement(
                    element_id=f"consciousness_{region_name}",
                    element_type="region",
                    position=region_data["position"],
                    size=region_data["size"] * (0.7 + 0.6 * consciousness_intensity),
                    color=consciousness_colors[consciousness_level],
                    intensity=consciousness_intensity,
                    metadata={
                        "region_name": region_name,
                        "consciousness_level": consciousness_level,
                        "consciousness_name": [
                            "Unconscious",
                            "Preconscious",
                            "Conscious",
                            "Self-aware",
                            "Meta-conscious",
                            "Hyperconscious",
                        ][consciousness_level],
                        "type": "consciousness_region",
                    },
                )
                elements.append(element)

        # 의식 흐름 연결
        consciousness_flows = [
            ("brainstem", "thalamus", 0.6),
            ("thalamus", "cingulate_cortex", 0.7),
            ("cingulate_cortex", "prefrontal_cortex", 0.8),
            ("prefrontal_cortex", "posterior_parietal", 0.9),
        ]

        for i, (from_region, to_region, flow_strength) in enumerate(
            consciousness_flows
        ):
            from_data = self.brain_template["regions"].get(from_region)
            to_data = self.brain_template["regions"].get(to_region)

            if from_data and to_data:
                mid_point = (
                    (from_data["position"][0] + to_data["position"][0]) / 2,
                    (from_data["position"][1] + to_data["position"][1]) / 2,
                    (from_data["position"][2] + to_data["position"][2]) / 2,
                )

                element = VisualizationElement(
                    element_id=f"consciousness_flow_{i}",
                    element_type="flow",
                    position=mid_point,
                    size=0.04 * flow_strength,
                    color="#FFD700",  # 황금색으로 의식 흐름 표현
                    intensity=flow_strength,
                    metadata={
                        "from": from_region,
                        "to": to_region,
                        "consciousness_flow": flow_strength,
                        "type": "consciousness_connection",
                    },
                )
                elements.append(element)

        visualization_data = {
            "type": "consciousness_map",
            "consciousness_regions": len(consciousness_mapping),
            "consciousness_flows": len(consciousness_flows),
            "average_consciousness_level": np.mean(
                list(consciousness_mapping.values())
            ),
            "signature": request.signature_context,
        }

        return visualization_data, elements

    def _create_signature_resonance_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """시그니처 공명 시각화 생성"""
        elements = []

        # 시그니처별 특성화된 뇌 영역들
        signature_brain_mapping = {
            "aurora": ["amygdala", "hippocampus", "cingulate_cortex"],  # 감정적, 창조적
            "phoenix": [
                "prefrontal_cortex",
                "motor_cortex",
                "posterior_parietal",
            ],  # 변화지향, 실행력
            "sage": [
                "prefrontal_cortex",
                "visual_cortex",
                "wernicke_area",
            ],  # 분석적, 지혜
            "companion": ["cingulate_cortex", "amygdala", "broca_area"],  # 공감적, 소통
        }

        # 현재 시그니처 또는 기본값
        current_signature = (
            request.signature_context.lower() if request.signature_context else "aurora"
        )
        signature_regions = signature_brain_mapping.get(
            current_signature, signature_brain_mapping["aurora"]
        )

        # 시그니처 색상
        signature_colors = self.color_palettes["signature_resonance"]
        signature_color = signature_colors[
            list(signature_brain_mapping.keys()).index(current_signature)
            % len(signature_colors)
        ]

        # 시그니처 특화 영역 시각화
        for i, region_name in enumerate(signature_regions):
            if region_name in self.brain_template["regions"]:
                region_data = self.brain_template["regions"][region_name]
                resonance_strength = np.random.uniform(0.6, 1.0)

                element = VisualizationElement(
                    element_id=f"signature_{region_name}",
                    element_type="region",
                    position=region_data["position"],
                    size=region_data["size"] * (1.2 + 0.3 * resonance_strength),
                    color=signature_color,
                    intensity=resonance_strength,
                    metadata={
                        "region_name": region_name,
                        "signature": current_signature,
                        "resonance_strength": resonance_strength,
                        "signature_affinity": ["high", "medium", "low"][i % 3],
                    },
                )
                elements.append(element)

        # 시그니처 간 공명 연결
        for i in range(len(signature_regions) - 1):
            region1 = signature_regions[i]
            region2 = signature_regions[i + 1]

            data1 = self.brain_template["regions"].get(region1)
            data2 = self.brain_template["regions"].get(region2)

            if data1 and data2:
                resonance_strength = np.random.uniform(0.5, 0.9)

                mid_point = (
                    (data1["position"][0] + data2["position"][0]) / 2,
                    (data1["position"][1] + data2["position"][1]) / 2,
                    (data1["position"][2] + data2["position"][2]) / 2,
                )

                element = VisualizationElement(
                    element_id=f"resonance_{i}",
                    element_type="connection",
                    position=mid_point,
                    size=0.05 * resonance_strength,
                    color=signature_color,
                    intensity=resonance_strength,
                    metadata={
                        "from": region1,
                        "to": region2,
                        "resonance_type": "signature_coupling",
                        "resonance_strength": resonance_strength,
                    },
                )
                elements.append(element)

        visualization_data = {
            "type": "signature_resonance",
            "active_signature": current_signature,
            "signature_regions": len(signature_regions),
            "resonance_connections": len(signature_regions) - 1,
            "average_resonance": np.mean([e.intensity for e in elements]),
            "signature_color": signature_color,
        }

        return visualization_data, elements

    def _create_default_visualization(
        self, request: BrainVisualizationRequest
    ) -> Tuple[Dict[str, Any], List[VisualizationElement]]:
        """기본 시각화 생성"""
        return self._create_brain_structure_visualization(request)

    def _apply_render_format(
        self,
        visualization_data: Dict[str, Any],
        elements: List[VisualizationElement],
        format_type: RenderFormat,
    ) -> Union[str, Dict[str, Any]]:
        """렌더링 포맷 적용"""
        if format_type == RenderFormat.JSON_DATA:
            return {
                "visualization_data": visualization_data,
                "elements": [asdict(e) for e in elements],
            }
        elif format_type == RenderFormat.ASCII:
            return self._render_ascii_brain(elements)
        elif format_type == RenderFormat.SVG:
            return self._render_svg_brain(elements)
        elif format_type == RenderFormat.HTML_CANVAS:
            return self._render_html_canvas(elements)
        else:
            return visualization_data

    def _render_ascii_brain(self, elements: List[VisualizationElement]) -> str:
        """ASCII 아트로 뇌 렌더링"""
        # 간단한 2D 평면 투영
        width, height = 80, 40
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        for element in elements:
            if element.element_type == "region":
                # 3D 좌표를 2D로 투영
                x = int((element.position[0] + 0.5) * width)
                y = int((element.position[1] + 0.5) * height)

                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))

                # 강도에 따른 문자 선택
                intensity_chars = [".", "o", "O", "@", "#"]
                char_index = int(element.intensity * (len(intensity_chars) - 1))
                canvas[y][x] = intensity_chars[char_index]

        # ASCII 아트 문자열로 변환
        ascii_art = "🧠 Echo Brain ASCII Visualization\n"
        ascii_art += "=" * width + "\n"
        for row in canvas:
            ascii_art += "".join(row) + "\n"
        ascii_art += "=" * width

        return ascii_art

    def _render_svg_brain(self, elements: List[VisualizationElement]) -> str:
        """SVG로 뇌 렌더링"""
        svg_width, svg_height = 800, 600

        svg = f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">\n'
        svg += f'<rect width="100%" height="100%" fill="#000020"/>\n'
        svg += f'<text x="10" y="30" fill="white" font-family="Arial" font-size="20">🧠 Echo Brain Visualization</text>\n'

        for element in elements:
            # 3D to 2D 투영
            x = (element.position[0] + 0.5) * svg_width
            y = (element.position[1] + 0.5) * svg_height

            if element.element_type == "region":
                radius = element.size * 100
                opacity = element.intensity

                svg += f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{element.color}" opacity="{opacity}"/>\n'
            elif element.element_type == "connection":
                radius = element.size * 50
                opacity = element.intensity * 0.7

                svg += f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{element.color}" opacity="{opacity}"/>\n'

        svg += "</svg>"
        return svg

    def _render_html_canvas(self, elements: List[VisualizationElement]) -> str:
        """HTML Canvas로 뇌 렌더링"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Echo Brain Visualization</title>
            <style>
                body { margin: 0; padding: 20px; background: #001122; color: white; font-family: Arial, sans-serif; }
                canvas { border: 1px solid #333; background: #000; }
            </style>
        </head>
        <body>
            <h1>🧠 Echo Brain Visualization</h1>
            <canvas id="brainCanvas" width="800" height="600"></canvas>
            <script>
                const canvas = document.getElementById('brainCanvas');
                const ctx = canvas.getContext('2d');

                // Clear canvas
                ctx.fillStyle = '#000020';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Draw elements
        """

        for element in elements:
            x = (element.position[0] + 0.5) * 800
            y = (element.position[1] + 0.5) * 600

            if element.element_type == "region":
                radius = element.size * 100
                html += f"""
                ctx.beginPath();
                ctx.arc({x}, {y}, {radius}, 0, 2 * Math.PI);
                ctx.fillStyle = '{element.color}';
                ctx.globalAlpha = {element.intensity};
                ctx.fill();
                """

        html += """
            </script>
        </body>
        </html>
        """

        return html

    def _apply_activity_intensity(self, base_color: str, intensity: float) -> str:
        """활동 강도에 따른 색상 변화"""
        # 간단한 밝기 조절
        if base_color.startswith("#"):
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)

            # 강도에 따라 밝기 증가
            r = min(255, int(r * (0.5 + 0.5 * intensity)))
            g = min(255, int(g * (0.5 + 0.5 * intensity)))
            b = min(255, int(b * (0.5 + 0.5 * intensity)))

            return f"#{r:02x}{g:02x}{b:02x}"

        return base_color

    def _activity_color(self, activity_strength: float) -> str:
        """활동 강도에 따른 색상 반환"""
        colors = ["#0066CC", "#00AAFF", "#66CCFF", "#CCEEFF", "#FFFFFF"]
        index = int(activity_strength * (len(colors) - 1))
        return colors[index]

    def _create_error_visualization(
        self, request_id: str, error_message: str
    ) -> BrainVisualizationResponse:
        """오류 시각화 생성"""
        error_element = VisualizationElement(
            element_id="error_indicator",
            element_type="marker",
            position=(0.0, 0.0, 0.0),
            size=0.1,
            color="#FF0000",
            intensity=1.0,
            metadata={"error": error_message},
        )

        return BrainVisualizationResponse(
            request_id=request_id,
            timestamp=datetime.now(),
            visualization_data={"error": error_message},
            render_format=RenderFormat.JSON_DATA,
            elements=[error_element],
            metadata={"status": "error"},
            generation_time_ms=0.0,
        )

    def get_visualization_session(
        self, session_id: str
    ) -> Optional[BrainVisualizationResponse]:
        """시각화 세션 조회"""
        return self.visualization_cache.get(session_id)

    def list_active_visualizations(self) -> List[str]:
        """활성 시각화 목록 반환"""
        return list(self.visualization_cache.keys())

    def clear_visualization_cache(self):
        """시각화 캐시 정리"""
        self.visualization_cache.clear()

    def get_brain_region_info(self, region_name: str) -> Optional[Dict[str, Any]]:
        """뇌 영역 정보 조회"""
        if region_name in self.brain_template["regions"]:
            region_data = self.brain_template["regions"][region_name]
            coordinate = self.brain_coordinates.get(region_name)

            return {
                "name": region_name,
                "position": region_data["position"],
                "size": region_data["size"],
                "color": region_data["color"],
                "coordinate": asdict(coordinate) if coordinate else None,
                "functions": self._get_region_functions(region_name),
            }
        return None

    def _get_region_functions(self, region_name: str) -> List[str]:
        """뇌 영역의 기능 반환"""
        function_mapping = {
            "prefrontal_cortex": [
                "executive_control",
                "decision_making",
                "working_memory",
                "planning",
            ],
            "motor_cortex": ["motor_control", "movement_planning", "motor_learning"],
            "somatosensory_cortex": [
                "touch_processing",
                "proprioception",
                "tactile_discrimination",
            ],
            "visual_cortex": [
                "visual_processing",
                "pattern_recognition",
                "visual_attention",
            ],
            "auditory_cortex": [
                "sound_processing",
                "pitch_recognition",
                "auditory_attention",
            ],
            "hippocampus": ["memory_formation", "spatial_navigation", "learning"],
            "amygdala": ["emotion_processing", "fear_response", "threat_detection"],
            "thalamus": ["sensory_relay", "attention_regulation", "consciousness"],
            "cerebellum": [
                "motor_coordination",
                "balance",
                "motor_learning",
                "cognitive_coordination",
            ],
        }

        return function_mapping.get(region_name, ["unknown_function"])