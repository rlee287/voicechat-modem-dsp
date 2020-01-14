#!/bin/sh
#cd voicechat_modem_dsp || exit 1

MYPYPATH=voicechat_modem_dsp/stubs mypy -p voicechat_modem_dsp
test_status=$?

#cd .. || exit 1
exit $test_status
