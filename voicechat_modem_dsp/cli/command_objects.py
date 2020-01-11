import cleo

import functools
import os

class CLIError(Exception):
    pass

def exit_on_error(func):
    def catch_error_and_exit(self,*args,**kwargs):
        try:
            return func(self,*args,**kwargs)
        except CLIError as e:
            self.line_error(*e.args)
            return 1
    functools.update_wrapper(catch_error_and_exit,func)
    return catch_error_and_exit

class TxFile(cleo.Command):
    """
    Modulates a given datafile and saves modulated audio to an audio file

    transmit_file
        {filename : Data file to modulate}
        {--o|output=modulated.wav : Output file for audio}
        {--config= : Modulation configuration file}
        {--no-preamble : Do not include audio preamble with 
            modulation information}
        {--no-toneburst : Do not include calibration toneburst}
        {--raw : Shortcut for --no-preamble --no-toneburst}
    """

    @exit_on_error
    def handle(self):
        config_file_name=self.option("config")
        output_file_name=self.option("output")

        # Check validity of command line options
        if not config_file_name:
            raise CLIError("A configuration file must be specified.","error")
        if not os.path.isfile(config_file_name):
            raise CLIError("Config file specified does not exist.","error")

        if os.path.exists(output_file_name):
            if os.path.isdir(output_file_name):
                raise CLIError("Output file {} must be writable as a file."
                    .format(output_file_name),"error")

            if self._io.is_interactive():
                result=self.confirm("Output file {} already exists. Overwrite?"
                    .format(output_file_name))
                self.line(str(result))
                if not result:
                    return 0
            else:
                raise CLIError("Output file {} already exists "
                    "and program is in noninteractive mode."
                    .format(output_file_name),"error")
