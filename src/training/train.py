import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from torch.amp import autocast, GradScaler

from dataset import DNACSVClassificationDataset, VOCAB_SIZE
from model import TinyDNAEncoder
from config import *
from evaluate_full import eval_auc

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)
    if device.type == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))

    # ---- Data ----
    train_ds = DNACSVClassificationDataset(DATASET_TRAIN, max_len=MAX_LEN, augment=True)
    train_dl = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4,
        pin_memory=True,
        persistent_workers=True
    )


    # ---- Model ----
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

    # ---- Optimizer / Loss ----
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    loss_fn = torch.nn.CrossEntropyLoss()

    # ---- AMP + Grad Accum ----
    grad_accum = 2  # effective batch size = BATCH_SIZE * grad_accum
    scaler = GradScaler("cuda", enabled=(device.type == "cuda"))


    for ep in range(1, EPOCHS + 1):
        model.train()
        running_loss = 0.0
        steps = 0

        opt.zero_grad(set_to_none=True)

        pbar = tqdm(train_dl, desc=f"epoch {ep}", leave=False)
        for step, (x, mask, y) in enumerate(pbar, start=1):
            # Move to GPU
            x = x.to(device, non_blocking=True)
            mask = mask.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            with autocast("cuda", enabled=(device.type == "cuda")): 
                logits = model(x, attn_mask=mask)
                loss = loss_fn(logits, y) / grad_accum

            scaler.scale(loss).backward()

            # update weights every grad_accum steps
            if step % grad_accum == 0:
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)

            running_loss += loss.item() * grad_accum  # undo divide for reporting
            steps += 1

        mean_loss = running_loss / max(steps, 1)

        # Proper evaluation on held-out test
        test_auc = eval_auc(model, DATASET_TEST, MAX_LEN, device)
        best_auc = getattr(main, "best_auc", -1.0)
        bad_epochs = getattr(main, "bad_epochs", 0)

        if test_auc > best_auc + MIN_DELTA:
            best_auc = test_auc
            bad_epochs = 0
            torch.save(model.state_dict(), CKPT_PATH)
            print(f"  saved new best: {best_auc:.4f}")
        else:
            bad_epochs += 1
            print(f"  no improv ({bad_epochs}/{PATIENCE}) best={best_auc:.4f}")

        main.best_auc = best_auc
        main.bad_epochs = bad_epochs

        if bad_epochs >= PATIENCE:
            print("Early stopping.")
            break

        print(f"Epoch {ep:02d} | loss={mean_loss:.4f} | test_auc={test_auc:.4f}")

    # ---- Save ----
    torch.save(model.state_dict(), CKPT_PATH)
    print(f"Saved {CKPT_PATH}")


if __name__ == "__main__":
    main()
