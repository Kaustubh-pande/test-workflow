import yaml

def validate_access_control_yaml():
    with open('config/access-control.yaml') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Root must be a dictionary.")

    # Validate admins
    admins = data.get('admins')
    if admins is None or not isinstance(admins, list):
        raise ValueError("'admins' key must exist and be a list.")
    for admin in admins:
        if not isinstance(admin, str):
            raise ValueError("Each admin must be a string.")

    # Validate repos
    repos = data.get('repos')
    if repos is None or not isinstance(repos, dict):
        raise ValueError("'repos' key must exist and be a dictionary.")

    for repo_name, info in repos.items():
        if not isinstance(info, dict):
            raise ValueError(f"Repo '{repo_name}' value must be a dictionary.")

        # reviewers and approvers can be missing or null — treat as empty lists
        for field in ['reviewers', 'approvers']:
            field_value = info.get(field)
            if field_value is None:
                continue  # missing key is OK (means empty)
            if not isinstance(field_value, list):
                raise ValueError(f"'{field}' in repo '{repo_name}' must be a list if present.")
            for user in field_value:
                if not isinstance(user, str):
                    raise ValueError(f"All entries in '{field}' in repo '{repo_name}' must be strings.")

    print("✅ access-control.yaml validation successful!")

if __name__ == "__main__":
    validate_access_control_yaml()
