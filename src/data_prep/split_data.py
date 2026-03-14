import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

def load_split_df(splits_csv, split, fraction=1.0, seed=42, seq_col="seq", label_col="label"):
    df = pd.read_csv(splits_csv)
    df = df[df["split"] == split].reset_index(drop=True)

    if split == "train" and fraction < 1.0:
        y = df[label_col].values
        sss = StratifiedShuffleSplit(n_splits=1, test_size=(1.0 - fraction), random_state=seed)
        keep_idx, _ = next(sss.split(df, y))
        df = df.iloc[keep_idx].reset_index(drop=True)

    return df
