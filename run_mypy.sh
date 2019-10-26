#!/bin/sh
cd voicechat_modem_dsp || exit 1
mypy -p encoders -p modulators
test_status=$?
cd .. || exit 1
exit $test_status
