"""Describe the Haddock3 ontology used for communicating between modules."""
import datetime
import jsonpickle
from enum import Enum
from haddock.core.defaults import MODULE_IO_FILE
from os import linesep
from pathlib import Path


class Format(Enum):
    """Input and Output possible formats."""

    PDB = "pdb"
    PDB_ENSEMBLE = "pdb"
    CNS_INPUT = "inp"
    CNS_OUTPUT = "out"
    TOPOLOGY = "psf"

    def __str__(self):
        return str(self.value)


class Persistent:
    """Any persistent file generated by this framework."""

    def __init__(self, file_name, file_type, path='.'):
        self.created = datetime.datetime.now().isoformat(' ', 'seconds')
        self.file_name = Path(file_name).name
        self.file_type = file_type
        self.path = str(Path(path).resolve())

    def __repr__(self):
        rep = (f"[{self.file_type}|{self.created}] "
               f"{Path(self.path) / self.file_name}")
        return rep


class PDBFile(Persistent):
    """Represent a PDB file."""

    def __init__(self, file_name, topology=None, path='.', score=float('nan')):
        super().__init__(file_name, Format.PDB, path)
        self.topology = topology
        self.score = score


class TopologyFile(Persistent):
    """Represent a CNS-generated topology file."""

    def __init__(self, file_name, path='.'):
        super().__init__(file_name, Format.TOPOLOGY, path)


class ModuleIO:
    """Intercommunicating modules and exchange input/output information."""

    def __init__(self):
        self.input = []
        self.output = []

    def add(self, persistent, mode="i"):
        """Add a given filename as input or output."""
        if mode == "i":
            if isinstance(persistent, list):
                self.input.extend(persistent)
            else:
                self.input.append(persistent)
        else:
            if isinstance(persistent, list):
                self.output.extend(persistent)
            else:
                self.output.append(persistent)

    def save(self, path, filename=MODULE_IO_FILE):
        """Save Input/Output needed files by this module to disk."""
        with open(path / filename, "w") as output_handler:
            to_save = {"input": self.input,
                       "output": self.output}
            jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
            output_handler.write(jsonpickle.encode(to_save))
        return path / filename

    def load(self, filename):
        """Load the content of a given IO filename."""
        with open(filename) as json_file:
            content = jsonpickle.decode(json_file.read())
            self.input = content["input"]
            self.output = content["output"]

    def __repr__(self):
        return f"Input: {self.input}{linesep}Output: {self.output}"
