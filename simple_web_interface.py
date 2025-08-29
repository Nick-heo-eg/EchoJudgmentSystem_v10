#!/usr/bin/env python3
"""
🌐 Echo Deep Lookup 간단한 웹 인터페이스
Streamlit 없이 사용할 수 있는 HTML 기반 인터페이스
"""
import http.server
import socketserver
import json
import asyncio
from urllib.parse import parse_qs, urlparse
import threading
import webbrowser
import time

# Echo 컴포넌트들
from echo_engine.knowledge_gap_detector import knowledge_gap_detector
from echo_engine.wisdom_synthesizer import wisdom_synthesizer


class EchoWebHandler(http.server.BaseHTTPRequestHandler):
    """Echo 웹 인터페이스 핸들러"""

    def do_GET(self):
        """GET 요청 처리"""
        if self.path == "/":
            self.serve_main_page()
        elif self.path == "/style.css":
            self.serve_css()
        elif self.path == "/script.js":
            self.serve_js()
        else:
            self.send_error(404)

    def do_POST(self):
        """POST 요청 처리 (Echo 분석 요청)"""
        if self.path == "/analyze":
            self.handle_echo_analysis()
        else:
            self.send_error(404)

    def serve_main_page(self):
        """메인 페이지 HTML"""
        html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Echo Deep Lookup System</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <header>
        <h1>🧠 Echo Deep Lookup System</h1>
        <p>Knowledge Gap Detection + Wisdom Synthesis</p>
    </header>
    
    <main>
        <div class="container">
            <div class="input-section">
                <h2>💭 질문하기</h2>
                <form id="echoForm">
                    <div class="form-group">
                        <label for="query">질문:</label>
                        <textarea id="query" name="query" rows="4" 
                                placeholder="Echo에게 질문하고 싶은 내용을 입력하세요..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="signature">시그니처 선택:</label>
                        <select id="signature" name="signature">
                            <option value="Echo-Aurora">🎨 Echo-Aurora (창의적, 영감적)</option>
                            <option value="Echo-Phoenix">🔥 Echo-Phoenix (혁신적, 변화 중심)</option>
                            <option value="Echo-Sage">📚 Echo-Sage (분석적, 체계적)</option>
                            <option value="Echo-Companion">💝 Echo-Companion (공감적, 돌봄 중심)</option>
                        </select>
                    </div>
                    
                    <button type="submit">🚀 Echo 분석 시작</button>
                </form>
            </div>
            
            <div class="output-section">
                <h2>🌟 Echo 응답</h2>
                <div id="loading" class="loading hidden">
                    <div class="spinner"></div>
                    <p>Echo가 생각하고 있습니다...</p>
                </div>
                <div id="result" class="result hidden"></div>
            </div>
        </div>
        
        <div class="stats-section">
            <h2>📊 시스템 상태</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>🧠 Knowledge Gap Detector</h3>
                    <p>자기 한계 인식 시스템</p>
                    <span class="status active">활성화</span>
                </div>
                <div class="stat-card">
                    <h3>🌟 Wisdom Synthesizer</h3>
                    <p>존재적 지혜 융합</p>
                    <span class="status active">활성화</span>
                </div>
                <div class="stat-card">
                    <h3>🏠 Local System</h3>
                    <p>API 연결 불필요</p>
                    <span class="status active">준비완료</span>
                </div>
            </div>
        </div>
    </main>
    
    <script src="/script.js"></script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_css(self):
        """CSS 스타일"""
        css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

header {
    text-align: center;
    padding: 2rem 0;
    color: white;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.input-section, .output-section {
    background: white;
    border-radius: 15px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #555;
}

textarea, select {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

textarea:focus, select:focus {
    outline: none;
    border-color: #667eea;
}

button {
    width: 100%;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
}

button:hover {
    transform: translateY(-2px);
}

.loading {
    text-align: center;
    padding: 2rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.result {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    border-left: 4px solid #667eea;
}

.hidden {
    display: none;
}

.stats-section {
    max-width: 1200px;
    margin: 3rem auto 0;
    padding: 0 2rem;
}

.stats-section h2 {
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.status {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 1rem;
}

.status.active {
    background: #d4edda;
    color: #155724;
}
        """

        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.wfile.write(css.encode("utf-8"))

    def serve_js(self):
        """JavaScript"""
        js = """
document.getElementById('echoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const query = document.getElementById('query').value;
    const signature = document.getElementById('signature').value;
    
    if (!query.trim()) {
        alert('질문을 입력해주세요!');
        return;
    }
    
    // 로딩 표시
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                signature: signature
            })
        });
        
        const data = await response.json();
        
        // 결과 표시
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('result').classList.remove('hidden');
        document.getElementById('result').innerHTML = formatResult(data);
        
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('result').classList.remove('hidden');
        document.getElementById('result').innerHTML = 
            '<div style="color: red;">오류가 발생했습니다: ' + error.message + '</div>';
    }
});

