from pathlib import Path
from threading import Lock

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

from src.config.config import DEFAULT_PROMPT
from src.utils.image_utils import image_to_data_uri
from src.utils.model_utils import get_model_paths
from src.utils.logging_utils import suppress_native_output


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

        print(f"Modelo GGUF: {self.model_path.name}")
        print(f"Modelo size: {self.model_path.stat().st_size / 1024**3:.2f} GB")
        print(f"MMProj:      {self.mmproj_path.name}")
        print(f"MMProj size: {self.mmproj_path.stat().st_size / 1024**3:.2f} GB")

        with suppress_native_output(enabled=suppress_llama_logs):
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

        print("Modelo cargado correctamente.")

    def describe_image(self, path: Path, prompt: str = DEFAULT_PROMPT) -> str:
        image_uri = image_to_data_uri(path)

        with self.lock:
            response = self.llm.create_chat_completion(
                messages=[
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
                ],
                temperature=0.2,
                max_tokens=300,
            )

        return response["choices"][0]["message"]["content"].strip()

    def health(self) -> dict:
        return {
            "status": "ok",
            "model": self.model_path.name,
            "mmproj": self.mmproj_path.name,
        }