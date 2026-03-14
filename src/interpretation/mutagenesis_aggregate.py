import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import argparse

from src.dataset import VOCAB_SIZE
from src.model import TinyDNAEncoder
from src.model_alibi import TinyDNAEncoderALiBi 
from src.config import *
from src.predict import predict_prob_class1


DNA = ["A", "C", "G", "T"]

def mutate_window(seq: str, start: int, w: int) -> str:
    seq = list(seq)
    for i in range(start, min(start + w, len(seq))):
        orig = seq[i]
        choices = [b for b in DNA if b != orig]
        seq[i] = random.choice(choices)
    return "".join(seq)

def importance_curve(model, seq: str, base_score: float, window: int, stride: int, device):
    L = len(seq)
    drops = np.zeros(L, dtype=np.float32)

    for start in range(0, L - window + 1, stride):
        mutated = mutate_window(seq, start, window)
        mscore = predict_prob_class1(model, mutated, MAX_LEN, device)
        drop = base_score - mscore
        # spread credit across the window
        drops[start:start+window] += drop

    # normalize per-sequence (prevents one sequence dominating)
    mx = float(drops.max())
    if mx > 1e-9:
        drops = drops / mx
    return drops

def main():
    random.seed(42)
    np.random.seed(42)
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", choices=["baseline", "alibi"], default="baseline")
    parser.add_argument("--ckpt", type=str, default=CKPT_PATH)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # load model
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

    df = pd.read_csv(DATASET_TEST)

    # ---- choose sequences: high-confidence true positives ----
    pos = df[df["label"] == 1].copy()

    # score a subset to avoid slow full scoring
    N_SCORE = min(400, len(pos))
    pos = pos.head(N_SCORE)

    scores = []
    for s in pos["seq"]:
        scores.append(predict_prob_class1(model, s, MAX_LEN, device))
    pos["score"] = scores
    pos = pos.sort_values("score", ascending=False)

    N = 250  # number of sequences for aggregation
    chosen = pos.head(N).copy()

    window = 6
    stride = 1

    curves = []
    top_rows = []  # for top windows export

    for idx, row in chosen.iterrows():
        seq = row["seq"]
        base = float(row["score"])

        drops = importance_curve(model, seq, base, window, stride, device)
        curves.append(drops)

        # extract top windows from this seq
        K = 20  # top windows per sequence
        # compute window scores by summing drops in window
        L = len(seq)
        w_scores = []
        for start in range(0, L - window + 1, stride):
            w_scores.append((float(drops[start:start+window].mean()), start))
        w_scores.sort(reverse=True)

        for rank in range(min(K, len(w_scores))):
            sc, start = w_scores[rank]
            subseq = seq[start:start+window]
            top_rows.append({
                "seq_index": int(idx),
                "base_score": base,
                "rank": rank + 1,
                "start": start,
                "window": window,
                "window_importance": sc,
                "subseq": subseq
            })

    curves = np.stack(curves, axis=0)  # (N, L)
    mean_curve = curves.mean(axis=0)
    std_curve = curves.std(axis=0)

    # ---- plot aggregate ----
    plt.figure(figsize=(14, 4))
    plt.plot(mean_curve, label="mean importance")
    plt.fill_between(np.arange(len(mean_curve)),
                     mean_curve - std_curve,
                     mean_curve + std_curve,
                     alpha=0.2, label="±1 std")
    plt.title(f"Aggregated in-silico mutagenesis | N={N} | window={window}")
    plt.xlabel("Position in sequence")
    plt.ylabel("Normalized importance (per-seq normalized)")
    plt.legend()
    plt.tight_layout()
    tag = args.arch
    plt.savefig(f"runs/mutagenesis_aggregate_{tag}.png", dpi=200)
    print(f"Saved runs/mutagenesis_aggregate_{tag}.png")

    # ---- save top windows ----
    out = pd.DataFrame(top_rows).sort_values(["window_importance"], ascending=False)
        
    out.to_csv(f"runs/top_windows_{tag}.csv", index=False)
    print(f"Saved runs/top_windows_{tag}.csv")

if __name__ == "__main__":
    main()
