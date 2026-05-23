from pathlib import Path
from threading import Lock
from time import perf_counter

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

from src.config.config import DEFAULT_PROMPT
from src.observability.metrics import (
    IMAGE_DESCRIPTION_DURATION_SECONDS,
    IMAGE_DESCRIPTION_ERRORS_TOTAL,
    IMAGE_DESCRIPTION_REQUESTS_TOTAL,
    MODEL_INFO,
    MODEL_LOADED,
)
from src.utils.image_utils import image_to_data_uri
from src.utils.logging_utils import suppress_native_output
from src.utils.model_utils import get_model_paths


class ImageDescriptionService:
    def __init__(
        self,
        models_dir: Path,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,
        verbose: bool = False,
        suppress_llama_logs: bool = True,
    ) -> None:
        self.model_path, self.mmproj_path = get_model_paths(models_dir)
        self.lock = Lock()
        self.suppress_llama_logs = suppress_llama_logs

        print(f"Modelo GGUF: {self.model_path.name}")
        print(f"Modelo size: {self.model_path.stat().st_size / 1024**3:.2f} GB")
        print(f"MMProj:      {self.mmproj_path.name}")
        print(f"MMProj size: {self.mmproj_path.stat().st_size / 1024**3:.2f} GB")

        try:
            with suppress_native_output(enabled=self.suppress_llama_logs):
                chat_handler = Llava15ChatHandler(
                    clip_model_path=str(self.mmproj_path)
                )

                self.llm = Llama(
                    model_path=str(self.model_path),
                    chat_handler=chat_handler,
                    n_ctx=n_ctx,
                    n_gpu_layers=n_gpu_layers,
                    verbose=verbose,
                )

            MODEL_LOADED.set(1)

            MODEL_INFO.info(
                {
                    "model": self.model_path.name,
                    "mmproj": self.mmproj_path.name,
                    "n_ctx": str(n_ctx),
                    "n_gpu_layers": str(n_gpu_layers),
                }
            )

            print("Modelo cargado correctamente.")

        except Exception:
            MODEL_LOADED.set(0)
            raise

    def describe_image(self, path: Path, prompt: str = DEFAULT_PROMPT) -> str:
        start_time = perf_counter()

        try:
            image_uri = image_to_data_uri(path)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_uri,
                            },
                        },
                    ],
                }
            ]

            with self.lock:
                with suppress_native_output(enabled=self.suppress_llama_logs):
                    response = self.llm.create_chat_completion(
                        messages=messages,
                        temperature=0.2,
                        max_tokens=300,
                    )

            description = response["choices"][0]["message"]["content"].strip()

            IMAGE_DESCRIPTION_REQUESTS_TOTAL.labels(status="success").inc()

            return description

        except Exception as exc:
            IMAGE_DESCRIPTION_REQUESTS_TOTAL.labels(status="error").inc()
            IMAGE_DESCRIPTION_ERRORS_TOTAL.labels(
                error_type=type(exc).__name__
            ).inc()
            raise

        finally:
            duration = perf_counter() - start_time
            IMAGE_DESCRIPTION_DURATION_SECONDS.observe(duration)

    def health(self) -> dict:
        return {
            "status": "ok",
            "model": self.model_path.name,
            "mmproj": self.mmproj_path.name,
        }
