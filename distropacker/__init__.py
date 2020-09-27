
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
docker_dir = root_dir.joinpath("docker")
samples_dir = docker_dir.joinpath("sample_package")
