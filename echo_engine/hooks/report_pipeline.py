#!/usr/bin/env python3
"""
듀얼 파이프라인 훅 시스템
- 기계적 보고서 파이프라인 (mechanical)
- 의미 있는 보고서 파이프라인 (resonant)
- 통합 실행 및 오류 처리
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

# Echo 시스템 임포트
try:
    from echo_engine.sql.sql_builder import SQLBuilder
    from echo_engine.sql.sql_executor import SQLExecutor
    from echo_engine.rag.doc_indexer import DocumentIndexer
    from echo_engine.report.templater_mech import MechanicalReportTemplater
    from echo_engine.report.synthesizer_resonant import ResonantReportSynthesizer

    IMPORTS_SUCCESS = True
except ImportError as e:
    logging.warning(f"일부 모듈 임포트 실패: {e}")
    IMPORTS_SUCCESS = False

logger = logging.getLogger(__name__)


class ReportPipelineError(Exception):
    """리포트 파이프라인 오류"""

    pass


class ReportPipeline:
    """듀얼 리포트 파이프라인 통합 실행기"""

    def __init__(
        self,
        db_url: str = None,
        vector_store_path: str = "echo_engine/rag/vector_store",
        output_dir: str = "output/reports",
    ):

        # 환경 변수에서 DB URL 가져오기
        self.db_url = db_url or os.getenv("ECHO_DB_URL", "duckdb://warehouse.duckdb")
        self.vector_store_path = vector_store_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # 컴포넌트 초기화
        self.sql_builder = None
        self.sql_executor = None
        self.doc_indexer = None
        self.mechanical_templater = None
        self.resonant_synthesizer = None

        # 감사 로그
        self.audit_log = []

        logger.info(f"ReportPipeline 초기화: DB={self.db_url}")

    def _initialize_components(self):
        """필요시 컴포넌트 초기화"""
        if not IMPORTS_SUCCESS:
            raise ReportPipelineError("필요한 모듈들이 임포트되지 않았습니다")

        try:
            if not self.sql_builder:
                self.sql_builder = SQLBuilder()

            if not self.sql_executor:
                self.sql_executor = SQLExecutor(self.db_url)

            if not self.doc_indexer:
                self.doc_indexer = DocumentIndexer(
                    vector_store_path=self.vector_store_path
                )

            if not self.mechanical_templater:
                self.mechanical_templater = MechanicalReportTemplater(
                    str(self.output_dir)
                )

            if not self.resonant_synthesizer:
                self.resonant_synthesizer = ResonantReportSynthesizer()

        except Exception as e:
            logger.error(f"컴포넌트 초기화 실패: {e}")
            raise ReportPipelineError(f"초기화 오류: {e}")

    def run_pipeline(
        self, question: str, mode: str = "mechanical", signature: str = "Cosmos"
    ) -> Dict[str, Any]:
        """
        듀얼 파이프라인 실행

        Args:
            question: 자연어 질의
            mode: "mechanical" 또는 "resonant"
            signature: 시그니처 (resonant 모드에서만 사용)

        Returns:
            보고서 결과 딕셔너리
        """
        start_time = time.time()

        # 감사 로그 기록 시작
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "mode": mode,
            "signature": signature,
            "status": "started",
            "execution_time": 0,
            "errors": [],
        }

        try:
            # 1. 컴포넌트 초기화
            self._initialize_components()

            # 2. 모드 검증
            if mode not in ["mechanical", "resonant"]:
                raise ValueError("mode는 'mechanical' 또는 'resonant'여야 합니다")

            # 3. 스키마 로드 및 SQL 생성
            logger.info(f"질의 처리 시작: {question[:100]}...")
            sql = self.sql_builder.build_sql(question, signature)
            audit_entry["sql"] = sql

            # 4. SQL 실행
            df, sql_diagnostics = self.sql_executor.execute_sql(sql)
            audit_entry["sql_diagnostics"] = sql_diagnostics
            audit_entry["data_rows"] = len(df)

            logger.info(f"SQL 실행 완료: {len(df)}행 반환")

            # 5. 모드별 파이프라인 실행
            if mode == "mechanical":
                result = self._run_mechanical_pipeline(df, question)
            else:  # resonant
                result = self._run_resonant_pipeline(df, question, signature)

            # 6. 공통 메타데이터 추가
            result.update(
                {
                    "pipeline_info": {
                        "mode": mode,
                        "signature": signature if mode == "resonant" else None,
                        "sql_used": sql,
                        "sql_diagnostics": sql_diagnostics,
                        "execution_time": time.time() - start_time,
                        "timestamp": datetime.now().isoformat(),
                    }
                }
            )

            # 감사 로그 완료
            audit_entry.update(
                {
                    "status": "completed",
                    "execution_time": time.time() - start_time,
                    "result_type": result.get("type"),
                    "output_files": result.get("chart_paths", []),
                }
            )

            logger.info(
                f"파이프라인 완료: {mode} 모드, {audit_entry['execution_time']:.2f}초"
            )

        except Exception as e:
            # 오류 처리
            error_msg = str(e)
            audit_entry.update(
                {
                    "status": "failed",
                    "execution_time": time.time() - start_time,
                    "errors": [error_msg],
                }
            )

            logger.error(f"파이프라인 실패: {error_msg}")

            result = {
                "type": "error",
                "question": question,
                "mode": mode,
                "error": error_msg,
                "pipeline_info": {
                    "mode": mode,
                    "signature": signature,
                    "execution_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                },
                "status": "error",
            }

        finally:
            # 감사 로그 저장
            self.audit_log.append(audit_entry)
            self._save_audit_log(audit_entry)

        return result

    def _run_mechanical_pipeline(self, df, question: str) -> Dict[str, Any]:
        """기계적 파이프라인 실행"""
        logger.info("기계적 파이프라인 실행")

        # 기계적 보고서 생성
        result = self.mechanical_templater.build(df, question)

        # 보고서 파일 저장
        if result.get("html_report"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mechanical_report_{timestamp}"

            # HTML 저장
            html_path = self.mechanical_templater.export_report(
                result, filename, "html"
            )
            result["saved_files"] = [html_path]

        return result

    def _run_resonant_pipeline(
        self, df, question: str, signature: str
    ) -> Dict[str, Any]:
        """의미 있는 파이프라인 실행"""
        logger.info(f"의미 있는 파이프라인 실행: {signature} 시그니처")

        # 1. 컨텍스트 생성
        context = self._make_context_from_df(df, question)

        # 2. RAG 검색
        evidences = self.doc_indexer.search_topk(context, k=5)
        logger.info(f"RAG 검색 완료: {len(evidences)}개 근거 문서")

        # 3. 의미 있는 보고서 생성
        result = self.resonant_synthesizer.build(df, evidences, question, signature)

        # 4. 보고서 파일 저장
        if result.get("html_report"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resonant_report_{signature.lower()}_{timestamp}"

            # HTML 파일로 저장
            html_path = self.output_dir / f"{filename}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(result["html_report"])

            result["saved_files"] = [str(html_path)]
            logger.info(f"보고서 저장: {html_path}")

        return result

    def _make_context_from_df(self, df, question: str) -> str:
        """데이터프레임에서 RAG 검색용 컨텍스트 생성"""
        if df.empty:
            return question

        # 기본 정보
        context_parts = [question]
        context_parts.append(f"데이터: {len(df)}행 {len(df.columns)}개 컬럼")
        context_parts.append(
            f"컬럼: {', '.join(df.columns.tolist()[:5])}"
        )  # 상위 5개 컬럼

        # 수치형 데이터 요약
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols[:3]:  # 상위 3개
                total = df[col].sum()
                avg = df[col].mean()
                context_parts.append(f"{col}: 합계 {total:.0f}, 평균 {avg:.2f}")

        # 범주형 데이터 요약
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            top_values = df[col].value_counts().head(3)
            context_parts.append(
                f"{col} 상위값: {', '.join(top_values.index.tolist())}"
            )

        return " | ".join(context_parts)

    def _save_audit_log(self, audit_entry: Dict[str, Any]):
        """감사 로그 저장"""
        try:
            log_dir = self.output_dir / "audit_logs"
            log_dir.mkdir(exist_ok=True)

            log_file = (
                log_dir / f"pipeline_audit_{datetime.now().strftime('%Y%m')}.jsonl"
            )

            import json

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry, ensure_ascii=False, default=str) + "\n")

        except Exception as e:
            logger.error(f"감사 로그 저장 실패: {e}")

    def get_pipeline_status(self) -> Dict[str, Any]:
        """파이프라인 상태 확인"""
        try:
            self._initialize_components()

            # DB 연결 확인
            db_status = self.sql_executor.validate_connection()

            # RAG 인덱스 확인
            rag_status = self.doc_indexer.get_index_stats()

            # 스키마 확인
            schema_summary = (
                self.sql_builder.get_schema_summary() if self.sql_builder else {}
            )

            return {
                "status": "healthy",
                "database": db_status,
                "rag_index": rag_status,
                "schema": schema_summary,
                "output_directory": str(self.output_dir),
                "recent_requests": len(
                    [
                        log
                        for log in self.audit_log
                        if log.get("timestamp", "").startswith(
                            datetime.now().strftime("%Y-%m-%d")
                        )
                    ]
                ),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "database": {"status": "unknown"},
                "rag_index": {"status": "unknown"},
            }

    def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 생성된 보고서 목록"""
        try:
            # 출력 디렉토리에서 HTML 파일 찾기
            html_files = list(self.output_dir.glob("*.html"))
            html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            reports = []
            for html_file in html_files[:limit]:
                stat = html_file.stat()
                reports.append(
                    {
                        "filename": html_file.name,
                        "path": str(html_file),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": (
                            "mechanical"
                            if "mechanical" in html_file.name
                            else "resonant"
                        ),
                    }
                )

            return reports

        except Exception as e:
            logger.error(f"보고서 목록 조회 실패: {e}")
            return []

    def cleanup_old_reports(self, days: int = 30) -> int:
        """오래된 보고서 파일 정리"""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)

            cleaned_count = 0
            for html_file in self.output_dir.glob("*.html"):
                if html_file.stat().st_mtime < cutoff_time:
                    html_file.unlink()
                    cleaned_count += 1

            # 오래된 차트 파일도 정리
            for png_file in self.output_dir.glob("*.png"):
                if png_file.stat().st_mtime < cutoff_time:
                    png_file.unlink()
                    cleaned_count += 1

            logger.info(f"오래된 파일 {cleaned_count}개 정리 완료")
            return cleaned_count

        except Exception as e:
            logger.error(f"파일 정리 실패: {e}")
            return 0


