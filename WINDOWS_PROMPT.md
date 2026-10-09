CONTINUATION PROMPT — AI CI/CD AUTOMATION ENGINE ON WINDOWS
We are continuing my existing AI CI/CD Automation Engine project on my Windows laptop. Previous repository and workflow work was performed on my Mac, but my actual AI engine already exists on this Windows machine.
Your first priority is to inspect and integrate with my existing AI engine, not build a new one.

1. Existing GitHub project
Repository: https://github.com/AdvayKankaria/ai-cicd-demo
Pull request: https://github.com/AdvayKankaria/ai-cicd-demo/pull/14
Feature branch: feat/add-failure-scenarios

The latest report from my previous session states that PR Validation run 37876390393 completed successfully, including Ruff, unit tests, integration tests and configured security checks. Verify the live PR status and latest checks instead of assuming this report is still current.

PR #14 contains two intended demonstration scenarios:

Scenario A — transient_failure_once
Attempt 1 intentionally fails in the transient-failure-simulation job.
The failure is classified as TRANSIENT.
The AI engine detects the failed run using GitHub polling.
It calls the GitHub API to rerun the entire workflow.
Attempt 2 passes the injected failure gate and continues through the existing pipeline.
Production approval gates must remain intact.
The engine must perform an actual GitHub workflow rerun in live mode. It must not merely recommend retrying or print a simulated success.

Scenario B — duplicate_order_failure
The e-commerce application contains an intentionally faulty order-idempotency implementation.
Repeating an order request with the same idempotency key creates a duplicate order.
The integration regression test detects the application defect.
The failure metadata includes FAILURE_CLASS=APPLICATION_BUG and FAILURE_REASON=IDEMPOTENCY_VIOLATION.
The AI engine retrieves the relevant logs and source code, diagnoses the problem, implements a fix on a separate branch, runs tests, commits and pushes the fix, and opens a real pull request.
The AI fix PR must run the idempotency regression test and prove the fix with passing tests.
It must not push the fix directly to the base branch or merge its own PR automatically.

These are two different remediation paths: transient failures get retried, while application defects receive code fixes.

2. Inspect my existing Windows AI engine first
Locate the existing AI CI/CD engine in the current workspace and inspect its actual code and architecture.
Identify:
The application entry point and startup commands.
Its existing agents, orchestration and decision-making components.
How it calls the LLM and processes failure logs.
Its GitHub client and authentication method.
Existing polling, scheduling, persistence and deduplication logic.
Its retry, code-fix, pull-request, escalation and rollback implementations.
Existing configuration, tests, logging and error-handling patterns.

Do not scaffold another engine, replace working components, or introduce unnecessary frameworks.
Reuse the current implementation and make the smallest coherent changes required to support the two demonstrations.
If the engine directory cannot be identified, ask me for its location rather than scanning the entire computer or creating a replacement.

3. Required architecture
My architecture is fixed:
The application and AI engine run locally on my Windows laptop.
GitHub Actions uses GitHub-hosted runners to execute CI/CD.
The Windows engine polls the GitHub REST API, approximately every 30 seconds by default.
It retrieves workflow-run status, attempts, jobs and relevant logs.
It analyzes failures and executes approved remediation through GitHub APIs.
GitHub remains the source of truth for workflow status, branches, commits, pull requests and checks.

Do NOT introduce:
Webhooks or a callback endpoint.
ngrok, Cloudflare Tunnel or public inbound endpoints.
A self-hosted GitHub runner.
A new remote service merely to connect the engine to GitHub.
The engine must work with outbound internet access and GitHub authentication only.

4. Implement actual GitHub operations
Reuse or implement a proper GitHub action adapter inside the existing engine.

Retry action
For a confirmed transient failure:
Retrieve the workflow run, run attempt, failed jobs and failure logs.
Confirm the failure is eligible for automatic retry.
Check persistent incident state and retry limits.
Call the GitHub API to rerun the entire workflow.
Poll for the new attempt and observe its outcome.
Record the previous and new attempts in persistent state.
Stop retrying when the configured limit is reached.

For the transient_failure_once demonstration, the engine should rerun attempt 1 once and observe attempt 2 passing.
Do not use a failed-jobs-only rerun for this demonstration because dependent jobs may have been skipped during the original run.

Application code-fix action
For IDEMPOTENCY_VIOLATION:
Retrieve and analyze the actual failing test and workflow logs.
Inspect the source files at the exact commit and branch associated with the failed run.
Reproduce the failure safely in an isolated workspace.
Identify the real cause instead of hardcoding a response to the error message.
Create a branch named ai-fix/<run-id> or another unique, traceable equivalent.
Correct the actual application logic and add or preserve regression coverage.
Run linting, relevant unit tests and integration tests.
Verify the exact idempotency regression test passes.
Inspect the diff and reject changes that simply skip, weaken or delete the failing test.
Commit and push the fix branch.
Create a real GitHub pull request against the correct base branch.
Poll the PR's CI checks and report whether they pass.
Wait for my human review and merge. Do not approve or merge the PR automatically.

