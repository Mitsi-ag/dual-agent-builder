#!/usr/bin/env python3
"""
Autonomous Pipeline Monitor — Covers both planning and build phases.

Designed to run as a cron job from Claude Code REPL:
    CronCreate: */5 * * * *
    Prompt: cd /path/to/project && python3 .buildrunner/monitor.py

Or called directly:
    python3 .buildrunner/monitor.py

Checks:
  1. Which pipeline phase (planning or building)?
  2. Is the runner process alive? (PID file check)
  3. Is it making progress? (file mtime on logs and state)
  4. Has it been stuck? (no log writes for N minutes)
  5. Current sprint/pass and phase from state files
  6. Git commit count
  7. Planning pass progress (X/12 passes complete)
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Thresholds
STUCK_THRESHOLD_MINUTES = 45   # Codex passes can run 45 min legitimately
WARN_THRESHOLD_MINUTES = 20    # Warning zone

RUNNER_DIR = Path(__file__).parent
REPO_DIR = RUNNER_DIR.parent

# PID files for different phases
PID_FILES = {
    "autonomous": RUNNER_DIR / ".autonomous-pid",
    "planner": RUNNER_DIR / ".planner-pid",
    "builder": RUNNER_DIR / ".runner-pid",
}

# State files
PLANNING_STATE_FILE = RUNNER_DIR / ".planning-state"
BUILD_STATE_FILE = RUNNER_DIR / ".state"
AUTONOMOUS_STATE_FILE = RUNNER_DIR / ".autonomous-state"
LOG_DIR = RUNNER_DIR / "logs"


class C:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'


def check_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_active_pid() -> tuple[int | None, str]:
    """Find which PID file is active and return (pid, phase_name)."""
    for phase, pid_file in PID_FILES.items():
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if check_pid_alive(pid):
                    return pid, phase
            except (ValueError, OSError):
                pass
    return None, "none"


def get_latest_log_mtime() -> tuple[float | None, str | None]:
    if not LOG_DIR.exists():
        return None, None
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return None, None
    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    return latest.stat().st_mtime, latest.name


def get_latest_log_tail(n_lines: int = 3) -> str:
    if not LOG_DIR.exists():
        return "(no logs)"
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return "(no logs)"
    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    try:
        lines = latest.read_text().strip().split("\n")
        return "\n".join(lines[-n_lines:])
    except Exception:
        return "(error reading log)"


def get_planning_state() -> dict:
    if PLANNING_STATE_FILE.exists():
        try:
            return json.loads(PLANNING_STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_autonomous_state() -> dict:
    if AUTONOMOUS_STATE_FILE.exists():
        try:
            return json.loads(AUTONOMOUS_STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_build_state() -> int:
    if BUILD_STATE_FILE.exists():
        content = BUILD_STATE_FILE.read_text().strip()
        if content.isdigit():
            return int(content)
    return 0


def get_git_commit_count() -> int:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=str(REPO_DIR),
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return len(result.stdout.strip().split("\n"))
    except Exception:
        pass
    return 0


def detect_phase_from_logs() -> str:
    if not LOG_DIR.exists():
        return "unknown"
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return "unknown"
    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    name = latest.stem.lower()

    if "planning" in name:
        return "Planning (Codex)"
    elif "consistency" in name:
        return "Consistency Review (Codex)"
    elif "backend" in name:
        return "Backend (Codex)"
    elif "frontend" in name:
        return "Frontend (Claude)"
    elif "design" in name:
        return "Design iteration (Claude)"
    elif "review" in name:
        return "Stage review (Codex)"
    elif "build-run" in name:
        return "Build runner"
    elif "codex" in name:
        return "Codex"
    elif "claude" in name:
        return "Claude"
    return "unknown"


def monitor() -> dict:
    now = time.time()

    pid, active_phase = get_active_pid()
    planning_state = get_planning_state()
    autonomous_state = get_autonomous_state()
    build_sprint = get_build_state()

    # Determine pipeline phase
    master_phase = autonomous_state.get("phase", "unknown")
    if master_phase in ("planning", "not_started") and planning_state:
        pipeline_phase = "PLANNING"
        completed = len(planning_state.get("completed_passes", []))
        total_passes = 12
        progress = f"{completed}/{total_passes} passes"
    elif master_phase in ("planning_complete", "building"):
        pipeline_phase = "BUILDING"
        progress = f"Sprint {build_sprint}/14"
    elif master_phase == "complete":
        pipeline_phase = "COMPLETE"
        progress = "All done"
    else:
        pipeline_phase = master_phase.upper().replace("_", " ") if master_phase != "unknown" else "UNKNOWN"
        progress = ""

    status = {
        "pipeline_phase": pipeline_phase,
        "progress": progress,
        "alive": pid is not None,
        "pid": pid,
        "active_process": active_phase,
        "current_task": detect_phase_from_logs(),
        "build_sprint": build_sprint,
        "planning_passes": len(planning_state.get("completed_passes", [])),
        "stuck": False,
        "stuck_minutes": 0,
        "commits": get_git_commit_count(),
        "last_activity": None,
        "product_name": autonomous_state.get("product_name", planning_state.get("product_name", "Unknown")),
        "status": "UNKNOWN",
    }

    # Stuck detection
    log_mtime, log_name = get_latest_log_mtime()
    if log_mtime:
        age_minutes = (now - log_mtime) / 60
        status["stuck_minutes"] = round(age_minutes, 1)
        status["last_activity"] = log_name
        if age_minutes > STUCK_THRESHOLD_MINUTES:
            status["stuck"] = True

    # Check state file mtimes too
    for sf in [PLANNING_STATE_FILE, BUILD_STATE_FILE, AUTONOMOUS_STATE_FILE]:
        if sf.exists():
            state_age = (now - sf.stat().st_mtime) / 60
            if log_mtime and sf.stat().st_mtime > log_mtime:
                status["stuck"] = False
                status["stuck_minutes"] = round(state_age, 1)

    # Overall status
    if pipeline_phase == "COMPLETE":
        status["status"] = "COMPLETE"
    elif not status["alive"] and (AUTONOMOUS_STATE_FILE.exists() or any(p.exists() for p in PID_FILES.values())):
        status["status"] = "DEAD"
    elif status["stuck"]:
        status["status"] = "STUCK"
    elif status["alive"]:
        status["status"] = "RUNNING"
    elif not any(p.exists() for p in PID_FILES.values()):
        status["status"] = "NOT STARTED"
    else:
        status["status"] = "UNKNOWN"

    return status


def print_report(status: dict):
    now_str = datetime.now().strftime("%H:%M")

    status_colors = {
        "RUNNING": C.GREEN, "COMPLETE": C.GREEN,
        "STUCK": C.RED, "DEAD": C.RED,
        "NOT STARTED": C.YELLOW, "UNKNOWN": C.YELLOW,
        "PLANNING FAILED": C.RED, "BUILD FAILED": C.RED,
    }
    sc = status_colors.get(status["status"], C.NC)

    phase_colors = {
        "PLANNING": C.BLUE, "BUILDING": C.MAGENTA,
        "COMPLETE": C.GREEN,
    }
    pc = phase_colors.get(status["pipeline_phase"], C.CYAN)

    print(f"\n{C.BOLD}{C.CYAN}{'=' * 55}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  Autonomous Pipeline Monitor [{now_str}]{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  {status['product_name']}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}{'=' * 55}{C.NC}")
    print(f"  Status:    {sc}{C.BOLD}{status['status']}{C.NC}")
    print(f"  Pipeline:  {pc}{C.BOLD}{status['pipeline_phase']}{C.NC}")
    print(f"  Progress:  {status['progress']}")
    print(f"  Task:      {status['current_task']}")
    print(f"  PID:       {status['pid'] or 'none'} ({status['active_process']})")
    print(f"  Commits:   {status['commits']}")

    if status["pipeline_phase"] == "PLANNING":
        planning = get_planning_state()
        passes = planning.get("completed_passes", [])
        if passes:
            print(f"  Last pass: {passes[-1]}")

    if status["stuck_minutes"] > 0:
        if status["stuck"]:
            print(f"  Last log:  {C.RED}{status['stuck_minutes']}m ago (STUCK){C.NC}")
        elif status["stuck_minutes"] > WARN_THRESHOLD_MINUTES:
            print(f"  Last log:  {C.YELLOW}{status['stuck_minutes']}m ago (slow){C.NC}")
        else:
            print(f"  Last log:  {status['stuck_minutes']}m ago")

    if status["last_activity"]:
        print(f"  Log file:  {status['last_activity']}")

    # Recent activity
    tail = get_latest_log_tail(3)
    if tail and tail != "(no logs)":
        print(f"\n  Recent:")
        for line in tail.split("\n"):
            print(f"    {line[:72]}")

    print(f"{C.BOLD}{C.CYAN}{'=' * 55}{C.NC}\n")

    # Actionable alerts
    if status["status"] == "DEAD":
        print(f"  {C.RED}ACTION: Pipeline died. Restart:{C.NC}")
        print(f"  {C.BOLD}nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 &{C.NC}")
    elif status["status"] == "STUCK":
        print(f"  {C.RED}ACTION: Stuck for {status['stuck_minutes']}m.{C.NC}")
        print(f"  Check: tail -50 .buildrunner/logs/")
        if status["pid"]:
            print(f"  Kill: kill {status['pid']}")
        print(f"  Restart: python3 .buildrunner/autonomous.py --resume")


def main():
    status = monitor()
    print_report(status)

    if status["status"] in ("RUNNING", "COMPLETE"):
        sys.exit(0)
    elif status["status"] == "DEAD":
        sys.exit(1)
    elif status["status"] == "STUCK":
        sys.exit(2)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
