"""
🎭 Capsule System FastAPI Router
캡슐 시스템 REST API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path

from echo_engine.tools.capsule_models import (
    CapsuleSpec,
    ExecutionContext,
    SimulationResult,
    CapsuleRegistry,
    CapsuleType,
)
from echo_engine.tools.capsule_cli import CapsuleEngine

router = APIRouter(prefix="/capsule", tags=["캡슐 시스템"])
engine = CapsuleEngine()


@router.get("/list", response_model=List[CapsuleSpec])
async def list_capsules(type_filter: Optional[str] = None):
    """등록된 캡슐 목록 조회"""
    try:
        filter_type = CapsuleType(type_filter) if type_filter else None
        return engine.registry.list_capsules(type_filter=filter_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"잘못된 타입: {type_filter}")


@router.get("/info/{capsule_name}", response_model=CapsuleSpec)
async def get_capsule_info(capsule_name: str):
    """캡슐 상세 정보 조회"""
    capsule = engine.registry.get_capsule(capsule_name)
    if not capsule:
        raise HTTPException(
            status_code=404, detail=f"캡슐 '{capsule_name}'을 찾을 수 없습니다"
        )
    return capsule


@router.post("/validate", response_model=Dict[str, Any])
async def validate_capsule(capsule: CapsuleSpec):
    """캡슐 사양 검증"""
    errors = engine.validate_capsule_spec(capsule)
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "capsule_name": capsule.name,
    }


@router.post("/register", response_model=Dict[str, str])
async def register_capsule(capsule: CapsuleSpec):
    """캡슐 등록"""
    # 검증
    errors = engine.validate_capsule_spec(capsule)
    if errors:
        raise HTTPException(
            status_code=400, detail=f"캡슐 검증 실패: {', '.join(errors)}"
        )

    # 등록
    engine.registry.register_capsule(capsule)
    engine._save_registry()

    return {"status": "success", "message": f"캡슐 '{capsule.name}' 등록 완료"}


@router.post("/simulate/{capsule_name}", response_model=SimulationResult)
async def simulate_capsule(capsule_name: str, context: ExecutionContext):
    """캡슐 시뮬레이션 실행"""
    capsule = engine.registry.get_capsule(capsule_name)
    if not capsule:
        raise HTTPException(
            status_code=404, detail=f"캡슐 '{capsule_name}'을 찾을 수 없습니다"
        )

    try:
        result = engine.simulate_capsule(capsule, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시뮬레이션 실패: {str(e)}")


@router.post("/upload", response_model=Dict[str, str])
async def upload_capsule_yaml(file: UploadFile = File(...)):
    """YAML 파일 업로드로 캡슐 등록"""
    if not file.filename.endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="YAML 파일만 업로드 가능합니다")

    try:
        contents = await file.read()
        capsule_data = yaml.safe_load(contents.decode("utf-8"))
        capsule = CapsuleSpec(**capsule_data)

        # 검증
        errors = engine.validate_capsule_spec(capsule)
        if errors:
            raise HTTPException(
                status_code=400, detail=f"캡슐 검증 실패: {', '.join(errors)}"
            )

        # 등록
        engine.registry.register_capsule(capsule)
        engine._save_registry()

        return {
            "status": "success",
            "message": f"캡슐 '{capsule.name}' 업로드 및 등록 완료",
            "filename": file.filename,
        }

    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML 파싱 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_capsule_stats():
    """캡슐 시스템 통계"""
    capsules = engine.registry.list_capsules()

    type_counts = {}
    for capsule in capsules:
        type_counts[capsule.type.value] = type_counts.get(capsule.type.value, 0) + 1

    total_rules = sum(len(capsule.rules) for capsule in capsules)
    avg_rules = total_rules / len(capsules) if capsules else 0

    return {
        "total_capsules": len(capsules),
        "type_distribution": type_counts,
        "total_rules": total_rules,
        "average_rules_per_capsule": round(avg_rules, 2),
        "registry_path": str(engine.registry_path),
    }


@router.delete("/remove/{capsule_name}", response_model=Dict[str, str])
async def remove_capsule(capsule_name: str):
    """캡슐 제거"""
    if capsule_name not in engine.registry.capsules:
        raise HTTPException(
            status_code=404, detail=f"캡슐 '{capsule_name}'을 찾을 수 없습니다"
        )

    del engine.registry.capsules[capsule_name]
    engine._save_registry()

    return {"status": "success", "message": f"캡슐 '{capsule_name}' 제거 완료"}


@router.post("/batch-simulate", response_model=List[SimulationResult])
async def batch_simulate(capsule_names: List[str], context: ExecutionContext):
    """여러 캡슐 배치 시뮬레이션"""
    results = []

    for capsule_name in capsule_names:
        capsule = engine.registry.get_capsule(capsule_name)
        if not capsule:
            results.append(
                SimulationResult(
                    capsule_name=capsule_name,
                    input_context=context,
                    triggered_rules=[f"ERROR: 캡슐 '{capsule_name}' 없음"],
                    output_actions=[],
                    emotional_state={},
                    execution_time_ms=0.0,
                    confidence_score=0.0,
                )
            )
        else:
            try:
                result = engine.simulate_capsule(capsule, context)
                results.append(result)
            except Exception as e:
                results.append(
                    SimulationResult(
                        capsule_name=capsule_name,
                        input_context=context,
                        triggered_rules=[f"ERROR: {str(e)}"],
                        output_actions=[],
                        emotional_state={},
                        execution_time_ms=0.0,
                        confidence_score=0.0,
                    )
                )

    return results
