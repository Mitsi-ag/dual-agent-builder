#!/usr/bin/env python3
"""
Dual-Agent Builder — Fully Automated Sprint Orchestrator

Coordinates a backend agent (Codex) and a frontend agent (Claude Code)
to build a full-stack app sprint by sprint with a shared contract layer.

Usage:
    python3 .buildrunner/run.py preflight     # Check prerequisites
    python3 .buildrunner/run.py status         # Show progress
    python3 .buildrunner/run.py sprint N       # Run sprint N
    python3 .buildrunner/run.py stage N        # Run all sprints in stage N
    python3 .buildrunner/run.py run-all        # Run all sprints 1-14
    python3 .buildrunner/run.py resume         # Resume from last completed
    python3 .buildrunner/run.py unattended     # Run all sprints, auto-approve gates
"""

import sys
import os
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime

UNATTENDED = False

RUNNER_DIR = Path(__file__).parent
REPO_DIR = RUNNER_DIR.parent
sys.path.insert(0, str(RUNNER_DIR))

from cli import run_codex, run_claude, run_command
from contracts import generate_contract_skeleton, update_contracts_after_backend
from prompts import (
    build_backend_prompt, build_frontend_prompt,
    build_design_iteration_prompt, build_review_prompt
)
from state import SprintState
from preflight import run_preflight
from config import (
    PROJECT_NAME, SPRINT_STAGES, STAGE_BOUNDARIES, SPRINT_NAMES,
    STAGE_NAMES, COMMERCIAL_GATES, SPRINT_STAGE_FILES,
    DESIGN_MAX_PASSES, INIT_PROMPT, PROTECTED_FILES,
    CIRCUIT_BREAKER_THRESHOLDS,
)


