import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    # Paths to match the user's results
    kmer_path = "runs/interpret/jaspar_match_pwm_cluster2_k6.csv"
    ism_path = "runs/interpret/jaspar_matches_k6.csv"
    output_path = "runs/visuals/causal_vs_kmer_motifs.png"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. K-mer Cluster Motifs (From background/depleted k-mer analysis)
    if os.path.exists(kmer_path):
        kdf = pd.read_csv(kmer_path)
        axes[0].axis('off')
        axes[0].set_title("K-mer Cluster Motifs\n(Background Enrichment)", fontsize=14, fontweight='bold')
        # Rename columns to match if needed
        cols = kdf.columns.tolist()
        name_col = 'name' if 'name' in cols else 'jaspar_name'
        corr_col = 'score' if 'score' in cols else 'correlation'
        
        table_data = kdf[[name_col, corr_col]].head(10).values
        axes[0].table(cellText=table_data, colLabels=['Transcription Factor', 'Correlation'], loc='center', cellLoc='center')
        
        # Add labels to explain the results
        axes[0].text(0.5, 0.1, "These motifs reflect base k-mer usage\nand may be associated with core promoter\narchitecture or background bias.", 
                     ha='center', va='center', transform=axes[0].transAxes, style='italic')
    else:
        axes[0].text(0.5, 0.5, f"File not found:\n{kmer_path}", ha='center')

    # 2. ISM-Based Causal Motifs (From high-importance sequences)
    if os.path.exists(ism_path):
        idf = pd.read_csv(ism_path)
        axes[1].axis('off')
        axes[1].set_title("ISM-Discovered Motifs\n(Causal Features)", fontsize=14, fontweight='bold', color='darkblue')
        
        table_data = idf[['jaspar_name', 'correlation']].head(10).values
        axes[1].table(cellText=table_data, colLabels=['Transcription Factor', 'Correlation'], loc='center', cellLoc='center')
        
        axes[1].text(0.5, 0.1, "These motifs were identified in windows\nthat directly cause a drop in model score\nwhen mutated. Likely causal TFBS.", 
                     ha='center', va='center', transform=axes[1].transAxes, style='italic', color='darkblue')
    else:
        axes[1].text(0.5, 0.5, f"File not found:\n{ism_path}", ha='center')

    plt.suptitle("DNA-SLM Motif Analysis: Identifying Causal Regulatory Elements", fontsize=20, y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300, facecolor='white')
    print(f"Final visualization saved to {output_path}")

if __name__ == "__main__":
    main()
