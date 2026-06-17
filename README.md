# CSI Fall Detection Monorepo

CSI(Channel State Information) 기반 낙상 감지 시스템의 통합 개발 환경입니다. **uv** 워크스페이스를 통해 독립적으로 격리된 개발 환경을 제공하면서도 `shared/` 폴더의 공유 핵심 라이브러리로 코드 중복을 제거합니다.

---

## 🚀 개발환경 설정

### 1단계: 저장소 클론 및 uv 설치

```bash
# 저장소 클론
git clone <repository-url>
cd csi_fall_monorepo

# uv 설치 (미설치 시)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2단계: 워크스페이스 초기화

```bash
# 모든 패키지의 의존성 설치 (uv.lock 기반)
uv sync

# 개발 도구도 함께 설치
uv sync --group dev
```

### uv 워크스페이스 구조

이 모노레포는 **uv workspace**를 사용하여 5개의 독립적인 Python 패키지를 관리합니다:

```
pyproject.toml (워크스페이스 루트)
├── [tool.uv.workspace]
│   members = [
│       "shared",                              # 공유 신호처리 라이브러리
│       "apps/infrastructure",                 # MQTT/S3 인프라
│       "apps/service",                        # FastAPI 서비스
│       "apps/research/acf_cwt",              # ACF+CWT 연구 환경
│       "apps/research/combined_feature"       # Combined 연구 환경
│   ]
```

**각 패키지는 독립적인 개발 환경을 가집니다:**

| 패키지 | 경로 | 주요 의존성 | 용도 |
|--------|------|----------|------|
| **fall-sensing-core** | `shared/` | numpy, scipy, pywt, sklearn | 신호처리 및 특성 추출 |
| **fall-sensing-infrastructure** | `apps/infrastructure/` | paho-mqtt, boto3 | MQTT/S3 데이터 수집 |
| **fall-sensing-service** | `apps/service/` | fastapi, motor, psycopg | REST API 서버 |
| **fall-sensing-research-acf_cwt** | `apps/research/acf_cwt/` | torch, pandas, wandb | ACF+CWT 모델 학습 |
| **fall-sensing-research-combined** | `apps/research/combined_feature/` | torch, pandas, wandb | Combined 모델 학습 |

### Namespace Package 공유

모든 패키지는 `fall_sensing` namespace를 공유합니다:

```python
# 어디서나 사용 가능
from fall_sensing.core.sanitization import hampel_filter
from fall_sensing.core.feature import extract_dwt_energy
from fall_sensing.infra.mqtt_listener import MQTTReceiver
from fall_sensing.server.main_api import app
from fall_sensing.research.train import main
```

**설정 원리:**
- `shared/src/fall_sensing/` — `__init__.py` 없음 (namespace root)
- `shared/src/fall_sensing/core/` — `__init__.py` 있음 (subpackage)
- 각 app도 동일한 구조 → Python이 자동으로 namespace 병합

---

## 📁 디렉토리 구조

```
csi_fall_monorepo/
│
├── pyproject.toml              # uv 워크스페이스 설정 (모든 패키지 관리)
├── uv.lock                     # 의존성 잠금 파일 (282개 패키지)
├── ARCHITECTURE.md             # 상세 아키텍처 문서
├── README.md                   # 이 파일
│
├── .dvc/                       # DVC 설정
│   └── config                  # 원격 저장소 (Google Drive)
│
├── .venv/                      # 가상환경 (uv 자동 관리)
│
├── shared/                     # 📚 공유 핵심 라이브러리
│   ├── pyproject.toml          # 패키지 정의 (fall-sensing-core)
│   └── src/fall_sensing/core/
│       ├── __init__.py
│       ├── sanitization.py     # 신호 전처리: Hampel 필터, 선형보간
│       └── feature.py          # 특성 추출: PCA, DWT/CWT 에너지
│
└── apps/                       # 🚀 애플리케이션
    │
    ├── infrastructure/         # MQTT/S3 데이터 수집
    │   ├── pyproject.toml
    │   ├── Dockerfile
    │   └── src/fall_sensing/infra/
    │       ├── __init__.py
    │       └── mqtt_listener.py    # MQTT 센서 스트림 수신 → S3
    │
    ├── service/                # REST API 서버
    │   ├── pyproject.toml
    │   ├── Dockerfile
    │   └── src/fall_sensing/server/
    │       ├── __init__.py
    │       ├── main_api.py          # FastAPI 엔드포인트
    │       └── materialized_cron.py # PostgreSQL 물리화뷰 (CronJob)
    │
    └── research/               # 🔬 모델 연구 (두 가지 특성 비교)
        │
        ├── acf_cwt/            # ACF + CWT 특성 학습
        │   ├── pyproject.toml
        │   ├── Dockerfile
        │   ├── dvc.yaml            # DVC 파이프라인 (전처리 → 학습)
        │   ├── params.yaml         # 하이퍼파라미터
        │   ├── .dvcignore
        │   ├── notebooks/          # Jupyter 분석 노트북
        │   └── src/fall_sensing/research/
        │       ├── __init__.py
        │       ├── preprocess.py    # raw 데이터 → features.npz
        │       ├── train.py         # 모델 학습 (DVC/W&B)
        │       └── drift_monitor.py # 데이터 드리프트 감지
        │
        └── combined_feature/   # Combined 특성 학습
            ├── pyproject.toml
            ├── Dockerfile
            ├── dvc.yaml
            ├── params.yaml
            ├── .dvcignore
            ├── notebooks/
            └── src/fall_sensing/research/
                ├── __init__.py
                ├── preprocess.py
                ├── train.py
                └── drift_monitor.py

