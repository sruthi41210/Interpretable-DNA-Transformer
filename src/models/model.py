import torch
import torch.nn as nn
import math

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, attn_mask=None):
        # x: (B, L, D)
        B, L, D = x.shape
        qkv = self.qkv(x)  # (B, L, 3D)
        q, k, v = qkv.chunk(3, dim=-1)

        # (B, H, L, Dh)
        q = q.view(B, L, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(B, L, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, L, self.n_heads, self.d_head).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)  # (B,H,L,L)

        if attn_mask is not None:
            # attn_mask: (B, L), 1 for real, 0 for pad
            # convert to (B,1,1,L) and mask pad positions in keys
            key_mask = attn_mask[:, None, None, :].to(dtype=torch.bool)
            scores = scores.masked_fill(~key_mask, float("-inf"))

        attn = torch.softmax(scores, dim=-1)
        attn = self.drop(attn)
        out = attn @ v  # (B,H,L,Dh)
        out = out.transpose(1, 2).contiguous().view(B, L, D)  # (B,L,D)
        return self.out(out)

class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attn = MultiHeadSelfAttention(d_model, n_heads, dropout)
        self.ln1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, attn_mask=None):
        x = x + self.drop(self.attn(self.ln1(x), attn_mask=attn_mask))
        x = x + self.drop(self.ff(self.ln2(x)))
        return x

class TinyDNAEncoder(nn.Module):
    def __init__(self, vocab_size: int, max_len: int, d_model: int = 128, n_layers: int = 4,
                 n_heads: int = 4, d_ff: int = 512, dropout: float = 0.1, n_classes: int = 2):
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
        ])
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_classes)

        self.max_len = max_len

    def forward(self, input_ids, attn_mask=None):
        # input_ids: (B, L)
        B, L = input_ids.shape
        pos_ids = torch.arange(L, device=input_ids.device)[None, :].expand(B, L)

        x = self.tok(input_ids) + self.pos(pos_ids)  # (B,L,D)
        for blk in self.blocks:
            x = blk(x, attn_mask=attn_mask)
        x = self.ln(x)

        # CLS pooling: CLS token is at position 0
        cls = x[:, 0, :]  # (B,D)
        logits = self.head(cls)  # (B,2)
        return logits
