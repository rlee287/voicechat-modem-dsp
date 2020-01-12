import cleo

import functools
import os
from scipy.io import wavfile

from strictyaml import YAMLValidationError

from .config_loader import parse_config_str, construct_modulators
from ..modulators import ASKModulator, FSKModulator
from ..encoders import encode_function_mappings, decode_function_mappings

"""
Error raised to exit from cleo.Command.handle early
"""
class CLIError(Exception):
    pass

"""
Decorator that catches CLIErrors, prints the error,
and exits with a nonzero status code
"""
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
        {input-file : Data file to modulate}
        {--o|output=modulated.wav : Output file for audio}
        {--config= : Modulation configuration file}
        {--no-header : Do not include audio header with 
            modulation information}
        {--no-preamble : Do not include calibration preamble}
        {--raw : Shortcut for --no-preamble --no-toneburst}
    """

    @exit_on_error
    def handle(self):
        config_file_name=self.option("config")
        output_file_name=self.option("output")
        input_file_name=self.argument("input-file")

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
                if not result:
                    return 0
            else:
                raise CLIError("Output file {} already exists "
                    "and program is in noninteractive mode."
                    .format(output_file_name),"error")
        
        if not os.path.isfile(input_file_name):
            raise CLIError("Input file {} must exist."
                .format(input_file_name),"error")

        has_header = not (self.option("no-header") or self.option("raw"))
        has_preamble = not (self.option("no-preamble") or self.option("raw"))
        
        # TODO: obviously temporary; fix once prerequisites are done
        if has_header or has_preamble:
            raise CLIError("Headers and preambles are not yet supported.")

        self.line("Reading config file...")
        try:
            with open(config_file_name, "r") as fil:
                config_text=fil.read()
                config_obj=parse_config_str(config_text)
        except YAMLValidationError as e:
            # e.args[0] is the error message
            raise CLIError(e.args[0],"error")
        
        # TODO: obviously temporary; fix once prerequisites are done
        if len(config_obj["modulators"])>1:
            raise CLIError("Multiplexing modulators is not yet supported.")

        modulator_objects=construct_modulators(config_obj.data)
        # TODO: construct OFDM once that is complete
        modulator_obj=modulator_objects[0]

        if modulator_obj.fs!=int(modulator_obj.fs):
            raise CLIError("Sampling rate must be an integer (for now).")

        if isinstance(modulator_obj,ASKModulator):
            constellation_length=len(modulator_obj.amp_list)
        elif isinstance(modulator_obj,FSKModulator):
            constellation_length=len(modulator_obj.freq_list)
        else:
            raise CLIError("Modulator type is not yet supported.")

        self.line("Encoding data...")
        try:
            datastream_encoder=encode_function_mappings[constellation_length]
        except KeyError:
            raise CLIError("Unsupported count of constellation values.")

        with open(input_file_name,"rb") as fil:
            bitstream=fil.read()
        datastream=datastream_encoder(bitstream)
        self.line("Modulating data...")
        modulated_datastream=modulator_obj.modulate(datastream)

        self.line("Writing audio file...")
        wavfile.write(output_file_name, int(modulator_obj.fs),
            modulated_datastream)