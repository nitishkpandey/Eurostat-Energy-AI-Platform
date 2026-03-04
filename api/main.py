"""FastAPI application entry-point for the Eurostat Energy AI Platform."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import data, forecast, insights
from api.schemas import HealthResponse

app = FastAPI(
    title="Eurostat Energy AI Platform API",
    description="REST API for energy analytics, ML forecasting, and AI insights.",
    version="1.0.0",
)

# Allow the React dev-server (port 5173) and the production Nginx container
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(forecast.router)
app.include_router(insights.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok")