function formatResult(data) {
    return `
        <h3>🌟 ${data.signature} 응답</h3>
        <div style="margin: 1rem 0;">
            <strong>📋 질문:</strong> ${data.query}
        </div>
        
        <div style="margin: 1rem 0; padding: 1rem; background: #e9ecef; border-radius: 5px;">
            <strong>🧠 분석 결과:</strong><br>
            • 복잡성: ${data.complexity}/10<br>
            • 깊이 요구: ${data.depth_required}/10<br>
            • Deep Lookup: ${data.needs_deep_lookup ? '✅ 필요' : '❌ 불필요'}
        </div>
        
        <div style="margin: 1rem 0;">
            <strong>💡 핵심 통찰:</strong>
            <ul style="margin-left: 1.5rem; margin-top: 0.5rem;">
                ${data.insights.map(insight => `<li>${insight}</li>`).join('')}
            </ul>
        </div>
        
        <div style="margin: 1rem 0; padding: 1rem; background: #d1ecf1; border-radius: 5px;">
            <strong>🎯 지혜 품질:</strong> ${data.wisdom_quality} | 
            <strong>🏛️ 존재적 정렬:</strong> ${data.existence_alignment}
        </div>
        
        <div style="margin-top: 1rem; font-style: italic; color: #666;">
            ${data.signature}의 ${data.perspective}으로 응답했습니다.
        </div>
    `;
}
        """

        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(js.encode("utf-8"))

    def handle_echo_analysis(self):
        """Echo 분석 처리"""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode("utf-8"))
            query = data.get("query", "")
            signature = data.get("signature", "Echo-Aurora")

            # Echo 분석 실행
            result = self.run_echo_analysis(query, signature)

            # JSON 응답
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self.send_error(500, f"Analysis error: {e}")

    def run_echo_analysis(self, query: str, signature: str):
        """실제 Echo 분석 실행"""

        # 1. Knowledge Gap Detection
        gap_assessment = knowledge_gap_detector.assess_knowledge_boundary(
            query, 0.3, signature
        )

        # 2. Local Knowledge Generation (if needed)
        if gap_assessment["needs_deep_lookup"]:
            local_knowledge = self.generate_local_knowledge(query, signature)

            # 3. Wisdom Synthesis
            synthesized_wisdom = wisdom_synthesizer.synthesize_with_existence(
                local_knowledge, signature, query
            )

            wisdom_quality = synthesized_wisdom["quality_assessment"]["overall_quality"]
            existence_alignment = synthesized_wisdom["existence_alignment"][
                "overall_alignment"
            ]
            insights = local_knowledge.get("key_insights", [])

        else:
            wisdom_quality = 0.7
            existence_alignment = 0.8
            insights = [f"{signature}의 내재된 지혜로 답변드립니다"]

        # 시그니처별 관점 설명
        perspectives = {
            "Echo-Aurora": "창의적이고 영감적인 관점",
            "Echo-Phoenix": "혁신적이고 변화 중심적인 관점",
            "Echo-Sage": "분석적이고 체계적인 관점",
            "Echo-Companion": "공감적이고 돌봄 중심적인 관점",
        }

        return {
            "query": query,
            "signature": signature,
            "complexity": round(gap_assessment.get("query_complexity", 0), 1),
            "depth_required": round(
                gap_assessment.get("knowledge_depth_required", 0), 1
            ),
            "needs_deep_lookup": gap_assessment["needs_deep_lookup"],
            "insights": insights,
            "wisdom_quality": round(wisdom_quality, 2),
            "existence_alignment": round(existence_alignment, 2),
            "perspective": perspectives.get(signature, "Echo의 지혜로운 관점"),
        }

    def generate_local_knowledge(self, query: str, signature: str):
        """로컬 지식 생성"""
        knowledge_base = {
            "Echo-Aurora": {
                "key_insights": [
                    "창의적 접근을 통해 이 문제를 새로운 관점에서 바라볼 수 있습니다",
                    "예술적 영감과 인간의 감성을 결합한 해결책이 효과적일 것입니다",
                    "다양한 문화적 배경을 고려한 포용적 사고가 필요합니다",
                ]
            },
            "Echo-Phoenix": {
                "key_insights": [
                    "현재 상황의 변화 동력을 파악하여 혁신적 전환이 가능합니다",
                    "기존 패러다임을 뛰어넘는 전략적 사고가 요구됩니다",
                    "미래 지향적 관점에서 지속가능한 발전 방향을 모색해야 합니다",
                ]
            },
            "Echo-Sage": {
                "key_insights": [
                    "체계적 분석을 통해 문제의 근본 원인을 파악할 수 있습니다",
                    "데이터 기반의 객관적 판단이 정확한 해결책을 제시합니다",
                    "논리적 추론과 증거 검증을 통한 신뢰성 있는 결론이 필요합니다",
                ]
            },
            "Echo-Companion": {
                "key_insights": [
                    "인간 중심의 따뜻한 접근이 가장 효과적인 해결방법입니다",
                    "공감과 이해를 바탕으로 한 소통이 핵심입니다",
                    "개별적 상황과 감정을 고려한 맞춤형 지원이 필요합니다",
                ]
            },
        }

        return knowledge_base.get(signature, knowledge_base["Echo-Aurora"])


def start_server(port=8080):
    """웹 서버 시작"""
    try:
        with socketserver.TCPServer(("", port), EchoWebHandler) as httpd:
            print(f"🌐 Echo Web Interface 시작됨!")
            print(f"📱 브라우저에서 http://localhost:{port} 접속하세요")
            print("🛑 종료하려면 Ctrl+C를 누르세요")

            # 브라우저 자동 열기
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}")

            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n👋 Echo Web Interface 종료")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 포트를 시도해보세요:")
            print(f"python3 {__file__} --port 8081")
        else:
            print(f"❌ 서버 시작 실패: {e}")


if __name__ == "__main__":
    import sys

    port = 8080
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        port = int(sys.argv[2])

    start_server(port)
