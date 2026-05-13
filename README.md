# Image Description API

API local para describir imágenes en español usando **Gemma 4 E4B-it** (GGUF) con **llama.cpp** como backend de inferencia.

Corre completamente en local, no requiere conexión a internet ni claves de API.

## Requisitos

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- GPU con soporte Vulkan/CUDA/Metal (recomendado) o CPU con suficiente RAM (~6 GB para Q5_K_M)
- [huggingface-cli](https://huggingface.co/docs/huggingface_hub/guides/cli) (`pip install huggingface_hub`)

## Instalación

```bash
# Clonar e instalar dependencias
uv sync

# Descargar el modelo multimodal (~5 GB)
bash scripts/download_vlm.sh
```

Esto descarga el modelo `unsloth/gemma-4-E4B-it-GGUF` con cuantización Q5_K_M y el proyector visual (`mmproj`) en `models/gemma-4-E4B-it/`.

## Uso

### Iniciar la API

```bash
bash scripts/start_api.sh
```

La API queda disponible en `http://localhost:8000`. La interfaz Scalar en [`/scalar`](http://localhost:8000/scalar) permite probar los endpoints interactivamente.

### Describir una imagen

```bash
curl -X POST http://localhost:8000/describe-image \
  -F "file=@imgs/frieren-winter.png"
```

Respuesta:

```json
{
  "file": "frieren-winter.png",
  "description": "Una ilustración de anime que muestra a un personaje con cabello blanco..."
}
```

### Describir múltiples imágenes

```bash
curl -X POST http://localhost:8000/describe-images \
  -F "files=@imgs/image1.jpg" \
  -F "files=@imgs/image2.jpg"
```

### Procesar todas las imágenes de un directorio

```bash
bash scripts/process_all_images.sh
```

Procesa en paralelo todas las imágenes en `imgs/` y guarda las descripciones JSON en `outputs/descriptions/`.

### Prompt personalizado

Cualquier endpoint acepta un parámetro `prompt` para cambiar la instrucción:

```bash
curl -X POST http://localhost:8000/describe-image \
  -F "file=@imgs/photo.jpg" \
  -F "prompt=Describe los colores predominantes de la imagen."
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del modelo y rutas |
| `GET` | `/scalar` | Documentación interactiva |
| `POST` | `/describe-image` | Describir una imagen (`file` + `prompt` opcional) |
| `POST` | `/describe-images` | Describir varias imágenes (`files` + `prompt` opcional) |

Formatos soportados: `.jpg`, `.jpeg`, `.png`, `.webp`.

## Estructura del proyecto

```
├── src/
│   ├── main.py                  # App FastAPI + lifespan
│   ├── config/config.py         # Rutas y constantes
│   ├── inference/inference.py   # Servicio de descripción (llama.cpp)
│   ├── routers/
│   │   ├── health.py            # /health, redirección raíz
│   │   └── images.py            # /describe-image, /describe-images
│   └── utils/
│       ├── image_utils.py       # Conversión a data URI, validación
│       ├── model_utils.py       # Selección de archivos GGUF
│       └── logging_utils.py     # Supresión de logs nativos
├── scripts/
│   ├── download_vlm.sh          # Descarga del modelo desde HuggingFace
│   ├── start_api.sh             # Inicio de la API en background
│   └── process_all_images.sh    # Procesamiento batch de imágenes
├── imgs/                        # Imágenes de entrada
├── outputs/                     # Descripciones generadas
└── models/                      # Modelos GGUF (gitignored)
```

## Configuración

El modelo y las rutas se configuran en `src/config/config.py`. Los scripts aceptan variables de entorno:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host de la API |
| `PORT` | `8000` | Puerto de la API |
| `API_URL` | `http://localhost:8000` | URL del API para `process_all_images.sh` |
| `CONCURRENCY` | `3` | Procesamiento paralelo |
