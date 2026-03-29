"""
Sprint state machine and progress tracking.

Reads sprint/stage configuration from config.py.
Persists last completed sprint number to a file.
"""

from pathlib import Path
from config import (
    SPRINT_STAGES, STAGE_BOUNDARIES, ENV_REQUIREMENTS,
    SPRINT_STAGE_FILES, SPRINT_PAGES, STAGE_NAMES, SPRINT_NAMES
)


class SprintState:
    """Persists the last completed sprint number to a file."""

    def __init__(self, state_file: Path):
        self.state_file = state_file

    def load(self) -> int:
        """Load the last completed sprint number. Returns 0 if no state."""
        if self.state_file.exists():
            content = self.state_file.read_text().strip()
            if content.isdigit():
                return int(content)
        return 0

    def save(self, sprint_num: int):
        """Save the completed sprint number."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(str(sprint_num))
