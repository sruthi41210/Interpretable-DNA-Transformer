import torch
import numpy as np
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader
from dataset import DNACSVClassificationDataset

@torch.no_grad()
def eval_auc(model, csv_path, max_len, device, batch_size=128):
    ds = DNACSVClassificationDataset(csv_path, max_len=max_len)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model.eval()
    probs, ys = [], []
    for x, mask, y in dl:
        x, mask = x.to(device), mask.to(device)
        logits = model(x, attn_mask=mask)
        p = torch.softmax(logits, dim=-1)[:, 1].detach().cpu().numpy()
        probs.append(p)
        ys.append(y.numpy())

    probs = np.concatenate(probs)
    ys = np.concatenate(ys)
    return float(roc_auc_score(ys, probs))
