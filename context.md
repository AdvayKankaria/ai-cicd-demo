# Project Context & Handoff Document

## 1. Project Purpose
This repository (`ai-cicd-demo`) serves as the multi-service e-commerce application and the GitHub Actions CI/CD execution environment for an external **AI CI/CD Automation Engine**. The AI Engine itself lives entirely outside of this repository (on a separate Windows machine). This repository provides the required application architecture, telemetry, test suites, and deployment executor interfaces for that external engine to drive and heal.

## 2. Current Application Architecture
The application has been expanded from a monolith into a realistic 16-service microservice architecture:
- **Core E-commerce Journey:** `catalog`, `cart`, `checkout`, `order`
- **Supporting Services:** `pricing`, `inventory`, `payment`, `fulfillment`, `shipping`, `notification`, `search`, `customer`, `identity`, `returns`, `reviews`, `recommendation`

**Implementation Details:**
- Each service is a FastAPI application located in `services/<service-name>/`.
- Each service has a dedicated `docker/<service-name>.Dockerfile` and independent unit tests (`tests/unit/services/test_<service-name>.py`).
- Each service exposes `/health` and `/ready` endpoints.
- The `docker-compose.yml` runs all 16 services alongside PostgreSQL and Redis for full local testing.

## 3. Current CI/CD Architecture
The repository relies on GitHub Actions for its CI/CD execution:
1. **01-pr-validation.yml (PR Gate):** Runs unit tests, integrations tests, and the Enterprise Security Gate for all Pull Requests.
2. **02-release.yml (Release & Recovery Demo):** Simulates a production release pipeline with Dev/UAT/Prod phases, canary deployments, and failure-injection simulations.
3. **04-kg-deployment-plan.yml (KG Executor):** The integration point for the external AI Engine. It dynamically executes a plan to test, build, and deploy specific impacted services in parallel waves.

**Enterprise Security Tools:**
- **REAL Mode (Actively blocking failures):** Trivy (Container CVEs), CodeQL (SAST), Bandit (Python AST), pip-audit (Dependencies).
- **DEMO Mode (Simulated Success/Failure):** SonarQube, Fortify, Sonatype Lifecycle, Sysdig Secure.

*Note: Infrastructure deployments, canary routing, and rollbacks in GitHub Actions are currently simulated to avoid cloud costs.*

## 4. Existing Failure Demonstrations
The `02-release.yml` pipeline supports two primary failure simulations via the `workflow_dispatch` dropdown:
- **`transient_failure_once`:** Fails intentionally on attempt 1 in the `transient-failure-simulation` job. If the AI Engine triggers a full workflow rerun (attempt 2), the pipeline gracefully passes the failure gate and succeeds.
- **`duplicate_order_failure`:** The application code lacks true idempotency. This scenario triggers an actual integration regression test (`test_order_idempotency.py`) which fails. The AI engine must supply a real source-code fix to make the test pass.

## 5. Correct AI-Engine Architecture
**CRITICAL:** The AI CI/CD Automation Engine and its Knowledge Graph (KG) **are not** implemented in this repository. 
- The Windows engine **owns the KG** and performs all dependency-reasoning, impact analysis, and deployment wave planning. 
- This repository merely provides the application metadata, contracts, tests, and the execution pipeline. 
- The Windows engine **polls GitHub APIs** to detect failures and trigger workflows. **There are no inbound webhooks, ngrok tunnels, or public endpoints required.**

## 6. Future Integration Interface (KG Deployment Plan)
The `04-kg-deployment-plan.yml` workflow acts as the interface for the Windows AI Engine. 
The AI Engine uses the GitHub REST API (`workflow_dispatch`) to supply a JSON `plan_payload`.

**Current Interface Schema:**
```json
{
  "schema_version": "1.0",
  "plan_id": "plan-xyz",
  "mode": "impacted_services",
  "commit_sha": "<target-sha>",
  "services": ["catalog", "checkout"],
  "test_suites": ["unit", "contract"],
  "waves": [
    {"id": 1, "services": ["catalog"]}, 
    {"id": 2, "services": ["checkout"]}
  ]
}
```
**Execution:**
- GitHub Actions parses this JSON (`.github/scripts/parse_plan.py`).
- It tests the listed services dynamically via matrix jobs.
- It builds the listed services in parallel.
- It executes deployment waves sequentially (blocking downstream waves if a prerequisite fails, e.g., a contract test).

## 7. Local Setup and Demo Instructions
**Local Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install pytest fastapi uvicorn pydantic httpx
docker compose up -d
```
**Validation:**
- Linting: `ruff check .`
- Formatting: `ruff format --check .`
- Tests: `PYTHONPATH=. pytest tests/unit/services`
- Workflow syntax: `actionlint` (via docker if installed)

**Testing the KG Executor Fixture (Demo 7):**
To test the pipeline executor before connecting the engine, trigger `04-kg-deployment-plan.yml` manually from the GitHub UI using the sample JSON plan above. Set `BREAK_CATALOG_CONTRACT=true` in GitHub variables to verify that a simulated contract failure safely blocks Wave 2.

## 8. Limitations and Next Steps
- **Implemented & Tested:** 16-service architecture, local Docker Compose, parallel CI tests, Enterprise Security Gate, KG plan parser & workflow executor, integration contract test, failure scenarios (idempotency & transient).
- **Simulated:** Production deployments, rollback execution, proprietary security scanner actuals (SonarQube, etc.).
- **Pending/Next Steps:** The immediate next milestone is connecting the existing Windows AI polling engine to this repository, allowing the actual KG to analyze commits and automatically dispatch the deployment plan JSON payload to the executor.
