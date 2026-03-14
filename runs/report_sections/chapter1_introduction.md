# **CHAPTER 1: INTRODUCTION**

## 1.1 BACKGROUND

The human genome, comprising approximately 3 billion base pairs, encodes the instructions for life. While only about 2% of this genome codes for proteins, the remaining 98% consists of non-coding regions that play critical roles in regulating gene expression. Among the most important of these non-coding elements are **promoters** and **enhancers**. Promoters are DNA sequences located near the transcription start site (TSS) of genes and are essential for initiating transcription. Enhancers, on the other hand, can be located thousands of base pairs away and act as distal regulatory switches, amplifying or modulating gene expression.

Understanding the sequence patterns within these regulatory elements is crucial for deciphering disease mechanisms, as mutations in promoters and enhancers are frequently associated with complex diseases like cancer, diabetes, and neurological disorders. The challenge lies in accurately classifying and interpreting these sequences to identify the specific motifs that govern transcriptional regulation.

### 1.1.1 Machine Learning Based Approaches
Early computational approaches to genomic classification relied on hand-crafted features and traditional machine learning algorithms. The most prominent among these were Position Weight Matrices (PWMs), which aggregated nucleotide frequencies at specific positions to score potential binding sites. Subsequently, kernel-based methods such as the **gapped k-mer Support Vector Machine (gkm-SVM)** gained popularity. These models treated DNA sequences as collections of short subsequences (k-mers) and used high-dimensional kernels to distinguish between regulatory and non-regulatory regions. While effective for short sequences, these "shallow" models struggled to capture long-range dependencies and complex combinatorial logic, often requiring significant domain expertise for feature engineering.

### 1.1.2 Deep Learning Based Approaches
The advent of deep learning revolutionized the field by enabling models to learn features directly from raw DNA sequences. Convolutional Neural Networks (CNNs), such as **DeepSEA** and **Basset**, were the first to demonstrate that deep networks could automatically detect regulatory motifs (like "motif detectors") without manual feature extraction. More recently, the field has shifted toward Transformer architectures, inspired by Large Language Models (LLMs) in NLP. Models like **DNABERT** and **Nucleotide Transformer** utilize self-attention mechanisms to capture global context across long DNA sequences. These "foundation models" have achieved state-of-the-art performance but often come at the cost of high computational requirements and reduced interpretability, functioning as opaque "black boxes."

## 1.2 MOTIVATIONS

The primary motivation for this project stems from the "interpretability gap" in modern deep learning models for genomics. While foundation models like DNABERT-2 and Nucleotide Transformer have achieved impressive classification accuracy, they often function as "black boxes," providing predictions without revealing the underlying biological features that drive those predictions.

The key motivations are:
1.  **Causal Understanding:** Moving beyond correlation to identify motifs that causally influence gene expression.
2.  **Computational Efficiency:** Developing a lightweight model that can be trained and deployed on standard hardware, avoiding the massive computational costs of foundation models.
3.  **Biological Validation:** Ensuring that the patterns learned by the model correspond to known transcription factor binding sites, thereby bridging the gap between machine learning and functional genomics.

## 1.3 SCOPE OF THE PROJECT

This project focuses on developing an interpretable Transformer-based deep learning model for the binary classification of human promoter and enhancer sequences. The scope includes:

1.  **Model Development:** Implementation of a 4-layer Transformer encoder with ALiBi (Attention with Linear Biases) positional encoding for improved data efficiency.
2.  **Interpretability Pipeline:** Development of a multi-method framework combining k-mer enrichment analysis and In-Silico Mutagenesis (ISM) to discover sequence motifs.
3.  **Biological Validation:** Statistical validation of discovered motifs against the JASPAR database of known transcription factor binding profiles.
4.  **Dataset:** Utilization of ~65,000 human promoter and enhancer sequences for training, validation, and testing.

The project does not aim to compete with large-scale foundation models in terms of raw performance on diverse tasks but rather to demonstrate a biologically grounded approach to sequence classification.
