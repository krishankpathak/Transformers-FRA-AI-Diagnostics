import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH = Path("data/processed/fra/fra_curves.csv")
OUTPUT_PATH = Path("data/processed/fra/fra_augmented.csv")

AUGMENT_FACTOR = 20  # creates 20 variations per sample


def ensure_output_dir():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def augment_curve(group):
    augmented_rows = []

    for _ in range(AUGMENT_FACTOR):
        factor_R = np.random.uniform(0.8, 1.2)
        factor_L = np.random.uniform(0.8, 1.2)
        factor_C = np.random.uniform(0.8, 1.2)

        new_group = group.copy()

        new_group["R"] *= factor_R
        new_group["L"] *= factor_L
        new_group["C"] *= factor_C

        # simulate effect on magnitude (simple approximation)
        noise = np.random.normal(0, 0.5, size=len(new_group))
        new_group["magnitude_db"] += noise

        new_group["source_file"] = new_group["source_file"] + f"_aug_{np.random.randint(10000)}"

        augmented_rows.append(new_group)

    return pd.concat(augmented_rows)


def run_augmentation():
    print("🔁 Augmenting FRA dataset...")

    ensure_output_dir()

    df = pd.read_csv(INPUT_PATH)
    grouped = df.groupby("source_file")

    augmented_data = []

    for name, group in grouped:
        augmented = augment_curve(group)
        augmented_data.append(augmented)

    final_df = pd.concat([df] + augmented_data)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Augmented dataset created: {OUTPUT_PATH}")
    print(f"📊 Total rows: {len(final_df)}")


if __name__ == "__main__":
    run_augmentation()