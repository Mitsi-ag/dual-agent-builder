#!/usr/bin/env python3
"""
Build Runner Monitor — Health checker with file-mtime stuck detection.

Designed to run as a cron job from Claude Code REPL:
    CronCreate: */5 * * * *
    Prompt: cd /path/to/project && python3 .buildrunner/monitor.py

Or called directly:
    python3 .buildrunner/monitor.py

Checks:
  1. Is the runner process alive? (PID file check)
  2. Is it making progress? (file mtime on logs and state)
  3. Has it been stuck? (no log writes for N minutes)
  4. Current sprint and phase from state file
  5. Git commit count since runner started

Outputs a structured status report suitable for Claude Code cron monitoring.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Thresholds
STUCK_THRESHOLD_MINUTES = 30   # No log writes for this long = stuck
WARN_THRESHOLD_MINUTES = 15    # Warning zone

RUNNER_DIR = Path(__file__).parent
REPO_DIR = RUNNER_DIR.parent
PID_FILE = RUNNER_DIR / ".runner-pid"
STATE_FILE = RUNNER_DIR / ".state"
LOG_DIR = RUNNER_DIR / "logs"


class C:
    """ANSI color codes."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'


def check_pid_alive(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_latest_log_mtime() -> tuple[float | None, str | None]:
    """Find the most recently modified log file and return its mtime."""
    if not LOG_DIR.exists():
        return None, None

    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return None, None

    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    return latest.stat().st_mtime, latest.name


def get_latest_log_tail(n_lines: int = 3) -> str:
    """Get the last N lines from the most recent log file."""
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


def get_state() -> int:
    """Read the current sprint state."""
    if STATE_FILE.exists():
        content = STATE_FILE.read_text().strip()
        if content.isdigit():
            return int(content)
    return 0


def get_git_commit_count() -> int:
    """Count git commits (sprint commits)."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=str(REPO_DIR),
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return len(result.stdout.strip().split("\n"))
    except Exception:
        pass
    return 0


def detect_phase_from_logs() -> str:
    """Try to detect current phase from recent log filenames."""
    if not LOG_DIR.exists():
        return "unknown"

    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return "unknown"

    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    name = latest.stem.lower()

    if "backend" in name:
        return "Backend (Codex)"
    elif "frontend" in name:
        return "Frontend (Claude)"
    elif "design" in name:
        return "Design iteration"
    elif "review" in name:
        return "Stage review"
    elif "codex" in name:
        return "Codex"
    elif "claude" in name:
        return "Claude"
    return "unknown"


def monitor() -> dict:
    """Run all health checks and return structured status."""
    now = time.time()
    status = {
        "alive": False,
        "pid": None,
        "sprint": get_state(),
        "phase": "unknown",
        "stuck": False,
        "stuck_minutes": 0,
        "commits": get_git_commit_count(),
        "last_activity": None,
        "status": "UNKNOWN",
    }

    # Check PID
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            status["pid"] = pid
            status["alive"] = check_pid_alive(pid)
        except (ValueError, OSError):
            pass

    # Check log mtime for stuck detection
    log_mtime, log_name = get_latest_log_mtime()
    if log_mtime:
        age_minutes = (now - log_mtime) / 60
        status["stuck_minutes"] = round(age_minutes, 1)
        status["last_activity"] = log_name

        if age_minutes > STUCK_THRESHOLD_MINUTES:
            status["stuck"] = True
        elif age_minutes > WARN_THRESHOLD_MINUTES:
            status["stuck"] = False  # warning but not stuck yet

    # Also check state file mtime
    if STATE_FILE.exists():
        state_age = (now - STATE_FILE.stat().st_mtime) / 60
        # If state file is newer than logs, something just completed
        if log_mtime and STATE_FILE.stat().st_mtime > log_mtime:
            status["stuck"] = False
            status["stuck_minutes"] = round(state_age, 1)

    # Detect phase
    status["phase"] = detect_phase_from_logs()

    # Determine overall status
    if not status["alive"] and status["pid"]:
        status["status"] = "DEAD"
    elif status["stuck"]:
        status["status"] = "STUCK"
    elif status["alive"]:
        status["status"] = "RUNNING"
    elif status["sprint"] >= 14:
        status["status"] = "COMPLETE"
    elif not status["pid"]:
        status["status"] = "NOT STARTED"
    else:
        status["status"] = "UNKNOWN"

    return status


def print_report(status: dict):
    """Print a formatted status report."""
    now_str = datetime.now().strftime("%H:%M")
    total_sprints = 14

    # Status color
    status_colors = {
        "RUNNING": C.GREEN,
        "COMPLETE": C.GREEN,
        "STUCK": C.RED,
        "DEAD": C.RED,
        "NOT STARTED": C.YELLOW,
        "UNKNOWN": C.YELLOW,
    }
    sc = status_colors.get(status["status"], C.NC)

    print(f"\n{C.BOLD}{C.CYAN}{'=' * 50}{C.NC}")
    print(f"{C.BOLD}{C.CYAN}  Build Monitor [{now_str}]{C.NC}")
    print(f"{C.BOLD}{C.CYAN}{'=' * 50}{C.NC}")
    print(f"  Status:    {sc}{C.BOLD}{status['status']}{C.NC}")
    print(f"  Sprint:    {status['sprint']} of {total_sprints}")
    print(f"  Phase:     {status['phase']}")
    print(f"  PID:       {status['pid'] or 'none'}")
    print(f"  Commits:   {status['commits']}")

    if status["stuck_minutes"] > 0:
        if status["stuck"]:
            print(f"  Last log:  {C.RED}{status['stuck_minutes']}m ago (STUCK){C.NC}")
        elif status["stuck_minutes"] > WARN_THRESHOLD_MINUTES:
            print(f"  Last log:  {C.YELLOW}{status['stuck_minutes']}m ago (slow){C.NC}")
        else:
            print(f"  Last log:  {status['stuck_minutes']}m ago")

    if status["last_activity"]:
        print(f"  Log file:  {status['last_activity']}")

    # Show last few lines of activity
    tail = get_latest_log_tail(2)
    if tail and tail != "(no logs)":
        print(f"\n  Recent:")
        for line in tail.split("\n"):
            print(f"    {line[:70]}")

    print(f"{C.BOLD}{C.CYAN}{'=' * 50}{C.NC}\n")

    # Actionable alerts
    if status["status"] == "DEAD":
        print(f"  {C.RED}ACTION: Runner died. Restart with:{C.NC}")
        print(f"  {C.BOLD}nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &{C.NC}")
        print(f"  {C.BOLD}echo $! > .buildrunner/.runner-pid{C.NC}")
    elif status["status"] == "STUCK":
        print(f"  {C.RED}ACTION: Runner stuck for {status['stuck_minutes']}m.{C.NC}")
        print(f"  Check logs: tail -50 .buildrunner/logs/")
        print(f"  Kill and restart if needed: kill {status['pid']}")


def main():
    status = monitor()
    print_report(status)

    # Exit codes for scripting
    if status["status"] == "RUNNING":
        sys.exit(0)
    elif status["status"] == "COMPLETE":
        sys.exit(0)
    elif status["status"] == "DEAD":
        sys.exit(1)
    elif status["status"] == "STUCK":
        sys.exit(2)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
