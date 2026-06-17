"""
DVC stage: raw CSI data → DWT/PCA feature matrix.

dvc.yaml의 deps로 shared core 함수를 직접 참조하므로
sanitization.py / feature.py 변경 시 자동 재실행됨.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import yaml

from fall_sensing.core.sanitization import hampel_filter, linear_interpolate_gaps
from fall_sensing.core.feature import dwt_energy_features, pca_reduce

logger = logging.getLogger(__name__)


def main() -> None:
    """DVC entry point: load params, process raw data, save features."""
    params_path = Path("apps/research/params.yaml")
    if not params_path.exists():
        params_path = Path("params.yaml")

    params = yaml.safe_load(params_path.read_text())

    logger.info("Preprocessing configuration: %s", params["preprocessing"])
    logger.info("Feature extraction configuration: %s", params["feature"])

    raise NotImplementedError("DVC pipeline stub — implement data loading and processing")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
