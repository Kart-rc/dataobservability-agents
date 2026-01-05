# Claude Skills Reference

This document provides comprehensive documentation for all Claude Skills in the Data Observability Agents system. These skills enable AI-assisted development of observability instrumentation.

## Table of Contents

1. [What are Claude Skills?](#what-are-claude-skills)
2. [Skill Installation](#skill-installation)
3. [Scout Agent Skill](#scout-agent-skill)
4. [PR Author Agent Skill](#pr-author-agent-skill)
5. [CI Gatekeeper Agent Skill](#ci-gatekeeper-agent-skill)
6. [Telemetry Validator Agent Skill](#telemetry-validator-agent-skill)
7. [Signal Factory Core Skill](#signal-factory-core-skill)
8. [RCA Copilot Agent Skill](#rca-copilot-agent-skill)
9. [Skill Development](#skill-development)

## What are Claude Skills?

Claude Skills are specialized instruction sets that enable Claude to perform domain-specific tasks. Each skill contains:

- **SKILL.md**: Core skill definition with triggers, workflows, and references
- **scripts/**: Python scripts for execution
- **references/**: Templates, schemas, and lookup data
- **assets/**: OpenSpec specs and Windsurf workflows

Skills can be:
- Uploaded to Claude Projects for interactive use
- Extracted for Windsurf IDE integration
- Used as prompts in API-based integrations

## Skill Installation

### Claude Projects

1. Download the `.skill` file (ZIP archive)
2. Upload to Claude Projects
3. Claude automatically parses the skill definition
4. Use trigger phrases to invoke the skill

### Windsurf Integration

```bash
# Extract skill package
unzip {skill-name}.skill -d .

# Copy Windsurf workflows
cp -r {skill-name}/assets/windsurf/workflows/* .windsurf/workflows/

# Copy OpenSpec configuration
cp -r {skill-name}/assets/openspec/* openspec/
```

---

## Scout Agent Skill

**Status**: Complete
**Location**: `docs/scout/scout-agent.skill`

### Purpose

Detect tech stack, identify observability gaps, and generate Observability Diff Plans for repositories.

### Trigger Phrases

- "scan repo for observability gaps"
- "analyze repository instrumentation"
- "generate diff plan for [service-name]"
- "find missing OTel instrumentation"
- "detect observability coverage"

### Core Responsibilities

1. **Archetype Detection**: Identify repository patterns (kafka-microservice, spring-boot, airflow-dag, etc.)
2. **Gap Identification**: Find missing OTel, correlation headers, lineage specs, contracts
3. **Diff Plan Generation**: Produce JSON specification for PR Author
4. **Confidence Scoring**: Assess automation confidence for each gap

### Supported Archetypes

| Archetype | Language | Detection Pattern |
|-----------|----------|-------------------|
| kafka-microservice | Java | spring-kafka dependency |
| kafka-microservice | Python | kafka-python, confluent-kafka |
| kafka-microservice | Go | sarama, segmentio/kafka-go |
| spring-boot | Java | spring-boot-starter dependency |
| airflow-dag | Python | DAG definition files |
| spark-job | Scala/Python | SparkSession usage |
| go-microservice | Go | gin, echo, fiber, chi frameworks |
| grpc-service | Multi | .proto files, grpc dependencies |

### Output: Observability Diff Plan

```json
{
  "repo": "orders-enricher",
  "archetypes": ["kafka-microservice", "spring-boot"],
  "confidence": 0.87,
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

### Scripts

- `scripts/scan_repo.py`: Main repository scanner
- `scripts/detect_archetype.py`: Archetype detection logic
- `scripts/generate_diff_plan.py`: Diff Plan generation

### References

- `references/archetypes.md`: Archetype definitions and patterns
- `references/gap-templates.md`: Gap type to template mapping
- `references/diff-plan-schema.md`: JSON schema for Diff Plans

---

## PR Author Agent Skill

**Status**: Defined
**Location**: `docs/pr-author-agent/SKILL.md`, `docs/autopilot-agent-expert/skills/pr-author-agent/SKILL.md`

### Purpose

Transform Observability Diff Plans into complete Pull Requests with instrumentation code, configuration, tests, and documentation.

### Trigger Phrases

- "generate PR from diff plan"
- "create instrumentation PR"
- "scaffold observability code"
- "generate OTel config"
- "create telemetry PR"

### Core Responsibilities

1. **Diff Plan Parsing**: Validate and parse Scout Agent output
2. **Template Selection**: Choose archetype-specific templates
3. **Code Generation**: Generate OTel interceptors, correlation headers, middleware
4. **Lineage Spec Creation**: Create YAML specs for input/output mappings
5. **Contract Stub Generation**: Create data contract definitions with SLOs
6. **Test Scaffolding**: Generate telemetry validation tests
7. **Runbook Generation**: Create operational runbooks
8. **PR Creation**: Create GitHub/GitLab PR with all artifacts

### Template Library

Templates organized by language and archetype:

```
references/templates/
├── java/
│   ├── kafka-consumer-otel/
│   ├── kafka-producer-otel/
│   ├── kafka-producer-headers/
│   ├── spring-boot-otel/
│   └── grpc-otel/
├── python/
│   ├── kafka-otel/
│   ├── airflow-openlineage/
│   └── spark-openlineage/
├── go/
│   ├── kafka-sarama-otel/
│   ├── gin-otel/
│   ├── echo-otel/
│   ├── grpc-otel/
│   └── chi-otel/
└── common/
    ├── lineage-spec/
    ├── contract-stub/
    ├── runbook/
    └── test/
```

### Variable Interpolation

Templates use `${VAR}` syntax:

| Variable | Source | Example |
|----------|--------|---------|
| `${SERVICE_NAME}` | Diff Plan repo name | `orders-enricher` |
| `${SERVICE_URN}` | Computed from repo | `urn:svc:prod:commerce:orders-enricher` |
| `${INPUT_TOPIC}` | Detected from code | `orders_raw` |
| `${OUTPUT_TOPIC}` | Detected from code | `orders_enriched` |
| `${OTEL_VERSION}` | Config or latest | `1.32.0` |

### Windsurf Workflows

- `/pr-author-generate`: Generate PR from Diff Plan
- `/pr-author-template`: Create new archetype template
- `/pr-author-test`: Test generated code locally

### Scripts

- `scripts/generate_pr.py`: PR generation orchestrator
- `scripts/template_engine.py`: Template interpolation engine
- `scripts/github_client.py`: GitHub API wrapper
- `scripts/gitlab_client.py`: GitLab API wrapper

---

## CI Gatekeeper Agent Skill

**Status**: Defined
**Location**: `docs/autopilot-agent-expert/skills/ci-gatekeeper-agent/SKILL.md`

### Purpose

Enforce observability standards through CI pipeline checks with progressive gating.

### Trigger Phrases

- "create observability gate"
- "configure CI enforcement"
- "generate gate policy"
- "check observability compliance"
- "add observability CI workflow"

### Core Responsibilities

1. **Gate Policy Management**: Define and enforce gate policies by tier
2. **CI Workflow Generation**: Create GitHub Actions/Jenkins pipelines
3. **Schema Validation**: Check schema compatibility against registry
4. **Status Reporting**: Report gate status to PRs and event bus
5. **Progressive Enforcement**: Manage warn → soft-fail → hard-fail transitions

### Gate Policies

#### Gate 1: PR Merge (Pre-Merge)

**Requirements**:
- OTel SDK in dependencies
- Asset URN tags present
- Owner metadata defined
- RUNBOOK.md exists
- Lineage spec present (Tier-1)
- Contract stub present (Tier-1)

| Tier | On Failure |
|------|------------|
| Tier-1 | Block merge |
| Tier-2+ | Warn only |

#### Gate 2: Migration Cutover

**Requirements**:
- Signals live in prod (verified)
- Freshness/volume monitors configured
- On-call route established
- Blast radius queryable in Neptune

| Tier | On Failure |
|------|------------|
| All | Block cutover |

#### Gate 3: Post-Cutover (14 days)

**Requirements**:
- Schema change events wired
- Lineage edges present in Neptune
- DQ checks configured (2+ high-value)
- No critical incidents in window

| Tier | On Failure |
|------|------------|
| Tier-1 | Leadership review |
| Tier-2+ | Warn only |

### Generated Workflow Example

```yaml
name: Observability Gate
on: [pull_request]

jobs:
  gate-1-baseline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check OTel SDK
        run: |
          # Language-specific OTel detection
          grep -q "opentelemetry" pom.xml || grep -q "opentelemetry" go.mod
      - name: Check Lineage Spec
        run: |
          [ -d "lineage" ] && ls lineage/*.yaml
      - name: Enforce by Tier
        run: |
          TIER=$(yq '.service.tier' lineage/*.yaml)
          # Tier-based enforcement logic
```

### Scripts

- `scripts/generate_workflow.py`: GitHub Actions generator
- `scripts/check_gate.py`: Local gate check runner
- `scripts/report_status.py`: Status reporter

---

## Telemetry Validator Agent Skill

**Status**: Defined
**Location**: `docs/autopilot-agent-expert/skills/telemetry-validator-agent/SKILL.md`

### Purpose

Verify instrumentation works by running services in sandbox environments and confirming expected signals arrive.

### Trigger Phrases

- "validate telemetry"
- "verify instrumentation"
- "check OTel spans"
- "validate correlation headers"
- "test observability setup"

### Core Responsibilities

1. **Environment Setup**: Spin up isolated test environments (K8s namespace)
2. **Traffic Generation**: Send synthetic requests to exercise code paths
3. **Signal Querying**: Query OTel Collector for expected spans/metrics
4. **Header Validation**: Verify correlation headers in Kafka messages
5. **Lineage Verification**: Confirm OpenLineage events for data jobs
6. **Evidence Collection**: Capture proof of successful validation
7. **Report Generation**: Produce detailed validation reports

### Validation Process

1. Deploy service to isolated namespace
2. Send synthetic traffic based on archetype
3. Wait for signal propagation (5-10s)
4. Query OTel Collector for expected spans
5. Validate span attributes against schema
6. Check Kafka headers for correlation IDs
7. Generate evidence (span IDs, offsets, screenshots)

### Expected Signals by Archetype

| Archetype | Expected Signals |
|-----------|------------------|
| Kafka Producer | Span: `{topic} send`, Attrs: `messaging.destination` |
| Kafka Consumer | Span: `{topic} receive`, Attrs: `consumer_group`, `partition` |
| Airflow Task | OpenLineage RunEvent with inputs/outputs |
| Spark Job | OpenLineage with column lineage facet |
| HTTP Handler | Span: `HTTP {method}`, Attrs: `http.route` |
| gRPC Server | Span: `{service}/{method}`, Attrs: `rpc.system` |

### Validation Report Schema

```json
{
  "validation_id": "val-2026-01-04-001",
  "repository": "orders-enricher",
  "commit_sha": "abc123def",
  "status": "PASSED",
  "tests": [
    {
      "name": "otel_spans_emitted",
      "status": "PASSED",
      "expected": 3,
      "actual": 3
    },
    {
      "name": "correlation_headers_present",
      "status": "PASSED",
      "headers_validated": ["traceparent", "x-obs-producer-service"]
    }
  ],
  "evidence": {
    "span_ids": ["span-001", "span-002"],
    "kafka_offsets": {"orders_enriched": 12345}
  }
}
```

### Scripts

- `scripts/validate_service.py`: Main validation orchestrator
- `scripts/traffic_generator.py`: Synthetic traffic generation
- `scripts/otel_client.py`: OTel Collector query client
- `scripts/kafka_inspector.py`: Kafka header inspection
- `scripts/report_generator.py`: Validation report generation

---

## Signal Factory Core Skill

**Status**: Defined
**Location**: `docs/autopilot-agent-expert/skills/signal-factory-core/SKILL.md`

### Purpose

Process observability signals, maintain the Neptune knowledge graph, and power the RCA Copilot with pre-computed incident context.

### Trigger Phrases

- "create signal engine"
- "configure signal router"
- "design graph schema"
- "implement signal processing"
- "add signal type"

### Core Responsibilities

1. **Signal Router**: Normalize and route raw telemetry to engines
2. **Signal Engines**: Detect anomalies (Freshness, Volume, Drift, Contract, DQ)
3. **Neptune Graph**: Maintain asset relationships and lineage
4. **DynamoDB State**: Track signal state and incident context

### Architecture

```
Signal Router → Event Bus → Signal Engines
                               │
                               ▼
                    Neptune Graph + DynamoDB State
```

### Signal Engines

| Engine | Purpose | Detection |
|--------|---------|-----------|
| Freshness | Stale data detection | SLA breach on arrival time |
| Volume | Throughput anomalies | 3-sigma deviation from baseline |
| Drift | Schema changes | Breaking compatibility changes |
| Contract | SLO violations | Contract breach detection |
| DQ | Quality issues | Deequ rule failures |
| Anomaly | ML-based detection | Multi-metric anomalies |

### Neptune Graph Schema

**Node Types**:
- `Asset`: Data assets (topics, tables, datasets)
- `Service`: Producing/consuming services
- `Incident`: Active incidents
- `Evidence`: Root cause evidence

**Edge Types**:
- `PRODUCES`: Service → Asset
- `CONSUMES`: Asset → Service
- `AFFECTS`: Incident → Asset
- `SUPPORTED_BY`: Incident → Evidence

### Scripts

- `scripts/signal_router.py`: Event normalization and routing
- `scripts/freshness_engine.py`: Freshness detection
- `scripts/volume_engine.py`: Volume anomaly detection
- `scripts/drift_engine.py`: Schema drift detection
- `scripts/graph_writer.py`: Neptune graph operations
- `scripts/state_manager.py`: DynamoDB state management

---

## RCA Copilot Agent Skill

**Status**: Defined
**Location**: `docs/autopilot-agent-expert/skills/rca-copilot-agent/SKILL.md`

### Purpose

Transform raw observability data into actionable incident explanations with AI-powered root cause analysis.

### Trigger Phrases

- "explain incident"
- "find root cause"
- "diagnose data issue"
- "what caused the alert"
- "RCA for incident [ID]"

### Core Responsibilities

1. **Context Retrieval**: Fetch pre-computed incident context from DynamoDB cache
2. **Graph Expansion**: Query Neptune for blast radius and lineage
3. **Evidence Ranking**: Score and rank root cause candidates
4. **Explanation Generation**: Produce natural language incident summaries via LLM
5. **Action Recommendation**: Suggest remediation steps and runbooks

### Architecture

```
Cache Fetch → Graph Expand → Evidence Rank → Timeline Build
                                    │
                                    ▼
                            LLM Interface (Claude/Bedrock)
                                    │
                                    ▼
                          Explanation + Actions
```

### Output Format

```json
{
  "incident_id": "INC-2026-01-04-001",
  "query_latency_ms": 1823,
  "root_cause": {
    "summary": "Schema validation failed at ingestion gateway",
    "details": "Field total_amount expected double, received string",
    "confidence": 0.94
  },
  "evidence": [
    {
      "type": "schema_rejection",
      "description": "94% reject rate increase after 12:10Z",
      "confidence": 0.94
    }
  ],
  "impact": {
    "blast_radius": ["orders_enriched topic", "bronze.orders_enriched"],
    "affected_teams": ["orders-team", "analytics-team"],
    "data_loss_estimate": "~5000 events not ingested"
  },
  "recommended_actions": [
    {
      "action": "rollback",
      "target": "orders-api",
      "command": "kubectl rollout undo deployment/orders-api",
      "urgency": "immediate"
    }
  ],
  "prevention": [
    "Enable schema compatibility check in CI pipeline"
  ]
}
```

### Performance Requirements

- **Cache hit latency**: < 10ms
- **Graph expansion**: < 500ms for depth=3
- **LLM generation**: < 2000ms
- **Total query latency**: < 2 minutes (SLA for Tier-1)

### Scripts

- `scripts/context_builder.py`: Incident context assembly
- `scripts/graph_queries.py`: Neptune Gremlin queries
- `scripts/evidence_ranker.py`: Evidence scoring and ranking
- `scripts/explanation_engine.py`: LLM-powered explanations
- `scripts/action_recommender.py`: Remediation suggestions

---

## Skill Development

### Creating a New Skill

1. **Create skill directory**:
   ```bash
   mkdir -p skills/{skill-name}/{scripts,references,assets}
   ```

2. **Create SKILL.md** with:
   - YAML frontmatter (name, description)
   - Core responsibilities
   - Workflow steps
   - Scripts and references

3. **Add scripts** for skill logic

4. **Add references** (templates, schemas)

5. **Create OpenSpec integration**:
   ```bash
   mkdir -p skills/{skill-name}/assets/openspec/specs/{skill-name}
   ```

6. **Create Windsurf workflows**:
   ```bash
   mkdir -p skills/{skill-name}/assets/windsurf/workflows
   ```

### Skill Package Format

Skills are packaged as ZIP files with `.skill` extension:

```
{skill-name}.skill (ZIP)
├── SKILL.md
├── scripts/
│   └── *.py
├── references/
│   └── *.md, *.json, *.yaml
└── assets/
    ├── openspec/
    │   ├── project.md
    │   ├── AGENTS.md
    │   └── specs/{skill-name}/spec.md
    └── windsurf/
        └── workflows/*.md
```

### Best Practices

1. **Clear Triggers**: Define unambiguous trigger phrases
2. **Modular Scripts**: Keep scripts focused on single responsibility
3. **Schema Validation**: Validate all inputs/outputs
4. **Error Handling**: Provide actionable error messages
5. **Documentation**: Include examples in SKILL.md
6. **Testing**: Add test cases for all scripts
