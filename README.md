# voicechat-modem-dsp

`voicechat-modem` is an implementation of an audio modem communication program that transmits data over a voice/audio channel. The goal is to allow for data transmission and normal speaking over a voice channel simultaneously such that human communication will not interfere with the data transmission.

This is the DSP portion of `voicechat-modem` which modulates and demodulates data. It will write audio to an audio file, and eventually, use a protobuf communication channel to communicate with other programs to allow for live data transmission and receiving.
