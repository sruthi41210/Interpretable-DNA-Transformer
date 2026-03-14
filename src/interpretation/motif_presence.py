import argparse
import pandas as pd

def contains_any(seq, motifs):
    seq = str(seq).upper()
    return any(m in seq for m in motifs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits_csv", required=True)
    ap.add_argument("--preds_csv", required=True)
    ap.add_argument("--top_n", type=int, default=2000)
    ap.add_argument("--bottom_n", type=int, default=2000)
    ap.add_argument("--split", default="test")
    args = ap.parse_args()

    df = pd.read_csv(args.splits_csv)
    df = df[df["split"] == args.split].reset_index(drop=True)
    preds = pd.read_csv(args.preds_csv)
    df = df.copy()
    df["prob"] = preds["prob"].values
    df = df.sort_values("prob", ascending=False)

    top = df.head(args.top_n)
    bot = df.tail(args.bottom_n)

    # simple promoter motif sets (start simple; expand later)
    tata = ["TATAAA", "TATATA", "TATAAT", "TATAAG"]
    gcbox = ["GGGCGG", "CCGCCC", "GCGGGG", "GGCGGG"]  # crude SP1-like

    for name, motifs in [("TATA_like", tata), ("GCbox_like", gcbox)]:
        top_rate = top["seq"].apply(lambda s: contains_any(s, motifs)).mean()
        bot_rate = bot["seq"].apply(lambda s: contains_any(s, motifs)).mean()
        enrich = (top_rate + 1e-9) / (bot_rate + 1e-9)
        print(f"{name}: top_rate={top_rate:.3f} bottom_rate={bot_rate:.3f} enrichment={enrich:.2f}x")

if __name__ == "__main__":
    main()
