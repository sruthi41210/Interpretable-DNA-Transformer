import pandas as pd
import numpy as np
import os
from Bio import motifs
from Bio.Seq import Seq
from collections import Counter
import logomaker
import matplotlib.pyplot as plt

def extract_enriched_kmers(sequences, k=6, top_n=50):
    kmer_counts = Counter()
    for seq in sequences:
        seq_str = str(seq).upper()
        for i in range(len(seq_str) - k + 1):
            kmer = seq_str[i:i+k]
            if 'N' not in kmer and len(kmer) == k:
                kmer_counts[kmer] += 1
    return kmer_counts.most_common(top_n)

def kmers_to_pwm(kmer_list, k=6):
    instances = [Seq(kmer) for kmer, count in kmer_list]
    if not instances: return None
    m = motifs.create(instances)
    pwm = m.counts.normalize(pseudocounts=0.5)
    return pwm

def pwm_to_dataframe(pwm):
    return pd.DataFrame({'A': pwm['A'], 'C': pwm['C'], 'G': pwm['G'], 'T': pwm['T']})

def compare_to_jaspar(query_pwm_df, jaspar_file):
    with open(jaspar_file) as handle:
        # Use jaspar format as it was reliable in jaspar_compare.py
        jaspar_motifs = motifs.parse(handle, 'jaspar')
    
    best_matches = []
    
    # Query PWM as (4, K)
    q_pwm = query_pwm_df[['A', 'C', 'G', 'T']].values.T
    K = q_pwm.shape[1]
    
    for jm in jaspar_motifs:
        # Get JASPAR PWM (4, L)
        j_counts = np.array([jm.counts[b] for b in "ACGT"])
        j_pwm = j_counts / (j_counts.sum(axis=0, keepdims=True) + 1e-9)
        L = j_pwm.shape[1]
        
        if L < K: continue # Skip if target shorter than query
        
        best_corr = -1.0
        
        # Check both strands
        for strand in [q_pwm, np.flip(q_pwm[[3, 2, 1, 0], :], axis=1)]:
            # Slide query over jaspar motif
            for start in range(L - K + 1):
                sub = j_pwm[:, start:start+K]
                corr = np.corrcoef(strand.flatten(), sub.flatten())[0, 1]
                if corr > best_corr:
                    best_corr = corr
            
        best_matches.append({
            'jaspar_id': jm.matrix_id,
            'jaspar_name': jm.name,
            'correlation': best_corr,
        })
    
    return pd.DataFrame(best_matches).sort_values('correlation', ascending=False)

def main():
    from Bio import SeqIO
    fasta_path = 'runs/interpret/high_ism_windows.fa'
    jaspar_path = 'data/JASPAR2024_CORE_vertebrates.txt'
    
    if not os.path.exists(fasta_path): return
    sequences = [rec.seq for rec in SeqIO.parse(fasta_path, 'fasta')]
    print(f"Analyzing {len(sequences)} high-ISM windows...")
    
    # Focus on k=6 since windows are 6bp
    for k in [6]:
        print(f"\n=== k={k} analysis ===")
        top_kmers = extract_enriched_kmers(sequences, k=k, top_n=20)
        
        print(f"Top 10 {k}-mers:")
        for kmer, count in top_kmers[:10]:
            print(f"  {kmer}: {count}")
        
        pwm = kmers_to_pwm(top_kmers, k=k)
        if pwm:
            pwm_df = pwm_to_dataframe(pwm)
            pwm_df.to_csv(f'runs/interpret/discovered_motif_k{k}.csv', index=False)
            
            logo = logomaker.Logo(pwm_df)
            logo.fig.savefig(f'runs/interpret/motif_logo_k{k}.png', dpi=300)
            plt.close(logo.fig)
            
            if os.path.exists(jaspar_path):
                print("Matching to JASPAR...")
                matches = compare_to_jaspar(pwm_df, jaspar_path)
                print(matches.head(5))
                matches.to_csv(f'runs/interpret/jaspar_matches_k{k}.csv', index=False)

if __name__ == '__main__':
    main()
