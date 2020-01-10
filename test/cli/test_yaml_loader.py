from voicechat_modem_dsp.cli.config_loader import parse_config_str

import glob
import os
from strictyaml import YAMLValidationError

import pytest

class DirectoryChanger:
    def __init__(self, path):
        self.oldpath=os.getcwd()
        self.path=path
    
    def __enter__(self):
        os.chdir(self.path)
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.oldpath)

@pytest.mark.unit
def test_load_doc_examples():
    with DirectoryChanger("docs/specs/examples"):
        for yaml_file in glob.iglob("*.yaml"):
            with open(yaml_file,"r") as fil:
                config_text=fil.read()
            # Just make sure this doesn't cause an error
            config_obj=parse_config_str(config_text)

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