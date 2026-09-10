from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.exceptions.content_safety import ContentSafetyServiceError

from app.schemas.analyze import AnalyzeResponse
from app.services.content_safety import ContentSafetyService

router = APIRouter()

content_safety_service = ContentSafetyService()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(
    text: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
):
    if text is not None:
        text = text.strip()

    if not text and image is None:
        raise HTTPException(
            status_code=400,
            detail="É necessário informar texto, imagem ou ambos."
        )

    image_bytes = None

    if image:
        image_bytes = await image.read()

    try:
        return content_safety_service.analyze(
            text=text,
            image_bytes=image_bytes
        )

    except ContentSafetyServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc