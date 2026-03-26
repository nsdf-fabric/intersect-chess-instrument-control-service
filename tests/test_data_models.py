import pytest
from pydantic import ValidationError

from chess_instrument_control_service.data_models import ExperimentConfig, MotorPosition


class TestExperimentConfig:
    def test_valid_config(self):
        config = ExperimentConfig(
            experiment_name="experiment1",
            base_dir="/data/chess",
        )
        assert config.experiment_name == "experiment1"
        assert config.base_dir == "/data/chess"

    def test_missing_experiment_name_raises(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(base_dir="/data/chess")

    def test_missing_base_dir_raises(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(experiment_name="experiment1")


class TestMotorPosition:
    def test_valid_position(self):
        pos = MotorPosition(labx=-47.33, labz=-242.5)
        assert pos.labx == -47.33
        assert pos.labz == -242.5

    def test_positive_values(self):
        pos = MotorPosition(labx=10.5, labz=20.3)
        assert pos.labx == 10.5
        assert pos.labz == 20.3

    def test_zero_values(self):
        pos = MotorPosition(labx=0.0, labz=0.0)
        assert pos.labx == 0.0
        assert pos.labz == 0.0
