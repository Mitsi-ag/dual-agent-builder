#!/usr/bin/env python3
"""
Autonomous Planning Orchestrator — Research + Documentation via Codex

Runs 12 sequential passes of Codex, each up to 45-60 minutes,
building cumulative planning documentation from market research
through final quality gate.

Usage:
    python3 .buildrunner/planner.py --name "ShieldAU" --desc "Essential Eight compliance for AU SMBs"
    python3 .buildrunner/planner.py --seed ideas/shieldau/BUILD-PROMPT.md
    python3 .buildrunner/planner.py --resume   # Resume from last completed pass
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

RUNNER_DIR = Path(__file__).parent
REPO_DIR = RUNNER_DIR.parent
sys.path.insert(0, str(RUNNER_DIR))

from cli import run_codex, run_command
from planning_prompts import PLANNING_PASSES


class C:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'


STATE_FILE = RUNNER_DIR / '.planning-state'
MAX_RETRIES = 3


def log(msg: str, color: str = ''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{C.CYAN}[{timestamp}]{C.NC} {color}{msg}{C.NC}")


def log_phase(pass_num: int, name: str, total: int):
    print(f"\n{C.BOLD}{C.BLUE}{'=' * 60}{C.NC}")
    print(f"{C.BOLD}{C.BLUE}  PLANNING PASS {pass_num}/{total}: {name}{C.NC}")
    print(f"{C.BOLD}{C.BLUE}  Agent: Codex (full-auto, ~45 min){C.NC}")
    print(f"{C.BOLD}{C.BLUE}{'=' * 60}{C.NC}\n")


def load_state() -> dict:
    """Load planning progress state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"completed_passes": [], "product_name": "", "product_desc": "", "started_at": None}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def read_seed(seed_path: str) -> str:
    """Read seed research (BUILD-PROMPT.md or similar)."""
    p = Path(seed_path)
    if p.exists():
        return p.read_text()
    # Try relative to repo
    p = REPO_DIR / seed_path
    if p.exists():
        return p.read_text()
    return ""


def ensure_dirs(project_dir: Path):
    """Create all needed directories."""
    (project_dir / "docs" / "research").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "sprints").mkdir(parents=True, exist_ok=True)
    (project_dir / ".buildrunner" / "logs").mkdir(parents=True, exist_ok=True)
    (project_dir / ".buildrunner" / "prompts").mkdir(parents=True, exist_ok=True)


def run_planning_pass(
    pass_config: dict,
    pass_num: int,
    total: int,
    product_name: str,
    product_desc: str,
    seed_content: str,
    project_dir: Path,
) -> bool:
    """Run a single planning pass with Codex. Returns True on success."""
    log_phase(pass_num, pass_config["name"], total)

    seed_section = ""
    if seed_content and pass_num <= 2:
        seed_section = f"## Seed Research (from preliminary analysis)\n\n{seed_content[:8000]}"

    prompt = pass_config["prompt"].format(
        product_name=product_name,
        product_description=product_desc,
        seed_section=seed_section,
    )

    # Save prompt for debugging
    prompt_file = project_dir / ".buildrunner" / "prompts" / f"planning-{pass_num:02d}-{pass_config['name'].lower().replace(' ', '-')}.txt"
    prompt_file.write_text(prompt)

    timeout = pass_config.get("timeout", 2700)

    for attempt in range(1, MAX_RETRIES + 1):
        log(f"Attempt {attempt}/{MAX_RETRIES}...")
        try:
            result = run_codex(
                prompt,
                cwd=str(project_dir),
                timeout=timeout,
            )

            # Save log
            log_file = project_dir / ".buildrunner" / "logs" / f"planning-{pass_num:02d}-attempt-{attempt}.log"
            log_file.write_text(result.stdout + "\n" + result.stderr)

            # Check if expected output files exist
            all_exist = True
            for expected in pass_config["output_files"]:
                if not (project_dir / expected).exists():
                    log(f"Expected output missing: {expected}", C.YELLOW)
                    all_exist = False

            if all_exist:
                log(f"Pass {pass_num} complete: {pass_config['name']}", C.GREEN)
                return True
            elif attempt < MAX_RETRIES:
                log(f"Some outputs missing. Retrying...", C.YELLOW)
                time.sleep(10)
            else:
                log(f"Outputs still missing after {MAX_RETRIES} attempts.", C.RED)
                # Non-critical passes can continue
                if not pass_config.get("critical", True):
                    log("Non-critical pass. Continuing.", C.YELLOW)
                    return True
                return False

        except Exception as e:
            log(f"Pass failed: {e}", C.RED)
            if attempt < MAX_RETRIES:
                wait = min(60, 2 ** attempt * 10)
                log(f"Retrying in {wait}s...", C.YELLOW)
                time.sleep(wait)
            else:
                if not pass_config.get("critical", True):
                    log("Non-critical pass. Continuing.", C.YELLOW)
                    return True
                return False

    return False


def run_codex_review(project_dir: Path, product_name: str, product_desc: str) -> bool:
    """Run Codex for a quick consistency review after all passes."""
    log("Running Codex final consistency check...", C.BLUE)
    prompt = f"""You are reviewing planning docs for {product_name} — {product_desc}.

Read every file in docs/ and PRODUCT.md, DECISIONS.md, CLAUDE.md, .buildrunner/config.py.

Check:
1. Every API endpoint in ARCHITECTURE.md has a corresponding sprint task
2. Every sprint task is specific enough for an AI to execute
3. config.py SPRINT_CONTRACTS cover all types
4. No contradictions between documents

Fix any issues you find directly in the files. Write a brief summary of changes to docs/research/CONSISTENCY-CHECK.md.
"""
    try:
        result = run_codex(prompt, cwd=str(project_dir), timeout=2700)
        log_file = project_dir / ".buildrunner" / "logs" / "planning-consistency-check.log"
        log_file.write_text(result.stdout + "\n" + result.stderr)
        log("Consistency check complete", C.GREEN)
        return True
    except Exception as e:
        log(f"Consistency check failed: {e}", C.YELLOW)
        return False


