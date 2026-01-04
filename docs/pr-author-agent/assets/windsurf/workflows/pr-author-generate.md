# PR Author Generate Workflow

Generate a Pull Request from an Observability Diff Plan.

## Trigger

Use this workflow when:
- You have a Diff Plan JSON from Scout Agent
- You need to create instrumentation code and a PR
- You want to test PR generation without actually creating a PR

## Prerequisites

1. Valid Diff Plan JSON file
2. Repository URL or access to the target repo
3. GitHub/GitLab credentials configured (for non-dry-run)

## Steps

### Step 1: Validate Diff Plan

Read and validate the Diff Plan:

```bash
python scripts/generate_pr.py --diff-plan <path-to-diffplan.json> --dry-run
```

Check for:
- Valid JSON structure
- Required fields present
- Confidence >= threshold (0.7 default)
- At least one gap identified

### Step 2: Review Generated Artifacts

In dry-run mode, review what would be generated:

1. **Code files**: OTel interceptors, wrappers, middleware
2. **Config files**: application.yaml, dependencies
3. **Spec files**: lineage/*.yaml, contracts/*.yaml
4. **Test files**: Telemetry validation tests
5. **Docs**: RUNBOOK.md

### Step 3: Customize Templates (Optional)

If the default templates need modification:

1. Copy template to `references/templates/{lang}/{archetype}/`
2. Modify `.tmpl` files as needed
3. Re-run generation

### Step 4: Generate PR

Create the actual Pull Request:

```bash
python scripts/generate_pr.py \
  --diff-plan <path-to-diffplan.json> \
  --repo-url <github-repo-url> \
  --vcs github
```

### Step 5: Verify PR

1. Check PR was created successfully
2. Review generated files in the PR
3. Verify labels and reviewers applied
4. Confirm CI checks are running

## Output

After completing this workflow:
- PR created with instrumentation code
- All gaps from Diff Plan addressed
- RUNBOOK.md and specs included
- Ready for human review

## Example

```bash
# Dry run first
python scripts/generate_pr.py \
  --diff-plan ./orders-enricher-diffplan.json \
  --dry-run

# Create actual PR
python scripts/generate_pr.py \
  --diff-plan ./orders-enricher-diffplan.json \
  --repo-url https://github.com/company/orders-enricher \
  --output result.json
```

## Troubleshooting

### "Confidence below threshold"
- Scout Agent confidence is too low
- Lower threshold: `--confidence-threshold 0.5`
- Or review and manually address gaps

### "Template not found"
- Check template name in Diff Plan matches available templates
- Add missing template to `references/templates/`

### "GitHub API error"
- Verify GITHUB_TOKEN is set
- Check repository permissions
- Confirm branch doesn't already exist
