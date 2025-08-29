# Echo Judgment System v10 - Makefile
# Common commands for development and CI

.PHONY: help install lint test format build up up-dev down logs smoke clean health agent-smoke agent-bench agent-regress agent-bench-curve agent-bench-visualize agent-dashboard agent-bench-signatures agent-bench-compare agent-check-regression agent-slack-notify agent-dashboard-compare

# Default target
help:
	@echo "Echo Judgment System v10 - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install Python dependencies"
	@echo "  lint        Run linting (ruff)"
	@echo "  format      Format code (black + isort)"
	@echo "  test        Run tests (pytest)"
	@echo ""
	@echo "Docker:"
	@echo "  build       Build Docker images"
	@echo "  up          Start services (production mode)"
	@echo "  up-dev      Start services (development mode with hot reload)"
	@echo "  down        Stop and remove services"
	@echo "  logs        Show service logs"
	@echo ""
	@echo "Testing:"
	@echo "  smoke       Run smoke tests against running services"
	@echo "  health      Check service health"
	@echo "  agent-smoke Run Agent Hub smoke tests"
	@echo "  agent-bench Run Agent Hub benchmarks"
	@echo "  agent-regress Run Agent Hub regression tests"
	@echo "  agent-bench-curve Run Agent Hub bench curve"
	@echo "  agent-bench-visualize Visualize latest benchmark results"
	@echo "  agent-dashboard Open Streamlit benchmark dashboard"
	@echo ""
	@echo "Agent Hub Extensions:"
	@echo "  agent-bench-signatures  Run signature comparison benchmarks"
	@echo "  agent-bench-compare     Visualize signature comparison results"
	@echo "  agent-check-regression  Check for performance regressions"
	@echo "  agent-slack-notify      Send Slack notifications (requires SLACK_WEBHOOK_URL)"
	@echo "  agent-dashboard-compare Open signature comparison dashboard (port 8503)"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Clean Docker resources"

# Development
install:
	pip install -r requirements.txt
	pip install -r echogpt/requirements.txt
	pip install pytest ruff black isort

lint:
	ruff check .

format:
	black .
	isort .

test:
	@if find . -name "*test*.py" -type f | grep -q .; then \
		PYTHONPATH=$$(pwd) pytest -v; \
	else \
		echo "No tests found, skipping pytest"; \
	fi

# Docker
build:
	docker build -f Dockerfile.api -t echo-api:latest .
	docker build -f Dockerfile.echogpt -t echogpt:latest .  
	docker build -f Dockerfile.dashboard -t echo-dashboard:latest .

up:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
	fi
	docker compose -f docker-compose.yml up -d

up-dev:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
	fi
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

down:
	docker compose down -v

logs:
	docker compose logs -f

# Testing
smoke:
	@echo "Running smoke tests..."
	@echo "Testing Echo API health..."
	@curl -sf http://localhost:$${ECHO_API_PORT:-9000}/health || (echo "Echo API health check failed" && exit 1)
	@echo "✅ Echo API health check passed"
	
	@echo "Testing EchoGPT status..."
	@curl -sf http://localhost:$${ECHOGPT_PORT:-9001}/v1/system/status > /dev/null || (echo "EchoGPT status check failed" && exit 1)
	@echo "✅ EchoGPT status check passed"
	
	@echo "Testing EchoGPT chat..."
	@curl -sf -X POST http://localhost:$${ECHOGPT_PORT:-9001}/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"messages":[{"role":"user","content":"Hello"}],"model":"echogpt-1.0"}' > /dev/null || (echo "EchoGPT chat test failed" && exit 1)
	@echo "✅ EchoGPT chat test passed"
	
	@echo "Testing Dashboard..."
	@curl -sf http://localhost:$${DASHBOARD_PORT:-9501} > /dev/null || (echo "Dashboard check failed" && exit 1)
	@echo "✅ Dashboard check passed"
	
	@echo "🎉 All smoke tests passed!"

