.PHONY: up down seed load baseline corrupt compare check reset \
	watermark changes extract apply crash-apply replay \
	demo-corruption incremental-demo demo-late-arrival

up:
	docker compose up -d

down:
	docker compose down

seed:
	uv run python -m src.generator.seed_source --rows 10000

load:
	uv run python -m src.ingestion.initial_load

baseline:
	rm -f artifacts/baseline.json
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
	rm -f artifacts/baseline.json
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