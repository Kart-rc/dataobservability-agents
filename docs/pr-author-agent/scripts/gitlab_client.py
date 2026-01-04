#!/usr/bin/env python3
"""
PR Author Agent - GitLab REST API Client
Handles branch creation, file commits, and Merge Request creation via GitLab API.
"""

import base64
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlparse

import httpx


@dataclass
class GitLabConfig:
    """Configuration for GitLab API access."""
    access_token: str | None = None
    api_url: str = "https://gitlab.com/api/v4"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0

    def __post_init__(self):
        # Try to load from environment if not provided
        if not self.access_token:
            self.access_token = os.environ.get("GITLAB_TOKEN")
        if not self.api_url:
            self.api_url = os.environ.get(
                "GITLAB_API_URL",
                "https://gitlab.com/api/v4"
            )


class GitLabClient:
    """
    GitLab API client for PR Author Agent.

    Supports:
    - Personal Access Token authentication
    - Project token authentication
    - Branch creation and management
    - Multi-file commits
    - Merge Request creation with labels and reviewers
    """

    def __init__(self, config: GitLabConfig = None):
        self.config = config or GitLabConfig()
        self._client = httpx.Client(
            timeout=self.config.timeout,
            headers=self._build_headers()
        )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.config.access_token:
            headers["PRIVATE-TOKEN"] = self.config.access_token
        return headers

    def _parse_repo_url(self, repo_url: str) -> str:
        """Parse project path from URL and return URL-encoded project ID."""
        parsed = urlparse(repo_url)
        path = parsed.path.strip("/").replace(".git", "")
        # GitLab uses URL-encoded project path as ID
        return quote(path, safe="")

    def _get_project_id(self, repo_url: str) -> int:
        """Get the numeric project ID from URL."""
        project_path = self._parse_repo_url(repo_url)
        response = self._request("GET", f"/projects/{project_path}")
        return response.json()["id"]

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an API request with retry logic."""
        url = f"{self.config.api_url}{endpoint}"

        for attempt in range(self.config.max_retries):
            try:
                response = self._client.request(method, url, **kwargs)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    print(f"Rate limited, waiting {retry_after}s...")
                    time.sleep(min(retry_after, 60))
                    continue

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"Request failed ({e.response.status_code}), retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise

        raise RuntimeError("Max retries exceeded")

    def get_default_branch(self, repo_url: str) -> str:
        """Get the default branch name for a project."""
        project_path = self._parse_repo_url(repo_url)
        response = self._request("GET", f"/projects/{project_path}")
        return response.json()["default_branch"]

    def get_branch_sha(self, repo_url: str, branch: str) -> str:
        """Get the SHA of a branch's HEAD commit."""
        project_path = self._parse_repo_url(repo_url)
        response = self._request(
            "GET",
            f"/projects/{project_path}/repository/branches/{quote(branch, safe='')}"
        )
        return response.json()["commit"]["id"]

    def create_branch(
        self,
        repo_url: str,
        branch_name: str,
        base_branch: str = "main"
    ) -> dict[str, Any]:
        """
        Create a new branch from the base branch.

        Args:
            repo_url: Repository URL
            branch_name: Name for the new branch
            base_branch: Branch to base off (default: main)

        Returns:
            Created branch object
        """
        project_path = self._parse_repo_url(repo_url)

        response = self._request(
            "POST",
            f"/projects/{project_path}/repository/branches",
            json={
                "branch": branch_name,
                "ref": base_branch
            }
        )
        return response.json()

    def commit_files(
        self,
        repo_url: str,
        branch_name: str,
        files: dict[str, str],
        message: str
    ) -> dict[str, Any]:
        """
        Commit multiple files to a branch using Commits API.

        GitLab's commits API supports multiple file actions in a single request.

        Args:
            repo_url: Repository URL
            branch_name: Target branch
            files: Dictionary of file_path -> content
            message: Commit message

        Returns:
            Created commit object
        """
        project_path = self._parse_repo_url(repo_url)

        # Build actions array for multi-file commit
        actions = []
        for file_path, content in files.items():
            # Check if file exists to determine create vs update
            try:
                self._request(
                    "GET",
                    f"/projects/{project_path}/repository/files/{quote(file_path, safe='')}",
                    params={"ref": branch_name}
                )
                action = "update"
            except httpx.HTTPStatusError:
                action = "create"

            actions.append({
                "action": action,
                "file_path": file_path,
                "content": content
            })

        response = self._request(
            "POST",
            f"/projects/{project_path}/repository/commits",
            json={
                "branch": branch_name,
                "commit_message": message,
                "actions": actions
            }
        )
        return response.json()

    def create_pull_request(
        self,
        repo_url: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        labels: list[str] = None,
        reviewers: list[str] = None,
        draft: bool = False
    ) -> dict[str, Any]:
        """
        Create a Merge Request.

        Args:
            repo_url: Repository URL
            title: MR title
            body: MR description
            head_branch: Source branch
            base_branch: Target branch
            labels: List of label names to apply
            reviewers: List of usernames to request review from
            draft: Create as draft MR

        Returns:
            Created MR object with number (iid) and URL
        """
        project_path = self._parse_repo_url(repo_url)

        # Resolve reviewer usernames to IDs if provided
        reviewer_ids = []
        if reviewers:
            for username in reviewers:
                try:
                    user_response = self._request(
                        "GET",
                        f"/users",
                        params={"username": username}
                    )
                    users = user_response.json()
                    if users:
                        reviewer_ids.append(users[0]["id"])
                except httpx.HTTPStatusError:
                    pass

        # Create MR
        mr_data = {
            "source_branch": head_branch,
            "target_branch": base_branch,
            "title": f"Draft: {title}" if draft else title,
            "description": body,
            "remove_source_branch": True
        }

        if labels:
            mr_data["labels"] = ",".join(labels)

        if reviewer_ids:
            mr_data["reviewer_ids"] = reviewer_ids

        mr_response = self._request(
            "POST",
            f"/projects/{project_path}/merge_requests",
            json=mr_data
        )
        mr_json = mr_response.json()

        return {
            "number": mr_json["iid"],
            "url": mr_json["web_url"],
            "state": mr_json["state"],
            "head": head_branch,
            "base": base_branch
        }

    def get_codeowners(self, repo_url: str) -> list[str]:
        """Get reviewers from CODEOWNERS file."""
        project_path = self._parse_repo_url(repo_url)

        # Try common CODEOWNERS locations
        codeowners_paths = [
            "CODEOWNERS",
            ".gitlab/CODEOWNERS",
            "docs/CODEOWNERS"
        ]

        for path in codeowners_paths:
            try:
                response = self._request(
                    "GET",
                    f"/projects/{project_path}/repository/files/{quote(path, safe='')}/raw",
                    params={"ref": "main"}
                )
                content = response.text

                # Parse CODEOWNERS (simplified)
                owners = []
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split()
                        for part in parts[1:]:  # Skip path pattern
                            if part.startswith("@"):
                                owners.append(part.lstrip("@"))
                return owners

            except httpx.HTTPStatusError:
                continue

        return []

    def add_comment(
        self,
        repo_url: str,
        mr_iid: int,
        body: str
    ) -> dict[str, Any]:
        """Add a note (comment) to a Merge Request."""
        project_path = self._parse_repo_url(repo_url)
        response = self._request(
            "POST",
            f"/projects/{project_path}/merge_requests/{mr_iid}/notes",
            json={"body": body}
        )
        return response.json()

    def get_pipeline_status(
        self,
        repo_url: str,
        mr_iid: int
    ) -> dict[str, Any]:
        """Get the pipeline status for a Merge Request."""
        project_path = self._parse_repo_url(repo_url)
        response = self._request(
            "GET",
            f"/projects/{project_path}/merge_requests/{mr_iid}/pipelines"
        )
        pipelines = response.json()
        if pipelines:
            return pipelines[0]  # Return most recent pipeline
        return {"status": "unknown"}

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def main():
    """CLI for testing GitLab client."""
    import argparse

    parser = argparse.ArgumentParser(description="GitLab API Client")
    parser.add_argument("--repo", required=True, help="Repository URL")
    parser.add_argument("--action", choices=["info", "branch", "mr"], default="info")
    parser.add_argument("--branch", help="Branch name")
    parser.add_argument("--title", help="MR title")
    parser.add_argument("--body", help="MR body")

    args = parser.parse_args()

    client = GitLabClient()

    try:
        if args.action == "info":
            project_path = client._parse_repo_url(args.repo)
            print(f"Project path: {project_path}")
            print(f"Default branch: {client.get_default_branch(args.repo)}")

        elif args.action == "branch":
            if not args.branch:
                print("Error: --branch required")
                return
            result = client.create_branch(args.repo, args.branch)
            print(f"Created branch: {result}")

        elif args.action == "mr":
            if not all([args.branch, args.title]):
                print("Error: --branch and --title required")
                return
            result = client.create_pull_request(
                repo_url=args.repo,
                title=args.title,
                body=args.body or "",
                head_branch=args.branch
            )
            print(f"Created MR: {result}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
