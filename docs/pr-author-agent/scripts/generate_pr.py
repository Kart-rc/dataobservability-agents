#!/usr/bin/env python3
"""
PR Author Agent - Main PR Generation Orchestrator
Transforms Observability Diff Plans into Pull Requests with instrumentation code.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from template_engine import TemplateEngine, TemplateContext
from github_client import GitHubClient
from gitlab_client import GitLabClient


@dataclass
class PRAuthorConfig:
    """Configuration for PR Author Agent."""
    templates_path: str = "./references/templates"
    default_branch: str = "main"
    branch_prefix: str = "autopilot/observability"
    pr_labels: list[str] = None
    confidence_threshold: float = 0.7
    auto_create_pr: bool = True
    require_human_review: bool = True

    def __post_init__(self):
        if self.pr_labels is None:
            self.pr_labels = ["autopilot", "observability"]


@dataclass
class GeneratedArtifact:
    """Represents a generated file artifact."""
    file_path: str
    content: str
    action: str  # create, modify, merge
    template: str | None = None


class PRAuthorAgent:
    """
    PR Author Agent - Transforms Diff Plans into Pull Requests.

    This agent consumes Observability Diff Plans from the Scout Agent
    and generates complete Pull Requests with:
    - Instrumentation code (OTel interceptors, correlation headers)
    - Configuration files (application.yaml, go.mod, pom.xml)
    - Lineage specs and data contracts
    - Telemetry validation tests
    - Operational runbooks
    """

    def __init__(self, config: PRAuthorConfig = None, vcs_client: str = "github"):
        self.config = config or PRAuthorConfig()
        self.template_engine = TemplateEngine(self.config.templates_path)

        if vcs_client == "github":
            self.vcs_client = GitHubClient()
        elif vcs_client == "gitlab":
            self.vcs_client = GitLabClient()
        else:
            raise ValueError(f"Unsupported VCS client: {vcs_client}")

    def process_diff_plan(
        self,
        diff_plan: dict[str, Any],
        repo_url: str,
        dry_run: bool = False
    ) -> dict[str, Any]:
        """
        Process a Diff Plan and create a Pull Request.

        Args:
            diff_plan: Observability Diff Plan from Scout Agent
            repo_url: URL of the target repository
            dry_run: If True, generate artifacts but don't create PR

        Returns:
            Result dictionary with PR details or generated artifacts
        """
        # Step 1: Validate Diff Plan
        self._validate_diff_plan(diff_plan)

        # Step 2: Check confidence threshold
        confidence = diff_plan.get("confidence", 0)
        if confidence < self.config.confidence_threshold:
            return {
                "status": "skipped",
                "reason": f"Confidence {confidence:.2f} below threshold {self.config.confidence_threshold}",
                "diff_plan_id": diff_plan.get("diff_plan_id")
            }

        print(f"Processing Diff Plan for: {diff_plan['repo']}")
        print(f"  Archetypes: {', '.join(diff_plan['archetypes'])}")
        print(f"  Confidence: {confidence:.0%}")
        print(f"  Gaps: {len(diff_plan.get('gaps', []))}")

        # Step 3: Build template context
        context = self._build_template_context(diff_plan, repo_url)

        # Step 4: Generate artifacts
        print("\nGenerating artifacts...")
        artifacts = self._generate_artifacts(diff_plan, context)
        print(f"  Generated {len(artifacts)} files")

        # Step 5: Generate PR description
        pr_description = self._generate_pr_description(diff_plan, artifacts, context)

        if dry_run:
            return {
                "status": "dry_run",
                "diff_plan_id": diff_plan.get("diff_plan_id"),
                "artifacts": [
                    {"path": a.file_path, "action": a.action}
                    for a in artifacts
                ],
                "pr_description": pr_description
            }

        # Step 6: Create branch and PR
        if self.config.auto_create_pr:
            print("\nCreating Pull Request...")
            pr_result = self._create_pull_request(
                repo_url=repo_url,
                diff_plan=diff_plan,
                artifacts=artifacts,
                pr_description=pr_description
            )
            return pr_result

        return {
            "status": "artifacts_generated",
            "diff_plan_id": diff_plan.get("diff_plan_id"),
            "artifacts_count": len(artifacts)
        }

    def _validate_diff_plan(self, diff_plan: dict[str, Any]) -> None:
        """Validate the Diff Plan structure."""
        required_fields = ["repo", "archetypes", "confidence", "tech_stack", "gaps"]
        missing = [f for f in required_fields if f not in diff_plan]

        if missing:
            raise ValueError(f"Invalid Diff Plan: missing fields {missing}")

        if not diff_plan["archetypes"]:
            raise ValueError("Diff Plan has no archetypes detected")

    def _build_template_context(
        self,
        diff_plan: dict[str, Any],
        repo_url: str
    ) -> TemplateContext:
        """Build the context for template interpolation."""
        repo_name = diff_plan["repo"]
        tech_stack = diff_plan.get("tech_stack", {})

        # Extract topics from gaps (if Kafka archetype)
        input_topic = ""
        output_topic = ""
        for gap in diff_plan.get("gaps", []):
            if "kafka" in gap.get("template", "").lower():
                # Would extract from actual code analysis
                input_topic = f"{repo_name}_input"
                output_topic = f"{repo_name}_output"
                break

        return TemplateContext(
            service_name=repo_name,
            service_urn=f"urn:svc:prod:{repo_name}",
            namespace=repo_name.split("-")[0] if "-" in repo_name else "default",
            input_topic=input_topic,
            output_topic=output_topic,
            owner_team=self._get_owner_team(repo_url),
            consumer_group=f"{repo_name}-cg",
            schema_id=f"{repo_name}.v1",
            otel_version=self._get_otel_version(tech_stack.get("language", "java")),
            timestamp=datetime.now(timezone.utc).isoformat(),
            diff_plan_id=diff_plan.get("diff_plan_id", f"dp-{repo_name}"),
            confidence=diff_plan["confidence"],
            archetypes=diff_plan["archetypes"],
            language=tech_stack.get("language", "java")
        )

    def _get_owner_team(self, repo_url: str) -> str:
        """Extract owner team from repository (via CODEOWNERS or default)."""
        # In real implementation, would fetch CODEOWNERS from repo
        return "platform-team"

    def _get_otel_version(self, language: str) -> str:
        """Get the recommended OTel SDK version for a language."""
        versions = {
            "java": "1.32.0",
            "python": "1.22.0",
            "go": "1.24.0"
        }
        return versions.get(language, "1.32.0")

    def _generate_artifacts(
        self,
        diff_plan: dict[str, Any],
        context: TemplateContext
    ) -> list[GeneratedArtifact]:
        """Generate all artifacts based on the Diff Plan."""
        artifacts = []

        # Process each gap
        for gap in diff_plan.get("gaps", []):
            template_name = gap.get("template", "")
            if not template_name:
                continue

            try:
                # Render template
                rendered_files = self.template_engine.render_template(
                    template_name=template_name,
                    context=context
                )

                for file_path, content in rendered_files.items():
                    artifacts.append(GeneratedArtifact(
                        file_path=file_path,
                        content=content,
                        action="create",
                        template=template_name
                    ))

            except Exception as e:
                print(f"  Warning: Failed to render template {template_name}: {e}")

        # Process patch plan
        for patch in diff_plan.get("patch_plan", []):
            artifacts.append(GeneratedArtifact(
                file_path=patch["file"],
                content=patch.get("content", ""),
                action=patch["action"]
            ))

        # Always generate runbook if missing
        if not any(a.file_path == "RUNBOOK.md" for a in artifacts):
            runbook_content = self.template_engine.render_runbook(context)
            artifacts.append(GeneratedArtifact(
                file_path="RUNBOOK.md",
                content=runbook_content,
                action="create",
                template="runbook"
            ))

        # Generate lineage spec if missing
        if "missing_lineage_spec" in [g["type"] for g in diff_plan.get("gaps", [])]:
            lineage_content = self.template_engine.render_lineage_spec(context)
            artifacts.append(GeneratedArtifact(
                file_path=f"lineage/{context.service_name}.yaml",
                content=lineage_content,
                action="create",
                template="lineage-spec"
            ))

        # Generate data contract if missing
        if "missing_contract" in [g["type"] for g in diff_plan.get("gaps", [])]:
            contract_content = self.template_engine.render_contract_stub(context)
            artifacts.append(GeneratedArtifact(
                file_path=f"contracts/{context.service_name}.yaml",
                content=contract_content,
                action="create",
                template="contract-stub"
            ))

        # Generate telemetry validation tests
        # Tests are generated for any instrumentation gap (missing_otel, missing_correlation)
        instrumentation_gaps = [g for g in diff_plan.get("gaps", [])
                                if g["type"] in ("missing_otel", "missing_correlation")]
        if instrumentation_gaps:
            test_content = self.template_engine.render_telemetry_test(context)
            test_path = self._get_test_path(context)
            artifacts.append(GeneratedArtifact(
                file_path=test_path,
                content=test_content,
                action="create",
                template="telemetry-test"
            ))

        return artifacts

    def _get_test_path(self, context: TemplateContext) -> str:
        """Determine the test file path based on language."""
        lang = context.language
        service_name = context.service_name

        test_paths = {
            "java": f"src/test/java/com/company/{service_name.replace('-', '/')}/otel/{context.service_name.replace('-', '').title()}OtelInterceptorTest.java",
            "python": f"tests/test_otel_{service_name.replace('-', '_')}.py",
            "go": f"internal/observability/otel_test.go"
        }
        return test_paths.get(lang, f"tests/test_telemetry.{lang}")

    def _generate_pr_description(
        self,
        diff_plan: dict[str, Any],
        artifacts: list[GeneratedArtifact],
        context: TemplateContext
    ) -> str:
        """Generate the PR description from template."""
        changes_list = "\n".join([
            f"- `{a.file_path}` ({a.action})"
            for a in artifacts
        ])

        gaps_list = "\n".join([
            f"- [{gap['priority']}] {gap['type']}: {gap['description']}"
            for gap in diff_plan.get("gaps", [])
        ])

        files_list = "\n".join([
            f"| `{a.file_path}` | {a.action} | {a.template or 'patch'} |"
            for a in artifacts
        ])

        return f"""## Autopilot: Observability Instrumentation