class C:
    """ANSI color codes."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'


state = SprintState(RUNNER_DIR / '.state')


def log(msg: str, color: str = ''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{C.CYAN}[{timestamp}]{C.NC} {color}{msg}{C.NC}")


def log_phase(phase: str, agent: str):
    agents = {
        'codex': f'{C.BLUE}Codex{C.NC}',
        'claude': f'{C.GREEN}Claude{C.NC}',
        'system': f'{C.CYAN}System{C.NC}',
    }
    print(f"\n{C.BOLD}{'=' * 60}{C.NC}")
    print(f"{C.BOLD}  {phase} -- {agents.get(agent, agent)}{C.NC}")
    print(f"{C.BOLD}{'=' * 60}{C.NC}\n")


def validate_protected_files():
    """Check critical files exist; restore from git if missing."""
    missing = [f for f in PROTECTED_FILES if not (REPO_DIR / f).exists()]
    if missing:
        for f in missing:
            result = run_command(["git", "checkout", "HEAD", "--", f], cwd=str(REPO_DIR))
            if result.returncode == 0:
                log(f"RESTORED protected file: {f}", C.YELLOW)
            else:
                log(f"WARNING: Could not restore {f}", C.RED)
        log(f"Restored {len(missing)} protected files", C.YELLOW)


def verify_build(phase: str) -> bool:
    log(f"Verifying build ({phase})...")
    result = run_command(["pnpm", "build"], cwd=str(REPO_DIR), timeout=120)
    if result.returncode != 0:
        log(f"Build FAILED after {phase}", C.RED)
        log(f"Error: {result.stderr[-500:]}", C.RED)
        return False
    log(f"Build passed ({phase})", C.GREEN)
    return True


def start_dev_server() -> subprocess.Popen:
    log("Starting dev server (pnpm dev)...")
    proc = subprocess.Popen(
        ["pnpm", "dev"],
        cwd=str(REPO_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    time.sleep(8)
    log("Dev server running on http://localhost:3000", C.GREEN)
    return proc


def stop_dev_server(proc: subprocess.Popen):
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=10)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        log("Dev server stopped")


def git_commit(message: str):
    log(f"Committing: {message}")
    run_command(["git", "add", "-A"], cwd=str(REPO_DIR))
    result = run_command(["git", "commit", "-m", message], cwd=str(REPO_DIR))
    if result.returncode != 0:
        log(f"Commit warning: {result.stderr[:200]}", C.YELLOW)
    else:
        log("Committed", C.GREEN)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def run_sprint(sprint_num: int):
    """Execute a single sprint: backend -> contracts -> frontend -> design -> commit."""
    stage = SPRINT_STAGES.get(sprint_num, 0)
    max_retries = CIRCUIT_BREAKER_THRESHOLDS["max_retries"]

    print(f"\n{C.BOLD}{C.CYAN}{'=' * 60}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  SPRINT {sprint_num} -- Stage {stage} -- {PROJECT_NAME}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}{'=' * 60}{C.NC}\n")

    if sprint_num == 0:
        log("Sprint 0 is VALIDATION -- no code.", C.YELLOW)
        return

    max_sprint = max(SPRINT_STAGES.keys())
    if sprint_num < 0 or sprint_num > max_sprint:
        log(f"Invalid sprint number: {sprint_num}. Must be 0-{max_sprint}.", C.RED)
        sys.exit(1)

    # Preflight
    if not run_preflight(sprint_num, REPO_DIR):
        log("Preflight failed. Fix issues above before continuing.", C.RED)
        sys.exit(1)

    ensure_dir(RUNNER_DIR / "logs")
    ensure_dir(RUNNER_DIR / "prompts")
    ensure_dir(RUNNER_DIR / "reviews")

    # Validate protected files before every sprint
    validate_protected_files()

    # Sprint 1 special: initialize project if needed
    if sprint_num == 1 and not (REPO_DIR / "package.json").exists():
        log_phase("Phase 0: Project Initialization", "codex")
        attempt = 0
        while attempt < max_retries:
            attempt += 1
            log(f"Initialization attempt {attempt}...")
            try:
                run_codex(INIT_PROMPT, cwd=str(REPO_DIR), timeout=2700)
                if (REPO_DIR / "package.json").exists():
                    log("Project initialized", C.GREEN)
                    break
            except Exception as e:
                log(f"Init failed: {e}. Retrying...", C.YELLOW)
                time.sleep(min(30, 2 ** attempt))
        else:
            log("Project initialization failed.", C.RED)
            sys.exit(1)

    # -- Phase 1: Generate Contract Skeleton --
    log_phase(f"Phase 1: Contract Skeleton (Sprint {sprint_num})", "system")
    generate_contract_skeleton(sprint_num, REPO_DIR)
    log("Contract skeleton generated", C.GREEN)

    # -- Phase 2: Backend --
    log_phase(f"Phase 2: Backend (Sprint {sprint_num})", "codex")
    backend_prompt = build_backend_prompt(sprint_num, REPO_DIR)

    prompt_file = RUNNER_DIR / "prompts" / f"sprint-{sprint_num}-backend.txt"
    prompt_file.write_text(backend_prompt)

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        log(f"Backend attempt {attempt}...")
        try:
            validate_protected_files()
            result = run_codex(backend_prompt, cwd=str(REPO_DIR), timeout=2700)

            log_file = RUNNER_DIR / "logs" / f"sprint-{sprint_num}-backend-{attempt}.log"
            log_file.write_text(result.stdout + "\n" + result.stderr)

            if verify_build("backend"):
                break
            else:
                fix_prompt = f"""The build failed after your backend changes. Fix the errors:

{result.stderr[-2000:]}

Run pnpm build again after fixing."""
                run_codex(fix_prompt, cwd=str(REPO_DIR), timeout=2700)
        except Exception as e:
            log(f"Backend error: {e}. Retrying in {min(60, 2**attempt)}s...", C.YELLOW)
            time.sleep(min(60, 2 ** attempt))
    else:
        log("Backend phase failed after all attempts.", C.RED)
        sys.exit(1)

    log("Backend complete", C.GREEN)

    # -- Phase 3: Update Contracts --
    log_phase(f"Phase 3: Contract Update (Sprint {sprint_num})", "system")
    update_contracts_after_backend(sprint_num, REPO_DIR)
    log("Contracts updated", C.GREEN)

    # -- Phase 4: Frontend --
    log_phase(f"Phase 4: Frontend (Sprint {sprint_num})", "claude")
    frontend_prompt = build_frontend_prompt(sprint_num, REPO_DIR)

    prompt_file = RUNNER_DIR / "prompts" / f"sprint-{sprint_num}-frontend.txt"
    prompt_file.write_text(frontend_prompt)

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        log(f"Frontend attempt {attempt}...")
        try:
            validate_protected_files()
            result = run_claude(frontend_prompt, cwd=str(REPO_DIR), timeout=2700)

            log_file = RUNNER_DIR / "logs" / f"sprint-{sprint_num}-frontend-{attempt}.log"
            log_file.write_text(result.stdout + "\n" + result.stderr)

            if verify_build("frontend"):
                break
            else:
                fix_prompt = f"""The build failed after your frontend changes. Fix the TypeScript errors:

