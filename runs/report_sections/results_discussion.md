# Results Discussion

## 1. Performance Achievement
Both the Baseline and ALiBi models achieved strong performance on the classification task. The **ALiBi Transformer** slightly outperformed the baseline (AUROC 0.89 vs 0.87), but its primary advantage was observed in **data efficiency**. As shown in the learning curve analysis, the ALiBi model maintained near-peak performance with only 25% of the training data, whereas the baseline dropped significantly. This suggests that the linear bias mechanism provides a more robust structural prior for genomic sequences than learned positional embeddings.

## 2. The GC-Content Paradox
An interesting secondary finding was the "GC-content paradox." K-mer enrichment analysis identified several GC-rich 6-mers (e.g., GCGGCG) as highly enriched in promoters. However, when these specific regions were analyzed using In-Silico Mutagenesis (ISM), the model often showed very low importance scores for these k-mers. 

This leads to a critical biological insight: **Correlation does not equal Causation**. The GC-rich background is a structural feature of human promoters (the "landscape"), but the model learned that mutating these generic background bases does not significantly change the sequence's functional class. The model correctly ignores the "background noise" of the GC-rich architecture in favor of specific regulatory signatures.

## 3. TFAP2A Discovery
The most significant result was the discovery of the **TFAP2A** motif through the ISM-driven discovery pipeline. ISM identified high-importance windows characterized by the consensus `GCCNNNGGC`. Comparison with the JASPAR database confirmed a high correlation (**0.869**) with the AP-2 alpha family.

Statistical validation via Fisher's Exact Test showed a **1.51x enrichment** of this motif in high-ISM windows compared to low-ISM windows (**p = 1.04e-05**). TFAP2A is a well-known transcription factor involved in neural crest development and the regulation of epithelial genes. The model independently prioritized this motif as "causal" without prior biological knowledge, validating the robustness of the interpretability framework.

## 4. Interpretability Framework Value
The results highlight the risk of relying solely on k-mer enrichment or attention weights. The framework's ability to separate **Background Features** (like ZNF610/GC-richness) from **Causal Features** (like TFAP2A) is essential for functional genomics. By focusing on motifs that demonstrate a high "mutational impact," transcription factors that are more likely to have a direct regulatory role can be prioritized over those that simply bind to frequent sequence templates.
