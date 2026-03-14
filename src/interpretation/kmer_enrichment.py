import argparse
import pandas as pd
from collections import Counter
import math

def kmers(s, k):
    s = str(s).upper()
    out = []
    for i in range(0, len(s)-k+1):
        out.append(s[i:i+k])
    return out

def count_kmers(seqs, k):
    c = Counter()
    for s in seqs:
        c.update(kmers(s, k))
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits_csv", required=True)
    ap.add_argument("--preds_csv", required=True)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--top_n", type=int, default=2000)
    ap.add_argument("--bottom_n", type=int, default=2000)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--split", default="test")
    args = ap.parse_args()

    df = pd.read_csv(args.splits_csv)
    df = df[df["split"] == args.split].reset_index(drop=True)
    preds = pd.read_csv(args.preds_csv)
    df = df.copy()
    df["prob"] = preds["prob"].values

    df_sorted = df.sort_values("prob", ascending=False)
    top = df_sorted.head(args.top_n)
    bot = df_sorted.tail(args.bottom_n)

    top_counts = count_kmers(top["seq"].tolist(), args.k)
    bot_counts = count_kmers(bot["seq"].tolist(), args.k)

    top_total = sum(top_counts.values())
    bot_total = sum(bot_counts.values())

    rows = []
    all_kmers = set(top_counts) | set(bot_counts)
    for kmer in all_kmers:
        a = top_counts.get(kmer, 0)
        b = bot_counts.get(kmer, 0)

        # add small pseudocount to avoid div by zero
        p_top = (a + 1) / (top_total + len(all_kmers))
        p_bot = (b + 1) / (bot_total + len(all_kmers))
        log2fc = math.log(p_top / p_bot, 2)

        rows.append({
            "kmer": kmer,
            "top_count": a,
            "bottom_count": b,
            "log2_enrichment": log2fc
        })

    out = pd.DataFrame(rows).sort_values("log2_enrichment", ascending=False)
    out.to_csv(args.out_csv, index=False)
    print(f"Wrote {args.out_csv} rows={len(out)}")

if __name__ == "__main__":
    main()
