from __future__ import annotations

from pydantic import BaseModel, Field


class ExperimentConfig(BaseModel):
    """Configuration for initializing an autonomous experiment."""

    experiment_name: str = Field(description="Name of the experiment, e.g. 'experiment1'")
    base_dir: str = Field(description="Base directory for experiment data")


class MotorPosition(BaseModel):
    """A motor position to write as a location file for SPEC."""

    labx: float = Field(description="Lab X coordinate")
    labz: float = Field(description="Lab Z coordinate")
