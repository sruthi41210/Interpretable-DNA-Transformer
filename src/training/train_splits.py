import argparse, os, json
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from torch.amp import autocast, GradScaler

from src.split_data import load_split_df
from src.dataset import DNADFClassificationDataset, VOCAB_SIZE #<- from your dataset module
from src.config import *  # reuse your hyperparams for defaults
from src.evaluate_gold import eval_gold


# pick model based on flag
def build_model(model_name: str, device):
    if model_name == "baseline":
        from model import TinyDNAEncoder as ModelCls
    elif model_name == "alibi":
        # adjust import name to match your repo
        from src.model_alibi import TinyDNAEncoderALiBi as ModelCls
    else:
        raise ValueError(f"Unknown model: {model_name}")

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
    return model

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--model", choices=["baseline", "alibi"], default="alibi")
    ap.add_argument("--fraction", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rc_mode", choices=["none", "aug", "siamese"], default="aug")  # siamese later
    ap.add_argument("--batch_size", type=int, default=BATCH_SIZE)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--lr", type=float, default=LR)
    ap.add_argument("--weight_decay", type=float, default=0.01)
    ap.add_argument("--grad_accum", type=int, default=2)
    ap.add_argument("--num_workers", type=int, default=4)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)
    if device.type == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))

    os.makedirs(args.out_dir, exist_ok=True)

    # ---- Load split dfs ----
    train_df = load_split_df(args.splits_csv, "train", fraction=args.fraction, seed=args.seed, seq_col="seq", label_col="label")
    val_df   = load_split_df(args.splits_csv, "val",   fraction=1.0, seed=args.seed, seq_col="seq", label_col="label")
    test_df  = load_split_df(args.splits_csv, "test",  fraction=1.0, seed=args.seed, seq_col="seq", label_col="label")

    print(f"Train n={len(train_df)} | Val n={len(val_df)} | Test n={len(test_df)} | frac={args.fraction}")

    # ---- Datasets ----
    # keep your existing augmentation behavior when args.rc_mode == aug
    augment_train = (args.rc_mode == "aug")
    train_ds = DNADFClassificationDataset(train_df, max_len=MAX_LEN, augment=augment_train)
    val_ds   = DNADFClassificationDataset(val_df,   max_len=MAX_LEN, augment=False)
    test_ds  = DNADFClassificationDataset(test_df,  max_len=MAX_LEN, augment=False)

    train_dl = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True,
        persistent_workers=True
    )

    # ---- Model ----
    model = build_model(args.model, device)

    # ---- Optimizer / Loss ----
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    loss_fn = torch.nn.CrossEntropyLoss()

    scaler = GradScaler("cuda", enabled=(device.type == "cuda"))
    best_val = -1.0
    bad = 0

    for ep in range(1, args.epochs + 1):
        model.train()
        opt.zero_grad(set_to_none=True)
        running = 0.0
        steps = 0

        pbar = tqdm(train_dl, desc=f"epoch {ep}", leave=False)
        for step, (x, mask, y) in enumerate(pbar, start=1):
            x = x.to(device, non_blocking=True)
            mask = mask.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            with autocast("cuda", enabled=(device.type == "cuda")):
                logits = model(x, attn_mask=mask)
                loss = loss_fn(logits, y) / args.grad_accum

            scaler.scale(loss).backward()

            if step % args.grad_accum == 0:
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)

            running += loss.item() * args.grad_accum
            steps += 1

        mean_loss = running / max(steps, 1)

        # ---- Validate (gold metrics) ----
        val_metrics = eval_gold(model, val_ds, device, batch_size=512, num_workers=2, out_dir=args.out_dir, prefix="val")
        val_auc = val_metrics.get("roc_auc", float("nan"))

        # early stopping uses VAL (not test)
        if val_auc > best_val + MIN_DELTA:
            best_val = val_auc
            bad = 0
            torch.save(model.state_dict(), os.path.join(args.out_dir, "best.pt"))
            print(f"  saved best val_auc={best_val:.4f}")
        else:
            bad += 1
            print(f"  no improv ({bad}/{PATIENCE}) best_val={best_val:.4f}")

        if bad >= PATIENCE:
            print("Early stopping on val.")
            break

        print(f"Epoch {ep:02d} | loss={mean_loss:.4f} | val_auc={val_auc:.4f}")

    # ---- Test with best checkpoint ----
    best_path = os.path.join(args.out_dir, "best.pt")
    if os.path.exists(best_path):
        model.load_state_dict(torch.load(best_path, map_location=device))

    test_metrics = eval_gold(model, test_ds, device, batch_size=512, num_workers=2, out_dir=args.out_dir, prefix="test")
    with open(os.path.join(args.out_dir, "run_summary.json"), "w") as f:
        json.dump({"best_val_auc": best_val, "test_metrics": test_metrics}, f, indent=2)

    print("DONE. Test metrics:", test_metrics)

if __name__ == "__main__":
    main()
