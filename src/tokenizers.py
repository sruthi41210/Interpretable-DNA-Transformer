# src/tokenizers.py
from dataclasses import dataclass

DNA_VOCAB = {"A":0, "C":1, "G":2, "T":3, "N":4}

def rc_seq(s: str) -> str:
    comp = {"A":"T","T":"A","C":"G","G":"C","N":"N"}
    s = s.upper()
    return "".join(comp.get(ch, "N") for ch in s[::-1])


@dataclass
class CharTokenizer:
    pad_id: int = 5
    unk_id: int = 4  # N
    vocab_size: int = 6  # A,C,G,T,N,PAD
    def encode(self, s: str):
        ids = []
        for ch in s.upper():
            ids.append(DNA_VOCAB.get(ch, self.unk_id))
        return ids

@dataclass
class KmerTokenizer:
    k: int = 3
    pad_id: int = None
    unk_id: int = None
    def __post_init__(self):
        # k-mer vocab: 4^k, map A,C,G,T only; anything with N -> UNK
        self.base = 4
        self.vocab_size = (self.base ** self.k) + 2
        self.unk_id = self.base ** self.k
        self.pad_id = self.base ** self.k + 1
        self.map4 = {"A":0,"C":1,"G":2,"T":3}

    def encode(self, s: str):
        s = s.upper()
        out = []
        for i in range(0, len(s) - self.k + 1):
            kmer = s[i:i+self.k]
            ok = True
            val = 0
            for ch in kmer:
                if ch not in self.map4:
                    ok = False
                    break
                val = val * 4 + self.map4[ch]
            out.append(val if ok else self.unk_id)
        return out
