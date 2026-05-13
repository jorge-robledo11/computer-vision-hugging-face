from pathlib import Path
import asyncio

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse

from src.config.config import (
    DEFAULT_PROMPT,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from src.utils.image_utils import (
    save_upload_to_temp,
    validate_image_extension,
)


router = APIRouter(tags=["images"])


@router.post("/describe-image")
async def describe_uploaded_image(
    request: Request,
    file: UploadFile = File(...),
    prompt: str | None = None,
):
    service = request.app.state.image_service

    try:
        suffix = validate_image_extension(
            file.filename or "",
            SUPPORTED_IMAGE_EXTENSIONS,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tmp_path: Path | None = None

    try:
        tmp_path = await save_upload_to_temp(file, suffix)

        description = await asyncio.to_thread(
            service.describe_image,
            tmp_path,
            prompt or DEFAULT_PROMPT,
        )

        return {
            "file": file.filename,
            "description": description,
        }

    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


@router.post("/describe-images")
async def describe_multiple_images(
    request: Request,
    files: list[UploadFile] = File(...),
    prompt: str | None = None,
):
    service = request.app.state.image_service
    results = []

    for file in files:
        tmp_path: Path | None = None

        try:
            suffix = validate_image_extension(
                file.filename or "",
                SUPPORTED_IMAGE_EXTENSIONS,
            )

            tmp_path = await save_upload_to_temp(file, suffix)

            description = await asyncio.to_thread(
                service.describe_image,
                tmp_path,
                prompt or DEFAULT_PROMPT,
            )

            results.append(
                {
                    "file": file.filename,
                    "description": description,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "file": file.filename,
                    "error": str(exc),
                }
            )

        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

    return JSONResponse(content={"results": results})