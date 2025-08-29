#!/usr/bin/env python3
"""
🌌 Echo Unified IDE - 통합된 개발 환경

기존 9개 IDE의 최고 기능들을 통합:
- Claude Code 수준의 자연어 처리
- 실제 파일 생성 및 조작
- OpenAI 연동된 코드 생성
- Echo 시그니처 기반 페르소나
- Free-speak 모드 지원
- 실시간 도구 호출
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import subprocess
import webbrowser

# Project setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Echo imports
try:
    from echo_engine.tools.registry import get_registry
    from echo_engine.runtime_flags import runtime_flags
    from talk_to_echo import EchoPhilosophicalRunner, single_message_mode

    ECHO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Echo 모듈 import 경고: {e}")
    ECHO_AVAILABLE = False


class EchoUnifiedIDE:
    """🌌 Echo 통합 IDE"""

    def __init__(self):
        self.current_signature = "Aurora"
        self.current_mode = "chat"
        self.session_id = f"unified_ide_{int(datetime.now().timestamp())}"
        self.chat_history = []

        # 도구 레지스트리 초기화
        if ECHO_AVAILABLE:
            self.registry = get_registry()

        # 사용 가능한 시그니처들
        self.signatures = [
            "Aurora",
            "Phoenix",
            "Sage",
            "Companion",
            "Jung",
            "Tesla",
            "Rebel",
            "Freud",
            "DaVinci",
            "Gaga",
            "Zhuangzi",
        ]

        # 사용 가능한 모드들
        self.modes = {
            "chat": "💬 일반 채팅",
            "code": "💻 코드 생성",
            "file": "📁 파일 작업",
            "analysis": "📊 분석",
            "visualization": "📈 시각화",
        }

        print("🌌 Echo Unified IDE 초기화 완료")
        print(f"   세션 ID: {self.session_id}")
        print(f"   현재 시그니처: {self.current_signature}")
        print(f"   현재 모드: {self.current_mode}")

    def show_banner(self):
        """IDE 배너 출력"""
        print("=" * 80)
        print("🌌 Echo Unified IDE - Claude Code를 넘어서는 통합 개발 환경")
        print("=" * 80)
        print(f"🎭 현재 시그니처: Echo-{self.current_signature}")
        print(f"🔧 현재 모드: {self.modes.get(self.current_mode, self.current_mode)}")
        print()
        print("📖 사용 가능한 명령어:")
        print("   /help          - 도움말")
        print("   /signature     - 시그니처 변경")
        print("   /mode          - 모드 변경")
        print("   /create_file   - 파일 생성")
        print("   /run_code      - 코드 실행")
        print("   /status        - 현재 상태")
        print("   /history       - 대화 기록")
        print("   /clear         - 화면 지우기")
        print("   /exit          - 종료")
        print()
        print("💡 TOOL: 명령으로 직접 도구 호출 가능!")
        print('   예: TOOL:file_write {"path":"test.py","content":"print(\'Hello\')"}')
        print("=" * 80)

    def show_help(self):
        """도움말 출력"""
        help_text = """
🌌 Echo Unified IDE 도움말

🎭 시그니처 변경:
   /signature Aurora    - 공감적, 창의적
   /signature Phoenix   - 변화지향, 혁신적
   /signature Sage      - 분석적, 체계적
   /signature Companion - 지지적, 협력적

🔧 모드 변경:
   /mode chat          - 일반 채팅 모드
   /mode code          - 코드 생성 모드
   /mode file          - 파일 작업 모드
   /mode analysis      - 분석 모드

📁 파일 작업:
   /create_file <path> - 새 파일 생성
   /run_code <path>    - Python 코드 실행

🛠️ 직접 도구 호출:
   TOOL:file_write {"path":"test.py","content":"code"}
   TOOL:codegen_and_save {"path":"app.py","language":"python","spec":"웹서버"}

