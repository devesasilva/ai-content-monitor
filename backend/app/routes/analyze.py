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
        if text == "":
            text = None

    image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            image_bytes = None

    has_text = text is not None
    has_image = image_bytes is not None

    if not has_text and not has_image:
        raise HTTPException(
            status_code=400,
            detail="É necessário informar texto, imagem ou ambos."
        )

    input_type = "both" if (has_text and has_image) else ("text" if has_text else "image")
    attributes = {"input_type": input_type}

    start_time = time.time()
    content_analysis_total.add(1, attributes)

    try:
        result = content_safety_service.analyze(
            text=text,
            image_bytes=image_bytes
        )

        status_str = str(result.status).upper()
        if status_str in ["APPROVED", "OK", "SAFE"]:
            content_approved_total.add(1, attributes)
        else:
            content_blocked_total.add(1, attributes)

        return result

    except ContentSafetyServiceError as exc:
        content_analysis_errors_total.add(1, {"error_type": "service_error", **attributes})
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        content_analysis_errors_total.add(1, {"error_type": "internal_error", **attributes})
        raise exc
    finally:
        duration = time.time() - start_time
        content_analysis_duration_seconds.record(duration, attributes)
