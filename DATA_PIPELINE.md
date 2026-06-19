# 데이터 및 실험 파이프라인 가이드

CSI 낙상 감지 시스템의 전체 데이터 흐름, 실험 단계, 결과 관리 프로세스를 정리합니다.

---

## 📊 전체 데이터 파이프라인 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                    1️⃣ 데이터 수집 단계                           │
├─────────────────────────────────────────────────────────────────┤
│ MQTT 센서 → apps/infrastructure                                  │
│ (paho-mqtt로 CSI 스트림 수신)                                    │
│          ↓                                                       │
│ S3 저장소 또는 로컬 파일                                          │
│          ↓                                                       │
│ data/research/{variant}/raw/  ← 원본 데이터 (DVC 추적)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              2️⃣ 전처리 단계 (dvc repro - stage: preprocess)      │
├─────────────────────────────────────────────────────────────────┤
│ Input: data/research/{variant}/raw/*.csv                        │
│          + shared/core/sanitization.py (Hampel filter)          │
│          + shared/core/feature.py (linear interpolation)        │
│          + params.yaml (하이퍼파라미터)                          │
│                                                                 │
│ Process:                                                        │
│   1. CSI raw 데이터 로드                                         │
│   2. Hampel 필터로 이상치 제거                                    │
│   3. 선형보간으로 결측치 처리                                     │
│   4. 정규화 및 표준화                                            │
│                                                                 │
│ Output:                                                         │
│   - data/research/{variant}/preprocessed/preprocessed.npz      │
│     └─ Shape: (N_samples, N_features, N_timesteps)             │
│   - DVC 캐시 저장 (로컬: .dvc/cache/)                           │
│                                                                 │
│ 의존성 추적:                                                    │
│   ✅ preprocess.py 변경 → 자동 재실행                            │
│   ✅ sanitization.py 변경 (shared) → 자동 재실행                 │
│   ✅ feature.py 변경 (shared) → 자동 재실행                      │
│   ✅ params.yaml 변경 → 자동 재실행                              │
│   ❌ 모두 동일 → 캐시 재사용 (빠름)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              3️⃣ 특성 추출 단계 (dvc repro 계속)                  │
├─────────────────────────────────────────────────────────────────┤
│ Input: data/research/{variant}/preprocessed/preprocessed.npz   │
│          + shared/core/feature.py (PCA, DWT/CWT)               │
│          + params.yaml (feature 파라미터)                        │
│                                                                 │
│ Process (variant별 다름):                                       │
│                                                                 │
│ 📌 acf_cwt variant:                                             │
│    1. ACF (Auto-Correlation Function) 계산                     │
│    2. CWT (Continuous Wavelet Transform) 에너지 추출             │
│    3. PCA로 차원 축소 (n_pca=10)                                │
│    4. 특성 행렬 구성                                            │
│                                                                 │
│ 📌 combined_feature variant:                                    │
│    1. Multiple 특성 조합                                         │
│    2. Statistical features (mean, std, skew, kurtosis)         │
│    3. Frequency domain features                                │
│    4. PCA로 차원 축소                                           │
│                                                                 │
│ Output:                                                         │
│   - data/research/{variant}/features/features.npz              │
│     └─ Shape: (N_samples, N_features_extracted)                │
│     └─ 레이블: (N_samples,) - fall/no-fall binary               │
│   - DVC 캐시 저장                                                │
│                                                                 │
│ 💡 왜 두 단계로 나눔?                                            │
│    - preprocessed.npz: 재사용 가능한 중간 산물                    │
│    - features.npz: variant별 다른 추출 방식                      │
│    - 전처리 재실행 없이 특성만 변경 가능                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              4️⃣ 모델 학습 단계 (dvc repro - stage: train)       │
├─────────────────────────────────────────────────────────────────┤
│ Input: data/research/{variant}/features/features.npz           │
│          + train.py (PyTorch 학습 루프)                          │
│          + params.yaml (train 하이퍼파라미터)                    │
│                                                                 │
│ Process:                                                        │
│   1. features.npz 로드 및 train/val/test 분할                   │
│   2. PyTorch DataLoader 구성                                    │
│   3. 신경망 구축 (LSTM/CNN 등)                                  │
│   4. 에포크 반복:                                                │
│      - Forward pass                                             │
│      - Loss 계산                                                │
│      - Backward pass + Optimizer 스텝                           │
│      - Validation 평가                                          │
│   5. 최적 모델 저장 (Early stopping)                             │
│                                                                 │
│ 하이퍼파라미터 (params.yaml):                                    │
│   train:                                                        │
│     epochs: 100                                                │
│     batch_size: 32                                             │
│     learning_rate: 0.001                                       │
│     val_split: 0.2                                             │
│     test_split: 0.1                                            │
│                                                                 │
│ Output:                                                         │
│   - data/research/{variant}/models/best_model.pt               │
│     └─ PyTorch 체크포인트 (state_dict)                          │
│     └─ DVC 캐시 저장                                            │
│                                                                 │
│   - data/research/{variant}/models/metrics.json (캐시 X)        │
│     └─ accuracy, precision, recall, f1-score                  │
│     └─ confusion matrix                                        │
│     └─ 학습 곡선 (train_loss, val_loss per epoch)              │
│                                                                 │
│ 선택적 추적 (W&B):                                              │
│   WANDB_ENABLED=true로 실행하면:                                │
│   - 실시간 손실 곡선                                             │
│   - 레이어별 그래디언트                                          │
│   - 하이퍼파라미터 비교                                          │
│   - 모델 checkpoint 저장                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              5️⃣ 평가 및 배포 단계                                │
├─────────────────────────────────────────────────────────────────┤
│ Test Set 평가:                                                  │
│   - best_model.pt로 테스트 셋 평가                               │
│   - metrics.json에 최종 성능 기록                                │
│                                                                 │
│ 결과 비교:                                                      │
│   - acf_cwt vs combined_feature 성능 비교                       │
│   - metrics.json 차이 분석                                      │
│                                                                 │
│ 배포:                                                           │
│   ✅ best_model.pt → apps/service/models/ 복사                 │
│   ✅ FastAPI에서 로드 후 REST API로 제공                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 각 단계의 DVC 명령어

### 초기 설정 (첫 번만)

```bash
# 1. 모노레포 루트에서
cd csi_fall_monorepo

# 2. DVC 로컬 저장소 설정 (이미 완료되었으면 스킵)
# .dvc/config에서 local-storage 확인
cat .dvc/config

# 3. research 폴더로 이동
cd apps/research/acf_cwt

# 4. DVC 초기화 (첫 작업만)
dvc init --subdir
```

### 일일 워크플로우

```bash
cd apps/research/acf_cwt

# Step 1: 원본 데이터 준비
# data/research/acf_cwt/raw/ 폴더에 CSV 파일 복사/수집
cp /path/to/sensor/data/*.csv ../../data/research/acf_cwt/raw/

# Step 2: 전체 파이프라인 실행
dvc repro
# → Stage 1: preprocess (입력: raw/)
# → Stage 2: train (입력: features.npz)

# Step 3: 상태 확인
dvc status
# 출력:
# ✓ Workspace is up to date
# (또는 변경사항 있으면 "modified: data/models/metrics.json" 등)

# Step 4: 캐시에 저장
dvc push
# → 로컬 .dvc/cache/에 저장
# → metrics.json 제외 (cache: false)

# Step 5: 결과 확인
cat ../../data/research/acf_cwt/models/metrics.json
# {
#   "accuracy": 0.95,
#   "precision": 0.93,
#   "recall": 0.97,
#   "f1": 0.95
# }
```

### 파라미터만 변경할 때

```bash
# params.yaml 수정
nano params.yaml
# preprocessing.hampel_window: 5 → 7 변경

# DVC가 자동으로 영향받는 단계만 재실행
dvc repro
# → preprocess 단계만 실행 (features 변경됨)
# → train 단계 자동 실행 (features 입력 변경됨)

# 결과 확인
dvc diff
# → 이전 모델과의 성능 비교
```

### Shared core 수정할 때

```bash
# shared/src/fall_sensing/core/feature.py 수정
vim ../../shared/src/fall_sensing/core/feature.py

# DVC가 자동으로 감지
cd apps/research/acf_cwt
dvc repro
# → preprocess 단계 재실행 (의존성에 feature.py 명시)
# → features.npz 갱신
# → train 단계 자동 실행
# → best_model.pt 갱신
```

---

## 📁 파일 위치 및 역할

### 1. 원본 데이터 (Raw)

```
data/research/acf_cwt/raw/
├── sensor_data_001.csv     # CSI 센서 데이터 (3개 채널 × N 타임스텝)
├── sensor_data_002.csv     # shape: (N_samples, 3, timesteps)
├── labels_001.csv          # 레이블 (fall=1, no-fall=0)
└── labels_002.csv
```

**특징:**
- 원본 데이터 그대로 (전처리 X)
- 대용량 (몇 GB 가능)
- DVC로 관리
- 재수집하기 어려움 → 백업 필수

---

### 2. 전처리된 데이터 (Preprocessed)

```
data/research/acf_cwt/preprocessed/
└── preprocessed.npz
    ├── 'data': array(shape=(N_samples, 3, timesteps))
    │           Hampel 필터, 선형보간 적용됨
    └── 'labels': array(shape=(N_samples,))
                 0 or 1
```

**특징:**
- Hampel 필터: 이상치 제거
- 선형보간: 결측치 처리
- 정규화: 범위 [-1, 1]로 표준화
- DVC 캐시: true (중간 산물이지만 재계산 비용 크므로)
- 재현성: 파라미터 변경 시 자동 재계산

---

### 3. 특성 추출 데이터 (Features)

```
data/research/acf_cwt/features/
└── features.npz
    ├── 'X': array(shape=(N_samples, 10))
    │        ACF+CWT 특성, PCA로 10차원 축소
    └── 'y': array(shape=(N_samples,))
             레이블
```

**특징:**
- Variant별 다름 (acf_cwt vs combined_feature)
- 이미 정규화됨
- 모델 학습용
- DVC 캐시: true

---

### 4. 학습된 모델 (Models)

```
data/research/acf_cwt/models/
├── best_model.pt           # DVC 캐시됨 (cache: true)
│   └─ PyTorch state_dict
│   └─ 최적 epoch에서 저장
│
├── checkpoint_epoch_50.pt   # Optional: 중간 체크포인트
│
└── metrics.json             # 캐시 안 함 (cache: false)
    {
      "test_accuracy": 0.95,
      "test_precision": 0.93,
      "test_recall": 0.97,
      "test_f1": 0.95,
      "confusion_matrix": [[tn, fp], [fn, tp]],
      "training_time": 125.5,
      "model_params": 45230
    }
```

**특징:**
- best_model.pt: 재현성 중요 → DVC 캐시
- metrics.json: 실험 기록용 → 캐시 X (매번 덮어쓰기)

---

## 🔀 브랜치별 데이터 자동 관리

### 상황 1: 새로운 전처리 방식 시도

```bash
# 1. 새 브랜치 생성
git checkout -b feature/new-preprocessing

# 2. shared/core/sanitization.py 수정 (새로운 필터 추가)
vim ../../shared/src/fall_sensing/core/sanitization.py

# 3. DVC 파이프라인 재실행
cd apps/research/acf_cwt
dvc repro
# → preprocessed.npz 갱신
# → features.npz 갱신 (자동)
# → best_model.pt 갱신 (자동)
# → dvc.lock 생성/갱신

# 4. 결과 확인
cat ../../data/research/acf_cwt/models/metrics.json
# {"accuracy": 0.96, ...}  ← 개선됨

# 5. 커밋
git add dvc.yaml dvc.lock ../../data/research/acf_cwt/models/metrics.json
git commit -m "feat: improve preprocessing with new filter"
git push origin feature/new-preprocessing
```

### 상황 2: 메인 브랜치로 돌아가기

```bash
# 1. 메인 브랜치 체크아웃
git checkout main
dvc checkout
# → 자동으로 이전 best_model.pt 복원
# → 자동으로 이전 preprocessed.npz 복원
# → metrics.json도 이전 버전 반영

# 2. 메인 브랜치의 모델 사용
python -c "import torch; m = torch.load('../../data/research/acf_cwt/models/best_model.pt'); print(m.keys())"
```

### 상황 3: 두 Variant 동시 실험

```bash
# Terminal 1: acf_cwt 실험
cd apps/research/acf_cwt
dvc repro
# → data/research/acf_cwt/models/best_model.pt

# Terminal 2: combined_feature 실험 (다른 터미널)
cd apps/research/combined_feature
dvc repro
# → data/research/combined_feature/models/best_model.pt

# 비교
cat ../../data/research/acf_cwt/models/metrics.json
cat ../../data/research/combined_feature/models/metrics.json
# {"accuracy": 0.95, ...} vs {"accuracy": 0.93, ...}
```

---

## 💾 스토리지 관리

### DVC 로컬 캐시 구조

```
.dvc/cache/
├── files
│   └── md5/
│       ├── a1/
│       │   └── 23b4...  # features.npz의 MD5 해시
│       └── c5/
│           └── 67e8...  # best_model.pt의 MD5 해시
└── tmp/  # 임시 파일
```

**캐시 정리:**

```bash
# 사용 중인 캐시만 유지
dvc gc --workspace

# 전체 캐시 삭제 (위험)
rm -rf .dvc/cache/
dvc pull  # 다시 다운로드 (로컬 저장소에서)
```

### 디스크 사용량 확인

```bash
# 각 파일의 크기
du -sh data/research/acf_cwt/*/
# raw/          500M
# preprocessed/ 400M
# features/     50M
# models/       10M

