import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

def precision_recall_at_k(y_true, y_score, k):
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score)
    n = len(y_true)

    kk = int(k*n) if 0 < k <= 1 else int(k)
    kk = max(1, min(n, kk))

    idx = np.argsort(-y_score)[:kk]
    tp = y_true[idx].sum()
    prec = tp / kk
    rec = tp / max(1, y_true.sum())
    return float(prec), float(rec), kk

def ece_score(y_true, y_prob, n_bins=10):
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob)
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        lo, hi = bins[i], bins[i+1]
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += (mask.mean()) * abs(acc - conf)
    return float(ece)

def compute_all(y_true, logits):
    y_true = np.asarray(y_true).astype(int)
    logits = np.asarray(logits, dtype=float)
    prob = 1.0 / (1.0 + np.exp(-logits))

    out = {}
    if len(np.unique(y_true)) > 1:
        out["roc_auc"] = float(roc_auc_score(y_true, prob))
        out["pr_auc"]  = float(average_precision_score(y_true, prob))
    else:
        out["roc_auc"] = float("nan")
        out["pr_auc"]  = float("nan")

    out["ece_10"] = ece_score(y_true, prob, n_bins=10)

    # prioritization metrics
    for k in [0.01, 0.05, 100]:
        p, r, kk = precision_recall_at_k(y_true, prob, k)
        if isinstance(k, float):
            out[f"p@{int(k*100)}%"] = p
            out[f"r@{int(k*100)}%"] = r
        else:
            out[f"p@{kk}"] = p
            out[f"r@{kk}"] = r

    return out, prob
