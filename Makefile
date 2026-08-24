.PHONY: up down seed load baseline corrupt compare check reset \
	watermark changes extract apply crash-apply replay \
	demo-corruption incremental-demo demo-late-arrival \
	test test-cov

up:
	docker compose up -d

down:
	docker compose down

seed:
	uv run python -m src.generator.seed_source --rows 10000

load:
	uv run python -m src.ingestion.initial_load

baseline:
	uv run python -m src.validation.capture_baseline

watermark:
	uv run python -m src.ingestion.watermark

changes:
	uv run python -m src.scenarios.generate_changes

extract:
	uv run python -m src.ingestion.extract_incremental

apply:
	uv run python -m src.ingestion.apply_incremental

corrupt:
	uv run python -m src.scenarios.corrupt_values

compare:
	uv run python -m src.validation.compare_baseline

check:
	uv run python -m src.validation.run_checks

reset:
	rm -f artifacts/incremental_batch.parquet artifacts/incremental_batch.json
	uv run python -m src.generator.seed_source --rows 10000
	uv run python -m src.ingestion.initial_load
	uv run python -m src.validation.capture_baseline
	uv run python -m src.ingestion.watermark

demo-corruption:
	@echo ""
	@echo "======================================"
	@echo "   DEMO: WHY ROW COUNTS AREN'T ENOUGH"
	@echo "======================================"
	@echo ""
	uv run python -m src.scenarios.corrupt_values
	uv run python -m src.ingestion.initial_load
	uv run python -m src.validation.compare_baseline

incremental-demo:
	@echo ""
	@echo "======================================"
	@echo "      INCREMENTAL PROCESSING DEMO"
	@echo "======================================"
	@echo ""
	uv run python -m src.scenarios.generate_changes
	uv run python -m src.ingestion.extract_incremental
	uv run python -m src.ingestion.apply_incremental

crash-apply:
	uv run python -m src.ingestion.apply_incremental \
		--simulate-crash-before-watermark

replay:
	uv run python -m src.ingestion.extract_incremental
	uv run python -m src.ingestion.apply_incremental

demo-crash-replay:
	@echo ""
	@echo "======================================"
	@echo "      CRASH + REPLAY DEMO"
	@echo "======================================"
	@echo ""
	$(MAKE) reset
	$(MAKE) changes
	$(MAKE) extract
	@uv run python -m src.ingestion.apply_incremental \
		--simulate-crash-before-watermark; \
		code=$$?; \
		if [ $$code -ne 99 ]; then \
			echo "Unexpected failure: exit code $$code"; \
			exit $$code; \
		fi; \
		echo ""; \
		echo "Expected crash captured. Restarting pipeline..."
	$(MAKE) extract
	$(MAKE) apply

late-arrival:
	uv run python -m src.scenarios.late_arrival

demo-late-arrival:
	@echo ""
	@echo "======================================"
	@echo "       LATE ARRIVAL DEMO"
	@echo "======================================"
	@echo ""
	$(MAKE) reset
	$(MAKE) late-arrival
	$(MAKE) extract
	$(MAKE) apply
	$(MAKE) extract

test:
	uv run python -m pytest

test-cov:
	uv run python -m pytest \
		--cov=src \
		--cov-report=term-missing

demo:
	@docker compose up -d
	@echo "Waiting for local Iceberg services..."
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' iceberg-lab-postgres 2>/dev/null)" = "healthy" ]; do sleep 1; done
	@until [ "$$(docker inspect -f '{{.State.Status}}' iceberg-lab-mc 2>/dev/null)" = "exited" ]; do sleep 1; done
	@test "$$(docker inspect -f '{{.State.ExitCode}}' iceberg-lab-mc)" = "0"
	@until curl -fsS http://localhost:9000/minio/health/live >/dev/null 2>&1; do sleep 1; done
	@until curl -fsS http://localhost:8181/v1/config >/dev/null 2>&1; do sleep 1; done
	@echo "✓ Local services ready"
	@uv run python -m src.demo