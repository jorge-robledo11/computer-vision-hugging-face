.PHONY: help api-start api-stop obs-start obs-stop obs-restart obs-status context process-images

help:
	@echo "Comandos disponibles:"
	@echo "  make api-start        Levanta la API"
	@echo "  make api-stop         Detiene la API"
	@echo "  make obs-start        Levanta Prometheus + Grafana"
	@echo "  make obs-stop         Detiene Prometheus + Grafana"
	@echo "  make obs-restart      Reinicia Prometheus + Grafana"
	@echo "  make obs-status       Muestra estado de Prometheus + Grafana"
	@echo "  make context          Genera context/repomix-output.xml"
	@echo "  make process-images   Procesa imágenes en imgs/"

api-start:
	./scripts/start_api.sh

api-stop:
	@if [ -f outputs/api.pid ]; then \
		PID="$$(cat outputs/api.pid)"; \
		if kill -0 "$$PID" 2>/dev/null && ps -p "$$PID" -o args= | grep -q "uvicorn src.main:app"; then \
			kill "$$PID"; \
			rm -f outputs/api.pid; \
			echo "API detenida."; \
		else \
			echo "PID file obsoleto. Limpiando outputs/api.pid."; \
			rm -f outputs/api.pid; \
		fi; \
	else \
		echo "No existe outputs/api.pid. Intentando detener uvicorn por patrón..."; \
		pkill -f "uvicorn src.main:app" || true; \
	fi

obs-start:
	docker compose up -d prometheus grafana

obs-stop:
	docker compose stop prometheus grafana

obs-restart:
	docker compose restart prometheus grafana

obs-status:
	docker compose ps prometheus grafana
	@echo
	@echo "Prometheus targets:"
	@curl -fsS http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, scrapeUrl: .scrapeUrl, health: .health, lastError: .lastError}' || true

context:
	./scripts/build_context.sh

process-images:
	./scripts/process_all_images.sh