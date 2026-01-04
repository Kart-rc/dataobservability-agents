# PR Author Agent Specification

## Purpose

The PR Author Agent transforms Observability Diff Plans from Scout Agent into complete Pull Requests containing instrumentation code, configuration, tests, and documentation.

## Requirements

### Requirement: Diff Plan Parsing

The system SHALL parse and validate Observability Diff Plans from Scout Agent.

#### Scenario: Valid Diff Plan processing
- **GIVEN** a valid Diff Plan JSON with confidence >= 0.7
- **WHEN** the PR Author Agent processes the plan
- **THEN** it extracts archetypes, gaps, and tech_stack
- **AND** proceeds with template selection

#### Scenario: Invalid Diff Plan rejection
- **GIVEN** a Diff Plan JSON with missing required fields
- **WHEN** the PR Author Agent attempts to process
- **THEN** it rejects the plan with validation errors
- **AND** does not create a PR

#### Scenario: Low confidence Diff Plan
- **GIVEN** a Diff Plan with confidence < 0.7
- **WHEN** the PR Author Agent processes the plan
- **THEN** it skips PR creation
- **AND** logs the reason with diff_plan_id

### Requirement: Template Selection

The system SHALL select appropriate templates based on archetypes and language.

#### Scenario: Java Kafka template selection
- **GIVEN** a Diff Plan with archetype "kafka-microservice"
- **AND** tech_stack.language = "java"
- **WHEN** templates are selected for gap type "missing_otel"
- **THEN** it selects "kafka-consumer-otel-java" template
- **AND** loads template files from references/templates/java/

#### Scenario: Go microservice template selection
- **GIVEN** a Diff Plan with archetype "go-microservice"
- **AND** tech_stack.http_framework = "gin"
- **WHEN** templates are selected
- **THEN** it selects "gin-otel-go" template

#### Scenario: Python template selection
- **GIVEN** a Diff Plan with archetype "kafka-microservice"
- **AND** tech_stack.language = "python"
- **WHEN** templates are selected
- **THEN** it selects "kafka-otel-python" template

#### Scenario: Missing template fallback
- **GIVEN** a Diff Plan requesting unavailable template
- **WHEN** template selection fails
- **THEN** it falls back to generic template for the language
- **AND** logs a warning about missing specific template

### Requirement: Code Generation

The system SHALL generate instrumentation code through template interpolation.

#### Scenario: Variable interpolation
- **GIVEN** a template with ${SERVICE_NAME} placeholder
- **AND** Diff Plan with repo = "orders-enricher"
- **WHEN** the template is rendered
- **THEN** ${SERVICE_NAME} is replaced with "orders-enricher"
- **AND** no unresolved ${...} placeholders remain

#### Scenario: Derived variable computation
- **GIVEN** a Java template with ${CLASS_NAME} placeholder
- **AND** SERVICE_NAME = "orders-enricher"
- **WHEN** derived variables are computed
- **THEN** CLASS_NAME = "OrdersEnricher" (PascalCase)
- **AND** PACKAGE_NAME = "orders.enricher" (dot notation)

#### Scenario: Multi-file generation
- **GIVEN** a template with multiple .tmpl files
- **WHEN** the template is rendered
- **THEN** each .tmpl file produces a corresponding output file
- **AND** output paths match language conventions

### Requirement: Artifact Generation

The system SHALL generate all required artifacts for observability.

#### Scenario: Runbook generation
- **GIVEN** a Diff Plan with gap type "missing_runbook"
- **WHEN** artifacts are generated
- **THEN** RUNBOOK.md is created from template
- **AND** contains service-specific information

#### Scenario: Lineage spec generation
- **GIVEN** a Diff Plan with gap type "missing_lineage_spec"
- **WHEN** artifacts are generated
- **THEN** lineage/{service}.yaml is created
- **AND** contains input/output mappings from tech_stack

#### Scenario: Contract stub generation
- **GIVEN** a Diff Plan with gap type "missing_contract"
- **WHEN** artifacts are generated
- **THEN** contracts/{service}.yaml is created
- **AND** contains SLO definitions

### Requirement: Pull Request Creation

The system SHALL create Pull Requests via VCS API.

