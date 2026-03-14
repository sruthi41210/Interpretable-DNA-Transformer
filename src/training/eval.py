import torch
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, confusion_matrix

from dataset import DNACSVClassificationDataset, VOCAB_SIZE
from model import TinyDNAEncoder

from config import *

def main():
    csv_path = DATASET_TEST
    max_len = MAX_LEN
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



    ds = DNACSVClassificationDataset(csv_path, max_len=max_len)
    dl = DataLoader(ds, batch_size=32, shuffle=False)

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
    model.to(device)
    model.eval()

    all_probs = []
    all_y = []
    all_pred = []

    with torch.no_grad():
        for x, mask, y in dl:
            x, mask = x.to(device), mask.to(device)
            logits = model(x, attn_mask=mask)
            probs = torch.softmax(logits, dim=-1)[:, 1].cpu().numpy()
            pred = torch.argmax(logits, dim=-1).cpu().numpy()

            all_probs.extend(probs.tolist())
            all_pred.extend(pred.tolist())
            all_y.extend(y.numpy().tolist())

    auc = roc_auc_score(all_y, all_probs) if len(set(all_y)) > 1 else float("nan")
    cm = confusion_matrix(all_y, all_pred)
    print("AUC:", auc)
    print("Confusion matrix:\n", cm)

if __name__ == "__main__":
    main()
