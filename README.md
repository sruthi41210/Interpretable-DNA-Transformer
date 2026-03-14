# DNA-SLM: Interpretable DNA Transformer for Motif Discovery

A lightweight Transformer model with ALiBi attention for classifying human promoter and enhancer sequences, with a built-in interpretability pipeline that discovers causal transcription factor binding motifs.

## Key Results
- **AUROC:** 0.89 | **PR-AUC:** 0.92
- **Discovery:** Independently identified the **TFAP2A** binding motif (JASPAR correlation: 0.869, p < 0.0001)
- **Efficiency:** 2.1M parameters, trains in <30 minutes on a single GPU

## Project Structure

```
dna-slm/
├── src/                        # Source code
│   ├── config.py               # Hyperparameters & paths
│   ├── dataset.py              # Data loading & tokenization
│   ├── demo_lightning.py       # Quick inference demo
│   ├── models/                 # Model architectures
│   ├── training/               # Training, eval & sweep scripts
│   ├── interpretation/         # ISM, K-mer, JASPAR validation
│   ├── data_prep/              # Splitting & window extraction
│   └── visualization/          # Plotting & figure generation
│
├── data/                       # Datasets & JASPAR database
├── runs/                       # Experiment outputs
│   ├── checkpoints/            # Trained model weights (.pt)
│   ├── experiments/            # Per-run metrics (enh/, pro/)
│   ├── figures/                # Generated plots
│   ├── csv/                    # Intermediate CSV outputs
│   ├── diagrams/               # Architecture & system diagrams
│   ├── interpret/              # Motif discovery results
│   ├── visuals/                # ISM example visualizations
│   ├── tables/                 # Formatted tables (CSV/LaTeX)
│   ├── report_sections/        # Midterm report chapters
│   ├── presentation/           # Slide guide & speaker notes
│   └── final_deliverables/     # Compiled report draft
│
└── notebooks/                  # Jupyter notebooks (future)
```

## Quick Start

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run inference demo
python src/demo_lightning.py

# Train the ALiBi model
python src/training/train_alibi.py
```

## Tech Stack
- **Framework:** PyTorch
- **Model:** Custom Transformer Encoder with ALiBi (Attention with Linear Biases)
- **Interpretability:** In-Silico Mutagenesis (ISM) + K-mer Enrichment
- **Validation:** JASPAR 2024 database + Fisher's Exact Test
