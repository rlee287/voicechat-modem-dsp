from voicechat_modem_dsp.cli.config_loader import parse_config_str

import glob
import os
import pprint

import pytest

@pytest.mark.unit
def test_load_doc_examples():
    os.chdir("docs/specs")
    for yaml_file in glob.iglob("*.yaml"):
        with open(yaml_file,"r") as fil:
            config_text=fil.read()
        # Just make sure this doesn't cause an error
        config_obj=parse_config_str(config_text)
        pprint.pprint(config_obj.data)