from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from src.config.config import MODELS_DIR
from src.inference.inference import ImageDescriptionService
from src.routers.health import router as health_router
from src.routers.images import router as images_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.image_service = ImageDescriptionService(
        models_dir=MODELS_DIR,
        n_ctx=8192,
        n_gpu_layers=-1,
        verbose=False,
        suppress_llama_logs=True,
    )

    yield

    app.state.image_service = None


app = FastAPI(
    title="Image Description API",
    description="API local para describir imágenes usando llama.cpp + Gemma GGUF multimodal.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


app.include_router(health_router)
app.include_router(images_router)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )