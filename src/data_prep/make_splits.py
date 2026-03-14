# src/make_splits.py
import argparse, hashlib
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

def stable_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--val_frac", type=float, default=0.1)
    ap.add_argument("--test_frac", type=float, default=0.1)
    ap.add_argument("--label_col", default="label")
    ap.add_argument("--seq_col", default="sequence")
    ap.add_argument("--group_by", choices=["sequence", "none"], default="sequence")
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)
    # --- auto-detect columns if user passed defaults but CSV differs ---
    def pick_first_existing(candidates, cols):
        for c in candidates:
            if c in cols:
                return c
        return None

    cols = list(df.columns)

    # auto-detect seq col
    if args.seq_col not in df.columns:
        guessed = pick_first_existing(
            ["sequence", "seq", "Sequence", "SEQ", "dna", "DNA", "text", "x", "X"],
            cols
        )
        if guessed is None:
            raise ValueError(f"Could not find sequence column. Available columns: {cols}. "
                            f"Pass --seq_col explicitly.")
        print(f"[make_splits] seq_col '{args.seq_col}' not found. Using '{guessed}'.")
        args.seq_col = guessed

    # auto-detect label col
    if args.label_col not in df.columns:
        guessed = pick_first_existing(
            ["label", "y", "Y", "target", "Target", "class", "Class", "is_positive"],
            cols
        )
        if guessed is None:
            raise ValueError(f"Could not find label column. Available columns: {cols}. "
                            f"Pass --label_col explicitly.")
        print(f"[make_splits] label_col '{args.label_col}' not found. Using '{guessed}'.")
        args.label_col = guessed


    # Group ID to prevent duplicates leaking across splits
    if args.group_by == "sequence":
        df["group_id"] = df[args.seq_col].astype(str).map(stable_hash)
    else:
        df["group_id"] = [stable_hash(str(i)) for i in range(len(df))]

    # Deduplicate by group_id (keep first); you can also keep all but force same split per group later
    df = df.drop_duplicates(subset=["group_id"]).reset_index(drop=True)

    y = df[args.label_col].values

    # First split: train_val vs test
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=args.test_frac, random_state=args.seed)
    trainval_idx, test_idx = next(sss1.split(df, y))

    df["split"] = "train"
    df.loc[test_idx, "split"] = "test"

    # Second split: train vs val (within trainval)
    trainval = df.iloc[trainval_idx].copy().reset_index(drop=True)
    y_tv = trainval[args.label_col].values
    val_frac_rel = args.val_frac / (1.0 - args.test_frac)

    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=val_frac_rel, random_state=args.seed)
    tr_idx, va_idx = next(sss2.split(trainval, y_tv))

    train_groups = set(trainval.loc[tr_idx, "group_id"].tolist())
    val_groups = set(trainval.loc[va_idx, "group_id"].tolist())

    # Assign splits back by group_id to guarantee grouping (even after dedupe this keeps semantics)
    df.loc[df["group_id"].isin(train_groups), "split"] = "train"
    df.loc[df["group_id"].isin(val_groups), "split"] = "val"

    # Save
    out = df[[args.seq_col, args.label_col, "group_id", "split"]].copy()
    out.to_csv(args.out_csv, index=False)
    print(f"Wrote {args.out_csv}:",
          out["split"].value_counts().to_dict(),
          "pos_rate_by_split:",
          out.groupby("split")[args.label_col].mean().to_dict())

if __name__ == "__main__":
    main()
