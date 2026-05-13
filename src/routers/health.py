from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.config.config import PROJECT_ROOT


router = APIRouter(tags=["health"])


@router.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/scalar")


@router.get("/health")
def health(request: Request):
    service = request.app.state.image_service

    return {
        **service.health(),
        "project_root": str(PROJECT_ROOT),
    }