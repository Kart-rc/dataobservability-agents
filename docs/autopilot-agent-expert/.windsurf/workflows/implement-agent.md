# Implement Agent Workflow

Implement a new agent or add features to an existing agent in the Instrumentation Autopilot system.

## Trigger

Use this workflow when:
- Implementing a new agent from the skill definition
- Adding features to an existing agent
- Connecting agents in the pipeline

## Prerequisites

1. Read `openspec/project.md` for system context
2. Read `openspec/AGENTS.md` for implementation guidelines
3. Read the specific skill SKILL.md for the agent being implemented

## Steps

### Step 1: Understand the Agent

1. Read the agent's skill definition in `skills/{agent-name}/SKILL.md`
2. Identify:
   - Core responsibilities
   - Input/output formats
   - Integration points
   - Configuration requirements

### Step 2: Create OpenSpec Change Proposal

If adding new features, create a change proposal:

```
openspec/changes/{change-id}/
├── proposal.md
├── tasks.md
└── specs/{agent}/spec.md
```

### Step 3: Implement Core Logic

For each agent, implement in this order:

**Scout Agent (✅ Complete)**
- `detect_archetype.py` - Pattern detection
- `generate_diff_plan.py` - Gap identification
- `scan_repo.py` - Orchestration

**PR Author Agent**
1. `template_engine.py` - Variable interpolation
2. `generate_pr.py` - PR generation orchestration
3. `github_client.py` - GitHub API integration
4. Templates in `references/templates/`

**CI Gatekeeper Agent**
1. `generate_workflow.py` - GitHub Actions generation
2. `check_gate.py` - Gate check logic
3. `report_status.py` - Status reporting

**Telemetry Validator Agent**
1. `validate_service.py` - Main orchestrator
2. `traffic_generator.py` - Synthetic traffic
3. `otel_client.py` - OTel querying
4. `report_generator.py` - Validation reports

**Signal Factory Core**
1. `signal_router.py` - Event normalization
2. `{engine}_engine.py` - Per-signal processing
3. `graph_writer.py` - Neptune operations
4. `state_manager.py` - DynamoDB operations

**RCA Copilot Agent**
1. `context_builder.py` - Context assembly
2. `graph_queries.py` - Neptune queries
3. `evidence_ranker.py` - Ranking logic
4. `explanation_engine.py` - LLM integration

### Step 4: Create Unit Tests

For each script, create corresponding test:
- `tests/test_{script_name}.py`
- Mock external dependencies
- Test happy path and error cases

### Step 5: Integration Testing

Test agent interactions:
1. Scout → PR Author: Diff Plan handoff
2. PR Author → Gatekeeper: PR webhook
3. Gatekeeper → Validator: Trigger validation
4. Validator → Signal Factory: Signal emission
5. Signal Factory → RCA: Incident context

### Step 6: Configuration

Create configuration files:
- `config/autopilot-config.yaml` - Main config
- `config/{agent}-config.yaml` - Agent-specific
- Environment variables documentation

### Step 7: Documentation

Update documentation:
- Agent README
- API documentation
- Runbook for operations

## Output

After completing this workflow:
1. Agent implemented with core logic
2. Unit tests passing
3. Integration points defined
4. Configuration documented

Inform the user of next steps for deployment and testing.
