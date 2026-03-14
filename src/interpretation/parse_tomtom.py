import pandas as pd
import os

def main():
    tomtom_path = "tomtom_high_ism/tomtom.tsv"
    output_path = "runs/interpret/causal_motifs_discovered.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(tomtom_path):
        print(f"Error: {tomtom_path} not found. Run TomTom first.")
        return

    # TomTom TSV has a header and then data.
    # Columns usually: Query_ID, Target_ID, Optimal_offset, p-value, E-value, q-value, Overlap, query_consensus, target_consensus, orientation
    try:
        df = pd.read_csv(tomtom_path, sep="\t", comment="#")
        
        # Filter E-value < 0.01
        # Note: E-value might be a string if there are comments, handled by comment="#"
        df["E-value"] = pd.to_numeric(df["E-value"], errors='coerce')
        df_filtered = df[df["E-value"] < 0.01].copy()
        
        # Sort by E-value
        df_filtered = df_filtered.sort_values("E-value")
        
        # Top 10 matches
        top_10 = df_filtered.head(10)
        
        top_10.to_csv(output_path, index=False)
        print(f"Saved top {len(top_10)} matches to {output_path}")
        
    except Exception as e:
        print(f"Error parsing TomTom results: {e}")

if __name__ == "__main__":
    main()
