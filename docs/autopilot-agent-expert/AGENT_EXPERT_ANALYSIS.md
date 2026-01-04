# Instrumentation Autopilot: Agent Expert Analysis

## Executive Summary

The Instrumentation Autopilot system comprises **four specialized agents** that work in concert to automate observability instrumentation at scale. This document maps the complete agent pipeline, analyzes the data flows from Scout Agent output through to production validation, and defines the Claude skills required for Windsurf-based implementation.

## System Thinking Analysis

### Things & Connections

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INSTRUMENTATION AUTOPILOT                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │ REPO SCOUT   │─────▶│  PR AUTHOR   │─────▶│ CI GATEKEEPER│              │
│  │    Agent     │      │    Agent     │      │    Agent     │              │
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
│                       │    Agent     │                                      │
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
│  Signal Router → Signal Engines → Neptune Graph → RCA Copilot              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Inflow/Outflow Analysis

| Agent | Inflows | Outflows | Downstream Consumers |
|-------|---------|----------|---------------------|
| **Scout Agent** | Repository path, Git webhooks | Observability Diff Plan (JSON) | PR Author Agent |
| **PR Author** | Diff Plan, Template library | Pull Request, Code, Tests, Configs | CI Gatekeeper, Human reviewers |
| **CI Gatekeeper** | PR webhooks, Gate policies | Gate Status, Enforcement decisions | Telemetry Validator, GitHub/GitLab |
| **Telemetry Validator** | Deployed service, OTel Collector | Validation Report, Evidence | Neptune Graph, Merge approval |

### Cost of Action vs. Inaction

| Action | Benefit | Cost |
|--------|---------|------|
| **Implement Scout Agent** | Consistent gap detection across 100s of repos | Development effort, false positive tuning |
| **Implement PR Author** | 2-4 weeks → <1 day instrumentation time | Template maintenance, edge case handling |
| **Implement CI Gatekeeper** | Prevent broken observability reaching prod | CI pipeline latency, policy governance |
| **Implement Validator** | Guarantee signals actually emit | Test environment infrastructure |
| **Inaction** | None | Manual instrumentation, inconsistent coverage, slow MTTR |

---

## Agent Pipeline: From Scout Output to Production

### Stage 1: Scout Agent → Diff Plan

**Input:** Repository URL/path
**Output:** Observability Diff Plan (JSON)

```json
{
  "repo": "orders-enricher",
  "archetypes": ["kafka-microservice", "spring-boot"],
  "confidence": 0.87,
  "gaps": [
    {"type": "missing_otel", "template": "kafka-consumer-otel-java"},
    {"type": "missing_lineage_spec", "template": "lineage-spec-kafka"}
  ],
  "patch_plan": [...]
}
```

**Handoff Protocol:**
- Scout publishes Diff Plan to event bus (Kafka topic: `autopilot-events`)
- PR Author subscribes and triggers on new plans with confidence >= threshold

### Stage 2: PR Author → Pull Request

**Input:** Observability Diff Plan
**Output:** GitHub/GitLab Pull Request containing:
- Modified dependency files (pom.xml, requirements.txt, go.mod)
- OTel configuration files
- Correlation header interceptors
- Lineage spec YAML
- Contract stub YAML
- RUNBOOK.md
- Telemetry validation tests

**Key Transformations:**
1. Template selection based on `archetype` + `language`
2. Variable interpolation (SERVICE_NAME, TOPIC, URN)
3. File merge strategies (append vs. create vs. modify)
4. Test generation matching instrumented code paths

### Stage 3: CI Gatekeeper → Enforcement

**Input:** PR webhook, Gate policies
**Output:** CI check results, merge blocking/allowing

**Gate Progression:**
| Gate | Trigger | Tier-1 Action | Tier-2+ Action |
|------|---------|---------------|----------------|
| Gate 1 | PR Merge | Block | Warn |
| Gate 2 | Migration Cutover | Block | Block |
| Gate 3 | Post-Cutover (14d) | Review | Warn |

**Checks Performed:**
- OTel SDK presence
- Lineage spec validation
- Contract stub presence
- Schema compatibility (via Registry API)
- RUNBOOK.md existence

### Stage 4: Telemetry Validator → Evidence

**Input:** Deployed service (staging), OTel Collector endpoint
**Output:** Validation Report with evidence

**Validation Sequence:**
1. Deploy to isolated namespace
2. Send synthetic traffic
3. Wait for signal propagation (5-10s)
4. Query OTel Collector for expected spans
5. Validate span attributes against schema
6. Check Kafka headers for correlation IDs
7. Generate evidence (span IDs, offsets, screenshots)

---

## Hidden Assumptions Surfaced

1. **GitHub/GitLab API availability** for PR creation and status checks
2. **Schema Registry** accessible for compatibility validation
3. **OTel Collector** in staging with query API (not just ingestion)
4. **Neptune Graph** for lineage edge creation
5. **Kafka** for event bus between agents
6. **Template library** maintained and versioned
7. **Human review required** for all auto-generated PRs
8. **Service deployable** in isolated test environment

## 5 Whys: Why This Architecture?

1. **Why automate instrumentation?** → Manual instrumentation takes weeks and is inconsistent
2. **Why four agents?** → Separation of concerns: detect → generate → enforce → validate
3. **Why human-in-the-loop?** → Code changes require review; AI assists, doesn't replace
4. **Why progressive gates?** → Cultural change requires gradual enforcement
5. **Why validate in staging?** → Prevent broken instrumentation reaching production

---

## Claude Skills Required for Implementation

### Skill 1: Scout Agent (✅ COMPLETE)

