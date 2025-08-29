#!/usr/bin/env python3
"""
SQL 생성 가드레일 시스템
- 자연어 질의를 안전한 READ-ONLY SQL로 변환
- 화이트리스트 기반 테이블/컬럼 제한
- 금지 키워드 차단 및 보안 가드레일
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SQLSecurityError(Exception):
    """SQL 보안 위반 오류"""

    pass


class SQLBuilder:
    """안전한 SQL 생성기"""

    # 금지 키워드 (대소문자 무시)
    FORBIDDEN_KEYWORDS = {
        "UPDATE",
        "DELETE",
        "DROP",
        "INSERT",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "SP_",
        "XP_",
        "--",
        "/*",
        "*/",
        "UNION",
        "SCRIPT",
        "DECLARE",
        "CURSOR",
    }

    def __init__(self, schema_meta_path: str = None):
        if not schema_meta_path:
            schema_meta_path = Path(__file__).parent / "schema_meta.json"

        self.schema_meta = self._load_schema_meta(schema_meta_path)
        self.allowed_tables = set(self.schema_meta.keys())
        self.allowed_columns = self._build_column_whitelist()

    def _load_schema_meta(self, path: str) -> Dict[str, Any]:
        """스키마 메타데이터 로드"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"스키마 메타파일을 찾을 수 없습니다: {path}")
            return {}

    def _build_column_whitelist(self) -> Dict[str, set]:
        """테이블별 허용 컬럼 목록 생성"""
        whitelist = {}
        for table_name, table_meta in self.schema_meta.items():
            columns = {col["name"].lower() for col in table_meta.get("columns", [])}
            whitelist[table_name.lower()] = columns
        return whitelist

    def build_sql(self, question: str, signature: str = "default") -> str:
        """자연어 질의를 SQL로 변환"""

        # 1. LLM을 통한 SQL 생성
        raw_sql = self._generate_sql_with_llm(question, signature)

        # 2. 보안 검사
        self._validate_sql_security(raw_sql)

        # 3. 가드레일 적용
        safe_sql = self._apply_guardrails(raw_sql)

        logger.info(f"SQL 생성 완료: {question[:50]}...")
        return safe_sql

    def _generate_sql_with_llm(self, question: str, signature: str) -> str:
        """LLM을 사용한 SQL 생성"""

        # 스키마 정보 포맷팅
        schema_context = self._format_schema_for_prompt()

        # 시스템 프롬프트
        system_prompt = f"""너는 데이터 애널리스트다. 아래 스키마만 사용해 READ-ONLY SQL을 작성해라.

핵심 규칙:
- 화이트리스트 테이블/컬럼만 사용
- 항상 기간 필터와 LIMIT 100 포함
- 금지: UPDATE, DELETE, DROP, INSERT, ALTER
- 출력은 SQL만

스키마:
{schema_context}

사용자 질문: {question}

SQL:"""

        # TODO: LLM 호출 (실제 구현에서는 Echo 시그니처 시스템 사용)
        # 임시로 간단한 템플릿 기반 SQL 생성
        return self._template_based_sql(question)

    def _template_based_sql(self, question: str) -> str:
        """템플릿 기반 SQL 생성 (LLM 대체용)"""
        question_lower = question.lower()

        # 기본 테이블 선택 (첫 번째 테이블 사용)
        if not self.schema_meta:
            raise ValueError("스키마 메타데이터가 없습니다")

        table_name = list(self.schema_meta.keys())[0]
        table_meta = self.schema_meta[table_name]
        columns = [col["name"] for col in table_meta["columns"][:5]]  # 상위 5개 컬럼

        # 날짜 컬럼 찾기
        date_column = None
        for col in table_meta["columns"]:
            if "date" in col["name"].lower() or col["type"] == "TIMESTAMP":
                date_column = col["name"]
                break

        # 기본 SELECT 구문 생성
        select_columns = ", ".join(columns)
        sql = f"SELECT {select_columns} FROM {table_name}"

        # WHERE 절 추가 (기간 필터)
        if date_column:
            sql += f" WHERE {date_column} >= '2024-01-01'"
        else:
            sql += " WHERE 1=1"  # 기본 조건

        # 집계 처리
        if any(word in question_lower for word in ["합계", "총", "sum", "평균", "avg"]):
            numeric_cols = [
                col["name"]
                for col in table_meta["columns"]
                if col["type"] in ["INTEGER", "DOUBLE"]
            ]
            if numeric_cols:
                sql = f"SELECT COUNT(*) as count, SUM({numeric_cols[0]}) as total FROM {table_name}"
                if date_column:
                    sql += f" WHERE {date_column} >= '2024-01-01'"

        # 정렬 및 제한
        sql += f" ORDER BY {columns[0]} LIMIT 100"

        return sql

    def _validate_sql_security(self, sql: str):
        """SQL 보안 검사"""
        sql_upper = sql.upper()

        # 금지 키워드 검사
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                raise SQLSecurityError(f"금지된 키워드 발견: {keyword}")

        # 테이블 화이트리스트 검사
        used_tables = self._extract_table_names(sql)
        for table in used_tables:
            if table.lower() not in self.allowed_tables:
                raise SQLSecurityError(f"허용되지 않은 테이블: {table}")

        # 조인 제한 검사 (최대 3개)
        join_count = len(re.findall(r"\bJOIN\b", sql_upper))
        if join_count > 3:
            raise SQLSecurityError(f"조인 개수 초과: {join_count} (최대 3개)")

    def _extract_table_names(self, sql: str) -> List[str]:
        """SQL에서 테이블명 추출"""
        # 간단한 정규식 기반 추출 (FROM, JOIN 절)
        pattern = r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        return matches

    def _apply_guardrails(self, sql: str) -> str:
        """가드레일 적용"""
        sql = sql.strip()

        # LIMIT 강제 추가
        if "LIMIT" not in sql.upper():
            sql += " LIMIT 100"

        # 기간 필터 검사 (경고만)
        if not self._has_date_filter(sql):
            logger.warning("기간 필터가 없는 쿼리입니다")

        return sql

    def _has_date_filter(self, sql: str) -> bool:
        """기간 필터 존재 여부 확인"""
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"WHERE.*date",  # date 컬럼 필터
            r"WHERE.*time",  # time 컬럼 필터
        ]

        for pattern in date_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return True
        return False

    def _format_schema_for_prompt(self) -> str:
        """프롬프트용 스키마 포맷팅"""
        if not self.schema_meta:
            return "스키마 정보 없음"

        schema_text = []
        for table_name, table_meta in self.schema_meta.items():
            columns_info = []
            for col in table_meta["columns"]:
                sample_values = ", ".join(col["sample_values"][:2])
                columns_info.append(
                    f"  {col['name']} ({col['type']}) - 예시: {sample_values}"
                )

            schema_text.append(f"{table_name}:\n" + "\n".join(columns_info))

        return "\n\n".join(schema_text)

    def get_schema_summary(self) -> Dict[str, Any]:
        """스키마 요약 정보 반환"""
        return {
            "tables": list(self.allowed_tables),
            "total_columns": sum(len(cols) for cols in self.allowed_columns.values()),
            "schema_meta": self.schema_meta,
        }
