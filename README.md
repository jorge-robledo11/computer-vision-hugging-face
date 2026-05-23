# Image Description API

API local para describir imágenes en español usando **Gemma 4 E4B-it** (GGUF cuantizado) con **llama-cpp-python** como backend de inferencia y **FastAPI** como servidor HTTP.

Corre completamente en local. No requiere conexión a internet ni claves de API externas.

## Stack

- **Modelo**: `unsloth/gemma-4-E4B-it-GGUF` (Q5\_K\_M) — multimodal con proyector visual (`mmproj`)
- **Inferencia**: `llama-cpp-python` (llama.cpp)
- **Servidor**: FastAPI + Uvicorn
- **Observabilidad**: Prometheus + Grafana (Docker)
- **Documentación interactiva**: Scalar (`/scalar`)
- **Gestión de paquetes**: `uv`

## Requisitos

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)
- GPU con soporte Vulkan / CUDA / Metal (recomendado) o CPU con ~6 GB de RAM libres para Q5\_K\_M
- [huggingface-cli](https://huggingface.co/docs/huggingface_hub/guides/cli) — `pip install huggingface_hub`
- Docker + Docker Compose (solo para observabilidad, opcional)

## Instalación

```bash
# 1. Instalar dependencias Python
uv sync

# 2. Descargar el modelo multimodal (~5 GB)
bash scripts/download_vlm.sh
```

El script descarga el modelo `unsloth/gemma-4-E4B-it-GGUF` con cuantización Q5\_K\_M y el proyector visual en `models/gemma-4-E4B-it/`.

## Uso rápido con Make

```bash
make help            # Lista todos los comandos disponibles
make api-start       # Levanta la API en background
make api-stop        # Detiene la API
make process-images  # Procesa todas las imágenes en imgs/
make obs-start       # Levanta Prometheus + Grafana
make obs-stop        # Detiene Prometheus + Grafana
make context         # Genera context/repomix-output.xml del proyecto
```

## API

### Iniciar

```bash
bash scripts/start_api.sh
# o
make api-start
```

La API queda disponible en `http://localhost:8000`.
La documentación interactiva Scalar está en [`/scalar`](http://localhost:8000/scalar).

### Detener

```bash
bash scripts/stop_api.sh
# o
make api-stop
```

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

Respuesta:

```json
{
  "results": [
    { "file": "image1.jpg", "description": "..." },
    { "file": "image2.jpg", "description": "..." }
  ]
}
```

### Procesar un directorio completo

```bash
bash scripts/process_all_images.sh
# o
make process-images
```

Procesa en paralelo todas las imágenes en `imgs/` y guarda una descripción JSON por imagen en `outputs/descriptions/`.

### Prompt personalizado

Todos los endpoints aceptan el parámetro `prompt` opcional:

```bash
curl -X POST http://localhost:8000/describe-image \
  -F "file=@imgs/photo.jpg" \
  -F "prompt=Describe los colores predominantes de la imagen."
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del modelo y rutas del proyecto |
| `GET` | `/scalar` | Documentación interactiva |
| `GET` | `/metrics` | Métricas Prometheus |
| `POST` | `/describe-image` | Describir una imagen (`file` + `prompt` opcional) |
| `POST` | `/describe-images` | Describir varias imágenes (`files` + `prompt` opcional) |

Formatos de imagen soportados: `.jpg`, `.jpeg`, `.png`, `.webp`.

## Observabilidad

Prometheus y Grafana se levantan con Docker Compose:

```bash
make obs-start   # Levanta ambos servicios
make obs-status  # Muestra estado y targets activos
make obs-stop    # Detiene ambos servicios
```

- **Prometheus**: `http://localhost:9090` — scraping cada 5 s sobre `/metrics`
- **Grafana**: `http://localhost:3000` — datasource Prometheus preconfigurado

### Métricas expuestas

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `image_description_requests_total` | Counter | Total de requests por estado (`success` / `error`) |
| `image_description_duration_seconds` | Histogram | Tiempo de inferencia por imagen |
| `image_description_errors_total` | Counter | Errores por tipo de excepción |
| `image_model_loaded` | Gauge | `1` si el modelo está cargado, `0` si no |
| `image_model_info` | Info | Nombre del modelo, mmproj, `n_ctx`, `n_gpu_layers` |

## Configuración

Rutas y constantes se configuran en `src/config/config.py`. Los scripts de shell aceptan variables de entorno:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host del servidor |
| `PORT` | `8000` | Puerto del servidor |
| `API_URL` | `http://localhost:8000` | URL base para `process_all_images.sh` |
| `CONCURRENCY` | `3` | Número de imágenes procesadas en paralelo |
| `LOG_DIR` | `outputs/logs` | Directorio de logs de la API |
| `PID_FILE` | `outputs/api.pid` | Archivo PID para gestión del proceso |

## Estructura del proyecto

```
├── src/
│   ├── main.py                    # App FastAPI + lifespan
│   ├── config/config.py           # Rutas, constantes y detección de PROJECT_ROOT
│   ├── inference/inference.py     # ImageDescriptionService (llama-cpp-python)
│   ├── observability/metrics.py   # Métricas Prometheus
│   ├── routers/
│   │   ├── health.py              # GET /health, redirección raíz
│   │   └── images.py              # POST /describe-image, /describe-images
│   └── utils/
│       ├── image_utils.py         # Conversión a data URI, validación de extensión
│       ├── model_utils.py         # Selección automática de archivos GGUF por preferencia
│       └── logging_utils.py       # Supresión de stdout/stderr nativos de llama.cpp
├── scripts/
│   ├── download_vlm.sh            # Descarga modelo GGUF + mmproj desde Hugging Face
│   ├── start_api.sh               # Levanta la API en background con nohup
│   ├── stop_api.sh                # Detiene la API por PID o patrón de proceso
│   ├── process_all_images.sh      # Procesamiento batch en paralelo de imgs/
│   └── build_context.sh           # Genera repomix-output.xml del proyecto
├── infra/
│   ├── prometheus.yaml            # Configuración de scraping
│   └── grafana.yaml               # Datasource Prometheus para Grafana
├── imgs/                          # Imágenes de entrada (gitignored)
├── models/                        # Modelos GGUF (gitignored)
├── outputs/                       # Descripciones JSON y logs (gitignored)
├── docker-compose.yaml            # Prometheus + Grafana
├── Makefile                       # Comandos de gestión del proyecto
└── pyproject.toml                 # Dependencias Python (uv)
```
