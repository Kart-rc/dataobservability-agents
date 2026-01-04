# PR Author Agent - OpenSpec Project

## Purpose

The PR Author Agent transforms Observability Diff Plans (produced by Scout Agent) into complete Pull Requests containing instrumentation code, configuration, tests, and documentation.

## System Architecture

```
Scout Agent → [Diff Plan] → PR Author Agent → [Pull Request] → CI Gatekeeper
                                    ↓
                           Template Library
```

## Tech Stack

### Agent Runtime
- **Language**: Python 3.11+
- **Async**: asyncio for concurrent operations
- **HTTP**: httpx for API clients
- **Templates**: Jinja2-style interpolation

### Integration Points
- **GitHub**: REST API v3 for PR creation
- **GitLab**: REST API v4 for MR creation
- **Event Bus**: Kafka (CloudEvents format)
- **Schema Registry**: REST API for validation

## Agent Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Diff Plan Parsing | Validate and extract gaps from Scout Agent output |
| Template Selection | Choose templates based on archetype and language |
| Code Generation | Render templates with variable interpolation |
| PR Creation | Create branches, commits, and PRs via VCS API |
| Event Emission | Publish CloudEvents for downstream agents |

## Code Style

- Python: PEP 8, Black formatting, type hints required
- Templates: `${VAR}` syntax for interpolation
- YAML: 2-space indentation

## Architecture Patterns

- **Stateless Design**: No local state; all state from Diff Plan
- **Template-Driven**: All code generation via templates
- **Human-in-the-Loop**: PRs require human review
- **Idempotent**: Safe to retry with same Diff Plan

## Performance Requirements

| Operation | Target |
|-----------|--------|
| PR Generation | < 30 seconds |
| Template Rendering | < 1 second per file |
| GitHub API Calls | < 10 seconds per PR |

## Security Requirements

- No credentials in generated code
- Use GitHub App authentication (not PATs) in production
- Secrets from environment variables or Secrets Manager
- Least-privilege repository access
