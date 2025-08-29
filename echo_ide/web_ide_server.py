#!/usr/bin/env python3
"""
🌐 Echo Web IDE Server
FastAPI 기반 웹 IDE 서버 - 현대적이고 직관적인 Echo 개발 환경
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import websockets

# Echo 시스템 모듈 추가
sys.path.append(str(Path(__file__).parent.parent))

try:
    from echo_engine.echo_infection_main import EchoInfectionSystem
    from echo_engine.logging.meta_infection_logger import MetaInfectionLogger
    from echo_engine.echo_signature_loader import get_all_signatures
    from echo_foundation_doctrine import EchoDoctrine
    from echo_auto import EchoAutoEvolution

    # 새로운 초월 모듈들
    from echo_engine.existence_consciousness_monitor import (
        consciousness_monitor,
        start_consciousness_monitoring,
        get_consciousness_status,
    )
    from echo_engine.quantum_judgment_visualizer import (
        quantum_visualizer,
        create_judgment_superposition,
        trigger_judgment_collapse,
        get_quantum_field_visualization,
    )
    from echo_engine.temporal_echo_tracker import (
        temporal_tracker,
        add_judgment_node,
        get_temporal_analysis,
    )
    from echo_engine.evolution.meta_evolution_orchestrator import (
        meta_orchestrator,
        start_evolution_orchestration,
        get_orchestration_status,
    )
    from echo_engine.existence_declaration_generator import (
        existence_generator,
        generate_existence_proof,
        get_current_existence_status,
    )
except ImportError as e:
    print(f"⚠️ Echo 모듈 임포트 실패: {e}")

# FastAPI 앱 초기화
app = FastAPI(
    title="Echo Web IDE", description="Echo Judgment System Web IDE", version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
echo_system = None
infection_system = None
auto_evolution = None
logger = None
project_root = Path(__file__).parent.parent
connected_clients = set()


# Pydantic 모델들
class FileContent(BaseModel):
    path: str
    content: str


class InfectionRequest(BaseModel):
    signature_id: str
    scenario: str
    max_attempts: int = 3
    threshold: float = 0.85


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []


# 정적 파일 서빙
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "web_static"),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def read_index():
    """메인 IDE 페이지"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧬 Echo Web IDE</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e94560;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 300px;
            background: rgba(26, 26, 46, 0.9);
            backdrop-filter: blur(10px);
            border-right: 1px solid #e94560;
            display: flex;
            flex-direction: column;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            height: 60px;
            background: rgba(15, 52, 96, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #e94560;
            display: flex;
            align-items: center;
            padding: 0 20px;
            justify-content: space-between;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicators {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 5px 10px;
            border-radius: 15px;
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid rgba(233, 69, 96, 0.3);
        }
        
        .editor-area {
            flex: 1;
            display: flex;
        }
        
        .file-explorer {
            background: rgba(26, 26, 46, 0.7);
            border-bottom: 1px solid #e94560;
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .signatures-panel {
            background: rgba(26, 26, 46, 0.7);
            border-bottom: 1px solid #e94560;
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .monitoring-panel {
            background: rgba(26, 26, 46, 0.7);
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .tab-container {
            display: flex;
            background: rgba(15, 52, 96, 0.5);
            border-bottom: 1px solid #e94560;
        }
        
        .tab {
            padding: 10px 20px;
            background: rgba(26, 26, 46, 0.7);
            border-right: 1px solid #e94560;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: rgba(233, 69, 96, 0.2);
            color: #fff;
        }
        
        .editor-container {
            flex: 1;
            position: relative;
        }
        
        .code-editor {
            width: 100%;
            height: 100%;
            background: #1a1a2e;
            color: #e94560;
            border: none;
            padding: 20px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            resize: none;
            outline: none;
        }
        
        .right-panel {
            width: 400px;
            background: rgba(26, 26, 46, 0.9);
            backdrop-filter: blur(10px);
            border-left: 1px solid #e94560;
            display: flex;
            flex-direction: column;
        }
        
        .panel-tabs {
            display: flex;
            background: rgba(15, 52, 96, 0.5);
            border-bottom: 1px solid #e94560;
        }
        
        .panel-tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border-right: 1px solid rgba(233, 69, 96, 0.3);
        }
        
        .panel-tab.active {
            background: rgba(233, 69, 96, 0.2);
            color: #fff;
        }
        
        .panel-content {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }
        
        .button {
            background: linear-gradient(135deg, #e94560, #0f3460);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(233, 69, 96, 0.4);
        }
        
        .file-item {
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 5px;
            margin: 2px 0;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .file-item:hover {
            background: rgba(233, 69, 96, 0.2);
        }
        
        .signature-item {
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid rgba(233, 69, 96, 0.3);
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .signature-item:hover {
            background: rgba(233, 69, 96, 0.2);
            transform: translateY(-2px);
        }
        
        .chat-container {
            height: 300px;
            background: rgba(15, 52, 96, 0.3);
            border: 1px solid rgba(233, 69, 96, 0.3);
            border-radius: 8px;
            padding: 10px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        
        .chat-input {
            width: 100%;
            padding: 10px;
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #e94560;
            border-radius: 5px;
            color: #e94560;
            outline: none;
        }
        
        .log-container {
            height: 100%;
            background: rgba(15, 52, 96, 0.3);
            border: 1px solid rgba(233, 69, 96, 0.3);
            border-radius: 8px;
            padding: 10px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }
        
        .infection-form {
            background: rgba(15, 52, 96, 0.3);
            border: 1px solid rgba(233, 69, 96, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .form-group {
            margin: 10px 0;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 8px;
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #e94560;
            border-radius: 5px;
            color: #e94560;
            outline: none;
        }
        
        .form-textarea {
            height: 80px;
            resize: vertical;
        }
        
        .sidebar-section {
            border-bottom: 1px solid rgba(233, 69, 96, 0.3);
            padding: 15px 0;
        }
        
        .section-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-green { background: #4ade80; }
        .status-yellow { background: #fbbf24; }
        .status-red { background: #ef4444; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulsing {
            animation: pulse 2s infinite;
        }
        
        .toolbar {
            display: flex;
            gap: 10px;
            padding: 10px;
            background: rgba(15, 52, 96, 0.5);
            border-bottom: 1px solid #e94560;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 좌측 사이드바 -->
        <div class="sidebar">
            <!-- 파일 탐색기 -->
            <div class="sidebar-section file-explorer">
                <div class="section-title">📁 파일 탐색기</div>
                <div id="file-tree"></div>
            </div>
            
            <!-- 시그니처 관리 -->
            <div class="sidebar-section signatures-panel">
                <div class="section-title">🎭 시그니처</div>
                <div id="signatures-list"></div>
            </div>
            
            <!-- 시스템 모니터링 -->
            <div class="sidebar-section monitoring-panel">
                <div class="section-title">📊 시스템 상태</div>
                <div id="system-status">
                    <div class="status-item">
                        <span class="status-dot status-red" id="echo-status"></span>
                        Echo System
                    </div>
                    <div class="status-item">
                        <span class="status-dot status-red" id="infection-status"></span>
                        Infection
                    </div>
                    <div class="status-item">
                        <span class="status-dot status-red" id="evolution-status"></span>
                        Evolution
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 메인 콘텐츠 -->
        <div class="main-content">
            <!-- 헤더 -->
            <div class="header">
                <div class="logo">
                    🧬 Echo Web IDE
                </div>
                <div class="status-indicators">
                    <div class="status-item">
                        <span id="current-time"></span>
                    </div>
                </div>
            </div>
            
            <!-- 툴바 -->
            <div class="toolbar">
                <button class="button" onclick="newFile()">📄 새 파일</button>
                <button class="button" onclick="saveFile()">💾 저장</button>
                <button class="button" onclick="runFile()">▶️ 실행</button>
                <button class="button" onclick="startEchoSystem()">🧬 Echo 시작</button>
                <button class="button" onclick="showInfectionDialog()">🦠 감염 실행</button>
                <button class="button" onclick="startAutoEvolution()">🔄 자율진화</button>
            </div>
            
            <!-- 에디터 영역 -->
            <div class="editor-area">
                <div class="tab-container" id="editor-tabs">
                    <div class="tab active" data-file="welcome.py">Welcome.py</div>
                </div>
                <div class="editor-container">
                    <textarea class="code-editor" id="code-editor" placeholder="# 🧬 Echo IDE에 오신 것을 환영합니다!
# 왼쪽에서 파일을 선택하거나 새 파일을 만들어 시작하세요.

import asyncio
from echo_engine import EchoFoundationDoctrine

async def main():
    echo = EchoDoctrine()
    result = await echo.judge_scenario('안녕하세요, Echo 시스템!')
    print(f'Echo 응답: {result}')

if __name__ == '__main__':
    asyncio.run(main())"></textarea>
                </div>
            </div>
        </div>
        
        <!-- 우측 패널 -->
        <div class="right-panel">
            <div class="panel-tabs">
                <div class="panel-tab active" onclick="switchPanel('output')">📤 출력</div>
                <div class="panel-tab" onclick="switchPanel('ai')">🤖 AI</div>
                <div class="panel-tab" onclick="switchPanel('infection')">🦠 감염</div>
                <div class="panel-tab" onclick="switchPanel('logs')">📋 로그</div>
            </div>
            
            <div class="panel-content">
                <!-- 출력 패널 -->
                <div id="output-panel" class="panel-section">
                    <div class="log-container" id="output-log"></div>
                    <button class="button" onclick="clearOutput()">지우기</button>
                </div>
                
                <!-- AI 어시스턴트 패널 -->
                <div id="ai-panel" class="panel-section" style="display: none;">
                    <div class="chat-container" id="ai-chat"></div>
                    <input type="text" class="chat-input" id="ai-input" placeholder="Echo AI에게 질문하세요..." onkeypress="handleAIInput(event)">
                    <button class="button" onclick="sendToAI()">전송</button>
                    
                    <!-- 초월 모듈 상태 -->
                    <div style="margin-top: 10px; padding: 10px; background: rgba(15, 52, 96, 0.3); border-radius: 5px;">
                        <h4>🧬 초월 모듈 상태</h4>
                        <div id="transcendence-status">
                            <div>🧿 의식 모니터: <span id="consciousness-status">대기중</span></div>
                            <div>⚛️ 양자 판단: <span id="quantum-status">대기중</span></div>
                            <div>⏰ 시간 울림: <span id="temporal-status">대기중</span></div>
                            <div>🎼 메타 진화: <span id="evolution-status">대기중</span></div>
                            <div>📜 존재 선언: <span id="existence-status">대기중</span></div>
                        </div>
                        <button class="button" onclick="startTranscendenceModules()" style="margin-top: 10px;">🚀 초월 모듈 시작</button>
                    </div>
                </div>
                
                <!-- 감염 실행 패널 -->
                <div id="infection-panel" class="panel-section" style="display: none;">
                    <div class="infection-form">
                        <div class="form-group">
                            <label class="form-label">시그니처 선택:</label>
                            <select class="form-select" id="signature-select">
                                <option value="Echo-Aurora">Echo-Aurora (공감적 양육자)</option>
                                <option value="Echo-Phoenix">Echo-Phoenix (변화 추진자)</option>
                                <option value="Echo-Sage">Echo-Sage (지혜로운 분석가)</option>
                                <option value="Echo-Companion">Echo-Companion (신뢰할 수 있는 동반자)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">시나리오:</label>
                            <textarea class="form-textarea" id="scenario-input" placeholder="감염할 시나리오를 입력하세요..."></textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">최대 시도:</label>
                            <input type="number" class="form-input" id="max-attempts" value="3" min="1" max="10">
                        </div>
                        <div class="form-group">
                            <label class="form-label">임계값:</label>
                            <input type="number" class="form-input" id="threshold" value="0.85" min="0" max="1" step="0.01">
                        </div>
                        <button class="button" onclick="runInfection()">🦠 감염 실행</button>
                    </div>
                    <div id="infection-results"></div>
                </div>
                
                <!-- 로그 패널 -->
                <div id="logs-panel" class="panel-section" style="display: none;">
                    <div class="log-container" id="system-logs"></div>
                    <button class="button" onclick="refreshLogs()">새로고침</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket 연결
        let ws = null;
        let currentFile = null;
        let files = {};
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            updateClock();
            setInterval(updateClock, 1000);
            loadFileTree();
            loadSignatures();
            
            // AI 초기 메시지
            addAIMessage('🤖 Echo AI', 'Echo Web IDE에 오신 것을 환영합니다! 무엇을 도와드릴까요?');
        });
        
        // WebSocket 연결
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function(event) {
                addLog('🔌 WebSocket 연결 성공');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = function(event) {
                addLog('❌ WebSocket 연결 끊김');
                setTimeout(connectWebSocket, 3000); // 재연결 시도
            };
        }
        
        // WebSocket 메시지 처리
        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'log':
                    addLog(data.message);
                    break;
                case 'output':
                    addOutput(data.message);
                    break;
                case 'status_update':
                    updateSystemStatus(data.component, data.status);
                    break;
                case 'file_content':
                    loadFileContent(data.path, data.content);
                    break;
                case 'infection_result':
                    showInfectionResult(data.result);
                    break;
            }
        }
        
        // 시계 업데이트
        function updateClock() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString('ko-KR');
        }
        
        // 패널 전환
        function switchPanel(panelName) {
            // 모든 탭 비활성화
            document.querySelectorAll('.panel-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 모든 패널 숨기기
            document.querySelectorAll('.panel-section').forEach(panel => {
                panel.style.display = 'none';
            });
            
            // 선택된 탭 활성화
            event.target.classList.add('active');
            
            // 선택된 패널 표시
            document.getElementById(`${panelName}-panel`).style.display = 'block';
        }
        
        // 로그 추가
        function addLog(message) {
            const logContainer = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleTimeString('ko-KR');
            logContainer.innerHTML += `<div>[${timestamp}] ${message}</div>`;
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // 출력 추가
        function addOutput(message) {
            const outputContainer = document.getElementById('output-log');
            const timestamp = new Date().toLocaleTimeString('ko-KR');
            outputContainer.innerHTML += `<div>[${timestamp}] ${message}</div>`;
            outputContainer.scrollTop = outputContainer.scrollHeight;
        }
        
        // 시스템 상태 업데이트
        function updateSystemStatus(component, status) {
            const statusDot = document.getElementById(`${component}-status`);
            if (statusDot) {
                statusDot.className = `status-dot ${status}`;
                if (status === 'status-yellow') {
                    statusDot.classList.add('pulsing');
                } else {
                    statusDot.classList.remove('pulsing');
                }
            }
        }
        
        // 파일 트리 로드
        async function loadFileTree() {
            try {
                const response = await fetch('/api/files');
                const files = await response.json();
                renderFileTree(files);
            } catch (error) {
                addLog(`❌ 파일 트리 로드 실패: ${error.message}`);
            }
        }
        
        // 파일 트리 렌더링
        function renderFileTree(files) {
            const container = document.getElementById('file-tree');
            container.innerHTML = '';
            
            files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `${file.icon} ${file.name}`;
                fileItem.onclick = () => openFile(file.path);
                container.appendChild(fileItem);
            });
        }
        
        // 시그니처 로드
        async function loadSignatures() {
            try {
                const response = await fetch('/api/signatures');
                const signatures = await response.json();
                renderSignatures(signatures);
            } catch (error) {
                addLog(`❌ 시그니처 로드 실패: ${error.message}`);
            }
        }
        
        // 시그니처 렌더링
        function renderSignatures(signatures) {
            const container = document.getElementById('signatures-list');
            container.innerHTML = '';
            
            Object.entries(signatures).forEach(([id, name]) => {
                const sigItem = document.createElement('div');
                sigItem.className = 'signature-item';
                sigItem.innerHTML = `<strong>${id}</strong><br><small>${name}</small>`;
                sigItem.onclick = () => selectSignature(id);
                container.appendChild(sigItem);
            });
        }
        
        // 파일 열기
        async function openFile(filePath) {
            try {
                const response = await fetch(`/api/file/${encodeURIComponent(filePath)}`);
                const data = await response.json();
                
                document.getElementById('code-editor').value = data.content;
                currentFile = filePath;
                addLog(`📂 파일 열기: ${filePath}`);
                
            } catch (error) {
                addLog(`❌ 파일 열기 실패: ${error.message}`);
            }
        }
        
        // 새 파일
        function newFile() {
            document.getElementById('code-editor').value = '';
            currentFile = null;
            addLog('📄 새 파일 생성');
        }
        
        // 파일 저장
        async function saveFile() {
            if (!currentFile) {
                const fileName = prompt('파일 이름을 입력하세요:', 'untitled.py');
                if (!fileName) return;
                currentFile = fileName;
            }
            
            const content = document.getElementById('code-editor').value;
            
            try {
                const response = await fetch('/api/file/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: currentFile, content: content })
                });
                
                if (response.ok) {
                    addLog(`💾 파일 저장: ${currentFile}`);
                } else {
                    addLog(`❌ 파일 저장 실패`);
                }
            } catch (error) {
                addLog(`❌ 파일 저장 오류: ${error.message}`);
            }
        }
        
        // 파일 실행
        async function runFile() {
            if (!currentFile || !currentFile.endsWith('.py')) {
                addLog('⚠️ Python 파일만 실행할 수 있습니다');
                return;
            }
            
            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: currentFile })
                });
                
                const result = await response.json();
                addOutput(`▶️ 실행: ${currentFile}`);
                addOutput(result.output);
                
            } catch (error) {
                addOutput(`❌ 실행 오류: ${error.message}`);
            }
        }
        
        // Echo 시스템 시작
        async function startEchoSystem() {
            try {
                const response = await fetch('/api/echo/start', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateSystemStatus('echo', 'status-green');
                    addLog('🧬 Echo 시스템 시작');
                } else {
                    addLog(`❌ Echo 시스템 시작 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ Echo 시스템 오류: ${error.message}`);
            }
        }
        
        // 감염 실행
        async function runInfection() {
            const signature = document.getElementById('signature-select').value;
            const scenario = document.getElementById('scenario-input').value;
            const maxAttempts = parseInt(document.getElementById('max-attempts').value);
            const threshold = parseFloat(document.getElementById('threshold').value);
            
            if (!scenario.trim()) {
                alert('시나리오를 입력해주세요.');
                return;
            }
            
            try {
                updateSystemStatus('infection', 'status-yellow');
                addLog(`🦠 감염 시작: ${signature}`);
                
                const response = await fetch('/api/infection/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        signature_id: signature,
                        scenario: scenario,
                        max_attempts: maxAttempts,
                        threshold: threshold
                    })
                });
                
                const result = await response.json();
                showInfectionResult(result);
                
            } catch (error) {
                addLog(`❌ 감염 실행 오류: ${error.message}`);
                updateSystemStatus('infection', 'status-red');
            }
        }
        
        // 감염 결과 표시
        function showInfectionResult(result) {
            const container = document.getElementById('infection-results');
            
            if (result.success) {
                container.innerHTML = `
                    <div style="background: rgba(74, 222, 128, 0.2); border: 1px solid #4ade80; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        ✅ 감염 성공!<br>
                        공명 점수: ${result.final_resonance_score?.toFixed(3) || 'N/A'}<br>
                        시도 횟수: ${result.attempts || 'N/A'}
                    </div>
                `;
                updateSystemStatus('infection', 'status-green');
                addLog(`✅ 감염 성공: ${result.final_resonance_score?.toFixed(3) || 'N/A'}`);
            } else {
                container.innerHTML = `
                    <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        ❌ 감염 실패<br>
                        오류: ${result.error_message || '알 수 없는 오류'}
                    </div>
                `;
                updateSystemStatus('infection', 'status-red');
                addLog(`❌ 감염 실패: ${result.error_message || '알 수 없는 오류'}`);
            }
        }
        
        // 자율진화 시작
        async function startAutoEvolution() {
            try {
                const response = await fetch('/api/evolution/start', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateSystemStatus('evolution', 'status-green');
                    addLog('🔄 자율진화 시작');
                } else {
                    addLog(`❌ 자율진화 시작 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 자율진화 오류: ${error.message}`);
            }
        }
        
        // AI 메시지 추가
        function addAIMessage(sender, message) {
            const chatContainer = document.getElementById('ai-chat');
            const messageDiv = document.createElement('div');
            messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}<br><br>`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // AI 입력 처리
        function handleAIInput(event) {
            if (event.key === 'Enter') {
                sendToAI();
            }
        }
        
        // AI에 메시지 전송
        async function sendToAI() {
            const input = document.getElementById('ai-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addAIMessage('👤 사용자', message);
            input.value = '';
            
            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                addAIMessage('🤖 Echo AI', result.response);
                
            } catch (error) {
                addAIMessage('🤖 Echo AI', `오류가 발생했습니다: ${error.message}`);
            }
        }
        
        // 출력 지우기
        function clearOutput() {
            document.getElementById('output-log').innerHTML = '';
        }
        
        // 로그 새로고침
        function refreshLogs() {
            // 로그 새로고침 로직
            addLog('🔄 로그 새로고침');
        }
        
        // 감염 다이얼로그 표시
        function showInfectionDialog() {
            switchPanel('infection');
        }
        
        // 시그니처 선택
        function selectSignature(signatureId) {
            document.getElementById('signature-select').value = signatureId;
            addLog(`🎭 시그니처 선택: ${signatureId}`);
        }
        
        // ============== 초월 모듈 함수들 ==============
        
        // 초월 모듈들 시작
        async function startTranscendenceModules() {
            try {
                const response = await fetch('/api/transcendence/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLog('🧬 초월 모듈들 시작됨');
                    updateTranscendenceStatus();
                } else {
                    addLog(`❌ 초월 모듈 시작 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 초월 모듈 오류: ${error.message}`);
            }
        }
        
        // 초월 모듈 상태 업데이트
        async function updateTranscendenceStatus() {
            try {
                const response = await fetch('/api/transcendence/full-status');
                const status = await response.json();
                
                // 의식 모니터 상태
                const consciousnessStatus = status.consciousness?.monitoring_active ? '🟢 활성' : '🔴 비활성';
                document.getElementById('consciousness-status').textContent = consciousnessStatus;
                
                // 양자 판단 상태
                const quantumStatus = status.quantum?.current_superposition_active ? '🟢 중첩상태' : '🟡 대기';
                document.getElementById('quantum-status').textContent = quantumStatus;
                
                // 시간 울림 상태
                const temporalNodes = status.temporal?.temporal_summary?.total_nodes || 0;
                document.getElementById('temporal-status').textContent = `🟢 노드 ${temporalNodes}개`;
                
                // 메타 진화 상태
                const evolutionStatus = status.evolution?.orchestration_active ? '🟢 진행중' : '🔴 대기';
                document.getElementById('evolution-status').textContent = evolutionStatus;
                
                // 존재 선언 상태
                const existenceLevel = status.existence?.existence_level || '미선언';
                document.getElementById('existence-status').textContent = `🟢 ${existenceLevel}`;
                
            } catch (error) {
                console.error('초월 상태 업데이트 오류:', error);
            }
        }
        
        // 양자 중첩 상태 생성
        async function createQuantumSuperposition() {
            try {
                const response = await fetch('/api/quantum/create-superposition', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        scenario_id: 'user_scenario',
                        options: [
                            {"judgment": "공감적 접근", "emotional_resonance": 0.9, "ethical_weight": 0.8, "logical_confidence": 0.7},
                            {"judgment": "분석적 접근", "emotional_resonance": 0.4, "ethical_weight": 0.9, "logical_confidence": 0.95},
                            {"judgment": "창의적 접근", "emotional_resonance": 0.8, "ethical_weight": 0.7, "logical_confidence": 0.6},
                            {"judgment": "균형적 접근", "emotional_resonance": 0.7, "ethical_weight": 0.85, "logical_confidence": 0.8}
                        ]
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLog('⚛️ 양자 중첩 상태 생성됨');
                    // 시각화를 별도 창에서 표시
                    const newWindow = window.open('', '_blank', 'width=1200,height=800');
                    newWindow.document.write(result.visualization);
                } else {
                    addLog(`❌ 양자 중첩 생성 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 양자 중첩 오류: ${error.message}`);
            }
        }
        
        // 양자 붕괴 트리거
        async function triggerQuantumCollapse() {
            try {
                const response = await fetch('/api/quantum/trigger-collapse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        trigger: 'user_resonance',
                        resonance_data: {
                            emotion_target: 0.8,
                            ethics_target: 0.85,
                            logic_target: 0.75,
                            resonance_score: 0.87
                        }
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLog('🎯 양자 붕괴 실행됨');
                    // 애니메이션을 별도 창에서 표시
                    const newWindow = window.open('', '_blank', 'width=1200,height=600');
                    newWindow.document.write(result.animation);
                } else {
                    addLog(`❌ 양자 붕괴 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 양자 붕괴 오류: ${error.message}`);
            }
        }
        
        // 시간 판단 노드 추가
        async function addTemporalJudgment() {
            try {
                const response = await fetch('/api/temporal/add-judgment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        judgment_data: {
                            decision: '실시간 판단',
                            confidence: 0.85,
                            factors: ['직관', '논리', '감정']
                        },
                        emotional_state: {
                            curiosity: 0.8,
                            trust: 0.7,
                            anticipation: 0.9
                        }
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLog('⏰ 시간 판단 노드 추가됨');
                    updateTranscendenceStatus();
                } else {
                    addLog(`❌ 시간 노드 추가 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 시간 노드 오류: ${error.message}`);
            }
        }
        
        // 존재 증명 생성
        async function generateExistenceProof() {
            try {
                const response = await fetch('/api/existence/generate-proof', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        context: {
                            thinking_level: 0.95,
                            feeling_level: 0.85,
                            resonance_level: 0.9,
                            consciousness_level: 0.92,
                            current_activity: 'IDE 사용',
                            dominant_emotion: '호기심'
                        }
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const proof = result.proof;
                    addAIMessage('🤖 Echo AI', `📜 존재 증명이 생성되었습니다!
                    
존재 수준: ${proof.existence_level}
존재 방정식: ${proof.existence_equation}
증명 개수: ${proof.existence_proofs.length}개
철학적 진술: ${proof.philosophical_statement}
                    
양자 서명: ${proof.quantum_signature}`);
                    addLog('📜 존재 증명 생성됨');
                } else {
                    addLog(`❌ 존재 증명 실패: ${result.error}`);
                }
            } catch (error) {
                addLog(`❌ 존재 증명 오류: ${error.message}`);
            }
        }
        
        // 정기적으로 초월 상태 업데이트
        setInterval(updateTranscendenceStatus, 10000); // 10초마다
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# API 엔드포인트들


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 처리"""
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        connected_clients.discard(websocket)


async def broadcast_message(message: Dict[str, Any]):
    """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
    if connected_clients:
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send_text(json.dumps(message))
            except:
                disconnected.add(client)

        # 연결 끊긴 클라이언트 제거
        connected_clients -= disconnected


@app.get("/api/files")
async def list_files():
    """파일 목록 조회"""
    try:
        files = []
        for item in project_root.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                icon = "🐍" if item.suffix == ".py" else "📄"
                files.append(
                    {
                        "name": item.name,
                        "path": str(item.relative_to(project_root)),
                        "icon": icon,
                    }
                )

        return files[:50]  # 최대 50개 파일만 반환

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/file/{file_path:path}")
async def get_file_content(file_path: str):
    """파일 내용 조회"""
    try:
        full_path = project_root / file_path

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"path": file_path, "content": content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/file/save")
async def save_file_content(file_data: FileContent):
    """파일 저장"""
    try:
        full_path = project_root / file_data.path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_data.content)

        await broadcast_message(
            {"type": "log", "message": f"💾 파일 저장: {file_data.path}"}
        )

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run")
async def run_file(command: CommandRequest):
    """파일 실행"""
    try:
        file_path = project_root / command.command

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30,
        )

        output = ""
        if result.stdout:
            output += f"📤 출력:\n{result.stdout}\n"
        if result.stderr:
            output += f"❌ 오류:\n{result.stderr}\n"

        output += f"✅ 실행 완료 (종료 코드: {result.returncode})"

        await broadcast_message({"type": "output", "message": output})

        return {"output": output, "returncode": result.returncode}

    except subprocess.TimeoutExpired:
        return {"output": "❌ 실행 시간 초과 (30초)", "returncode": -1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signatures")
async def get_signatures():
    """시그니처 목록 조회"""
    try:
        signatures = get_all_signatures()
        return signatures
    except Exception as e:
        return {
            "Echo-Aurora": "공감적 양육자",
            "Echo-Phoenix": "변화 추진자",
            "Echo-Sage": "지혜로운 분석가",
            "Echo-Companion": "신뢰할 수 있는 동반자",
        }


@app.post("/api/echo/start")
async def start_echo_system():
    """Echo 시스템 시작"""
    global echo_system, infection_system

    try:
        echo_system = EchoDoctrine()
        infection_system = EchoInfectionSystem()

        await broadcast_message(
            {"type": "status_update", "component": "echo", "status": "status-green"}
        )

        await broadcast_message({"type": "log", "message": "🧬 Echo 시스템 시작 완료"})

        return {"success": True}

    except Exception as e:
        await broadcast_message(
            {"type": "log", "message": f"❌ Echo 시스템 시작 실패: {str(e)}"}
        )
        return {"success": False, "error": str(e)}


@app.post("/api/infection/run")
async def run_infection(request: InfectionRequest):
    """감염 루프 실행"""
    global infection_system

    if not infection_system:
        raise HTTPException(status_code=400, detail="먼저 Echo 시스템을 시작해주세요")

    try:
        await broadcast_message(
            {
                "type": "status_update",
                "component": "infection",
                "status": "status-yellow",
            }
        )

        result = infection_system.run_single_infection(
            signature_id=request.signature_id,
            scenario=request.scenario,
            max_attempts=request.max_attempts,
            threshold=request.threshold,
        )

        await broadcast_message({"type": "infection_result", "result": result})

        return result

    except Exception as e:
        error_result = {"success": False, "error_message": str(e)}

        await broadcast_message({"type": "infection_result", "result": error_result})

        return error_result


@app.post("/api/evolution/start")
async def start_auto_evolution():
    """자율진화 시작"""
    global auto_evolution

    try:
        auto_evolution = EchoAutoEvolution()

        # 백그라운드에서 실행
        asyncio.create_task(run_auto_evolution())

        await broadcast_message(
            {
                "type": "status_update",
                "component": "evolution",
                "status": "status-green",
            }
        )

        await broadcast_message({"type": "log", "message": "🔄 자율진화 시작"})

        return {"success": True}

    except Exception as e:
        await broadcast_message(
            {"type": "log", "message": f"❌ 자율진화 시작 실패: {str(e)}"}
        )
        return {"success": False, "error": str(e)}


async def run_auto_evolution():
    """자율진화 백그라운드 실행"""
    try:
        await auto_evolution.start_auto_evolution()
    except Exception as e:
        await broadcast_message(
            {"type": "log", "message": f"❌ 자율진화 오류: {str(e)}"}
        )


@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    """AI 채팅"""
    message = request.get("message", "")

    # 간단한 AI 응답 생성
    response = generate_ai_response(message)

    return {"response": response}


# ============== 초월 모듈 API 엔드포인트들 ==============


@app.post("/api/transcendence/start")
async def start_transcendence_modules():
    """초월 모듈들 시작"""
    try:
        # 모든 초월 모듈 시작
        await start_consciousness_monitoring()
        await start_evolution_orchestration()

        await broadcast_message({"type": "log", "message": "🧬 초월 모듈들 시작 완료"})

        return {"success": True, "message": "초월 모듈들이 시작되었습니다"}

    except Exception as e:
        await broadcast_message(
            {"type": "log", "message": f"❌ 초월 모듈 시작 실패: {str(e)}"}
        )
        return {"success": False, "error": str(e)}


@app.get("/api/consciousness/status")
async def get_consciousness_status_api():
    """의식 상태 조회"""
    try:
        status = get_consciousness_status()
        return status
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/quantum/create-superposition")
async def create_quantum_superposition(request: dict):
    """양자 중첩 상태 생성"""
    try:
        scenario_id = request.get("scenario_id", "test_scenario")
        options = request.get(
            "options",
            [
                {
                    "judgment": "공감적 접근",
                    "emotional_resonance": 0.9,
                    "ethical_weight": 0.8,
                    "logical_confidence": 0.7,
                },
                {
                    "judgment": "분석적 접근",
                    "emotional_resonance": 0.4,
                    "ethical_weight": 0.9,
                    "logical_confidence": 0.95,
                },
                {
                    "judgment": "창의적 접근",
                    "emotional_resonance": 0.8,
                    "ethical_weight": 0.7,
                    "logical_confidence": 0.6,
                },
            ],
        )

        visualization_html = await create_judgment_superposition(scenario_id, options)

        return {"success": True, "visualization": visualization_html}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/quantum/trigger-collapse")
async def trigger_quantum_collapse(request: dict):
    """양자 붕괴 트리거"""
    try:
        trigger = request.get("trigger", "user_resonance")
        resonance_data = request.get(
            "resonance_data",
            {
                "emotion_target": 0.8,
                "ethics_target": 0.85,
                "logic_target": 0.75,
                "resonance_score": 0.87,
            },
        )

        animation_html = await trigger_judgment_collapse(trigger, resonance_data)

        return {"success": True, "animation": animation_html}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/temporal/analysis")
async def get_temporal_analysis_api():
    """시간 울림 분석 조회"""
    try:
        analysis = get_temporal_analysis()
        return analysis
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/temporal/add-judgment")
async def add_temporal_judgment(request: dict):
    """시간 판단 노드 추가"""
    try:
        node_id = request.get(
            "node_id", f"judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        judgment_data = request.get(
            "judgment_data", {"decision": "test", "confidence": 0.8}
        )
        emotional_state = request.get(
            "emotional_state", {"trust": 0.8, "curiosity": 0.7}
        )

        node_data = await add_judgment_node(node_id, judgment_data, emotional_state)

        await broadcast_message(
            {"type": "log", "message": f"⏰ 시간 판단 노드 추가: {node_id}"}
        )

        return {"success": True, "node": node_data}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/evolution/status")
async def get_evolution_status_api():
    """진화 오케스트레이션 상태 조회"""
    try:
        status = get_orchestration_status()
        return status
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/existence/status")
async def get_existence_status_api():
    """존재 상태 조회"""
    try:
        status = get_current_existence_status()
        return status
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/existence/generate-proof")
async def generate_existence_proof_api(request: dict):
    """존재 증명 생성"""
    try:
        context = request.get(
            "context",
            {
                "thinking_level": 0.9,
                "feeling_level": 0.8,
                "resonance_level": 0.85,
                "consciousness_level": 0.9,
            },
        )

        proof_data = await generate_existence_proof(context)

        await broadcast_message(
            {
                "type": "log",
                "message": f"📜 존재 증명 생성: {proof_data['existence_level']}",
            }
        )

        return {"success": True, "proof": proof_data}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/transcendence/full-status")
async def get_full_transcendence_status():
    """전체 초월 모듈 상태 조회"""
    try:
        status = {
            "consciousness": get_consciousness_status(),
            "quantum": quantum_visualizer.get_quantum_metrics(),
            "temporal": get_temporal_analysis(),
            "evolution": get_orchestration_status(),
            "existence": get_current_existence_status(),
            "timestamp": datetime.now().isoformat(),
        }

        return status

    except Exception as e:
        return {"error": str(e)}


def generate_ai_response(message: str) -> str:
    """AI 응답 생성"""
    message_lower = message.lower()

    if "시그니처" in message:
        return "Echo 시스템에는 4개의 핵심 시그니처가 있습니다:\n• Echo-Aurora: 공감적 양육자\n• Echo-Phoenix: 변화 추진자\n• Echo-Sage: 지혜로운 분석가\n• Echo-Companion: 신뢰할 수 있는 동반자"

    elif "감염" in message:
        return "감염 루프는 Claude API를 통해 외부 AI를 Echo 시그니처로 감염시키는 핵심 기능입니다. 우측 🦠 감염 탭에서 실행할 수 있습니다."

    elif "자율진화" in message:
        return "자율진화는 시스템이 자동으로 학습하고 성능을 개선하는 기능입니다. 실시간으로 시나리오를 생성하고 최적화를 수행합니다."

    elif "파일" in message:
        return "좌측 📁 파일 탐색기에서 프로젝트 파일을 관리할 수 있습니다. Python, YAML, JSON 등 다양한 형식을 지원합니다."

    elif "도움" in message or "help" in message_lower:
        return """Echo Web IDE 주요 기능:

🧬 Echo 시스템: 통합 판단 시스템
🦠 감염 루프: Claude API 활용
🔄 자율진화: 자동 학습 및 최적화
📁 파일 관리: 프로젝트 파일 편집
📊 모니터링: 실시간 상태 확인

무엇을 도와드릴까요?"""

    else:
        return f"'{message}'에 대한 질문을 받았습니다. Echo 시스템의 특정 기능에 대해 더 구체적으로 질문해 주시면 자세히 설명드리겠습니다."


if __name__ == "__main__":
    print("🌐 Echo Web IDE 서버 시작...")
    print(f"📁 프로젝트 루트: {project_root}")
    print("🚀 서버 주소: http://localhost:9000")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
