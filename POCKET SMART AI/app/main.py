from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, engine
from .routes import (
    auth,
    history,
    pages,
    planners,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts
    Base.metadata.create_all(bind=engine)

    yield

    # Application shutdown code can be added here later


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Budget-aware GenAI recommendation assistant",
    lifespan=lifespan,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# Application routers
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)
app.include_router(pages.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
    }


@app.get("/startup")
def startup():
    return {
        "status": "ready",
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
        "model": settings.gemini_model,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )