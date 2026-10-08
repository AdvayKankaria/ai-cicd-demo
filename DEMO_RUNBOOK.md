# DEMO RUNBOOK

This runbook contains exact Git commands and GitHub UI actions to demonstrate the capabilities of the AI CI/CD Automation Platform.

## DEMO 1: Normal release
**Goal:** Demonstrate a clean, successful pipeline run through PROD.

**Option A: Trigger via CLI**
1. Execute locally:
   ```bash
   git checkout main
   git commit --allow-empty -m "chore: trigger normal release"
   git push origin main
   ```

**Option B: Trigger via GitHub UI**
1. Navigate to the GitHub UI -> **Actions** tab -> **Production Release**.
2. Click **Run workflow**, leave the dropdown at `none`, and click **Run workflow**.

**Observation Steps (For both options):**
3. Observe the `Production Release` workflow running.
4. It will pause at `prod-approval` (the Release Gate).
5. Click **Review deployments** and approve the production deployment.
6. The pipeline resumes, deploys the canary, promotes, and succeeds.

## DEMO 2: Break order calculation code
**Goal:** Demonstrate AI diagnosis and automatic PR remediation for a code failure.
**Steps:**
1. Navigate to GitHub UI -> **Actions** tab -> **Production Release**.
2. Click **Run workflow**.
3. Select `test_failure` from the "Simulate a failure scenario" dropdown and click **Run workflow**.
4. The workflow will fail at the `validation` job because the injected scenario modifies the code logic (price + quantity).
5. The `AI Failure Handler` workflow automatically triggers upon failure.
6. The AI Engine receives the payload, diagnoses the root cause, and pushes a fix branch `ai-fix/<run-id>`.
7. An AI-generated PR appears in the **Pull requests** tab.
8. Review the PR. The `PR Validation` checks will run and pass.
9. Approve and merge the PR.
10. The `Production Release` workflow runs again automatically and succeeds.

## DEMO 3: Security failure
**Goal:** Demonstrate the security gate blocking a release due to a dependency issue.
**Steps:**
1. Navigate to GitHub UI -> **Actions** tab -> **Production Release**.
2. Click **Run workflow**.
3. Select `security_failure` from the dropdown and click **Run workflow**.
4. The workflow will successfully build and publish the image, but fail at the `security-scan` job (Trivy scan).
5. The AI Failure Handler triggers, diagnoses the vulnerable package, and creates a remediation PR bumping the version.

## DEMO 4: Production canary failure
**Goal:** Demonstrate automatic production rollback when a newly promoted release fails canary validation.
**Steps:**
1. Navigate to GitHub UI -> **Actions** tab -> **Production Release**.
2. Click **Run workflow**.
3. Select `prod_canary_failure` from the dropdown and click **Run workflow**.
4. Approve the PROD deployment when prompted.
5. The `prod-canary` job will fail.
6. The failure handler triggers an automatic rollback mechanism (`scripts/rollback.py`) simulating restoring the previous artifact digest and verifying health.
7. The release is aborted, preventing production outages.

## Enterprise Security Tools

This repository is integrated with 8 enterprise-grade security and quality gates. These gates evaluate the codebase, dependencies, and container images before any deployment can proceed.

### Tool Overview & Mode Status

The pipeline supports dual modes for enterprise vendors:
* **REAL MODE**: The scanner actively evaluates the code and enforces policies. Requires vendor credentials.
* **DEMO MODE**: The scanner simulates a successful run and clearly logs its demo status. Used when vendor credentials are unavailable.

| Tool | Purpose | Current Mode | Failure Scenario Trigger |
|---|---|---|---|
| **SonarQube** | Code Quality (SAST, Coverage) | DEMO | `sonarqube_failure` |
| **Fortify** | Static Application Security Testing (SAST) | DEMO | `fortify_failure` |
| **Sonatype Lifecycle** | Dependency Security | DEMO | `sonatype_failure` |
| **Sysdig Secure** | Container Vulnerability Scanning | DEMO | `sysdig_failure` |
| **Trivy** | Container CVE Scanning | REAL | `security_failure` |
| **CodeQL** | SAST & Vulnerability Scanning | REAL | *N/A* |
| **Bandit** | Python AST Security Scanning | REAL | *N/A* |
| **pip-audit** | Python Dependency Security | REAL | *N/A* |

### Unified Enterprise Security Gate

All 8 tools feed their results into a centralized **Enterprise Security Gate**. This gate aggregates the results and presents a unified GitHub Step Summary table. If any of the 8 tools report a failure or are cancelled, the Enterprise Gate fails the pipeline and prevents downstream deployment.

### Simulating Vendor Failures

You can trigger a simulated failure for any of the demo tools via `workflow_dispatch` (UI). When triggered:
1. The simulated tool logs a `FAILURE_STAGE`, `FAILURE_CLASS`, and `FAILURE_REASON`.
2. The specific job fails gracefully.
3. The Unified Security Gate detects the failure and halts the release.
4. The AI Failure Handler scrapes the payload for automated remediation.
