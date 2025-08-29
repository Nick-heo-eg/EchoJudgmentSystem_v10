from pydantic import BaseModel


class JudgmentRequest(BaseModel):
    prompt: str


class JudgmentResponse(BaseModel):
    response: str
    strategy: str
    npi_score: dict
    claude_result: str
