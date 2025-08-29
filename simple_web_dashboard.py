#!/usr/bin/env python3
"""
🌐 Echo Judgment System v10 - Simple Web Dashboard
의존성 없이 작동하는 간단한 웹 대시보드

기능:
- 시스템 상태 모니터링
- 메타로그 조회
- 판단 루프 상태 확인
- Collapse 분석 결과 보기
"""

import http.server
import socketserver
import json
import os
import sys
import webbrowser
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import threading
import time


class EchoWebDashboard:
    """🌐 Echo 웹 대시보드"""

    def __init__(self, port=8080):
        self.port = port
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.meta_logs_dir = self.project_root / "meta_logs"
        self.judgment_loops_dir = self.project_root / "judgment_loops"

    def get_system_status(self):
        """시스템 상태 확인"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "files": {},
            "recent_activity": [],
        }

        # 핵심 컴포넌트 확인
        components = [
            "echo_engine/collapse_analyzer.py",
            "echo_engine/quantum_judgment_engine.py",
            "echo_engine/meta_log_enhanced.py",
            "echo_engine/judgment_loop_generator.py",
        ]

        for component in components:
            file_path = self.project_root / component
            status["components"][component] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "modified": (
                    datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    if file_path.exists()
                    else None
                ),
            }

        # 데이터 파일 확인
        data_files = ["logs.jsonl", "persona_profiles.json", "qtable.json"]
        for data_file in data_files:
            file_path = self.data_dir / data_file
            status["files"][data_file] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "modified": (
                    datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    if file_path.exists()
                    else None
                ),
            }

        # 최근 활동 확인
        if self.meta_logs_dir.exists():
            for log_file in sorted(
                self.meta_logs_dir.glob("*.jsonl"), key=os.path.getmtime, reverse=True
            )[:5]:
                status["recent_activity"].append(
                    {
                        "file": log_file.name,
                        "modified": datetime.fromtimestamp(
                            log_file.stat().st_mtime
                        ).isoformat(),
                        "size": log_file.stat().st_size,
                    }
                )

        return status

    def get_meta_logs(self, limit=20):
        """메타로그 조회"""
        logs = []

        if not self.meta_logs_dir.exists():
            return logs

        # 모든 .jsonl 파일에서 로그 수집
        for log_file in self.meta_logs_dir.glob("*.jsonl"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            log_data = json.loads(line.strip())
                            logs.append(log_data)
            except Exception as e:
                print(f"⚠️ 로그 파일 읽기 오류: {log_file}, {e}")

        # 타임스탬프 역순 정렬
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return logs[:limit]

    def get_judgment_loops(self):
        """판단 루프 목록 조회"""
        loops = []

        if not self.judgment_loops_dir.exists():
            return loops

        for loop_file in self.judgment_loops_dir.glob("*.json"):
            try:
                with open(loop_file, "r", encoding="utf-8") as f:
                    loop_data = json.load(f)
                    loops.append(
                        {
                            "file": loop_file.name,
                            "loop_id": loop_data.get("loop_id", "unknown"),
                            "title": loop_data.get("title", "Unknown"),
                            "domain": loop_data.get("domain", "unknown"),
                            "signature": loop_data.get("signature", "unknown"),
                            "created_at": loop_data.get("created_at", ""),
                        }
                    )
            except Exception as e:
                print(f"⚠️ 루프 파일 읽기 오류: {loop_file}, {e}")

        # 생성일 역순 정렬
        loops.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return loops

    def get_collapse_analyses(self):
        """Collapse 분석 결과 조회"""
        analyses = []

        for analysis_file in self.project_root.glob("analysis_*.json"):
            try:
                with open(analysis_file, "r", encoding="utf-8") as f:
                    analysis_data = json.load(f)
                    analyses.append(
                        {
                            "file": analysis_file.name,
                            "collapse_title": analysis_data.get(
                                "collapse_event", {}
                            ).get("title", "Unknown"),
                            "collapse_id": analysis_data.get("collapse_event", {}).get(
                                "collapse_id", "unknown"
                            ),
                            "generated_at": analysis_data.get("generated_at", ""),
                            "key_insight": (
                                analysis_data.get("analysis", {}).get(
                                    "meta_insights", [""]
                                )[0]
                                if analysis_data.get("analysis", {}).get(
                                    "meta_insights"
                                )
                                else ""
                            ),
                        }
                    )
            except Exception as e:
                print(f"⚠️ 분석 파일 읽기 오류: {analysis_file}, {e}")

        # 생성일 역순 정렬
        analyses.sort(key=lambda x: x.get("generated_at", ""), reverse=True)

        return analyses


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """대시보드 요청 핸들러"""

    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """GET 요청 처리"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self.serve_main_dashboard()
        elif path == "/api/status":
            self.serve_json(self.dashboard.get_system_status())
        elif path == "/api/meta-logs":
            self.serve_json(self.dashboard.get_meta_logs())
        elif path == "/api/judgment-loops":
            self.serve_json(self.dashboard.get_judgment_loops())
        elif path == "/api/collapse-analyses":
            self.serve_json(self.dashboard.get_collapse_analyses())
        else:
            self.send_error(404, "Not Found")

    def serve_main_dashboard(self):
        """메인 대시보드 HTML 제공"""
        html_content = self.generate_dashboard_html()

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

    def generate_dashboard_html(self):
        """대시보드 HTML 생성"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 Echo Judgment System v10 - Dashboard</title>
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
            max-width: 1200px;
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
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .card h2 {
            color: #4a5568;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-indicator {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-ok {
            background: #48bb78;
            color: white;
        }
        
        .status-error {
            background: #f56565;
            color: white;
        }
        
        .log-item {
            background: #f7fafc;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 4px solid #4299e1;
        }
        
        .log-meta {
            font-size: 0.8em;
            color: #718096;
            margin-top: 5px;
        }
        
        .refresh-btn {
            background: #4299e1;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #3182ce;
        }
        
        .loading {
            text-align: center;
            color: #718096;
            font-style: italic;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Echo Judgment System v10</h1>
            <p>존재 기반 AI 판단 시스템 - 실시간 대시보드</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- 시스템 상태 -->
            <div class="card">
                <h2>🔧 시스템 상태</h2>
                <div id="system-status" class="loading">로딩 중...</div>
                <button class="refresh-btn" onclick="loadSystemStatus()">새로고침</button>
            </div>
            
            <!-- 최근 메타로그 -->
            <div class="card">
                <h2>📜 최근 메타로그</h2>
                <div id="meta-logs" class="loading">로딩 중...</div>
                <button class="refresh-btn" onclick="loadMetaLogs()">새로고침</button>
            </div>
            
            <!-- 판단 루프 -->
            <div class="card">
                <h2>🔁 판단 루프</h2>
                <div id="judgment-loops" class="loading">로딩 중...</div>
                <button class="refresh-btn" onclick="loadJudgmentLoops()">새로고침</button>
            </div>
            
            <!-- Collapse 분석 -->
            <div class="card">
                <h2>🔬 Collapse 분석</h2>
                <div id="collapse-analyses" class="loading">로딩 중...</div>
                <button class="refresh-btn" onclick="loadCollapseAnalyses()">새로고침</button>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 실시간 업데이트 • 마지막 새로고침: <span id="last-update">-</span></p>
        </div>
    </div>

    <script>
        // API 호출 함수
        async function fetchData(endpoint) {
            try {
                const response = await fetch(`/api/${endpoint}`);
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
                return null;
            }
        }
        
        // 시스템 상태 로드
        async function loadSystemStatus() {
            const container = document.getElementById('system-status');
            container.innerHTML = '<div class="loading">로딩 중...</div>';
            
            const data = await fetchData('status');
            if (!data) {
                container.innerHTML = '<div class="status-error">데이터 로드 실패</div>';
                return;
            }
            
            let html = '';
            
            // 컴포넌트 상태
            for (const [component, info] of Object.entries(data.components)) {
                const status = info.exists ? 'status-ok' : 'status-error';
                const statusText = info.exists ? '✅ 정상' : '❌ 없음';
                html += `
                    <div class="status-item">
                        <span>${component.split('/').pop()}</span>
                        <span class="status-indicator ${status}">${statusText}</span>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // 메타로그 로드
        async function loadMetaLogs() {
            const container = document.getElementById('meta-logs');
            container.innerHTML = '<div class="loading">로딩 중...</div>';
            
            const data = await fetchData('meta-logs');
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="loading">메타로그가 없습니다</div>';
                return;
            }
            
            let html = '';
            for (const log of data.slice(0, 5)) {
                html += `
                    <div class="log-item">
                        <strong>${log.title || 'Unknown'}</strong>
                        <div class="log-meta">
                            ${log.log_type} • ${log.resonance_level} • ${log.signature}
                            <br>
                            ${new Date(log.timestamp).toLocaleString('ko-KR')}
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // 판단 루프 로드
        async function loadJudgmentLoops() {
            const container = document.getElementById('judgment-loops');
            container.innerHTML = '<div class="loading">로딩 중...</div>';
            
            const data = await fetchData('judgment-loops');
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="loading">판단 루프가 없습니다</div>';
                return;
            }
            
            let html = '';
            for (const loop of data.slice(0, 5)) {
                html += `
                    <div class="log-item">
                        <strong>${loop.title}</strong>
                        <div class="log-meta">
                            도메인: ${loop.domain} • 시그니처: ${loop.signature}
                            <br>
                            ${new Date(loop.created_at).toLocaleString('ko-KR')}
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // Collapse 분석 로드
        async function loadCollapseAnalyses() {
            const container = document.getElementById('collapse-analyses');
            container.innerHTML = '<div class="loading">로딩 중...</div>';
            
            const data = await fetchData('collapse-analyses');
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="loading">Collapse 분석이 없습니다</div>';
                return;
            }
            
            let html = '';
            for (const analysis of data.slice(0, 3)) {
                html += `
                    <div class="log-item">
                        <strong>${analysis.collapse_title}</strong>
                        <div class="log-meta">
                            ${analysis.key_insight.substring(0, 80)}${analysis.key_insight.length > 80 ? '...' : ''}
                            <br>
                            ${new Date(analysis.generated_at).toLocaleString('ko-KR')}
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // 전체 데이터 로드
        function loadAllData() {
            loadSystemStatus();
            loadMetaLogs();
            loadJudgmentLoops();
            loadCollapseAnalyses();
            document.getElementById('last-update').textContent = new Date().toLocaleString('ko-KR');
        }
        
        // 초기 로드
        window.onload = loadAllData;
        
        // 자동 새로고침 (30초마다)
        setInterval(loadAllData, 30000);
    </script>
</body>
</html>
        """


def create_handler(dashboard):
    """핸들러 팩토리"""

    def handler(*args, **kwargs):
        return DashboardRequestHandler(*args, dashboard=dashboard, **kwargs)

    return handler


def main():
    """메인 실행"""
    dashboard = EchoWebDashboard()
    port = dashboard.port

    print(f"🌐 Echo Judgment System v10 - Simple Web Dashboard")
    print(f"=" * 60)
    print(f"🚀 서버 시작 중... 포트: {port}")

    # 웹서버 시작
    handler = create_handler(dashboard)

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"✅ 대시보드 준비 완료!")
        print(f"🔗 URL: http://localhost:{port}")
        print(f"💡 브라우저에서 위 URL을 열어서 대시보드를 확인하세요!")
        print(f"💡 서버를 종료하려면 Ctrl+C를 누르세요.")
        print()

        # 브라우저 자동 열기 (별도 스레드)
        def open_browser():
            time.sleep(2)  # 서버 시작 대기
            webbrowser.open(f"http://localhost:{port}")

        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 서버 종료됨")


if __name__ == "__main__":
    main()
