# Slide-by-Slide Presentation Content

---
SLIDE 01: TITLE SLIDE
Visual Elements:
- [Cover Image: system_architecture.png]

Bullet Points:
- Interpretable DNA Transformers for Regulatory Sequence Classification
- Multi-Method Validation of Causal Motif Discovery
- [Your Name]
- Guide: [Guide Name] | Dept: [Department]
- [Date]

Speaker Notes:
"Good morning/afternoon everyone. Today I'll be presenting my progress on DNA sequence classification using interpretable Transformers. We focus not just on 'if' a model predicts correctly, but 'why'—specifically identifying the causal biological motifs it has learned."

---
SLIDE 02: INTRODUCTION - THE NON-CODING LANDSCAPE
Visual Elements:
- [Diagram showing Promoter vs Enhancer looping]

Bullet Points:
- Non-coding DNA (98% of genome) contains critical switches.
- Promoters: Direct gene "on" switches.
- Enhancers: Distal "volume knobs" for gene expression.
- Challenges: Rare motifs, complex spacing, and "black box" modeling.

Speaker Notes:
"Most of our DNA doesn't code for proteins, but it contains the instructions for when and where to make them. Our goal is to classify these promoters and enhancers and decode the grammar hidden within them."

---
SLIDE 03: INTRODUCTION - CURRENT CHALLENGES
Visual Elements:
- [Image showing a generic DNN and a 'Black Box' label]

Bullet Points:
- Foundation models (DNABERT) are powerful but computationally heavy.
- Interpretability Gap: High accuracy ≠ high understanding.
- Need for lightweight, verifiable models for clinical/biological use.

Speaker Notes:
"Large foundation models are great at AUROC, but they are often too complex to interpret. We want a model that fits on a single GPU and tells us exactly which nucleotides matter most."

---
SLIDE 04: PROBLEM STATEMENT
Visual Elements:
- [Contrast image: Correlation (k-mer) vs Causation (ISM)]

Bullet Points:
- Standard methods identify common sequences (ZNF610) that don't drive function.
- How can we separate background genomic architecture from causal regulatory motifs?
- Can a small Transformer learn this without massive pre-training?

Speaker Notes:
"The core problem we address is distinguishing correlation from causation. Many sequences are enriched in promoters just because they are GC-rich, but they don't actually control transcription. We need a way to find the real causal drivers."

---
SLIDE 05: RESEARCH OBJECTIVES
Visual Elements:
- [Numbered list icon]

Bullet Points:
1. Implement a lightweight Transformer with ALiBi for positional logic.
2. Build a contrasting interpretability pipeline (K-mer vs ISM).
3. Statistically validate discovered motifs using the JASPAR database.
4. Demonstrate data efficiency in low-resource settings.

Speaker Notes:
"Our objectives were to build a robust model, create a pipeline to find causal motifs, and validate them against known biological databases."

---
SLIDE 06: SYSTEM OVERVIEW
Visual Elements:
- [Infographic: biological_summary.png]

Bullet Points:
- End-to-end pipeline from raw FASTA to validated motifs.
- Key components: Data Prep, Transformer Training, Interpretability, Statistical Validation.
- Output: Publication-ready figures and validated TF binding sites.

Speaker Notes:
"Here is the high-level flow. We take sequences, train our Transformer, then apply multiple interpretability methods to see what the model learned, finally validating it with JASPAR."

---
SLIDE 07: SYSTEM DIAGRAM
Visual Elements:
- [Large Figure: system_architecture.png]

Bullet Points:
- Input: 64k sequences (Promoters/Enhancers).
- Model: 4-layer Encoder + ALiBi.
- Output: 0.89 AUROC.
- Validation: JASPAR matching + Fisher's test.

Speaker Notes:
"This is our full system architecture. We use a 4-layer Transformer with ALiBi positional encoding. This specific encoding helps the model generalize across different sequence lengths and improves training stability."

---
SLIDE 08: MODULE 1 & 2: DATA & MODELING
Visual Elements:
- [Table snippet: dataset_statistics.csv]

Bullet Points:
- Data Split: 70/15/15 grouped by locus.
- Transformer Specs: 256 hidden dim, 8 heads per layer.
- Training: AMP for speed, RC augmentation for strand-invariance.

Speaker Notes:
"We split our data carefully to avoid leakage. Our model is compact, with only 2 million parameters, making it highly interpretable and efficient."

---
SLIDE 09: MODULE 3 & 4: EVALUATION & K-MER ANALYSIS
Visual Elements:
- [Performance plot or metrics table]

Bullet Points:
- Benchmark: 0.89 AUROC vs 0.87 (Baseline).
- K-mer enrichment finds "Landscape" motifs.
- Example: ZNF610 found as background feature (0.65x depleted in ISM).

Speaker Notes:
"Classification performance is strong. Interestingly, k-mer analysis finds common motifs like ZNF610, which we later prove are just 'background architecture' rather than causal drivers."

---
SLIDE 10: MODULE 5: IN-SILICO MUTAGENESIS (ISM)
Visual Elements:
- [Carousel of ISM curves: ism_example_*.png]

Bullet Points:
- Systematic single-base perturbations.
- Measures direct causal impact on model score.
- Discovers "High-Importance Windows" (6-10bp).

Speaker Notes:
"ISM is our most powerful tool. By mutating every base, we see which ones cause the model's prediction to drop. High-importance regions indicate the exact nucleotides the model uses as decision features."

---
SLIDE 11: MODULE 6: BIOLOGICAL VALIDATION
Visual Elements:
- [Table: motif_validation.csv]

Bullet Points:
- Match: Discovered motif aligns with TFAP2A (0.869 correlation).
- TFAP2A: Known regulator of neural crest/epithelial genes.
- Statistical proof: 1.51x enriched, p < 0.0001.

Speaker Notes:
"We didn't just find 'a' motif—we found TFAP2A. This is a biologically validated transcription factor. Our model 'discovered' it from the data without any prior knowledge."

---
SLIDE 12: RESULTS - PERFORMANCE & EFFICIENCY
Visual Elements:
- [Plot: data_efficiency.png]

Bullet Points:
- ALiBi provides a 13% AUROC boost with only 10% data.
- Stable performance across varying genomic lengths.
- Higher PR-AUC (0.92) indicates robust minority-class detection.

Speaker Notes:
"One of our biggest wins is efficiency. The ALiBi model is much better at learning from limited data, which is critical for rare regulatory elements."

---
SLIDE 13: RESULTS - MOTIF ENRICHMENT
Visual Elements:
- [Figure: results_summary.png]

Bullet Points:
- Top-Right: ZNF610 (Background) vs TFAP2A (Causal).
- Bottom-Left: 41.6% presence in high-ISM vs 32% in low-ISM.
- The model correctly prioritizes the "functional" motif.

Speaker Notes:
"Comparing our two discovery methods, we see that ISM identifies motifs that are significantly enriched in the regions the model thinks are important. This confirms the model's 'logic' is biologically sound."

---
SLIDE 14: SUMMARY & FUTURE WORK
Visual Elements:
- [Checklist icon: Midterm Readiness Summary table]

Bullet Points:
- Achieved efficient, interpretable DNA classification.
- Pipeline successfully distinguishes correlation from causation.
- Future: MPRA correlation, variant impact prediction, synthetic promoter design.

Speaker Notes:
"To summarize, we've successfully mapped how a Transformer learns DNA grammar. In the future, we hope to use this to predict the impact of disease-causing mutations and even design new regulatory sequences for therapy. Thank you!"

---
