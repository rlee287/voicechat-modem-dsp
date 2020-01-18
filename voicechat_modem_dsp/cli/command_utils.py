import cleo

from strictyaml import YAMLValidationError
import os.path

from .config_loader import parse_config_str

class CLIError(Exception):
    """
    Error raised to exit from cleo.Command.handle early
    """

class FileExistsAndCannotOverwriteException(CLIError):
    """
    Error indicating file exists and cannot overwrite

    Subclass of CLIError
    """

class ExtendedCommand(cleo.Command):
    """cleo.Command extended with additional utility functions"""

    """Confirm whether a file is writable and raise an exception if not"""
    def confirm_file_writable(self, filename: str) -> None:
        if os.path.exists(filename):
            if os.path.isdir(filename):
                raise FileExistsAndCannotOverwriteException(
                    "Output file {} must be writable as a file."
                    .format(filename),"error")

            if self.io.is_interactive():
                result=self.confirm("Output file {} already exists. Overwrite?"
                    .format(filename))
                if not result:
                    raise FileExistsAndCannotOverwriteException(
                        "Choosing not to overwrite existing output file {}."
                        .format(filename))
            else:
                raise FileExistsAndCannotOverwriteException(
                    "Output file {} already exists "
                    "and program is in noninteractive mode."
                    .format(filename),"error")

    @staticmethod
    def parse_config_file(config_file_name):
        try:
            with open(config_file_name, "r") as fil:
                config_text=fil.read()
                config_obj=parse_config_str(config_text)
        except YAMLValidationError as e:
            # e.args[0] is the error message
            raise CLIError(e.args[0],"error")
        return config_obj
