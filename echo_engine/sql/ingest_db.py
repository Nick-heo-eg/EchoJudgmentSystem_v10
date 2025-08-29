#!/usr/bin/env python3
"""
데이터 적재 및 스키마 메타데이터 생성 시스템
- CSV 파일을 DuckDB/Postgres로 적재
- schema_meta.json 자동 생성 (테이블/컬럼/타입/예시값)
- 환경 변수 ECHO_DB_URL 지원
"""

import argparse
import json
import os
import pandas as pd
import duckdb
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngester:
    """데이터 적재 및 스키마 메타데이터 생성"""

    def __init__(self, db_url: str = "duckdb://warehouse.duckdb"):
        self.db_url = db_url
        self.schema_meta = {}

        # DuckDB 연결 설정
        if db_url.startswith("duckdb://"):
            self.db_path = db_url.replace("duckdb://", "")
            self.conn = duckdb.connect(self.db_path)
            self.db_type = "duckdb"
            logger.info(f"DuckDB 연결: {self.db_path}")
        else:
            # TODO: Postgres 지원
            raise NotImplementedError("Postgres 지원은 추후 구현")

    def ingest_csv(self, csv_path: str, table_name: str = None) -> Dict[str, Any]:
        """CSV 파일을 데이터베이스로 적재"""
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

        # 테이블명 자동 생성
        if not table_name:
            table_name = csv_path.stem.lower().replace("-", "_").replace(" ", "_")

        logger.info(f"CSV 적재 시작: {csv_path} → {table_name}")

        try:
            # pandas로 CSV 읽기 (데이터 타입 추론)
            df = pd.read_csv(csv_path, encoding="utf-8")

            # DuckDB로 테이블 생성
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")

            # 스키마 메타데이터 생성
            table_meta = self._generate_table_meta(table_name, df)
            self.schema_meta[table_name] = table_meta

            logger.info(
                f"테이블 생성 완료: {table_name} ({len(df)} rows, {len(df.columns)} columns)"
            )
            return table_meta

        except Exception as e:
            logger.error(f"CSV 적재 실패: {e}")
            raise

    def _generate_table_meta(self, table_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """테이블 스키마 메타데이터 생성"""
        columns = []

        for col in df.columns:
            col_data = df[col].dropna()

            # 데이터 타입 추론
            dtype_str = str(df[col].dtype)
            if dtype_str.startswith("int"):
                sql_type = "INTEGER"
            elif dtype_str.startswith("float"):
                sql_type = "DOUBLE"
            elif dtype_str == "bool":
                sql_type = "BOOLEAN"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                sql_type = "TIMESTAMP"
            else:
                sql_type = "VARCHAR"

            # 예시값 상위 3개 (중복 제거)
            sample_values = col_data.unique()[:3].tolist() if len(col_data) > 0 else []

            columns.append(
                {
                    "name": col,
                    "type": sql_type,
                    "nullable": df[col].isnull().any(),
                    "sample_values": [str(v) for v in sample_values],
                }
            )

        return {
            "table_name": table_name,
            "row_count": len(df),
            "columns": columns,
            "description": f"Imported from CSV with {len(df)} rows",
        }

    def save_schema_meta(self, output_path: str = None):
        """스키마 메타데이터를 JSON 파일로 저장"""
        if not output_path:
            output_path = Path(__file__).parent / "schema_meta.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.schema_meta, f, ensure_ascii=False, indent=2)

        logger.info(f"스키마 메타데이터 저장: {output_path}")
        logger.info(f"총 테이블: {len(self.schema_meta)}개")

    def get_table_list(self) -> List[str]:
        """테이블 목록 조회"""
        result = self.conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]

    def close(self):
        """데이터베이스 연결 종료"""
        if hasattr(self, "conn"):
            self.conn.close()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="CSV 데이터 적재 및 스키마 생성")
    parser.add_argument("--src", required=True, help="CSV 파일 또는 디렉토리 경로")
    parser.add_argument(
        "--db", default="duckdb://warehouse.duckdb", help="데이터베이스 URL"
    )
    parser.add_argument("--output", help="스키마 메타데이터 출력 경로")

    args = parser.parse_args()

    # 환경 변수에서 DB URL 오버라이드
    db_url = os.getenv("ECHO_DB_URL", args.db)

    ingester = DataIngester(db_url)

    try:
        src_path = Path(args.src)

        if src_path.is_file() and src_path.suffix == ".csv":
            # 단일 CSV 파일 처리
            ingester.ingest_csv(str(src_path))
        elif src_path.is_dir():
            # 디렉토리 내 모든 CSV 파일 처리
            csv_files = list(src_path.glob("*.csv"))
            if not csv_files:
                logger.warning(f"CSV 파일을 찾을 수 없습니다: {src_path}")
                return

            for csv_file in csv_files:
                ingester.ingest_csv(str(csv_file))
        else:
            logger.error(f"유효하지 않은 경로: {src_path}")
            return

        # 스키마 메타데이터 저장
        ingester.save_schema_meta(args.output)

        # 테이블 목록 출력
        tables = ingester.get_table_list()
        print(f"\n✅ 적재 완료된 테이블: {', '.join(tables)}")

    finally:
        ingester.close()


if __name__ == "__main__":
    main()
