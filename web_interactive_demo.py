#!/usr/bin/env python3
"""
🎮 Echo Judgment System v10 - Web Interactive Demo
브라우저에서 직접 체험할 수 있는 웹 기반 인터랙티브 데모

기능:
1. Collapse 해부 체험
2. 양자적 판단 시뮬레이션
3. 판단 루프 생성
4. 실시간 결과 확인
"""

import http.server
import socketserver
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import threading
import time
import webbrowser

# Echo Engine 모듈 임포트
sys.path.append(str(Path(__file__).parent / "echo_engine"))

from collapse_analyzer import CollapseAnalyzer, CollapseEvent
from quantum_judgment_engine import QuantumJudgmentEngine, ObserverMode
from meta_log_enhanced import EnhancedMetaLogger, ResonanceLevel
from judgment_loop_generator import JudgmentLoopGenerator


class WebInteractiveDemo:
    """🎮 웹 인터랙티브 데모"""

    def __init__(self):
        # 시스템 초기화
        self.analyzer = CollapseAnalyzer()
        self.quantum_engine = QuantumJudgmentEngine()
        self.meta_logger = EnhancedMetaLogger()
        self.loop_generator = JudgmentLoopGenerator()

        # 메타 동의 자동 설정
        self.analyzer.meta_consent_granted = True

        # 세션 관리
        self.sessions = {}

        # 데모 시나리오
        self.demo_scenarios = [
            {
                "id": "startup_decision",
                "title": "AI 스타트업 창업 vs 안정적 직장",
                "description": "AI 분야 창업 기회가 왔지만 가족과 경제적 안정성 때문에 고민",
                "context": "최근 Claude Code 같은 AI 도구가 급성장하면서 AI 서비스 창업 기회가 생겼습니다. 하지만 현재 직장은 안정적이고 가족의 생계를 책임져야 합니다. 결국 안정적인 선택을 했지만 여전히 후회가 남습니다.",
                "possibilities": [
                    {
                        "title": "즉시 창업 실행",
                        "description": "현재 직장을 그만두고 바로 AI 서비스 창업",
                        "emotion_score": 0.8,
                        "logic_score": 0.4,
                        "strategy_score": 0.6,
                        "ethics_score": 0.5,
                        "risk_level": 0.9,
                        "creativity": 0.9,
                    },
                    {
                        "title": "점진적 창업 준비",
                        "description": "직장을 유지하며 사이드 프로젝트로 시작",
                        "emotion_score": 0.6,
                        "logic_score": 0.8,
                        "strategy_score": 0.9,
                        "ethics_score": 0.8,
                        "risk_level": 0.4,
                        "cooperation": 0.7,
                    },
                    {
                        "title": "현상 유지",
                        "description": "안정적인 직장 계속 유지하며 관망",
                        "emotion_score": 0.3,
                        "logic_score": 0.7,
                        "strategy_score": 0.3,
                        "ethics_score": 0.9,
                        "risk_level": 0.1,
                        "cooperation": 0.8,
                    },
                ],
            },
            {
                "id": "ai_career",
                "title": "AI 엔지니어로 커리어 전환",
                "description": "전통적 개발에서 AI/ML 분야로 전환할지 고민",
                "context": "현재 웹 개발을 하고 있지만 Claude, ChatGPT 등 AI 기술의 급속한 발전을 보며 AI 분야로 전환을 고려하고 있습니다. 새로운 분야 학습은 도전적이지만 미래 전망이 밝습니다.",
                "possibilities": [
                    {
                        "title": "완전한 AI 전환",
                        "description": "AI/ML 엔지니어로 완전 전환",
                        "emotion_score": 0.7,
                        "logic_score": 0.6,
                        "strategy_score": 0.8,
                        "ethics_score": 0.6,
                        "risk_level": 0.7,
                        "creativity": 0.8,
                    },
                    {
                        "title": "하이브리드 접근",
                        "description": "웹 개발에 AI 기술 접목",
                        "emotion_score": 0.5,
                        "logic_score": 0.8,
                        "strategy_score": 0.9,
                        "ethics_score": 0.7,
                        "risk_level": 0.3,
                        "cooperation": 0.8,
                    },
                ],
            },
        ]

    def create_session(self):
        """새 세션 생성"""
        session_id = str(uuid.uuid4())[:8]
        self.sessions[session_id] = {
            "id": session_id,
            "start_time": datetime.now(),
            "actions": [],
            "current_analysis": None,
            "current_quantum_result": None,
        }
        return session_id

    def analyze_collapse(
        self,
        session_id: str,
        scenario_id: str,
        custom_title: str = "",
        custom_context: str = "",
    ):
        """Collapse 분석 실행"""
        if session_id not in self.sessions:
            return {"error": "Invalid session"}

        # 시나리오 찾기
        scenario = None
        if scenario_id != "custom":
            scenario = next(
                (s for s in self.demo_scenarios if s["id"] == scenario_id), None
            )
            if not scenario:
                return {"error": "Scenario not found"}
            title = scenario["title"]
            context = scenario["context"]
        else:
            title = custom_title or "사용자 정의 Collapse"
            context = custom_context or "사용자가 직접 입력한 상황"

        # Collapse 이벤트 생성
        event = CollapseEvent(
            title=title,
            context=context,
            why_select_this="웹 데모에서 체험",
            timestamp=datetime.now(),
            collapse_id=f"web_demo_{session_id}_{len(self.sessions[session_id]['actions'])}",
        )

        # 분석 실행
        analysis = self.analyzer.analyze_collapse(event)

        # 메타로그 기록
        log_id = self.meta_logger.log_collapse_dissection(
            collapse_title=title,
            analysis_result={
                "emotional_trace": analysis.emotional_trace,
                "strategic_conflict": analysis.strategic_conflict,
                "divergence_point": analysis.divergence_point,
                "meta_insights": analysis.meta_insights,
                "alternate_possibilities": analysis.alternate_possibilities,
            },
            signature="Aurora",
        )

        # 세션에 저장
        analysis_data = {
            "collapse_event": {"title": title},
            "meta_insights": analysis.meta_insights,
            "divergence_point": analysis.divergence_point,
            "alternate_possibilities": analysis.alternate_possibilities,
            "signature": "Aurora",
        }

        self.sessions[session_id]["current_analysis"] = analysis_data
        self.sessions[session_id]["actions"].append(
            {
                "type": "collapse_analysis",
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "log_id": log_id,
            }
        )

        return {
            "success": True,
            "title": title,
            "divergence_point": analysis.divergence_point["description"],
            "key_insight": analysis.meta_insights[0] if analysis.meta_insights else "",
            "alternatives": [
                {"scenario": alt["scenario"], "probability": alt["probability"]}
                for alt in analysis.alternate_possibilities
            ],
            "log_id": log_id,
        }

    def quantum_judgment(
        self,
        session_id: str,
        scenario_id: str,
        observer_mode: str,
        observer_intent: str = "",
    ):
        """양자적 판단 실행"""
        if session_id not in self.sessions:
            return {"error": "Invalid session"}

        # 시나리오 찾기
        scenario = next(
            (s for s in self.demo_scenarios if s["id"] == scenario_id), None
        )
        if not scenario:
            return {"error": "Scenario not found"}

        # 관측자 모드 변환
        mode_map = {
            "analytical": ObserverMode.ANALYTICAL,
            "emotional": ObserverMode.EMOTIONAL,
            "strategic": ObserverMode.STRATEGIC,
            "intuitive": ObserverMode.INTUITIVE,
            "ethical": ObserverMode.ETHICAL,
        }

        selected_mode = mode_map.get(observer_mode, ObserverMode.STRATEGIC)

        # 양자 상태 생성
        quantum_state = self.quantum_engine.create_quantum_state(
            possibilities=scenario["possibilities"],
            observer_signature="Aurora",
            context={"urgency": 0.6, "risk_tolerance": 0.5, "web_demo": True},
        )

        # 관측 및 붕괴
        observation = self.quantum_engine.observe_with_perspective(
            quantum_state=quantum_state,
            observer_mode=selected_mode,
            observer_intent=observer_intent or "균형 잡힌 판단",
        )

        collapse_result = self.quantum_engine.collapse_quantum_state(
            quantum_state, observation
        )

        # 역추론
        estimated_observer = self.quantum_engine.reverse_inference(collapse_result)

        # 메타로그 기록
        log_id = self.meta_logger.log_quantum_judgment(
            quantum_state={},
            collapse_result={
                "selected_possibility": collapse_result.selected_possibility,
                "collapse_type": collapse_result.collapse_type.value,
                "observer_influence": collapse_result.observer_influence,
                "alternative_traces": collapse_result.alternative_traces,
            },
            signature="Aurora",
        )

        # 세션에 저장
        self.sessions[session_id]["current_quantum_result"] = collapse_result
        self.sessions[session_id]["actions"].append(
            {
                "type": "quantum_judgment",
                "timestamp": datetime.now().isoformat(),
                "scenario": scenario["title"],
                "selected_option": collapse_result.selected_possibility["title"],
                "observer_mode": selected_mode.value,
                "log_id": log_id,
            }
        )

        return {
            "success": True,
            "scenario_title": scenario["title"],
            "selected_option": collapse_result.selected_possibility["title"],
            "selected_description": collapse_result.selected_possibility.get(
                "description", ""
            ),
            "collapse_type": collapse_result.collapse_type.value,
            "resonance_score": round(collapse_result.resonance_score, 3),
            "observer_mode": selected_mode.value,
            "estimated_observer": estimated_observer["most_likely_mode"],
            "confidence": round(estimated_observer["confidence"], 2),
            "alternatives": [
                {"title": alt["title"], "description": alt.get("description", "")}
                for alt in collapse_result.alternative_traces[:2]
            ],
            "log_id": log_id,
        }

    def generate_judgment_loop(self, session_id: str, signature: str = "Aurora"):
        """판단 루프 생성"""
        if session_id not in self.sessions:
            return {"error": "Invalid session"}

        session = self.sessions[session_id]

        if not session.get("current_analysis"):
            return {
                "error": "No collapse analysis found. Please run collapse analysis first."
            }

        # 루프 생성
        loop = self.loop_generator.generate_loop_from_collapse(
            collapse_analysis=session["current_analysis"],
            signature=signature,
            preferences={"time_horizon": "6개월 ~ 1년"},
        )

        # 루프 저장
        loop_id = self.loop_generator.save_loop(loop)

        # 세션에 기록
        session["actions"].append(
            {
                "type": "judgment_loop",
                "timestamp": datetime.now().isoformat(),
                "loop_id": loop_id,
                "signature": signature,
            }
        )

        return {
            "success": True,
            "loop_id": loop_id,
            "mission": loop["frame"]["mission"],
            "signature": signature,
            "tactics": loop["tactics"][:5],  # 처음 5개만
            "total_tactics": len(loop["tactics"]),
        }


