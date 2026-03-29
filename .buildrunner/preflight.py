"""
Prerequisites checker for the build runner.

Validates CLI tools, project documentation, and environment
variables are present before running a sprint.
"""

import shutil
from pathlib import Path
from config import ENV_REQUIREMENTS, REQUIRED_DOCS

C_GREEN = '\033[0;32m'
C_RED = '\033[0;31m'
C_YELLOW = '\033[1;33m'
C_NC = '\033[0m'


def run_preflight(sprint_num: int, repo_dir: Path) -> bool:
    """Check all prerequisites for a given sprint.

    Returns True if all checks pass, False if any critical check fails.
    """
    errors = 0

    # -- CLI Tools --
    print("\n  CLI Tools:")
    for cmd in ["claude", "codex", "pnpm", "node"]:
        if shutil.which(cmd):
            print(f"    {C_GREEN}[ok]{C_NC} {cmd}")
        else:
            print(f"    {C_RED}[missing]{C_NC} {cmd} -- NOT FOUND in PATH")
            errors += 1

    # -- Project Documentation --
    print("\n  Project Docs:")
    for f in REQUIRED_DOCS:
        path = repo_dir / f
        if path.exists():
            print(f"    {C_GREEN}[ok]{C_NC} {f}")
        else:
            print(f"    {C_RED}[missing]{C_NC} {f}")
            errors += 1

    # -- Environment Variables --
    print("\n  Environment Variables:")
    env_file = repo_dir / ".env.local"

    if not env_file.exists():
        print(f"    {C_RED}[missing]{C_NC} .env.local -- FILE NOT FOUND")
        print(f"      Run: cp .env.example .env.local && fill in values")
        errors += 1
    else:
        env_content = env_file.read_text()

        required_vars: set[str] = set()
        for s, var_list in ENV_REQUIREMENTS.items():
            if s <= sprint_num:
                required_vars.update(var_list)

        for var in sorted(required_vars):
            found = False
            for line in env_content.splitlines():
                stripped = line.strip()
                if stripped.startswith("#") or not stripped:
                    continue
                if stripped.startswith(f"{var}="):
                    value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                    if len(value) > 0:
                        found = True
                    break
            if found:
                print(f"    {C_GREEN}[ok]{C_NC} {var}")
            else:
                print(f"    {C_RED}[missing]{C_NC} {var} -- MISSING or EMPTY in .env.local")
                errors += 1

        # Show deferred vars
        for s, var_list in sorted(ENV_REQUIREMENTS.items()):
            if s > sprint_num:
                for var in var_list:
                    print(f"    {C_YELLOW}[deferred]{C_NC} {var} -- not needed until Sprint {s}")

    # -- Sprint-specific checks --
    print("\n  Sprint-specific:")

    if sprint_num >= 2:
        pkg = repo_dir / "package.json"
        if pkg.exists():
            print(f"    {C_GREEN}[ok]{C_NC} package.json exists")
        else:
            print(f"    {C_RED}[missing]{C_NC} package.json -- run Sprint 1 first")
            errors += 1

    if sprint_num >= 2:
        contracts = repo_dir / "src" / "contracts" / "api-types.ts"
        if contracts.exists():
            print(f"    {C_GREEN}[ok]{C_NC} src/contracts/api-types.ts exists")
        else:
            print(f"    {C_YELLOW}[info]{C_NC} src/contracts/api-types.ts -- will be generated")

    git_dir = repo_dir / ".git"
    if git_dir.exists():
        print(f"    {C_GREEN}[ok]{C_NC} Git repository initialized")
    else:
        print(f"    {C_YELLOW}[info]{C_NC} Not a git repo -- commits will be skipped")

    return errors == 0
