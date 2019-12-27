Specification of the Configuration File
=======================================

The configuration file is written using the `StrictYaml <https://hitchdev.com/strictyaml/>`_ subset of YAML.

The configuration file first specifies the sampling rate and the error correction code to use. After this, the config file specifies modulation mode specific parameters.

Error Correction Codes
----------------------

Error Correction Code (ECC) choice is set with the ``ecc:`` key.
Supported Error Correction Codes:

- None (``none`` or ``raw``)
- Hamming (7,4) (``hamming_7_4``)

Modulation Modes
----------------

Modulation modes are set by including one of the keys named below.
Supported modulation modes:

- Amplitude Shift Keying (``ask``)

Modes that will be supported in the future:

- Phase Shift Keying (``psk``)
- Quadrature Amplitude Modulation (``qam``)
- Frequency Shift Keying (``fsk``)

Amplitude Shift Keying
~~~~~~~~~~~~~~~~~~~~~~

The parameters for the ``ask`` key are as follows:

- ``carrier:`` The carrier frequency
- ``amplitudes:`` A list of amplitudes between 0 and 1
- ``baud:`` The symbol rate

Phase Shift Keying
~~~~~~~~~~~~~~~~~~

The parameters for the ``psk`` key are as follows:

- ``carrier:`` The carrier frequency
- ``phases:`` A list of phases between 0 and 1 (internally multiplied by 2π)
- ``baud:`` The symbol rate