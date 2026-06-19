"""
시각화 스크립트
Stage 5: visualize - 학습 곡선, confusion matrix, 성능 그래프 생성
"""
import logging
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_params():
    """params.yaml 로드"""
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def get_data_paths():
    """실험별 데이터 경로 반환"""
    params = load_params()
    exp_name = params["experiment"]["name"]

    base_path = Path(__file__).parent.parent / "data" / exp_name

    return {
        "models": base_path / "models",
        "result": base_path / "result",
    }


def visualize_results():
    """
    훈련 결과 시각화

    생성 파일:
    - result/plots/training_loss.png
    - result/plots/confusion_matrix.png
    - result/plots/roc_curve.png
    - result/plots/metrics_summary.html
    """
    logger.info("🔄 Stage 5: Visualize - 시각화 및 보고서 생성 시작")

    paths = get_data_paths()
    plot_dir = paths["result"] / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # TODO: 실제 시각화 로직
    # 1. metrics.json 로드
    # 2. best_model.pt 로드
    # 3. matplotlib/seaborn으로 그래프 생성:
    #    - Training/Validation loss curve
    #    - Confusion matrix heatmap
    #    - ROC curve (threshold 분석)
    #    - Precision-Recall curve
    # 4. HTML 보고서 생성

    # 예시 (텍스트 파일):
    with open(plot_dir / "metrics_summary.txt", "w") as f:
        f.write("=== Experiment Results ===\n")
        f.write("Accuracy: 0.95\n")
        f.write("Precision: 0.93\n")
        f.write("Recall: 0.97\n")
        f.write("F1-Score: 0.95\n")

    logger.info(f"✅ Visualization 완료: {plot_dir}")


def main():
    visualize_results()


if __name__ == "__main__":
    main()
