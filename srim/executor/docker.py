import pathlib
import subprocess
from typing import Tuple

from .executor import SRIMExecutorBase
from .types import PathLike


class DockerExecutor(SRIMExecutorBase):

    entrypoint_contents = """
#!/usr/bin/env bash
set -eu
shopt -s extglob globstar nullglob
cp -R "{directory}/." .

# Run wine
xvfb-run -a wine "{executable}"

# Copy outputs (recursively)
cp -n **/*.{{IN,txt}} "{directory}/" || true
"""

    def __init__(
        self,
        container_image: str = "costrouc/srim",
        container_bind_path: PathLike = "/usr/local/src/srim",
        container_srim_directory: PathLike = "/tmp/srim",
    ):
        self._container_image = container_image
        self._container_bind_directory = pathlib.PurePosixPath(container_bind_path)
        self._container_srim_directory = pathlib.PurePosixPath(container_srim_directory)

    def _run_command(self, io_directory: pathlib.Path, parts: Tuple[str, ...]):
        # Resolve executable on remote FS
        executable_path = self._container_srim_directory.joinpath(*parts)

        # Build entrypoint for user
        entrypoint_script = self.entrypoint_contents.format(
            executable=executable_path, directory=self._container_bind_directory
        )

        # Run command
        subprocess.check_call(
            [
                "docker",
                "run",
                "--rm",
                "--volume",
                f"{io_directory}:{self._container_bind_directory}",
                "--workdir",
                executable_path.parent,
                self._container_image,
                "bash",
                "-c",
                entrypoint_script,
            ]
        )
