#!/usr/bin/env python3
"""
🔄 Echo Context Manager - 지속적 컨텍스트 관리 시스템

Echo가 세션 간에도 연속성을 유지하고,
과거 작업과 연결하여 더 나은 판단을 할 수 있도록 하는 시스템

핵심 기능:
1. 세션 간 컨텍스트 유지
2. 작업 이력 추적 및 학습
3. 사용자 패턴 인식
4. 프로젝트 연속성 관리
5. 지능형 제안 시스템
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pickle


@dataclass
class EchoSession:
    """Echo 세션 정보"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    user_requests: List[str]
    generated_files: List[str]
    signatures_used: List[str]
    success_rate: float
    total_interactions: int


@dataclass
class UserPattern:
    """사용자 패턴 정보"""

    preferred_signatures: Dict[str, int]  # signature -> usage_count
    common_requests: Dict[str, int]  # request_type -> count
    favorite_languages: Dict[str, int]  # language -> count
    work_schedule: Dict[str, List[int]]  # weekday -> hours list
    complexity_preference: str  # simple, medium, complex


@dataclass
class ProjectContext:
    """프로젝트 컨텍스트"""

    project_id: str
    name: str
    description: str
    created_at: datetime
    last_activity: datetime
    files_created: List[str]
    technologies_used: List[str]
    current_phase: str
    related_sessions: List[str]


