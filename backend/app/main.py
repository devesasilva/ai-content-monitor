from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

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

@app.get("/health")
def health():
    return {
        "status": "UP"
    }


app.include_router(analyze_router)

Instrumentator().instrument(app).expose(app)