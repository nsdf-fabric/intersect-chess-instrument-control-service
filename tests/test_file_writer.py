from pathlib import Path

from chess_instrument_control_service.file_writer import initialize_experiment, write_motor_position


class TestInitializeExperiment:
    def test_creates_experiment_directory(self, tmp_path):
        result = initialize_experiment("experiment1", str(tmp_path))
        expected = tmp_path / "experiment1"
        assert expected.is_dir()
        assert result == expected

    def test_creates_nested_directories(self, tmp_path):
        base = tmp_path / "deep" / "nested"
        initialize_experiment("experiment1", str(base))
        expected = base / "experiment1"
        assert expected.is_dir()

    def test_returns_experiment_path(self, tmp_path):
        result = initialize_experiment("experiment1", str(tmp_path))
        assert isinstance(result, Path)
        assert result.name == "experiment1"
        

    def test_idempotent_on_existing_directory(self, tmp_path):
        """Calling initialize_experiment twice should not error."""
        initialize_experiment("experiment1", str(tmp_path))
        result = initialize_experiment("experiment1", str(tmp_path))
        assert result.is_dir()


class TestWriteMotorPosition:
    def test_writes_first_location_file(self, tmp_path):
        experiment_dir = tmp_path / "experiment1"
        experiment_dir.mkdir(parents=True)

        path = write_motor_position(experiment_dir, labx=-47.33, labz=-242.5)

        assert path.name == "loc001.txt"
        content = path.read_text()
        lines = content.strip().splitlines()
        assert lines[0] == "labx,labz"
        assert lines[1] == "-47.33,-242.5"

    def test_sequential_numbering(self, tmp_path):
        experiment_dir = tmp_path / "experiment1"
        experiment_dir.mkdir(parents=True)

        path1 = write_motor_position(experiment_dir, labx=1.0, labz=2.0)
        path2 = write_motor_position(experiment_dir, labx=3.0, labz=4.0)
        path3 = write_motor_position(experiment_dir, labx=5.0, labz=6.0)

        assert path1.name == "loc001.txt"
        assert path2.name == "loc002.txt"
        assert path3.name == "loc003.txt"

    def test_file_content_format(self, tmp_path):
        """File format must be compatible with
        chess_instrument_control_informer.locations.parse_location_file()
        which expects: header 'labx,labz' then 'float,float' rows.
        """
        experiment_dir = tmp_path / "experiment1"
        experiment_dir.mkdir(parents=True)

        write_motor_position(experiment_dir, labx=10.5, labz=-20.3)

        path = experiment_dir / "loc001.txt"
        content = path.read_text()
        lines = content.strip().splitlines()
        # Header
        assert lines[0] == "labx,labz"
        # Data row - parseable as floats
        parts = lines[1].split(",")
        assert float(parts[0]) == 10.5
        assert float(parts[1]) == -20.3

    def test_returns_written_path(self, tmp_path):
        experiment_dir = tmp_path / "experiment1"
        experiment_dir.mkdir(parents=True)

        path = write_motor_position(experiment_dir, labx=1.0, labz=2.0)
        assert isinstance(path, Path)
        assert path.exists()

    def test_auto_detects_existing_files_for_numbering(self, tmp_path):
        """If loc001.txt already exists, the next write should be loc002.txt."""
        experiment_dir = tmp_path / "experiment1"
        experiment_dir.mkdir(parents=True)

        # Manually create loc001.txt
        (experiment_dir / "loc001.txt").write_text("labx,labz\n1.0,2.0\n")

        path = write_motor_position(experiment_dir, labx=3.0, labz=4.0)
        assert path.name == "loc002.txt"
