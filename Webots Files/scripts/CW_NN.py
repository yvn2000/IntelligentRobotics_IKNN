from pathlib import Path
import numpy as np

from CW_fk_ned import fk_ned
from CW_fk_scara import fk_scara

from sklearn.neural_network import MLPRegressor


#DATASET PREPROCESSING
#Load in ned and scara datasets
#Modify them to include flags: is_scara, is_ned
#OPTIONAL: Normalize the TCP x,y,z values; do this after training on unnormalized TCP
#values to see if the improve the results or not.
#Combine the two to form one dataset:
# (is_ned, is_scara, x, y, z ; joint1_norm, joint2_norm, joint3_norm)
#Shuffle the dataset to randomize the order.

DATASET_DIR = "../datasets"

def load_dataset(split, size=None):
    """Load and shuffle both robots using NumPy only."""

    if split not in ("train", "val", "test"):
        raise ValueError("Split must be 'train', 'val', or 'test'.")

    if split != "test" and size not in ("small", "medium", "large"):
        raise ValueError("Size must be 'small', 'medium', or 'large'.")

    filename = (
        "{robot}_test.csv"
        if split == "test"
        else "{robot}_" + split + "_" + size + ".csv"
    )

    def load_robot(robot, is_ned, is_scara):
        path = f"{DATASET_DIR}/{robot}/{filename.format(robot=robot)}"

        data = np.loadtxt(
            path,
            delimiter=",",
            skiprows=1,
            ndmin=2
        )

        if data.shape[1] != 9:
            raise ValueError(
                f"Expected 9 CSV columns in {path}, got {data.shape[1]}"
            )

        flags = np.tile([is_ned, is_scara], (len(data), 1))

        return np.column_stack((
            flags,
            data[:, 0:3],
            data[:, 6:9]
        ))

    ned = load_robot("ned", 1, 0)
    scara = load_robot("scara", 0, 1)

    combined = np.vstack((ned, scara))

    rng = np.random.RandomState(42)

    return combined[rng.permutation(len(combined))]

def prepare_data(dataset, normalize_tcp=False, tcp_bounds=None):
    """Create X and Y from the eight-column combined NumPy dataset."""
    X = dataset[:, :5].copy()
    Y = dataset[:, 5:8].copy()

    if normalize_tcp:
        tcp = X[:, 2:5]
        if tcp_bounds is None:
            tcp_bounds = (tcp.min(axis=0), tcp.max(axis=0))
        tcp_min, tcp_max = tcp_bounds
        X[:, 2:5] = 2 * (tcp - tcp_min) / (tcp_max - tcp_min) - 1

    #Calculate radius as additional feature using raw TCP coordinates.
    x = dataset[:, 2]
    y = dataset[:, 3]

    radius = np.sqrt(x**2 + y**2)
    X = np.column_stack((X, radius))
    return X, Y, tcp_bounds



#Training

def train_network(X_train, Y_train):
    model = MLPRegressor(
        hidden_layer_sizes=(64, 64),
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        #alpha=0.001,
        max_iter=2000,
        tol=1e-7,
        n_iter_no_change=30,
        early_stopping=False,
        random_state=42
    )

    model.fit(X_train, Y_train)

    return model






if __name__ == "__main__":
    for size in ("small", "medium", "large"):
        print(f"\n{'=' * 20} {size.upper()} DATASET {'=' * 20}")

        #Load the corresponding training and validation datasets.
        train = load_dataset("train", size)
        val = load_dataset("val", size)

        #Prepare inputs and normalized joint targets.

        normalize_tcp = False  #False = raw TCP, True = normalized TCP

        #Prepare training data and calculate TCP bounds.
        X_train, Y_train, tcp_bounds = prepare_data(
            train,
            normalize_tcp=normalize_tcp
        )
        X_val, Y_val, _ = prepare_data(
            val,
            normalize_tcp=normalize_tcp,
            tcp_bounds=tcp_bounds
        )

        model = train_network(X_train, Y_train)

        print(f"\nTraining complete!")
        print(f"Iterations: {model.n_iter_}")
        print(f"Final training loss: {model.loss_:.6f}")

