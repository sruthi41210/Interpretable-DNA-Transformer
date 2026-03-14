# Introduction

## DNA Regulatory Elements
The human genome contains millions of non-coding elements that orchestrate the precise timing and tissue-specificity of gene expression. Among these, promoters and enhancers are the most critical. Promoters serve as the immediate transcription start sites, typically characterized by core elements like the TATA-box or Initiator (Inr) sequences. Enhancers, which can be located thousands of base pairs away, loop across the 3D chromatin space to interact with promoters, acting as distal regulatory switches. Understanding the "grammar" of these sequences—the specific arrangement of transcription factor (TF) binding sites—is essential for deciphering the genetic basis of health and disease.

The classification of these elements is a non-trivial task due to the high variability in motif spacing and the degenerate nature of DNA binding sites. Mutations within these regulatory regions are frequently associated with complex traits and diseases, yet the ability to predict the functional impact of such variants remains limited by the current understanding of regulatory logic.

## Current Approaches
In recent years, the field has pivoted from traditional k-mer based support vector machines (gkm-SVMs) and convolutional neural networks (CNNs) toward large-scale foundation models. Models such as DNABERT-2 and Nucleotide Transformer leverage the Transformer architecture to learn long-range dependencies across the genome. However, these models require immense computational resources and often prioritize classification accuracy over biological interpretability. As these models grow in complexity, the "interpretability gap" widens, making it difficult to extract the specific motifs that drive model decisions.

Furthermore, traditional attention-based interpretability can be misleading in genomic contexts, as high attention weights do not always correlate with the causal influence of a motif on the final prediction. There is a pressing need for lightweight, efficient models that provide verifiable biological insights.

## Project Contribution
This report describes the development and validation of an interpretable DNA Transformer. The contributions are three-fold:
1.  **Efficient Architecture:** Implementation of a 4-layer Transformer encoder utilizing ALiBi positional encoding, which significantly improves data efficiency and handles varying sequence lengths without retraining.
2.  **Multi-Method Interpretability:** Development of a pipeline that contrasts global sequence statistics (k-mer enrichment) with local causal impact (In-Silico Mutagenesis).
3.  **Biological Validation:** Provision of statistical proof that the model independently discovers biologically validated transcription factor motifs, specifically identifying the TFAP2A motif as a causal element in human promoter sequences.

## Report Organization
The remainder of this report is organized as follows: Section 2 provides a review of current literature in DNA language modeling and interpretability. Section 3 details the methodology, including the model architecture and the design of the interpretability tools. Section 4 presents the results, highlighting the statistical significance of discovered motifs. Finally, Section 5 discusses the implications of this work and outlines future research directions.
