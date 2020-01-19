import cleo

from voicechat_modem_dsp.cli.command_utils import \
    ExtendedCommand, FileExistsAndCannotOverwriteException

from .testing_utils import MockIO
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
def test_file_extendedcmd_interactive():
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
