"""
Save all hyperparameters from config.py to a structured JSON file.
Usage:  python src/save_hparams.py
"""
import json, os, sys

# Allow importing from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import config as cfg


def main():
    hparams = {
        "model": {
            "max_len": cfg.MAX_LEN,
            "d_model": cfg.D_MODEL,
            "n_layers": cfg.N_LAYERS,
            "n_heads": cfg.N_HEADS,
            "d_ff": cfg.D_FF,
            "dropout": cfg.DROPOUT,
            "n_classes": cfg.N_CLASSES,
        },
        "training": {
            "batch_size": cfg.BATCH_SIZE,
            "epochs": cfg.EPOCHS,
            "learning_rate": cfg.LR,
            "optimizer": "AdamW",
            "amp": True,
            "reverse_complement_augmentation": True,
        },
        "early_stopping": {
            "patience": cfg.PATIENCE,
            "min_delta": cfg.MIN_DELTA,
            "monitor": "val_pr_auc",
        },
        "data": {
            "dataset_train": cfg.DATASET_TRAIN,
            "dataset_test": cfg.DATASET_TEST,
            "run_name": cfg.RUN_NAME,
            "checkpoint": cfg.CKPT_PATH,
            "tokenisation": "character-level (A=0, C=1, G=2, T=3)",
            "sequence_length": 500,
        },
        "seed": 42,
    }

    out_path = "runs/hparams.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(hparams, f, indent=2)
    print(f"Saved hyperparameters to {out_path}")


if __name__ == "__main__":
    main()
