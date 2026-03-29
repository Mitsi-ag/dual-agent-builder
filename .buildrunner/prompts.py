"""
Prompt builders for backend, frontend, design iteration, and review phases.

KEY DESIGN: Prompts tell agents to READ files from disk rather than
embedding entire multi-thousand-line documents in the prompt.
Only contracts (small, critical for coordination) are embedded inline.

All prompt templates are defined in config.py and interpolated here.
"""

from pathlib import Path
from config import (
    PROJECT_NAME, SPRINT_STAGE_FILES, SPRINT_PAGES,
    DESIGN_ITERATION_FOCUSES, DESIGN_MAX_PASSES,
    BACKEND_PROMPT_TEMPLATE, FRONTEND_PROMPT_TEMPLATE,
    DESIGN_REVIEW_TEMPLATE, STAGE_REVIEW_TEMPLATE,
)


def _read_file(repo_dir: Path, relative_path: str) -> str:
    """Read a file from the repo, return empty string if not found."""
    f = repo_dir / relative_path
    if f.exists():
        try:
            return f.read_text()
        except Exception:
            return ""
    return ""


def build_backend_prompt(sprint_num: int, repo_dir: Path) -> str:
    """Build prompt for the backend agent."""
    contracts = _read_file(repo_dir, "src/contracts/api-types.ts")
    routes = _read_file(repo_dir, "src/contracts/api-routes.ts")
    constants = _read_file(repo_dir, "src/contracts/constants.ts")
    stage_file = SPRINT_STAGE_FILES[sprint_num]

    return BACKEND_PROMPT_TEMPLATE.format(
        project_name=PROJECT_NAME,
        sprint_num=sprint_num,
        stage_file=stage_file,
        contracts=contracts,
        routes=routes,
        constants=constants,
    )


def build_frontend_prompt(sprint_num: int, repo_dir: Path) -> str:
    """Build prompt for the frontend agent."""
    contracts = _read_file(repo_dir, "src/contracts/api-types.ts")
    routes = _read_file(repo_dir, "src/contracts/api-routes.ts")
    constants = _read_file(repo_dir, "src/contracts/constants.ts")
    stage_file = SPRINT_STAGE_FILES[sprint_num]

    return FRONTEND_PROMPT_TEMPLATE.format(
        project_name=PROJECT_NAME,
        sprint_num=sprint_num,
        stage_file=stage_file,
        contracts=contracts,
        routes=routes,
        constants=constants,
    )


def build_design_iteration_prompt(
    sprint_num: int, iteration: int, repo_dir: Path
) -> str:
    """Build prompt for design iteration with Playwright."""
    pages = SPRINT_PAGES.get(sprint_num, [])
    pages_str = (
        "\n".join(f"- http://localhost:3000{p}" for p in pages)
        if pages
        else "- http://localhost:3000 (check all accessible pages)"
    )
    focus = DESIGN_ITERATION_FOCUSES.get(iteration, "General quality check")

    if iteration <= 3:
        detail_level = "broad -- check overall layout"
    elif iteration <= 7:
        detail_level = "specific -- catch details"
    else:
        detail_level = "extremely critical -- final polish"

    return DESIGN_REVIEW_TEMPLATE.format(
        project_name=PROJECT_NAME,
        sprint_num=sprint_num,
        iteration=iteration,
        max_passes=DESIGN_MAX_PASSES,
        pages=pages_str,
        focus=focus,
        detail_level=detail_level,
    )


def build_review_prompt(sprint_num: int, stage: int, repo_dir: Path) -> str:
    """Build prompt for stage review."""
    stage_file = SPRINT_STAGE_FILES[sprint_num]

    return STAGE_REVIEW_TEMPLATE.format(
        project_name=PROJECT_NAME,
        stage=stage,
        stage_file=stage_file,
    )
