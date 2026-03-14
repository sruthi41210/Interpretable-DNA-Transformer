import random
import pandas as pd
import torch
from torch.utils.data import Dataset

DNA_VOCAB = {"A": 0, "C": 1, "G": 2, "T": 3, "N": 4}
PAD_ID = 5  # padding token
CLS_ID = 6  # classification token
VOCAB_SIZE = 7  # A,C,G,T,N,PAD,CLS
_COMP = str.maketrans({"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"})

def revcomp(seq: str) -> str:
    seq = seq.upper()
    return seq.translate(_COMP)[::-1]


def encode_dna(seq: str, max_len: int) -> torch.Tensor:
    seq = seq.upper()
    ids = [CLS_ID]  # prepend CLS
    for ch in seq:
        ids.append(DNA_VOCAB.get(ch, DNA_VOCAB["N"]))
    # pad / truncate to max_len
    ids = ids[:max_len]
    if len(ids) < max_len:
        ids += [PAD_ID] * (max_len - len(ids))
    return torch.tensor(ids, dtype=torch.long)

def make_attention_mask(input_ids: torch.Tensor) -> torch.Tensor:
    # 1 for real tokens, 0 for PAD
    return (input_ids != PAD_ID).long()

class DNACSVClassificationDataset(Dataset):
    def __init__(self, csv_path: str, max_len: int = 128, augment: bool = False):
        df = pd.read_csv(csv_path)
        self.seqs = df["seq"].astype(str).tolist()
        self.labels = df["label"].astype(int).tolist()
        self.max_len = max_len
        self.augment = augment

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx: int):
        seq = self.seqs[idx]

        # Reverse-complement augmentation (training only)
        if self.augment and random.random() < 0.5:
            seq = revcomp(seq)

        x = encode_dna(seq, self.max_len)
        mask = make_attention_mask(x)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, mask, y

class DNADFClassificationDataset(Dataset):
    """
    DataFrame-backed version for splits workflow.
    Expects df with columns: seq, label (same as your CSV format).
    Returns: x, mask, y (same as DNACSVClassificationDataset)
    """
    def __init__(self, df: pd.DataFrame, max_len: int = 128, augment: bool = False):
        self.seqs = df["seq"].astype(str).tolist()
        self.labels = df["label"].astype(int).tolist()
        self.max_len = max_len
        self.augment = augment

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx: int):
        seq = self.seqs[idx]

        # Reverse-complement augmentation (training only)
        if self.augment and random.random() < 0.5:
            seq = revcomp(seq)

        x = encode_dna(seq, self.max_len)
        mask = make_attention_mask(x)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, mask, y


class DNADFRCSiameseDataset(Dataset):
    """
    Returns both forward and reverse-complement tokenizations:
      x, mask, x_rc, mask_rc, y
    Used for rc_mode=siamese in training/eval.
    """
    def __init__(self, df: pd.DataFrame, max_len: int = 128):
        self.seqs = df["seq"].astype(str).tolist()
        self.labels = df["label"].astype(int).tolist()
        self.max_len = max_len

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx: int):
        seq = self.seqs[idx]
        seq_rc = revcomp(seq)

        x = encode_dna(seq, self.max_len)
        mask = make_attention_mask(x)

        x_rc = encode_dna(seq_rc, self.max_len)
        mask_rc = make_attention_mask(x_rc)

        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, mask, x_rc, mask_rc, y
