#!/bin/sh
COVERAGE_FILE='.coverage.unit' coverage run --branch --source 'test,voicechat_modem_dsp' -m pytest -v -m unit
test_status_unit=$?
COVERAGE_FILE='.coverage.property' coverage run --branch --source 'test,voicechat_modem_dsp' -m pytest -v -m property
test_status_property=$?
coverage combine
coverage report -m
coverage xml -i
if [ $test_status_unit -eq 0 ] && [ $test_status_property -eq 0 ]; then
    exit 0
else
    exit 1
fi

