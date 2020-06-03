#!/bin/sh
# There may be warnings about "no data collected", but this seems to work correctly
# Only parallelize long property tests for now
# A cmd unit test needs refactoring to resolve filesystem races first
pytest --cov=voicechat_modem_dsp --cov=test --cov-report= --cov-branch -n auto -v -m unit
test_status_unit=$?
pytest --cov=voicechat_modem_dsp --cov=test --cov-report= --cov-branch --cov-append -n auto -v -m property
test_status_property=$?
coverage report
coverage xml -i
if [ $test_status_unit -eq 0 ] && [ $test_status_property -eq 0 ]; then
    exit 0
else
    exit 1
fi

