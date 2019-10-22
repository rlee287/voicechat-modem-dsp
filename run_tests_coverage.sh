#!/bin/sh
coverage run --branch --source 'test,voicechat_modem_dsp' -m pytest
coverage report -m
