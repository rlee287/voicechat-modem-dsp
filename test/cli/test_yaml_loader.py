from voicechat_modem_dsp.cli.config_loader import parse_config_str, \
    construct_modulators
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
            # Just make sure this doesn't cause an error
            # TODO: other tests that check specific attributes
            config_obj=parse_config_str(config_text)
            modulator_list=construct_modulators(config_obj.data)
            assert len(modulator_list)==1

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
