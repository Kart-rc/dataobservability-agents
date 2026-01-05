# Windsurf Integration Guide

This guide provides comprehensive documentation for integrating Data Observability Agents with Windsurf IDE using OpenSpec-driven development workflows.

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [OpenSpec Fundamentals](#openspec-fundamentals)
4. [Available Workflows](#available-workflows)
5. [Development Patterns](#development-patterns)
6. [Agent Implementation](#agent-implementation)
7. [Template Development](#template-development)
8. [Testing Workflows](#testing-workflows)
9. [Best Practices](#best-practices)

## Overview

Windsurf integration enables AI-assisted development of Data Observability Agents through:

- **OpenSpec Workflows**: Structured change management with proposal → apply → archive flow
- **Skill Extraction**: Converting Claude Skills to Windsurf-compatible workflows
- **Spec-Driven Development**: Maintaining living specifications alongside code

### Benefits

- Consistent development process across agents
- AI-guided implementation with context
- Change tracking and archival
- Reduced context-switching between documentation and code

## Setup

### Prerequisites

- Windsurf IDE installed
- Node.js 18.x or higher
- Git repository initialized

### Installation

1. **Install OpenSpec CLI**:
   ```bash
   npm install -g @fission-ai/openspec@latest
   ```

2. **Extract skills for Windsurf**:
   ```bash
   # Extract Scout Agent skill
   unzip docs/scout/scout-agent.skill -d scout-agent-extracted

   # Create workflow directories
   mkdir -p .windsurf/workflows openspec/specs

   # Copy workflows
   cp -r scout-agent-extracted/assets/windsurf/workflows/* .windsurf/workflows/

   # Copy OpenSpec configuration
   cp -r scout-agent-extracted/assets/openspec/* openspec/
   ```

3. **Initialize OpenSpec**:
   ```bash
   openspec init
   # Select "Windsurf" integration
   # Confirm project structure
   ```

4. **Verify setup**:
   ```bash
   openspec status
   # Should show: OpenSpec initialized, Windsurf integration active
   ```

### Directory Structure After Setup

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
│   ├── project.md          # Project context
│   ├── AGENTS.md           # AI assistant instructions
│   ├── specs/
│   │   ├── scout-agent/
│   │   │   └── spec.md
│   │   ├── pr-author/
│   │   │   └── spec.md
│   │   └── ...
│   ├── changes/            # Active changes
│   │   └── {change-id}/
│   └── archive/            # Completed changes
│       └── {archived-changes}/
└── skills/
    └── {skill-name}/
        └── SKILL.md
```

## OpenSpec Fundamentals

### Core Concepts

**Project Context** (`openspec/project.md`):
Defines the system architecture, tech stack, conventions, and constraints. AI assistants read this to understand the project.

**AI Instructions** (`openspec/AGENTS.md`):
Guidelines for AI assistants working on the project, including implementation priorities and workflows.

**Specifications** (`openspec/specs/`):
Living documentation for each agent/component that evolves with the codebase.

**Changes** (`openspec/changes/`):
Active change proposals being implemented. Contains proposal, tasks, and spec deltas.

**Archive** (`openspec/archive/`):
Completed changes for reference and audit trail.

### Change Flow

```
1. Proposal   → Create change proposal with scope and tasks
2. Apply      → Implement changes, update code and specs
3. Archive    → Merge spec deltas, move to archive
```

## Available Workflows

### `/openspec-proposal` - Create Change Proposal

**Purpose**: Create a structured proposal for adding features or modifying agents.

**Usage**:
```
/openspec-proposal Add gRPC archetype to Scout Agent
```

**What it creates**:
```
openspec/changes/add-grpc-archetype/
├── proposal.md     # Why and what
├── tasks.md        # Implementation checklist
└── specs/
    └── scout-agent/
        └── spec.md # Spec delta
```

**Proposal Template**:
```markdown
# Proposal: Add gRPC Archetype to Scout Agent

## Summary
Enable Scout Agent to detect gRPC services and generate appropriate gaps.

## Motivation
Many microservices use gRPC for inter-service communication. Current Scout
Agent cannot detect gRPC patterns or recommend appropriate instrumentation.

## Scope
- Detection patterns for gRPC in Go, Java, Python
- New gap templates for gRPC OTel instrumentation
- Update archetype reference documentation

## Non-Goals
- gRPC client-side instrumentation (separate proposal)

## Tasks
See tasks.md
```

### `/openspec-apply` - Implement Change

**Purpose**: Work through a change proposal, implementing tasks and updating specs.

**Usage**:
```
/openspec-apply add-grpc-archetype
```

**Workflow**:
1. Read proposal and tasks
2. Mark tasks as in-progress
3. Implement code changes
4. Update spec delta
5. Mark tasks complete
6. Run tests

**Task States**:
- `[ ]` Pending
- `[~]` In Progress
- `[x]` Complete
- `[!]` Blocked

### `/openspec-archive` - Archive Completed Change

**Purpose**: Finalize a completed change by merging spec deltas and archiving.

**Usage**:
```
/openspec-archive add-grpc-archetype
```

**Workflow**:
1. Verify all tasks complete
2. Merge spec delta into source spec
3. Move change to archive
4. Update changelog (if applicable)

### `/implement-agent` - Build Agent from Skill

**Purpose**: Implement a new agent or add features using the skill definition.

**Usage**:
```
/implement-agent pr-author-agent
```

**Implementation Sequence**:

For **PR Author Agent**:
1. `template_engine.py` - Variable interpolation
2. `generate_pr.py` - PR generation orchestration
3. `github_client.py` - GitHub API integration
4. Templates in `references/templates/`

For **CI Gatekeeper Agent**:
1. `generate_workflow.py` - GitHub Actions generation
2. `check_gate.py` - Gate check logic
3. `report_status.py` - Status reporting

For **Telemetry Validator Agent**:
1. `validate_service.py` - Main orchestrator
2. `traffic_generator.py` - Synthetic traffic
3. `otel_client.py` - OTel querying
4. `report_generator.py` - Validation reports

For **Signal Factory Core**:
1. `signal_router.py` - Event normalization
2. `{engine}_engine.py` - Per-signal processing
3. `graph_writer.py` - Neptune operations
4. `state_manager.py` - DynamoDB operations

For **RCA Copilot Agent**:
1. `context_builder.py` - Context assembly
2. `graph_queries.py` - Neptune queries
3. `evidence_ranker.py` - Ranking logic
4. `explanation_engine.py` - LLM integration

### `/pr-author-generate` - Generate PR from Diff Plan

**Purpose**: Generate instrumentation PR from Scout Agent output.

**Usage**:
```
/pr-author-generate --diff-plan ./orders-enricher-diffplan.json --dry-run
```

**Steps**:
1. Validate Diff Plan JSON
2. Select templates based on archetypes
3. Render templates with variable substitution
4. Generate test files
5. Create RUNBOOK.md
6. (If not dry-run) Create GitHub PR

### `/pr-author-template` - Create Archetype Template

**Purpose**: Add a new archetype template to the template library.

**Usage**:
```
/pr-author-template --language go --archetype grpc-otel
```

**Steps**:
1. Create template directory: `references/templates/go/grpc-otel/`
2. Create template files with `${VAR}` placeholders
3. Add output path logic to template engine
4. Update SKILL.md template library section
5. Add test cases

### `/pr-author-test` - Test PR Author

**Purpose**: Test PR Author functionality including template rendering.

**Usage**:
```
/pr-author-test --template kafka-consumer-otel-java
```

**Steps**:
1. Run unit tests
2. Test template engine in isolation
3. Test with sample Diff Plan
4. Verify generated files
5. (Optional) Test VCS integration

## Development Patterns

### Adding New Archetypes

1. **Create proposal**:
   ```
   /openspec-proposal Add Flink archetype to Scout Agent
   ```

2. **Update Scout Agent detection** in `detect_archetype.py`:
   ```python
   FLINK_PATTERNS = {
       "java": ["flink-streaming-java", "org.apache.flink"],
       "scala": ["flink-streaming-scala"],
       "python": ["pyflink"]
   }
   ```

3. **Add gap templates** in `generate_diff_plan.py`

4. **Create PR Author templates** in `references/templates/`

5. **Add Telemetry Validator expected signals**

6. **Archive change**:
   ```
   /openspec-archive add-flink-archetype
   ```

### Adding New Observability Components

1. Define gap type in Scout Agent
2. Create generation template in PR Author
3. Add validation test in Telemetry Validator
4. Create Signal Engine if needed

### Improving RCA Accuracy

1. Enhance Neptune graph queries
2. Update evidence ranking logic
3. Refine LLM prompts
4. A/B test explanations

## Agent Implementation

### Implementation Checklist

For each agent, follow this sequence:

**Phase 1: Core Logic**
- [ ] Main orchestrator script
- [ ] Business logic modules
- [ ] External API clients

**Phase 2: Testing**
- [ ] Unit tests with mocks
- [ ] Integration tests
- [ ] Contract tests for APIs

**Phase 3: Configuration**
- [ ] Config file schema
- [ ] Environment variable docs
- [ ] Default values

**Phase 4: Documentation**
- [ ] README for agent
- [ ] API documentation
- [ ] Runbook for operations

### Example: Implementing PR Author Agent

```python
# scripts/generate_pr.py
"""
PR generation orchestrator.

Reads Diff Plan from Scout Agent and generates a PR with:
- Instrumentation code
- Configuration files
- Lineage specs
- Contract stubs
- Tests
- RUNBOOK.md
"""

import argparse
import json
from pathlib import Path

from template_engine import TemplateEngine
from github_client import GitHubClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff-plan", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="result.json")
    args = parser.parse_args()

    # Load and validate Diff Plan
    with open(args.diff_plan) as f:
        diff_plan = json.load(f)

    validate_diff_plan(diff_plan)

    # Initialize template engine
    engine = TemplateEngine(templates_path="references/templates")

    # Generate artifacts for each gap
    artifacts = []
    for gap in diff_plan["gaps"]:
        rendered = engine.render(
            template=gap["template"],
            context=build_context(diff_plan, gap)
        )
        artifacts.extend(rendered)

    if args.dry_run:
        print(json.dumps({"artifacts": artifacts}, indent=2))
        return

    # Create PR
    client = GitHubClient()
    pr = client.create_pr(
        repo_url=diff_plan["repo_url"],
        branch=f"autopilot/observability-{diff_plan['repo']}-{timestamp()}",
        artifacts=artifacts,
        title=f"Autopilot: Add observability to {diff_plan['repo']}",
        body=generate_pr_body(diff_plan, artifacts)
    )

    with open(args.output, "w") as f:
        json.dump({"pr_url": pr.url, "pr_number": pr.number}, f)

if __name__ == "__main__":
    main()
```

## Template Development

### Template Structure

```
references/templates/{language}/{archetype}/
├── {main-file}.{ext}.tmpl      # Main instrumentation code
├── {config-file}.{ext}.tmpl    # Configuration additions
├── {test-file}.{ext}.tmpl      # Test file
└── dependencies.{ext}.tmpl     # Dependency additions
```

### Variable Syntax

```
${VARIABLE_NAME}           # Simple substitution
{{#if CONDITION}}...{{/if}}  # Conditional block
{{#each COLLECTION}}...{{/each}}  # Loop block
$${ESCAPED}                # Outputs literal ${ESCAPED}
```

### Example Template

```java
// ${CLASS_NAME}OtelInterceptor.java.tmpl
package com.company.${NAMESPACE}.${MODULE_NAME}.otel;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;

/**
 * OpenTelemetry interceptor for ${SERVICE_NAME}.
 * Generated by PR Author Agent.
 *
 * @since ${TIMESTAMP}
 */
public class ${CLASS_NAME}OtelInterceptor {

    private static final String SERVICE_NAME = "${SERVICE_NAME}";
    private final Tracer tracer;

    public ${CLASS_NAME}OtelInterceptor(OpenTelemetry openTelemetry) {
        this.tracer = openTelemetry.getTracer(SERVICE_NAME, "${OTEL_VERSION}");
    }

    {{#if KAFKA_ENABLED}}
    // Kafka consumer configuration
    private static final String CONSUMER_GROUP = "${CONSUMER_GROUP}";
    private static final String INPUT_TOPIC = "${INPUT_TOPIC}";
    {{/if}}
}
```

## Testing Workflows

### Unit Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific agent tests
pytest tests/test_pr_author.py -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

### Integration Testing

```bash
# Test with mock GitHub API
pytest tests/integration/ --github-mock

# Test template rendering
python scripts/template_engine.py --test --template kafka-consumer-otel-java

# Dry-run PR generation
python scripts/generate_pr.py --diff-plan test-data/sample-diffplan.json --dry-run
```

### Validation Testing

```bash
# Test against real repository (staging)
python scripts/validate_service.py \
  --service test-service \
  --commit abc123 \
  --environment staging
```

## Best Practices

### Change Management

1. **One change per proposal**: Keep proposals focused
2. **Clear scope**: Define what is and isn't included
3. **Incremental implementation**: Complete tasks one at a time
4. **Test before archive**: Ensure all tests pass

### Template Development

1. **Use descriptive variables**: `${CONSUMER_GROUP}` not `${CG}`
2. **Include documentation**: Add comments explaining generated code
3. **Follow language idioms**: Match target language conventions
4. **Test all templates**: Render with sample context

### AI Assistant Interaction

1. **Provide context**: Reference project.md and AGENTS.md
2. **Be specific**: Name the exact agent/component
3. **Review outputs**: Verify generated code before committing
4. **Iterate**: Use follow-up prompts to refine

### Performance

1. **Cache templates**: Load once, render many
2. **Parallel processing**: Generate artifacts concurrently
3. **Minimize API calls**: Batch GitHub operations
4. **Profile bottlenecks**: Measure generation time

### Security

1. **No secrets in templates**: Use environment variables
2. **Validate inputs**: Check Diff Plan before processing
3. **Sanitize outputs**: Escape special characters
4. **Audit trail**: Log all PR creation events
