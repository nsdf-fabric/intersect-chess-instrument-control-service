from __future__ import annotations

import re
from pathlib import Path


def initialize_experiment(experiment_name: str, base_dir: str) -> Path:
    """Create the directory structure for an autonomous experiment.

    Creates: <base_dir>/autonomous_experiment/<experiment_name>/

    Returns the experiment directory path.
    """
    experiment_dir = Path(base_dir) / "autonomous_experiment" / experiment_name
    experiment_dir.mkdir(parents=True, exist_ok=True)
    return experiment_dir


def write_motor_position(experiment_dir: Path, labx: float, labz: float) -> Path:
    """Write a motor position file in the format expected by parse_location_file().

    File format:
        labx,labz
        <labx_value>,<labz_value>

    Files are named loc001.txt, loc002.txt, etc. Numbering auto-detects
    existing files in the directory.

    Returns the path of the written file.
    """
    next_num = _next_location_number(experiment_dir)
    filename = f"loc{next_num:03d}.txt"
    filepath = experiment_dir / filename

    filepath.write_text(f"labx,labz\n{labx},{labz}\n")
    return filepath


def _next_location_number(experiment_dir: Path) -> int:
    """Determine the next location file number based on existing files."""
    pattern = re.compile(r"^loc(\d+)\.txt$")
    max_num = 0
    for f in experiment_dir.iterdir():
        match = pattern.match(f.name)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1