health:
	@echo "Service Health Status:"
	@echo "======================"
	docker compose ps
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost:$${ECHO_API_PORT:-9000}/health || echo "❌ Echo API not responding"
	@echo ""
	@echo "EchoGPT Status:"  
	@curl -s http://localhost:$${ECHOGPT_PORT:-9001}/v1/system/status | jq '.status // "❌ EchoGPT not responding"' || echo "❌ EchoGPT not responding"

# Cleanup
clean:
	docker compose down -v
	docker system prune -f
	docker volume prune -f

# Agent Hub Tests
agent-smoke:
	@echo "Running Agent Hub smoke tests..."
	bash tests/agent_hub/smoke_tests.sh

agent-bench:
	@echo "Running Agent Hub benchmarks..."
	python tests/agent_hub/bench_async.py

agent-bench-heavy:
	@echo "Running heavy Agent Hub benchmarks..."
	python tests/agent_hub/bench_async.py 50 1000

agent-regress:
	@echo "Running Agent Hub regression tests..."
	python tests/agent_hub/run_regression.py tests/agent_hub/regression.yaml

agent-bench-curve:
	@echo "Running Agent Hub bench curve..."
	cd tests/agent_hub && python bench_curve.py --steps 20x200,50x1000 --tag makefile

agent-bench-visualize:
	@echo "Visualizing latest benchmark results..."
	LATEST=$$(ls -td tests/agent_hub/artifacts/bench/* | head -1); \
	cd tests/agent_hub && python visualize_results.py $$LATEST/results.json

agent-dashboard:
	@echo "Starting Streamlit benchmark dashboard..."
	@echo "Open: http://localhost:8502"
	cd tests/agent_hub && streamlit run ../../web/dashboard/streamlit_app.py --server.port 8502

# Agent Hub Extensions
agent-bench-signatures:
	@echo "Running signature comparison benchmarks..."
	cd agent_hub_ci_bundle && python tests/agent_hub/bench_signatures.py --signatures Aurora,Selene,Heo --steps 20x200,50x1000,100x2000 --tag sigbench

agent-bench-compare:
	@echo "Visualizing signature comparison results..."
	LATEST=$$(ls -td agent_hub_ci_bundle/artifacts/bench/* | head -1); \
	cd agent_hub_ci_bundle && python tests/agent_hub/visualize_compare.py $$LATEST/combined.json

agent-check-regression:
	@echo "Checking for performance regressions..."
	LATEST=$$(ls -td agent_hub_ci_bundle/artifacts/bench/* | head -1); \
	cd agent_hub_ci_bundle && python tests/agent_hub/check_regression.py $$LATEST/results.json --baseline tests/agent_hub/bench_baseline.yaml --fail-on-violation

agent-slack-notify:
	@echo "Sending Slack notification..."
	LATEST=$$(ls -td agent_hub_ci_bundle/artifacts/bench/* | head -1); \
	cd agent_hub_ci_bundle && python alerts/slack_notify.py $$LATEST/summary.json "Agent Hub Bench Guard"

agent-dashboard-compare:
	@echo "Starting signature comparison dashboard..."
	@echo "Open: http://localhost:8503"
	cd agent_hub_ci_bundle && streamlit run web/dashboard/streamlit_compare.py --server.port 8503

# Special targets for CI
ci-test: lint test

ci-smoke: smoke

# Local development helpers
dev-reset: down clean up-dev logs

quick-start: 
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "🚀 Starting Echo Judgment System..."
	@make up-dev
	@echo ""
	@echo "Services starting up... Wait a moment then try:"
	@echo "  make health     # Check if services are ready"
	@echo "  make smoke      # Run smoke tests"  
	@echo "  make logs       # View logs"
	@echo ""
	@echo "Web interfaces:"
	@echo "  Dashboard: http://localhost:9501"
	@echo "  API Docs:  http://localhost:9000/docs (if available)"