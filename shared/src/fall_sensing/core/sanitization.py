"""
Sanitization utilities for raw CSI amplitude data.

Implements:
    - Hampel filter: robust outlier removal using median absolute deviation
    - Linear interpolation: gap-fill after masking corrupted samples
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def hampel_filter(
    signal: NDArray[np.float64],
    window_size: int = 5,
    n_sigma: float = 3.0,
) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    """
    Apply the Hampel identifier to detect and replace outliers.

    Parameters
    ----------
    signal : ndarray of shape (N,)
        1-D input signal (e.g., CSI amplitude over time).
    window_size : int
        One-sided half-window length. Full window = 2*window_size + 1.
    n_sigma : float
        Threshold in units of scaled MAD (default 3.0, equivalent to 3-sigma).

    Returns
    -------
    cleaned : ndarray of shape (N,)
        Signal with outlier samples replaced by the local median.
    outlier_mask : bool ndarray of shape (N,)
        True at positions identified as outliers.

    References
    ----------
    Hampel, F. R. (1974). "The influence curve and its role in robust estimation."
    """
    raise NotImplementedError


def linear_interpolate_gaps(
    signal: NDArray[np.float64],
    mask: NDArray[np.bool_],
) -> NDArray[np.float64]:
    """
    Replace masked (invalid) samples with linear interpolation.

    Parameters
    ----------
    signal : ndarray of shape (N,)
        Input signal possibly containing NaNs or flagged samples.
    mask : bool ndarray of shape (N,)
        True at positions to be interpolated.

    Returns
    -------
    interpolated : ndarray of shape (N,)
        Signal with masked regions linearly interpolated from neighbours.
    """
    raise NotImplementedError
