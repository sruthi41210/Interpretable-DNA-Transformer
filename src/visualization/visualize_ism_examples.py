import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import argparse
import os

from src.dataset import VOCAB_SIZE
from src.model import TinyDNAEncoder
from src.model_alibi import TinyDNAEncoderALiBi 
from src.config import *
from src.predict import predict_prob_class1
from src.mutagenesis_aggregate import importance_curve

def plot_single_sequence(seq, importance, title, filename, top_k=5):
    L = len(seq)
    plt.figure(figsize=(15, 6))
    
    # Use a nice color for the importance curve
    plt.plot(importance, color='#1f77b4', linewidth=2, label='Importance Score')
    plt.fill_between(range(L), importance, color='#1f77b4', alpha=0.3)
    
    # Find and highlight top windows
    window = 6
    w_scores = []
    for start in range(L - window + 1):
        w_scores.append((importance[start:start+window].mean(), start))
    w_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Highlight top peaks
    for i in range(min(top_k, len(w_scores))):
        score, start = w_scores[i]
        plt.axvspan(start, start + window, color='orange', alpha=0.2, label='Top Motif Region' if i == 0 else "")
        plt.text(start + window/2, score + 0.05, seq[start:start+window], 
                 rotation=90, ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Sequence Position", fontsize=12)
    plt.ylabel("Normalized Importance", fontsize=12)
    plt.ylim(0, 1.2)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Add sequence characters along the x-axis if short enough, otherwise just positions
    if L <= 200:
        plt.xticks(range(0, L, 10), [f"{i}\n{seq[i]}" if i < L else i for i in range(0, L, 10)])
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", choices=["baseline", "alibi"], default="baseline")
    parser.add_argument("--ckpt", type=str, default=CKPT_PATH)
    parser.add_argument("--n_examples", type=int, default=5)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs("runs/visuals", exist_ok=True)

    # Load model
    ModelCls = TinyDNAEncoderALiBi if args.arch == "alibi" else TinyDNAEncoder
    model = ModelCls(
        vocab_size=VOCAB_SIZE,
        max_len=MAX_LEN,
        d_model=D_MODEL,
        n_layers=N_LAYERS,
        n_heads=N_HEADS,
        d_ff=D_FF,
        dropout=DROPOUT,
        n_classes=N_CLASSES
    ).to(device)
    
    model.load_state_dict(torch.load(args.ckpt, map_location=device))
    model.eval()

    # Load test data
    df = pd.read_csv(DATASET_TEST)
    pos = df[df["label"] == 1].copy()
    
    # Score to find best examples
    print(f"Scoring {len(pos)} sequences to find top examples...")
    scores = []
    for s in pos["seq"]:
        scores.append(predict_prob_class1(model, s, MAX_LEN, device))
    pos["score"] = scores
    pos = pos.sort_values("score", ascending=False)
    
    top_examples = pos.head(args.n_examples)
    
    window = 6
    stride = 1
    
    for i, (idx, row) in enumerate(top_examples.iterrows()):
        seq = row["seq"]
        base_score = float(row["score"])
        
        print(f"Generating plot for example {i+1}/{args.n_examples} (Score: {base_score:.4f})...")
        importance = importance_curve(model, seq, base_score, window, stride, device)
        
        filename = f"runs/visuals/ism_example_{args.arch}_{idx}.png"
        title = f"ISM Importance Curve | {args.arch.upper()} Model | Prob: {base_score:.3f}"
        plot_single_sequence(seq, importance, title, filename)
        print(f"Saved: {filename}")

if __name__ == "__main__":
    main()
