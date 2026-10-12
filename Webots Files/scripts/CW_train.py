from __future__ import annotations

import argparse
import csv
import pickle
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor

# FINAL MODEL TRAINING
# This script loads and combines Ned and SCARA training and
# validation datasets for Small, Medium, and Large models.
# It uses the best hyperparameters selected during tuning,
# trains three final neural network models, checks validation
# RMSE and MAE, and saves the fitted models as .pkl files
# along with a training summary CSV.
# Test datasets are not used during training.

SELECTED_CONFIGS = {
    "small": {"hidden_layer_sizes": (128, 64), "learning_rate_init": 0.001, "alpha": 0.0001},
    "medium": {"hidden_layer_sizes": (128, 64), "learning_rate_init": 0.001, "alpha": 0.0001},
    "large": {"hidden_layer_sizes": (128, 64), "learning_rate_init": 0.0005, "alpha": 0.001},
}


def locate_csv(data_dir: Path, robot: str, split: str, size: str) -> Path:
    """Find a CSV in either a flat folder or a per-robot subfolder."""
    filename = f"{robot}_{split}_{size}.csv"
    candidates = [data_dir / filename]

    # Check common spellings first, then find matching subfolders case-insensitively.
    candidates.extend([
        data_dir / robot / filename,
        data_dir / robot.capitalize() / filename,
        data_dir / robot.upper() / filename,
    ])
    if data_dir.is_dir():
        for child in data_dir.iterdir():
            if child.is_dir() and child.name.lower() == robot.lower():
                candidates.append(child / filename)

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not find {filename}. Checked the data folder and its {robot}/ subfolder."
    )


def load_robot(data_dir: Path, robot: str, split: str, size: str) -> tuple[np.ndarray, np.ndarray]:
    """Load one robot split and return coursework-aligned X and normalised Y."""
    path = locate_csv(data_dir, robot, split, size)
    raw = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    if raw.shape[1] != 9:
        raise ValueError(f"Expected 9 CSV columns in {path}, found {raw.shape[1]}.")
    if not np.isfinite(raw).all():
        raise ValueError(f"NaN or infinite value found in {path}.")

    # The coursework asks for two robot flags and TCP x/y/z: exactly five inputs.
    flags = np.tile([1.0, 0.0] if robot == "ned" else [0.0, 1.0], (len(raw), 1))
    x = np.column_stack((flags, raw[:, 0:3]))
    # Columns 6-8 are the normalised targets. For SCARA, target 3 is q4_norm.
    y = raw[:, 6:9].copy()
    return x, y


def combine_split(data_dir: Path, split: str, size: str) -> tuple[np.ndarray, np.ndarray]:
    x_ned, y_ned = load_robot(data_dir, "ned", split, size)
    x_scara, y_scara = load_robot(data_dir, "scara", split, size)
    x = np.vstack((x_ned, x_scara))
    y = np.vstack((y_ned, y_scara))
    if split == "train":
        order = np.random.RandomState(42).permutation(len(x))
        x, y = x[order], y[order]
    return x, y


def main() -> None:
    parser = argparse.ArgumentParser(description="Train final selected ANN models (no test data is read).")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent.parent / "Dataset")
    parser.add_argument("--model-dir", type=Path, default=Path(__file__).resolve().parent / "trained_models")
    parser.add_argument("--max-iter", type=int, default=2000)
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    model_dir = args.model_dir.expanduser().resolve()
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Dataset directory does not exist: {data_dir}")
    model_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    print(f"Dataset folder: {data_dir}")
    print(f"Model output folder: {model_dir}")
    print("Inputs: [is_ned, is_scara, x, y, z]; targets: 3 normalised joint values.")
    print("Only training and validation files are loaded; test files are not opened.\n")

    for size, config in SELECTED_CONFIGS.items():
        x_train, y_train = combine_split(data_dir, "train", size)
        x_val, y_val = combine_split(data_dir, "val", size)

        model = MLPRegressor(
            hidden_layer_sizes=config["hidden_layer_sizes"],
            activation="relu",
            solver="adam",
            learning_rate_init=config["learning_rate_init"],
            alpha=config["alpha"],
            max_iter=args.max_iter,
            tol=1e-7,
            n_iter_no_change=30,
            early_stopping=False,
            random_state=42,
        )
        model.fit(x_train, y_train)
        val_pred = model.predict(x_val)
        val_rmse = float(np.sqrt(mean_squared_error(y_val, val_pred)))
        val_mae = float(mean_absolute_error(y_val, val_pred))

        model_path = model_dir / f"iknn_{size}_model.pkl"
        with model_path.open("wb") as f:
            pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

        row = {
            "size": size,
            "train_rows_combined": len(x_train),
            "validation_rows_combined": len(x_val),
            "hidden_layer_sizes": str(config["hidden_layer_sizes"]),
            "learning_rate_init": config["learning_rate_init"],
            "alpha": config["alpha"],
            "iterations": model.n_iter_,
            "train_loss": float(model.loss_),
            "validation_rmse": val_rmse,
            "validation_mae": val_mae,
            "max_iter_reached": model.n_iter_ >= model.max_iter,
            "model_file": model_path.name,
        }
        summary_rows.append(row)
        print(
            f"{size.upper()}: train={len(x_train)}, val={len(x_val)}, "
            f"layers={config['hidden_layer_sizes']}, lr={config['learning_rate_init']}, "
            f"alpha={config['alpha']}, iterations={model.n_iter_}, "
            f"val RMSE={val_rmse:.6f}, val MAE={val_mae:.6f}"
        )
        print(f"  Saved: {model_path}\n")

    summary_path = model_dir / "final_models_training_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Summary saved: {summary_path}")
    print("Reminder: model files were trained on training splits; validation was used only for checking selected settings.")


if __name__ == "__main__":
    main()
