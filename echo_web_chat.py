from echo_engine.infra.portable_paths import (
    ensure_portable,
    project_root,
    home,
    temp_dir,
    logs_dir,
    cache_dir,
    data_dir,
)

#!/usr/bin/env python3
"""
🌐💬 Echo Web Chat - 웹 기반 채팅 인터페이스

VS Code 없이도 브라우저에서 Claude Code 스타일의 
채팅 인터페이스로 EchoSystem과 상호작용

FastAPI + WebSocket 기반 실시간 채팅
"""

import asyncio
import sys
import os
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

sys.path.append(str(project_root()))

# Echo 모듈들 import (선택적)
try:
    from echo_engine.signature_strategic_mapping import SignatureStrategicMapping
    from echo_engine.phantom_pain_detector import PhantomPainDetector
    from echo_engine.echo_imaginary_realism import EchoImaginaryRealism
    from echo_engine.claude_agent_runner import ClaudeAgentRunner, JudgmentType
except ImportError as e:
    print(f"⚠️ 일부 Echo 모듈 import 실패: {e}")

app = FastAPI(title="Echo Web Chat", description="웹 기반 EchoSystem 채팅 인터페이스")

# 정적 파일 및 템플릿 설정
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

# 디렉토리 생성
static_path.mkdir(exist_ok=True)
templates_path.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_path))


