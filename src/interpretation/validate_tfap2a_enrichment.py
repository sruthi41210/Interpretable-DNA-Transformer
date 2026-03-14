import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
import regex
import os
from Bio import SeqIO

def scan_motif(sequence, pattern='GCC[ACGT]{3}GGC'):
    """Scan sequence for motif presence with soft matching (1 substitution allowed)"""
    matches = regex.findall(f'({pattern}){{s<=1}}', str(sequence).upper(), overlapped=True)
    return len(matches) > 0

def scan_fasta(fasta_path):
    if not os.path.exists(fasta_path):
        return 0
    records = list(SeqIO.parse(fasta_path, "fasta"))
    hits = sum(1 for rec in records if scan_motif(rec.seq))
    return hits

def main():
    high_fa = "runs/interpret/high_ism_windows_context.fa"
    low_fa = "runs/interpret/low_ism_windows_context.fa"

    if not os.path.exists(high_fa) or not os.path.exists(low_fa):
        print("Error: Context FASTA files not found. Run extraction script first.")
        return

    print("Scanning high-ISM context windows for TFAP2A (GCCNNNGGC)...")
    high_hits = scan_fasta(high_fa)
    
    print("Scanning low-ISM context windows for TFAP2A...")
    low_hits = scan_fasta(low_fa)

    n_high = len(list(SeqIO.parse(high_fa, "fasta")))
    n_low = len(list(SeqIO.parse(low_fa, "fasta")))

    # Fisher's exact test
    table = [
        [high_hits, n_high - high_hits],
        [low_hits, n_low - low_hits]
    ]

    odds_ratio, p_value = fisher_exact(table)

    print(f"\n{'='*30}")
    print(f"TFAP2A Enrichment Test (with 10bp flanks):")
    print(f"  High-ISM: {high_hits}/{n_high} ({high_hits/n_high*100:.1f}%)")
    print(f"  Low-ISM: {low_hits}/{n_low} ({low_hits/n_low*100:.1f}%)")
    print(f"  Odds Ratio: {odds_ratio:.2f}x")
    print(f"  P-value: {p_value:.2e}")
    # Remove unicode to avoid cp1252 errors
    print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'}")
    print(f"{'='*30}\n")

    # Save result
    os.makedirs('runs/interpret', exist_ok=True)
    result = pd.DataFrame([{
        'motif': 'TFAP2A',
        'high_ism_count': high_hits,
        'low_ism_count': low_hits,
        'odds_ratio': odds_ratio,
        'p_value': p_value
    }])

    result.to_csv('runs/interpret/tfap2a_enrichment_test.csv', index=False)
    print(f"Results saved to runs/interpret/tfap2a_enrichment_test.csv")

if __name__ == "__main__":
    main()
