import os, json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.metrics import compute_all

@torch.no_grad()
def eval_gold(model, ds, device, batch_size=256, num_workers=2, out_dir=None, prefix="test"):
    model.eval()
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    all_logits = []
    all_y = []

    for x, mask, y in tqdm(dl, desc=f"eval_{prefix}", leave=False):
        x = x.to(device, non_blocking=True)
        mask = mask.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        logits = model(x, attn_mask=mask)  # (B, C)
        # for binary classification with CrossEntropyLoss: take logit for class 1
        if logits.shape[-1] == 2:
            logit_pos = logits[:, 1]
        else:
            # if you ever switch to single-logit BCE, handle here
            logit_pos = logits.squeeze(-1)

        all_logits.append(logit_pos.detach().float().cpu().numpy())
        all_y.append(y.detach().cpu().numpy())

    all_logits = np.concatenate(all_logits)
    all_y = np.concatenate(all_y)

    metrics, prob = compute_all(all_y, all_logits)

    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, f"metrics_{prefix}.json"), "w") as f:
            json.dump(metrics, f, indent=2)

        pd.DataFrame({"y": all_y, "logit": all_logits, "prob": prob}).to_csv(
            os.path.join(out_dir, f"preds_{prefix}.csv"),
            index=False
        )

    return metrics
