"""
fall_sensing.server
-------------------
FastAPI application for the CSI fall detection service layer.

Components:
    main_api           -- REST endpoints: alerts, device registry, health
    materialized_cron  -- Scheduled job to refresh PostgreSQL materialized views
"""
