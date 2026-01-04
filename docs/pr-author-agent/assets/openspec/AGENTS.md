# PR Author Agent - AI Assistant Instructions

These instructions guide AI assistants working on the PR Author Agent using OpenSpec and Windsurf.

## Agent Overview

The PR Author Agent is the second stage of the Instrumentation Autopilot pipeline:

1. **Scout Agent** (upstream) - Detects observability gaps → produces Diff Plans
2. **PR Author Agent** (this agent) - Generates PRs from Diff Plans
3. **CI Gatekeeper** (downstream) - Enforces observability gates on PRs

## When to Use OpenSpec

Always open this file when the request:
- Adds new template types or archetypes
- Modifies the Diff Plan schema
- Changes PR generation logic
- Updates VCS API integration
- Modifies variable interpolation

## Project Structure

```
pr-author-agent/
├── SKILL.md                    # Main skill definition
├── scripts/
│   ├── generate_pr.py          # Main orchestrator
│   ├── template_engine.py      # Template interpolation
│   ├── github_client.py        # GitHub API client
│   └── gitlab_client.py        # GitLab API client
├── references/
│   ├── diff-plan-schema.md     # Input schema (shared with Scout)
│   ├── pr-template.md          # PR description template
│   ├── variable-mapping.md     # Variable reference
│   └── templates/              # Code templates by language
│       ├── java/
│       ├── python/
│       ├── go/
│       └── common/
└── assets/
    ├── openspec/               # OpenSpec integration
    └── windsurf/workflows/     # Windsurf workflows
```

## Key Implementation Guidelines

### Adding New Templates

1. Create template directory: `references/templates/{language}/{archetype}/`
2. Add `.tmpl` files with `${VAR}` placeholders
3. Register template in `template_engine.py`
4. Update variable-mapping.md with new variables
5. Add unit tests for template rendering

### Modifying PR Generation

1. Update `generate_pr.py` with new logic
2. Update PR description template if needed
3. Test with sample Diff Plan
4. Verify GitHub/GitLab API calls work

### Adding New VCS Support

1. Create new client class (e.g., `bitbucket_client.py`)
2. Implement required interface methods:
   - `create_branch()`
   - `commit_files()`
   - `create_pull_request()`
3. Add configuration options
4. Update SKILL.md with new integration

## Event Schema

### Input Event (from Scout Agent)
```json
{
  "specversion": "1.0",
  "type": "autopilot.scout.diff-plan-created",
  "source": "urn:autopilot:scout-agent",
  "data": {
    "diff_plan_id": "dp-abc123",
    "repo": "orders-enricher",
    "diff_plan": { ... }
  }
}
```

### Output Event (to CI Gatekeeper)
```json
{
  "specversion": "1.0",
  "type": "autopilot.pr-author.pr-created",
  "source": "urn:autopilot:pr-author-agent",
  "data": {
    "diff_plan_id": "dp-abc123",
    "pr_number": 42,
    "pr_url": "https://github.com/..."
  }
}
```

## Testing Requirements

Before archiving any change:

1. **Unit tests** - pytest for all Python scripts
2. **Template tests** - Render each template with sample context
3. **Integration tests** - Mock VCS API calls
4. **Manual validation** - Generate PR for test repository

## Common Development Tasks

### Task: Add new language support

1. Create `references/templates/{language}/` directory
2. Create archetype subdirectories with templates
3. Add language-specific derived variables to TemplateContext
4. Test template rendering
5. Update documentation

### Task: Add new archetype template

1. Create template directory
2. Add `.tmpl` files for code, config, tests
3. Register in template index
4. Add to SKILL.md template library section
5. Test with sample Diff Plan

### Task: Improve PR description

1. Edit `references/pr-template.md`
2. Add new variables if needed
3. Update `generate_pr.py` to populate variables
4. Test PR creation

## Troubleshooting

### Template Errors
- **Variable not found**: Check variable-mapping.md for correct name
- **File not generated**: Verify template directory exists

### API Errors
- **401 Unauthorized**: Check authentication token
- **403 Forbidden**: Verify repository permissions
- **422 Unprocessable**: Check request payload format

### Generation Errors
- **Low confidence**: Scout Agent threshold not met
- **Invalid Diff Plan**: Schema validation failed
