# Instrumentation Autopilot - OpenSpec Project

## Purpose

The Instrumentation Autopilot is a suite of AI-powered agents that automate observability instrumentation at scale. This project encompasses six interconnected components that work together to detect, implement, validate, and enforce observability standards across repositories.

## System Architecture

```
Scout Agent → PR Author → CI Gatekeeper → Telemetry Validator
                                    ↓
                           Signal Factory Core
                                    ↓
                              RCA Copilot
```

## Tech Stack

### Agent Runtime
- **Language**: Python 3.11+
- **Async**: asyncio for concurrent operations
- **HTTP**: httpx for async HTTP clients
- **CLI**: Click for command-line interfaces

### Infrastructure
- **Container Orchestration**: Kubernetes (EKS)
- **Event Bus**: Kafka (MSK) / Kinesis
- **Graph Database**: Amazon Neptune (Gremlin)
- **State Store**: DynamoDB
- **Object Storage**: S3
- **LLM**: AWS Bedrock (Claude)

### Observability
- **Tracing**: OpenTelemetry
- **Lineage**: OpenLineage
- **Metrics**: Prometheus / CloudWatch
- **Logging**: CloudWatch Logs

### Version Control Integration
- **Primary**: GitHub (App + Webhooks + API)
- **Secondary**: GitLab (Webhooks + API)

## Agent Components

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| Scout Agent | Detect gaps | Repository path | Diff Plan JSON |
| PR Author | Generate code | Diff Plan | Pull Request |
| CI Gatekeeper | Enforce gates | PR webhook | Gate status |
| Telemetry Validator | Verify signals | Deployed service | Validation report |
| Signal Factory | Process signals | Raw telemetry | Graph + state |
| RCA Copilot | Explain incidents | Incident ID | Explanation |

## Project Conventions

### Code Style
- Python: PEP 8, Black formatting, type hints required
- YAML: 2-space indentation, explicit types
- JSON Schema: Draft-07

### Architecture Patterns
- Event-driven communication between agents
- Stateless agent design (state in DynamoDB)
- Idempotent operations (safe to retry)
- Human-in-the-loop for code changes

### Testing Strategy
- Unit tests for business logic
- Integration tests for agent interactions
- Contract tests for API boundaries
- Chaos tests for failure modes

### Observability Standards
- All agents emit OTel traces
- Structured logging with correlation IDs
- Metrics for throughput and latency
- Alerting via New Relic + PagerDuty

## Important Constraints

### Performance
- Scout Agent scan: < 5 minutes per repo
- PR generation: < 30 seconds
- Gate check: < 60 seconds
- Validation: < 120 seconds
- RCA query: < 120 seconds (2 min SLA)

### Security
- No credentials in generated code
- PII redaction in logs
- Least-privilege IAM roles
- Secrets from AWS Secrets Manager

### Scalability
- Support 500+ repositories
- Handle 100+ PRs per day
- Process 10K signals per second
- Store 1 year of graph history

## Deployment Model

| Agent | Deployment | Replicas | Resources |
|-------|------------|----------|-----------|
| Scout Agent | CronJob (K8s) | 1 scheduled | 2 CPU, 4GB |
| PR Author | Deployment | 2-5 (HPA) | 1 CPU, 2GB |
| CI Gatekeeper | GitHub App | 3 (HA) | 0.5 CPU, 1GB |
| Telemetry Validator | Job (on-demand) | 1 per validation | 2 CPU, 4GB |
| Signal Factory | Deployment | 5-10 (HPA) | 2 CPU, 4GB |
| RCA Copilot | Deployment | 3 (HA) | 2 CPU, 8GB |

## Rollout Strategy

### Phase 0: Foundations (Weeks 1-2)
- Deploy Scout Agent on 5 pilot repos
- PR Author generates but doesn't auto-create

### Phase 1: Code Generation (Weeks 3-4)
- Auto-PR creation enabled
- Gate 1 in warn-only mode
- Target: 50% PR acceptance rate

### Phase 2: Enforcement (Weeks 5-8)
- Gate 1 enforcement for Tier-1
- Telemetry Validator in staging
- Target: 100% Tier-1 compliant

### Phase 3: Scale (Weeks 9-12)
- Full rollout to all repos
- Gate 2 for migrations
- Target: MTTR < 2 minutes

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Repos with baseline telemetry | ~20% | >90% | 12 weeks |
| PR acceptance rate | N/A | >70% | 4 weeks |
| Validation accuracy | N/A | >95% | 6 weeks |
| Time to first signal (new repo) | 2-4 weeks | <1 day | 8 weeks |
| MTTR for Tier-1 incidents | >30 min | <2 min | 12 weeks |
