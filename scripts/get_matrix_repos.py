import os
import sys
import json
import requests
from datetime import datetime, timedelta

GITHUB_API = "https://api.github.com"
ORG = os.getenv("ORG_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")
DAYS_ACTIVE = int(os.getenv("BRANCH_ACTIVE_DAYS", 90))

if not TOKEN or not ORG:
    print("❌ GITHUB_TOKEN or ORG_NAME not set in environment")
    sys.exit(1)

headers = {"Authorization": f"token {TOKEN}"}
cutoff = datetime.utcnow() - timedelta(days=DAYS_ACTIVE)

def get_default_branch(repo):
    url = f"{GITHUB_API}/repos/{ORG}/{repo}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("default_branch", "main")

def get_active_branches(repo):
    branches = []
    url = f"{GITHUB_API}/repos/{ORG}/{repo}/branches?per_page=100"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    for branch in resp.json():
        name = branch["name"]
        commit_url = branch["commit"]["url"]
        commit_resp = requests.get(commit_url, headers=headers)
        commit_resp.raise_for_status()
        commit_date = commit_resp.json()["commit"]["committer"]["date"]
        dt = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        if dt >= cutoff:
            branches.append(name)
    return branches

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_matrix_repos.py <changed_repos.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        changed_repos = json.load(f)

    matrix = []

    for repo in changed_repos:
        try:
            default_branch = get_default_branch(repo)
            active = set(get_active_branches(repo))
            active.add(default_branch)
            for branch in sorted(active):
                matrix.append({"repo": repo, "branch": branch})
        except Exception as e:
            print(f"⚠️ Failed to process repo {repo}: {e}", file=sys.stderr)

    print(json.dumps(matrix, indent=2))

if __name__ == "__main__":
    main()
