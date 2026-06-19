# 실험 파이프라인 사용 가이드

새로운 DVC 파이프라인 구조를 사용한 실험 관리 방법입니다.

---

## 📁 새로운 디렉토리 구조

```
csi_fall_monorepo/
│
├── data/                                    # 원본 데이터셋 (루트)
│   ├── .gitkeep
│   ├── mandeley/                            # 데이터셋 1
│   ├── HT-HAR/                              # 데이터셋 2
│   └── manual/                              # 데이터셋 3
│
└── apps/research/acf_cwt/                   # ACF+CWT 실험
    ├── data/                                # 실험별 데이터
    │   ├── exp_001/                         # 첫 번째 실험
    │   │   ├── raw/                         # 원본 (분할됨)
    │   │   │   ├── train/
    │   │   │   └── test/
    │   │   ├── preprocessed/                # 전처리 데이터
    │   │   ├── features/                    # 특성 추출 데이터
    │   │   ├── models/                      # 학습 모델
    │   │   │   ├── best_model.pt            # 최적 모델
    │   │   │   └── checkpoint_*.pt
    │   │   └── result/                      # 실험 결과
    │   │       ├── metrics.json             # 성능 메트릭
    │   │       └── plots/                   # 시각화 (학습 곡선 등)
    │   └── exp_002/                         # 두 번째 실험 (동일 구조)
    │
    ├── scripts/
    │   ├── preprocess.py                    # Stage 1+2: split, preprocess
    │   ├── feature_extraction.py            # Stage 3: 특성 추출
    │   ├── train.py                         # Stage 4: 모델 훈련
    │   ├── visualize.py                     # Stage 5: 시각화
    │   ├── infer.py                         # 독립 실행: 추론
    │   └── run_pipeline.py                  # 전체 파이프라인 + 자동 커밋
    │
    ├── params.yaml                          # 실험 파라미터
    ├── dvc.yaml                             # DVC 파이프라인 정의
    └── .dvcignore
```

---

## 🚀 빠른 시작

### 1단계: 개발 환경 설정

```bash
cd csi_fall_monorepo

# uv 워크스페이스 설정 (첫 번실만)
uv sync --group dev

# 앱 실행 (선택)
cd apps/research/acf_cwt
```

### 2단계: 원본 데이터 준비

원본 데이터셋을 준비합니다:

```bash
# 예시: mandeley 데이터셋
data/mandeley/
├── feature_matrix.csv      # 또는 .npz, .parquet
├── labels.csv
├── metadata.json
└── ...
```

**지원하는 데이터셋 폴더:**
- `data/mandeley/`
- `data/HT-HAR/`
- `data/manual/`
- 또는 새로운 폴더 생성

### 3단계: 파이프라인 실행

```bash
cd apps/research/acf_cwt

# 기본값 (exp_001, mandeley 데이터셋)
python scripts/run_pipeline.py

# 또는 커스텀 설정
python scripts/run_pipeline.py --exp exp_002 --dataset HT-HAR
```

**자동 실행 순서:**
```
1. split → raw/train, raw/test 생성
2. preprocess → preprocessed/ 생성 (Hampel filter)
3. extract_features → features/ 생성 (ACF+CWT)
4. train → models/best_model.pt + result/metrics.json
5. visualize → result/plots/ 생성
6. git commit "experiment: exp_002 (HT-HAR)"
```

**결과 확인:**
```bash
# 메트릭 확인
cat apps/research/acf_cwt/data/exp_002/result/metrics.json

# 모델 확인
ls -lh apps/research/acf_cwt/data/exp_002/models/best_model.pt

# 커밋 기록
git log --oneline | grep "experiment:"
```

---

## 📊 params.yaml 파일 이해

```yaml
# 실험 설정
experiment:
  name: exp_001           # 실험 이름 (결과 폴더명)
  dataset: mandeley       # 사용할 데이터셋

# 데이터 분할
preprocessing:
  train_ratio: 0.8        # 80% train, 20% test
  hampel_window: 5        # Hampel 필터 윈도우
  n_sigma: 3.0            # 시그마값

# 특성 추출
feature:
  dwt_level: 4            # DWT 레벨
  wavelet: db4            # 웨이블릿 타입
  n_pca: 3                # PCA 차원

# 모델 훈련
train:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
  n_classes: 2            # fall/no-fall
```