def run_planner(
    product_name: str,
    product_desc: str,
    project_dir: Path,
    seed_path: str = "",
    resume: bool = False,
):
    """Run the full planning pipeline."""
    print(f"\n{C.BOLD}{C.CYAN}{'=' * 60}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  AUTONOMOUS PLANNER — {product_name}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  {len(PLANNING_PASSES)} passes via Codex (est. 6-9 hours){C.NC}")
    print(f"{C.BOLD}{C.CYAN}{'=' * 60}{C.NC}\n")

    ensure_dirs(project_dir)

    # Load or create state
    state = load_state()
    if resume and state["completed_passes"]:
        log(f"Resuming from pass {len(state['completed_passes']) + 1}", C.YELLOW)
    else:
        state = {
            "completed_passes": [],
            "product_name": product_name,
            "product_desc": product_desc,
            "started_at": datetime.now().isoformat(),
        }
        save_state(state)

    # Read seed research
    seed_content = read_seed(seed_path) if seed_path else ""
    if seed_content:
        log(f"Loaded seed research: {len(seed_content)} chars", C.GREEN)

    # Write PID file for monitor
    (project_dir / ".buildrunner" / ".planner-pid").write_text(str(os.getpid()))

    total = len(PLANNING_PASSES)
    failed_critical = False

    for i, pass_config in enumerate(PLANNING_PASSES):
        pass_num = i + 1
        pass_name = pass_config["name"]

        # Skip completed passes
        if pass_name in state["completed_passes"]:
            log(f"Skipping completed pass {pass_num}: {pass_name}", C.YELLOW)
            continue

        start_time = time.time()
        success = run_planning_pass(
            pass_config, pass_num, total,
            product_name, product_desc,
            seed_content, project_dir,
        )
        elapsed = (time.time() - start_time) / 60

        if success:
            state["completed_passes"].append(pass_name)
            state[f"pass_{pass_num}_elapsed_min"] = round(elapsed, 1)
            save_state(state)
            log(f"Pass {pass_num}/{total} done in {elapsed:.1f}min", C.GREEN)

            # Git commit after each pass
            run_command(["git", "add", "-A"], cwd=str(project_dir))
            run_command(
                ["git", "commit", "-m", f"Planning pass {pass_num}: {pass_name}"],
                cwd=str(project_dir),
            )
        else:
            if pass_config.get("critical", True):
                log(f"CRITICAL pass {pass_num} failed: {pass_name}", C.RED)
                failed_critical = True
                break
            else:
                log(f"Non-critical pass {pass_num} failed. Continuing.", C.YELLOW)

    # Final Codex consistency review
    if not failed_critical:
        run_codex_review(project_dir, product_name, product_desc)
        run_command(["git", "add", "-A"], cwd=str(project_dir))
        run_command(
            ["git", "commit", "-m", "Planning complete: final consistency review"],
            cwd=str(project_dir),
        )

    # Summary
    elapsed_total = sum(
        state.get(f"pass_{i}_elapsed_min", 0) for i in range(1, total + 1)
    )

    print(f"\n{C.BOLD}{'=' * 60}{C.NC}")
    if failed_critical:
        print(f"{C.RED}{C.BOLD}  PLANNING INCOMPLETE — Critical pass failed{C.NC}")
        print(f"  Completed: {len(state['completed_passes'])}/{total} passes")
        print(f"  Resume: python3 .buildrunner/planner.py --resume")
    else:
        state["planning_complete"] = True
        state["completed_at"] = datetime.now().isoformat()
        save_state(state)
        print(f"{C.GREEN}{C.BOLD}  PLANNING COMPLETE — {product_name}{C.NC}")
        print(f"  Passes: {len(state['completed_passes'])}/{total}")
        print(f"  Total time: {elapsed_total:.0f} minutes")
        print(f"  Ready for: python3 .buildrunner/run.py unattended")
    print(f"{C.BOLD}{'=' * 60}{C.NC}\n")

    # Clean up PID
    pid_file = project_dir / ".buildrunner" / ".planner-pid"
    if pid_file.exists():
        pid_file.unlink()

    return not failed_critical


def main():
    parser = argparse.ArgumentParser(description="Autonomous Planning Orchestrator")
    parser.add_argument("--name", type=str, help="Product name")
    parser.add_argument("--desc", type=str, help="Product description")
    parser.add_argument("--seed", type=str, help="Path to seed research (BUILD-PROMPT.md)")
    parser.add_argument("--project-dir", type=str, help="Project directory (default: current)")
    parser.add_argument("--resume", action="store_true", help="Resume from last completed pass")
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else REPO_DIR

    if args.resume:
        state = load_state()
        if not state.get("product_name"):
            print("No previous planning state found. Start fresh with --name and --desc.")
            sys.exit(1)
        product_name = state["product_name"]
        product_desc = state["product_desc"]
        seed_path = args.seed or ""
    else:
        if not args.name or not args.desc:
            print("Usage: python3 .buildrunner/planner.py --name 'Name' --desc 'Description'")
            print("   or: python3 .buildrunner/planner.py --seed path/to/BUILD-PROMPT.md --name 'Name' --desc 'Description'")
            sys.exit(1)
        product_name = args.name
        product_desc = args.desc
        seed_path = args.seed or ""

    success = run_planner(
        product_name=product_name,
        product_desc=product_desc,
        project_dir=project_dir,
        seed_path=seed_path,
        resume=args.resume,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
