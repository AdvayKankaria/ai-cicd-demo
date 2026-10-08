# AI-Powered Autonomous CI/CD and Release Recovery Platform

## 1 Overview
This repository provides an entire production-style CI/CD demonstration platform that integrates an external AI CI/CD Automation Engine. It features an Order Management Platform backend demonstrating automated build, test, security, deployment, and AI-driven self-healing pipelines.

## 2 Business problem
Modern cloud-native deployments are complex, resulting in a high cognitive load for engineers when troubleshooting deployment failures, rollbacks, and failed migrations. When a pipeline fails in production, manual investigation delays resolution.

## 3 Solution
This platform integrates an AI CI/CD Automation Engine to automatically diagnose pipeline failures across CI, staging, and production boundaries. It can dynamically choose to retry transients, create pull requests to remediate code and dependency issues, or automatically rollback deployments.

## 4 Architecture
```text
Developer -> PR -> CI -> Approval -> Merge -> Build -> GHCR -> DEV -> UAT -> Human PROD approval -> Canary -> PROD -> Post validation -> SUCCESS
```

## 5 Application architecture
```text
      CLIENT
         |
         v
    FastAPI API
     /   |   \
    /    |    \
   v     v     v
PostgreSQL Redis Worker
   ^
   |
Order Service
```

## 6 CI architecture
GitHub Actions drives the pipeline. PR validation checks code quality (Ruff), tests (pytest), integration tests, and security (Bandit, pip-audit, Trivy, CodeQL, Dependency Review).

## 7 CD architecture
Artifacts are built once. The same immutable Docker image digest is promoted through DEV, UAT, and PROD. Deployments run database migrations before cutting over traffic.

## 8 DEV/UAT/PROD
- DEV: Validates container boot and smoke tests.
- UAT: Validates regression on a staging environment.
- PROD: Requires human approval via GitHub Environments.

## 9 Immutable artifact strategy
Docker images are built tagged with the commit SHA and pushed to GHCR. Downstream environments deploy the exact image digest to eliminate drift.

## 10 Security controls
Pipeline includes Trivy container scanning, pip-audit for dependency vulnerability, Bandit for static code analysis, and CodeQL. Secrets are managed securely by GitHub, avoiding hardcoded credentials.

## 11 AI failure detection
A `workflow_run` action triggers whenever the Release pipeline fails, collecting logs, branch info, commit SHAs, and failure stages to send to the AI Engine in a structured JSON payload.

## 12 AI remediation
Based on the failure class (TEST_FAILURE, SECURITY_FAILURE, etc.), the AI engine decides the remediation path.

## 13 Retry logic
Deployment failures trigger bounded retries. Transients are recovered without code changes.

## 14 PR self-healing flow
The AI engine pushes a fix to an `ai-fix/pipeline-<run-id>` branch and creates a PR. This PR must pass all standard CI checks.

## 15 Human approval
The AI engine cannot bypass human controls. Production deployment and AI-generated PR merges both require manual authorization.

## 16 Production canary
10% of traffic routes to the new deployment. Validation checks error rates and latency before 100% promotion.

## 17 Rollback
If canary or post-deployment checks fail, the orchestrator reverts to the previous known-good artifact digest automatically.

## 18 Failure scenarios
The platform supports injecting controlled failures (e.g., `test_failure`, `migration_failure`) via workflow dispatch to demonstrate AI capabilities.

## 19 Local setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
# Requires Docker daemon
docker compose up -d
```

## 20 GitHub Setup Required
To fully operate this repository, you must manually perform the following steps in GitHub:
1. **Repository Visibility**: Make sure it is Public (or Private with Actions enabled).
2. **Environments**: Go to Settings -> Environments. Create an environment named `PROD-APPROVAL`.
3. **Required Reviewers**: Inside the `PROD-APPROVAL` environment, check "Required reviewers" and add yourself.
4. **Branch Rules**: Go to Settings -> Branches -> Add branch protection rule for `main`:
   - Require a pull request before merging (minimum 1 approval).
   - Require status checks to pass (Select `pr-release-gate`).
   - Prevent force pushes.
5. **Repository Secrets**: Go to Settings -> Secrets and variables -> Actions. Add `AI_ENGINE_URL` and `AI_ENGINE_TOKEN`.
6. **Actions Permissions**: Go to Settings -> Actions -> General. Ensure "Read and write permissions" is selected so workflows can publish packages and push branches.
7. **GHCR Permissions**: Go to your Profile -> Packages -> `ai-cicd-demo-api` -> Package Settings. Ensure the repository has Admin/Write access to the package.

## 21 Simulation vs Reality
This repository separates **REAL** CI/CD configurations from **SIMULATED** cloud infrastructure:
**REAL:**
- GitHub Actions workflows
- Pull Request Branch Protections
- Tests, Linting, formatting
- Security Scans (CodeQL, Trivy, Bandit, pip-audit)
- Docker builds and GHCR pushing
- Artifact passing via image digests
- GitHub Environments and Approvals
- Workflow failure payload generation

**SIMULATED:**
- Cloud infrastructure (AWS/ECS/EKS)
- Actual load balancers
- Real Kubernetes canary routing (implemented as a failure-toggle job)
- Multi-node production state
- Real production observability metrics

For a full demonstration guide, see `DEMO_RUNBOOK.md`.