# 편의 함수들
def run_mechanical_report(question: str, db_url: str = None) -> Dict[str, Any]:
    """기계적 보고서 생성 (편의 함수)"""
    pipeline = ReportPipeline(db_url=db_url)
    return pipeline.run_pipeline(question, mode="mechanical")


def run_resonant_report(
    question: str, signature: str = "Cosmos", db_url: str = None
) -> Dict[str, Any]:
    """의미 있는 보고서 생성 (편의 함수)"""
    pipeline = ReportPipeline(db_url=db_url)
    return pipeline.run_pipeline(question, mode="resonant", signature=signature)


def get_pipeline_health() -> Dict[str, Any]:
    """파이프라인 상태 확인 (편의 함수)"""
    pipeline = ReportPipeline()
    return pipeline.get_pipeline_status()


if __name__ == "__main__":
    # 테스트 실행
    pipeline = ReportPipeline()

    # 상태 확인
    status = pipeline.get_pipeline_status()
    print("Pipeline Status:", status)

    # 테스트 질의
    test_question = "최근 데이터 현황을 보여주세요"

    print(f"\n테스트 질의: {test_question}")

    # 기계적 보고서
    print("\n=== 기계적 보고서 테스트 ===")
    try:
        result = pipeline.run_pipeline(test_question, mode="mechanical")
        print(f"결과: {result.get('status', 'unknown')}")
        if result.get("saved_files"):
            print(f"저장된 파일: {result['saved_files']}")
    except Exception as e:
        print(f"기계적 보고서 오류: {e}")

    # 의미 있는 보고서
    print("\n=== 의미 있는 보고서 테스트 ===")
    try:
        result = pipeline.run_pipeline(
            test_question, mode="resonant", signature="Cosmos"
        )
        print(f"결과: {result.get('status', 'unknown')}")
        if result.get("saved_files"):
            print(f"저장된 파일: {result['saved_files']}")
    except Exception as e:
        print(f"의미 있는 보고서 오류: {e}")
