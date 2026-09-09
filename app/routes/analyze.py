from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.content_safety import ContentSafetyService


router = APIRouter()

content_safety_service = ContentSafetyService()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(request: AnalyzeRequest):
    return content_safety_service.analyze(request.text)