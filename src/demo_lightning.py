import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import torch
import torch.nn.functional as F
from models.model_alibi import TinyDNAEncoderALiBi
from config import *
from dataset import VOCAB_SIZE
import time

def demo():
    print("=== DNA-SLM LIGHTNING DEMO ===")
    print("--------------------------------")
    
    # 1. Load Model
    print(f"[1/4] Loading model architecture (TinyDNAEncoderALiBi)...")
    device = torch.device("cpu") # CPU is fine for inference
    model = TinyDNAEncoderALiBi(
        vocab_size=VOCAB_SIZE,
        max_len=MAX_LEN,
        d_model=D_MODEL,
        n_layers=N_LAYERS,
        n_heads=N_HEADS,
        d_ff=D_FF,
        dropout=DROPOUT,
        n_classes=N_CLASSES
    ).to(device)
    
    # 2. Load Weights
    print(f"[2/4] Loading trained weights from {CKPT_PATH}...")
    try:
        model.load_state_dict(torch.load(CKPT_PATH, map_location=device))
        model.eval()
        print("      [OK] Weights loaded successfully!")
    except FileNotFoundError:
        print("      [WARN] Checkpoint not found! (Showing behavior with random weights)")

    # 3. Define Test Sequences
    print("[3/4] Preparing test sequences...")
    # Seq A: Contains TFAP2A motif (GCCNNNGGC) - Should be POSITIVE
    seq_a = "ATCG" * 20 + "GCCAAAGGC" + "ATCG" * 100 
    seq_a = seq_a[:500]
    
    # Seq B: Random background - Should be NEGATIVE
    seq_b = "AAAA" * 125
    
    seqs = [("Promoter Candidate", seq_a), ("Random Background", seq_b)]
    
    # 4. Run Inference
    print("[4/4] Running real-time inference...")
    
    vocab = {"A":1, "C":2, "G":3, "T":4, "N":0}
    
    for name, seq in seqs:
        # Tokenize
        tokens = [vocab.get(c, 0) for c in seq]
        tokens = tokens + [0]*(MAX_LEN - len(tokens)) # Pad
        x = torch.tensor([tokens], dtype=torch.long).to(device)
        mask = (x != 0).long()
        
        # Predict
        start = time.time()
        with torch.no_grad():
            logits = model(x, attn_mask=mask)
            probs = F.softmax(logits, dim=-1)
            conf = probs[0][1].item()
            
        dt = (time.time() - start) * 1000
        
        # Result
        label = "POSITIVE (Promoter/Enhancer)" if conf > 0.5 else "NEGATIVE (Background)"
        
        print(f"\n   Sequence: {name}")
        print(f"   Length:   {len(seq)}bp")
        print(f"   Inference: {dt:.2f}ms")
        print(f"   Score:    {conf:.4f}")
        print(f"   Verdict:  {label}")

    print("\n--------------------------------")
    print("[DONE] DEMO COMPLETE")

if __name__ == "__main__":
    demo()
