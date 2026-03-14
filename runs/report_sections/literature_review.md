# Literature Review

## DNA Language Models
The application of Natural Language Processing (NLP) techniques to genomics began with the realization that DNA sequences share properties with human language, such as sequential hierarchy and regulatory grammar. **DNABERT [Zhou et al., 2021]** was a pioneering work that applied the BERT architecture to k-merized DNA sequences, demonstrating the power of pre-training for downstream tasks. This was followed by the **Nucleotide Transformer [Dalla-Torre et al., 2023]**, which scaled these models to billions of parameters across diverse species.

More recently, **DNABERT-2 [Zhou et al., 2024]** introduced more efficient tokenization and training strategies, moving towards foundation models that can generalize across varied genomic tasks. While these models achieve remarkable AUROC scores, they are often criticized for their "black-box" nature, where the underlying features driving classification remain obscured by the complexity of the attention mechanism.

## Interpretability Methods
Interpreting what a genomic deep learning model has learned is as important as its predictive accuracy. Early efforts focused on **Attention Visualization**, but studies have shown that attention weights often focus on frequent but uninformative background patterns [Jain and Wallace, 2019]. To address this, gradient-based methods like **Integrated Gradients [Sundararajan et al., 2017]** were developed to attribute predictions to specific input features.

In genomics, **In-Silico Mutagenesis (ISM)** has emerged as the "gold standard" for causal interpretation [Alipanahi et al., 2015]. By systematically perturbing every base in a sequence and measuring the change in output, ISM directly quantifies the causal impact of a motif. However, ISM is computationally expensive, leading researchers to explore hybrid approaches that combine ISM with more efficient feature attribution methods.

## Positional Encodings
The standard Transformer architecture uses **Sinusoidal Positional Encodings [Vaswani et al., 2017]** or **Learned Embeddings** to provide the model with a sense of sequence order. However, these methods often struggle with sequences longer than those seen during training. **ALiBi (Attention with Linear Biases) [Press et al., 2021]** was introduced to solve this by adding a static bias to the attention scores based on distance, allowing for better length extrapolation and improved training stability. In genomics, where sequence length and spacing are critical, ALiBi offers a promising alternative for efficient sequence modeling.

## Contextual Gap
Despite the success of foundation models, there is a lack of focus on **lightweight, interpretable alternatives** that can be deployed on modest hardware while still providing biological validation. Most current research either focuses on scaling (foundation models) or narrow interpretability (CNN-based motif discovery). This research addresses this gap by combining the efficiency of a Transformer with a rigorous interpretability pipeline that validates discovered motifs against the **JASPAR database**, ensuring that the model's "logic" aligns with established regulatory biology.
