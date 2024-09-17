import os
import yaml

SRC_DIR = "/home/ubuntu/test165"


def origin_for(
    folder,
    default_repo_pattern,
):
    base = os.path.basename(folder)
    pattern = default_repo_pattern
    return pattern.format(base)


def missing_repos_config():
    missing = set()

    with open("addons.yaml") as yaml_file:
        for doc in yaml.safe_load_all(yaml_file):
            for repo in doc:
                if repo in {
                    "ENV",
                }:
                    continue
                repo_path = os.path.abspath(os.path.join(SRC_DIR, repo))

                if not os.path.exists(repo_path) or os.path.isdir(
                    os.path.join(repo_path, ".git")
                ):
                    missing.add(repo_path)

    config = {}
    for repo_path in missing:
        depth = 1
        origin_version = "origin 16.0"
        config[repo_path] = {
            "defaults": {"depth": depth},
            "merges": [origin_version],
            "remotes": {
                "origin": origin_for(repo_path, "https://github.com/OCA/{}.git")
            },
            "target": origin_version,
        }
    return config

missing_config = missing_repos_config()
if missing_config:
    with open("auto_repos.yaml", "w") as autorepos:
        yaml.dump(missing_config, autorepos)
