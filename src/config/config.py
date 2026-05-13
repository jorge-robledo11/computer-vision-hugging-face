from pathlib import Path


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

DEFAULT_PROMPT = (
    "Describe la imagen en español de forma clara y breve. "
    "Incluye también una lista corta de los elementos u objetos visibles."
)


def find_project_root(start: Path | None = None) -> Path:
    """
    Busca la raíz del proyecto subiendo directorios hasta encontrar
    un marcador típico del proyecto.
    """
    current = (start or Path(__file__)).resolve()

    if current.is_file():
        current = current.parent

    markers = {
        "pyproject.toml",
        ".git",
        "README.md",
        "uv.lock",
    }

    for path in [current, *current.parents]:
        if any((path / marker).exists() for marker in markers):
            return path

    # Fallback: si este archivo está en src/config/config.py,
    # parents[2] debería ser project_root.
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = find_project_root()

IMGS_DIR = PROJECT_ROOT / "imgs"
MODELS_DIR = PROJECT_ROOT / "models" / "gemma-4-E4B-it"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

IMGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)