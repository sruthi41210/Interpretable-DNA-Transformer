# Future Work

## 1. Technical Extensions
The current study focused on a 4-layer Transformer. Future work will investigate the impact of increasing model depth and introducing more diverse baseline comparisons, such as **gkm-SVM** and deeper **CNN (Basset/DeepSEA)** architectures. Plans also include extending the sequence context from 500bp to several kilobases to fully utilize the length-extrapolation capabilities of ALiBi. Finally, implementing **Multi-task Learning** (simultaneous promoter, enhancer, and chromatin accessibility prediction) could lead to more generalized sequence representations.

## 2. Biological Validation
While motifs were validated against JASPAR, the true test of a predictive model is its correlation with experimental data. Future efforts will compare ISM importance scores with **Massively Parallel Reporter Assay (MPRA)** data to determine if the model's predicted mutational impact matches experimental gene expression changes. Furthermore, the model will be evaluated for its ability to predict the impact of **Single Nucleotide Polymorphisms (SNPs)** known to be associated with diseases in GWAS (Genome-Wide Association Studies).

## 3. Grammar Discovery
Transcription factors rarely act in isolation. Future analysis will focus on the "regulatory grammar" learned by the model, specifically looking for **Motif Spacing Rules** and **Combinatorial Logic**. Determining whether certain motifs (e.g., TFAP2A and SP1) are required to be at specific distances from each other will be investigated. Understanding these spacing constraints is a major step toward a complete "decoder" of the non-coding genome.

## 4. Applications
The ultimate goal of this research is the design of **Synthetic Regulatory Elements**. By identifying motifs that drive high promoter activity, new promoter sequences can be computationally designed for use in gene therapy. Additionally, this framework can be used to interpret variants of unknown significance in clinical genomics, providing a "causal score" for mutations found in patients with rare regulatory disorders.
