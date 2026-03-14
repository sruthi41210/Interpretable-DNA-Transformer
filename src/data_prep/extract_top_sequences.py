import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits_csv", required=True)
    ap.add_argument("--preds_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--top_n", type=int, default=2000)
    ap.add_argument("--min_len", type=int, default=1)
    args = ap.parse_args()

    df = pd.read_csv(args.splits_csv)
    df = df[df["split"] == args.split].reset_index(drop=True)

    preds = pd.read_csv(args.preds_csv)
    assert len(df) == len(preds), "preds and split df length mismatch (must be same eval order)"

    df = df.copy()
    df["prob"] = preds["prob"].values
    df = df[df["seq"].astype(str).str.len() >= args.min_len]

    top = df.sort_values("prob", ascending=False).head(args.top_n)
    top.to_csv(args.out_csv, index=False)
    print(f"Wrote {args.out_csv} rows={len(top)}")

if __name__ == "__main__":
    main()
