# Instrumentation Autopilot: Implementation Roadmap for Windsurf

## Executive Summary

This document provides a complete implementation plan for the Instrumentation Autopilot system using Windsurf development workflows and OpenSpec spec-driven development.

## Quick Start

### 1. Install Scout Agent Skill (✅ Complete)

Upload `scout-agent.skill` to Claude Projects or extract for Windsurf:
```bash
unzip scout-agent.skill -d .
cp -r scout-agent/assets/windsurf/workflows/* .windsurf/workflows/
cp -r scout-agent/assets/openspec/* openspec/
```

### 2. Initialize OpenSpec

```bash
npm install -g @fission-ai/openspec@latest
openspec init
# Select Windsurf integration
```

### 3. Use Windsurf Workflows

```
/openspec-proposal Add feature to Scout Agent
/openspec-apply add-feature
/openspec-archive add-feature
```

---

## Agent Implementation Sequence

### Phase 1: Scout Agent → PR Author Pipeline (Weeks 1-4)

#### Week 1-2: Scout Agent Enhancement
- [x] Base Scout Agent complete
- [ ] Add Go framework support ✅
- [ ] Add gRPC archetype
- [ ] Add streaming (Flink/Kafka Streams) archetype

#### Week 3-4: PR Author Agent
- [ ] Template engine implementation
- [ ] GitHub API integration
- [ ] Code generation for Java/Python/Go
- [ ] Test scaffolding
- [ ] PR creation workflow

**Milestone:** Auto-generated PRs with >50% acceptance rate

### Phase 2: CI Integration (Weeks 5-6)

#### Week 5: CI Gatekeeper Agent
- [ ] GitHub Actions workflow generation
- [ ] Gate policy engine
- [ ] Schema Registry integration
- [ ] Status reporting to PRs

#### Week 6: Gate Enforcement
- [ ] Gate 1 implementation (PR merge)
- [ ] Tier-based enforcement logic
- [ ] Event bus integration for status

**Milestone:** Gate 1 enforcing on Tier-1 repos

### Phase 3: Validation (Weeks 7-8)

#### Week 7: Telemetry Validator Agent
- [ ] Test harness generation
- [ ] OTel Collector query client
- [ ] Synthetic traffic generation
- [ ] Kafka header inspection

#### Week 8: Validation Pipeline
- [ ] K8s namespace orchestration
- [ ] Evidence collection
- [ ] Validation report generation
- [ ] GitHub status integration

**Milestone:** Validation passes for pilot repos

### Phase 4: Signal Factory (Weeks 9-12)

#### Week 9-10: Signal Router + Engines
- [ ] Signal Router deployment
- [ ] Freshness Engine
- [ ] Volume Engine
- [ ] Schema Drift Engine

#### Week 11-12: Graph + State
- [ ] Neptune graph schema deployment
- [ ] DynamoDB state tables
- [ ] Contract Engine
- [ ] DQ Engine

**Milestone:** Signals flowing to Neptune

### Phase 5: RCA Copilot (Weeks 13-16)

#### Week 13-14: Context Builder
- [ ] Incident context retrieval
- [ ] Graph expansion queries
- [ ] Evidence ranking

#### Week 15-16: Explanation Engine
- [ ] LLM integration (Bedrock/Claude)
- [ ] Prompt engineering
- [ ] Action recommendation
- [ ] API deployment

**Milestone:** MTTR < 2 minutes for Tier-1

---

## Claude Skills Required

| Skill | Status | Purpose |
|-------|--------|---------|
| `scout-agent` | ✅ Complete | Detect observability gaps |
| `pr-author-agent` | 🔧 Defined | Generate instrumentation PRs |
| `ci-gatekeeper-agent` | 🔧 Defined | Enforce observability gates |
| `telemetry-validator-agent` | 🔧 Defined | Verify signals in sandbox |
| `signal-factory-core` | 🔧 Defined | Process signals, maintain graph |
| `rca-copilot-agent` | 🔧 Defined | AI-powered incident explanation |

---

## Windsurf Development Workflows

### Available Workflows

| Workflow | Command | Purpose |
|----------|---------|---------|
| OpenSpec Proposal | `/openspec-proposal` | Create change proposal |
| OpenSpec Apply | `/openspec-apply` | Implement change |
| OpenSpec Archive | `/openspec-archive` | Archive completed change |
| Implement Agent | `/implement-agent` | Build agent from skill |

### Typical Development Flow

1. **Start Feature**
   ```
   /openspec-proposal Add Kafka Streams archetype to Scout Agent
   ```

2. **Implement**
   ```
   /openspec-apply add-kafka-streams-archetype
   ```

3. **Test**
   - Run unit tests
   - Test against sample repository
   - Validate output schema

4. **Complete**
   ```
   /openspec-archive add-kafka-streams-archetype
   ```

---

## File Structure After Implementation

```
instrumentation-autopilot/
├── .windsurf/
│   └── workflows/
│       ├── openspec-proposal.md
│       ├── openspec-apply.md
│       ├── openspec-archive.md
│       └── implement-agent.md
├── openspec/
│   ├── project.md
│   ├── AGENTS.md
│   ├── specs/
│   │   ├── scout-agent/
│   │   ├── pr-author/
│   │   ├── ci-gatekeeper/
│   │   ├── telemetry-validator/
│   │   ├── signal-factory/
│   │   └── rca-copilot/
│   ├── changes/
│   │   └── {active-changes}/
│   └── archive/
│       └── {completed-changes}/
├── agents/
│   ├── scout-agent/
│   │   ├── scripts/
│   │   ├── references/
│   │   └── tests/
│   ├── pr-author/
│   ├── ci-gatekeeper/
│   ├── telemetry-validator/
│   ├── signal-factory/
│   └── rca-copilot/
├── config/
│   ├── autopilot-config.yaml
│   └── {agent}-config.yaml
└── deploy/
    ├── kubernetes/
    └── terraform/
```

---

## Success Metrics

| Metric | Baseline | Week 4 | Week 8 | Week 12 | Week 16 |
|--------|----------|--------|--------|---------|---------|
| Repos instrumented | 20% | 40% | 70% | 90% | >95% |
| PR acceptance rate | N/A | 50% | 70% | 80% | >85% |
| Gate compliance | 0% | 30% | 70% | 95% | 100% |
| Validation accuracy | N/A | N/A | 80% | 95% | >98% |
| MTTR (Tier-1) | 30min | 30min | 15min | 5min | <2min |

---

## Next Actions

1. **Immediate**: Review Scout Agent skill, test on pilot repository
2. **This Week**: Begin PR Author Agent implementation
3. **This Sprint**: Complete Scout → PR Author pipeline
4. **This Month**: CI Gatekeeper integration with GitHub

## Resources

- **Scout Agent Skill**: `scout-agent.skill` (attached)
- **Skill Definitions**: `/skills/{agent-name}/SKILL.md`
- **OpenSpec Project**: `/openspec/project.md`
- **AI Instructions**: `/openspec/AGENTS.md`
