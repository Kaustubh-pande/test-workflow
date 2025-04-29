import sys
import yaml
import json

def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"⚠️ File not found: {path}")
        return {}
    except Exception as e:
        print(f"❌ Failed to load YAML from {path}: {e}")
        sys.exit(1)

def normalize_list(lst):
    if not lst:
        return []
    return sorted(set(str(i) for i in lst))

def list_changed(old_list, new_list):
    return normalize_list(old_list) != normalize_list(new_list)

def repo_access_changed(old_repo, new_repo):
    for key in ['reviewers', 'approvers']:
        old_list = old_repo.get(key, [])
        new_list = new_repo.get(key, [])
        if list_changed(old_list, new_list):
            return True
    return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python get_changed_repos.py <old_yaml> <new_yaml>")
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]

    old_data = load_yaml(old_path)
    new_data = load_yaml(new_path)

    old_admins = old_data.get('admins', [])
    new_admins = new_data.get('admins', [])

    old_repos = old_data.get('repos', {})
    new_repos = new_data.get('repos', {})

    # ✅ If admins changed, update all repos
    if list_changed(old_admins, new_admins):
        print(json.dumps(sorted(new_repos.keys())))
        return

    # ✅ Compare per-repo access changes
    changed_repos = []
    all_repo_names = set(old_repos.keys()).union(new_repos.keys())

    for repo in sorted(all_repo_names):
        old_repo = old_repos.get(repo, {})
        new_repo = new_repos.get(repo, {})
        if repo_access_changed(old_repo, new_repo):
            changed_repos.append(repo)

    print(json.dumps(changed_repos))

if __name__ == "__main__":
    main()
