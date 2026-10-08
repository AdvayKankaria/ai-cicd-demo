# DEMO RUNBOOK

This runbook contains exact Git commands and GitHub UI actions to demonstrate the capabilities of the AI CI/CD Automation Platform.

## DEMO 1: Normal release
**Goal:** Demonstrate a clean, successful pipeline run through PROD.
**Steps:**
1. Execute locally:
   ```bash
   git checkout main
   git commit --allow-empty -m "chore: trigger normal release"
   git push origin main
   ```
2. Navigate to the GitHub UI -> **Actions** tab.
3. Observe the `Production Release` workflow running.
4. It will pause at `PROD-APPROVAL`.
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
