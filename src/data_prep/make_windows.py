import argparse
import pandas as pd

def sliding_windows(seq, w, stride):
    seq = str(seq).upper()
    out = []
    for i in range(0, max(0, len(seq) - w + 1), stride):
        out.append((i, seq[i:i+w]))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--window", type=int, default=50)
    ap.add_argument("--stride", type=int, default=5)
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)
    rows = []
    for ridx, row in df.iterrows():
        seq = row["seq"]
        prob = float(row.get("prob", 0.0))
        for start, wseq in sliding_windows(seq, args.window, args.stride):
            rows.append({
                "row_id": ridx,
                "start": start,
                "window_seq": wseq,
                "prob": prob
            })
    out = pd.DataFrame(rows)
    out.to_csv(args.out_csv, index=False)
    print(f"Wrote {args.out_csv} windows={len(out)}")

if __name__ == "__main__":
    main()
