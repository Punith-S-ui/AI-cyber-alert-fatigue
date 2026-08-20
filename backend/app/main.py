from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.init_db import init_db
from app.api import auth, alerts, analysis, incidents, dashboard, ml


app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(analysis.router)
app.include_router(incidents.router)
app.include_router(dashboard.router)
app.include_router(ml.router)


@app.get("/")
def root():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
