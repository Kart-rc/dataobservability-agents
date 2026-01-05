# Data Observability Agents - System Architecture

This document provides comprehensive technical architecture documentation for the Data Observability Agents system, also known as the Instrumentation Autopilot.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Agent Pipeline](#agent-pipeline)
4. [Data Flow](#data-flow)
5. [Infrastructure](#infrastructure)
6. [Integration Points](#integration-points)
7. [Deployment Model](#deployment-model)
8. [Security Architecture](#security-architecture)
9. [Observability](#observability)

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INSTRUMENTATION AUTOPILOT                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │ SCOUT AGENT  │─────▶│  PR AUTHOR   │─────▶│ CI GATEKEEPER│              │
│  │              │      │    AGENT     │      │    AGENT     │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│         │                     │                     │                       │
│         ▼                     ▼                     ▼                       │
│  Observability         Pull Request          Gate Status                   │
│    Diff Plan           + Code + Tests        + Enforcement                 │
│                                                     │                       │
│                              ┌──────────────────────┘                       │
│                              ▼                                              │
│                       ┌──────────────┐                                      │
│                       │  TELEMETRY   │                                      │
│                       │  VALIDATOR   │                                      │
│                       │    AGENT     │                                      │
│                       └──────────────┘                                      │
│                              │                                              │
│                              ▼                                              │
│                       Validation Report                                     │
│                       + Signal Evidence                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL FACTORY CORE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐             │
│  │   Signal    │───▶│  Event Bus  │───▶│   Signal Engines    │             │
│  │   Router    │    │ (Kinesis/   │    │ ┌─────┐ ┌─────┐    │             │
│  │             │    │    MSK)     │    │ │Fresh│ │ Vol │    │             │
│  └─────────────┘    └─────────────┘    │ └─────┘ └─────┘    │             │
│        │                               │ ┌─────┐ ┌─────┐    │             │
│        │ Normalization                 │ │Drift│ │ DQ  │    │             │
│        │ + Correlation                 │ └─────┘ └─────┘    │             │
│        │ + URN Resolution              │ ┌─────┐ ┌─────┐    │             │
│        ▼                               │ │Anom │ │Contr│    │             │
│  ┌─────────────┐                       │ └─────┘ └─────┘    │             │
│  │  Canonical  │                       └─────────────────────┘             │
│  │   Signal    │                               │                           │
│  │   Event     │                               ▼                           │
│  └─────────────┘                       ┌───────────────────┐               │
│                                        │ State & Graph     │               │
│                                        │ ┌─────┐ ┌─────┐  │               │
│                                        │ │DDB  │ │Nept │  │               │
│                                        │ └─────┘ └─────┘  │               │
│                                        └───────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RCA COPILOT                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐               │
│  │                  Context Builder                         │               │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │               │
│  │  │ Cache   │  │ Graph   │  │Evidence │  │Timeline │   │               │
│  │  │ Fetch   │  │ Expand  │  │ Rank    │  │ Build   │   │               │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │               │
│  │       └────────────┴────────────┴────────────┘         │               │
│  └─────────────────────────┬───────────────────────────────┘               │
│                            ▼                                                │
│                 ┌─────────────────────┐                                    │
│                 │   LLM Interface     │                                    │
│                 │  (Claude/Bedrock)   │                                    │
│                 └──────────┬──────────┘                                    │
│                            ▼                                                │
│              Explanation + Recommended Actions                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | Type | Purpose | Technology |
|-----------|------|---------|------------|
| Scout Agent | Detector | Identify observability gaps | Python, AST parsing |
| PR Author Agent | Generator | Create instrumentation PRs | Python, Jinja2, GitHub API |
| CI Gatekeeper Agent | Enforcer | Progressive gate enforcement | GitHub Actions, Python |
| Telemetry Validator | Verifier | Confirm signals in sandbox | Python, K8s, OTel |
| Signal Factory Core | Processor | Signal normalization, anomaly detection | Python, Kinesis, Neptune |
| RCA Copilot | Explainer | AI-powered incident analysis | Python, Bedrock, Neptune |

## Architecture Principles

### 1. Event-Driven Communication

Agents communicate via CloudEvents on Kafka/Kinesis:

```json
{
  "specversion": "1.0",
  "type": "autopilot.{agent}.{event_type}",
  "source": "urn:autopilot:{agent}",
  "id": "evt-{uuid}",
  "time": "2026-01-04T10:00:00Z",
  "datacontenttype": "application/json",
  "data": { ... }
}
```

### 2. Stateless Agents

- Agents don't maintain internal state
- All state stored in DynamoDB or Neptune
- Operations are idempotent (safe to retry)
- Enables horizontal scaling

### 3. Human-in-the-Loop

- All code changes require human review
- AI assists but doesn't replace humans
- Progressive enforcement allows gradual adoption

### 4. Separation of Concerns

- Each agent has single responsibility
- Clear contracts between agents (Diff Plan, Gate Status, etc.)
- Independent deployment and scaling

### 5. Progressive Gates

- Enforcement increases gradually
- Tier-1 repositories have strictest requirements
- Warn → Soft-fail → Hard-fail progression

## Agent Pipeline

### Stage 1: Scout Agent → Diff Plan

```
Input:  Repository path/URL
Output: Observability Diff Plan (JSON)

┌─────────────────────────────────────────┐
│              SCOUT AGENT                 │
├─────────────────────────────────────────┤
│                                         │
│  Repository ──▶ Archetype Detection     │
│                      │                  │
│                      ▼                  │
│              Gap Identification         │
│                      │                  │
│                      ▼                  │
│              Confidence Scoring         │
│                      │                  │
│                      ▼                  │
│              Diff Plan Generation       │
│                                         │
└─────────────────────────────────────────┘
                      │
                      ▼
              Diff Plan JSON
```

**Detection Patterns**:
- Dependency files (pom.xml, go.mod, requirements.txt)
- Framework markers (Spring Boot annotations, Gin router)
- Configuration files (application.yaml, docker-compose.yaml)

**Gap Types**:
- `missing_otel`: No OTel SDK
- `missing_correlation`: No header propagation
- `missing_lineage_spec`: No lineage YAML
- `missing_contract`: No data contract
- `missing_runbook`: No RUNBOOK.md

### Stage 2: PR Author → Pull Request

```
Input:  Observability Diff Plan
Output: Pull Request with code, tests, docs

┌─────────────────────────────────────────┐
│            PR AUTHOR AGENT              │
├─────────────────────────────────────────┤
│                                         │
│  Diff Plan ──▶ Template Selection       │
│                      │                  │
│                      ▼                  │
│              Variable Resolution        │
│                      │                  │
│                      ▼                  │
│              Template Rendering         │
│                      │                  │
│                      ▼                  │
│              PR Creation (GitHub)       │
│                                         │
└─────────────────────────────────────────┘
                      │
                      ▼
              Pull Request
              - Instrumentation code
              - Configuration files
              - Lineage specs
              - Contract stubs
              - Tests
              - RUNBOOK.md
```

**Template Library**:
```
templates/
├── java/kafka-consumer-otel/
├── java/kafka-producer-headers/
├── python/kafka-otel/
├── go/gin-otel/
└── common/lineage-spec/
```

### Stage 3: CI Gatekeeper → Enforcement

```
Input:  PR webhook, Gate policies
Output: Gate status, Enforcement decision

┌─────────────────────────────────────────┐
│          CI GATEKEEPER AGENT            │
├─────────────────────────────────────────┤
│                                         │
│  PR Webhook ──▶ Policy Lookup           │
│                      │                  │
│                      ▼                  │
│              Check Execution            │
│              - OTel SDK                 │
│              - Lineage spec             │
│              - Schema compat            │
│              - RUNBOOK                  │
│                      │                  │
│                      ▼                  │
│              Tier-Based Enforcement     │
│                      │                  │
│                      ▼                  │
│              Status Reporting           │
│                                         │
└─────────────────────────────────────────┘
                      │
                      ▼
              Gate Status
              - PASS/WARN/FAIL
              - Check details
              - Next gate info
```

### Stage 4: Telemetry Validator → Evidence

```
Input:  Deployed service, Commit SHA
Output: Validation report with evidence

┌─────────────────────────────────────────┐
│        TELEMETRY VALIDATOR AGENT        │
├─────────────────────────────────────────┤
│                                         │
│  Service ──▶ Environment Setup (K8s)    │
│                      │                  │
│                      ▼                  │
│              Traffic Generation         │
│                      │                  │
│                      ▼                  │
│              Signal Collection          │
│              - Query OTel Collector     │
│              - Check Kafka headers      │
│              - Verify lineage events    │
│                      │                  │
│                      ▼                  │
│              Evidence Capture           │
│                      │                  │
│                      ▼                  │
│              Report Generation          │
│                                         │
└─────────────────────────────────────────┘
                      │
                      ▼
              Validation Report
              - Test results
              - Span evidence
              - Kafka offsets
              - Screenshots
```

## Data Flow

### Inter-Agent Events

```
Scout Agent                    PR Author                  CI Gatekeeper
     │                              │                           │
     │  autopilot.scout.            │                           │
     │  diff-plan-created           │                           │
     │─────────────────────────────▶│                           │
     │                              │                           │
     │                              │  autopilot.pr-author.     │
     │                              │  pr-created               │
     │                              │──────────────────────────▶│
     │                              │                           │
     │                              │                           │  autopilot.gatekeeper.
     │                              │                           │  gate-status-updated
     │                              │                           │────────────────────▶
```

### Event Schemas

**Scout Agent Output**:
```json
{
  "type": "autopilot.scout.diff-plan-created",
  "data": {
    "diff_plan_id": "dp-abc123",
    "repo": "orders-enricher",
    "confidence": 0.87,
    "gaps": [...]
  }
}
```

**PR Author Output**:
```json
{
  "type": "autopilot.pr-author.pr-created",
  "data": {
    "diff_plan_id": "dp-abc123",
    "pr_number": 42,
    "pr_url": "https://github.com/.../pull/42",
    "files_changed": 8
  }
}
```

**Gatekeeper Output**:
```json
{
  "type": "autopilot.gatekeeper.gate-status-updated",
  "data": {
    "pr_number": 42,
    "gate": "gate-1",
    "status": "PASSED",
    "tier": 1,
    "checks": {...}
  }
}
```

## Infrastructure

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Runtime | Python 3.11+ | Agent implementation |
| Async | asyncio | Concurrent operations |
| HTTP | httpx | Async HTTP client |
| Container | Docker | Agent packaging |
| Orchestration | Kubernetes (EKS) | Agent deployment |
| Event Bus | Kafka (MSK) / Kinesis | Inter-agent messaging |
| Graph DB | Amazon Neptune | Asset relationships |
| State Store | DynamoDB | Signal state, caches |
| Object Store | S3 | Artifacts, evidence |
| LLM | AWS Bedrock (Claude) | RCA explanations |

### AWS Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Account                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │     EKS     │  │     MSK     │  │        Neptune          │ │
│  │  ┌───────┐  │  │  ┌───────┐  │  │                         │ │
│  │  │Scout  │  │  │  │Events │  │  │  Assets ──▶ Services    │ │
│  │  │Agent  │  │  │  │Topic  │  │  │     │                   │ │
│  │  └───────┘  │  │  └───────┘  │  │     ▼                   │ │
│  │  ┌───────┐  │  │             │  │  Incidents ──▶ Evidence │ │
│  │  │PR Auth│  │  │             │  │                         │ │
│  │  └───────┘  │  │             │  └─────────────────────────┘ │
│  │  ┌───────┐  │  │             │                               │
│  │  │Gate   │  │  │             │  ┌─────────────────────────┐ │
│  │  │keeper │  │  │             │  │       DynamoDB          │ │
│  │  └───────┘  │  │             │  │                         │ │
│  │  ┌───────┐  │  │             │  │  SignalState            │ │
│  │  │Validat│  │  │             │  │  IncidentContextCache   │ │
│  │  └───────┘  │  │             │  │                         │ │
│  │  ┌───────┐  │  │             │  └─────────────────────────┘ │
│  │  │Signal │  │  │             │                               │
│  │  │Factory│  │  │             │  ┌─────────────────────────┐ │
│  │  └───────┘  │  │             │  │       Bedrock           │ │
│  │  ┌───────┐  │  │             │  │                         │ │
│  │  │RCA    │  │  │             │  │  Claude 3 Sonnet        │ │
│  │  │Copilot│  │  │             │  │                         │ │
│  │  └───────┘  │  │             │  └─────────────────────────┘ │
│  └─────────────┘  └─────────────┘                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │     S3      │  │   Secrets   │                               │
│  │             │  │   Manager   │                               │
│  │  Artifacts  │  │             │                               │
│  │  Templates  │  │  API Keys   │                               │
│  │  Evidence   │  │  Tokens     │                               │
│  └─────────────┘  └─────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

### Version Control Systems

| Platform | Integration | Purpose |
|----------|-------------|---------|
| GitHub | REST API v3 + GraphQL | Branches, commits, PRs |
| GitHub | Webhooks | PR events, push events |
| GitHub | App + Installation | Auth, organization access |
| GitLab | REST API v4 | Branches, commits, MRs |
| GitLab | Webhooks | MR events, push events |

### Schema Registry

| System | Protocol | Purpose |
|--------|----------|---------|
| Confluent | REST API | Schema lookup, compatibility check |
| AWS Glue | REST API | Alternative schema store |

### Observability Platforms

| System | Protocol | Purpose |
|--------|----------|---------|
| OTel Collector | OTLP/gRPC | Signal ingestion |
| OTel Collector | HTTP Query | Signal verification |
| New Relic | REST API | Alerting |
| PagerDuty | REST API | Incident escalation |

## Deployment Model

### Kubernetes Deployments

| Agent | Type | Replicas | Resources |
|-------|------|----------|-----------|
| Scout Agent | CronJob | 1 scheduled | 2 CPU, 4GB |
| PR Author | Deployment | 2-5 (HPA) | 1 CPU, 2GB |
| CI Gatekeeper | Deployment | 3 (HA) | 0.5 CPU, 1GB |
| Telemetry Validator | Job | 1 per validation | 2 CPU, 4GB |
| Signal Factory | Deployment | 5-10 (HPA) | 2 CPU, 4GB |
| RCA Copilot | Deployment | 3 (HA) | 2 CPU, 8GB |

### Scaling Strategy

- **Scout Agent**: Scheduled runs, scale vertically
- **PR Author**: HPA on queue depth
- **CI Gatekeeper**: Fixed HA, scale on webhook rate
- **Telemetry Validator**: Ephemeral jobs, parallel validation
- **Signal Factory**: HPA on consumer lag
- **RCA Copilot**: Fixed HA, optimize for latency

## Security Architecture

### Authentication & Authorization

- **GitHub**: App-based authentication with installation tokens
- **AWS**: IAM roles for service accounts (IRSA)
- **Inter-agent**: Mutual TLS in Kubernetes

### Secrets Management

- All secrets in AWS Secrets Manager
- No credentials in code or containers
- Rotation policies for tokens

### Network Security

- Private subnets for all agents
- VPC endpoints for AWS services
- Network policies in Kubernetes

### Data Security

- PII redaction in logs
- Encryption at rest (KMS)
- Encryption in transit (TLS 1.3)

## Observability

### Metrics

All agents emit Prometheus metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `{agent}_requests_total` | Counter | Total requests processed |
| `{agent}_errors_total` | Counter | Total errors |
| `{agent}_duration_seconds` | Histogram | Processing duration |
| `{agent}_queue_depth` | Gauge | Pending items |

### Tracing

All agents participate in distributed tracing:

- OTel SDK integrated
- Trace context propagation via CloudEvents
- Spans for external calls (GitHub, Neptune, etc.)

### Logging

Structured JSON logging with:

- Correlation IDs
- Request context
- Error details
- Performance data

### Alerting

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Agent Down | No heartbeat 5m | P1 | Page on-call |
| High Error Rate | >5% errors 10m | P2 | Notify team |
| Slow Processing | p95 > 2x baseline | P3 | Investigate |
| Queue Backlog | Depth > 1000 | P2 | Scale up |

## Performance Requirements

| Agent | Latency Target | Throughput |
|-------|----------------|------------|
| Scout Agent | < 5 min/repo | 10 repos/hour |
| PR Author | < 30 sec/PR | 100 PRs/day |
| CI Gatekeeper | < 60 sec/check | 1000 checks/day |
| Telemetry Validator | < 120 sec | 50 validations/day |
| Signal Factory | < 1 sec/event | 10K events/sec |
| RCA Copilot | < 120 sec | 100 queries/hour |
