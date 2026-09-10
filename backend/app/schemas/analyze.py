from pydantic import BaseModel, Field

class AnalyzeResponse(BaseModel):
    status: str
    severity: int
    duration_ms: int
    categories: list[str]
    analyzed: dict[str, bool]