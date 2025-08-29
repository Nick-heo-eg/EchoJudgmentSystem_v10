from fastapi import APIRouter
from api.schema import JudgmentRequest, JudgmentResponse
from api.npi import evaluate_npi
from api.nunchi_response_engine import generate_response
from api.log_writer import write_log
from api.llm_runner import run_claude_judgment

router = APIRouter()


@router.post("/judge", response_model=JudgmentResponse)
def judge(request: JudgmentRequest):
    npi_score = evaluate_npi(request.prompt)
    claude_result = run_claude_judgment(request.prompt)

    # Claude 결과를 문자열로 변환
    claude_result_str = (
        claude_result.get("judgment", str(claude_result))
        if isinstance(claude_result, dict)
        else str(claude_result)
    )

    response, strategy = generate_response(request.prompt, npi_score, claude_result_str)
    write_log(request.prompt, npi_score, strategy, response, claude_result_str)

    return JudgmentResponse(
        response=response,
        strategy=strategy,
        npi_score=npi_score,
        claude_result=claude_result_str,
    )