# 전체 캐시 크기
du -sh .dvc/cache/
# 950M (대략 raw + preprocessed + models)
```

---

## 🚀 재현성 보장

### dvc.lock 파일

`dvc.lock`은 각 단계의 의존성과 출력물을 기록합니다:

```yaml
schema: '2.0'
stages:
  preprocess:
    cmd: python -m fall_sensing.research.preprocess
    deps:
    - path: ../../data/research/acf_cwt/raw/
      md5: a1b2c3d4...
      size: 500000000
    - path: src/fall_sensing/research/preprocess.py
      md5: e5f6g7h8...
      size: 5000
    - path: ../../shared/src/fall_sensing/core/sanitization.py
      md5: i9j0k1l2...
      size: 3000
    outs:
    - path: ../../data/research/acf_cwt/features/features.npz
      md5: m3n4o5p6...
      size: 50000000
    params:
      params.yaml:
        preprocessing.hampel_window: 5
        preprocessing.n_sigma: 3
  train:
    cmd: python -m fall_sensing.research.train
    deps:
    - path: ../../data/research/acf_cwt/features/features.npz
      md5: m3n4o5p6...  # preprocess 단계의 MD5
    outs:
    - path: ../../data/research/acf_cwt/models/best_model.pt
      md5: q7r8s9t0...
