"""
Evidently DataDrift 리포트 생성 + W&B Artifact 로깅.

run.log_artifact()로 HTML 리포트를 W&B에 업로드하면
모델 Run과 드리프트 리포트 간 계보가 콘솔에서 시각화됨.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import wandb
from evidently.column_mapping import ColumnMapping
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

logger = logging.getLogger(__name__)


def build_drift_report(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    column_mapping: Optional[ColumnMapping] = None,
    output_path: Optional[Path] = None,
) -> dict:
    """
    Run Evidently DataDrift on reference vs. current feature distributions.

    Parameters
    ----------
    reference_df : pd.DataFrame
        Feature matrix from the training/reference period.
    current_df : pd.DataFrame
        Feature matrix from the current production window.
    column_mapping : ColumnMapping or None
        Evidently column roles (target, prediction, features).
    output_path : Path or None
        If provided, save HTML report to this path.

    Returns
    -------
    result : dict
        Evidently JSON-serializable report result with drift metrics.
    """
    raise NotImplementedError


def main() -> None:
    """CLI entry point for batch drift monitoring job."""
    logging.basicConfig(level=logging.INFO)

    run = wandb.init(project="csi-fall-detection", job_type="drift-monitor")

    ref_path = Path(os.getenv("REFERENCE_DATA", "data/reference.parquet"))
    cur_path = Path(os.getenv("CURRENT_DATA", "data/current.parquet"))
    out_path = Path(os.getenv("REPORT_OUTPUT", "data/drift_report.html"))

    logger.info("Loading reference data from %s", ref_path)
    logger.info("Loading current data from %s", cur_path)

    reference_df = pd.read_parquet(ref_path)
    current_df = pd.read_parquet(cur_path)
    result = build_drift_report(reference_df, current_df, output_path=out_path)

    logger.info("Drift report: %s", result)

    artifact = wandb.Artifact("drift_report", type="report")
    artifact.add_file(str(out_path))
    run.log_artifact(artifact)
    run.finish()


if __name__ == "__main__":
    main()