{result.stderr[-2000:]}

Import types from src/contracts/api-types.ts. Run pnpm build again."""
                run_claude(fix_prompt, cwd=str(REPO_DIR), timeout=2700)
        except Exception as e:
            log(f"Frontend error: {e}. Retrying in {min(60, 2**attempt)}s...", C.YELLOW)
            time.sleep(min(60, 2 ** attempt))
    else:
        log("Frontend phase failed after all attempts.", C.RED)
        sys.exit(1)

    log("Frontend complete", C.GREEN)

    # -- Phase 5: Design Iteration --
    log_phase(f"Phase 5: Design Iteration (Sprint {sprint_num})", "claude")

    dev_server = start_dev_server()
    try:
        for iteration in range(1, DESIGN_MAX_PASSES + 1):
            log(f"Design iteration {iteration}/{DESIGN_MAX_PASSES}...")
            design_prompt = build_design_iteration_prompt(sprint_num, iteration, REPO_DIR)

            prompt_file = RUNNER_DIR / "prompts" / f"sprint-{sprint_num}-design-{iteration}.txt"
            prompt_file.write_text(design_prompt)

            try:
                result = run_claude(design_prompt, cwd=str(REPO_DIR), timeout=2700)
                log_file = RUNNER_DIR / "logs" / f"sprint-{sprint_num}-design-{iteration}.log"
                log_file.write_text(result.stdout + "\n" + result.stderr)
                log(f"Design pass {iteration}/{DESIGN_MAX_PASSES} complete", C.GREEN)
            except Exception as e:
                log(f"Design iteration {iteration} failed: {e}. Continuing...", C.YELLOW)
    finally:
        stop_dev_server(dev_server)

    # -- Phase 6: Commit --
    git_commit(
        f"Sprint {sprint_num} complete\n\n"
        f"Backend: Codex\n"
        f"Frontend: Claude Code (Opus)\n"
        f"Design: {DESIGN_MAX_PASSES}-pass Playwright iteration"
    )

    # -- Phase 7: Stage Review --
    if sprint_num in STAGE_BOUNDARIES:
        log_phase(f"Phase 7: Stage {stage} Review", "codex")
        review_prompt = build_review_prompt(sprint_num, stage, REPO_DIR)

        prompt_file = RUNNER_DIR / "prompts" / f"stage-{stage}-review.txt"
        prompt_file.write_text(review_prompt)

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            try:
                result = run_codex(review_prompt, cwd=str(REPO_DIR), timeout=2700)
                review_file = RUNNER_DIR / "reviews" / f"stage-{stage}-review.md"
                review_file.write_text(result.stdout)
                log(f"Stage {stage} review saved to {review_file}", C.GREEN)
                break
            except Exception as e:
                log(f"Review failed: {e}. Retrying...", C.YELLOW)
                time.sleep(min(60, 2 ** attempt))
        else:
            log("Stage review failed. Continuing anyway.", C.YELLOW)

        # Commercial gate
        gate_desc = COMMERCIAL_GATES.get(stage, "Unknown gate")

        print(f"\n{C.YELLOW}{C.BOLD}{'=' * 60}{C.NC}")
        print(f"{C.YELLOW}{C.BOLD}  COMMERCIAL GATE -- Stage {stage}{C.NC}")
        print(f"{C.YELLOW}{C.BOLD}  {gate_desc}{C.NC}")
        print(f"{C.YELLOW}{C.BOLD}{'=' * 60}{C.NC}\n")

        if UNATTENDED:
            log(f"UNATTENDED: Auto-approving gate for Stage {stage}.", C.YELLOW)
        else:
            response = input("Has this gate been met? [y/n]: ").strip().lower()
            if response != 'y':
                log("STOPPED. Meet the commercial gate before proceeding.", C.RED)
                state.save(sprint_num)
                sys.exit(0)

    state.save(sprint_num)
    log(f"Sprint {sprint_num} DONE", C.GREEN + C.BOLD)


def show_status():
    """Display build progress across all sprints and stages."""
    current = state.load()
    max_sprint = max(SPRINT_STAGES.keys())

    print(f"\n{C.BOLD}{C.CYAN}=== {PROJECT_NAME} Build Status ==={C.NC}\n")

    last_stage = -1
    for num in sorted(SPRINT_STAGES.keys()):
        stage_num = SPRINT_STAGES[num]
        name = SPRINT_NAMES.get(num, f"Sprint {num}")

        if stage_num != last_stage:
            stage_name = STAGE_NAMES.get(stage_num, f"Stage {stage_num}")
            print(f"  {C.BOLD}Stage {stage_num} -- {stage_name}{C.NC}")
            last_stage = stage_num

        if num <= current and current > 0:
            print(f"    {C.GREEN}[done]{C.NC} Sprint {num}: {name}")
        elif num == current + 1 or (current == 0 and num <= 1):
            print(f"    {C.YELLOW}[next]{C.NC} Sprint {num}: {name} {C.YELLOW}<-- NEXT{C.NC}")
        else:
            print(f"         Sprint {num}: {name}")

    print(f"\n  Last completed: Sprint {current}")
    next_sprint = current + 1 if current < max_sprint else None
    if next_sprint:
        print(f"  Next: {C.BOLD}python3 .buildrunner/run.py sprint {next_sprint}{C.NC}")
    else:
        print(f"  {C.GREEN}{C.BOLD}ALL SPRINTS COMPLETE{C.NC}")


def main():
    args = sys.argv[1:]
    max_sprint = max(SPRINT_STAGES.keys())

    if not args or args[0] == 'status':
        show_status()

    elif args[0] == 'preflight':
        sprint = int(args[1]) if len(args) > 1 else 1
        if run_preflight(sprint, REPO_DIR):
            print(f"\n{C.GREEN}{C.BOLD}All prerequisites met{C.NC}")
        else:
            print(f"\n{C.RED}{C.BOLD}Fix issues above{C.NC}")
            sys.exit(1)

    elif args[0] == 'sprint':
        if len(args) < 2:
            print("Usage: python3 .buildrunner/run.py sprint N")
            sys.exit(1)
        # Write PID file for monitor
        (RUNNER_DIR / ".runner-pid").write_text(str(os.getpid()))
        run_sprint(int(args[1]))

    elif args[0] == 'stage':
        if len(args) < 2:
            print("Usage: python3 .buildrunner/run.py stage N")
            sys.exit(1)
        stage_num = int(args[1])
        stage_sprints = [s for s, st in sorted(SPRINT_STAGES.items()) if st == stage_num and s > 0]
        if not stage_sprints:
            log(f"Invalid stage: {stage_num}.", C.RED)
            sys.exit(1)
        (RUNNER_DIR / ".runner-pid").write_text(str(os.getpid()))
        for s in stage_sprints:
            run_sprint(s)

    elif args[0] == 'run-all':
        (RUNNER_DIR / ".runner-pid").write_text(str(os.getpid()))
        current = state.load()
        start = current + 1 if current > 0 else 1
        for s in range(start, max_sprint + 1):
            run_sprint(s)

    elif args[0] == 'resume':
        current = state.load()
        if current >= max_sprint:
            log("All sprints complete!", C.GREEN)
        else:
            (RUNNER_DIR / ".runner-pid").write_text(str(os.getpid()))
            run_sprint(current + 1)

    elif args[0] == 'unattended':
        global UNATTENDED
        UNATTENDED = True
        (RUNNER_DIR / ".runner-pid").write_text(str(os.getpid()))
        log(f"UNATTENDED MODE: Building {PROJECT_NAME} Sprints 1-{max_sprint}.", C.YELLOW + C.BOLD)
        current = state.load()
        start = current + 1 if current > 0 else 1
        for s in range(start, max_sprint + 1):
            try:
                run_sprint(s)
            except Exception as e:
                log(f"Sprint {s} CRASHED: {e}", C.RED)
                log(f"Waiting 60s then retrying Sprint {s}...", C.YELLOW)
                time.sleep(60)
                try:
                    run_sprint(s)
                except Exception as e2:
                    log(f"Sprint {s} CRASHED AGAIN: {e2}. Skipping.", C.RED)
                    state.save(s)
                    continue
        log("ALL SPRINTS COMPLETE", C.GREEN + C.BOLD)

    else:
        print("Usage: python3 .buildrunner/run.py [preflight|status|sprint N|stage N|run-all|resume|unattended]")
        sys.exit(1)


if __name__ == '__main__':
    main()
