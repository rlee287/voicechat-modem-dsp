# Stubs for modulators.modulator_ask (Python 3)

from .modulator_base import Modulator
from typing import Sequence, Dict, Tuple

from numpy import ndarray

class ASKModulator(Modulator):
    fs: float = ...
    amp_list: Dict[int, float] = ...
    carrier_freq: float = ...
    baud: float = ...
    def __init__(self, fs: float, carrier: float,
            amp_list: Sequence[float], baud: float) -> None: ...
    def modulate(self, datastream: Sequence[int]) -> ndarray: ...
    def demodulate(self, modulated_data: ndarray) -> Sequence[int]: ...
