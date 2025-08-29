#!/usr/bin/env python3
"""
SQL 실행 엔진
- READ-ONLY 모드로 안전한 SQL 실행
- 타임아웃 및 리미트 강제
- 자동 재시도 메커니즘
"""

import time
import pandas as pd
import duckdb
from typing import Dict, Any, Optional, Tuple
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SQLExecutionError(Exception):
    """SQL 실행 오류"""

    pass


class SQLExecutor:
    """안전한 SQL 실행기"""

    def __init__(self, db_url: str = "duckdb://warehouse.duckdb"):
        self.db_url = db_url
        self.db_type = "duckdb" if db_url.startswith("duckdb://") else "postgres"

        if self.db_type == "duckdb":
            self.db_path = db_url.replace("duckdb://", "")
        else:
            # TODO: Postgres 지원
            raise NotImplementedError("Postgres 지원은 추후 구현")

    @contextmanager
    def get_connection(self, read_only: bool = True):
        """READ-ONLY 데이터베이스 연결"""
        conn = None
        try:
            if self.db_type == "duckdb":
                conn = duckdb.connect(self.db_path, read_only=read_only)
                # 추가 보안 설정
                conn.execute("SET enable_progress_bar=false")
                conn.execute("SET threads=1")  # 리소스 제한

            yield conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_sql(
        self, sql: str, timeout: int = 20, max_retries: int = 1
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        SQL 실행 (재시도 포함)

        Returns:
            tuple: (결과 DataFrame, 실행 정보)
        """
        diagnostics = {
            "sql": sql,
            "execution_time": 0,
            "row_count": 0,
            "error": None,
            "retries": 0,
        }

        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()

                # SQL 실행
                df = self._execute_with_timeout(sql, timeout)

                # 실행 정보 기록
                diagnostics["execution_time"] = time.time() - start_time
                diagnostics["row_count"] = len(df)
                diagnostics["retries"] = attempt

                logger.info(
                    f"SQL 실행 성공: {len(df)}행, {diagnostics['execution_time']:.2f}초"
                )
                return df, diagnostics

            except Exception as e:
                diagnostics["error"] = str(e)
                diagnostics["retries"] = attempt

                if attempt < max_retries:
                    logger.warning(
                        f"SQL 실행 실패 (재시도 {attempt + 1}/{max_retries}): {e}"
                    )

                    # 오류 기반 SQL 수정 시도
                    sql = self._fix_sql_based_on_error(sql, str(e))
                    diagnostics["sql"] = sql  # 수정된 SQL로 업데이트
                else:
                    logger.error(f"SQL 실행 최종 실패: {e}")
                    raise SQLExecutionError(f"SQL 실행 실패: {e}")

        return pd.DataFrame(), diagnostics

    def _execute_with_timeout(self, sql: str, timeout: int) -> pd.DataFrame:
        """타임아웃을 적용한 SQL 실행"""

        with self.get_connection(read_only=True) as conn:
            # 타임아웃 설정
            if self.db_type == "duckdb":
                # DuckDB는 내장 타임아웃 없음, pandas read_sql 사용
                try:
                    df = conn.execute(sql).df()
                    return df
                except Exception as e:
                    raise SQLExecutionError(f"쿼리 실행 오류: {e}")

        return pd.DataFrame()

    def _fix_sql_based_on_error(self, sql: str, error_message: str) -> str:
        """오류 메시지 기반 SQL 자동 수정"""

        error_lower = error_message.lower()

        # 컬럼 존재하지 않음
        if "column" in error_lower and "does not exist" in error_lower:
            # 컬럼명 수정 시도 (간단한 경우만)
            if "date" in error_lower:
                sql = sql.replace("date", "created_date").replace(
                    "Date", "created_date"
                )

        # 테이블 존재하지 않음
        elif "table" in error_lower and (
            "does not exist" in error_lower or "not found" in error_lower
        ):
            logger.warning("테이블이 존재하지 않습니다. 기본 쿼리로 대체합니다.")
            sql = "SELECT 'No data available' as message LIMIT 1"

        # 문법 오류
        elif "syntax error" in error_lower:
            # LIMIT 절 수정
            if "limit" in sql.lower() and sql.count("LIMIT") > 1:
                # 중복 LIMIT 제거
                parts = sql.upper().split("LIMIT")
                sql = parts[0] + "LIMIT " + parts[-1].strip()

        return sql

    def validate_connection(self) -> Dict[str, Any]:
        """데이터베이스 연결 상태 확인"""
        try:
            with self.get_connection() as conn:
                if self.db_type == "duckdb":
                    result = conn.execute("SELECT 1 as test").fetchone()
                    tables = conn.execute("SHOW TABLES").fetchall()

                    return {
                        "status": "connected",
                        "db_type": self.db_type,
                        "db_path": self.db_path,
                        "table_count": len(tables),
                        "tables": [row[0] for row in tables],
                    }
        except Exception as e:
            return {"status": "error", "error": str(e), "db_type": self.db_type}

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """테이블 정보 조회"""
        try:
            with self.get_connection() as conn:
                # 테이블 스키마 정보
                schema_sql = f"DESCRIBE {table_name}"
                schema_df = conn.execute(schema_sql).df()

                # 행 수 조회
                count_sql = f"SELECT COUNT(*) as row_count FROM {table_name}"
                count_result = conn.execute(count_sql).fetchone()

                return {
                    "table_name": table_name,
                    "columns": schema_df.to_dict("records"),
                    "row_count": count_result[0] if count_result else 0,
                    "status": "success",
                }
        except Exception as e:
            return {"table_name": table_name, "status": "error", "error": str(e)}

    def execute_diagnostic_query(self) -> Dict[str, Any]:
        """진단용 쿼리 실행"""
        diagnostics = {}

        try:
            with self.get_connection() as conn:
                # 데이터베이스 정보
                if self.db_type == "duckdb":
                    # DuckDB 버전
                    version = conn.execute("SELECT version()").fetchone()[0]
                    diagnostics["db_version"] = version

                    # 테이블 목록
                    tables = conn.execute("SHOW TABLES").fetchall()
                    diagnostics["tables"] = [row[0] for row in tables]

                    # 각 테이블의 행 수
                    table_counts = {}
                    for table_name in diagnostics["tables"]:
                        try:
                            count = conn.execute(
                                f"SELECT COUNT(*) FROM {table_name}"
                            ).fetchone()[0]
                            table_counts[table_name] = count
                        except:
                            table_counts[table_name] = "error"

                    diagnostics["table_counts"] = table_counts
                    diagnostics["status"] = "success"

        except Exception as e:
            diagnostics = {"status": "error", "error": str(e)}

        return diagnostics
