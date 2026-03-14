# **CHAPTER 5: METHODOLOGY AND TESTING**

## 5.1 MODULE DESCRIPTION

The DNA-SLM project is organized into seven core software modules, each responsible for a distinct phase of the analysis pipeline.

### Module 1: Data Preparation
**Source Files:** `src/make_splits.py`, `src/tokenizers.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Loads raw promoter/enhancer sequences, applies grouped splitting (70/15/15) to prevent data leakage, and performs character-level tokenization. |
| Input | `data/enh_train.csv`, `data/pro_train.csv` |
| Output | Train/validation/test CSV files for both enhancers and promoters. |
| Key Logic | Sequences are grouped by genomic locus to ensure that similar sequences are not present in both training and test sets. |

### Module 2: Model Architecture
**Source Files:** `src/model.py`, `src/model_alibi.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Defines the Transformer encoder architecture for sequence classification. |
| Components | `CharTokenizer` (maps A, C, G, T to integer tokens), `TinyDNAEncoder` (4-layer Transformer with learned positional embeddings), `TinyDNAEncoderALiBi` (replaces learned embeddings with ALiBi). |
| Output | A single probability score (0-1) indicating the likelihood of the input being a promoter. |

### Module 3: Training Pipeline
**Source Files:** `src/train.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Trains the model using the AdamW optimizer with Automatic Mixed Precision (AMP) and early stopping based on validation PR-AUC. |
| Input | Training and validation data loaders. |
| Output | `runs/best_model.pt` (checkpoint of the best performing model). |
| Key Features | Reverse Complement (RC) augmentation to enforce strand-invariance. |

### Module 4: Evaluation
**Source Files:** `src/evaluate.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Computes performance metrics on the held-out test set. |
| Metrics | AUROC, PR-AUC, Accuracy, Precision, Recall, F1-Score, Expected Calibration Error (ECE). |
| Output | `runs/metrics.json` |

### Module 5: K-mer Enrichment Analysis
**Source Files:** `src/kmer_enrichment.py`, `src/cluster_kmers.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Identifies enriched or depleted k-mers in top-predicted vs. bottom-predicted sequences. |
| Output | `runs/interpret/pro_k6_enrichment.csv` |
| Limitation | Identifies background patterns (e.g., ZNF610) rather than causal motifs. |

### Module 6: In-Silico Mutagenesis (ISM)
**Source Files:** `src/mutagenesis_aggregate.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Systematically mutates each base in high-confidence sequences and measures the impact on model prediction. |
| Output | `runs/top_windows_alibi.csv` (top 1000 high-importance windows). |
| Key Finding | Discovered TFAP2A binding motif (`GCCNNNGGC`). |

### Module 7: Biological Validation
**Source Files:** `src/jaspar_compare.py`, `src/validate_tfap2a_enrichment.py`

| Attribute | Description |
| :--- | :--- |
| Purpose | Compares discovered Position Weight Matrices (PWMs) against JASPAR 2024 and performs Fisher's Exact Test for enrichment. |
| Output | TFAP2A identified with 1.51x enrichment (p = 1.04e-05). |

---

## 5.2 TESTING

### 5.2.1 Unit Testing

| Test Case | Module | Input | Expected Output | Result |
| :--- | :--- | :--- | :--- | :---: |
| TC-01 | CharTokenizer | "ACGT" | [1, 2, 3, 4] | Pass |
| TC-02 | CharTokenizer | "NNNNN" | [0, 0, 0, 0, 0] (PAD tokens) | Pass |
| TC-03 | TinyDNAEncoder | Random tensor of shape (1, 100) | Output shape (1, 1) | Pass |
| TC-04 | ISMAnalyzer | Sequence containing known TFAP2A motif | High score drop at expected position | Pass |

### 5.2.2 Integration Testing

| Test Case | Description | Result |
| :--- | :--- | :---: |
| IT-01 | Full training loop executes without error for one epoch. | Pass |
| IT-02 | Model checkpoint can be saved and reloaded successfully. | Pass |
| IT-03 | ISM pipeline produces expected CSV output format. | Pass |
| IT-04 | JASPAR comparison script correctly parses MEME format files. | Pass |

### 5.2.3 Validation Testing (Model Performance)

| Metric | Baseline Transformer | ALiBi Transformer | Target | Status |
| :--- | :---: | :---: | :---: | :---: |
| AUROC | 0.87 | 0.89 | > 0.85 | Achieved |
| PR-AUC | 0.90 | 0.92 | > 0.85 | Achieved |
| ECE (Calibration) | 0.08 | 0.06 | < 0.10 | Achieved |

---

## 5.3 RESULTS SUMMARY

The model successfully achieved all stated objectives:

1. **Classification Performance:** The ALiBi Transformer achieved an AUROC of 0.89 and PR-AUC of 0.92, exceeding the target threshold of 0.85.
2. **Motif Discovery:** The interpretability pipeline identified the TFAP2A transcription factor binding motif as a primary causal driver of model predictions.
3. **Statistical Validation:** Fisher's Exact Test confirmed a 1.51x enrichment of TFAP2A motifs in high-importance windows with a p-value of 1.04e-05, demonstrating robust statistical significance.

---

## 5.4 EXPERIMENTAL RESULTS AND FIGURES

This section presents the actual experimental outputs generated during the project. All figures are located in the `runs/` directory.

### 5.4.1 In-Silico Mutagenesis Aggregate Results

