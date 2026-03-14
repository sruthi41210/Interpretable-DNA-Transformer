import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

BASES = "ACGT"
b2i = {b:i for i,b in enumerate(BASES)}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="runs/top_windows_alibi.csv")
    parser.add_argument("--out_dir", default="runs/interpret/pwms_ism")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.csv)
    
    if len(df) == 0:
        print("Empty CSV.")
        return

    # Assuming all subseqs have the same length
    k = len(df.iloc[0]["subseq"])
    counts = np.ones((k, 4), dtype=float) # pseudocount
    
    for _, row in df.iterrows():
        subseq = str(row["subseq"]).upper()
        if len(subseq) != k: continue
        for j, ch in enumerate(subseq):
            if ch in b2i:
                counts[j, b2i[ch]] += 1
                
    pwm = counts / counts.sum(axis=1, keepdims=True)
    
    out_csv = os.path.join(args.out_dir, f"pwm_ism_{os.path.basename(args.csv)}")
    pd.DataFrame(pwm, columns=list(BASES)).to_csv(out_csv, index=False)
    
    plt.figure()
    plt.imshow(pwm.T, aspect="auto", cmap="Blues")
    plt.yticks(range(4), list(BASES))
    plt.xlabel("Position")
    plt.title(f"PWM from ISM Windows (N={len(df)})")
    out_png = out_csv.replace(".csv", ".png")
    plt.savefig(out_png, bbox_inches="tight", dpi=200)
    
    print(f"Saved PWM to {out_csv}")
    print(f"Saved Visualization to {out_png}")

if __name__ == "__main__":
    main()