```

### 핵심 폴더 설명

| 폴더 | 용도 | 특징 |
|------|------|------|
| **shared/** | 모든 app이 사용하는 신호처리 함수 | `import fall_sensing.core` 공유 |
| **apps/infrastructure/** | MQTT 센서 데이터 수신, S3 저장 | 프로덕션 데이터 수집 파이프라인 |
| **apps/service/** | REST API 백엔드, MongoDB, PostgreSQL | 이벤트 로깅 및 분석 조회 |
| **apps/research/\*/** | 모델 학습 및 실험 | DVC + W&B 추적, Jupyter 분석 |

---

## 🔄 DVC를 이용한 데이터 버전 관리

### DVC 개요

**Data Version Control(DVC)**은 대용량 데이터, 파이프라인, 모델을 Git처럼 관리합니다.

- **데이터 추적**: `data/`, `features/`, `models/` 파일 변경사항 기록
- **파이프라인 캐싱**: 코드나 의존성이 변경되지 않으면 이전 결과 재사용
- **원격 저장소**: Google Drive에 데이터 백업
- **자동 재현성**: shared core 변경 시 파이프라인 자동 재실행

### 초기 설정 (첫 작업만)

#### 1. Google Drive 폴더 생성

```
Google Drive에서 "DVC Cache" 같은 폴더 생성
→ 폴더 공유 링크: https://drive.google.com/drive/folders/{FOLDER_ID}
→ {FOLDER_ID} 복사 (약 33자의 영문+숫자)
```

#### 2. DVC 원격 저장소 설정

```bash
# 워크스페이스 루트에서
dvc remote modify gdrive-dvc --local auth basic

# 각 research 폴더에서 첫 설정만 (subdirectory 초기화)
cd apps/research/acf_cwt
dvc init --subdir
dvc remote add -d gdrive-dvc "gdrive://{FOLDER_ID}"
```

#### 3. `.dvc/config` 확인

`.dvc/config` 파일에 Google Drive 원격이 설정되었는지 확인:

```ini
[core]
    remote = gdrive-dvc
    autostage = true
[remote "gdrive-dvc"]
    url = gdrive://YOUR_FOLDER_ID