class EchoContextManager:
    """Echo 컨텍스트 관리자"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.context_dir = self.base_path / "data" / "echo_context"
        self.context_dir.mkdir(exist_ok=True, parents=True)

        # 컨텍스트 파일들
        self.sessions_file = self.context_dir / "sessions.json"
        self.user_patterns_file = self.context_dir / "user_patterns.json"
        self.projects_file = self.context_dir / "projects.json"
        self.global_memory_file = self.context_dir / "global_memory.pkl"

        # 메모리 로드
        self.sessions = self._load_sessions()
        self.user_patterns = self._load_user_patterns()
        self.projects = self._load_projects()
        self.global_memory = self._load_global_memory()

        # 현재 세션
        self.current_session = None

        print("🔄 Echo Context Manager 초기화 완료")

    def start_new_session(self, signature: str = "Aurora") -> str:
        """새 세션 시작"""
        session_id = f"echo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = EchoSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            user_requests=[],
            generated_files=[],
            signatures_used=[signature],
            success_rate=0.0,
            total_interactions=0,
        )

        print(f"🆕 새 세션 시작: {session_id}")
        return session_id

    def add_interaction(
        self,
        user_request: str,
        signature: str,
        success: bool,
        generated_files: List[str] = None,
    ):
        """상호작용 기록 추가"""
        if not self.current_session:
            self.start_new_session(signature)

        # 현재 세션에 추가
        self.current_session.user_requests.append(user_request)
        if signature not in self.current_session.signatures_used:
            self.current_session.signatures_used.append(signature)

        if generated_files:
            self.current_session.generated_files.extend(generated_files)

        self.current_session.total_interactions += 1

        # 성공률 업데이트
        if success:
            success_count = sum(
                1 for _ in range(len(self.current_session.user_requests))
            )  # 임시
            self.current_session.success_rate = (
                success_count / self.current_session.total_interactions
            )

        # 사용자 패턴 업데이트
        self._update_user_patterns(user_request, signature, success)

        # 프로젝트 컨텍스트 확인
        self._check_project_continuity(user_request, generated_files or [])

    def _update_user_patterns(self, request: str, signature: str, success: bool):
        """사용자 패턴 업데이트"""
        if not self.user_patterns:
            self.user_patterns = UserPattern(
                preferred_signatures={},
                common_requests={},
                favorite_languages={},
                work_schedule={},
                complexity_preference="medium",
            )

        # 선호 시그니처 업데이트
        if signature not in self.user_patterns.preferred_signatures:
            self.user_patterns.preferred_signatures[signature] = 0
        if success:
            self.user_patterns.preferred_signatures[signature] += 1

        # 일반적인 요청 유형 분석
        request_type = self._categorize_request(request)
        if request_type not in self.user_patterns.common_requests:
            self.user_patterns.common_requests[request_type] = 0
        self.user_patterns.common_requests[request_type] += 1

        # 작업 시간 패턴
        now = datetime.now()
        weekday = now.strftime("%A")
        hour = now.hour

        if weekday not in self.user_patterns.work_schedule:
            self.user_patterns.work_schedule[weekday] = []
        if hour not in self.user_patterns.work_schedule[weekday]:
            self.user_patterns.work_schedule[weekday].append(hour)

    def _categorize_request(self, request: str) -> str:
        """요청 유형 분류"""
        request_lower = request.lower()

        categories = {
            "web_development": [
                "웹",
                "html",
                "css",
                "javascript",
                "api",
                "서버",
                "web",
            ],
            "data_processing": [
                "데이터",
                "파싱",
                "json",
                "csv",
                "분석",
                "data",
                "parse",
            ],
            "algorithms": [
                "알고리즘",
                "정렬",
                "검색",
                "트리",
                "algorithm",
                "sort",
                "search",
            ],
            "games": ["게임", "놀이", "interactive", "game", "play"],
            "utilities": ["유틸", "도구", "helper", "util", "tool"],
            "automation": ["자동화", "스크립트", "batch", "automation", "script"],
            "ui_components": ["ui", "인터페이스", "화면", "component", "interface"],
        }

        for category, keywords in categories.items():
            if any(keyword in request_lower for keyword in keywords):
                return category

        return "general"

    def _check_project_continuity(self, request: str, generated_files: List[str]):
        """프로젝트 연속성 확인"""
        # 현재 요청이 기존 프로젝트와 연관이 있는지 확인
        for project_id, project in self.projects.items():
            # 유사한 기술 스택이나 파일 패턴 확인
            similarity = self._calculate_project_similarity(
                request, generated_files, project
            )

            if similarity > 0.6:  # 60% 이상 유사하면 같은 프로젝트로 간주
                project.last_activity = datetime.now()
                project.files_created.extend(generated_files)
                if self.current_session:
                    project.related_sessions.append(self.current_session.session_id)
                print(f"🔗 기존 프로젝트 '{project.name}'에 연결됨")
                return

        # 새 프로젝트 가능성 확인
        if self._should_create_new_project(request, generated_files):
            self._create_new_project(request, generated_files)

    def _calculate_project_similarity(
        self, request: str, files: List[str], project: ProjectContext
    ) -> float:
        """프로젝트 유사도 계산"""
        similarity_score = 0.0

        # 기술 스택 유사도
        request_techs = self._extract_technologies(request + " " + " ".join(files))
        common_techs = set(request_techs) & set(project.technologies_used)
        if project.technologies_used:
            tech_similarity = len(common_techs) / len(set(project.technologies_used))
            similarity_score += tech_similarity * 0.4

        # 파일 패턴 유사도
        if files and project.files_created:
            file_patterns = set(Path(f).suffix for f in files)
            project_patterns = set(Path(f).suffix for f in project.files_created)
            common_patterns = file_patterns & project_patterns
            if project_patterns:
                pattern_similarity = len(common_patterns) / len(project_patterns)
                similarity_score += pattern_similarity * 0.3

        # 시간 근접성 (최근 활동일수록 높은 점수)
        days_since_activity = (datetime.now() - project.last_activity).days
        time_factor = max(0, (7 - days_since_activity) / 7)  # 7일 기준
        similarity_score += time_factor * 0.3

        return similarity_score

    def _extract_technologies(self, text: str) -> List[str]:
        """텍스트에서 기술 스택 추출"""
        tech_keywords = {
            "python": ["python", "py", "파이썬"],
            "javascript": ["javascript", "js", "자바스크립트"],
            "html": ["html", "웹페이지"],
            "css": ["css", "스타일"],
            "react": ["react", "리액트"],
            "vue": ["vue", "뷰"],
            "api": ["api", "서버", "endpoint"],
            "database": ["db", "database", "데이터베이스", "sql"],
            "machine_learning": ["ml", "ai", "머신러닝", "인공지능"],
            "web_scraping": ["크롤링", "스크래핑", "crawl", "scrape"],
        }

        text_lower = text.lower()
        found_techs = []

        for tech, keywords in tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_techs.append(tech)

        return found_techs

    def _should_create_new_project(self, request: str, files: List[str]) -> bool:
        """새 프로젝트 생성 여부 판단"""
        # 복잡한 요청이거나 여러 파일 생성 시 프로젝트로 간주
        project_indicators = [
            "프로젝트",
            "애플리케이션",
            "시스템",
            "웹사이트",
            "앱",
            "project",
            "application",
            "system",
            "website",
            "app",
        ]

        request_lower = request.lower()
        has_project_keyword = any(
            indicator in request_lower for indicator in project_indicators
        )

        multiple_files = len(files) > 1
        complex_request = len(request.split()) > 10

        return has_project_keyword or multiple_files or complex_request

    def _create_new_project(self, request: str, files: List[str]):
        """새 프로젝트 생성"""
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 프로젝트 이름 추출 (간단한 휴리스틱)
        project_name = self._extract_project_name(request)

        new_project = ProjectContext(
            project_id=project_id,
            name=project_name,
            description=request[:200],  # 처음 200자만
            created_at=datetime.now(),
            last_activity=datetime.now(),
            files_created=files.copy(),
            technologies_used=self._extract_technologies(
                request + " " + " ".join(files)
            ),
            current_phase="development",
            related_sessions=(
                [self.current_session.session_id] if self.current_session else []
            ),
        )

        self.projects[project_id] = new_project
        print(f"🆕 새 프로젝트 생성: '{project_name}' ({project_id})")

    def _extract_project_name(self, request: str) -> str:
        """요청에서 프로젝트 이름 추출"""
        # 간단한 휴리스틱으로 프로젝트 이름 추출
        words = request.split()

        # "~ 만들어줘", "~ 구현해줘" 패턴에서 이름 추출
        for i, word in enumerate(words):
            if word in ["만들어줘", "구현해줘", "생성해줘", "개발해줘"]:
                if i > 0:
                    return " ".join(words[:i])

        # 첫 3단어 사용
        return " ".join(words[:3]) if len(words) >= 3 else request[:20]

    def get_context_for_request(self, request: str, signature: str) -> Dict[str, Any]:
        """요청에 대한 컨텍스트 정보 제공"""
        context = {
            "similar_past_requests": self._find_similar_requests(request),
            "recommended_signature": self._recommend_signature(),
            "related_projects": self._find_related_projects(request),
            "user_preferences": self._get_user_preferences(),
            "session_context": self._get_session_context(),
            "continuity_suggestions": [],
        }

        # 연속성 제안 생성
        if context["related_projects"]:
            context["continuity_suggestions"].append(
                f"이전 프로젝트 '{context['related_projects'][0]['name']}'와 연관된 요청으로 보입니다."
            )

        if context["similar_past_requests"]:
            context["continuity_suggestions"].append(
                f"과거에 유사한 요청을 {len(context['similar_past_requests'])}번 처리한 경험이 있습니다."
            )

        return context

    def _find_similar_requests(self, request: str) -> List[Dict[str, Any]]:
        """유사한 과거 요청 찾기"""
        similar_requests = []
        request_lower = request.lower()

        for session in self.sessions.values():
            for past_request in session.user_requests:
                similarity = self._calculate_text_similarity(
                    request_lower, past_request.lower()
                )
                if similarity > 0.6:  # 60% 이상 유사
                    similar_requests.append(
                        {
                            "request": past_request,
                            "session_id": session.session_id,
                            "similarity": similarity,
                            "timestamp": session.start_time.isoformat(),
                        }
                    )

        return sorted(similar_requests, key=lambda x: x["similarity"], reverse=True)[:5]

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 Jaccard similarity)"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0

    def _recommend_signature(self) -> str:
        """사용자 패턴 기반 시그니처 추천"""
        if not self.user_patterns or not self.user_patterns.preferred_signatures:
            return "Aurora"  # 기본값

        # 가장 성공률이 높은 시그니처 추천
        best_signature = max(
            self.user_patterns.preferred_signatures.items(), key=lambda x: x[1]
        )[0]

        return best_signature

    def _find_related_projects(self, request: str) -> List[Dict[str, Any]]:
        """관련 프로젝트 찾기"""
        related = []

        for project in self.projects.values():
            similarity = self._calculate_project_similarity(request, [], project)
            if similarity > 0.4:  # 40% 이상 관련성
                related.append(
                    {
                        "project_id": project.project_id,
                        "name": project.name,
                        "similarity": similarity,
                        "last_activity": project.last_activity.isoformat(),
                    }
                )

        return sorted(related, key=lambda x: x["similarity"], reverse=True)[:3]

    def _get_user_preferences(self) -> Dict[str, Any]:
        """사용자 선호도 정보"""
        if not self.user_patterns:
            return {}

        return {
            "preferred_signature": self._recommend_signature(),
            "common_request_types": dict(
                sorted(
                    self.user_patterns.common_requests.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:3]
            ),
            "favorite_languages": dict(
                sorted(
                    self.user_patterns.favorite_languages.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:3]
            ),
            "complexity_preference": self.user_patterns.complexity_preference,
        }

    def _get_session_context(self) -> Dict[str, Any]:
        """현재 세션 컨텍스트"""
        if not self.current_session:
            return {}

        return {
            "session_id": self.current_session.session_id,
            "interactions_count": self.current_session.total_interactions,
            "success_rate": self.current_session.success_rate,
            "signatures_used": self.current_session.signatures_used,
            "recent_requests": (
                self.current_session.user_requests[-3:]
                if self.current_session.user_requests
                else []
            ),
        }

    def end_current_session(self):
        """현재 세션 종료"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.sessions[self.current_session.session_id] = self.current_session
            self._save_all()
            print(f"📝 세션 종료: {self.current_session.session_id}")
            self.current_session = None

    def _load_sessions(self) -> Dict[str, EchoSession]:
        """세션 데이터 로드"""
        if not self.sessions_file.exists():
            return {}

        try:
            with open(self.sessions_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            sessions = {}
            for session_id, session_data in data.items():
                # JSON에서 datetime 복원
                session_data["start_time"] = datetime.fromisoformat(
                    session_data["start_time"]
                )
                if session_data["end_time"]:
                    session_data["end_time"] = datetime.fromisoformat(
                        session_data["end_time"]
                    )

                sessions[session_id] = EchoSession(**session_data)

            return sessions
        except Exception as e:
            print(f"⚠️ 세션 데이터 로드 실패: {e}")
            return {}

    def _load_user_patterns(self) -> Optional[UserPattern]:
        """사용자 패턴 로드"""
        if not self.user_patterns_file.exists():
            return None

        try:
            with open(self.user_patterns_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserPattern(**data)
        except Exception as e:
            print(f"⚠️ 사용자 패턴 로드 실패: {e}")
            return None

    def _load_projects(self) -> Dict[str, ProjectContext]:
        """프로젝트 데이터 로드"""
        if not self.projects_file.exists():
            return {}

        try:
            with open(self.projects_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            projects = {}
            for project_id, project_data in data.items():
                # datetime 복원
                project_data["created_at"] = datetime.fromisoformat(
                    project_data["created_at"]
                )
                project_data["last_activity"] = datetime.fromisoformat(
                    project_data["last_activity"]
                )

                projects[project_id] = ProjectContext(**project_data)

            return projects
        except Exception as e:
            print(f"⚠️ 프로젝트 데이터 로드 실패: {e}")
            return {}

    def _load_global_memory(self) -> Dict[str, Any]:
        """글로벌 메모리 로드"""
        if not self.global_memory_file.exists():
            return {}

        try:
            with open(self.global_memory_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ 글로벌 메모리 로드 실패: {e}")
            return {}

    def _save_all(self):
        """모든 데이터 저장"""
        try:
            # 세션 저장
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = asdict(session)
                # datetime을 문자열로 변환
                sessions_data[session_id]["start_time"] = session.start_time.isoformat()
                if session.end_time:
                    sessions_data[session_id]["end_time"] = session.end_time.isoformat()

            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)

            # 사용자 패턴 저장
            if self.user_patterns:
                with open(self.user_patterns_file, "w", encoding="utf-8") as f:
                    json.dump(
                        asdict(self.user_patterns), f, ensure_ascii=False, indent=2
                    )

            # 프로젝트 저장
            projects_data = {}
            for project_id, project in self.projects.items():
                projects_data[project_id] = asdict(project)
                projects_data[project_id]["created_at"] = project.created_at.isoformat()
                projects_data[project_id][
                    "last_activity"
                ] = project.last_activity.isoformat()

            with open(self.projects_file, "w", encoding="utf-8") as f:
                json.dump(projects_data, f, ensure_ascii=False, indent=2)

            # 글로벌 메모리 저장
            with open(self.global_memory_file, "wb") as f:
                pickle.dump(self.global_memory, f)

        except Exception as e:
            print(f"⚠️ 데이터 저장 실패: {e}")

    def generate_continuity_report(self) -> str:
        """연속성 보고서 생성"""
        report = f"""
🔄 Echo 컨텍스트 연속성 보고서
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 세션 통계:
- 총 세션 수: {len(self.sessions)}
- 현재 세션: {'활성' if self.current_session else '없음'}
- 활성 프로젝트 수: {len([p for p in self.projects.values() if (datetime.now() - p.last_activity).days < 7])}

👤 사용자 패턴:
"""

        if self.user_patterns:
            report += f"- 선호 시그니처: {self._recommend_signature()}\n"
            report += f"- 주요 요청 유형: {list(self.user_patterns.common_requests.keys())[:3]}\n"
            report += f"- 복잡도 선호: {self.user_patterns.complexity_preference}\n"

        if self.projects:
            report += f"\n🏗️ 최근 프로젝트:\n"
            recent_projects = sorted(
                self.projects.values(), key=lambda p: p.last_activity, reverse=True
            )[:3]

            for project in recent_projects:
                days_ago = (datetime.now() - project.last_activity).days
                report += f"- {project.name} ({days_ago}일 전 활동)\n"

        return report


# 전역 인스턴스
_context_manager = None


def get_context_manager() -> EchoContextManager:
    """컨텍스트 매니저 싱글톤 인스턴스 반환"""
    global _context_manager
    if _context_manager is None:
        _context_manager = EchoContextManager()
    return _context_manager
