import torch
import torch.nn as nn
import math

# ---------------- ALiBi helpers ----------------

def get_alibi_slopes(n_heads: int):
    """
    From the ALiBi paper.
    Returns slopes for each attention head.
    """
    def get_slopes_power_of_2(n):
        start = 2 ** (-2 ** -(math.log2(n) - 3))
        ratio = start
        return [start * ratio ** i for i in range(n)]

    if math.log2(n_heads).is_integer():
        return torch.tensor(get_slopes_power_of_2(n_heads))
    else:
        closest_power = 2 ** math.floor(math.log2(n_heads))
        slopes = get_slopes_power_of_2(closest_power)
        extra = get_slopes_power_of_2(2 * closest_power)[0::2]
        return torch.tensor(slopes + extra[: n_heads - closest_power])


def build_alibi_bias(seq_len: int, slopes: torch.Tensor, device):
    """
    Creates (n_heads, seq_len, seq_len) bias tensor
    """
    pos = torch.arange(seq_len, device=device)
    rel = pos[None, :] - pos[:, None]
    rel = rel.abs().unsqueeze(0)          # (1, L, L)
    slopes = slopes[:, None, None]        # (H, 1, 1)
    return -slopes * rel                  # negative bias for distant positions


# ---------------- Attention block ----------------

class MultiHeadSelfAttentionALiBi(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)

        slopes = get_alibi_slopes(n_heads)
        self.register_buffer("slopes", slopes)

    def forward(self, x, attn_mask=None):
        B, L, D = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.view(B, L, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(B, L, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, L, self.n_heads, self.d_head).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)

        alibi = build_alibi_bias(L, self.slopes.to(x.device), x.device)
        scores = scores + alibi.unsqueeze(0)

        if attn_mask is not None:
            scores = scores.masked_fill(attn_mask[:, None, None, :] == 0, -1e9)

        attn = torch.softmax(scores, dim=-1)
        out = attn @ v

        out = out.transpose(1, 2).contiguous().view(B, L, D)
        return self.out(out)


# ---------------- Transformer block ----------------

class TransformerBlockALiBi(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout):
        super().__init__()
        self.attn = MultiHeadSelfAttentionALiBi(d_model, n_heads)
        self.ln1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )
        self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, attn_mask=None):
        x = x + self.drop(self.attn(self.ln1(x), attn_mask))
        x = x + self.drop(self.ff(self.ln2(x)))
        return x


# ---------------- Full model ----------------

class TinyDNAEncoderALiBi(nn.Module):
    def __init__(
        self,
        vocab_size,
        max_len,
        d_model,
        n_layers,
        n_heads,
        d_ff,
        dropout,
        n_classes,
    ):
        super().__init__()

        self.embed = nn.Embedding(vocab_size, d_model)
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model))

        self.blocks = nn.ModuleList([
            TransformerBlockALiBi(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_classes)

    def forward(self, x, attn_mask=None):
        B, L = x.shape

        x = self.embed(x)

        cls = self.cls.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)

        if attn_mask is not None:
            cls_mask = torch.ones(B, 1, device=x.device)
            attn_mask = torch.cat([cls_mask, attn_mask], dim=1)

        for block in self.blocks:
            x = block(x, attn_mask)

        x = self.norm(x)
        return self.head(x[:, 0])
