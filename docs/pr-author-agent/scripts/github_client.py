#!/usr/bin/env python3
"""
PR Author Agent - GitHub REST API Client
Handles branch creation, file commits, and Pull Request creation via GitHub API.
"""

import base64
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx


@dataclass
class GitHubConfig:
    """Configuration for GitHub API access."""
    app_id: str | None = None
    installation_id: str | None = None
    private_key_path: str | None = None
    access_token: str | None = None
    api_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0

    def __post_init__(self):
        # Try to load from environment if not provided
        if not self.access_token:
            self.access_token = os.environ.get("GITHUB_TOKEN")
        if not self.app_id:
            self.app_id = os.environ.get("GITHUB_APP_ID")
        if not self.installation_id:
            self.installation_id = os.environ.get("GITHUB_INSTALLATION_ID")


class GitHubClient:
    """
    GitHub API client for PR Author Agent.

    Supports:
    - Personal Access Token authentication
    - GitHub App authentication (for production)
    - Branch creation and management
    - File tree commits (efficient multi-file commits)
    - Pull Request creation with labels and reviewers
    """

    def __init__(self, config: GitHubConfig = None):
        self.config = config or GitHubConfig()
        self._client = httpx.Client(
            timeout=self.config.timeout,
            headers=self._build_headers()
        )
        self._installation_token: str | None = None
        self._token_expires: float = 0

    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        token = self._get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _get_auth_token(self) -> str | None:
        """Get the authentication token."""
        # Use personal access token if available
        if self.config.access_token:
            return self.config.access_token

        # Use GitHub App installation token
        if self._installation_token and time.time() < self._token_expires:
            return self._installation_token

        # Generate new installation token (would require JWT signing)
        # For now, fall back to PAT or None
        return None

    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse owner and repo name from URL."""
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace(".git", "")
            return owner, repo
        raise ValueError(f"Invalid repository URL: {repo_url}")

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
                if response.status_code == 403:
                    remaining = response.headers.get("X-RateLimit-Remaining", "0")
                    if remaining == "0":
                        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                        wait_time = max(reset_time - time.time(), 1)
                        print(f"Rate limited, waiting {wait_time:.0f}s...")
                        time.sleep(min(wait_time, 60))
                        continue

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"Request failed, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise

        raise RuntimeError("Max retries exceeded")

    def get_default_branch(self, repo_url: str) -> str:
        """Get the default branch name for a repository."""
        owner, repo = self._parse_repo_url(repo_url)
        response = self._request("GET", f"/repos/{owner}/{repo}")
        return response.json()["default_branch"]

    def get_branch_sha(self, repo_url: str, branch: str) -> str:
        """Get the SHA of a branch's HEAD commit."""
        owner, repo = self._parse_repo_url(repo_url)
        response = self._request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
        return response.json()["object"]["sha"]

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
            Created reference object
        """
        owner, repo = self._parse_repo_url(repo_url)

        # Get base branch SHA
        base_sha = self.get_branch_sha(repo_url, base_branch)

        # Create new reference
        response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/git/refs",
            json={
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
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
        Commit multiple files to a branch using Git tree API.

        This is more efficient than individual file commits as it
        creates a single tree with all files and a single commit.

        Args:
            repo_url: Repository URL
            branch_name: Target branch
            files: Dictionary of file_path -> content
            message: Commit message

        Returns:
            Created commit object
        """
        owner, repo = self._parse_repo_url(repo_url)

        # Get current branch HEAD
        current_sha = self.get_branch_sha(repo_url, branch_name)

        # Get current tree
        commit_response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/git/commits/{current_sha}"
        )
        base_tree_sha = commit_response.json()["tree"]["sha"]

        # Create blobs for each file
        tree_items = []
        for file_path, content in files.items():
            blob_response = self._request(
                "POST",
                f"/repos/{owner}/{repo}/git/blobs",
                json={
                    "content": base64.b64encode(content.encode()).decode(),
                    "encoding": "base64"
                }
            )
            blob_sha = blob_response.json()["sha"]

            tree_items.append({
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })

        # Create new tree
        tree_response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/git/trees",
            json={
                "base_tree": base_tree_sha,
                "tree": tree_items
            }
        )
        new_tree_sha = tree_response.json()["sha"]

        # Create commit
        commit_response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/git/commits",
            json={
                "message": message,
                "tree": new_tree_sha,
                "parents": [current_sha]
            }
        )
        new_commit_sha = commit_response.json()["sha"]

        # Update branch reference
        self._request(
            "PATCH",
            f"/repos/{owner}/{repo}/git/refs/heads/{branch_name}",
            json={"sha": new_commit_sha}
        )

        return commit_response.json()

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
        Create a Pull Request.

        Args:
            repo_url: Repository URL
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
            labels: List of label names to apply
            reviewers: List of usernames to request review from
            draft: Create as draft PR

        Returns:
            Created PR object with number and URL
        """
        owner, repo = self._parse_repo_url(repo_url)

        # Create PR
        pr_response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "draft": draft
            }
        )
        pr_data = pr_response.json()
        pr_number = pr_data["number"]

        # Add labels
        if labels:
            self._request(
                "POST",
                f"/repos/{owner}/{repo}/issues/{pr_number}/labels",
                json={"labels": labels}
            )

        # Request reviewers
        if reviewers:
            self._request(
                "POST",
                f"/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers",
                json={"reviewers": reviewers}
            )

        return {
            "number": pr_number,
            "url": pr_data["html_url"],
            "state": pr_data["state"],
            "head": head_branch,
            "base": base_branch
        }

    def get_codeowners(self, repo_url: str) -> list[str]:
        """Get reviewers from CODEOWNERS file."""
        owner, repo = self._parse_repo_url(repo_url)

        # Try common CODEOWNERS locations
        codeowners_paths = [
            "CODEOWNERS",
            ".github/CODEOWNERS",
            "docs/CODEOWNERS"
        ]

        for path in codeowners_paths:
            try:
                response = self._request(
                    "GET",
                    f"/repos/{owner}/{repo}/contents/{path}"
                )
                content = base64.b64decode(
                    response.json()["content"]
                ).decode()

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
        pr_number: int,
        body: str
    ) -> dict[str, Any]:
        """Add a comment to a PR."""
        owner, repo = self._parse_repo_url(repo_url)
        response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": body}
        )
        return response.json()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def main():
    """CLI for testing GitHub client."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub API Client")
    parser.add_argument("--repo", required=True, help="Repository URL")
    parser.add_argument("--action", choices=["info", "branch", "pr"], default="info")
    parser.add_argument("--branch", help="Branch name")
    parser.add_argument("--title", help="PR title")
    parser.add_argument("--body", help="PR body")

    args = parser.parse_args()

    client = GitHubClient()

    try:
        if args.action == "info":
            owner, repo = client._parse_repo_url(args.repo)
            print(f"Owner: {owner}")
            print(f"Repo: {repo}")
            print(f"Default branch: {client.get_default_branch(args.repo)}")

        elif args.action == "branch":
            if not args.branch:
                print("Error: --branch required")
                return
            result = client.create_branch(args.repo, args.branch)
            print(f"Created branch: {result}")

        elif args.action == "pr":
            if not all([args.branch, args.title]):
                print("Error: --branch and --title required")
                return
            result = client.create_pull_request(
                repo_url=args.repo,
                title=args.title,
                body=args.body or "",
                head_branch=args.branch
            )
            print(f"Created PR: {result}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
