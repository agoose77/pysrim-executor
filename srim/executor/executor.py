import contextlib
import os
import pathlib
import tempfile
from typing import Callable, Tuple, TypeVar, NamedTuple

from srim import output, srim

from .types import PathLike


@contextlib.contextmanager
def cwd_as(path: PathLike):
    """Set the current working directory, and restore it upon exit.

    :param path: new working directory
    :return:
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


T = TypeVar("T")


class SRIMPipeline(NamedTuple):
    generator: Callable[[], None]
    parser: Callable[[pathlib.Path], T]
    command: Tuple[str, ...]


class SRIMExecutorBase:
    """Base class for a SRIM pipeline executor."""

    def _run_command(self, io_directory: pathlib.Path, parts: Tuple[str, ...]):
        """Run a SRIM command for a set of input files.

        :param io_directory: directory from which to read/write the inputs/outputs
        :param parts: path components which together build the relative SRIM executable
        path
        :return:
        """
        raise NotImplementedError

    def _run_pipeline(self, io_directory: pathlib.Path, pipeline: SRIMPipeline):
        """Run a SRIM pipeline by generating the input files, running the command,
        and parsing the results.

        :param io_directory: directory from which to read & write the inputs & outputs
        :param pipeline: object describing the SRIM pipeline
        :return: the parsed pipeline result
        """
        with cwd_as(io_directory):
            pipeline.generator()

        self._run_command(io_directory, pipeline.command)

        return pipeline.parser(io_directory)

    def run(self, obj, io_directory: PathLike = None):
        """Run a SRIM pipeline given by a SRIM object.

        :param obj: SRIM object
        :param io_directory: directory from which to read & write the inputs & outputs
        :return:
        """
        if isinstance(obj, srim.SR):
            pipeline = SRIMPipeline(
                obj._write_input_file, output.SRResults, ("SR Module", "SRModule.exe")
            )

        elif isinstance(obj, srim.TRIM):
            pipeline = SRIMPipeline(
                obj._write_input_files, output.Results, ("TRIM.exe",)
            )
        else:
            raise NotImplementedError(f"No implementation found for {type(obj)}")

        if io_directory is None:
            io_directory = pathlib.Path(tempfile.mkdtemp())

        io_directory.mkdir(exist_ok=True)

        return self._run_pipeline(io_directory, pipeline)
