# Instrumentation Autopilot - AI Assistant Instructions

These instructions guide AI assistants working on the Instrumentation Autopilot system using OpenSpec and Windsurf.

## System Overview

The Instrumentation Autopilot consists of six agents that work together:

1. **Scout Agent** (✅ Complete) - Detects observability gaps
2. **PR Author Agent** - Generates instrumentation PRs
3. **CI Gatekeeper Agent** - Enforces observability gates
4. **Telemetry Validator Agent** - Verifies signals in sandbox
5. **Signal Factory Core** - Processes signals, maintains graph
6. **RCA Copilot** - Explains incidents with AI

## When to Use OpenSpec

Always open this file when the request:
- Involves implementing any of the agents
- Adds new archetypes or detection patterns
- Modifies event schemas or APIs
- Changes gate policies or enforcement logic
- Updates graph schema or signal processing

## Project Structure

```
instrumentation-autopilot/
├── openspec/
│   ├── project.md           # Project context
│   ├── AGENTS.md            # This file
│   └── specs/
│       ├── scout-agent/     # Scout Agent spec
│       ├── pr-author/       # PR Author spec
│       ├── ci-gatekeeper/   # CI Gatekeeper spec
│       ├── telemetry-validator/  # Validator spec
│       ├── signal-factory/  # Signal Factory spec
│       └── rca-copilot/     # RCA Copilot spec
├── skills/
│   ├── scout-agent/         # Scout Agent skill
│   ├── pr-author-agent/     # PR Author skill
│   ├── ci-gatekeeper-agent/ # CI Gatekeeper skill
│   ├── telemetry-validator-agent/  # Validator skill
│   ├── signal-factory-core/ # Signal Factory skill
│   └── rca-copilot-agent/   # RCA Copilot skill
└── .windsurf/
    └── workflows/           # Windsurf workflows
```

## Implementation Priority

Follow this sequence when implementing:

### Priority 1: Scout Agent → PR Author Pipeline
1. Scout Agent outputs Diff Plan (✅ Complete)
2. PR Author consumes Diff Plan, generates PRs
3. Integration: Event bus handoff between agents

### Priority 2: CI Integration
4. CI Gatekeeper receives PR webhooks
5. Gatekeeper runs checks, reports status
6. Integration: GitHub/GitLab webhooks

### Priority 3: Validation Loop
7. Telemetry Validator deploys to sandbox
8. Validator queries OTel, reports evidence
9. Integration: K8s + OTel Collector

### Priority 4: Signal Processing
10. Signal Factory Router normalizes events
11. Signal Engines detect anomalies
12. Neptune graph maintains state

### Priority 5: AI-Powered RCA
13. RCA Copilot retrieves context
14. LLM generates explanations
15. Actions recommended to users

## OpenSpec Workflows for Windsurf

### Creating New Agent Features

```
/openspec-proposal Add gRPC archetype to Scout Agent
```

Creates change proposal with:
- `proposal.md` - Why and what
- `tasks.md` - Implementation checklist
- `specs/{agent}/spec.md` - Spec delta

### Implementing Agent Features

```
/openspec-apply add-grpc-archetype
```

Works through tasks, updates code, marks complete.

### Archiving Completed Features

```
/openspec-archive add-grpc-archetype
```

Merges spec delta into source specs.

## Key Implementation Guidelines

### Adding New Archetypes (Scout Agent)

1. Add detection patterns to `references/archetypes.md`
2. Add requirements to `generate_diff_plan.py`
3. Create templates in `references/gap-templates.md`
4. Update spec with new scenarios

### Creating PR Templates (PR Author)

1. Create template directory: `references/templates/{language}/{archetype}/`
2. Add code files with `${VAR}` placeholders
3. Add test templates
4. Register in template index

### Defining Gate Policies (CI Gatekeeper)

1. Define policy in `references/gate-policies.md`
2. Implement check in `scripts/check_gate.py`
3. Add to GitHub Actions workflow generator
4. Update spec with enforcement scenarios

### Adding Signal Engines (Signal Factory)

1. Create engine class in `scripts/{engine}_engine.py`
2. Define input/output schemas
3. Add Neptune graph writes
4. Add DynamoDB state updates
5. Register in router config

### Expanding RCA Capabilities (Copilot)

1. Add prompt template in `references/prompt-templates/`
2. Implement context retrieval
3. Add action catalog entries
4. Update API endpoints

## Event Schema Standards

All inter-agent events follow CloudEvents format:

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

## Testing Requirements

Before archiving any change:

1. **Unit tests** - pytest for Python, Jest for TypeScript
2. **Integration tests** - Mock external services
3. **Contract tests** - Validate event schemas
4. **Manual validation** - Run against test repo

## Common Development Tasks

### Task: Add new language support

1. Create proposal: `add-{language}-support`
2. Update Scout Agent detection patterns
3. Create PR Author templates
4. Create Validator expected signals
5. Test end-to-end

### Task: Add new observability component

1. Create proposal: `add-{component}-detection`
2. Define gap type in Scout Agent
3. Create generation template in PR Author
4. Add validation test in Validator
5. Create Signal Engine if needed

### Task: Improve RCA accuracy

1. Create proposal: `improve-rca-{area}`
2. Enhance Neptune graph queries
3. Update evidence ranking logic
4. Refine LLM prompts
5. A/B test explanations

## Troubleshooting

### Scout Agent Issues
- **Low confidence**: Check detection patterns match actual code
- **Missing archetypes**: Verify dependency patterns

### PR Author Issues
- **Template errors**: Check variable interpolation
- **Failed tests**: Review generated test code

### Gatekeeper Issues
- **False positives**: Tune check thresholds
- **Missing checks**: Verify workflow generation

### Validator Issues
- **Timeout**: Increase `timeout_seconds`
- **Missing spans**: Check OTel collector config

### Signal Factory Issues
- **Lost events**: Check event bus consumer lag
- **Graph errors**: Verify Neptune connectivity

### RCA Copilot Issues
- **Slow queries**: Check DynamoDB cache hit rate
- **Poor explanations**: Refine prompt templates
