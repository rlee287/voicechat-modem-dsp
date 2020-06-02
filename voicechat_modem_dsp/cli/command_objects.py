import cleo

import functools
import os
from scipy.io import wavfile

from .config_loader import construct_modulators
from .command_utils import CLIError, ExtendedCommand

from ..modulators import ASKModulator, PSKModulator, QAMModulator, FSKModulator
from ..encoders import encode_function_mappings, decode_function_mappings
from ..encoders.ecc import *

"""
Decorator for class methods that catches CLIErrors, prints the error,
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

class TxFile(ExtendedCommand):
    """
    Modulates a given datafile and saves modulated audio to an audio file

    transmit_file
        {input-file : Data file to modulate}
        {--o|output=modulated.wav : Output file for audio}
        {--config= : Modulation configuration file}
        {--no-header : Do not include audio header with 
            modulation information}
        {--no-preamble : Do not include calibration preamble}
        {--raw : Shortcut for --no-header --no-preamble}
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
            raise CLIError("Configuration file {} does not exist."
                .format(config_file_name),"error")

        if not os.path.isfile(input_file_name):
            raise CLIError("Input file {} must exist."
                .format(input_file_name),"error")

        self.confirm_file_writable(output_file_name)

        has_header = not (self.option("no-header") or self.option("raw"))
        has_preamble = not (self.option("no-preamble") or self.option("raw"))
        
        # TODO: obviously temporary; fix once prerequisites are done
        if has_header or has_preamble:
            raise CLIError("Headers and preambles are not yet supported.")

        # Read in config file and check its validity
        self.line("Reading config file...")
        config_obj=self.parse_config_file(config_file_name)
        
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
        elif isinstance(modulator_obj,PSKModulator):
            constellation_length=len(modulator_obj.phase_list)
        elif isinstance(modulator_obj,QAMModulator):
            constellation_length=len(modulator_obj.constellation_list)
        else:
            raise CLIError("Modulator type is not yet supported.")

        self.line("Encoding data...")
        try:
            datastream_encoder=encode_function_mappings[constellation_length]
        except KeyError:
            raise CLIError("Unsupported count of constellation values.")

        with open(input_file_name,"rb") as fil:
            bitstream=fil.read()
        ecc_object=NoECC() # type: BaseECC
        if config_obj["ecc"].data in ["none","raw"]:
            pass
        elif config_obj["ecc"].data in ["hamming_7_4"]:
            ecc_object=Hamming_7_4_ECC()
        else:
            # Should never happen
            raise CLIError("Invalid ECC mode found late; should have been caught earlier","error") # pragma: no cover
        bitstream=ecc_object.encode(bitstream)
        datastream=datastream_encoder(bitstream)
        self.line("Modulating data...")
        modulated_datastream=modulator_obj.modulate(datastream)

        self.line("Writing audio file...")
        wavfile.write(output_file_name, int(modulator_obj.fs),
            modulated_datastream)

class RxFile(ExtendedCommand):
    """
    Deodulates a given audiofile and saves demodulated data to a file

    receive_file
        {input-file : Wave file to demodulate}
        {--o|output= : Output file for audio}
        {--config= : Modulation configuration file (when header is missing)}
    """

    @exit_on_error
    def handle(self):
        config_file_name=self.option("config")
        output_file_name=self.option("output")
        input_file_name=self.argument("input-file")

        # Check validity of command line options
        if not output_file_name:
            raise CLIError("An output file must be specified.","error")

        if not os.path.isfile(input_file_name):
            raise CLIError("Input file {} must exist."
                .format(input_file_name),"error")

        self.confirm_file_writable(output_file_name)

        # TODO: try to extract information from header once that is implemented
        self.line("Falling back onto reading config file...")

        if not config_file_name:
            raise CLIError("A configuration file must be specified.","error")
        if not os.path.isfile(config_file_name):
            raise CLIError("Configuration file {} does not exist."
                .format(config_file_name),"error")

        config_obj=self.parse_config_file(config_file_name)

        # TODO: obviously temporary; fix once prerequisites are done
        if len(config_obj["modulators"])>1:
            raise CLIError("Multiplexing modulators is not yet supported.")

        modulator_objects=construct_modulators(config_obj.data)
        # TODO: construct OFDM once that is complete
        modulator_obj=modulator_objects[0]
        if isinstance(modulator_obj,ASKModulator):
            constellation_length=len(modulator_obj.amp_list)
        elif isinstance(modulator_obj,FSKModulator):
            constellation_length=len(modulator_obj.freq_list)
        elif isinstance(modulator_obj,PSKModulator):
            constellation_length=len(modulator_obj.phase_list)
        elif isinstance(modulator_obj,QAMModulator):
            constellation_length=len(modulator_obj.constellation_list)
        else:
            raise CLIError("Modulator type is not yet supported.")

        try:
            datastream_decoder=decode_function_mappings[constellation_length]
        except KeyError:
            raise CLIError("Unsupported count of constellation values.")

        self.line("Reading audio file...")
        wavfile_fs, modulated_datastream = wavfile.read(input_file_name)
        if wavfile_fs != config_obj["fs"].data:
            raise CLIError("Sampling frequency mismatch in config and audio",
                "error")
        self.line("Demodulating audio...")
        datastream=modulator_obj.demodulate(modulated_datastream)
        bitstream=datastream_decoder(datastream)

        self.line("Writing demodulated data...")
        ecc_object=NoECC() # type: BaseECC
        if config_obj["ecc"].data in ["none","raw"]:
            pass
        elif config_obj["ecc"].data in ["hamming_7_4"]:
            ecc_object=Hamming_7_4_ECC()
        else:
            # Should never happen
            raise CLIError("Invalid ECC mode found late; should have been caught earlier","error") # pragma: no cover
        bitstream=ecc_object.decode(bitstream)

        with open(output_file_name,"wb") as fil:
            fil.write(bitstream)
