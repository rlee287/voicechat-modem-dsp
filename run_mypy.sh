#!/bin/sh
pushd voicechat_modem_dsp
mypy -p encoders -p modulators
test_status=$?
popd
exit $test_status
