.PHONY: up down seed load baseline corrupt compare check reset demo-corruption

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

corrupt:
	uv run python -m src.scenarios.corrupt_values

compare:
	uv run python -m src.validation.compare_baseline

check:
	uv run python -m src.validation.run_checks

reset:
	uv run python -m src.generator.seed_source --rows 10000
	uv run python -m src.ingestion.initial_load
	rm -f artifacts/baseline.json
	uv run python -m src.validation.capture_baseline

demo-corruption:
	@echo ""
	@echo "======================================"
	@echo "   DEMO: WHY ROW COUNTS AREN'T ENOUGH"
	@echo "======================================"
	@echo ""
	uv run python -m src.scenarios.corrupt_values
	uv run python -m src.ingestion.initial_load
	uv run python -m src.validation.compare_baseline