from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_settings, init_services
from app.services.llm_service import check_llm_connection
from app.routes.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load data and init services on startup."""
    settings = get_settings()
    print(f"Loading legal datasets from {settings.DATA_DIR}...")
    init_services()
    # Check LLM availability (cloud or local) and log for operators
    try:
        llm_ok = await check_llm_connection(settings, timeout_s=5.0)
        if llm_ok:
            print("LLM backend reachable — using configured provider.")
        else:
            print("Warning: LLM backend not reachable. Service will use fallback responses.")
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Warning: LLM health check failed: {exc}")
    print("Legal datasets loaded. Server ready.")
    yield
    print("Shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="LegalDoc AI Backend",
        version="2.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