---

## 🔄 여러 실험 비교

### 실험 1: 기본 설정 (mandeley, ACF+CWT)

```bash
cd apps/research/acf_cwt

# params.yaml 확인
cat params.yaml

# 파이프라인 실행
python scripts/run_pipeline.py
```

### 실험 2: 다른 데이터셋 (HT-HAR)

```bash
# 매개변수 변경 후 실행
python scripts/run_pipeline.py --exp exp_002 --dataset HT-HAR
```

### 실험 3: 하이퍼파라미터 변경

```bash
# params.yaml 수동 수정
vim params.yaml
# epochs: 100
# learning_rate: 0.0005

# 다시 파이프라인 실행
python scripts/run_pipeline.py --exp exp_003
```

### 결과 비교

```bash
# 모든 실험의 메트릭 확인
for exp in exp_001 exp_002 exp_003; do
  echo "=== $exp ==="
  cat apps/research/acf_cwt/data/$exp/result/metrics.json | grep -E "accuracy|f1"
done
```

---

## 📌 DVC 파이프라인 구조

### dvc.yaml의 5 Stage

```yaml
vars:
  - params.yaml          # params 파일 로드

stages:
  split:                 # Stage 1: 데이터 분할
    cmd: python scripts/preprocess.py --stage split
    deps: [../../data/${experiment.dataset}/]
    outs: [data/${experiment.name}/raw/train/, data/${experiment.name}/raw/test/]

  preprocess:            # Stage 2: 전처리
    cmd: python scripts/preprocess.py --stage preprocess
    deps: [data/${experiment.name}/raw/]
    outs: [data/${experiment.name}/preprocessed/]

  extract_features:      # Stage 3: 특성 추출
    cmd: python scripts/feature_extraction.py
    deps: [data/${experiment.name}/preprocessed/]
    outs: [data/${experiment.name}/features/]

  train:                 # Stage 4: 모델 훈련
    cmd: python scripts/train.py
    deps: [data/${experiment.name}/features/]
    outs: [data/${experiment.name}/models/best_model.pt]
    metrics: [data/${experiment.name}/result/metrics.json]

  visualize:             # Stage 5: 시각화
    cmd: python scripts/visualize.py
    deps: [data/${experiment.name}/models/best_model.pt]
    outs: [data/${experiment.name}/result/plots/]
```

### 변수 보간 (${experiment.name}, ${experiment.dataset})

DVC는 `params.yaml`의 값으로 경로를 자동으로 생성합니다:

```bash
# params.yaml에서:
# experiment.name: exp_001
# experiment.dataset: mandeley

# dvc.yaml의 경로가 자동으로:
# ../../data/mandeley/      (deps)
# data/exp_001/raw/train/   (outs)
```

---

## 🧪 각 스크립트 사용법

### preprocess.py

```bash
# Stage 1: 데이터 분할 (split)
cd apps/research/acf_cwt
python scripts/preprocess.py --stage split

# Stage 2: 전처리 (preprocess)
python scripts/preprocess.py --stage preprocess

# 또는 dvc repro로 자동 실행
dvc repro --stages split,preprocess
```

### feature_extraction.py

```bash
# Stage 3: 특성 추출
python scripts/feature_extraction.py

# 또는
dvc repro --stages extract_features
```

### train.py

```bash
# Stage 4: 모델 훈련
python scripts/train.py

# 또는
dvc repro --stages train
```

### visualize.py

```bash
# Stage 5: 시각화
python scripts/visualize.py

# 또는
dvc repro --stages visualize
```

### infer.py (독립 실행)

```bash
# 학습된 모델로 새 데이터 추론
python scripts/infer.py --input new_data.csv --exp exp_001

# 또는 다른 실험의 모델 사용
python scripts/infer.py --input test.npz --exp exp_002 --output result.json
```

---

