from voicechat_modem_dsp.cli.config_loader import parse_config_str, \
    construct_modulators
from voicechat_modem_dsp.cli.command_utils import CLIError, ExtendedCommand
from voicechat_modem_dsp.modulators import ASKModulator, PSKModulator, \
    QAMModulator, FSKModulator
from .testing_utils import DirectoryChanger, FileCleanup

import glob
from strictyaml import YAMLValidationError

import pytest

@pytest.mark.unit
def test_load_doc_examples():
    with DirectoryChanger("docs/specs/examples"):
        for yaml_file in glob.iglob("*.yaml"):
            with open(yaml_file,"r") as fil:
                config_text=fil.read()
            # YAML is valid <=> no error in parsing
            config_obj=parse_config_str(config_text)
            modulator_list=construct_modulators(config_obj.data)

            # TODO: remove length check once FDM is in place
            assert len(modulator_list)==1
            # TODO: complete for other modes once done
            if "ask" in yaml_file:
                assert isinstance(modulator_list[0],ASKModulator)
            elif "fsk" in yaml_file:
                assert isinstance(modulator_list[0],FSKModulator)
            elif "psk" in yaml_file:
                assert isinstance(modulator_list[0],PSKModulator)
            elif "qam" in yaml_file:
                assert isinstance(modulator_list[0],QAMModulator)
            else:
                raise ValueError("Invalid modulator type in examples!") # pragma: no cover

@pytest.mark.unit
def test_load_doc_examples_staticmethod():
    with DirectoryChanger("docs/specs/examples"):
        for yaml_file in glob.iglob("*.yaml"):
            # YAML is valid <=> no error in parsing
            config_obj=ExtendedCommand.parse_config_file(yaml_file)
            modulator_list=construct_modulators(config_obj.data)

            # TODO: remove length check once FDM is in place
            assert len(modulator_list)==1
            # TODO: complete for other modes once done
            if "ask" in yaml_file:
                assert isinstance(modulator_list[0],ASKModulator)
            elif "fsk" in yaml_file:
                assert isinstance(modulator_list[0],FSKModulator)
            elif "psk" in yaml_file:
                assert isinstance(modulator_list[0],PSKModulator)
            elif "qam" in yaml_file:
                assert isinstance(modulator_list[0],QAMModulator)
            else:
                raise ValueError("Invalid modulator type in examples!") # pragma: no cover

@pytest.mark.unit
def test_load_doc_nonexamples():
    with DirectoryChanger("docs/specs/nonexamples"):
        for yaml_file in glob.iglob("*.yaml"):
            with open(yaml_file,"r") as fil:
                config_text=fil.read()
            # Just make sure this causes an error
            # See TODO notice as to why not check error message contents
            with pytest.raises(YAMLValidationError):
                config_obj=parse_config_str(config_text)

@pytest.mark.unit
def test_load_doc_nonexamples_staticmethod():
    with DirectoryChanger("docs/specs/nonexamples"):
        for yaml_file in glob.iglob("*.yaml"):
            # Just make sure this causes an error
            # See TODO notice as to why not check error message contents
            with pytest.raises(CLIError):
                config_obj=ExtendedCommand.parse_config_file(yaml_file)
