# CSI Fall Detection Monorepo Architecture

## 전체 구조

```
csi_fall_monorepo/
├── pyproject.toml (uv workspace root)
├── uv.lock (282 packages)
├── .gitignore / .dockerignore
├── ARCHITECTURE.md (this file)
│
├── shared/
│   └── fall-sensing-core
│       ├── Signal preprocessing: Hampel filter, linear interpolation
│       └── Feature extraction: PCA, DWT/CWT energy features
│
└── apps/
    ├── infrastructure/
    │   └── fall-sensing-infrastructure
    │       ├── MQTT → S3 Data Lake ingestion
    │       └── CSI sensor stream validation
    │
    ├── service/
    │   └── fall-sensing-service
    │       ├── FastAPI REST backend
    │       ├── MongoDB event log
    │       └── PostgreSQL materialized views (CronJob)
    │
    └── research/
        ├── acf_cwt/ (ACF + CWT variant)
        │   └── fall-sensing-research-acf_cwt
        │       ├── DVC: data/features/model versioning
        │       └── Jupyter notebooks for analysis
        │
        └── combined_feature/ (Combined features variant)
            └── fall-sensing-research-combined
                ├── DVC: data/features/model versioning
                └── Jupyter notebooks for analysis
```

---

## 역할 분담: DVC vs W&B

### DVC (Data Version Control) — 데이터 & 파이프라인 버저닝

**용도**: `data/`, `features/`, `models/` 파일 버전 관리

**Remote**: Google Drive (`.dvc/config` 참조)
```ini
[remote "gdrive-dvc"]
    url = gdrive://<GDRIVE_FOLDER_ID>
```

**파이프라인 캐싱** (dvc.yaml):
```yaml
stages:
  preprocess:
    cmd: python -m fall_sensing.research.preprocess
    deps:
      - src/fall_sensing/research/preprocess.py
      - ../../shared/src/fall_sensing/core/sanitization.py  # shared core 변경 시 자동 재실행
    outs:
      - data/processed/features.npz:  # Google Drive에 캐시됨
          cache: true

  train:
    deps:
      - data/processed/features.npz
    outs:
      - data/models/best_model.pt:
          cache: true
    metrics:
      - data/metrics.json:
          cache: false  # 매번 덮어쓰기 (매트릭 추적 용)
```

**사용 예시**:
```bash
cd apps/research/acf_cwt

# 데이터 로드
dvc pull

# 파이프라인 실행 (shared core 변경 시 자동 감지)
dvc repro

# Google Drive에 아티팩트 푸시
dvc push

# 브랜치 전환 후 자동 스와핑
git checkout feature-dwt-level5
dvc checkout  # 해당 브랜치의 features.npz로 자동 변경
```

---

### W&B (Weights & Biases) — 선택적 실험 추적

**용도**: 세부 실험 단위에서만 *선택적으로* 실행

**특징**:
- DVC 파이프라인 밖에서 독립적으로 실행
- 환경 변수 `WANDB_ENABLED=true`로 활성화
- 기본값: `False` (DVC 파이프라인만 실행)

**train.py 함수 시그니처**:
```python
def main(params: Optional[dict] = None, use_wandb: bool = False) -> None:
    """
    Entry point: load data, build model, run training loop.

    Parameters
    ----------
    use_wandb : bool
        Enable W&B tracking (default: False).
        Can also be controlled via WANDB_ENABLED env var.
    """
    use_wandb = use_wandb or os.getenv("WANDB_ENABLED", "").lower() == "true"

    if use_wandb:
        run = wandb.init(project="csi-fall-detection", config=params)
        logger.info("W&B run initialized: %s", run.id)
    else:
        logger.info("W&B disabled (set WANDB_ENABLED=true to enable)")
        run = None
```

**사용 예시**:
```bash
# DVC만 사용 (기본값, 빠름)
cd apps/research/acf_cwt
dvc repro

# W&B 포함 실험 (세부 추적 필요할 때만)
WANDB_ENABLED=true WANDB_API_KEY=<key> python -m fall_sensing.research.train

# Jupyter에서 선택적 실험
import os
os.environ["WANDB_ENABLED"] = "true"
from fall_sensing.research.train import main
main(use_wandb=True)
```

---

## Workspace Members (uv)