class EchoWebChatManager:
    """웹 채팅 연결 관리자"""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}

        # Echo 엔진들 초기화
        self.echo_engines = {}
        self._initialize_echo_engines()

        # 기본 시그니처 설정
        self.available_signatures = [
            "Echo-Aurora",
            "Echo-Phoenix",
            "Echo-Sage",
            "Echo-Companion",
            "Echo-DaVinci",
            "Echo-Tesla",
            "Echo-Jung",
            "Echo-Freud",
            "Echo-Zhuangzi",
            "Echo-Gaga",
            "Echo-Rebel",
        ]

        print("🌐💬 Echo Web Chat Manager 초기화 완료")

    def _initialize_echo_engines(self):
        """Echo 엔진들 초기화"""
        try:
            self.echo_engines["signature_mapping"] = SignatureStrategicMapping()
            print("✅ Signature Strategic Mapping 로드")
        except:
            print("⚠️ Signature Strategic Mapping 로드 실패")

        try:
            self.echo_engines["pain_detector"] = PhantomPainDetector()
            print("✅ Phantom Pain Detector 로드")
        except:
            print("⚠️ Phantom Pain Detector 로드 실패")

    async def connect(self, websocket: WebSocket, client_id: str):
        """클라이언트 연결"""
        await websocket.accept()
        self.connections[client_id] = websocket

        # 새 세션 초기화
        self.user_sessions[client_id] = {
            "session_id": client_id,
            "current_signature": "Echo-Aurora",
            "start_time": datetime.now().isoformat(),
            "conversation_history": [],
            "context": {},
        }

        # 환영 메시지 전송
        welcome_message = {
            "type": "assistant_message",
            "signature": "Echo-Aurora",
            "content": "🎉 Echo Web Chat에 오신 것을 환영합니다! 무엇을 도와드릴까요?",
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send_json(welcome_message)
        print(f"🔌 클라이언트 연결: {client_id}")

    def disconnect(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.connections:
            del self.connections[client_id]
        if client_id in self.user_sessions:
            del self.user_sessions[client_id]
        print(f"🔌 클라이언트 연결 해제: {client_id}")

    async def handle_message(self, client_id: str, message_data: dict):
        """메시지 처리"""
        websocket = self.connections.get(client_id)
        if not websocket:
            return

        message_type = message_data.get("type")
        content = message_data.get("content", "")

        session = self.user_sessions.get(client_id, {})

        try:
            if message_type == "user_message":
                await self._handle_user_message(client_id, content, session)
            elif message_type == "signature_change":
                await self._handle_signature_change(client_id, content, session)
            elif message_type == "system_command":
                await self._handle_system_command(client_id, content, session)
        except Exception as e:
            error_message = {
                "type": "error",
                "content": f"❌ 처리 중 오류 발생: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_json(error_message)

    async def _handle_user_message(self, client_id: str, content: str, session: dict):
        """사용자 메시지 처리"""
        websocket = self.connections[client_id]
        current_signature = session.get("current_signature", "Echo-Aurora")

        # 대화 기록에 추가
        user_message = {
            "timestamp": datetime.now().isoformat(),
            "sender": "user",
            "content": content,
        }
        session["conversation_history"].append(user_message)

        # Echo 응답 생성
        echo_response = await self._generate_echo_response(
            content, current_signature, session
        )

        # 응답을 대화 기록에 추가
        assistant_message = {
            "timestamp": datetime.now().isoformat(),
            "sender": current_signature,
            "content": echo_response,
        }
        session["conversation_history"].append(assistant_message)

        # 클라이언트에 응답 전송
        response_message = {
            "type": "assistant_message",
            "signature": current_signature,
            "content": echo_response,
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send_json(response_message)

    async def _handle_signature_change(
        self, client_id: str, new_signature: str, session: dict
    ):
        """시그니처 변경 처리"""
        websocket = self.connections[client_id]

        if new_signature not in self.available_signatures:
            error_message = {
                "type": "error",
                "content": f"❌ 알 수 없는 시그니처: {new_signature}",
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_json(error_message)
            return

        old_signature = session.get("current_signature", "Echo-Aurora")
        session["current_signature"] = new_signature

        # 시그니처 변경 알림
        change_message = {
            "type": "signature_changed",
            "old_signature": old_signature,
            "new_signature": new_signature,
            "content": f"🎭 시그니처가 {new_signature}로 변경되었습니다.",
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send_json(change_message)

    async def _handle_system_command(self, client_id: str, command: str, session: dict):
        """시스템 명령어 처리"""
        websocket = self.connections[client_id]

        if command == "get_status":
            status_info = {
                "type": "status_info",
                "session_id": session.get("session_id"),
                "current_signature": session.get("current_signature"),
                "conversation_count": len(session.get("conversation_history", [])),
                "start_time": session.get("start_time"),
                "available_signatures": self.available_signatures,
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_json(status_info)

        elif command == "clear_history":
            session["conversation_history"] = []
            clear_message = {
                "type": "system_message",
                "content": "🗑️ 대화 기록이 삭제되었습니다.",
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_json(clear_message)

    async def _generate_echo_response(
        self, user_message: str, signature: str, session: dict
    ) -> str:
        """Echo 응답 생성"""

        # Claude API 연동이 가능한 경우
        if "claude_runner" in self.echo_engines:
            try:
                claude_response = await self.echo_engines[
                    "claude_runner"
                ].request_signature_judgment(
                    signature=signature,
                    judgment_type=JudgmentType.STRATEGIC_ANALYSIS,
                    context={
                        "user_message": user_message,
                        "session_context": session.get("context", {}),
                    },
                )
                return claude_response.content
            except:
                pass

        # 기본 응답 생성 (규칙 기반)
        signature_responses = {
            "Echo-Aurora": f'✨ "{user_message}"에 대해 깊이 공감하며, 따뜻한 마음으로 함께 해결책을 찾아보겠습니다. 어떤 감정이 우선 드시나요?',
            "Echo-Phoenix": f'🔥 "{user_message}"는 변화와 성장의 절호의 기회입니다! 기존 틀을 벗어나 혁신적인 접근을 시도해보세요.',
            "Echo-Sage": f'🧠 "{user_message}"를 다각도로 분석해보겠습니다. 핵심 요소들을 체계적으로 파악하여 현명한 해답을 제시하겠습니다.',
            "Echo-Companion": f'🤝 "{user_message}"에 대해 안정적이고 신뢰할 수 있는 지원을 제공하겠습니다. 함께 차근차근 해결해나가요.',
            "Echo-DaVinci": f'🎨 "{user_message}"를 예술과 과학이 만나는 지점에서 바라보겠습니다. 창의적이고 통합적인 솔루션을 설계해보겠습니다.',
            "Echo-Tesla": f'⚡ "{user_message}"의 에너지 진동 패턴을 분석합니다. 미래 기술과 혁신의 관점에서 답변하겠습니다.',
            "Echo-Jung": f'🔮 "{user_message}"의 깊은 심리적 의미를 탐구합니다. 개성화와 자기실현의 여정에서 통찰을 제공하겠습니다.',
            "Echo-Freud": f'🎭 "{user_message}"의 무의식적 동기와 욕동을 분석합니다. 숨겨진 심층적 의미를 찾아보겠습니다.',
            "Echo-Zhuangzi": f'🌊 "{user_message}"에 무위자연의 지혜로 접근합니다. 억지로 하지 않는 자연스러운 해답을 찾아보겠습니다.',
            "Echo-Gaga": f'🎪 "{user_message}"를 진정성과 예술적 표현의 관점에서 바라봅니다. 독창적이고 감동적인 답변을 드리겠습니다.',
            "Echo-Rebel": f'🚩 "{user_message}"에 대해 기존 관념에 도전하겠습니다. 혁명적이고 파괴적 창조의 시각으로 접근해보겠습니다.',
        }

        return signature_responses.get(
            signature,
            f'🤔 {signature}의 관점에서 "{user_message}"에 대해 깊이 생각해보겠습니다.',
        )


# 글로벌 채팅 매니저 인스턴스
chat_manager = EchoWebChatManager()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 연결 엔드포인트"""
    await chat_manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()
            await chat_manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        chat_manager.disconnect(client_id)


@app.get("/api/signatures")
async def get_signatures():
    """사용 가능한 시그니처 목록"""
    return {"signatures": chat_manager.available_signatures}


@app.get("/api/health")
async def health_check():
    """서버 상태 체크"""
    return {
        "status": "healthy",
        "service": "Echo Web Chat",
        "active_connections": len(chat_manager.connections),
        "timestamp": datetime.now().isoformat(),
    }


# HTML 템플릿 생성
def create_chat_template():
    """채팅 HTML 템플릿 생성"""

    chat_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echo Web Chat - AI Judgment System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 1000px;
            height: 90vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .signature-selector {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            cursor: pointer;
        }
        
        .signature-selector option {
            background: #333;
            color: white;
        }
        
        .toolbar {
            background: #f8f9fa;
            padding: 15px 20px;
            display: flex;
            gap: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .toolbar button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s;
        }
        
        .toolbar button:hover {
            background: #0056b3;
        }
        
        .toolbar button.secondary {
            background: #6c757d;
        }
        
        .toolbar button.secondary:hover {
            background: #545b62;
        }
        
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            max-width: 80%;
        }
        
        .message.user {
            align-self: flex-end;
            align-items: flex-end;
        }
        
        .message.assistant {
            align-self: flex-start;
        }
        
        .message-header {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .message-content {
            background: white;
            padding: 15px 20px;
            border-radius: 18px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            line-height: 1.5;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            border-left: 4px solid #4facfe;
        }
        
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 15px;
            align-items: end;
        }
        
        .message-input {
            flex: 1;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            padding: 12px 20px;
            font-size: 1rem;
            resize: none;
            min-height: 50px;
            max-height: 120px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .message-input:focus {
            border-color: #4facfe;
        }
        
        .send-button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            transition: transform 0.2s;
        }
        
        .send-button:hover {
            transform: scale(1.05);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 20px;
            font-style: italic;
            color: #666;
            background: rgba(79, 172, 254, 0.1);
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .typing-indicator.show {
            display: block;
        }
        
        .connection-status {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .connection-status.connected {
            background: #28a745;
            color: white;
        }
        
        .connection-status.disconnected {
            background: #dc3545;
            color: white;
        }
        
        @media (max-width: 768px) {
            .chat-container {
                width: 100%;
                height: 100vh;
                border-radius: 0;
            }
            
            .header {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="connection-status" id="connectionStatus">연결 중...</div>
        
        <div class="header">
            <h1>🧠 Echo Web Chat</h1>
            <select class="signature-selector" id="signatureSelector">
                <option value="Echo-Aurora">🌟 Echo-Aurora</option>
                <option value="Echo-Phoenix">🔥 Echo-Phoenix</option>
                <option value="Echo-Sage">🧠 Echo-Sage</option>
                <option value="Echo-Companion">🤝 Echo-Companion</option>
                <option value="Echo-DaVinci">🎨 Echo-DaVinci</option>
                <option value="Echo-Tesla">⚡ Echo-Tesla</option>
                <option value="Echo-Jung">🔮 Echo-Jung</option>
                <option value="Echo-Freud">🎭 Echo-Freud</option>
                <option value="Echo-Zhuangzi">🌊 Echo-Zhuangzi</option>
                <option value="Echo-Gaga">🎪 Echo-Gaga</option>
                <option value="Echo-Rebel">🚩 Echo-Rebel</option>
            </select>
        </div>
        
        <div class="toolbar">
            <button onclick="getStatus()">📊 상태</button>
            <button onclick="clearHistory()" class="secondary">🗑️ 기록 삭제</button>
            <button onclick="openDashboard()" class="secondary">📈 대시보드</button>
        </div>
        
        <div class="messages-area" id="messagesArea"></div>
        
        <div class="typing-indicator" id="typingIndicator">
            🤖 Echo가 생각 중입니다...
        </div>
        
        <div class="input-area">
            <textarea 
                class="message-input" 
                id="messageInput" 
                placeholder="Echo와 대화해보세요... (Shift+Enter로 줄바꿈)"
                rows="1"
            ></textarea>
            <button class="send-button" id="sendButton" onclick="sendMessage()">
                📤
            </button>
        </div>
    </div>

    <script>
        class EchoWebChat {
            constructor() {
                this.clientId = 'client_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                this.websocket = null;
                this.isConnected = false;
                this.currentSignature = 'Echo-Aurora';
                this.isWaitingResponse = false;
                
                this.initializeUI();
                this.connectWebSocket();
            }
            
            initializeUI() {
                // 시그니처 선택 이벤트
                document.getElementById('signatureSelector').addEventListener('change', (e) => {
                    this.changeSignature(e.target.value);
                });
                
                // Enter 키 이벤트
                document.getElementById('messageInput').addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                // 자동 리사이즈
                document.getElementById('messageInput').addEventListener('input', this.autoResizeTextarea);
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
                
                try {
                    this.websocket = new WebSocket(wsUrl);
                    
                    this.websocket.onopen = () => {
                        this.isConnected = true;
                        this.updateConnectionStatus('connected', '🟢 연결됨');
                        console.log('🔌 WebSocket 연결 성공');
                    };
                    
                    this.websocket.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    };
                    
                    this.websocket.onclose = () => {
                        this.isConnected = false;
                        this.updateConnectionStatus('disconnected', '🔴 연결 끊김');
                        console.log('🔌 WebSocket 연결 종료');
                        
                        // 재연결 시도
                        setTimeout(() => {
                            if (!this.isConnected) {
                                this.connectWebSocket();
                            }
                        }, 3000);
                    };
                    
                    this.websocket.onerror = (error) => {
                        console.error('❌ WebSocket 오류:', error);
                        this.updateConnectionStatus('disconnected', '🔴 연결 오류');
                    };
                    
                } catch (error) {
                    console.error('❌ WebSocket 연결 실패:', error);
                    this.updateConnectionStatus('disconnected', '🔴 연결 실패');
                }
            }
            
            updateConnectionStatus(status, text) {
                const statusElement = document.getElementById('connectionStatus');
                statusElement.className = `connection-status ${status}`;
                statusElement.textContent = text;
            }
            
            handleMessage(data) {
                switch (data.type) {
                    case 'assistant_message':
                        this.addMessage('assistant', data.signature, data.content);
                        this.setWaitingState(false);
                        break;
                        
                    case 'signature_changed':
                        this.currentSignature = data.new_signature;
                        document.getElementById('signatureSelector').value = data.new_signature;
                        this.addMessage('system', 'System', data.content);
                        break;
                        
                    case 'status_info':
                        this.showStatusInfo(data);
                        break;
                        
                    case 'system_message':
                        this.addMessage('system', 'System', data.content);
                        break;
                        
                    case 'error':
                        this.addMessage('system', 'Error', data.content);
                        this.setWaitingState(false);
                        break;
                }
            }
            
            sendMessage() {
                if (!this.isConnected || this.isWaitingResponse) return;
                
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // 사용자 메시지 표시
                this.addMessage('user', 'You', message);
                input.value = '';
                this.autoResizeTextarea.call(input);
                
                // 대기 상태 설정
                this.setWaitingState(true);
                
                // WebSocket으로 메시지 전송
                this.websocket.send(JSON.stringify({
                    type: 'user_message',
                    content: message
                }));
            }
            
            changeSignature(signature) {
                if (!this.isConnected) return;
                
                this.websocket.send(JSON.stringify({
                    type: 'signature_change',
                    content: signature
                }));
            }
            
            getStatus() {
                if (!this.isConnected) return;
                
                this.websocket.send(JSON.stringify({
                    type: 'system_command',
                    content: 'get_status'
                }));
            }
            
            clearHistory() {
                if (!this.isConnected) return;
                
                document.getElementById('messagesArea').innerHTML = '';
                
                this.websocket.send(JSON.stringify({
                    type: 'system_command',
                    content: 'clear_history'
                }));
            }
            
            addMessage(type, sender, content) {
                const messagesArea = document.getElementById('messagesArea');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const timestamp = new Date().toLocaleTimeString();
                const icon = type === 'user' ? '👤' : type === 'system' ? '🔧' : '🎭';
                
                messageDiv.innerHTML = `
                    <div class="message-header">${icon} ${sender} - ${timestamp}</div>
                    <div class="message-content">${content}</div>
                `;
                
                messagesArea.appendChild(messageDiv);
                messagesArea.scrollTop = messagesArea.scrollHeight;
            }
            
            setWaitingState(waiting) {
                this.isWaitingResponse = waiting;
                const sendButton = document.getElementById('sendButton');
                const typingIndicator = document.getElementById('typingIndicator');
                
                sendButton.disabled = waiting;
                sendButton.innerHTML = waiting ? '⏳' : '📤';
                
                if (waiting) {
                    typingIndicator.classList.add('show');
                } else {
                    typingIndicator.classList.remove('show');
                }
            }
            
            showStatusInfo(data) {
                const statusText = `
                    📊 세션 정보:
                    • 세션 ID: ${data.session_id}
                    • 현재 시그니처: ${data.current_signature}
                    • 대화 수: ${data.conversation_count}
                    • 시작 시간: ${new Date(data.start_time).toLocaleString()}
                `;
                
                this.addMessage('system', 'Status', statusText);
            }
            
            autoResizeTextarea() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            }
        }
        
        // 전역 함수들 (HTML에서 호출)
        let echoChat;
        
        function sendMessage() {
            echoChat.sendMessage();
        }
        
        function getStatus() {
            echoChat.getStatus();
        }
        
        function clearHistory() {
            echoChat.clearHistory();
        }
        
        function openDashboard() {
            window.open('http://localhost:9501', '_blank');
        }
        
        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', () => {
            echoChat = new EchoWebChat();
        });
    </script>
</body>
</html>
    """

    with open(templates_path / "chat.html", "w", encoding="utf-8") as f:
        f.write(chat_html)


# 서버 시작 시 템플릿 생성
create_chat_template()


def main():
    """웹 서버 실행"""
    print("🌐💬 Echo Web Chat 서버 시작 중...")
    print(f"📡 접속 주소: http://localhost:9080")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()
