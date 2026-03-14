import argparse, os, math, random
import pandas as pd

DNA = set("ACGTN")

def scan_has_motif(seq: str, motifs: set) -> bool:
    seq = str(seq).upper()
    k = len(next(iter(motifs)))
    if len(seq) < k:
        return False
    for i in range(0, len(seq) - k + 1):
        sub = seq[i:i+k]
        if sub in motifs:
            return True
    return False

def load_motif_set_from_cluster(clusters_csv: str, cluster_id: int) -> set:
    cdf = pd.read_csv(clusters_csv)
    row = cdf[cdf["cluster_id"] == cluster_id]
    if len(row) != 1:
        raise ValueError(f"cluster_id {cluster_id} not found in {clusters_csv}")
    members = str(row.iloc[0]["members"]).split(",")
    members = [m.strip().upper() for m in members if m.strip()]
    k = len(members[0])
    members = [m for m in members if len(m) == k and set(m).issubset(DNA)]
    return set(members)

def approx_pvalue_ztest(p1, n1, p2, n2):
    # two-proportion z-test (normal approx). Always returns (p_value, z).
    if n1 == 0 or n2 == 0:
        return 1.0, 0.0

    p = (p1*n1 + p2*n2) / (n1+n2)
    denom = math.sqrt(p*(1-p)*(1/n1 + 1/n2) + 1e-12)
    z = ((p1 - p2) / denom) if denom > 0 else 0.0

    # two-sided p-value from normal approx
    pval = math.erfc(abs(z)/math.sqrt(2))
    return float(pval), float(z)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="subseq", choices=["subseq","seq_index"])
    ap.add_argument("--splits_csv", required=True, help="e.g. data/pro_splits.csv or data/enh_splits.csv")
    ap.add_argument("--top_windows_csv", required=True, help="mutagenesis top windows CSV")
    ap.add_argument("--clusters_csv", required=True, help="kmer cluster CSV (pro_k6_clusters.csv or enh_k6_clusters.csv)")
    ap.add_argument("--cluster_id", type=int, required=True, help="which cluster family to test")
    ap.add_argument("--split", default="test", choices=["train","val","test"])
    ap.add_argument("--n_windows", type=int, default=5000, help="use top N mutagenesis windows")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out_json", required=True)
    args = ap.parse_args()

    random.seed(args.seed)

    # Load sequences for the chosen split, in the same index space used by mutagenesis
    sdf = pd.read_csv(args.splits_csv)
    sdf = sdf[sdf["split"] == args.split].reset_index(drop=True)
    seqs = sdf["seq"].astype(str).tolist()

    # Load mutagenesis windows
    wdf = pd.read_csv(args.top_windows_csv)

    # Must have these columns
    for col in ["seq_index", "start"]:
        if col not in wdf.columns:
            raise ValueError(f"Missing column '{col}' in {args.top_windows_csv}")
    # window length column might be named 'window' or 'window_len'
    if "window" in wdf.columns:
        win_col = "window"
    elif "window_len" in wdf.columns:
        win_col = "window_len"
    else:
        raise ValueError("Missing window length column: expected 'window' or 'window_len'")

    # Take top N windows (assumes file is already sorted by importance; if not, you can sort by 'base_score' or 'window_importance')
    wdf = wdf.head(args.n_windows).copy()

    motifs = load_motif_set_from_cluster(args.clusters_csv, args.cluster_id)
    k = len(next(iter(motifs)))

    # Compute motif-hit rate in important windows
    imp_hits = 0
    used = 0

    # Background: same number of windows, same lengths, sampled from same sequences uniformly
    bg_hits = 0

    motifs = load_motif_set_from_cluster(args.clusters_csv, args.cluster_id)
    k = len(next(iter(motifs)))

    # Take top N windows
    wdf = wdf.head(args.n_windows).copy()

    imp_hits = 0
    bg_hits = 0
    used = 0

    if args.mode == "subseq":
        # We only use the window sequence itself (subseq) and a shuffled background.
        if "subseq" not in wdf.columns:
            raise ValueError(f"mode=subseq requires 'subseq' column in {args.top_windows_csv}")

        subseqs = wdf["subseq"].astype(str).str.upper().tolist()

        for s in subseqs:
            if len(s) < k:
                continue
            used += 1
            if scan_has_motif(s, motifs):
                imp_hits += 1

        # Background: shuffle the subseqs to destroy motif structure while keeping composition
        rng = random.Random(args.seed)
        for s in subseqs:
            s = str(s).upper()
            if len(s) < k:
                continue
            chars = list(s)
            rng.shuffle(chars)
            shuf = "".join(chars)
            if scan_has_motif(shuf, motifs):
                bg_hits += 1

    else:
        # mode == "seq_index" (your original approach)
        sdf = pd.read_csv(args.splits_csv)
        sdf = sdf[sdf["split"] == args.split].reset_index(drop=True)
        seqs = sdf["seq"].astype(str).tolist()

        for col in ["seq_index", "start"]:
            if col not in wdf.columns:
                raise ValueError(f"Missing column '{col}' in {args.top_windows_csv}")

        if "window" in wdf.columns:
            win_col = "window"
        elif "window_len" in wdf.columns:
            win_col = "window_len"
        else:
            raise ValueError("Missing window length column: expected 'window' or 'window_len'")

        for _, row in wdf.iterrows():
            si = int(row["seq_index"])
            start = int(row["start"])
            wlen = int(row[win_col])

            if si < 0 or si >= len(seqs):
                continue

            seq = str(seqs[si]).upper()
            if len(seq) < wlen or wlen < k:
                continue

            wseq = seq[start:start+wlen]
            if len(wseq) != wlen:
                continue

            used += 1
            if scan_has_motif(wseq, motifs):
                imp_hits += 1

            # Background window: random start in same sequence with same wlen
            max_start = len(seq) - wlen
            rstart = random.randint(0, max_start) if max_start > 0 else 0
            rseq = seq[rstart:rstart+wlen]
            if scan_has_motif(rseq, motifs):
                bg_hits += 1


    imp_rate = imp_hits / max(used, 1)
    bg_rate = bg_hits / max(used, 1)
    fold = (imp_rate + 1e-12) / (bg_rate + 1e-12)
    pval, z = approx_pvalue_ztest(imp_rate, used, bg_rate, used)

    out = {
        "split": args.split,
        "cluster_id": args.cluster_id,
        "k": k,
        "n_used_windows": used,
        "important_hit_rate": imp_rate,
        "background_hit_rate": bg_rate,
        "fold_enrichment": fold,
        "z": z,
        "p_value_approx": pval,
        "top_windows_csv": args.top_windows_csv,
        "clusters_csv": args.clusters_csv
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    pd.Series(out).to_json(args.out_json, indent=2)
    print("Wrote:", args.out_json)
    print(out)

if __name__ == "__main__":
    main()