**File:** `runs/mutagenesis_aggregate_alibi.png`

This figure shows the aggregated ISM importance scores across all high-confidence promoter sequences analyzed with the ALiBi model. Each curve represents the normalized importance of nucleotide positions within a 500bp window. Peaks in the plot indicate regions where single-nucleotide mutations caused the largest drops in prediction confidence, suggesting the presence of functionally critical motifs.

**File:** `runs/mutagenesis_aggregate_baseline.png`

A comparison plot showing the same analysis performed using the baseline Transformer model. Differences between the ALiBi and baseline plots reveal how the attention mechanism with linear biases focuses on different sequence features compared to learned positional embeddings.

### 5.4.2 Individual ISM Example Curves

**Files:** `runs/visuals/ism_example_alibi_4282.png`, `ism_example_alibi_5194.png`, `ism_example_alibi_6639.png`

These plots show the per-position importance scores for three individual high-confidence sequences. The x-axis represents the nucleotide position (0-500), and the y-axis represents the normalized importance score. Sharp peaks indicate regions where the model is highly sensitive to mutations, often corresponding to transcription factor binding sites. The highlighted regions in these examples overlap with the TFAP2A consensus motif (GCCNNNGGC).

### 5.4.3 K-mer Enrichment Motif Logo

**File:** `runs/interpret/motif_logo_k6.png`

This sequence logo was generated from the top enriched 6-mers identified in promoter sequences. The logo represents the frequency of each nucleotide at each position within the enriched k-mer clusters. While this method identifies the GC-rich background architecture of promoters (matching ZNF610), it does not distinguish causal from correlative features.

### 5.4.4 Position Weight Matrices (PWMs)

**K-mer Derived PWMs:**
- `runs/interpret/pwms/pwm_cluster2_k6.png` - PWM from k-mer cluster 2 (GC-rich pattern)
- `runs/interpret/pwms/pwm_cluster5_k6.png` - PWM from k-mer cluster 5 (alternative motif)

**ISM Derived PWM:**
- `runs/interpret/pwms_ism/pwm_ism_top_windows_alibi.png` - PWM extracted from the top 1000 high-ISM windows. This PWM shows the GCCNNNGGC consensus that matches TFAP2A in the JASPAR database.

The ISM-derived PWM demonstrates a distinct pattern compared to k-mer PWMs, highlighting the advantage of causal interpretability methods.

### 5.4.5 TFAP2A Positional Distribution

**File:** `runs/interpret/tfap2a_position_distribution.png`

This histogram shows the distribution of TFAP2A motif positions within high-ISM windows. The concentration of motifs near the center of the high-importance windows (around position 10-15 within the 21bp window) confirms that the model correctly identified the motif location as the causal element. If the enrichment were spurious, the distribution would be uniform.

### 5.4.6 Causal vs K-mer Motif Comparison

**File:** `runs/visuals/causal_vs_kmer_motifs.png`

A side-by-side comparison of motifs discovered by the two methods:
- **Left panel (K-mer Enrichment):** ZNF610-like pattern, 0.65x depleted in high-ISM windows, representing background GC-rich architecture.
- **Right panel (ISM Discovery):** TFAP2A pattern, 1.51x enriched (p = 1.04e-05), representing causal regulatory element.

This figure directly illustrates the "correlation vs causation" distinction that is central to the interpretability framework.

### 5.4.7 JASPAR Database Match Results

**Files:** `runs/interpret/jaspar_match_pwm_ism_top_windows_alibi.csv`, `runs/interpret/jaspar_matches_k6.csv`

These CSV files contain the results of comparing discovered PWMs against the JASPAR 2024 CORE Vertebrate database. The ISM-derived PWM achieved a Pearson correlation of 0.869 with the TFAP2A (MA0003.4) profile, confirming the biological relevance of the discovered motif.

### 5.4.8 Statistical Enrichment Test

**File:** `runs/interpret/tfap2a_enrichment_test.csv`

This file contains the Fisher's Exact Test results comparing TFAP2A motif frequency between high-ISM and low-ISM windows:

| Metric | Value |
| :--- | :--- |
| High-ISM windows with TFAP2A | 18.2% |
| Low-ISM windows with TFAP2A | 12.1% |
| Odds Ratio | 1.51 |
| P-value | 1.04e-05 |
| Interpretation | Statistically significant enrichment |

---

## 5.5 OUTPUT FILE SUMMARY

The following key output files were generated during the project:

| File | Location | Description |
| :--- | :--- | :--- |
| `top_windows_alibi.csv` | `runs/` | Top 1000 high-importance windows from ISM analysis (ALiBi model). |
| `top_windows_baseline.csv` | `runs/` | Top 1000 high-importance windows from ISM analysis (Baseline model). |
| `pro_k6_enrichment.csv` | `runs/interpret/` | K-mer enrichment scores for all 6-mers in promoter sequences. |
| `pro_k6_clusters.csv` | `runs/interpret/` | Clustered k-mers grouped by sequence similarity. |
| `high_ism_windows.fa` | `runs/interpret/` | FASTA file of high-ISM window sequences for downstream analysis. |
| `tfap2a_enrichment_test.csv` | `runs/interpret/` | Fisher's Exact Test results for TFAP2A enrichment. |
| `enh_alibi.pt` | `runs/` | Trained ALiBi model checkpoint for enhancer classification. |
| `enh_strong_baseline.pt` | `runs/` | Trained baseline model checkpoint for enhancer classification. |
