# 🧬 DNA-SLM: Interpretable DNA Transformer for Motif Discovery

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-11.8+-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A lightweight Transformer that classifies human regulatory DNA sequences — and explains *why*.**

[The Problem](#the-problem) · [Quick Start](#-quick-start) · [Key Results](#-key-results) · [Architecture](#-model-architecture) · [Pipeline](#-interpretability-pipeline) · [Roadmap](#-roadmap)

</div>

---

## The Problem

Only **2% of the human genome** codes for proteins. The remaining 98% — particularly **promoters** and **enhancers** — controls when and where genes are switched on or off. Mutations in these non-coding regulatory regions are directly linked to cancer, diabetes, and neurological disorders.

State-of-the-art deep learning models like DNABERT (86M parameters) can classify these sequences with high accuracy, but function as **black boxes** — they give a prediction without revealing which DNA patterns drove it.

This project addresses the **interpretability gap**: building a model that is both accurate *and* explainable.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- NVIDIA GPU with 6GB+ VRAM (tested on RTX 4060 Laptop, 8GB VRAM)
- CUDA 11.8+

### Installation

```bash
# Clone the repository
git clone https://github.com/sruthi41210/Interpretable-DNA-Transformer.git
cd Interpretable-DNA-Transformer

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install biopython pandas numpy matplotlib scipy scikit-learn regex tqdm
```

### Run

```bash
# Quick inference demo on a sample sequence
python src/demo_lightning.py

# Train the ALiBi model from scratch (~25 min on RTX 4060)
python src/training/train_alibi.py

# Evaluate on held-out test set
python src/training/evaluate.py

# Run full interpretability pipeline
python src/interpretation/mutagenesis.py
python src/interpretation/jaspar_compare.py --top_n 10
python src/grammar_analysis.py \
  --top_windows runs/csv/top_windows_alibi.csv \
  --splits_csv data/pro_splits.csv data/enh_splits.csv \
  --out_dir runs/interpret/grammar \
  --n_windows 1000
```

---

## 🏆 Key Results

| Metric | Baseline Transformer | **ALiBi Transformer (Ours)** | Target |
|--------|---------------------|------------------------------|--------|
| AUROC | 0.87 | **0.89** | > 0.85 ✅ |
| PR-AUC | 0.90 | **0.92** | > 0.85 ✅ |
| ECE (Calibration) | 0.08 | **0.06** | < 0.10 ✅ |
| Parameters | ~2.1M | **~2.1M** | < 50MB ✅ |
| Training Time | ~30 min | **~25 min** | < 2hr ✅ |

### Key Biological Finding

The interpretability pipeline **independently identified TFAP2A** (MA0872.1) as the primary causal driver of promoter predictions — a well-established developmental transcription factor involved in neural crest development and cancer — without any prior biological knowledge being provided to the model.

| Method | Top Motif Found | Enrichment | p-value | Interpretation |
|--------|----------------|------------|---------|----------------|
| K-mer Enrichment | ZNF610 | 0.65x (depleted) | 0.013 | Background (correlative) |
| **In-Silico Mutagenesis** | **TFAP2A** | **1.51x** | **1.04e-05** | **Causal ✅** |
| Core Element Test | TATA/Inr | 1.2x | 0.004 | Architecture (significant) |

### Motif Grammar

Analysis of the top 1,000 high-importance windows revealed:
- **26.1%** of high-ISM windows contain TFAP2A motifs
- **Median inter-motif spacing: 16bp** — consistent with cooperative dimer binding (one helical turn of DNA)
- **KLF7** identified as a significant co-occurring transcription factor

---

## 🏗 Model Architecture

**TinyDNAEncoder** is a custom Transformer encoder built from scratch, optimised for DNA sequence classification on consumer hardware.

```
Input: DNA sequence (500bp) → "ACGTGCCNNNGGCACGT..."
         ↓
Character-level Tokenisation  (A=1, C=2, G=3, T=4, N=0)
         ↓
Token Embedding  (vocab_size=6, d_model=192)
         ↓
┌─────────────────────────────────────┐
│   Transformer Encoder Layer × 6     │
│                                     │
│   Multi-Head Self-Attention (6 heads)│
│   + ALiBi Positional Bias           │  ← Key innovation
│   + Feed-Forward Network (GELU)     │
│   + Layer Norm + Residual           │
└─────────────────────────────────────┘
         ↓
[CLS] token representation
         ↓
Linear Classification Head
         ↓
Output: P(Promoter) ∈ [0, 1]
```

### Why ALiBi?

Standard Transformers use **learned positional embeddings** — a lookup table that assigns a vector to each position. This fails when test sequences are longer than training sequences.

**ALiBi (Attention with Linear Biases)** instead adds a fixed linear penalty to attention scores based on the distance between positions. This means:

- **Data efficient** — reaches AUROC 0.80 with only 10% of training data (baseline needs 50%)
- **Length generalisation** — works on sequences longer than 500bp without retraining
- **No extra parameters** — the bias is mathematically fixed, not learned

---

## 🔬 Interpretability Pipeline

The pipeline distinguishes **causal motifs** from **correlative background features** — a distinction standard k-mer analysis cannot make.

```
Trained Model (frozen)
        ↓
┌───────────────────────────┐    ┌──────────────────────────┐
│   K-mer Enrichment        │    │   In-Silico Mutagenesis   │
│                           │    │                          │
│   Count k-mers in         │    │   Mutate every 6bp       │
│   top vs bottom           │    │   window systematically  │
│   predictions             │    │   → measure score drop   │
│                           │    │                          │
│   Finds: ZNF610           │    │   Finds: TFAP2A          │
│   (GC-rich background)    │    │   (causal regulatory)    │
│   ← correlative           │    │   ← causal ✅            │
└───────────────────────────┘    └──────────────────────────┘
                    ↓                          ↓
              PWM Extraction            PWM Extraction
                    ↓                          ↓
              ┌──────────────────────────────────┐
              │      JASPAR 2024 Validation       │
              │   + Fisher's Exact Test           │
              │   + Motif Grammar Analysis        │
              └──────────────────────────────────┘
                              ↓
                    TFAP2A confirmed as
                    primary causal motif
```

---

## 📁 Project Structure

```
Interpretable-DNA-Transformer/
│
├── src/                              # All source code
│   ├── config.py                     # Hyperparameters & paths
│   ├── dataset.py                    # PyTorch Dataset classes
│   ├── tokenizers.py                 # Character-level DNA tokenizer
│   ├── demo_lightning.py             # Quick inference demo
│   ├── grammar_analysis.py           # Motif grammar & co-occurrence
│   ├── save_hparams.py               # Hyperparameter logging
│   │
│   ├── models/
│   │   ├── model.py                  # Baseline Transformer encoder
│   │   └── model_alibi.py            # ALiBi Transformer ← main model
│   │
│   ├── training/
│   │   ├── train_alibi.py            # Main training loop
│   │   ├── evaluate.py               # Test set evaluation
│   │   └── metrics.py                # AUROC, PR-AUC, ECE
│   │
│   ├── interpretation/
│   │   ├── mutagenesis.py            # In-Silico Mutagenesis (ISM)
│   │   ├── kmer_enrichment.py        # K-mer frequency analysis
│   │   ├── cluster_kmers.py          # K-mer clustering → PWMs
│   │   ├── jaspar_compare.py         # JASPAR database matching
│   │   └── validate_tfap2a_enrichment.py  # Fisher's Exact Test
│   │
│   ├── data_prep/
│   │   └── make_splits.py            # Train/val/test splitting
│   │
│   └── visualization/                # Plotting utilities
│
├── data/                             # Datasets (not tracked by git)
│   ├── pro_splits.csv                # Human promoter sequences
│   ├── enh_splits.csv                # Human enhancer sequences
│   └── jaspar/                       # JASPAR 2024 CORE Vertebrate PWMs
│
├── runs/                             # Experiment outputs (not tracked by git)
│   ├── checkpoints/                  # Trained model weights (.pt)
│   ├── experiments/                  # Per-run metrics (enh/, pro/)
│   ├── csv/                          # ISM output CSVs
│   ├── figures/                      # Generated plots
│   ├── diagrams/                     # Architecture diagrams
│   ├── visuals/                      # ISM example visualisations
│   ├── tables/                       # Formatted result tables
│   ├── interpret/                    # Motif discovery results
│   │   ├── grammar/                  # Grammar analysis outputs
│   │   ├── pwms/                     # K-mer derived PWMs
│   │   └── pwms_ism/                 # ISM derived PWMs
│   └── hparams.json                  # Logged hyperparameters
│
├── notebooks/                        # Jupyter notebooks (in progress)
├── DNA_SLM_Implementation_Plan.md    # Development roadmap
├── .gitignore
└── README.md
```

---

## 📊 Dataset

| Dataset | Source | Sequences | Class | Avg Length | GC Content |
|---------|--------|-----------|-------|------------|------------|
| Promoters | EPDnew (human_nontata) | 35,682 | 1 | 500bp | 0.58 |
| Enhancers | ENCODE (human_cohn) | 28,947 | 0 | 500bp | 0.45 |
| **Train Split** | — | 45,240 | — | 500bp | 0.52 |
| **Val Split** | — | 9,694 | — | 500bp | 0.52 |
| **Test Split** | — | 9,695 | — | 500bp | 0.52 |

Sequences were split by **genomic locus grouping** (not random) to prevent data leakage from similar sequences appearing in both train and test sets.

---

## ⚙️ Hyperparameters

Key configuration (see `runs/hparams.json` for full details):

```json
{
  "model": {
    "d_model": 192,
    "num_layers": 6,
    "num_heads": 6,
    "parameters": "~2.1M"
  },
  "training": {
    "optimizer": "AdamW",
    "learning_rate": 3e-4,
    "batch_size": 64,
    "max_epochs": 50,
    "amp": true,
    "rc_augmentation": true
  },
  "early_stopping": {
    "monitor": "val_pr_auc",
    "patience": 5
  }
}
```

---

## 🔬 Use Cases

**1. Genome Annotation**
Classify uncharacterised non-coding sequences as promoters or enhancers in newly sequenced genomes.

**2. Variant Effect Prediction** *(in progress)*
Given a patient SNP in a non-coding region, compare model confidence on the reference vs. mutant sequence. A significant drop suggests the mutation disrupts a regulatory element — potentially disease-causing.

**3. Transcription Factor Discovery**
Run ISM on a set of functionally important sequences to identify which transcription factors are causally driving their regulatory activity.

**4. Drug Target Identification**
TFAP2A is overexpressed in several cancers. Identify TFAP2A-regulated promoters to find candidate genes for therapeutic intervention.

---

## 🗺 Roadmap

- [x] TinyDNAEncoder with ALiBi positional encoding
- [x] ISM interpretability pipeline
- [x] JASPAR 2024 validation + Fisher's Exact Test
- [x] Motif grammar analysis (spacing + co-occurrence)
- [x] Hyperparameter logging
- [ ] Ablation studies (ALiBi vs baseline, depth sweep)
- [ ] Variant effect prediction (ClinVar pathogenic SNPs)
- [ ] Cross-species zero-shot validation (mouse)
- [ ] Attention head specialisation analysis
- [ ] BioRxiv preprint

---

## 🛠 Tech Stack

- **Framework:** PyTorch 2.0+
- **Model:** Custom Transformer Encoder with ALiBi (Attention with Linear Biases)
- **Interpretability:** In-Silico Mutagenesis (ISM) + K-mer Enrichment
- **Biological Validation:** JASPAR 2024 CORE Vertebrate database + Fisher's Exact Test
- **Hardware:** NVIDIA RTX 4060 Laptop GPU (8GB VRAM), CUDA 12.7

---

## 📚 Key References

- Press, O., Smith, N. A., & Lewis, M. (2022). *Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation.* ICLR.
- Zhou, J., & Troyanskaya, O. G. (2015). *Predicting effects of noncoding variants with deep learning-based sequence model (DeepSEA).* Nature Methods.
- Zhou, Z., et al. (2021). *DNABERT: pre-trained Bidirectional Encoder Representations from Transformers model for DNA-language in genome.* Bioinformatics.
- Dalla-Torre, H., et al. (2023). *The Nucleotide Transformer.* ICML.
- Fornes, O., et al. (2020). *JASPAR 2020: update of the open-access database of transcription factor binding profiles.* Nucleic Acids Research.
- Lambert, S. A., et al. (2018). *The human transcription factors.* Cell.

---

## 👩‍💻 Author

**Sruthi Seetharaman**
B.Tech Computer Science & Engineering (Bioinformatics)
Vellore Institute of Technology
Under the supervision of **Prof. Balakrishnan P**, SCOPE, VIT

---

<div align="center">
<i>Training a model to read the non-coding genome — and understand what it finds.</i>
</div>
