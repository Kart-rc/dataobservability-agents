# Getting Started with Data Observability Agents

This guide provides comprehensive instructions for setting up and using the Data Observability Agents system, including Claude Skills and Windsurf integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Using Claude Skills](#using-claude-skills)
4. [Windsurf Development Setup](#windsurf-development-setup)
5. [Agent Workflows](#agent-workflows)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher (for OpenSpec CLI)
- **Git**: 2.x or higher
- **Docker**: For running validation tests (optional)

### Access Requirements

- GitHub account with appropriate repository permissions
- AWS credentials (for Signal Factory and RCA Copilot)
- Claude Projects access (for Claude Skills)

## Installation

### Option 1: Claude Skills in Claude Projects

1. **Download the Scout Agent skill package**:
   ```bash
   # From the repository
   cp docs/scout/scout-agent.skill ~/Downloads/
   ```

2. **Upload to Claude Projects**:
   - Open Claude Projects
   - Create a new project or open existing
   - Upload `scout-agent.skill` to project files
   - Claude will automatically parse and use the skill

3. **Trigger the skill**:
   ```
   "Scan this repository for observability gaps"
   "Generate a diff plan for orders-enricher"
   ```

### Option 2: Windsurf Integration

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/dataobservability-agents.git
   cd dataobservability-agents
   ```

2. **Install OpenSpec CLI**:
   ```bash
   npm install -g @fission-ai/openspec@latest
   ```

3. **Extract Scout Agent skill**:
   ```bash
   unzip docs/scout/scout-agent.skill -d .
   mkdir -p .windsurf/workflows openspec
   cp -r scout-agent/assets/windsurf/workflows/* .windsurf/workflows/
   cp -r scout-agent/assets/openspec/* openspec/
   ```

4. **Initialize OpenSpec**:
   ```bash
   openspec init
   # Select "Windsurf" as the integration target
   ```

5. **Verify installation**:
   ```bash
   openspec status
   ```

### Option 3: Python Development Environment

1. **Create virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run unit tests**:
   ```bash
   pytest tests/ -v
   ```

## Using Claude Skills

### Scout Agent Skill

The Scout Agent analyzes repositories to detect observability gaps.

**Triggers**:
- "scan repo for observability gaps"
- "analyze repository instrumentation"
- "generate diff plan for [service-name]"
- "find missing OTel instrumentation"

**Example Session**:
```
User: Scan the orders-enricher repository for observability gaps

Claude: I'll analyze the orders-enricher repository using the Scout Agent skill.

[Scans repository structure, dependencies, and existing instrumentation]

## Observability Analysis Report

**Repository**: orders-enricher
**Archetypes Detected**: kafka-microservice, spring-boot
**Confidence Score**: 87%

### Current Observability State
- OTel SDK: Not present
- Correlation Headers: Not configured
- Lineage Spec: Missing
- Data Contract: Missing
- Runbook: Missing

### Gaps Identified
1. **P0 - Missing OTel** (src/main/java/OrderConsumer.java)
   - Kafka consumer lacks OTel interceptor
   - Template: kafka-consumer-otel-java

2. **P0 - Missing Correlation** (src/main/java/OrderProducer.java)
   - Producer not injecting x-obs-* headers
   - Template: kafka-producer-headers-java

3. **P1 - Missing Lineage Spec** (lineage/)
   - No lineage spec defining input/output mappings
   - Template: lineage-spec-kafka

[Generates diff_plan.json for PR Author Agent]
```

### PR Author Agent Skill

Transforms Diff Plans into Pull Requests.

**Triggers**:
- "generate PR from diff plan"
- "create instrumentation PR"
- "scaffold observability code"
- "generate OTel config"

**Workflow**:
1. Provide the Diff Plan JSON from Scout Agent
2. PR Author selects appropriate templates
3. Generates code, tests, and documentation
4. Creates PR with all artifacts

### CI Gatekeeper Agent Skill

Enforces observability standards in CI pipelines.

**Triggers**:
- "create observability gate"
- "configure CI enforcement"
- "generate gate policy"
- "check observability compliance"

**Gate Policies**:

| Gate | Trigger | Tier-1 Action | Tier-2+ Action |
|------|---------|---------------|----------------|
| Gate 1 | PR Merge | Block | Warn |
| Gate 2 | Migration Cutover | Block | Block |
| Gate 3 | Post-Cutover (14d) | Review | Warn |

### Telemetry Validator Agent Skill

Verifies instrumentation works in sandbox environments.

**Triggers**:
- "validate telemetry"
- "verify instrumentation"
- "check OTel spans"
- "validate correlation headers"

### Signal Factory Core Skill

Develops signal processing engines.

**Triggers**:
- "create signal engine"
- "configure signal router"
- "design graph schema"
- "implement signal processing"

### RCA Copilot Skill

Provides AI-powered incident analysis.

**Triggers**:
- "explain incident"
- "find root cause"
- "diagnose data issue"
- "what caused the alert"

## Windsurf Development Setup

### Project Structure

After setup, your project should have:

```
your-project/
├── .windsurf/
│   └── workflows/
│       ├── openspec-proposal.md
│       ├── openspec-apply.md
│       ├── openspec-archive.md
│       ├── implement-agent.md
│       ├── pr-author-generate.md
│       ├── pr-author-template.md
│       └── pr-author-test.md
├── openspec/
│   ├── project.md
│   ├── AGENTS.md
│   ├── specs/
│   │   └── {agent-name}/
│   ├── changes/
│   └── archive/
└── skills/
    └── {skill-name}/
        └── SKILL.md
```

### Available Workflows

#### `/openspec-proposal` - Create Change Proposal

Use when adding new features or modifying agents:

```bash
/openspec-proposal Add gRPC archetype to Scout Agent
```

Creates:
- `openspec/changes/{change-id}/proposal.md`
- `openspec/changes/{change-id}/tasks.md`
- `openspec/changes/{change-id}/specs/{agent}/spec.md`

#### `/openspec-apply` - Implement Change

Apply a change proposal:

```bash
/openspec-apply add-grpc-archetype
```

Works through tasks, updates code, and marks tasks complete.

#### `/openspec-archive` - Archive Completed Change

Archive after successful implementation:

```bash
/openspec-archive add-grpc-archetype
```

Merges spec delta into source specs.

#### `/implement-agent` - Build Agent from Skill

Implement a new agent or add features:

```bash
/implement-agent pr-author-agent
```

Follows the implementation sequence defined in the skill.

#### `/pr-author-generate` - Generate PR from Diff Plan

Generate instrumentation PR:

```bash
/pr-author-generate --diff-plan ./orders-enricher-diffplan.json
```

#### `/pr-author-template` - Create Template

Add new archetype template:

```bash
/pr-author-template --language go --archetype grpc-otel
```

#### `/pr-author-test` - Test Generation

Test PR Author functionality:

```bash
/pr-author-test --template kafka-consumer-otel-java
```

## Agent Workflows

### End-to-End Instrumentation Flow

1. **Scan Repository** (Scout Agent)
   ```bash
   python scripts/scan_repo.py --repo-path /path/to/repo --output diff_plan.json
   ```

2. **Generate PR** (PR Author)
   ```bash
   python scripts/generate_pr.py --diff-plan diff_plan.json --dry-run
   ```

3. **Create PR** (PR Author)
   ```bash
   python scripts/generate_pr.py --diff-plan diff_plan.json --repo-url https://github.com/org/repo
   ```

4. **CI Gate Check** (CI Gatekeeper)
   ```bash
   python scripts/check_gate.py --gate gate-1 --tier 1
   ```

5. **Validate Telemetry** (Telemetry Validator)
   ```bash
   python scripts/validate_service.py --service orders-enricher --commit abc123
   ```

### Diff Plan Schema

The Observability Diff Plan is the contract between Scout Agent and PR Author:

```json
{
  "repo": "orders-enricher",
  "repo_url": "https://github.com/company/orders-enricher",
  "diff_plan_id": "dp-abc123",
  "scan_timestamp": "2026-01-04T10:30:00Z",
  "archetypes": ["kafka-microservice", "spring-boot"],
  "confidence": 0.87,
  "tech_stack": {
    "language": "java",
    "build_system": "maven",
    "framework": "spring-boot-3.2"
  },
  "current_observability": {
    "otel_sdk": false,
    "correlation_propagation": false,
    "lineage_spec": false,
    "contract_stub": false,
    "runbook": false
  },
  "gaps": [
    {
      "type": "missing_otel",
      "location": "src/main/java/OrderConsumer.java",
      "description": "Kafka consumer lacks OTel interceptor",
      "priority": "P0",
      "template": "kafka-consumer-otel-java"
    }
  ],
  "patch_plan": [...]
}
```

## Configuration

### Environment Variables

```bash
# GitHub Integration
export GITHUB_APP_ID="12345"
export GITHUB_INSTALLATION_ID="67890"
export GITHUB_PRIVATE_KEY_PATH="/etc/autopilot/github-key.pem"

# Kafka Event Bus
export KAFKA_BOOTSTRAP_SERVERS="kafka:9092"

# OTel Collector (for validation)
export OTEL_COLLECTOR_URL="http://otel-collector:4318"

# AWS (for Signal Factory and RCA)
export AWS_REGION="us-east-1"
export NEPTUNE_ENDPOINT="wss://neptune:8182/gremlin"
export DYNAMODB_TABLE_PREFIX="autopilot"
```

### autopilot-config.yaml

```yaml
# Global settings
autopilot:
  log_level: INFO
  enable_metrics: true

# Scout Agent
scout:
  confidence_threshold: 0.7
  archetypes_enabled:
    - kafka-microservice
    - spring-boot
    - airflow-dag
    - spark-job
    - go-microservice

# PR Author
pr_author:
  enabled: true
  auto_create_pr: true
  require_human_review: true
  templates_path: "/opt/autopilot/templates"
  default_branch: "main"
  pr_labels: ["autopilot", "observability"]

# CI Gatekeeper
ci_gatekeeper:
  gate_1:
    enforce_tier_1: true
    enforce_tier_2: false

# Telemetry Validator
telemetry_validator:
  timeout_seconds: 120
  cleanup_after: true

# Signal Factory
signal_factory:
  engines:
    freshness: true
    volume: true
    drift: true
    contract: true
    dq: true

# RCA Copilot
rca_copilot:
  provider: "bedrock"
  model: "anthropic.claude-3-sonnet"
  max_tokens: 1000
```

## Troubleshooting

### Scout Agent Issues

**Problem**: Low confidence score
- **Cause**: Detection patterns don't match code structure
- **Solution**: Add custom archetype patterns or lower threshold

**Problem**: Missing archetypes
- **Cause**: Dependency files not found
- **Solution**: Ensure build files (pom.xml, go.mod, etc.) are in expected locations

### PR Author Issues

**Problem**: Template not found
- **Cause**: Template name doesn't match available templates
- **Solution**: Check `references/templates/` for available templates

**Problem**: Variable not substituted
- **Cause**: Variable missing from context
- **Solution**: Verify Diff Plan contains required fields

### CI Gatekeeper Issues

**Problem**: False positives
- **Cause**: Check thresholds too strict
- **Solution**: Tune thresholds in gate policy

**Problem**: Gate not running
- **Cause**: Webhook not configured
- **Solution**: Verify GitHub/GitLab webhook setup

### Telemetry Validator Issues

**Problem**: Timeout during validation
- **Cause**: Service slow to start or signals delayed
- **Solution**: Increase `timeout_seconds` in config

**Problem**: Missing spans
- **Cause**: OTel Collector not receiving data
- **Solution**: Check collector connectivity and config

### General Issues

**Problem**: OpenSpec commands not found
- **Solution**: Reinstall CLI: `npm install -g @fission-ai/openspec@latest`

**Problem**: Windsurf workflows not recognized
- **Solution**: Ensure workflows are in `.windsurf/workflows/` directory

## Next Steps

1. **Scan a pilot repository** with Scout Agent
2. **Review the generated Diff Plan** for accuracy
3. **Generate a test PR** in dry-run mode
4. **Set up CI gates** for Tier-1 repositories
5. **Deploy Telemetry Validator** to staging environment

For more detailed information:
- [Claude Skills Reference](CLAUDE_SKILLS.md)
- [Windsurf Integration Guide](WINDSURF_INTEGRATION.md)
- [Architecture Documentation](ARCHITECTURE.md)
