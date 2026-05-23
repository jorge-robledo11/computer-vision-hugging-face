from prometheus_client import Counter, Gauge, Histogram, Info


IMAGE_DESCRIPTION_REQUESTS_TOTAL = Counter(
    "image_description_requests_total",
    "Total de requests de descripción de imágenes procesadas por el modelo.",
    ["status"],
)

IMAGE_DESCRIPTION_DURATION_SECONDS = Histogram(
    "image_description_duration_seconds",
    "Tiempo de inferencia del modelo para describir una imagen.",
    buckets=(0.5, 1, 2, 5, 10, 20, 30, 60, 120),
)

IMAGE_DESCRIPTION_ERRORS_TOTAL = Counter(
    "image_description_errors_total",
    "Total de errores durante la inferencia de imágenes.",
    ["error_type"],
)

MODEL_LOADED = Gauge(
    "image_model_loaded",
    "Indica si el modelo está cargado correctamente. 1 = cargado, 0 = no cargado.",
)

MODEL_INFO = Info(
    "image_model_info",
    "Información del modelo cargado.",
)