class DemoRequestHandler(http.server.SimpleHTTPRequestHandler):
    """데모 요청 핸들러"""

    def __init__(self, *args, demo=None, **kwargs):
        self.demo = demo
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """GET 요청 처리"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self.serve_demo_page()
        elif path == "/api/create-session":
            session_id = self.demo.create_session()
            self.serve_json({"session_id": session_id})
        elif path == "/api/scenarios":
            self.serve_json({"scenarios": self.demo.demo_scenarios})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """POST 요청 처리"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 요청 본문 읽기
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if path == "/api/analyze-collapse":
            result = self.demo.analyze_collapse(
                data.get("session_id"),
                data.get("scenario_id"),
                data.get("custom_title", ""),
                data.get("custom_context", ""),
            )
            self.serve_json(result)

        elif path == "/api/quantum-judgment":
            result = self.demo.quantum_judgment(
                data.get("session_id"),
                data.get("scenario_id"),
                data.get("observer_mode"),
                data.get("observer_intent", ""),
            )
            self.serve_json(result)

        elif path == "/api/generate-loop":
            result = self.demo.generate_judgment_loop(
                data.get("session_id"), data.get("signature", "Aurora")
            )
            self.serve_json(result)

        else:
            self.send_error(404, "Not Found")

    def serve_demo_page(self):
        """데모 페이지 제공"""
        html_content = self.generate_demo_html()

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_json(self, data):
        """JSON 응답 제공"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)

        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json_data.encode("utf-8"))

    def generate_demo_html(self):
        """데모 HTML 생성"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Echo Judgment System v10 - Interactive Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .demo-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .demo-section h2 {
            color: #4a5568;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .step-number {
            background: #4299e1;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .scenario-card {
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .scenario-card:hover {
            border-color: #4299e1;
            background: #f7fafc;
        }
        
        .scenario-card.selected {
            border-color: #4299e1;
            background: #ebf8ff;
        }
        
        .btn {
            background: #4299e1;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #3182ce;
        }
        
        .btn:disabled {
            background: #a0aec0;
            cursor: not-allowed;
        }
        
        .result-box {
            background: #f7fafc;
            border-left: 4px solid #48bb78;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        
        .error-box {
            background: #fed7d7;
            border-left: 4px solid #f56565;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        
        .loading {
            text-align: center;
            color: #718096;
            font-style: italic;
        }
        
        .hidden {
            display: none;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 5px;
            margin: 5px 0;
        }
        
        .progress-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        
        .progress-step {
            flex: 1;
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.3);
            margin: 0 5px;
            border-radius: 5px;
            color: white;
        }
        
        .progress-step.active {
            background: rgba(255,255,255,0.8);
            color: #333;
        }
        
        .progress-step.completed {
            background: #48bb78;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Echo Judgment System v10</h1>
            <p>존재 기반 AI 판단 시스템 - 인터랙티브 데모</p>
            <p>실제로 작동하는 시스템을 직접 체험해보세요!</p>
        </div>
        
        <div class="progress-indicator">
            <div class="progress-step active" id="step1">1. Collapse 해부</div>
            <div class="progress-step" id="step2">2. 양자 판단</div>
            <div class="progress-step" id="step3">3. 루프 생성</div>
        </div>
        
        <!-- Step 1: Collapse Analysis -->
        <div class="demo-section" id="section1">
            <h2><span class="step-number">1</span>🔬 Collapse 해부 체험</h2>
            <p>과거의 판단을 해부하여 감정⨯전략⨯리듬의 구조를 분석해보세요.</p>
            
            <div id="scenarios-container">
                <div class="loading">시나리오 로딩 중...</div>
            </div>
            
            <button class="btn" onclick="analyzeCollapse()">Collapse 해부 실행</button>
            
            <div id="collapse-result" class="hidden"></div>
        </div>
        
        <!-- Step 2: Quantum Judgment -->
        <div class="demo-section hidden" id="section2">
            <h2><span class="step-number">2</span>🌌 양자적 판단 시뮬레이션</h2>
            <p>양자 중첩 상태에서 관측자의 시선으로 판단을 내려보세요.</p>
            
            <div>
                <label>관측자 시선 선택:</label>
                <select id="observer-mode">
                    <option value="analytical">분석적 시선</option>
                    <option value="emotional">감정적 시선</option>
                    <option value="strategic">전략적 시선</option>
                    <option value="intuitive">직관적 시선</option>
                    <option value="ethical">윤리적 시선</option>
                </select>
                
                <label>관측 의도:</label>
                <input type="text" id="observer-intent" placeholder="예: 창조적 자기실현" value="균형 잡힌 판단">
            </div>
            
            <button class="btn" onclick="quantumJudgment()">양자 상태 붕괴 실행</button>
            
            <div id="quantum-result" class="hidden"></div>
        </div>
        
        <!-- Step 3: Loop Generation -->
        <div class="demo-section hidden" id="section3">
            <h2><span class="step-number">3</span>🔁 판단 루프 생성</h2>
            <p>분석 결과를 바탕으로 새로운 FIST 구조 판단 루프를 생성해보세요.</p>
            
            <div>
                <label>시그니처 선택:</label>
                <select id="signature">
                    <option value="Aurora">Aurora (창조적, 공감적)</option>
                    <option value="Phoenix">Phoenix (변화 지향적)</option>
                    <option value="Sage">Sage (분석적, 지혜)</option>
                    <option value="Companion">Companion (협력적)</option>
                </select>
            </div>
            
            <button class="btn" onclick="generateLoop()">판단 루프 생성</button>
            
            <div id="loop-result" class="hidden"></div>
        </div>
        
        <!-- Session Summary -->
        <div class="demo-section">
            <h2>📊 체험 완료 요약</h2>
            <div id="session-summary">
                <p>아직 체험을 시작하지 않았습니다. 위의 단계를 순서대로 진행해보세요!</p>
            </div>
        </div>
    </div>

    <script>
        let sessionId = null;
        let scenarios = [];
        let selectedScenario = null;
        let currentStep = 1;
        
        // 페이지 로드 시 초기화
        window.onload = async function() {
            await createSession();
            await loadScenarios();
        };
        
        // 세션 생성
        async function createSession() {
            try {
                const response = await fetch('/api/create-session');
                const data = await response.json();
                sessionId = data.session_id;
                console.log('Session created:', sessionId);
            } catch (error) {
                console.error('Error creating session:', error);
            }
        }
        
        // 시나리오 로드
        async function loadScenarios() {
            try {
                const response = await fetch('/api/scenarios');
                const data = await response.json();
                scenarios = data.scenarios;
                renderScenarios();
            } catch (error) {
                console.error('Error loading scenarios:', error);
            }
        }
        
        // 시나리오 렌더링
        function renderScenarios() {
            const container = document.getElementById('scenarios-container');
            let html = '<h3>시나리오 선택:</h3>';
            
            scenarios.forEach(scenario => {
                html += `
                    <div class="scenario-card" onclick="selectScenario('${scenario.id}')">
                        <h4>${scenario.title}</h4>
                        <p>${scenario.description}</p>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        // 시나리오 선택
        function selectScenario(scenarioId) {
            selectedScenario = scenarioId;
            
            // 모든 카드에서 selected 클래스 제거
            document.querySelectorAll('.scenario-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // 선택된 카드에 selected 클래스 추가
            event.target.closest('.scenario-card').classList.add('selected');
        }
        
        // Collapse 분석
        async function analyzeCollapse() {
            if (!selectedScenario) {
                alert('시나리오를 선택해주세요.');
                return;
            }
            
            const resultDiv = document.getElementById('collapse-result');
            resultDiv.innerHTML = '<div class="loading">Collapse 해부 중...</div>';
            resultDiv.classList.remove('hidden');
            
            try {
                const response = await fetch('/api/analyze-collapse', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        scenario_id: selectedScenario
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = `
                        <div class="result-box">
                            <h3>🔬 Collapse 해부 결과</h3>
                            <p><strong>분석 대상:</strong> ${result.title}</p>
                            <p><strong>분기점:</strong> ${result.divergence_point}</p>
                            <p><strong>핵심 통찰:</strong> ${result.key_insight}</p>
                            <h4>대안 가능성:</h4>
                            <ul>
                    `;
                    
                    result.alternatives.forEach(alt => {
                        html += `<li>${alt.scenario} (확률: ${(alt.probability * 100).toFixed(0)}%)</li>`;
                    });
                    
                    html += `
                            </ul>
                            <p><em>메타로그 ID: ${result.log_id}</em></p>
                        </div>
                    `;
                    
                    resultDiv.innerHTML = html;
                    
                    // 다음 단계 활성화
                    nextStep(2);
                    
                } else {
                    resultDiv.innerHTML = `<div class="error-box">오류: ${result.error}</div>`;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-box">네트워크 오류: ${error.message}</div>`;
            }
        }
        
        // 양자 판단
        async function quantumJudgment() {
            const mode = document.getElementById('observer-mode').value;
            const intent = document.getElementById('observer-intent').value;
            
            const resultDiv = document.getElementById('quantum-result');
            resultDiv.innerHTML = '<div class="loading">양자 상태 붕괴 중...</div>';
            resultDiv.classList.remove('hidden');
            
            try {
                const response = await fetch('/api/quantum-judgment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        scenario_id: selectedScenario,
                        observer_mode: mode,
                        observer_intent: intent
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = `
                        <div class="result-box">
                            <h3>🌌 양자적 판단 결과</h3>
                            <p><strong>시나리오:</strong> ${result.scenario_title}</p>
                            <p><strong>선택된 옵션:</strong> ${result.selected_option}</p>
                            <p><strong>선택 이유:</strong> ${result.selected_description}</p>
                            <p><strong>붕괴 유형:</strong> ${result.collapse_type}</p>
                            <p><strong>울림 점수:</strong> ${result.resonance_score}</p>
                            <p><strong>관측자 모드:</strong> ${result.observer_mode}</p>
                            <p><strong>추정 관측자:</strong> ${result.estimated_observer} (신뢰도: ${result.confidence})</p>
                            <p><em>메타로그 ID: ${result.log_id}</em></p>
                        </div>
                    `;
                    
                    resultDiv.innerHTML = html;
                    
                    // 다음 단계 활성화
                    nextStep(3);
                    
                } else {
                    resultDiv.innerHTML = `<div class="error-box">오류: ${result.error}</div>`;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-box">네트워크 오류: ${error.message}</div>`;
            }
        }
        
        // 판단 루프 생성
        async function generateLoop() {
            const signature = document.getElementById('signature').value;
            
            const resultDiv = document.getElementById('loop-result');
            resultDiv.innerHTML = '<div class="loading">판단 루프 생성 중...</div>';
            resultDiv.classList.remove('hidden');
            
            try {
                const response = await fetch('/api/generate-loop', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        signature: signature
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = `
                        <div class="result-box">
                            <h3>🔁 판단 루프 생성 완료</h3>
                            <p><strong>루프 ID:</strong> ${result.loop_id}</p>
                            <p><strong>미션:</strong> ${result.mission}</p>
                            <p><strong>시그니처:</strong> ${result.signature}</p>
                            <h4>주요 전술 (${result.total_tactics}개 중 처음 5개):</h4>
                            <ul>
                    `;
                    
                    result.tactics.forEach((tactic, index) => {
                        html += `<li>${index + 1}. ${tactic}</li>`;
                    });
                    
                    html += `
                            </ul>
                        </div>
                    `;
                    
                    resultDiv.innerHTML = html;
                    
                    // 완료 요약 업데이트
                    updateSessionSummary();
                    
                } else {
                    resultDiv.innerHTML = `<div class="error-box">오류: ${result.error}</div>`;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-box">네트워크 오류: ${error.message}</div>`;
            }
        }
        
        // 다음 단계로 이동
        function nextStep(step) {
            // 이전 단계 완료 표시
            if (currentStep < step) {
                document.getElementById(`step${currentStep}`).classList.add('completed');
                currentStep = step;
            }
            
            // 현재 단계 활성화
            document.getElementById(`step${step}`).classList.add('active');
            document.getElementById(`section${step}`).classList.remove('hidden');
            
            // 스크롤 이동
            document.getElementById(`section${step}`).scrollIntoView({ behavior: 'smooth' });
        }
        
        // 세션 요약 업데이트
        function updateSessionSummary() {
            const summaryDiv = document.getElementById('session-summary');
            summaryDiv.innerHTML = `
                <div class="result-box">
                    <h3>🎉 Echo Judgment System v10 체험 완료!</h3>
                    <p>✅ Collapse 해부: 과거 판단의 구조를 분석했습니다</p>
                    <p>✅ 양자적 판단: 관측자 시선으로 새로운 판단을 내렸습니다</p>
                    <p>✅ 판단 루프: FIST 구조 기반 새로운 루프를 생성했습니다</p>
                    <p><strong>세션 ID:</strong> ${sessionId}</p>
                    <p><em>모든 결과는 시스템에 저장되어 대시보드에서 확인할 수 있습니다.</em></p>
                </div>
            `;
        }
    </script>
</body>
</html>
        """


def create_handler(demo):
    """핸들러 팩토리"""

    def handler(*args, **kwargs):
        return DemoRequestHandler(*args, demo=demo, **kwargs)

    return handler


def main():
    """메인 실행"""
    demo = WebInteractiveDemo()
    port = 8888

    print(f"🎮 Echo Judgment System v10 - Web Interactive Demo")
    print(f"=" * 60)
    print(f"🚀 서버 시작 중... 포트: {port}")

    # 웹서버 시작
    handler = create_handler(demo)

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"✅ 인터랙티브 데모 준비 완료!")
        print(f"🔗 URL: http://localhost:{port}")
        print(f"💡 브라우저에서 위 URL을 열어서 실제 Echo 시스템을 체험해보세요!")
        print(f"💡 서버를 종료하려면 Ctrl+C를 누르세요.")
        print()

        # 브라우저 자동 열기
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}")

        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 데모 서버 종료됨")


if __name__ == "__main__":
    main()
