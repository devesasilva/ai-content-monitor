import os
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routes.analyze import router as analyze_router

connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

if connection_string:
    configure_azure_monitor(
        connection_string=connection_string,
        logger_name="azure_monitor"
    )

app = FastAPI(
    title="AI Content Monitor",
    description="API para análise e monitoramento de conteúdo",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "UP"}

app.include_router(analyze_router)

Instrumentator().instrument(app).expose(app)
