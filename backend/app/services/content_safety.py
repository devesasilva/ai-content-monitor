import base64
import time

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import (
    AnalyzeTextOptions,
    AnalyzeImageOptions,
    ImageData
)

from azure.core.credentials import AzureKeyCredential

from azure.core.exceptions import AzureError
from app.exceptions.content_safety import ContentSafetyServiceError

from app.config import (
    AZURE_CONTENT_SAFETY_ENDPOINT,
    AZURE_CONTENT_SAFETY_KEY,
)

from app.metrics import (
    content_analysis_total,
    content_analysis_errors_total,
    content_analysis_duration_seconds,
    content_approved_total,
    content_blocked_total,
)


class ContentSafetyService:

    def __init__(self):
        self.client = ContentSafetyClient(
            AZURE_CONTENT_SAFETY_ENDPOINT,
            AzureKeyCredential(AZURE_CONTENT_SAFETY_KEY)
        )

    def analyze_text(self, text: str):
        request = AnalyzeTextOptions(text=text)

        response = self.client.analyze_text(request)

        categories = []
        severity = 0

        for result in response.categories_analysis:
            if result.severity > 0:
                categories.append(result.category)

            severity = max(severity, result.severity)

        return {
            "severity": severity,
            "categories": categories
        }

    def analyze_image(self, image_bytes: bytes):
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        request = AnalyzeImageOptions(
            image=ImageData(content=encoded_image)
        )

        response = self.client.analyze_image(request)

        categories = []
        severity = 0

        for result in response.categories_analysis:
            if result.severity > 0:
                categories.append(result.category)

            severity = max(severity, result.severity)

        return {
            "severity": severity,
            "categories": categories
        }

    
    def analyze(self, text: str | None, image_bytes: bytes | None):
        start_time = time.perf_counter()

        try:
            content_analysis_total.add(1)

            analyzed_text = text is not None
            analyzed_image = image_bytes is not None

            if not analyzed_text and not analyzed_image:
                raise ValueError(
                    "É necessário informar texto, imagem ou ambos."
                )

            results = []

            if analyzed_text:
                results.append(self.analyze_text(text))

            if analyzed_image:
                results.append(self.analyze_image(image_bytes))

            severity = max(
                result["severity"]
                for result in results
            )

            categories = list({
                category
                for result in results
                for category in result["categories"]
            })

            status = "blocked" if severity > 0 else "approved"

            if status == "approved":
                content_approved_total.add(1)
            else:
                content_blocked_total.add(1)

            return {
                "status": status,
                "severity": severity,
                "duration_ms": round(
                    (time.perf_counter() - start_time) * 1000
                ),
                "categories": categories,
                "analyzed": {
                    "text": analyzed_text,
                    "image": analyzed_image
                }
            }

        except ValueError:
            raise

        except AzureError as exc:
            content_analysis_errors_total.add(1)

            raise ContentSafetyServiceError(
                "Não foi possível realizar a análise no Azure Content Safety."
            ) from exc

        except Exception:
            content_analysis_errors_total.add(1)
            raise

        finally:
            duration = time.perf_counter() - start_time
            content_analysis_duration_seconds.record(duration)