```

### 일일 작업 워크플로우

#### 데이터 가져오기

```bash
cd apps/research/acf_cwt
dvc pull  # Google Drive에서 로컬로 캐시 다운로드
```

이 명령어는:
- `dvc.yaml`에서 `cache: true`로 지정된 모든 파일 가져오기
- `features.npz`, `best_model.pt` 등 복원

#### 파이프라인 실행

```bash
dvc repro  # dvc.yaml의 모든 단계 실행
```

**DVC의 똑똑한 캐싱:**

```yaml
stages:
  preprocess:
    cmd: python -m fall_sensing.research.preprocess
    deps:
      - src/fall_sensing/research/preprocess.py
      - ../../shared/src/fall_sensing/core/sanitization.py  # ← 중요!
      - data/raw/
    outs:
      - data/processed/features.npz:
          cache: true
```

- ✅ `sanitization.py` 수정 → `dvc repro`가 자동으로 재실행
- ✅ 코드 미변경 → 이전 캐시 사용 (빠름)
- ✅ 결과 재현성 보장 (매번 동일)

#### 결과 저장

```bash
dvc push  # 로컬 캐시를 Google Drive에 업로드
```

#### 브랜치 전환 시

```bash
git checkout feature-new-model
dvc checkout  # 현재 브랜치의 features.npz로 자동 변경
```

### 파이프라인 구조 예시

```
dvc.yaml 구조:

stages:
  preprocess:
    cmd: python -m fall_sensing.research.preprocess
    deps: [preprocess.py, shared core, data/raw/]
    params: [params.yaml: preprocessing.*, feature.*]
    outs:
      - data/processed/features.npz (cache: true)  ← Google Drive 저장
    
  train:
    cmd: python -m fall_sensing.research.train
    deps: [train.py, data/processed/features.npz]
    params: [params.yaml: train.*]
    outs:
      - data/models/best_model.pt (cache: true)    ← Google Drive 저장
    metrics:
      - data/metrics.json (cache: false)           ← 매번 덮어쓰기
```

### 매개변수 관리 (params.yaml)

각 research 폴더의 `params.yaml`:

```yaml
preprocessing:
  hampel_window: 5
  n_sigma: 3

feature:
  dwt_level: 4
  wavelet: "db4"
  n_pca: 10

train:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
```

**매개변수 변경 후:**

```bash
# params.yaml 수정
dvc repro  # 영향받는 단계만 자동으로 재실행
```

DVC가 자동으로 감지:
- `preprocessing.*` 변경 → preprocess 단계만 재실행
- `train.*` 변경 → train 단계만 재실행
- 의존성 체인을 타고 필요한 모든 단계 갱신

### 실험 추적 (선택적 W&B)

데이터 버전관리는 DVC가 담당하고, 상세한 실험 추적은 **Weights & Biases**로:

```bash
# 기본값: DVC만 사용 (빠름)
dvc repro

# 선택적: W&B로 상세 추적 (metrics, 하이퍼파라미터, 로그 등)
WANDB_ENABLED=true WANDB_API_KEY=<your-key> dvc repro
```

자세한 내용은 [ARCHITECTURE.md](./ARCHITECTURE.md) **W&B** 섹션 참조.

### 유용한 DVC 명령어

```bash
# 파이프라인 상태 확인 (뭐가 캐시되어 있는지)
dvc status

# 특정 출력물의 변경사항 보기
dvc diff --targets data/models/best_model.pt

# 원격 저장소와 동기화 상태 확인
dvc remote status

# DVC 파일 (`.dvc` 메타데이터) 확인
cat data/processed/features.npz.dvc

# 파이프라인 DAG 시각화
dvc dag
```

---

## 🐳 Docker 배포

각 애플리케이션은 독립적으로 도커라이징 가능합니다:

```bash
# 1. Infrastructure (MQTT/S3)
docker build -f apps/infrastructure/Dockerfile -t fall-sensing-infra:v1 .

# 2. Service (REST API)
docker build -f apps/service/Dockerfile -t fall-sensing-service:v1 .

# 3. Research (CPU)
docker build -f apps/research/acf_cwt/Dockerfile \
  --build-arg BASE_IMAGE=python:3.11-slim \
  -t fall-sensing-research-acf_cwt:cpu .

