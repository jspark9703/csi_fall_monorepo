"""
fall_sensing.infra
------------------
MQTT ingestion layer for raw CSI frames from ESP32/Raspberry Pi sensors.

Responsibilities:
    - Subscribe to broker topics for CSI data streams
    - Parse and validate incoming payloads
    - Route validated frames to AWS S3 Data Lake partitions
"""
