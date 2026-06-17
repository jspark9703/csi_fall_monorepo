"""
fall_sensing.core
-----------------
Shared signal processing utilities for CSI-based fall detection.

Provides:
    sanitization  -- Hampel filter and linear interpolation helpers
    feature       -- PCA dimensionality reduction and DWT/CWT energy features
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("fall-sensing-core")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = ["sanitization", "feature"]
