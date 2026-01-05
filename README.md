# Data Observability Agents

A comprehensive suite of AI-powered agents and Claude Skills for automating observability instrumentation at scale. This system implements the **Instrumentation Autopilot** architecture, enabling organizations to achieve consistent, high-quality observability across hundreds of repositories.

## Overview

The Data Observability Agents system consists of six interconnected components that work together to detect, implement, validate, and enforce observability standards:

```
Scout Agent → PR Author → CI Gatekeeper → Telemetry Validator
                                    ↓
                           Signal Factory Core
                                    ↓
                              RCA Copilot
```

### Key Benefits

- **Automated Gap Detection**: Scout Agent scans repositories to identify missing instrumentation
- **Code Generation**: PR Author creates production-ready PRs with OTel, correlation headers, and lineage specs
- **Progressive Enforcement**: CI Gatekeeper implements tiered enforcement (warn → soft-fail → hard-fail)
- **Signal Validation**: Telemetry Validator confirms instrumentation works in sandbox environments
- **Knowledge Graph**: Signal Factory maintains asset relationships and detects anomalies
- **AI-Powered RCA**: RCA Copilot achieves sub-2-minute MTTR for Tier-1 incidents

## Quick Start

### 1. Install Scout Agent Skill (Claude Projects)

```bash
# Extract skill for Windsurf integration
unzip docs/scout/scout-agent.skill -d .
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

```bash
/openspec-proposal Add feature to Scout Agent
/openspec-apply add-feature
/openspec-archive add-feature
```

## Agent Components

| Agent | Status | Purpose | Output |
|-------|--------|---------|--------|
| **Scout Agent** | Complete | Detect observability gaps | Diff Plan JSON |
| **PR Author Agent** | Defined | Generate instrumentation PRs | Pull Request |
| **CI Gatekeeper Agent** | Defined | Enforce observability gates | Gate Status |
| **Telemetry Validator Agent** | Defined | Verify signals in sandbox | Validation Report |
| **Signal Factory Core** | Defined | Process signals, maintain graph | Graph + State |
| **RCA Copilot** | Defined | AI-powered incident explanation | Explanation |

## Repository Structure

```
dataobservability-agents/
├── README.md                          # This file
├── docs/
│   ├── GETTING_STARTED.md             # Comprehensive getting started guide
│   ├── CLAUDE_SKILLS.md               # Claude Skills documentation
│   ├── WINDSURF_INTEGRATION.md        # Windsurf workflows guide
│   ├── ARCHITECTURE.md                # System architecture
│   ├── DESIGN_ALIGNMENT.md            # Design document alignment
│   ├── Design/                        # Original design documents
│   │   ├── Data Observability System Design.docx
│   │   ├── Instrumentation_Autopilot_Technical_Design.docx
│   │   └── ...
│   ├── scout/                         # Scout Agent skill package
│   │   └── scout-agent.skill
│   ├── pr-author-agent/               # PR Author Agent skill
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   │   ├── openspec/
│   │   │   └── windsurf/workflows/
│   │   └── references/
│   └── autopilot-agent-expert/        # Central autopilot documentation
│       ├── AGENT_EXPERT_ANALYSIS.md
│       ├── IMPLEMENTATION_ROADMAP.md
│       ├── openspec/
│       └── skills/
│           ├── pr-author-agent/
│           ├── ci-gatekeeper-agent/
│           ├── telemetry-validator-agent/
│           ├── signal-factory-core/
│           └── rca-copilot-agent/
└── LICENSE
```

## Claude Skills

This repository includes Claude Skills for AI-assisted development:

| Skill | Description | Triggers |
|-------|-------------|----------|
| `scout-agent` | Detect observability gaps in repositories | "scan repo", "find gaps" |
| `pr-author-agent` | Generate instrumentation PRs | "generate PR from diff plan" |
| `ci-gatekeeper-agent` | Enforce observability gates | "create observability gate" |
| `telemetry-validator-agent` | Verify instrumentation works | "validate telemetry" |
| `signal-factory-core` | Process signals, maintain graph | "create signal engine" |
| `rca-copilot-agent` | AI-powered root cause analysis | "explain incident" |

See [CLAUDE_SKILLS.md](docs/CLAUDE_SKILLS.md) for detailed skill documentation.

## Windsurf Integration

This repository is designed for Windsurf-based development using OpenSpec workflows:

### Available Workflows

| Workflow | Command | Purpose |
|----------|---------|---------|
| OpenSpec Proposal | `/openspec-proposal` | Create change proposal |
| OpenSpec Apply | `/openspec-apply` | Implement change |
| OpenSpec Archive | `/openspec-archive` | Archive completed change |
| Implement Agent | `/implement-agent` | Build agent from skill |
| PR Author Generate | `/pr-author-generate` | Generate PR from Diff Plan |
| PR Author Template | `/pr-author-template` | Create new archetype template |
| PR Author Test | `/pr-author-test` | Test generated code locally |

See [WINDSURF_INTEGRATION.md](docs/WINDSURF_INTEGRATION.md) for setup and usage.

## Architecture

The system follows an event-driven architecture with clear separation of concerns:

### Agent Pipeline

1. **Scout Agent** scans repositories and produces Observability Diff Plans
2. **PR Author Agent** transforms Diff Plans into Pull Requests with code, tests, and docs
3. **CI Gatekeeper Agent** enforces observability standards through progressive gates
4. **Telemetry Validator Agent** confirms instrumentation works in sandbox environments
5. **Signal Factory Core** processes signals and maintains the Neptune knowledge graph
6. **RCA Copilot** provides AI-powered incident explanation and remediation

### Tech Stack

- **Runtime**: Python 3.11+ with asyncio
- **Infrastructure**: Kubernetes (EKS), Kafka (MSK), Neptune, DynamoDB, S3
- **Observability**: OpenTelemetry, OpenLineage, Prometheus
- **LLM**: AWS Bedrock (Claude)
- **VCS Integration**: GitHub, GitLab

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Implementation Roadmap

| Phase | Timeline | Focus | Milestone |
|-------|----------|-------|-----------|
| Phase 0 | Weeks 1-2 | Foundation | Scout Agent complete |
| Phase 1 | Weeks 3-4 | Code Generation | PR Author generates valid PRs |
| Phase 2 | Weeks 5-6 | CI Integration | Gate 1 enforcing on Tier-1 |
| Phase 3 | Weeks 7-8 | Validation | Validation passes for pilot repos |
| Phase 4 | Weeks 9-12 | Signal Processing | Signals flowing to Neptune |
| Phase 5 | Weeks 13-16 | RCA Copilot | MTTR < 2 minutes for Tier-1 |

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Repos with baseline telemetry | ~20% | >90% | 12 weeks |
| PR acceptance rate | N/A | >70% | 4 weeks |
| Validation accuracy | N/A | >95% | 6 weeks |
| Time to first signal (new repo) | 2-4 weeks | <1 day | 8 weeks |
| MTTR for Tier-1 incidents | >30 min | <2 min | 12 weeks |

## Documentation

- [Getting Started Guide](docs/GETTING_STARTED.md) - Comprehensive setup and usage
- [Claude Skills Reference](docs/CLAUDE_SKILLS.md) - Skill documentation and triggers
- [Windsurf Integration](docs/WINDSURF_INTEGRATION.md) - Workflow development guide
- [System Architecture](docs/ARCHITECTURE.md) - Technical architecture details
- [Design Alignment](docs/DESIGN_ALIGNMENT.md) - Mapping to design documents

## Contributing

1. Read the project context in `docs/autopilot-agent-expert/openspec/project.md`
2. Follow AI instructions in `docs/autopilot-agent-expert/openspec/AGENTS.md`
3. Use OpenSpec workflows for all changes
4. Ensure tests pass before submitting PRs

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## Support

- Documentation: This repository
- Issues: GitHub Issues
- Internal Support: #observability-support
