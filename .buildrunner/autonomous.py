#!/usr/bin/env python3
"""
Fully Autonomous Pipeline — Plan + Build with zero human intervention.

Phase 1: Codex researches and writes all planning docs (6-9 hours)
Phase 2: Codex builds backend, Claude builds frontend per sprint (4-8 hours)
Phase 3: Done. Git log shows everything.

Usage:
    # From scratch with seed research
    python3 .buildrunner/autonomous.py \
        --name "ShieldAU" \
        --desc "Essential Eight compliance for Australian SMBs" \
        --seed ideas/shieldau/BUILD-PROMPT.md

    # From scratch, no seed
    python3 .buildrunner/autonomous.py \
        --name "MyProduct" \
        --desc "AI-powered whatever for whoever"

    # Resume (auto-detects which phase)
    python3 .buildrunner/autonomous.py --resume

    # Skip planning (docs already written)
    python3 .buildrunner/autonomous.py --build-only

    # Planning only (don't build yet)
    python3 .buildrunner/autonomous.py --plan-only \
        --name "ShieldAU" \
        --desc "Essential Eight compliance for AU SMBs"
"""

import sys
import os
import json
import time
import argparse
import signal
import subprocess
from pathlib import Path
from datetime import datetime

RUNNER_DIR = Path(__file__).parent
REPO_DIR = RUNNER_DIR.parent
sys.path.insert(0, str(RUNNER_DIR))

from planner import run_planner, load_state as load_planning_state
from cli import run_command


class C:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'


MASTER_STATE_FILE = RUNNER_DIR / '.autonomous-state'


