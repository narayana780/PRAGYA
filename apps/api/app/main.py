from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    PragyaException,
    general_exception_handler,
    http_exception_handler,
    pragya_exception_handler,
)
from app.core.logging import logger, setup_logging

# Initialize structured logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and pre-warm application-scoped embedding provider during startup
    logger.info(f"Initializing embedding provider ({settings.EMBEDDING_PROVIDER})...")
    from app.modules.materials.embeddings import get_embedding_provider

    provider = get_embedding_provider()
    test_vec = provider.embed_text("PRAGYA system startup verification")
    if len(test_vec) != 384 and settings.EMBEDDING_PROVIDER.lower() not in ("mock", "hash", "mock_embedding"):
        raise RuntimeError(f"Embedding model dimension mismatch: expected 384, got {len(test_vec)}")
    logger.info(f"Embedding provider ready (model: {settings.EMBEDDING_MODEL}, dimension: {provider.dimension})")

    logger.info("PRAGYA API service initialized and ready.")
    yield
    logger.info("PRAGYA API service shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PRAGYA: AI-Powered Competency & Workforce Intelligence Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register standardized exception handlers
app.add_exception_handler(PragyaException, pragya_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Root level health check conforming to exact specification
@app.get("/health", tags=["Health"])
async def root_health():
    return {
        "status": "ok",
        "service": "pragya-api",
        "version": settings.VERSION,
    }

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
