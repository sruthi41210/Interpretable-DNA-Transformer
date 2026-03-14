# DNA-SLM: The Technical Deep Dive
## For when "It's a Transformer" isn't enough.

---

## 1. THE ARCHITECTURE: TinyDNAEncoder vs Standard BERT
You built a **Transformer Encoder**, specifically designed for small-data genomics.

### Why not BERT?
*   **BERT (Base):** 110M parameters. Needs 10GB+ GPU VRAM. Overfits on 65k sequences.
*   **TinyDNAEncoder:** 2.1M parameters. Runs on <2GB VRAM.
    *   **Embeddings:** Dimension $d_{model} = 192$ (Standard BERT is 768).
    *   **Layers:** 4 Layers (Standard BERT is 12).
    *   **Heads:** 6 Attention Heads.

### The "ALiBi" Mechanism (Attention with Linear Biases)
**The Math:**
Standard Self-Attention calculates scores as:
$$Attention(Q, K) = Softmax(\frac{QK^T}{\sqrt{d_k}})$$

ALiBi adds a static, non-learned penalty based on how far two tokens ($i$ and $j$) are:
$$Score_{i,j} = Q_i K_j^T - m \cdot |i - j|$$

*   $|i - j|$ is the distance (lag) between two DNA bases.
*   $m$ is a specific slope for each attention head (e.g., $m = \frac{1}{2^1}, \frac{1}{2^2}, ...$).
*   **Why it works:** The model doesn't need to "learn" that distance matters. We hard-code the bias that "nearby things interact more," which is biologically true for DNA (e.g., TATA box is near the start site). This allows **Extrapolation**: the model can handle sequence lengths it never saw during training because the math holds up for any distance $|i-j|$.

---

## 2. THE INTERPRETABILITY: In-Silico Mutagenesis (ISM)
K-mer counting is **Global Correlation**. ISM is **Local Causality**.

### The Algorithm step-by-step:
1.  **Forward Pass (Original):** Feed the sequence $S = [A, T, G, C...]$. Get prediction probability $P_{orig} = 0.95$.
2.  **Mutation Loop:**
    *   For position $i$ in $0$ to $L$:
        *   Mutate $S[i]$ to all other bases (e.g., $A \to C, G, T$).
        *   Forward Pass $P_{mut}$.
        *   Calculate Impact: $\Delta Score_i = P_{orig} - P_{mut}$.
3.  **Result:**
    *   If $\Delta Score_i$ is **Large Positive**: The original base was crucial (Causal).
    *   If $\Delta Score_i \approx 0$: The base changed nothing (Irrelevant).

### Why this beats Attention Maps:
Attention maps show where the model "routes information." Often, the model routes information *from* irrelevant background sequences (like repetitive 'AAAA') just to aggregate context. ISM ignores routing and asks: "Did the output change?"

---

## 3. THE VALIDATION: Fisher's Exact Test
We proved the TFAP2A motif wasn't random using a **Contingency Table**.

| | **High Importance Region** (ISM Peak) | **Low Importance Region** (Background) |
| :--- | :---: | :---: |
| **Contains TFAP2A** | **A** (Enriched) | **B** (Baseline) |
| **No TFAP2A** | **C** | **D** |

*   **Null Hypothesis ($H_0$):** TFAP2A appears equally in Important and Unimportant regions.
*   **Odds Ratio:** $\frac{A/C}{B/D} = 1.51$.
    *   *Interpretation:* You are 51% more likely to find TFAP2A in a region the model calls "Important".
*   **P-Value:** $1.04 \times 10^{-5}$.
    *   *Interpretation:* The chance of seeing this enrichment by pure luck is 1 in 100,000.

---

## 4. THE OPTIMIZATION: Mixed Precision Training (AMP)
We used **`torch.amp` (Automatic Mixed Precision)**.
*   **Float32 (Normal):** 32 bits per number. High precision, slow, high RAM.
*   **Float16 (Half):** 16 bits. Lower precision, 2x faster, half RAM.
*   **The Trick:** AMP keeps mastery weights in Float32 but does the heavy math (Matrix Multiplications) in Float16.
*   **Gradient Scaling:** Small gradients in Float16 might vanish to zero. We use a `GradScaler` to multiply them by large numbers (e.g., 65536) to save them, then divide back before updating weights.

---

## 5. TECHNICAL DEFENSE CHEAT SHEET
If they ask...
*   **"What is the Inductive Bias of your model?"**
    *   "The ALiBi mechanism injects a *locality bias*, assuming that proximal DNA interactions are more significant than distal ones, which aids generalization."
*   **"Is your interpretation post-hoc?"**
    *   "Yes, ISM is a post-hoc local perturbation method. It explains *predictions*, not the internal state."
*   **"Why 2 Million parameters?"**
    *   "Through empirical testing, we found that 2M params was the inflection point where validation loss plateaued. Adding more parameters led to overfitting on the relatively small EPDnew dataset."
