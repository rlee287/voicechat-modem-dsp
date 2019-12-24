# Stubs for modulators.modulator_utils (Python 3)

from typing import Any

def generate_timearray(fs: float, sample_count: int): ...
def samples_per_symbol(fs: float, baud: float) -> float: ...
def previous_resample_interpolate(timeseq: Any, baud: float, sequence: Any): ...
def average_interval_data(data: Any, begin: float, end: float) -> float: ...

def gaussian_window(fs: float, sigma_dt: float): ...
def fred_harris_fir_tap_count(fs: float, transition_width: float, db_attenuation: float) -> int: ...
def lowpass_fir_filter(fs: float, cutoff_low: float, cutoff_high: float, attenuation: float = ...): ...

def linearize_fir(filter: Any) -> None: ...
