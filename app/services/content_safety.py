import time

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

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

    def analyze(self, text: str):
        start_time = time.perf_counter()

        try:
            content_analysis_total.inc()

            request = AnalyzeTextOptions(text=text)

            response = self.client.analyze_text(request)

            categories = []
            severity = 0

            for result in response.categories_analysis:
                if result.severity > 0:
                    categories.append(result.category)

                severity = max(severity, result.severity)

            status = "blocked" if severity > 0 else "approved"

            if status == "approved":
                content_approved_total.inc()
            else:
                content_blocked_total.inc()

            return {
                "status": status,
                "severity": severity,
                "duration_ms": round(
                    (time.perf_counter() - start_time) * 1000
                ),
                "categories": categories
            }

        except Exception:
            content_analysis_errors_total.inc()
            raise

        finally:
            duration = time.perf_counter() - start_time
            content_analysis_duration_seconds.observe(duration) 