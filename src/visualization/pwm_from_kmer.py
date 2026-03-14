import argparse
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

BASES = "ACGT"
b2i = {b:i for i,b in enumerate(BASES)}

def pwm_from_matches(seqs, motif):
    k = len(motif)
    counts = np.ones((k, 4), dtype=float)  # pseudocount 1
    n = 0
    for s in seqs:
        s = str(s).upper()
        for i in range(0, len(s)-k+1):
            if s[i:i+k] == motif:
                n += 1
                for j,ch in enumerate(motif):
                    if ch in b2i:
                        counts[j, b2i[ch]] += 1
    pwm = counts / counts.sum(axis=1, keepdims=True)
    return pwm, n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq_csv", required=True, help="CSV with column 'seq' (e.g., pro_top2000.csv)")
    ap.add_argument("--motif", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.seq_csv)
    seqs = df["seq"].astype(str).tolist()

    pwm, n = pwm_from_matches(seqs, args.motif)
    out_csv = os.path.join(args.out_dir, f"pwm_{args.motif}.csv")
    pd.DataFrame(pwm, columns=list(BASES)).to_csv(out_csv, index=False)

    plt.figure()
    plt.imshow(pwm.T, aspect="auto")
    plt.yticks(range(4), list(BASES))
    plt.xlabel("Position")
    plt.title(f"PWM for {args.motif} (matches={n})")
    out_png = os.path.join(args.out_dir, f"pwm_{args.motif}.png")
    plt.savefig(out_png, bbox_inches="tight", dpi=200)
    print("Saved:", out_csv)
    print("Saved:", out_png)

if __name__ == "__main__":
    main()
