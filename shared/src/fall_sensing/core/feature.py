"""
Feature extraction from sanitized CSI amplitude sequences.

Implements:
    - PCA-based subspace projection for CSI stream dimensionality reduction
    - DWT (Discrete Wavelet Transform) energy features per decomposition level
    - CWT (Continuous Wavelet Transform) energy features across scale bands
"""
from __future__ import annotations

import numpy as np
import pywt
from numpy.typing import NDArray
from sklearn.decomposition import PCA


def pca_reduce(
    csi_matrix: NDArray[np.float64],
    n_components: int = 3,
) -> tuple[NDArray[np.float64], PCA]:
    """
    Project a multi-antenna CSI amplitude matrix onto its principal components.

    Parameters
    ----------
    csi_matrix : ndarray of shape (T, n_subcarriers)
        Time-series of CSI amplitudes across subcarriers/antennas.
    n_components : int
        Number of principal components to retain.

    Returns
    -------
    projected : ndarray of shape (T, n_components)
        Dimensionality-reduced representation.
    pca_model : sklearn.decomposition.PCA
        Fitted PCA model (retains explained_variance_ratio_ etc.).
    """
    raise NotImplementedError


def dwt_energy_features(
    signal: NDArray[np.float64],
    wavelet: str = "db4",
    level: int = 4,
) -> NDArray[np.float64]:
    """
    Compute per-level energy from a Discrete Wavelet Transform decomposition.

    Parameters
    ----------
    signal : ndarray of shape (N,)
        1-D input signal.
    wavelet : str
        PyWavelets wavelet name (default 'db4' = Daubechies 4).
    level : int
        Number of decomposition levels.

    Returns
    -------
    energies : ndarray of shape (level + 1,)
        Energy (sum of squared coefficients) for each level:
        [approx_L, detail_L, detail_{L-1}, ..., detail_1].
    """
    raise NotImplementedError


def cwt_energy_features(
    signal: NDArray[np.float64],
    scales: NDArray[np.float64] | None = None,
    wavelet: str = "morl",
) -> NDArray[np.float64]:
    """
    Compute scale-band energies from a Continuous Wavelet Transform.

    Parameters
    ----------
    signal : ndarray of shape (N,)
        1-D input signal.
    scales : ndarray or None
        Scales to analyse. Defaults to np.arange(1, 128).
    wavelet : str
        PyWavelets CWT wavelet name (default 'morl' = Morlet).

    Returns
    -------
    energies : ndarray of shape (len(scales),)
        Energy at each CWT scale.
    """
    raise NotImplementedError
