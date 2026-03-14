import argparse, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASES = "ACGT"
b2i = {b:i for i,b in enumerate(BASES)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq_csv", required=True)        # runs/interpret/pro_top2000.csv
    ap.add_argument("--clusters_csv", required=True)   # runs/interpret/pro_k6_clusters.csv
    ap.add_argument("--cluster_id", type=int, required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--max_matches", type=int, default=50000)  # safety
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    seqs = pd.read_csv(args.seq_csv)["seq"].astype(str).tolist()
    cldf = pd.read_csv(args.clusters_csv)
    row = cldf[cldf["cluster_id"] == args.cluster_id]
    assert len(row) == 1, f"cluster_id {args.cluster_id} not found"

    members = row.iloc[0]["members"].split(",")
    members = [m.strip().upper() for m in members if m.strip()]
    k = len(members[0])
    assert all(len(m) == k for m in members), "cluster contains mixed k-mer lengths"

    # collect aligned matches
    counts = np.ones((k, 4), dtype=float)  # pseudocount
    n = 0

    for s in seqs:
        s = s.upper()
        for i in range(0, len(s) - k + 1):
            sub = s[i:i+k]
            if sub in members:
                n += 1
                for j,ch in enumerate(sub):
                    if ch in b2i:
                        counts[j, b2i[ch]] += 1
                if n >= args.max_matches:
                    break
        if n >= args.max_matches:
            break

    pwm = counts / counts.sum(axis=1, keepdims=True)

    out_csv = os.path.join(args.out_dir, f"pwm_cluster{args.cluster_id}_k{k}.csv")
    pd.DataFrame(pwm, columns=list(BASES)).to_csv(out_csv, index=False)

    plt.figure()
    plt.imshow(pwm.T, aspect="auto")
    plt.yticks(range(4), list(BASES))
    plt.xlabel("Position")
    plt.title(f"PWM cluster {args.cluster_id} (k={k}, matches={n})")
    out_png = os.path.join(args.out_dir, f"pwm_cluster{args.cluster_id}_k{k}.png")
    plt.savefig(out_png, bbox_inches="tight", dpi=200)

    print("Saved:", out_csv)
    print("Saved:", out_png)
    print("Matches used:", n)

if __name__ == "__main__":
    main()
