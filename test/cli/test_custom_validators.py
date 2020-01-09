from voicechat_modem_dsp.cli.yaml_schema_validators import Complex

from strictyaml import Map, Str, YAMLValidationError, load

import pytest

complex_schema=Map({"complex": Complex()})

def generate_yaml(val):
    return "complex: {}".format(val)

@pytest.mark.unit
def test_complex_cartesian_valid():
    yaml_str=generate_yaml(1+1j)
    yaml_obj=load(yaml_str,schema=complex_schema)
    assert yaml_obj["complex"].data==1+1j
    yaml_str_2=generate_yaml("(1,0.5)")
    yaml_obj_2=load(yaml_str_2,schema=complex_schema)
    assert yaml_obj_2["complex"].data.real==-1

@pytest.mark.unit
def test_complex_invalid():
    yaml_str_garbage=generate_yaml("garbage")
    with pytest.raises(YAMLValidationError):
        yaml_obj=load(yaml_str_garbage,schema=complex_schema)
    yaml_str_bad_paren=generate_yaml("(aa,bb)")
    with pytest.raises(YAMLValidationError):
        yaml_obj=load(yaml_str_bad_paren,schema=complex_schema)