## 🔐 DVC 캐싱 및 재현성

### dvc.lock 파일

`dvc.lock`은 각 stage의 의존성과 출력물을 MD5로 기록합니다:

```yaml
split:
  cmd: python scripts/preprocess.py --stage split
  deps:
  - path: ../../data/mandeley/
    md5: a1b2c3d4...
    size: 500000000
  outs:
  - path: data/exp_001/raw/train/
    md5: e5f6g7h8...
```

**효과:**
- 코드/데이터 변경 없으면 캐시 재사용 (빠름)
- 변경 감지 → 자동 재실행
- Git으로 추적 → 실험 재현성 보장

### 캐시 관리

```bash
# DVC 캐시 위치: .dvc/cache/

# 현재 캐시 상태 확인
dvc status

# 캐시 정리
dvc gc --workspace

# 캐시 전체 삭제 (위험)
rm -rf .dvc/cache/
dvc pull  # 다시 다운로드
```

---

## 🌳 브랜치별 실험 관리

### 새로운 전처리 방식 시도

```bash
# 1. 새 브랜치 생성
git checkout -b feature/new-hampel-params

# 2. params.yaml 수정
vim apps/research/acf_cwt/params.yaml
# hampel_window: 5 → 7

# 3. 파이프라인 실행
python apps/research/acf_cwt/scripts/run_pipeline.py --exp exp_new

# 4. 결과 확인
cat apps/research/acf_cwt/data/exp_new/result/metrics.json

# 5. 커밋
git add apps/research/acf_cwt/
git commit -m "experiment: exp_new with improved hampel params"
git push origin feature/new-hampel-params
```

### 이전 실험으로 복귀

```bash
# 특정 커밋의 파라미터와 데이터로 복귀
git checkout <commit_hash> -- apps/research/acf_cwt/params.yaml
git checkout <commit_hash> -- apps/research/acf_cwt/dvc.lock

# DVC가 자동으로 캐시에서 이전 데이터 복원
dvc checkout

# 이전 모델 사용 가능
python apps/research/acf_cwt/scripts/infer.py --input test.csv --exp exp_001
```

---

## 📈 실험 히스토리 추적

### Git 로그로 실험 기록 보기

```bash
# 모든 실험 커밋 보기
git log --oneline | grep "experiment:"

# 특정 실험의 상세 정보
git show <commit_hash> -- apps/research/acf_cwt/dvc.lock

# 두 실험의 파라미터 차이
git diff <exp1_commit> <exp2_commit> -- params.yaml
```

### 실험 메타데이터 추적

각 실험마다:
- `params.yaml` → 파라미터
- `dvc.lock` → 의존성 + MD5
- `result/metrics.json` → 성능
- `result/plots/` → 시각화

---

## ⚙️ 트러블슈팅

### 문제: "Stage 'split' depends on data that does not exist"

**원인:** `data/mandeley/` 폴더가 비어있음

**해결:**
```bash
# 실제 데이터 추가
cp /path/to/dataset/* data/mandeley/
```

### 문제: "run_pipeline.py 실행 중 git 에러"

**원인:** Git 설정 필요

**해결:**
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

### 문제: DVC 캐시 오류

**해결:**
```bash
# 캐시 재설정
dvc remote list
dvc remote modify local-storage --local

# 캐시 확인
dvc status
dvc gc --workspace
```

---

## 📚 관련 문서

- [README.md](./README.md) — 개발환경 설정
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 시스템 아키텍처
- [.claude/plans/](./claude/plans/) — 구현 계획

---

## 🎯 요약

| 작업 | 명령어 |
|------|--------|
| 새 실험 (기본값) | `python scripts/run_pipeline.py` |
| 새 실험 (커스텀) | `python scripts/run_pipeline.py --exp exp_002 --dataset HT-HAR` |
| 특정 스테이지만 | `dvc repro --stages train` |
| 파이프라인 검증 | `dvc dag` |
| 캐시 상태 확인 | `dvc status` |
| 추론 실행 | `python scripts/infer.py --input test.csv --exp exp_001` |

---

**최종 수정**: 2026-06-19

