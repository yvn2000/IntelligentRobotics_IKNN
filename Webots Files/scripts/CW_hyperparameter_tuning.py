from __future__ import annotations

import argparse
import csv
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor


# HYPERPARAMETER TUNING
# This script loads and combines Ned and SCARA training and
# validation datasets for Small, Medium, and Large models.
# It tests 18 hyperparameter combinations per dataset size,
# selects the best configuration using validation RMSE, and
# saves the tuning results to CSV files.
# Test datasets are not used during tuning.


ARCHITECTURES = [(32,), (64, 64), (128, 64)]
LEARNING_RATES = [0.0005, 0.001, 0.005]
ALPHAS = [0.0001, 0.001]
RESULT_COLUMNS = [
    "hidden_layer_sizes", "learning_rate_init", "alpha", "iterations",
    "train_loss", "val_rmse", "val_mae", "max_iter_reached",
    "convergence_warning", "seconds",
]


def find_csv(data_dir: Path, robot: str, split: str, size: str | None = None) -> Path:
    filename = f"{robot}_test.csv" if split == "test" else f"{robot}_{split}_{size}.csv"
    candidates = (data_dir / filename, data_dir / robot / filename)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not find {filename}. Checked: " + ", ".join(str(p) for p in candidates)
    )


def load_robot(robot: str, split: str, size: str, data_dir: Path) -> np.ndarray:
    path = find_csv(data_dir, robot, split, size)
    raw = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    if raw.shape[1] != 9:
        raise ValueError(f"{path.name}: expected 9 columns, found {raw.shape[1]}.")
    if not np.isfinite(raw).all():
        raise ValueError(f"{path.name}: found NaN or infinite values.")

    # CSV columns are x,y,z, three raw joint values, then three normalised joints.
    flags = np.tile([1.0, 0.0] if robot == "ned" else [0.0, 1.0], (len(raw), 1))
    return np.column_stack((flags, raw[:, 0:3], raw[:, 6:9]))


def make_xy(dataset: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Coursework input: [is_ned, is_scara, x, y, z] -- no additional engineered feature.
    X = dataset[:, :5].copy()
    Y = dataset[:, 5:8].copy()
    return X, Y


def read_combined(split: str, size: str, data_dir: Path) -> np.ndarray:
    ned = load_robot("ned", split, size, data_dir)
    scara = load_robot("scara", split, size, data_dir)
    combined = np.vstack((ned, scara))
    if split == "train":
        # Shuffle only the training rows; fixed seed makes the experiment reproducible.
        rng = np.random.RandomState(42)
        combined = combined[rng.permutation(len(combined))]
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune the shared MLP using validation data only.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent,
                        help="Folder containing the flat CSV files or ned/ and scara/ subfolders.")
    parser.add_argument("--size", choices=("small", "medium", "large"), required=True,
                        help="Dataset size to tune. Run each size separately.")
    parser.add_argument("--max-iter", type=int, default=2000,
                        help="Maximum MLP iterations (default: 2000, matching the current baseline).")
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Dataset folder does not exist: {data_dir}")
    if args.max_iter < 1:
        raise ValueError("--max-iter must be at least 1.")

    train = read_combined("train", args.size, data_dir)
    val = read_combined("val", args.size, data_dir)
    X_train, y_train = make_xy(train)
    X_val, y_val = make_xy(val)

    results_path = data_dir / f"hyperparameter_tuning_{args.size}_coursework_results.csv"
    if results_path.exists():
        with results_path.open("r", newline="", encoding="utf-8") as f:
            results = list(csv.DictReader(f))
    else:
        results = []

    configs = [(arch, lr, alpha) for arch in ARCHITECTURES
               for lr in LEARNING_RATES for alpha in ALPHAS]
    completed = {
        (row["hidden_layer_sizes"], float(row["learning_rate_init"]), float(row["alpha"]))
        for row in results
    }

    print(f"Data folder: {data_dir}")
    print(f"Size: {args.size}; train rows combined={len(train)}; validation rows combined={len(val)}")
    print("Input columns: [is_ned, is_scara, x, y, z]; targets: three normalised joint values.")
    print("Only training and validation CSVs will be read; test CSVs are not loaded.")

    for i, (layers, lr, alpha) in enumerate(configs, start=1):
        key = (str(layers), lr, alpha)
        if key in completed:
            print(f"[{i}/{len(configs)}] already saved; skipping {layers}, lr={lr}, alpha={alpha}")
            continue

        model = MLPRegressor(
            hidden_layer_sizes=layers,
            activation="relu",
            solver="adam",
            learning_rate_init=lr,
            alpha=alpha,
            max_iter=args.max_iter,
            tol=1e-7,
            n_iter_no_change=30,
            early_stopping=False,
            random_state=42,
        )
        start = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model.fit(X_train, y_train)
        elapsed = round(time.perf_counter() - start, 2)
        predicted = model.predict(X_val)
        row = {
            "hidden_layer_sizes": str(layers),
            "learning_rate_init": lr,
            "alpha": alpha,
            "iterations": model.n_iter_,
            "train_loss": float(model.loss_),
            "val_rmse": float(np.sqrt(mean_squared_error(y_val, predicted))),
            "val_mae": float(mean_absolute_error(y_val, predicted)),
            "max_iter_reached": model.n_iter_ >= model.max_iter,
            "convergence_warning": any(isinstance(w.message, ConvergenceWarning) for w in caught),
            "seconds": elapsed,
        }
        results.append(row)
        completed.add(key)
        results.sort(key=lambda r: float(r["val_rmse"]))
        with results_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
            writer.writeheader()
            writer.writerows(results)

        print(
            f"[{i}/{len(configs)}] layers={layers}, lr={lr}, alpha={alpha} "
            f"-> val RMSE={row['val_rmse']:.6f}, val MAE={row['val_mae']:.6f}, "
            f"iterations={row['iterations']}, time={elapsed}s",
            flush=True,
        )

    print(f"\nSaved results: {results_path}")
    print("Top configurations by validation RMSE:")
    for row in sorted(results, key=lambda r: float(r["val_rmse"]))[:5]:
        print(
            f"layers={row['hidden_layer_sizes']}, lr={row['learning_rate_init']}, "
            f"alpha={row['alpha']}, RMSE={float(row['val_rmse']):.6f}, "
            f"MAE={float(row['val_mae']):.6f}, iterations={row['iterations']}"
        )


if __name__ == "__main__":
    main()