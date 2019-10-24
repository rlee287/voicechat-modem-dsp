#!/bin/sh
coverage run --branch --source 'test,voicechat_modem_dsp' -m pytest
test_status=$?
coverage report -m
coverage xml -i
exit $test_status
