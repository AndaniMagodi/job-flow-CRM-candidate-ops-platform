from fastapi import FastAPI

from app.api.health import router as health_router
from app.auth.router import router as auth_router
from app.applications.router import router as applications_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(applications_router)

