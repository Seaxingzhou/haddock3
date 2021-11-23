"""Run subprocess jobs."""
import os
import shlex
import subprocess

from haddock import toppar_path
from haddock.core.defaults import cns_exec
from haddock.core.exceptions import CNSRunningError, JobRunningError


class Job:
    """A job to be executed by the engine."""

    def __init__(self, input, output, executable, *args):
        self.input = input
        self.output = output
        self.executable = executable
        self.args = args

    def run(self):
        """Execute subprocess job."""
        cmd = " ".join([
            os.fspath(self.executable),
            ''.join(map(str, self.args)),  # empty string if no args
            os.fspath(self.input),
            ])

        with open(self.output, 'w') as outf:
            p = subprocess.Popen(shlex.split(cmd),
                                 stdout=outf,
                                 close_fds=True)
            out, error = p.communicate()

        p.kill()

        if error:
            raise JobRunningError(error)

        return out


class CNSJob:
    """A CNS job script."""

    def __init__(
            self,
            input_file,
            output_file,
            cns_folder,
            modpath,
            config_path,
            cns_exec=None,
            ):
        """
        CNS subprocess.

        Parameters
        ----------
        input_file : str or pathlib.Path
            The path to the .inp CNS file.

        output_file : str or pathlib.Path
            The path to the .out CNS file, where the standard output
            will be saved.

        cns_folder : str of pathlib.Path
            The path where the CNS scripts needed for the module reside.
            For example, `modules/rigidibody/cns`.

        mod_path : str of pathlib.Path
            Path where the results of the haddock3 module executing this
            CNS job will be saved.

        config_path : str of pathlib.Path
            Path of the haddock3 configuration file. Will be used to
            manage paths in relative manner.

        cns_exec : str of pathlib.Path, optional
            The path to the CNS exec. If not provided defaults to the
            global configuration in HADDOCK3.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.cns_folder = cns_folder
        self.modpath = modpath
        self.config_path = config_path

        self.cns_exec = cns_exec

    @property
    def cns_exec(self):
        """CNS executable path."""
        return self._cns_exec

    @cns_exec.setter
    def cns_exec(self, cns_exec_path):
        if cns_exec_path is None:
            cns_exec_path = cns_exec  # global cns_exec

        if not os.access(cns_exec_path, mode=os.X_OK):
            raise ValueError(
                f'{str(cns_exec_path)!r} binary file not found, '
                'or is not executable.'
                )

        self._cns_exec = cns_exec_path

    def run(self):
        """Run this CNS job script."""
        with open(self.input_file) as inp, \
                open(self.output_file, 'w+') as outf:

            env = {
                'MODDIR': self.modpath,
                'MODULE': self.cns_folder,
                'RUN': self.config_path,
                'TOPPAR': toppar_path,
                }
            p = subprocess.Popen(
                self.cns_exec,
                stdin=inp,
                stdout=outf,
                stderr=subprocess.PIPE,
                close_fds=True,
                env=env,
                )

            out, error = p.communicate()
            p.kill()

        if error:
            raise CNSRunningError(error)

        return out
