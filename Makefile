.PHONY: test-fe test-be test-integration test-e2e

test-fe:
	cd frontend && npm run ci

test-be:
	python -m pytest tests/ -v

test-integration:
	python -m pytest tests/integration/ -v --override-ini="addopts=" --tb=short

test-e2e:
	cd frontend && npm run test:e2e
