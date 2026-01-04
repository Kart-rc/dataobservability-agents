# PR Author Test Workflow

Test PR Author Agent functionality including template rendering and PR generation.

## Trigger

Use this workflow when:
- Verifying template changes work correctly
- Testing PR generation before deploying
- Debugging template or API issues

## Prerequisites

1. PR Author Agent scripts available
2. Sample Diff Plan for testing
3. (Optional) GitHub/GitLab test repository

## Steps

### Step 1: Run Unit Tests

Execute the test suite:

```bash
cd docs/pr-author-agent
pytest tests/ -v
```

Expected test coverage:
- Template rendering
- Variable interpolation
- Diff Plan validation
- API client mocking

### Step 2: Test Template Engine

Test the template engine in isolation:

```bash
python scripts/template_engine.py --test
```

This runs built-in template tests for:
- RUNBOOK.md generation
- Lineage spec generation
- Contract stub generation

### Step 3: Test with Sample Diff Plan

Create a sample Diff Plan:

```json
{
  "repo": "test-service",
  "repo_url": "https://github.com/test/test-service",
  "diff_plan_id": "dp-test123",
  "scan_timestamp": "2026-01-04T10:00:00Z",
  "archetypes": ["kafka-microservice"],
  "confidence": 0.85,
  "tech_stack": {
    "language": "java",
    "build_system": "maven",
    "framework": "spring-boot-3.2"
  },
  "current_observability": {
    "otel_sdk": false,
    "correlation_propagation": false,
    "lineage_spec": false,
    "contract_stub": false,
    "runbook": false
  },
  "gaps": [
    {
      "type": "missing_otel",
      "location": "src/main/java/com/test/Consumer.java",
      "description": "Missing OTel instrumentation",
      "priority": "P0",
      "template": "kafka-consumer-otel-java"
    }
  ],
  "patch_plan": []
}
```

Run dry-run generation:

```bash
python scripts/generate_pr.py \
  --diff-plan sample-diffplan.json \
  --dry-run \
  --output result.json
```

### Step 4: Verify Generated Files

Check the dry-run output:

1. **Correct file paths**: Files in expected directories
2. **Variable substitution**: No unresolved `${VAR}` in output
3. **Valid syntax**: Generated code compiles/parses
4. **Complete coverage**: All gaps have generated files

### Step 5: Test VCS Integration (Optional)

Test against a real repository in dry-run:

```bash
python scripts/generate_pr.py \
  --diff-plan sample-diffplan.json \
  --repo-url https://github.com/your-org/test-repo \
  --dry-run
```

Verify:
- Repository URL parsed correctly
- Branch name generated properly
- PR description complete

### Step 6: Test PR Creation (Integration)

For full integration testing with a test repository:

```bash
export GITHUB_TOKEN="your-test-token"

python scripts/generate_pr.py \
  --diff-plan sample-diffplan.json \
  --repo-url https://github.com/your-org/test-repo \
  --output result.json
```

Verify:
- Branch created
- Files committed
- PR created with correct title/description
- Labels applied

### Step 7: Cleanup

After integration testing:
- Close test PRs
- Delete test branches
- Review API rate limit usage

## Test Checklist

| Test | Command | Pass Criteria |
|------|---------|---------------|
| Unit tests | `pytest tests/` | All tests pass |
| Template engine | `python template_engine.py --test` | No errors |
| Dry run | `python generate_pr.py --dry-run` | Valid output |
| API mock | `pytest tests/test_github_client.py` | Mocked calls pass |

## Troubleshooting

### Template rendering fails
- Check template file exists in correct path
- Verify all required variables in context
- Check for syntax errors in template

### Variable not substituted
- Variable name must be in UPPER_SNAKE_CASE
- Variable must be in TemplateContext
- Check for typos in `${VAR_NAME}`

### API tests fail
- Mock may be outdated if API changed
- Check httpx version compatibility
- Verify mock response format

## Output

After completing this workflow:
- All unit tests passing
- Template rendering verified
- Dry-run generation working
- (Optional) Integration test successful