**Purpose:** Detect tech stack, identify observability gaps, generate Diff Plans
**Status:** Implemented in `scout-agent.skill`
**Outputs:** Observability Diff Plan JSON

### Skill 2: PR Author Agent (🔧 REQUIRED)

**Purpose:** Transform Diff Plans into Pull Requests with code, tests, and configs
**Key Capabilities:**
- Template interpolation engine
- Multi-file PR generation
- Test scaffolding
- GitHub/GitLab API integration

**OpenSpec Workflows:**
- `/pr-author-generate` - Generate PR from Diff Plan
- `/pr-author-template` - Create new archetype template
- `/pr-author-test` - Validate generated code

### Skill 3: CI Gatekeeper Agent (🔧 REQUIRED)

**Purpose:** Enforce observability standards in CI/CD pipelines
**Key Capabilities:**
- GitHub Actions workflow generation
- Gate policy configuration
- Schema Registry integration
- Status reporting

**OpenSpec Workflows:**
- `/gatekeeper-policy` - Define gate policies
- `/gatekeeper-check` - Run gate checks locally
- `/gatekeeper-report` - Generate gate status report

### Skill 4: Telemetry Validator Agent (🔧 REQUIRED)

**Purpose:** Verify instrumentation works by running in sandbox
**Key Capabilities:**
- Test harness generation
- OTel Collector querying
- Kafka header inspection
- Evidence collection

**OpenSpec Workflows:**
- `/validator-test` - Generate validation tests
- `/validator-run` - Execute validation suite
- `/validator-report` - Generate validation report

### Skill 5: Signal Factory Core (🔧 REQUIRED)

**Purpose:** Process signals, maintain graph, power RCA Copilot
**Key Capabilities:**
- Signal Router configuration
- Signal Engine development (Freshness, Drift, Contract, DQ)
- Neptune graph schema
- DynamoDB state management

**OpenSpec Workflows:**
- `/signal-engine` - Develop new signal engine
- `/graph-schema` - Define Neptune schema
- `/signal-route` - Configure signal routing

### Skill 6: RCA Copilot (🔧 REQUIRED)

**Purpose:** AI-powered root cause analysis and incident explanation
**Key Capabilities:**
- Context retrieval (Neptune + DynamoDB)
- Evidence ranking
- Root cause candidate generation
- Action recommendation

**OpenSpec Workflows:**
- `/rca-query` - Query incident context
- `/rca-explain` - Generate incident explanation
- `/rca-action` - Recommend remediation actions

---

## Implementation Roadmap for Windsurf

### Phase 0: Foundation (Weeks 1-2)
**Deliverables:**
- Scout Agent skill (✅ Complete)
- PR Author skill skeleton
- OpenSpec project structure

**Success Criteria:**
- Scout Agent generates valid Diff Plans
- PR Author can parse Diff Plans

### Phase 1: Code Generation (Weeks 3-4)
**Deliverables:**
- PR Author template library (Java, Python, Go)
- GitHub/GitLab PR creation
- Basic test generation

**Success Criteria:**
- Auto-generated PRs pass linting
- Tests compile and run

### Phase 2: CI Integration (Weeks 5-6)
**Deliverables:**
- CI Gatekeeper GitHub Actions
- Gate policy engine
- Schema Registry integration

**Success Criteria:**
- Gate 1 checks running in CI
- Tier-1 enforcement active

### Phase 3: Validation (Weeks 7-8)
**Deliverables:**
- Telemetry Validator test harness
- OTel Collector query interface
- Evidence collection

**Success Criteria:**
- Validation passes for pilot repos
- Evidence captured in reports

### Phase 4: Signal Factory (Weeks 9-12)
**Deliverables:**
- Signal Router deployment
- Signal Engines (Freshness, Drift)
- Neptune graph schema

**Success Criteria:**
- Signals flowing to Neptune
- Basic anomaly detection

### Phase 5: RCA Copilot (Weeks 13-16)
**Deliverables:**
- Context Builder service
- LLM integration (Claude/Bedrock)
- Incident explanation UI

**Success Criteria:**
- Copilot explains simulated incidents
- MTTR < 2 minutes for Tier-1

---

## Alternatives Explored

### Agent Architecture Alternatives

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Monolithic agent | Simpler deployment | No separation of concerns | ❌ Rejected |
| 4 specialized agents | Clear responsibilities | More coordination needed | ✅ Selected |
| LLM-only (no templates) | More flexible | Inconsistent output | ❌ Rejected |
| Template-only (no LLM) | Deterministic | Can't handle edge cases | ❌ Rejected |

### Correlation Strategy Alternatives

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Trace context only | Standard approach | Breaks at async boundaries | ❌ Rejected |
| Asset lineage only | Works everywhere | No runtime correlation | ❌ Rejected |
| Hybrid model | Best of both | More complex | ✅ Selected |

### Enforcement Strategy Alternatives

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Immediate hard-fail | Quick compliance | Team resistance | ❌ Rejected |
| Warn-only forever | No friction | No enforcement | ❌ Rejected |
| Progressive gates | Cultural change | Slower rollout | ✅ Selected |

---

## Next Steps

1. **Create PR Author Skill** - Template library, GitHub API integration
2. **Create CI Gatekeeper Skill** - GitHub Actions, gate policies
3. **Create Telemetry Validator Skill** - Test harness, OTel queries
4. **Create Signal Factory Skill** - Signal engines, Neptune schema
5. **Create RCA Copilot Skill** - Context retrieval, LLM integration
6. **Integration Testing** - End-to-end pipeline validation
7. **Pilot Deployment** - 5 repos with progressive gates