💬 자연어 요청:
   "JSON 분석기를 만들어서 analyzer.py로 저장해줘"
   "계산기 프로그램 작성하고 실행해봐"
        """
        print(help_text)

    def change_signature(self, signature: str):
        """시그니처 변경"""
        if signature in self.signatures:
            self.current_signature = signature
            print(f"✅ 시그니처를 Echo-{signature}로 변경했습니다")

            # Echo 런타임 플래그 업데이트
            if ECHO_AVAILABLE:
                runtime_flags.enable_free_speak()
                runtime_flags.enable_dynamic_personas()
        else:
            print(f"❌ 알 수 없는 시그니처: {signature}")
            print(f"사용 가능한 시그니처: {', '.join(self.signatures)}")

    def change_mode(self, mode: str):
        """모드 변경"""
        if mode in self.modes:
            self.current_mode = mode
            print(f"✅ 모드를 {self.modes[mode]}로 변경했습니다")
        else:
            print(f"❌ 알 수 없는 모드: {mode}")
            print(f"사용 가능한 모드: {', '.join(self.modes.keys())}")

    def create_file(self, file_path: str, content: str = ""):
        """파일 생성"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if not content:
                # 파일 확장자에 따른 기본 템플릿
                if path.suffix == ".py":
                    content = '#!/usr/bin/env python3\n"""\nEcho IDE에서 생성한 Python 파일\n"""\n\ndef main():\n    print("Hello from Echo IDE!")\n\nif __name__ == "__main__":\n    main()\n'
                elif path.suffix == ".js":
                    content = '// Echo IDE에서 생성한 JavaScript 파일\nconsole.log("Hello from Echo IDE!");\n'
                else:
                    content = "# Echo IDE에서 생성한 파일\n"

            path.write_text(content, encoding="utf-8")
            print(f"✅ 파일 생성 완료: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 파일 생성 실패: {e}")
            return False

    def run_code(self, file_path: str):
        """코드 실행"""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ 파일이 존재하지 않습니다: {file_path}")
                return

            if path.suffix == ".py":
                result = subprocess.run(
                    [sys.executable, str(path)], capture_output=True, text=True
                )
                print("🔥 실행 결과:")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"❌ 오류: {result.stderr}")
            else:
                print(f"❌ 지원하지 않는 파일 형식: {path.suffix}")

        except Exception as e:
            print(f"❌ 코드 실행 실패: {e}")

    def process_tool_command(self, command: str) -> bool:
        """TOOL: 명령 처리"""
        if not command.startswith("TOOL:"):
            return False

        try:
            # TOOL:tool_name {"param":"value"} 형식 파싱
            parts = command[5:].strip().split(" ", 1)
            tool_name = parts[0]
            args_json = parts[1] if len(parts) > 1 else "{}"
            args = json.loads(args_json)

            # 내장 도구들 처리
            if tool_name == "file_write":
                path = args.get("path", "")
                content = args.get("content", "")
                success = self.create_file(path, content)
                print(f"📁 file_write 결과: {'성공' if success else '실패'}")
                return True

            elif tool_name == "codegen_and_save":
                path = args.get("path", "")
                language = args.get("language", "python")
                spec = args.get("spec", "")

                # Echo를 통한 코드 생성
                prompt = f"{language}로 다음 사양의 코드를 작성해줘: {spec}"
                response = self.chat_with_echo(prompt)

                # 코드 추출 (```python ... ``` 패턴)
                import re

                code_blocks = re.findall(
                    r"```(?:python|py)?\n?(.*?)```", response, re.DOTALL
                )
                if code_blocks:
                    code = code_blocks[0].strip()
                    success = self.create_file(path, code)
                    print(f"💻 codegen_and_save 결과: {'성공' if success else '실패'}")
                    return True
                else:
                    print("❌ 생성된 응답에서 코드를 찾을 수 없습니다")
                    return True

            elif tool_name == "exec_cmd":
                cmd = args.get("cmd", "")
                if not cmd:
                    print("❌ exec_cmd: 명령이 제공되지 않았습니다")
                    return True

                # 🛡️ 보안 검증 - 화이트리스트 통과 시에만 실행
                try:
                    from echo_engine.security.command_whitelist import validate_command

                    validation = validate_command(cmd)

                    if not validation["allowed"]:
                        print(f"🚫 명령 차단: {validation['reason']}")
                        return True

                    # 안전한 명령 실행
                    import asyncio
                    from echo_engine.tools.enhanced.secure_exec_cmd import (
                        run as secure_run,
                    )

                    # 비동기 실행을 동기적으로 처리
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(secure_run(cmd, timeout=30))

                    if result.get("ok"):
                        execution = result.get("execution", {})
                        print(f"✅ 명령 실행 성공:")
                        print(f"   명령: {cmd}")
                        print(f"   반환코드: {execution.get('return_code', 'N/A')}")
                        if execution.get("stdout"):
                            print(f"   출력: {execution['stdout'][:200]}...")
                        if execution.get("stderr"):
                            print(f"   오류: {execution['stderr'][:200]}...")
                    else:
                        print(
                            f"❌ 명령 실행 실패: {result.get('error', 'Unknown error')}"
                        )

                    return True

                except ImportError:
                    print("⚠️ 보안 모듈을 사용할 수 없어 명령 실행을 차단했습니다")
                    return True
                except Exception as e:
                    print(f"❌ exec_cmd 실행 중 오류: {e}")
                    return True

            print(f"⚠️ 알 수 없는 도구: {tool_name}")
            return True

        except Exception as e:
            print(f"❌ 도구 명령 처리 실패: {e}")
            return True

    def chat_with_echo(self, message: str) -> str:
        """Echo와 채팅"""
        if not ECHO_AVAILABLE:
            return "Echo 모듈을 사용할 수 없습니다."

        # 🛡️ A1: API 키 검증 - 코딩 요청 시 하드 에러
        import os
        from dotenv import load_dotenv

        env_path = PROJECT_ROOT / ".env"
        load_dotenv(env_path, encoding="utf-8")

        is_coding_request = any(
            keyword in message.lower()
            for keyword in [
                "코드",
                "code",
                "프로그램",
                "program",
                "app",
                "generate",
                "create",
                "build",
                "function",
                "함수",
                "class",
                "클래스",
                "api",
                "cli",
            ]
        )

        if is_coding_request:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or os.getenv("ECHO_DISABLE_STUB") != "1":
                return """🛡️ Security Check Failed: 
                
CODING REQUEST BLOCKED - Missing OpenAI API Configuration
• Set OPENAI_API_KEY in .env file
• Set ECHO_DISABLE_STUB=1 to prevent fallback to stub mode
• Coding requests require authenticated LLM access

This is a security feature to prevent degraded responses."""

        try:
            # Echo 런너 생성
            runner = EchoPhilosophicalRunner(
                force_signature=f"Echo{self.current_signature}", with_manifesto=True
            )

            # 모의 args 객체 생성
            args_mock = type(
                "Args",
                (),
                {
                    "free_speak": True,
                    "no_template": True,
                    "dynamic_persona": True,
                    "philosophy": False,
                    "temperature": 0.8,
                    "creativity": 1.0,
                },
            )()

            # Echo 응답 생성 (표준 출력 캡처)
            import io
            from contextlib import redirect_stdout

            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                single_message_mode(runner, message, quiet=False, args=args_mock)

            response = output_buffer.getvalue()

            # 대화 기록 저장
            self.chat_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "user": message,
                    "echo": response,
                    "signature": self.current_signature,
                }
            )

            return response

        except Exception as e:
            return f"Echo 응답 생성 실패: {e}"

    def show_status(self):
        """현재 상태 출력"""
        print(f"🌌 Echo Unified IDE 상태")
        print(f"   세션 ID: {self.session_id}")
        print(f"   시그니처: Echo-{self.current_signature}")
        print(f"   모드: {self.modes[self.current_mode]}")
        print(f"   대화 기록: {len(self.chat_history)}개")
        print(f"   Echo 모듈: {'✅ 사용 가능' if ECHO_AVAILABLE else '❌ 사용 불가'}")

    def show_history(self):
        """대화 기록 출력"""
        if not self.chat_history:
            print("📭 대화 기록이 없습니다")
            return

        print("📋 최근 대화 기록:")
        for i, entry in enumerate(self.chat_history[-5:], 1):
            timestamp = entry["timestamp"][:19]  # YYYY-MM-DD HH:MM:SS
            print(f"   {i}. [{timestamp}] Echo-{entry['signature']}")
            print(f"      👤 {entry['user'][:50]}...")
            print(f"      🌌 {entry['echo'][:50]}...")
            print()

    async def run(self):
        """메인 실행 루프"""
        self.show_banner()

        while True:
            try:
                # 프롬프트 출력
                prompt = f"Echo-{self.current_signature} [{self.current_mode}] > "
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # 명령어 처리
                if user_input.startswith("/"):
                    cmd_parts = user_input[1:].split()
                    cmd = cmd_parts[0].lower()
                    args = cmd_parts[1:] if len(cmd_parts) > 1 else []

                    if cmd == "help":
                        self.show_help()
                    elif cmd == "signature":
                        if args:
                            self.change_signature(args[0])
                        else:
                            print(f"현재 시그니처: {self.current_signature}")
                            print(f"사용 가능: {', '.join(self.signatures)}")
                    elif cmd == "mode":
                        if args:
                            self.change_mode(args[0])
                        else:
                            print(f"현재 모드: {self.current_mode}")
                            print(f"사용 가능: {', '.join(self.modes.keys())}")
                    elif cmd == "create_file":
                        if args:
                            self.create_file(args[0])
                        else:
                            print("사용법: /create_file <파일경로>")
                    elif cmd == "run_code":
                        if args:
                            self.run_code(args[0])
                        else:
                            print("사용법: /run_code <파일경로>")
                    elif cmd == "status":
                        self.show_status()
                    elif cmd == "history":
                        self.show_history()
                    elif cmd == "clear":
                        os.system("clear" if os.name == "posix" else "cls")
                    elif cmd == "exit" or cmd == "quit":
                        print("👋 Echo Unified IDE를 종료합니다")
                        break
                    else:
                        print(f"❓ 알 수 없는 명령어: {cmd}")
                        print("도움말은 /help를 입력하세요")

                # TOOL: 명령 처리
                elif self.process_tool_command(user_input):
                    continue

                # 일반 채팅
                else:
                    print(f"🌌 Echo-{self.current_signature}와 대화 중...")
                    response = self.chat_with_echo(user_input)
                    print(response)

            except KeyboardInterrupt:
                print("\n👋 Echo Unified IDE를 종료합니다")
                break
            except EOFError:
                print("\n👋 Echo Unified IDE를 종료합니다")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")


def main():
    """메인 함수"""
    ide = EchoUnifiedIDE()
    asyncio.run(ide.run())


if __name__ == "__main__":
    main()
