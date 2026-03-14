import pandas as pd
import os

def main():
    csv_path = "runs/top_windows_alibi.csv"
    output_path = "runs/interpret/high_ism_windows_with_context.fa"
    dataset_path = "data/enh_test.csv" # Based on metadata and previous logs
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
    
    if not os.path.exists(dataset_path):
        print(f"Error: dataset {dataset_path} not found.")
        return

    # Load full sequences
    full_df = pd.read_csv(dataset_path)
    # The csv has "seq" and "label"

    # Load top windows
    df = pd.read_csv(csv_path)
    
    # Take top 1000 and bottom 1000 for enrichment test
    n = 1000
    top_indices = df.nlargest(n, 'window_importance').index
    bot_indices = df.nsmallest(n, 'window_importance').index
    
    # We will save both to FASTA for scanning
    def save_to_fasta(indices, tag):
        out_fa = f"runs/interpret/{tag}_ism_windows_context.fa"
        with open(out_fa, "w") as f:
            for i, idx in enumerate(indices):
                row = df.loc[idx]
                seq_idx = int(row["seq_index"])
                start = int(row["start"])
                window_len = int(row["window"])
                
                # Get full seq from dataset
                # Note: seq_index in top_windows refers to the row in the test set
                full_seq = full_df.iloc[seq_idx]["seq"]
                
                # Extract with 10bp context
                ctx = 10
                new_start = max(0, start - ctx)
                new_end = min(len(full_seq), start + window_len + ctx)
                subseq = full_seq[new_start:new_end]
                
                f.write(f">seq_{seq_idx}_win_{start}\n{subseq}\n")
        print(f"Saved {len(indices)} sequences to {out_fa}")

    save_to_fasta(top_indices, "high")
    save_to_fasta(bot_indices, "low")

if __name__ == "__main__":
    main()
