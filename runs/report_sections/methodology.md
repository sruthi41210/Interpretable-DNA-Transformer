# Methodology

## 1. Dataset Description
Two major genomic datasets are utilized in this study:
-   **Promoters:** A dataset of human non-TATA promoter sequences (35,682 total).
-   **Enhancers:** Human enhancer sequences from the Cohn dataset (28,947 total).

All sequences were standardized to 500bp in length. Sequences containing ambiguous bases (N) were excluded to maintain data quality. The sequences represent a GC-rich promoter landscape (avg GC 0.58) and a more AT-rich enhancer background (avg GC 0.45).

### Split Strategy
To ensure robust evaluation and prevent data leakage, a **grouped splitting strategy** was employed. Sequences were grouped by genomic locus or original cluster IDs, and these groups were split into Training (70%), Validation (15%), and Test (15%) sets. This ensures that the model cannot "memorize" nearly identical sequences from the same regulatory region across different splits.

## 2. Model Architecture
The **TinyDNAEncoder**, a lightweight Transformer-based encoder, was developed. The core architecture remains consistent across experiments:
-   **Layers:** 4-layer stacked Transformer blocks.
-   **Attention Heads:** 8 heads per layer to capture diverse sequence patterns.
-   **Hidden Dimension:** 256 for both embeddings and feed-forward layers.
-   **Parameter Count:** ~2.1 million parameters, allowing for efficient training on standard hardware.

### ALiBi Implementation
**ALiBi (Attention with Linear Biases)** was integrated into the self-attention mechanism. Unlike standard positional encodings which are added to embeddings, ALiBi adds a linear penalty to the attention scores that increases with the distance between tokens. This bias encourages the model to prioritize local interactions (within motifs) while remaining capable of modeling longer-range interactions across the 500bp window.

### Training Procedures
Models were trained using the AdamW optimizer with a learning rate of 1e-4 and a batch size of 32. **Automatic Mixed Precision (AMP)** was utilized to accelerate training on NVIDIA GPUs. Early stopping was implemented based on Validation PR-AUC to prevent overfitting, with a patience of 5 epochs. **Reverse Complement (RC) Augmentation** was applied during training, where each sequence was randomly replaced by its reverse complement to enforce biological strand-invariance.

## 3. Interpretability Pipeline
The interpretability framework uses a contrasting "Two-Method" approach:

### K-mer Enrichment
K-mer (k=6, 8) frequencies were calculated across top-predicted sequences compared to bottom-predicted ones. K-mers were ranked by their log2 enrichment ratio. While efficient, this method identifies sequence biases rather than causal elements.

### In-Silico Mutagenesis (ISM)
For selected high-confidence true positives in the test set, systematic single-base perturbations were performed. For each position in a sequence, the original base was substituted with a different one, and the drop in the model's predicted probability of the "positive" class was measured. Regions where mutations caused significant drops were identified as **High-Importance Windows**.

## 4. Validation Approach
To validate the biological relevance of discovered motifs, a three-step protocol was performed:
1.  **Database Matching:** Discovered Position Weight Matrices (PWMs) were compared against the **JASPAR 2024 CORE Vertebrate** database using Pearson correlation.
2.  **Statistical Testing:** 1000 high-importance windows and 1000 low-importance windows were extracted. **Fisher's Exact Test** was used to calculate the enrichment of the TFAP2A consensus motif (GCCNNNGGC) within these windows.
3.  **Positional Analysis:** The spatial distribution of these motifs was mapped to ensure localization near the centers of the identified high-importance windows.
