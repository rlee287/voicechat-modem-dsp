import cleo

from voicechat_modem_dsp.cli.command_utils import \
    ExtendedCommand, FileExistsAndCannotOverwriteException
from voicechat_modem_dsp.cli.command_objects import TxFile, RxFile
from .testing_utils import MockIO, FileCleanup
import glob
import os

import pytest

@pytest.mark.unit
def test_extendedcmd_noninteractive():
    extended_cmd = ExtendedCommand()
    extended_cmd._io = MockIO(is_interactive=False,input_list=list())

    # Can write to nonexistent file
    extended_cmd.confirm_file_writable("garbage")
    # Cannot write to existent file in noninteractive mode
    with pytest.raises(FileExistsAndCannotOverwriteException):
        extended_cmd.confirm_file_writable("__init__.py")

    # Cannot write to directory
    try:
        os.mkdir("nonsense")
        with pytest.raises(FileExistsAndCannotOverwriteException):
            extended_cmd.confirm_file_writable("nonsense")
    finally:
        os.rmdir("nonsense")

@pytest.mark.unit
def test_extendedcmd_interactive():
    extended_cmd = ExtendedCommand()
    extended_cmd._io = MockIO(is_interactive=True, input_list=[False])

    # Can write to nonexistent file
    extended_cmd.confirm_file_writable("garbage")
    # Cannot write to directory
    try:
        os.mkdir("nonsense")
        with pytest.raises(FileExistsAndCannotOverwriteException):
            extended_cmd.confirm_file_writable("nonsense")
    finally:
        os.rmdir("nonsense")

    # Cannot write to existent file when nonconfirmed
    with pytest.raises(FileExistsAndCannotOverwriteException):
        extended_cmd.confirm_file_writable("__init__.py")

    # Can write to existent file when confirmed
    extended_cmd._io = MockIO(is_interactive=True, input_list=[True])
    extended_cmd.confirm_file_writable("__init__.py")

@pytest.mark.unit
def test_roundtrip_modulation_cmd():
    configs_valid=glob.glob("docs/specs/examples/*.yaml")
    file_input="mypy.ini"
    for config in configs_valid:
        with FileCleanup("modulated.wav"):
            with FileCleanup("demodulated.dat"):
                application = cleo.Application()
                application.add(TxFile())
                application.add(RxFile())
                tx_commands=" ".join(["--config "+config,
                    "--output modulated.wav","--raw",file_input])

                command_tx = application.find("transmit_file")
                command_tx_tester = cleo.CommandTester(command_tx)
                command_tx_tester.execute(tx_commands)

                assert command_tx_tester.status_code == 0

                rx_commands=" ".join(["--config "+config,
                    "--output demodulated.dat","modulated.wav"])
                command_rx = application.find("receive_file")
                command_rx_tester = cleo.CommandTester(command_rx)
                command_rx_tester.execute(rx_commands)

                assert command_rx_tester.status_code == 0

@pytest.mark.unit
def test_improper_file_parameters():
    application = cleo.Application()
    application.add(TxFile())
    application.add(RxFile())
    tx_command_no_config=" ".join(["--output modulated.wav","--raw",
        "test/cli/testing_utils.py"])
    tx_command_config_nonexist=" ".join(["--output modulated.wav","--raw",
        "--config nonexist","test/cli/testing_utils.py"])
    tx_command_input_nonexist=" ".join([
        "--config docs/specs/examples/ask_1k.yaml", "--output modulated.wav",
        "--raw","nonexist"])

    command_tx = application.find("transmit_file")
    command_tx_tester = cleo.CommandTester(command_tx)

    command_tx_tester.execute(tx_command_no_config)
    assert command_tx_tester.status_code == 1

    command_tx_tester.execute(tx_command_config_nonexist)
    assert command_tx_tester.status_code == 1

    command_tx_tester.execute(tx_command_input_nonexist)
    assert command_tx_tester.status_code == 1

    rx_command_no_config=" ".join(["--output demodulated.dat","input.wav"])
    rx_command_config_nonexist=" ".join(["--output demodulated.dat",
        "--config nonexist","input.wav"])
    rx_command_input_nonexist=" ".join([
        "--config docs/specs/examples/ask_1k.yaml", "--output demodulated.dat",
        "nonexist.wav"])

    command_rx = application.find("receive_file")
    command_rx_tester = cleo.CommandTester(command_rx)

    command_rx_tester.execute(rx_command_no_config)
    assert command_rx_tester.status_code == 1

    command_rx_tester.execute(rx_command_config_nonexist)
    assert command_rx_tester.status_code == 1

    command_rx_tester.execute(rx_command_input_nonexist)
    assert command_rx_tester.status_code == 1
