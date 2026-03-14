import matplotlib.pyplot as plt
import numpy as np
import regex
import os
from Bio import SeqIO

def find_motif_positions(sequence, pattern='GCC[ACGT]{3}GGC'):
    """Find all positions of motif in sequence with soft matching"""
    positions = []
    for match in regex.finditer(f'({pattern}){{s<=1}}', str(sequence).upper(), overlapped=True):
        positions.append(match.start())
    return positions

def main():
    high_fa = "runs/interpret/high_ism_windows_context.fa"
    if not os.path.exists(high_fa):
        print(f"Error: {high_fa} not found.")
        return

    # Collect all TFAP2A positions
    print("Analyzing TFAP2A positions in high-ISM context windows...")
    all_positions = []
    for rec in SeqIO.parse(high_fa, "fasta"):
        positions = find_motif_positions(rec.seq)
        # Note: Position 10 is the start of the original 6bp target window
        all_positions.extend(positions)

    if not all_positions:
        print("No TFAP2A matches found to plot.")
        return

    # Plot histogram
    plt.figure(figsize=(10, 5))
    bins = np.arange(0, 30, 1) # 10 (left) + 6 (window) + 10 (right) = 26bp total
    plt.hist(all_positions, bins=bins, edgecolor='black', alpha=0.7, color='#2ca02c')
    
    # Highlight the target window
    plt.axvspan(10, 16, color='red', alpha=0.2, label='High-Importance Window (6bp)')
    
    plt.xlabel('Start Position along 26bp Context Region')
    plt.ylabel('Frequency')
    plt.title('TFAP2A Motif Positional Distribution')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    os.makedirs('runs/interpret', exist_ok=True)
    plt.savefig('runs/interpret/tfap2a_position_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Found {len(all_positions)} TFAP2A motif match start positions")
    print(f"Mean position: {np.mean(all_positions):.1f}")
    print(f"Saved plot to runs/interpret/tfap2a_position_distribution.png")

if __name__ == "__main__":
    main()
