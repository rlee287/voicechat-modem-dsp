#!/bin/sh
coverage run --source 'test,voicechat_modem_dsp' -m pytest
coverage report -m