# 4. Research (GPU)
docker build -f apps/research/acf_cwt/Dockerfile \
  --build-arg BASE_IMAGE=nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 \
  -t fall-sensing-research-acf_cwt:gpu .
```

---

## 📊 데이터 흐름

```
Raw CSI Data (센서 수집)
    ↓
[apps/infrastructure] MQTT 리스너 → S3 저장
    ↓
[apps/research] dvc pull → 로컬 다운로드
    ↓
shared/core (공유 전처리 함수)
    ↓
dvc repro (전처리 + 학습)
    ├─ preprocess.py → features.npz (DVC 캐시)
    └─ train.py → best_model.pt (DVC 캐시)
    ↓
dvc push → Google Drive 백업
    ↓
[apps/service] REST API → 결과 조회
```

---

## 🛠️ 개발 도구 및 명령어

### 린팅 및 형식화

```bash
# 코드 스타일 확인 (ruff)
ruff check .

# 자동 수정
ruff check --fix .

# 형식 확인
ruff format --check .

# 자동 포맷팅
ruff format .
```

### 타입 검사

```bash
# mypy 타입 검사
mypy apps/

# 전체 워크스페이스
mypy .
```

### 테스트 실행

```bash
# 모든 테스트
pytest

# 특정 폴더
pytest apps/infrastructure/

# 비동기 테스트 포함
pytest --asyncio-mode=auto
```

### 개발 모드 실행

```bash
# 특정 모듈 실행
python -m fall_sensing.research.preprocess

# 또는 Jupyter 노트북
cd apps/research/acf_cwt
jupyter notebook notebooks/
```

---

## 🤝 협업 가이드

### 기본 워크플로우

```bash
# 1. 최신 상태 가져오기
git pull origin main
uv sync  # 새로운 의존성 있으면 설치

# 2. 피처 브랜치 생성
git checkout -b feature/my-feature

# 3. 코드 작성
# ... 코드 수정 ...

# 4. 린팅/테스트
ruff check --fix .
pytest

# 5. 커밋 및 푸시
git commit -m "feat: describe your change"
git push origin feature/my-feature

# 6. PR 생성 (GitHub)
```

### shared 폴더 수정 시

shared 폴더의 핵심 함수를 수정하면 모든 research 파이프라인이 영향받습니다:

```bash
# shared/src/fall_sensing/core/sanitization.py 수정 후
cd apps/research/acf_cwt
dvc repro  # 자동으로 preprocess 단계 재실행!
```

### DVC로 협업할 때

```bash
# 팀원이 수정한 features.npz 받기
git pull origin feature-branch
dvc pull  # Google Drive에서 최신 features.npz 다운로드

# 로컬 수정 후 공유
dvc push  # Google Drive에 업로드
git add dvc.yaml dvc.lock
git commit -m "data: update training data"
```

---

## 📚 참고 문서

- [ARCHITECTURE.md](./ARCHITECTURE.md) — 상세 아키텍처, DVC 파이프라인, W&B 통합
- [DVC 공식 문서](https://dvc.org/doc)
- [uv 공식 문서](https://docs.astral.sh/uv/)

---

## ❓ FAQ

**Q: 다른 패키지의 코드를 수정할 때마다 언제 `uv sync`를 다시 실행해야 하나요?**

A: `pyproject.toml`을 수정한 경우만 필요합니다. 순수 코드 수정은 즉시 반영됩니다 (워크스페이스 로컬 참조).

**Q: 로컬에서 features.npz가 없으면?**

A: `dvc pull`을 실행하여 Google Drive에서 다운로드하세요.

**Q: 파이프라인을 다시 실행하고 싶으면?**

A: `dvc repro --force` 또는 `rm data/processed/features.npz && dvc repro`

**Q: 다른 브랜치의 데이터를 사용하려면?**

A: `git checkout` 후 `dvc checkout`으로 자동 스와핑.

**Q: Windows에서 경로 문제가 발생하면?**

A: `uv sync` 후 `pip install -e .` 대신 uv를 사용하세요 (경로 자동 처리).

---

**최종 수정**: 2026-06-17
