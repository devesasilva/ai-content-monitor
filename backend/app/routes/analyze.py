import time
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.exceptions.content_safety import ContentSafetyServiceError
from app.schemas.analyze import AnalyzeResponse
from app.services.content_safety import ContentSafetyService
from app.metrics import (
    content_analysis_total,
    content_approved_total,
    content_blocked_total,
    content_analysis_errors_total,
    content_analysis_duration_seconds,
)

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

    start_time = time.time()
    content_analysis_total.add(1)

    try:
        result = content_safety_service.analyze(
            text=text,
            image_bytes=image_bytes
        )

        if result.status.upper() in ["APPROVED", "OK", "SAFE"]:
            content_approved_total.add(1)
        else:
            content_blocked_total.add(1)

        return result

    except ContentSafetyServiceError as exc:
        content_analysis_errors_total.add(1)
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        content_analysis_errors_total.add(1)
        raise exc
    finally:
        duration = time.time() - start_time
        content_analysis_duration_seconds.record(duration)