| 패키지 | 경로 | 의존성 | 용도 |
|--------|------|--------|------|
| **fall-sensing-core** | `shared/` | numpy, scipy, pywt, sklearn | 공유 신호처리 |
| **fall-sensing-infrastructure** | `apps/infrastructure/` | paho-mqtt, boto3 | MQTT + S3 |
| **fall-sensing-service** | `apps/service/` | fastapi, motor, psycopg | REST API |
| **fall-sensing-research-acf_cwt** | `apps/research/acf_cwt/` | torch, pandas, dvc[s3], wandb | ACF+CWT 학습 |
| **fall-sensing-research-combined** | `apps/research/combined_feature/` | torch, pandas, dvc[s3], wandb | Combined 학습 |

**Namespace Package**: `from fall_sensing.core.X import Y` (모든 멤버에서 사용 가능)

---

## Implicit Namespace Package (PEP 420)

```
shared/src/fall_sensing/             # NO __init__.py
├── core/                            # HAS __init__.py
│   ├── __init__.py
│   ├── sanitization.py
│   └── feature.py

apps/infrastructure/src/fall_sensing/  # NO __init__.py
└── infra/                             # HAS __init__.py
    ├── __init__.py
    └── mqtt_listener.py
```

**효과**:
- 각 app이 `fall_sensing` namespace를 공유
- `from fall_sensing.core.X import Y` 모든 곳에서 작동
- namespace root에 `__init__.py` 없어야 merge 가능

---

## 데이터 흐름

### Research Workflow (DVC + Optional W&B)

```
1. Raw CSI data (Google Drive)
   ↓ dvc pull
   
2. shared core functions (sanitization, feature extraction)
   ↓ (모든 variant가 동일한 코어 사용)
   
3. Feature matrix (data/processed/features.npz)
   ↓ dvc cache (Google Drive)
   
4a. DVC Pipeline (기본값)
    └─ dvc repro → data/models/best_model.pt (Google Drive)
    
4b. W&B Experiment (선택적, WANDB_ENABLED=true)
    └─ metrics logged to wandb.com dashboard
    
5. Git branch 전환 후
   └─ dvc checkout → features/models 자동 스와핑
```

---

## Setup & Usage

### 초기 설정

```bash
# 1. Google Drive 폴더 생성 및 folder_id 추출
# 2. .dvc/config 업데이트
dvc remote modify gdrive-dvc --local auth basic

# 3. research 폴더로 이동
cd apps/research/acf_cwt

# 4. DVC 초기화 (첫 작업만)
dvc init --subdir
dvc remote add -d gdrive-dvc "gdrive://<FOLDER_ID>"
```

### 매일 작업

```bash
# DVC 캐시 다운로드
dvc pull

# 파이프라인 실행 (params 또는 shared core 변경 시에만 실행)
dvc repro

# 결과 Google Drive에 푸시
dvc push

# 선택적: W&B로 추적
WANDB_ENABLED=true python -m fall_sensing.research.train
```

---

## Docker 배포

모든 앱은 독립적으로 빌드 가능:

```bash
# shared core 기반 경량 이미지
docker build -f apps/infrastructure/Dockerfile -t fall-sensing-infra:v1 .
docker build -f apps/service/Dockerfile -t fall-sensing-service:v1 .

# GPU 선택 가능
docker build -f apps/research/acf_cwt/Dockerfile \
  --build-arg BASE_IMAGE=python:3.11-slim \
  -t fall-sensing-research-acf_cwt:cpu .

docker build -f apps/research/acf_cwt/Dockerfile \
  --build-arg BASE_IMAGE=nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 \
  -t fall-sensing-research-acf_cwt:gpu .
```

---

## 중요 사항

1. **shared core의 안정성**: 모든 app이 동일한 `sanitization.py`, `feature.py` 사용
   → DVC로 버저닝된 features.npz는 항상 재현 가능

2. **DVC Google Drive Remote**: `dvc.yaml`의 `deps`에 `shared/src/`경로 포함
   → shared core 수정 시 `dvc repro` 자동으로 재실행

3. **W&B 선택적 사용**: 기본 비활성화 → 필요시만 `WANDB_ENABLED=true`
   → DVC 파이프라인 성능 영향 없음

4. **Namespace Package Merge**: 모든 variant가 `fall_sensing.core.*` 공유
   → 코드 중복 제거, 유지보수 효율화

