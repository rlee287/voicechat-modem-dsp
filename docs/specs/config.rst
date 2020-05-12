Specification of the Configuration File (Version 0.1)
=====================================================

The configuration file is written using the `StrictYaml <https://hitchdev.com/strictyaml/>`_ subset of YAML.

The configuration file first specifies the config file version (``version``),
the sampling rate (``fs``), and the error correction code to use.
After this, the config file specifies the modulation modes
along with their parameters under the ``modulators`` key.

Error Correction Codes
----------------------

The Error Correction Code (ECC) is set with the ``ecc`` key.
Supported Error Correction Codes:

- None (``none`` or ``raw``)
- Hamming (7,4) (``hamming_7_4``)

Modulation Modes
----------------

Modulation modes are set by the ``modulators`` key, underneath which
is a list of modulators, starting with the ``mode`` key that specifies
the modulation mode and followed by mode specific parameters.
The value of the ``mode`` key must be a supported modulation mode.

Supported modulation modes are

- Amplitude Shift Keying (``ask``)
- Frequency Shift Keying (``fsk``)
- Phase Shift Keying (``psk``)
- Quadrature Amplitude Modulation (``qam``)

Amplitude Shift Keying
~~~~~~~~~~~~~~~~~~~~~~

The parameters for the ``ask`` mode are as follows:

- ``baud:`` The symbol rate
- ``carrier:`` The carrier frequency
- ``amplitudes:`` A list of amplitudes between 0 and 1

Phase Shift Keying
~~~~~~~~~~~~~~~~~~

The parameters for the ``psk`` mode are as follows:

- ``baud:`` The symbol rate
- ``carrier:`` The carrier frequency
- ``phases:`` A list of phases between 0 and 1 (internally multiplied by 2π)

Quadrature Amplitude Modulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The parameters for the ``qam`` mode are as follows:

- ``baud:`` The symbol rate
- ``carrier:`` The carrier frequency
- ``constellation:`` A list of constellation points, specified either as
  ``{re}(+/-){im}i`` or as ``({amp}, {phase})``

.. note::
    When specifying points in Cartesian form, the imaginary component
    must *always* be included as a number followed by the literal "i".

Frequency Shift Keying
~~~~~~~~~~~~~~~~~~~~~~

The parameters for the ``fsk`` mode are as follows:

- ``baud:`` The symbol rate
- ``amplitude:`` The amplitude of the signal
- ``frequencies:`` A list of frequencies between 0 and the Nyquist limit

Example Files
-------------

`Bell 202 <https://en.wikipedia.org/wiki/Bell_202_modem>`_ FSK Modulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/fsk_bell_202.yaml
    :language: yaml

1024 bits/second ASK Modulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/ask_1k.yaml
    :language: yaml

31.25 baud PSK
~~~~~~~~~~~~~~

This modulation is similar to the amateur radio PSK31 mode. However, it uses
a more rudimentary Hamming 7,4 ECC and Gaussian pulse shaping, as opposed to
a raised cosine filter and more advanced ECC methods.

.. literalinclude:: examples/psk31.yaml
    :language: yaml

2048 bits/second QAM Modulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/qam_1k.yaml
    :language: yaml