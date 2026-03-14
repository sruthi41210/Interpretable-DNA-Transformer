import pandas as pd
from collections import Counter

def main():
    df = pd.read_csv("runs/top_windows.csv")
    kmers = df["subseq"].astype(str).tolist()
    c = Counter(kmers)
    top = c.most_common(30)

    out = pd.DataFrame(top, columns=["kmer", "count"])
    out.to_csv("runs/top_kmers.csv", index=False)
    print(out.head(20))
    print("Saved runs/top_kmers.csv")

if __name__ == "__main__":
    main()
