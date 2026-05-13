from pathlib import Path


def pick_gguf_file(files: list[Path], preferences: list[str]) -> Path:
    """
    Selecciona un archivo GGUF usando un orden de preferencia.
    Si no encuentra coincidencias, devuelve el archivo más pequeño.
    """
    if not files:
        raise FileNotFoundError("No hay archivos GGUF candidatos.")

    files = sorted(files, key=lambda p: p.stat().st_size)

    for preference in preferences:
        match = next(
            (p for p in files if preference.lower() in p.name.lower()),
            None,
        )
        if match:
            return match

    return files[0]


def get_model_paths(models_dir: Path) -> tuple[Path, Path]:
    model_files = [
        p for p in models_dir.glob("*.gguf")
        if "mmproj" not in p.name.lower()
    ]

    if not model_files:
        raise FileNotFoundError(f"No encontré ningún modelo .gguf en {models_dir}")

    model_path = pick_gguf_file(
        files=model_files,
        preferences=[
            "Q5_K_M",
            "Q5_K_S",
            "Q4_K_M",
            "Q4_K_S",
            "Q6_K",
            "Q8_0",
        ],
    )

    mmproj_files = [
        p for p in models_dir.glob("*.gguf")
        if "mmproj" in p.name.lower()
    ]

    if not mmproj_files:
        raise FileNotFoundError(
            f"No encontré ningún mmproj*.gguf en {models_dir}. "
            "Para describir imágenes necesitas el proyector visual."
        )

    mmproj_path = pick_gguf_file(
        files=mmproj_files,
        preferences=[
            "BF16",
            "F16",
            "F32",
        ],
    )

    return model_path, mmproj_path