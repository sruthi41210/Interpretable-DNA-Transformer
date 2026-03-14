# **CHAPTER 2: PROJECT DESCRIPTION AND GOALS**

## 2.1 LITERATURE REVIEW

### 2.1.1 Machine Learning Based Approaches

Traditional machine learning approaches for DNA sequence classification relied heavily on k-mer based feature engineering. The most notable method is **gapped k-mer SVM (gkm-SVM) [Ghandi et al., 2014]**, which uses support vector machines with a specialized kernel that counts the occurrence of gapped k-mers to classify regulatory sequences. While effective for shorter sequences, these methods struggle with long-range dependencies and require significant domain expertise for feature selection.

Other approaches include Random Forests applied to position weight matrix (PWM) scores and Naive Bayes classifiers for promoter prediction. These methods provided early benchmarks but are limited by their inability to learn complex, non-linear patterns in DNA sequences.

### 2.1.2 Deep Learning Based Approaches

Deep learning has revolutionized genomic sequence analysis. Key milestones include:

*   **DeepSEA [Zhou & Troyanskaya, 2015]:** A pioneering Convolutional Neural Network (CNN) that predicts chromatin accessibility and transcription factor binding from DNA sequences.
*   **Basset [Kelley et al., 2016]:** A deep CNN for learning the regulatory code of the accessible genome.
*   **DNABERT [Zhou et al., 2021]:** Applied the BERT architecture from NLP to k-merized DNA sequences, demonstrating the power of pre-training for genomic tasks.
*   **Nucleotide Transformer [Dalla-Torre et al., 2023]:** A foundation model scaling to billions of parameters across diverse species.
*   **DNABERT-2 [Zhou et al., 2024]:** Introduced more efficient tokenization and achieved state-of-the-art results on diverse benchmarks.

While these models achieve high accuracy, their interpretability remains a significant challenge.

## 2.2 GAPS IDENTIFIED

Based on the literature review, the following gaps were identified:

| Gap ID | Description |
| :--- | :--- |
| G1 | Foundation models require massive computational resources, limiting accessibility for smaller research labs. |
| G2 | Standard interpretability methods (e.g., attention visualization) often highlight background features rather than causal motifs. |
| G3 | There is no standardized pipeline that validates discovered motifs against established biological databases like JASPAR. |
| G4 | Most models are trained on promoters OR enhancers, lacking a unified framework for joint analysis. |
| G5 | Existing models lack calibrated confidence scores, making it difficult to quantify uncertainty in clinical applications. |

## 2.3 OBJECTIVES

The objectives of this project are:

1.  **O1:** To design and implement a lightweight (~2M parameters) Transformer encoder for DNA sequence classification.
2.  **O2:** To integrate ALiBi positional encoding to improve data efficiency and length extrapolation.
3.  **O3:** To develop a multi-method interpretability pipeline (K-mer + ISM) that distinguishes background from causal features.
4.  **O4:** To statistically validate discovered motifs against the JASPAR 2024 database using Fisher's Exact Test.
5.  **O5:** To achieve competitive classification performance (AUROC > 0.85) on human promoter/enhancer sequences.

## 2.4 PROBLEM STATEMENT

> **"How can a lightweight Transformer model be designed for DNA sequence classification such that it not only achieves high predictive accuracy but also provides biologically interpretable outputs that identify causal transcription factor binding motifs?"**

This problem addresses the need for models that are both performant and transparent, enabling researchers to understand the regulatory grammar learned by the model.

## 2.5 PROJECT PLAN

The project is executed in distinct phases, transitioning from initial research to final system deployment:

| Phase | Activities |
| :--- | :--- |
| **Phase 1: Literature Survey** | Survey of ML/DL methods for genomics, identification of gaps vs current SOTA. |
| **Phase 2: Data Preparation** | Collection of promoter/enhancer datasets (EPDnew, Cohn), preprocessing, and diversity-aware splitting. |
| **Phase 3: Model Development** | Implementation of TinyDNAEncoder (Baseline) and integration of ALiBi for efficiency. |
| **Phase 4: Midterm Evaluation** | Performance benchmarking (AUROC, PR-AUC), initial interpretability analysis (K-mer/ISM), and TFAP2A validation. |
| **Phase 5: Advanced Optimization** | *(Upcoming)* Hyperparameter tuning, increasing model depth, and exploring larger context windows (>1kb). |
| **Phase 6: Grammar Analysis** | *(Upcoming)* Investigating combinatorial logic (motif spacing/co-occurrence) and validating against MPRA data. |
| **Phase 7: Final Delivery** | *(Upcoming)* Complete system integration, web interface development (optional), and final thesis submission. |

> **[IMAGE PLACEMENT: `runs/diagrams/biological_summary.png` - End-to-end project flow infographic]**
