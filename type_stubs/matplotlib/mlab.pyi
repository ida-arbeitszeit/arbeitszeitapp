from _typeshed import Incomplete
from matplotlib import cbook as cbook

def window_hanning(x): ...
def window_none(x): ...
def detrend(x, key: Incomplete | None = None, axis: Incomplete | None = None): ...
def detrend_mean(x, axis: Incomplete | None = None): ...
def detrend_none(x, axis: Incomplete | None = None): ...
def detrend_linear(y): ...
def psd(
    x,
    NFFT: Incomplete | None = None,
    Fs: Incomplete | None = None,
    detrend: Incomplete | None = None,
    window: Incomplete | None = None,
    noverlap: Incomplete | None = None,
    pad_to: Incomplete | None = None,
    sides: Incomplete | None = None,
    scale_by_freq: Incomplete | None = None,
): ...
def csd(
    x,
    y,
    NFFT: Incomplete | None = None,
    Fs: Incomplete | None = None,
    detrend: Incomplete | None = None,
    window: Incomplete | None = None,
    noverlap: Incomplete | None = None,
    pad_to: Incomplete | None = None,
    sides: Incomplete | None = None,
    scale_by_freq: Incomplete | None = None,
): ...

complex_spectrum: Incomplete
magnitude_spectrum: Incomplete
angle_spectrum: Incomplete
phase_spectrum: Incomplete

def specgram(
    x,
    NFFT: Incomplete | None = None,
    Fs: Incomplete | None = None,
    detrend: Incomplete | None = None,
    window: Incomplete | None = None,
    noverlap: Incomplete | None = None,
    pad_to: Incomplete | None = None,
    sides: Incomplete | None = None,
    scale_by_freq: Incomplete | None = None,
    mode: Incomplete | None = None,
): ...
def cohere(
    x,
    y,
    NFFT: int = 256,
    Fs: int = 2,
    detrend=...,
    window=...,
    noverlap: int = 0,
    pad_to: Incomplete | None = None,
    sides: str = "default",
    scale_by_freq: Incomplete | None = None,
): ...

class GaussianKDE:
    dataset: Incomplete
    covariance_factor: Incomplete
    factor: Incomplete
    data_covariance: Incomplete
    data_inv_cov: Incomplete
    covariance: Incomplete
    inv_cov: Incomplete
    norm_factor: Incomplete
    def __init__(self, dataset, bw_method: Incomplete | None = None) -> None: ...
    def scotts_factor(self): ...
    def silverman_factor(self): ...
    covariance_factor = scotts_factor
    def evaluate(self, points): ...
    __call__ = evaluate
