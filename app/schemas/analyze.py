from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    status: str
    severity: int
    duration_ms: int
    categories: list[str]