```

**효과:**
- 코드나 데이터 변경되지 않으면 캐시 재사용
- 타임스탬프가 아닌 MD5 기반 → 진정한 재현성
- 팀원이 같은 환경 복구 가능

---

## 📝 코드 예시: 파이썬에서 데이터 로드

### preprocess.py

```python
from pathlib import Path
import numpy as np

# 경로 설정
DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "research" / "acf_cwt"
RAW_DIR = DATA_ROOT / "raw"
PREPROCESSED_DIR = DATA_ROOT / "preprocessed"

def preprocess():
    # 1. 원본 데이터 로드
    all_data = []
    all_labels = []
    for csv_file in RAW_DIR.glob("sensor_data_*.csv"):
        data = np.loadtxt(csv_file, delimiter=",")
        all_data.append(data)
    
    data = np.concatenate(all_data)  # (N_samples, 3, timesteps)
    
    # 2. Hampel 필터 적용 (shared core 사용)
    from fall_sensing.core.sanitization import hampel_filter
    processed = hampel_filter(data, window_size=5, n_sigma=3)
    
    # 3. 선형보간으로 결측치 처리
    from fall_sensing.core.feature import linear_interpolate
    interpolated = linear_interpolate(processed)
    
    # 4. 저장
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(
        PREPROCESSED_DIR / "preprocessed.npz",
        data=interpolated,
        labels=all_labels
    )

