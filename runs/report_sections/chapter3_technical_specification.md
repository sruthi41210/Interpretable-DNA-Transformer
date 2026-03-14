# **CHAPTER 3: TECHNICAL SPECIFICATION**

## 3.1 REQUIREMENTS

### 3.1.1 Functional Requirements

| FR ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-01 | The system shall accept DNA sequences in FASTA or CSV format. | High |
| FR-02 | The system shall classify sequences as Promoter (Class 1) or Enhancer (Class 0). | High |
| FR-03 | The system shall output a probability score (0-1) for each prediction. | High |
| FR-04 | The system shall support character-level (single nucleotide) tokenization. | High |
| FR-05 | The system shall perform k-mer enrichment analysis on top/bottom predicted sequences. | Medium |
| FR-06 | The system shall perform In-Silico Mutagenesis (ISM) on high-confidence predictions. | Medium |
| FR-07 | The system shall generate Position Weight Matrices (PWMs) from discovered motifs. | Medium |
| FR-08 | The system shall compare generated PWMs against the JASPAR database. | Medium |
| FR-09 | The system shall save trained model checkpoints in PyTorch `.pt` format. | High |
| FR-10 | The system shall produce evaluation metrics (AUROC, PR-AUC, ECE) on the test set. | High |

### 3.1.2 Non-Functional Requirements

| NFR ID | Requirement | Category |
| :--- | :--- | :--- |
| NFR-01 | Training time shall not exceed 2 hours for the full dataset on a single GPU. | Performance |
| NFR-02 | Inference on a single sequence shall complete in < 50ms. | Performance |
| NFR-03 | The model footprint shall be < 50 MB. | Storage |
| NFR-04 | The system shall be modular, allowing easy replacement of model components. | Maintainability |
| NFR-05 | All code shall be compatible with Python 3.10+. | Compatibility |
| NFR-06 | The training pipeline shall support Automatic Mixed Precision (AMP) for efficiency. | Performance |
| NFR-07 | The system shall produce reproducible results given a fixed random seed. | Reliability |

## 3.2 FEASIBILITY STUDY

### 3.2.1 Technical Feasibility

The project is technically feasible based on the following:
*   **Hardware:** Standard consumer-grade GPUs (NVIDIA RTX 3060 or higher) are sufficient for training the ~2M parameter model.
*   **Software:** All required libraries (PyTorch, Biopython, pandas, numpy, matplotlib) are open-source and well-maintained.
*   **Data:** Publicly available promoter (EPDnew) and enhancer (ENCODE) datasets provide sufficient training data.
*   **Algorithms:** Transformer architectures and ALiBi positional encodings are well-documented in research literature.

### 3.2.2 Economic Feasibility

| Resource | Cost | Notes |
| :--- | :---: | :--- |
| Compute (Cloud GPU) | ~$50-100 | Estimated for 10-20 hours of GPU usage on Google Colab Pro or similar. |
| Datasets | $0 | All datasets used are publicly available. |
| Software | $0 | All tools are open-source (PyTorch, Biopython, etc.). |
| Personnel | N/A | Academic project, no external personnel costs. |

The project is economically viable for an academic research setting.

### 3.2.3 Social Feasibility

The project has positive social implications:
*   **Healthcare:** Identifying causal regulatory motifs can aid in understanding disease mechanisms.
*   **Accessibility:** A lightweight model democratizes access to genomic interpretation tools for labs without large compute clusters.
*   **Open Science:** All code and models will be made open-source, contributing to the research community.

## 3.3 SYSTEM SPECIFICATION

### 3.3.1 Hardware Specification

| Component | Minimum Requirement | Recommended |
| :--- | :--- | :--- |
| CPU | 4-core (Intel/AMD) | 8-core+ |
| RAM | 8 GB | 16 GB+ |
| GPU | NVIDIA GPU with 6GB VRAM | NVIDIA RTX 3060 (12GB VRAM) |
| Storage | 10 GB free | 50 GB SSD |
| Operating System | Windows 10 / Ubuntu 20.04+ | Windows 11 / Ubuntu 22.04 |

### 3.3.2 Software Specification

| Software | Version | Purpose |
| :--- | :--- | :--- |
| Python | 3.10+ | Core programming language. |
| PyTorch | 2.0+ | Deep learning framework. |
| CUDA | 11.8+ | GPU acceleration. |
| Biopython | 1.82+ | FASTA parsing, motif handling. |
| pandas | 2.0+ | Data manipulation. |
| numpy | 1.24+ | Numerical computation. |
| matplotlib | 3.7+ | Data visualization. |
| regex | 2024.x | Fuzzy motif matching. |
| scipy | 1.10+ | Statistical testing (Fisher's Exact Test). |

> **[IMAGE PLACEMENT: `runs/tables/dataset_statistics.csv` or a rendered table image - Chapter 3.3 to show data used]**