#### Scenario: GitHub PR creation
- **GIVEN** a repo_url pointing to GitHub
- **AND** valid GitHub authentication
- **WHEN** PR creation is triggered
- **THEN** a new branch is created with prefix "autopilot/observability"
- **AND** all artifacts are committed
- **AND** PR is created with description from template
- **AND** labels ["autopilot", "observability"] are applied

#### Scenario: GitLab MR creation
- **GIVEN** a repo_url pointing to GitLab
- **AND** valid GitLab authentication
- **WHEN** MR creation is triggered
- **THEN** a new branch is created
- **AND** all artifacts are committed
- **AND** Merge Request is created with description

#### Scenario: PR with reviewers
- **GIVEN** a repository with CODEOWNERS file
- **WHEN** PR is created
- **THEN** reviewers are requested based on CODEOWNERS
- **OR** default reviewers are used if CODEOWNERS not found

### Requirement: Dry Run Mode

The system SHALL support dry-run mode for testing without side effects.

#### Scenario: Dry run generation
- **GIVEN** a valid Diff Plan
- **AND** dry_run = true
- **WHEN** PR generation is executed
- **THEN** artifacts are generated in memory
- **AND** no VCS API calls are made
- **AND** result includes list of artifacts that would be created

### Requirement: Event Emission

The system SHALL emit CloudEvents for downstream processing.

#### Scenario: PR created event
- **GIVEN** a successfully created PR
- **WHEN** PR creation completes
- **THEN** a CloudEvent is emitted to output topic
- **AND** event type is "autopilot.pr-author.pr-created"
- **AND** data includes pr_number, pr_url, diff_plan_id

#### Scenario: PR creation failed event
- **GIVEN** a PR creation that fails
- **WHEN** error is caught
- **THEN** a CloudEvent is emitted with error details
- **AND** event type is "autopilot.pr-author.pr-failed"

### Requirement: Error Handling

The system SHALL handle errors gracefully with appropriate retries.

#### Scenario: API rate limiting
- **GIVEN** a GitHub API rate limit response (403)
- **WHEN** the client receives rate limit error
- **THEN** it waits until rate limit reset
- **AND** retries the request
- **AND** maximum 3 retries before failure

#### Scenario: Network errors
- **GIVEN** a transient network error
- **WHEN** API call fails
- **THEN** it retries with exponential backoff
- **AND** logs retry attempts

#### Scenario: Invalid repository
- **GIVEN** a repo_url that doesn't exist
- **WHEN** PR creation is attempted
- **THEN** it fails with clear error message
- **AND** does not retry

### Requirement: Configuration

The system SHALL be configurable via YAML configuration.

#### Scenario: Custom confidence threshold
- **GIVEN** configuration with confidence_threshold = 0.5
- **WHEN** Diff Plan with confidence 0.6 is processed
- **THEN** PR creation proceeds (meets threshold)

#### Scenario: Custom branch prefix
- **GIVEN** configuration with branch_prefix = "feat/observability"
- **WHEN** branch is created
- **THEN** branch name starts with "feat/observability"

#### Scenario: Disabled auto-create
- **GIVEN** configuration with auto_create_pr = false
- **WHEN** Diff Plan is processed
- **THEN** artifacts are generated but no PR created
- **AND** result indicates "artifacts_generated" status

### Requirement: Idempotency

The system SHALL be idempotent for repeated processing of the same Diff Plan.

#### Scenario: Duplicate Diff Plan processing
- **GIVEN** a Diff Plan that was already processed
- **WHEN** the same Diff Plan is received again
- **THEN** it checks for existing PR
- **AND** does not create duplicate PR
- **OR** updates existing PR if changed

### Requirement: Observability

The system SHALL emit metrics and traces for monitoring.

#### Scenario: Metrics emission
- **GIVEN** PR Author Agent running
- **WHEN** PRs are created
- **THEN** counters are incremented for:
  - `pr_author_plans_received`
  - `pr_author_prs_created`
  - `pr_author_prs_failed`
- **AND** histograms record generation duration

#### Scenario: Trace correlation
- **GIVEN** a Diff Plan with trace context
- **WHEN** PR is created
- **THEN** trace context is propagated
- **AND** PR creation span is child of Diff Plan processing span
