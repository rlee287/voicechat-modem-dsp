#!/bin/sh
coverage run --branch --source 'test,voicechat_modem_dsp' -m pytest
test_status=$?
coverage report -m
exit $test_status