If the test cannot be reproduced, the required context is unavailable, or the proposed fix is unsafe, escalate instead of manufacturing a successful result.

5. Persistent state and duplicate prevention
Inspect the existing persistence layer and reuse it where possible.
The engine needs to distinguish separate attempts of the same workflow run and prevent repeatedly processing the same failure. Track at least:
Repository and workflow run ID.
Run attempt number.
Head commit SHA and branch.
Failure classification and diagnostic reason.
Number of retry attempts and AI fix attempts.
Last processed state and timestamps.
Created fix branch and pull request, when applicable.
Final outcome.

Use a key equivalent to (repository, workflow_run_id, run_attempt) for attempt-level deduplication, with an incident identifier to relate multiple attempts.
Persist state across engine restarts. If the existing engine already uses SQLite or another persistent store, extend it rather than introducing a competing database.
Use a configurable poll interval and bounded retry limits. Handle API rate limits, timeouts, transient API failures and interrupted polling without creating duplicate pull requests or infinite retry loops.

6. Authentication and security
Use the existing secure GitHub authentication approach if it is already implemented correctly.
Otherwise, support GitHub CLI authentication or a securely supplied fine-grained token with the minimum required repository permissions for reading Actions runs and logs, rerunning workflows, pushing branches and opening PRs.
Never ask me to paste tokens into this conversation. Never commit credentials, print them in logs, write them into source code, or include them in LLM prompts.

Keep logs sanitized, validate LLM-generated patches, and never execute arbitrary commands generated by the LLM without appropriate validation and isolation.
The default startup mode must be DRY_RUN. Implement real GitHub API operations, but make live execution an explicit configuration choice. In live mode, the two named demo scenarios must execute their real remediation actions subject to the policy above.
Do not perform production deployments, production approvals, automatic PR merges or unverified rollbacks.

7. Other failure modes and existing functionality
Preserve the engine's existing failure classifications and architecture.
Map failures from the existing workflows where applicable, including:
Application tests and builds.
SonarQube, Fortify, Sonatype, Sysdig and Trivy.
CodeQL and other configured security checks.
Database migration failures.
DEV and UAT failures.
Production canary or post-production failures.

Do not assume an enterprise scanner is genuinely integrated just because a workflow step exists. Report what is actually configured and observed.
Inspect the existing rollback implementation before claiming rollback support. If rollback is only simulated, document that limitation rather than pretending a real rollback occurred.
Keep retry, code-fix, rollback and escalation as distinct actions. Never automatically retry deterministic application defects simply because their workflows failed.

8. Implementation and validation workflow
Work incrementally:
Phase 1 — Inspect: Understand the existing engine, repository configuration, PR #14 and the latest GitHub checks. Report the existing capabilities and gaps.
Phase 2 — Integrate: Reuse the current engine, implement missing GitHub API operations, connect the failure classifier to real remediation actions, and add persistent state and safety checks where needed.
Phase 3 — Test: Add automated tests for classification, state transitions, deduplication, attempt tracking, retry limits, API errors, patch validation and action dispatch.
Test mocked GitHub API operations first. Do not mistake mocked tests for a real GitHub integration test.
Phase 4 — Demonstrate: First validate the scenarios in dry-run mode. Then prepare a controlled live demonstration using the two dedicated failure scenarios. Execute a live retry and code-fix PR only when the correct workflow version is available and the configured live mode is explicitly enabled.
Phase 5 — Verify: Confirm the engine detects actual GitHub runs, invokes real API operations, records outcomes, and observes the resulting runs and PR checks.
Use Windows-compatible PowerShell commands and the project's existing Python environment and startup instructions. Do not assume that Mac shell commands or paths work unchanged on Windows.

9. Boundaries
Do not merge PR #14 automatically.
Do not commit directly to main.
Do not weaken branch protection or existing CI/security gates.
Do not bypass required reviews or production approval.
Do not modify real customer data or perform real customer orders during testing.
Do not claim that retries, code fixes, PR creation or rollback succeeded unless the actual operations and resulting GitHub state were verified.
Do not rebuild the application or AI engine from scratch.

10. Final report
When finished, give me:
The location and architecture of the existing Windows AI engine.
The files and components you changed, with reasons.
Which capabilities already existed and which you implemented.
The GitHub authentication method and required permissions, without exposing secrets.
The exact PowerShell command to start the engine in dry-run mode.
The exact safe configuration for live demonstration mode.
How to demonstrate transient_failure_once.
How to demonstrate duplicate_order_failure and verify its fix PR.
Automated test results and actual GitHub API operations verified.
Any limitations, unimplemented features or remaining manual steps.
Begin by inspecting the existing engine and PR #14. Do not start by generating a new engine or changing working code before understanding the architecture.
