"""
fall_sensing.research
---------------------
Model training and MLOps tooling for CSI-based fall detection.

Components:
    preprocess     -- DVC stage: raw CSI → DWT/PCA features
    train          -- DVC stage: features → model + W&B Artifact logging
    drift_monitor  -- Evidently + W&B drift report generation
"""
