import torch
from sklearn.metrics import roc_auc_score

def batch_auc(logits: torch.Tensor, labels: torch.Tensor) -> float:
    # for binary classification, use prob of class 1
    probs = torch.softmax(logits, dim=-1)[:, 1].detach().cpu().numpy()
    y = labels.detach().cpu().numpy()
    # if only one class in batch, auc is undefined -> return nan
    if len(set(y.tolist())) < 2:
        return float("nan")
    return float(roc_auc_score(y, probs))
