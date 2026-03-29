"""
CLI wrappers for Codex and Claude Code.

Prompts are written to temp files and piped via stdin.
Output streams to both a log file AND the main process stdout
so `tail -f` on the runner log shows everything in real-time.
"""

import subprocess
import os
import sys
import tempfile
import threading
from dataclasses import dataclass
from typing import Optional, IO
from pathlib import Path


@dataclass
class CLIResult:
    """Result from a CLI command execution."""
    stdout: str
    stderr: str
    returncode: int


def run_command(
    cmd: list[str],
    cwd: Optional[str] = None,
    timeout: int = 120
) -> CLIResult:
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return CLIResult(
            stdout=result.stdout, stderr=result.stderr, returncode=result.returncode
        )
    except subprocess.TimeoutExpired as e:
        return CLIResult(
            stdout=e.stdout or "", stderr=f"TIMEOUT after {timeout}s", returncode=-1
        )
    except FileNotFoundError:
        return CLIResult(
            stdout="", stderr=f"Command not found: {cmd[0]}", returncode=-1
        )


def _run_agent(
    cmd: list[str],
    prompt: str,
    cwd: Optional[str] = None,
    timeout: int = 2700,
    label: str = "agent",
    env_extra: Optional[dict] = None,
) -> CLIResult:
    """Run an AI agent CLI with streaming output.

    - Writes prompt to temp file, pipes via stdin
    - Streams stdout/stderr to both log file and console in real-time
    - Returns captured output when done
    """
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.md', delete=False, prefix=f'{label}-prompt-'
    ) as f:
        f.write(prompt)
        prompt_file = f.name

    log_dir = Path(cwd or '.') / '.buildrunner' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{label}-live.log"

    env = {**os.environ, **(env_extra or {})}

    try:
        with open(prompt_file, 'r') as pf, open(log_path, 'a') as lf:
            lf.write(f"\n{'=' * 60}\n")
            lf.write(f"[{label}] Starting at {__import__('datetime').datetime.now().isoformat()}\n")
            lf.write(f"{'=' * 60}\n\n")
            lf.flush()

            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=pf,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            stdout_captured = []
            stderr_captured = []

            def read_stdout():
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        tagged = f"[{label}] {line}"
                        lf.write(tagged)
                        lf.flush()
                        sys.stdout.write(tagged)
                        sys.stdout.flush()
                        stdout_captured.append(line)

            def read_stderr():
                for line in iter(proc.stderr.readline, ''):
                    if line:
                        tagged = f"[{label}:err] {line}"
                        lf.write(tagged)
                        lf.flush()
                        sys.stderr.write(tagged)
                        sys.stderr.flush()
                        stderr_captured.append(line)

            t_out = threading.Thread(target=read_stdout, daemon=True)
            t_err = threading.Thread(target=read_stderr, daemon=True)
            t_out.start()
            t_err.start()

            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                raise RuntimeError(f"{label} timed out after {timeout}s")

            t_out.join(timeout=5)
            t_err.join(timeout=5)

            stdout_text = ''.join(stdout_captured)
            stderr_text = ''.join(stderr_captured)

            if proc.returncode != 0:
                raise RuntimeError(
                    f"{label} exited with code {proc.returncode}: "
                    f"{stderr_text[-500:]}"
                )

            return CLIResult(
                stdout=stdout_text, stderr=stderr_text, returncode=proc.returncode
            )
    finally:
        try:
            os.unlink(prompt_file)
        except OSError:
            pass


def run_codex(
    prompt: str,
    cwd: Optional[str] = None,
    timeout: int = 2700
) -> CLIResult:
    """Run Codex CLI in full-auto mode with streaming output."""
    return _run_agent(
        cmd=["codex", "exec", "--full-auto", "--ephemeral", "-"],
        prompt=prompt,
        cwd=cwd,
        timeout=timeout,
        label="codex",
        env_extra={"CODEX_QUIET_MODE": "1"},
    )


def run_claude(
    prompt: str,
    cwd: Optional[str] = None,
    timeout: int = 2700
) -> CLIResult:
    """Run Claude Code CLI in non-interactive mode with streaming output."""
    return _run_agent(
        cmd=["claude", "-p", "--model", "opus", "--permission-mode", "bypassPermissions"],
        prompt=prompt,
        cwd=cwd,
        timeout=timeout,
        label="claude",
    )
