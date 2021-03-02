import contextlib
import os
import pathlib
import shutil
import subprocess
from typing import List, Tuple

from .executor import SRIMExecutorBase
from .types import PathLike


def copy_files(source: pathlib.Path, dest: pathlib.Path):
    """Copy files that are immediate children of the source

    :param source:
    :param dest:
    :return:
    """
    for p in source.iterdir():
        if not p.is_file():
            continue
        shutil.copy2(p, dest / p.name)


@contextlib.contextmanager
def copy_new_files(source: pathlib.Path, dest: pathlib.Path):
    # Record original set of files and their fs attributes
    before = set((p, p.stat()) for p in source.iterdir())
    yield
    # Record new set of files and their fs attributes
    after = set((p, p.stat()) for p in source.iterdir())
    # Find paths which changed between the yield
    modified_paths = [p for p, _ in after - before]

    for p in modified_paths:
        if not p.is_file():
            continue
        shutil.copy2(p, dest / p.name)


class NativeExecutor(SRIMExecutorBase):
    def __init__(self, srim_directory: PathLike):
        self._srim_directory = pathlib.Path(srim_directory)

    def _get_subprocess_args(self, executable_path: pathlib.Path) -> List[str]:
        """Return the argument list to be used by subprocess

        :param executable_path: executable name
        :return: list of subprocess arguments
        """
        args = []

        if os.name == "posix":
            # Use xvfb if available, for performance
            xvfb_path = shutil.which("xvfb-run")
            if xvfb_path is not None:
                args.extend([xvfb_path, "-a"])
            # Run executable with wine
            args.extend(["wine", executable_path.name])
        else:
            args.append(executable_path.name)

        return args

    def _run_command(self, io_directory: pathlib.Path, parts: Tuple[str, ...]):
        # Resolve executable on local FS
        executable_path = self._srim_directory.joinpath(*parts)
        assert executable_path.exists(), executable_path

        # Split executable path into
        working_directory = executable_path.parent

        # Copy input files
        copy_files(io_directory, working_directory)

        # Run command
        with copy_new_files(working_directory, io_directory):
            subprocess.check_call(
                self._get_subprocess_args(executable_path), cwd=working_directory
            )
