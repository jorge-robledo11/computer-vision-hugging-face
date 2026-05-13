from pathlib import Path
import base64
import mimetypes
from tempfile import NamedTemporaryFile

from fastapi import UploadFile


def image_to_data_uri(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path)

    if mime_type is None:
        mime_type = "image/png"

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def validate_image_extension(filename: str, supported_extensions: set[str]) -> str:
    suffix = Path(filename or "").suffix.lower()

    if suffix not in supported_extensions:
        raise ValueError(
            f"Formato no soportado. Usa uno de: {sorted(supported_extensions)}"
        )

    return suffix


async def save_upload_to_temp(file: UploadFile, suffix: str) -> Path:
    """
    Guarda temporalmente un UploadFile y devuelve su ruta.
    """
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        return Path(tmp.name)