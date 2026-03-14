# src/config.py

DATASET_TRAIN = "data/enh_train.csv"
DATASET_TEST  = "data/enh_test.csv"
RUN_NAME = "enh_alibi"
CKPT_PATH = f"runs/checkpoints/{RUN_NAME}.pt"


MAX_LEN   = 512
D_MODEL   = 192
N_LAYERS  = 6
N_HEADS   = 6      # must divide D_MODEL
D_FF      = 768
DROPOUT   = 0.1
N_CLASSES = 2

BATCH_SIZE = 32
EPOCHS     = 35
LR         = 3e-4

MIN_DELTA = 0.0005
PATIENCE = 5



