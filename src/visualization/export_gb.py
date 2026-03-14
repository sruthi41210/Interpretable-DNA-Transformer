import pandas as pd
from genomic_benchmarks.data_check import is_downloaded
from genomic_benchmarks.loc2seq import download_dataset
from genomic_benchmarks.dataset_getters.pytorch_datasets import get_dataset

def export(name: str, split: str, out_csv: str):
    if not is_downloaded(name):
        download_dataset(name)

    ds = get_dataset(name, split=split)  # returns (seq, label)
    rows = []
    for seq, label in ds:
        rows.append({"seq": seq, "label": int(label)})
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"wrote {out_csv} with {len(rows)} rows")

if __name__ == "__main__":
    # core enhancer dataset
    export("human_enhancers_cohn", "train", "data/enh_train.csv")
    export("human_enhancers_cohn", "test",  "data/enh_test.csv")

    # secondary promoter dataset
    export("human_nontata_promoters", "train", "data/pro_train.csv")
    export("human_nontata_promoters", "test",  "data/pro_test.csv")