def log(msg: str, color: str = ''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{C.CYAN}[{timestamp}]{C.NC} {color}{msg}{C.NC}")


def load_master_state() -> dict:
    if MASTER_STATE_FILE.exists():
        try:
            return json.loads(MASTER_STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"phase": "not_started", "product_name": "", "product_desc": ""}


def save_master_state(state: dict):
    MASTER_STATE_FILE.write_text(json.dumps(state, indent=2))


def run_build_phase(project_dir: Path) -> bool:
    """Launch the build runner in unattended mode."""
    log("Starting build phase (Codex backend + Claude frontend)...", C.MAGENTA)

    run_py = project_dir / ".buildrunner" / "run.py"
    if not run_py.exists():
        log(f"ERROR: {run_py} not found", C.RED)
        return False

    log_dir = project_dir / ".buildrunner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    run_log = log_dir / "build-run.log"

    try:
        # Run build synchronously so we can track status
        with open(run_log, 'w') as lf:
            proc = subprocess.Popen(
                [sys.executable, str(run_py), "unattended"],
                cwd=str(project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Write PID for monitor
            (project_dir / ".buildrunner" / ".runner-pid").write_text(str(proc.pid))

            for line in iter(proc.stdout.readline, ''):
                if line:
                    lf.write(line)
                    lf.flush()
                    sys.stdout.write(line)
                    sys.stdout.flush()

            proc.wait()

            if proc.returncode == 0:
                log("Build phase COMPLETE", C.GREEN + C.BOLD)
                return True
            else:
                log(f"Build phase FAILED (exit code {proc.returncode})", C.RED)
                return False

    except KeyboardInterrupt:
        log("Build interrupted. Resume with: python3 .buildrunner/autonomous.py --resume", C.YELLOW)
        return False
    except Exception as e:
        log(f"Build phase error: {e}", C.RED)
        return False


def init_project(project_dir: Path):
    """Initialize git and basic structure if needed."""
    if not (project_dir / ".git").exists():
        log("Initializing git repository...", C.CYAN)
        run_command(["git", "init"], cwd=str(project_dir))
        run_command(["git", "add", "-A"], cwd=str(project_dir))
        run_command(["git", "commit", "-m", "Initial commit: autonomous builder setup"],
                    cwd=str(project_dir))


def main():
    parser = argparse.ArgumentParser(
        description="Fully Autonomous Pipeline: Plan + Build"
    )
    parser.add_argument("--name", type=str, help="Product name")
    parser.add_argument("--desc", type=str, help="Product description")
    parser.add_argument("--seed", type=str, help="Path to seed research (BUILD-PROMPT.md)")
    parser.add_argument("--project-dir", type=str, help="Project directory (default: parent of .buildrunner)")
    parser.add_argument("--resume", action="store_true", help="Resume from where we left off")
    parser.add_argument("--plan-only", action="store_true", help="Only run planning phase")
    parser.add_argument("--build-only", action="store_true", help="Skip planning, start building")
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else REPO_DIR

    # Banner
    print(f"\n{C.BOLD}{C.MAGENTA}{'=' * 60}{C.NC}")
    print(f"{C.BOLD}{C.MAGENTA}  AUTONOMOUS PIPELINE{C.NC}")
    print(f"{C.BOLD}{C.MAGENTA}  Phase 1: Research + Planning (Codex, ~6-9 hours){C.NC}")
    print(f"{C.BOLD}{C.MAGENTA}  Phase 2: Build (Codex backend + Claude frontend, ~4-8 hours){C.NC}")
    print(f"{C.BOLD}{C.MAGENTA}{'=' * 60}{C.NC}\n")

    # Load/create state
    state = load_master_state()

    if args.resume:
        if state["phase"] == "not_started":
            log("No previous state found. Start fresh with --name and --desc.", C.RED)
            sys.exit(1)
        product_name = state["product_name"]
        product_desc = state["product_desc"]
        log(f"Resuming: {product_name} (phase: {state['phase']})", C.YELLOW)
    elif args.build_only:
        product_name = state.get("product_name", args.name or "Unknown")
        product_desc = state.get("product_desc", args.desc or "")
        state["phase"] = "building"
    else:
        if not args.name or not args.desc:
            print("Usage: python3 .buildrunner/autonomous.py --name 'Name' --desc 'Description'")
            print("       python3 .buildrunner/autonomous.py --resume")
            print("       python3 .buildrunner/autonomous.py --build-only")
            sys.exit(1)
        product_name = args.name
        product_desc = args.desc
        state = {
            "phase": "planning",
            "product_name": product_name,
            "product_desc": product_desc,
            "started_at": datetime.now().isoformat(),
        }

    save_master_state(state)
    init_project(project_dir)

    # Write master PID
    (project_dir / ".buildrunner" / ".autonomous-pid").write_text(str(os.getpid()))

    # ── Phase 1: Planning ──
    if state["phase"] in ("not_started", "planning"):
        state["phase"] = "planning"
        save_master_state(state)

        log(f"PHASE 1: Planning {product_name}...", C.BLUE + C.BOLD)
        planning_ok = run_planner(
            product_name=product_name,
            product_desc=product_desc,
            project_dir=project_dir,
            seed_path=args.seed or "",
            resume=args.resume,
        )

        if not planning_ok:
            log("Planning failed. Fix issues and run: python3 .buildrunner/autonomous.py --resume", C.RED)
            state["phase"] = "planning_failed"
            save_master_state(state)
            sys.exit(1)

        state["phase"] = "planning_complete"
        state["planning_completed_at"] = datetime.now().isoformat()
        save_master_state(state)

        run_command(["git", "add", "-A"], cwd=str(project_dir))
        run_command(
            ["git", "commit", "-m", f"Planning complete for {product_name}"],
            cwd=str(project_dir),
        )

        if args.plan_only:
            log(f"Planning complete. Build when ready: python3 .buildrunner/autonomous.py --build-only", C.GREEN)
            sys.exit(0)

    # ── Phase 2: Build ──
    if state["phase"] in ("planning_complete", "building"):
        state["phase"] = "building"
        state["build_started_at"] = datetime.now().isoformat()
        save_master_state(state)

        log(f"PHASE 2: Building {product_name}...", C.MAGENTA + C.BOLD)
        build_ok = run_build_phase(project_dir)

        if build_ok:
            state["phase"] = "complete"
            state["completed_at"] = datetime.now().isoformat()
            save_master_state(state)

            print(f"\n{C.BOLD}{C.GREEN}{'=' * 60}{C.NC}")
            print(f"{C.BOLD}{C.GREEN}  {product_name} — FULLY BUILT{C.NC}")
            print(f"{C.BOLD}{C.GREEN}  Started: {state.get('started_at', 'unknown')}{C.NC}")
            print(f"{C.BOLD}{C.GREEN}  Finished: {state['completed_at']}{C.NC}")
            print(f"{C.BOLD}{C.GREEN}{'=' * 60}{C.NC}\n")
        else:
            state["phase"] = "build_failed"
            save_master_state(state)
            log("Build failed. Resume with: python3 .buildrunner/autonomous.py --resume", C.RED)
            sys.exit(1)

    # Clean up PID
    pid_file = project_dir / ".buildrunner" / ".autonomous-pid"
    if pid_file.exists():
        pid_file.unlink()


if __name__ == "__main__":
    main()
