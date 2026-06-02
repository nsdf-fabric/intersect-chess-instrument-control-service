from chess_instrument_control_service.data_models import ExperimentConfig, MotorPosition
from chess_instrument_control_service.service import ChessInstrumentControlCapability


class TestChessInstrumentControlCapabilityInit:
    def test_capability_has_correct_name(self):
        capability = ChessInstrumentControlCapability()
        assert capability.intersect_sdk_capability_name == "chess_instrument_control"

    def test_initial_status_is_ready(self):
        capability = ChessInstrumentControlCapability()
        assert capability.status() == "Ready"


class TestChessInstrumentControlCapabilityInitExperiment:
    def test_initialize_experiment_creates_directories(self, tmp_path):
        capability = ChessInstrumentControlCapability()
        config = ExperimentConfig(
            experiment_name="experiment1",
            base_dir=str(tmp_path),
        )
        result = capability.initialize_experiment(config)
        expected = tmp_path / "experiment1"
        assert expected.is_dir()
        assert "experiment1" in result

    def test_status_changes_to_initialized(self, tmp_path):
        capability = ChessInstrumentControlCapability()
        config = ExperimentConfig(
            experiment_name="experiment1",
            base_dir=str(tmp_path),
        )
        capability.initialize_experiment(config)
        assert capability.status() == "Initialized"


class TestChessInstrumentControlCapabilityWriteMotorPosition:
    def test_write_motor_position_writes_file(self, tmp_path):
        capability = ChessInstrumentControlCapability()
        config = ExperimentConfig(
            experiment_name="experiment1",
            base_dir=str(tmp_path),
        )
        capability.initialize_experiment(config)

        position = MotorPosition(labx=-47.33, labz=-242.5)
        result = capability.write_motor_position(position)

        expected_file = tmp_path / "experiment1" / "loc001.txt"
        assert expected_file.exists()
        assert "loc001.txt" in result

    def test_write_motor_position_sequential(self, tmp_path):
        capability = ChessInstrumentControlCapability()
        config = ExperimentConfig(
            experiment_name="experiment1",
            base_dir=str(tmp_path),
        )
        capability.initialize_experiment(config)

        capability.write_motor_position(MotorPosition(labx=1.0, labz=2.0))
        result = capability.write_motor_position(MotorPosition(labx=3.0, labz=4.0))

        assert "loc002.txt" in result

    def test_write_motor_position_requires_initialization(self):
        capability = ChessInstrumentControlCapability()
        position = MotorPosition(labx=1.0, labz=2.0)

        try:
            capability.write_motor_position(position)
            assert False, "Should have raised an error"
        except RuntimeError:
            pass
