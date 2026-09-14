import os
import logging

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.monitor.opentelemetry").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)

connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

if connection_string:
    configure_azure_monitor(
        connection_string=connection_string,
        enable_live_metrics=False
    )

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="AI Content Monitor",
    description="API para análise e monitoramento de conteúdo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-content-monitor-frontend.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if connection_string:
    FastAPIInstrumentor.instrument_app(app)

@app.get("/health")
def health():
    return {"status": "UP"}

app.include_router(analyze_router)

Instrumentator().instrument(app).expose(app)
