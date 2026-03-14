import argparse
import pandas as pd

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--top_m", type=int, default=200)
    ap.add_argument("--max_hamming", type=int, default=1)
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv).head(args.top_m).copy()
    kmers = df["kmer"].astype(str).tolist()

    clusters = []
    assigned = set()

    for i, k in enumerate(kmers):
        if k in assigned:
            continue
        cluster = [k]
        assigned.add(k)
        for j in range(i+1, len(kmers)):
            k2 = kmers[j]
            if k2 in assigned:
                continue
            if len(k2) == len(k) and hamming(k, k2) <= args.max_hamming:
                cluster.append(k2)
                assigned.add(k2)
        clusters.append(cluster)

    rows = []
    for cid, cl in enumerate(clusters, start=1):
        rows.append({"cluster_id": cid, "representative": cl[0], "size": len(cl), "members": ",".join(cl)})

    out = pd.DataFrame(rows).sort_values("size", ascending=False)
    out.to_csv(args.out_csv, index=False)
    print(out.head(20))

if __name__ == "__main__":
    main()
