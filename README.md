# Intersect Chess Instrument Control Service

INTERSECT Spec Service for CHESS. Receives next-point recommendations from
[Dial](https://github.com/INTERSECT-DIAL/dial) (via the campaign orchestrator) and writes motor position files
that SPEC reads at the beamline.

## Architecture Role

This service is the **INTERSECT Spec Service** in the CHESS autonomous
experiment loop:

1. [Dial](https://github.com/INTERSECT-DIAL/dial) recommends the next measurement point `[labx, labz]`
2. The campaign orchestrator routes Dial's output to **this service**
3. **This service** writes a `locNNN.txt` file with the motor position
4. The [chess-instrument-control-informer](../chess-instrument-control-informer)
   watches the location directory and processes the new point

## Directory Structure

When initialized for an experiment, this service creates:

```
<base_dir>/
    <experiment_name>/
      loc001.txt
      loc002.txt
      ...
```

Each `locNNN.txt` file contains:
```
labx,labz
-47.33,-242.5
```

This format is compatible with the informer's `parse_location_file()`.

## Installation

```bash
uv sync
```

## Usage

### As an INTERSECT Service

```bash
# Start with local config
uv run python scripts/launch_service.py --config local-conf.json

# Or with Docker
docker compose up
```

### INTERSECT Message Endpoints

- `initialize_experiment(ExperimentConfig)` — Create the experiment directory
  structure
- `write_motor_position(MotorPosition)` — Write a motor position file for SPEC
- `status()` — Returns `"Ready"` or `"Initialized"`

### ExperimentConfig

```json
{
  "experiment_name": "experiment1",
  "base_dir": "/data/chess"
}
```

### MotorPosition

```json
{
  "labx": -47.33,
  "labz": -242.5
}
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/

# Lint
uv run ruff check --fix
uv run ruff format --check
```

## Docker

```bash
# Build
docker build -t chess-instrument-control-service .

# Run with docker-compose (includes RabbitMQ broker)
docker compose up
```
