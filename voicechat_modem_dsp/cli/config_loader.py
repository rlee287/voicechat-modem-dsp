# Import the schema types first, and then the actual loading stuff
from strictyaml import Map, Str, Float, Enum, Any, UniqueSeq, CommaSeparated
from strictyaml import load, YAML, YAMLValidationError

from .yaml_schema_validators import Complex
from ..modulators import ASKModulator, PSKModulator, QAMModulator, \
    FSKModulator, BaseModulator

from typing import List as TypingList
from typing import Mapping as TypingMap

from numpy import pi

init_config_schema=Map({
    "version": Str(),
    "fs": Float(),
    "ecc": Enum(["none","raw","hamming_7_4"]),
    "modulators": Any()
})

ask_schema=Map({
    "baud": Float(),
    "mode": Enum(["ask"]),
    "carrier": Float(),
    "amplitudes": UniqueSeq(Float()) | CommaSeparated(Float())
})
psk_schema=Map({
    "baud": Float(),
    "mode": Enum(["psk"]),
    "carrier": Float(),
    "phases": UniqueSeq(Float()) | CommaSeparated(Float())
})
qam_schema=Map({
    "baud": Float(),
    "mode": Enum(["qam"]),
    "carrier": Float(),
    "constellation": UniqueSeq(Complex()) | CommaSeparated(Complex())
})
fsk_schema=Map({
    "baud": Float(),
    "mode": Enum(["fsk"]),
    "amplitude": Float(),
    "frequencies": UniqueSeq(Float()) | CommaSeparated(Float())
})

# TODO: more informative ValidationError messages
# This is partially due to underdocumented libraries
def parse_config_str(string: str) -> YAML:
    config_obj=load(string,init_config_schema)
    # TODO: check version number
    if config_obj["fs"].data<=0:
        raise YAMLValidationError("Sampling frequency must be positive",
            None,config_obj["fs"])
    if not config_obj["modulators"].is_sequence():
        raise YAMLValidationError("Modulators must be a list of modulators",
            None,config_obj["modulators"])
    for index,modulator in enumerate(config_obj["modulators"]):
        for potential_validator in [ask_schema,psk_schema,qam_schema,
                fsk_schema]:
            try:
                modulator.revalidate(potential_validator)
                break
            except YAMLValidationError:
                continue
        else: # No validator matched
            raise YAMLValidationError("Invalid modulator found "
                "in modulator list",None,modulator)
    return config_obj

def construct_modulators(config_dict: TypingMap) -> TypingList[BaseModulator]:
    fs=config_dict["fs"]
    modulator_list=list() # type: TypingList[BaseModulator]
    for modulator_config in config_dict["modulators"]:
        baud=modulator_config["baud"]
        mode=modulator_config["mode"]
        if mode=="ask":
            carrier=modulator_config["carrier"]
            amplitudes=modulator_config["amplitudes"]
            modulator_list.append(ASKModulator(fs, carrier, amplitudes, baud))
        elif mode=="psk":
            carrier=modulator_config["carrier"]
            phases=modulator_config["phases"]
            phases=[2*pi*phase for phase in phases]
            modulator_list.append(PSKModulator(fs, carrier, 1, phases, baud))
        elif mode=="qam":
            carrier=modulator_config["carrier"]
            constellation=modulator_config["constellation"]
            modulator_list.append(QAMModulator(fs, carrier, constellation, baud))
        elif mode=="fsk":
            amplitude=modulator_config["amplitude"]
            frequencies=modulator_config["frequencies"]
            modulator_list.append(
                FSKModulator(fs, amplitude, frequencies, baud))
        else: # Should never happen (would have been caught by revalidation)
            raise ValueError("Mapping has invalid mode key") # pragma: no cover
    return modulator_list
