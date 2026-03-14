import torch
from src.dataset import encode_dna, make_attention_mask

@torch.no_grad()
def predict_prob_class1(model, seq: str, max_len: int, device):
    model.eval()
    x = encode_dna(seq, max_len).unsqueeze(0).to(device)      # (1,L)
    mask = make_attention_mask(x[0]).unsqueeze(0).to(device)  # (1,L)
    logits = model(x, attn_mask=mask)
    prob = torch.softmax(logits, dim=-1)[0, 1].item()
    return prob
