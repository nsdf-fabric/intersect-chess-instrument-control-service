from __future__ import annotations

import logging
from pathlib import Path

from intersect_sdk import (
    IntersectBaseCapabilityImplementation,
    intersect_message,
    intersect_status,
)

from .data_models import ExperimentConfig, MotorPosition
from .file_writer import initialize_experiment, write_motor_position

logger = logging.getLogger(__name__)


class ChessInstrumentControlCapability(IntersectBaseCapabilityImplementation):
    """INTERSECT capability that writes motor position files for SPEC."""

    intersect_sdk_capability_name = "chess-instrument-control"

    def __init__(self):
        super().__init__()
        self._experiment_dir: Path | None = None

    @intersect_message()
    def initialize_experiment(self, config: ExperimentConfig) -> str:
        """Initialize the directory structure for an autonomous experiment."""
        self._experiment_dir = initialize_experiment(config.experiment_name, config.base_dir)
        logger.info("Initialized experiment at %s", self._experiment_dir)
        return str(self._experiment_dir)

    @intersect_message()
    def write_motor_position(self, position: MotorPosition) -> str:
        """Write a motor position file for SPEC to read."""
        if self._experiment_dir is None:
            msg = "Experiment not initialized. Call initialize_experiment first."
            raise RuntimeError(msg)

        filepath = write_motor_position(self._experiment_dir, position.labx, position.labz)
        logger.info("Wrote motor position to %s", filepath)
        return str(filepath)

    @intersect_status()
    def status(self) -> str:
        """Return current service status."""
        return "Initialized" if self._experiment_dir is not None else "Ready"