This PR was generated by the Instrumentation Autopilot to add observability
instrumentation to this repository based on Scout Agent analysis.

### Summary
- **Archetypes Detected**: {', '.join(context.archetypes)}
- **Confidence Score**: {context.confidence:.0%}
- **Diff Plan ID**: {context.diff_plan_id}

### Changes
{changes_list}

### Gaps Addressed
{gaps_list}

### Files Modified
| File | Action | Template |
|------|--------|----------|
{files_list}

### Verification Checklist
- [ ] Code review approved by domain expert
- [ ] Unit tests passing
- [ ] Lineage spec reviewed for accuracy
- [ ] Contract SLOs appropriate for data tier
- [ ] RUNBOOK.md reviewed for operational accuracy

### Next Steps
After merge, the **Telemetry Validator** will automatically verify signals in staging.
Gate 1 checks will run as part of this PR's CI pipeline.

### Need Help?
- [Observability Runbook](./RUNBOOK.md)
- [Instrumentation Autopilot Docs](https://docs.internal/autopilot)
- Contact: #observability-support

---
*Generated by Instrumentation Autopilot v1.0*
*Scout Agent Scan: {diff_plan.get('scan_timestamp', 'N/A')}*
*PR Author: {context.timestamp}*
"""

    def _create_pull_request(
        self,
        repo_url: str,
        diff_plan: dict[str, Any],
        artifacts: list[GeneratedArtifact],
        pr_description: str
    ) -> dict[str, Any]:
        """Create the Pull Request via VCS API."""
        repo_name = diff_plan["repo"]
        timestamp = int(datetime.now().timestamp())
        branch_name = f"{self.config.branch_prefix}-{repo_name}-{timestamp}"

        # Create branch
        print(f"  Creating branch: {branch_name}")
        self.vcs_client.create_branch(
            repo_url=repo_url,
            branch_name=branch_name,
            base_branch=self.config.default_branch
        )

        # Commit files
        files_to_commit = {
            a.file_path: a.content
            for a in artifacts
        }
        print(f"  Committing {len(files_to_commit)} files...")

        commit_message = f"""feat(observability): Add instrumentation via Autopilot

Addresses gaps detected by Scout Agent:
{chr(10).join(f'- {g["type"]}' for g in diff_plan.get('gaps', []))}

Diff Plan ID: {diff_plan.get('diff_plan_id', 'N/A')}
Confidence: {diff_plan['confidence']:.0%}
"""

        self.vcs_client.commit_files(
            repo_url=repo_url,
            branch_name=branch_name,
            files=files_to_commit,
            message=commit_message
        )

        # Create PR
        archetypes_labels = [f"archetype:{a}" for a in diff_plan["archetypes"][:2]]
        pr_labels = self.config.pr_labels + archetypes_labels

        pr_title = f"feat(observability): Add {', '.join(diff_plan['archetypes'][:2])} instrumentation"

        print(f"  Creating PR: {pr_title}")
        pr_result = self.vcs_client.create_pull_request(
            repo_url=repo_url,
            title=pr_title,
            body=pr_description,
            head_branch=branch_name,
            base_branch=self.config.default_branch,
            labels=pr_labels
        )

        print(f"  PR created: {pr_result.get('url', 'N/A')}")

        return {
            "status": "success",
            "diff_plan_id": diff_plan.get("diff_plan_id"),
            "pr_number": pr_result.get("number"),
            "pr_url": pr_result.get("url"),
            "branch": branch_name,
            "files_changed": len(artifacts),
            "archetypes": diff_plan["archetypes"],
            "gaps_addressed": [g["type"] for g in diff_plan.get("gaps", [])]
        }


def print_result(result: dict[str, Any]) -> None:
    """Print a human-readable summary of the result."""
    print("\n" + "=" * 60)
    print("PR AUTHOR AGENT RESULT")
    print("=" * 60)

    status = result.get("status", "unknown")
    print(f"\nStatus: {status.upper()}")

    if status == "success":
        print(f"PR URL: {result.get('pr_url')}")
        print(f"PR Number: #{result.get('pr_number')}")
        print(f"Branch: {result.get('branch')}")
        print(f"Files Changed: {result.get('files_changed')}")
        print(f"Archetypes: {', '.join(result.get('archetypes', []))}")
        print(f"Gaps Addressed: {', '.join(result.get('gaps_addressed', []))}")
    elif status == "dry_run":
        print(f"Diff Plan ID: {result.get('diff_plan_id')}")
        print(f"\nArtifacts that would be created:")
        for artifact in result.get("artifacts", []):
            print(f"  - {artifact['path']} ({artifact['action']})")
    elif status == "skipped":
        print(f"Reason: {result.get('reason')}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="PR Author Agent - Generate PRs from Observability Diff Plans"
    )
    parser.add_argument(
        "--diff-plan",
        "-d",
        required=True,
        help="Path to Diff Plan JSON file"
    )
    parser.add_argument(
        "--repo-url",
        "-r",
        help="Repository URL (defaults to URL in diff plan)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate artifacts without creating PR"
    )
    parser.add_argument(
        "--vcs",
        choices=["github", "gitlab"],
        default="github",
        help="Version control system to use"
    )
    parser.add_argument(
        "--templates-path",
        default="./references/templates",
        help="Path to template library"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for result JSON"
    )

    args = parser.parse_args()

    try:
        # Load Diff Plan
        diff_plan_path = Path(args.diff_plan)
        if not diff_plan_path.exists():
            raise ValueError(f"Diff Plan not found: {diff_plan_path}")

        with open(diff_plan_path) as f:
            diff_plan = json.load(f)

        # Get repo URL
        repo_url = args.repo_url or diff_plan.get("repo_url")
        if not repo_url:
            raise ValueError("Repository URL required (--repo-url or in diff plan)")

        # Create agent
        config = PRAuthorConfig(templates_path=args.templates_path)
        agent = PRAuthorAgent(config=config, vcs_client=args.vcs)

        # Process Diff Plan
        result = agent.process_diff_plan(
            diff_plan=diff_plan,
            repo_url=repo_url,
            dry_run=args.dry_run
        )

        # Output result
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(result, indent=2))
            print(f"Result written to: {output_path}")

        print_result(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