if __name__ == "__main__":
    preprocess()
```

### train.py

```python
from pathlib import Path
import numpy as np
import torch
import json

DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "research" / "acf_cwt"
FEATURES_DIR = DATA_ROOT / "features"
MODELS_DIR = DATA_ROOT / "models"

def main():
    # 1. 특성 로드
    data = np.load(FEATURES_DIR / "features.npz")
    X = data['X']  # (N_samples, 10)
    y = data['y']  # (N_samples,)
    
    # 2. 데이터 분할
    train_size = int(0.7 * len(X))
    val_size = int(0.15 * len(X))
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
    X_test, y_test = X[train_size+val_size:], y[train_size+val_size:]
    
    # 3. PyTorch 변환
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train)
    
    # 4. 모델 정의 및 학습
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 1),
        torch.nn.Sigmoid()
    )
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.BCELoss()
    
    best_val_acc = 0
    for epoch in range(100):
        # 학습
        y_pred = model(X_train_t).squeeze()
        loss = criterion(y_pred, y_train_t)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 검증
        with torch.no_grad():
            y_val_pred = model(torch.FloatTensor(X_val)).squeeze()
            val_acc = ((y_val_pred > 0.5).float() == torch.FloatTensor(y_val)).float().mean()
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                MODELS_DIR.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), MODELS_DIR / "best_model.pt")
    
    # 5. 최종 평가
    with torch.no_grad():
        model.load_state_dict(torch.load(MODELS_DIR / "best_model.pt"))
        y_test_pred = model(torch.FloatTensor(X_test)).squeeze()
        y_test_pred_binary = (y_test_pred > 0.5).float().numpy()
        
        accuracy = (y_test_pred_binary == y_test).mean()
        tp = ((y_test_pred_binary == 1) & (y_test == 1)).sum()
        fp = ((y_test_pred_binary == 1) & (y_test == 0)).sum()
        fn = ((y_test_pred_binary == 0) & (y_test == 1)).sum()
        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        f1 = 2 * (precision * recall) / (precision + recall + 1e-8)
    
    # 6. 메트릭 저장
    metrics = {
        "test_accuracy": float(accuracy),
        "test_precision": float(precision),
        "test_recall": float(recall),
        "test_f1": float(f1),
        "confusion_matrix": {
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(((y_test_pred_binary == 0) & (y_test == 0)).sum())
        }
    }
    
    with open(MODELS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1-Score: {f1:.4f}")

if __name__ == "__main__":
    main()
```

---

## ✅ 체크리스트

매 실험마다 확인할 사항:

- [ ] Raw 데이터가 `data/research/{variant}/raw/`에 있는가?
- [ ] `dvc repro` 실행 후 에러가 없는가?
- [ ] `dvc status`가 "up to date"를 출력하는가?
- [ ] `metrics.json`에 성능이 기록되었는가?
- [ ] `best_model.pt`가 생성되었는가?
- [ ] `dvc.lock`이 업데이트되었는가?
- [ ] 두 variant 모두 비교했는가? (acf_cwt vs combined_feature)

---

## 🔗 관련 문서

- [README.md](./README.md) — 개발환경 설정, DVC 기본 사용법
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 전체 시스템 아키텍처, namespace package
- [.gitignore](../.gitignore) — Git에서 제외되는 파일
- [.dvcignore](./apps/research/acf_cwt/.dvcignore) — DVC 추적 규칙

