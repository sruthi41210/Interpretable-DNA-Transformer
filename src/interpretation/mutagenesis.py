import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch

from dataset import VOCAB_SIZE
from model import TinyDNAEncoder
from config import *
from predict import predict_prob_class1

DNA = ["A", "C", "G", "T"]

def mutate_window(seq: str, start: int, w: int) -> str:
    seq = list(seq)
    for i in range(start, min(start + w, len(seq))):
        orig = seq[i]
        choices = [b for b in DNA if b != orig]
        seq[i] = random.choice(choices)
    return "".join(seq)

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # load model
    model = TinyDNAEncoder(
        vocab_size=VOCAB_SIZE,
        max_len=MAX_LEN,
        d_model=D_MODEL,
        n_layers=N_LAYERS,
        n_heads=N_HEADS,
        d_ff=D_FF,
        dropout=DROPOUT,
        n_classes=N_CLASSES
    ).to(device)
    model.load_state_dict(torch.load(CKPT_PATH, map_location=device))
    model.eval()

    # load test data
    df = pd.read_csv(DATASET_TEST)

    # pick a high-confidence true positive (label=1)
    pos = df[df["label"] == 1].copy()
    # compute baseline scores for first N positives (fast enough)
    N = 200
    pos = pos.head(N)
    scores = []
    for s in pos["seq"]:
        scores.append(predict_prob_class1(model, s, MAX_LEN, device))
    pos["score"] = scores
    pos = pos.sort_values("score", ascending=False)

    seq = pos.iloc[0]["seq"]
    base_score = pos.iloc[0]["score"]
    print("Picked positive with base score:", base_score)

    # mutagenesis params
    window = 6
    stride = 1

    L = len(seq)
    drops = np.zeros(L)

    for start in range(0, L - window + 1, stride):
        mutated = mutate_window(seq, start, window)
        mscore = predict_prob_class1(model, mutated, MAX_LEN, device)
        drop = base_score - mscore
        drops[start:start+window] += drop  # spread credit across window

    # normalize
    drops = drops / (drops.max() + 1e-9)

    # plot
    plt.figure(figsize=(14, 3))
    plt.plot(drops)
    plt.title(f"In-silico mutagenesis importance (window={window}) | base={base_score:.3f}")
    plt.xlabel("Position in sequence")
    plt.ylabel("Normalized importance")
    plt.tight_layout()
    plt.savefig("runs/mutagenesis_example.png", dpi=200)
    print("Saved runs/mutagenesis_example.png")

if __name__ == "__main__":
    main()
