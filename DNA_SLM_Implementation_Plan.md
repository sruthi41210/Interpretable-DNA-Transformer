# DNA-SLM: Phase 2 Implementation Plan
### Interpretable DNA Transformers — Road to Review 3 & Beyond
**Project:** Interpretable DNA Transformers for Regulatory Sequence Classification  
**Hardware:** RTX 4060 Laptop (8GB VRAM) · 32GB RAM · Windows 11 · CUDA 12.7  
**Review 3 Date:** April 24, 2025  
**Plan Created:** March 12, 2025  

---

## How to use this file
- Work through tasks in order — each builds on the previous
- `[ ]` = not started · `[x]` = done · `[~]` = in progress
- Tasks marked **[GPU]** need the laptop running — schedule for evenings/weekends
- Tasks marked **[AGENT]** = prompt your code agent to write the code, then you run it
- Tasks marked **[WRITE]** = you write this in the report yourself
- Estimated times are for *implementation*, not including GPU training runs

---

## CURRENT STATE (as of March 12)

```
✅ Data pipeline (make_splits, tokenizers, dataset)
✅ TinyDNAEncoder baseline + ALiBi variant (6L, 6H, d=192, ~2.1M params)
✅ Training pipeline (AdamW, AMP, early stopping on val PR-AUC)
✅ Results: AUROC 0.89 | PR-AUC 0.92 | ECE 0.06
✅ ISM pipeline → top_windows_alibi.csv (top 5000 6bp windows)
✅ K-mer enrichment → ZNF610/VEZF1 identified as background
✅ JASPAR validation → TFAP2A confirmed (p=1.04e-05, OR=1.51)
✅ Grammar analysis → 26.1% TFAP2A hit rate, 16bp median spacing, KLF7 co-occurrence
✅ Hyperparameter logging → runs/hparams.json
⚠️  README/report says 4L/4H but code is 6L/6H — needs verification
```

---

## PHASE A — Strengthen Existing Results
> **Goal:** Make current findings bulletproof before adding anything new.  
> **Timeline:** Week 1 (March 13–19) · Mostly weekday evenings · No GPU needed

---

### A1 — Verify architecture discrepancy
> **Why:** README says 4 layers/4 heads, code says 6 layers/6 heads. Must resolve before ablations.  
> **Time:** ~15 minutes

- [ ] **A1.1** Open `runs/hparams.json` — check `num_layers` and `num_heads` values
- [ ] **A1.2** Open `src/models/model_alibi.py` — confirm actual architecture
- [ ] **A1.3** Cross-check against the model checkpoint: load `runs/checkpoints/best_alibi.pt` and count layers
  ```python
  import torch
  ckpt = torch.load('runs/checkpoints/best_alibi.pt', map_location='cpu')
  print([k for k in ckpt.keys() if 'layers' in k])
  ```
- [ ] **A1.4** Update `README.md` and report (Chapter 3) with the correct numbers
- [ ] **A1.5** [WRITE] Add a note in report: "The final architecture uses 6 transformer layers and 6 attention heads with embedding dimension 192, totalling ~2.1M parameters."

---

### A2 — Low-ISM background comparison
> **Why:** You have 26.1% TFAP2A in high-ISM windows. The obvious question is: what about low-ISM windows? This single comparison doubles the strength of your causal claim.  
> **Time:** ~30 minutes · [AGENT]

- [ ] **A2.1** [AGENT] Create `src/interpretation/background_comparison.py`:
  - Load `runs/csv/top_windows_alibi.csv` — these are your HIGH-ISM windows
  - Load the full ISM output (or resample bottom 1000 by ISM score) — these are LOW-ISM windows
  - Run TFAP2A fuzzy scan (`GCC[ACGT]{3}GGC`, ≤1 mismatch) on both sets
  - Output: a simple bar chart `runs/interpret/tfap2a_high_vs_low_ism.png`
  - Output: `runs/interpret/background_comparison.csv` with counts and percentages
  - Run Fisher's Exact Test between the two rates — save p-value
- [ ] **A2.2** Run the script and check output
- [ ] **A2.3** Expected result: ~12–15% in low-ISM vs 26.1% in high-ISM
- [ ] **A2.4** [WRITE] Add to Results section: "TFAP2A motif frequency was X% in high-ISM windows vs Y% in low-ISM windows (Fisher's p=Z), confirming the causal enrichment is specific to model-important regions."

---

### A3 — Negative controls (dinucleotide-shuffled sequences)
> **Why:** Proves your model isn't just detecting GC content. Essential for scientific rigour. Reviewers will ask this.  
> **Time:** ~45 minutes · [AGENT]

- [ ] **A3.1** [AGENT] Create `src/interpretation/negative_controls.py`:
  - Load 100 high-confidence promoter sequences from the test set (model score > 0.9)
  - For each, generate a dinucleotide-shuffled version:
    - Preserves GC content AND dinucleotide frequency
    - Uses `ushuffle` or implement manually by shuffling di-nucleotide pairs
  - Run ISM on both real and shuffled sequences using existing `mutagenesis.py` logic
  - Plot: side-by-side ISM importance curves — real vs shuffled
  - Output: `runs/interpret/negative_controls/ism_real_vs_shuffled.png`
  - Output: `runs/interpret/negative_controls/negative_control_summary.csv`
    - Columns: seq_id, real_max_importance, shuffled_max_importance, real_tfap2a_hit, shuffled_tfap2a_hit
- [ ] **A3.2** Run the script
- [ ] **A3.3** Expected result: shuffled sequences show flat/noisy ISM curves with no TFAP2A peaks
- [ ] **A3.4** [WRITE] Add to Methods: "To confirm the model responds to sequence-specific features rather than nucleotide composition, we generated dinucleotide-shuffled controls for 100 high-confidence test sequences and confirmed that ISM importance scores were uniformly low (mean importance < X vs Y for real sequences)."

---

### A4 — Fix JASPAR discrepancy in report
> **Why:** The gap between code fix (done) and report explanation (not done) is still there.  
> **Time:** ~20 minutes · [WRITE] only

- [ ] **A4.1** [WRITE] In report Chapter 5 (Results), under JASPAR section, add this paragraph:
  > "Raw PWM correlation ranked VEZF1 (r=0.729) above TFAP2A (r=0.869) due to shared palindromic GC-rich structure. However, PWM correlation measures motif shape similarity, not biological relevance. The Fisher's Exact Test, which directly measures motif enrichment in causal (high-ISM) versus non-causal (low-ISM) windows, identified TFAP2A as the statistically significant hit (OR=1.51, p=1.04×10⁻⁵). TFAP2A is therefore selected as the primary validated motif based on enrichment evidence, not correlation rank."
- [ ] **A4.2** Verify `jaspar_compare.py` output CSV has `enrichment_validated=True` for TFAP2A rows

---

## PHASE B — Ablation Studies
> **Goal:** Prove every design choice (ALiBi, RC augmentation, architecture depth) was justified.  
> **Timeline:** Week 2 (March 20–26) · Weekend GPU runs · Code prep on weekday evenings  
> **This is what separates a capstone from a paper.**

---

### B1 — Design the ablation matrix
> **Time:** ~20 minutes · Planning only

- [ ] **B1.1** Define the 5 ablation variants to train:

| Variant ID | Description | Changes from full model |
|---|---|---|
| V1 | Full model (baseline) | Already trained ✅ |
| V2 | No ALiBi (learned positional embeddings) | Already trained ✅ |
| V3 | ALiBi, no RC augmentation | Remove RC aug from train loop |
| V4 | ALiBi, 4 layers instead of 6 | num_layers=4 |
| V5 | ALiBi, 3 layers (even smaller) | num_layers=3 |

- [ ] **B1.2** Confirm V1 and V2 checkpoints exist in `runs/checkpoints/`
- [ ] **B1.3** Each training run takes ~25–30 mins on RTX 4060 — can run all 3 new variants in one evening

---

### B2 — Implement ablation training configs
> **Time:** ~45 minutes · [AGENT]

- [ ] **B2.1** [AGENT] Create `src/training/train_ablation.py`:
  - Accepts CLI args: `--variant V3/V4/V5`
  - V3: set `use_rc_augmentation=False` in training loop
  - V4: set `num_layers=4` in model config
  - V5: set `num_layers=3` in model config
  - Saves checkpoint to `runs/checkpoints/ablation_{variant}.pt`
  - Saves metrics to `runs/ablation_{variant}_metrics.json`
- [ ] **B2.2** [AGENT] Create `src/training/run_all_ablations.sh` (bash script):
  ```bash
  python src/training/train_ablation.py --variant V3
  python src/training/train_ablation.py --variant V4
  python src/training/train_ablation.py --variant V5
  ```
- [ ] **B2.3** Verify script runs correctly on V3 for 1 epoch before launching full run

---

### B3 — Run ablation training [GPU]
> **Time:** ~90 minutes total GPU time · Run Saturday evening, collect results Sunday  
> **Leave laptop plugged in, GPU fans will spin up**

- [ ] **B3.1** Run: `bash src/training/run_all_ablations.sh`
- [ ] **B3.2** Monitor first run for OOM errors — if VRAM issues, reduce batch size from default to 32
- [ ] **B3.3** Confirm 3 new checkpoint files exist in `runs/checkpoints/`

---

### B4 — Compile ablation results table
> **Time:** ~30 minutes · [AGENT]

- [ ] **B4.1** [AGENT] Create `src/analysis/compile_ablations.py`:
  - Load all 5 metrics JSON files
  - Output a summary table to `runs/ablation_summary.csv`
  - Generate a grouped bar chart: AUROC and PR-AUC across all 5 variants
  - Save to `runs/ablation_comparison.png`
- [ ] **B4.2** Run the script
- [ ] **B4.3** Expected: Full model (V1) should outperform all ablations — if it doesn't, investigate why
- [ ] **B4.4** [WRITE] Add Table to report Chapter 5: full ablation results table

---

### B5 — Data efficiency ablation (bonus, ~1 hour)
> **Why:** You already have the data efficiency curve for ALiBi vs baseline. Extend it to show V3/V4/V5 too.

- [ ] **B5.1** [AGENT] Extend `src/training/train_ablation.py` to accept `--data_fraction 0.1/0.25/0.5/1.0`
- [ ] **B5.2** Run data efficiency sweep for V1, V2, V4 only (3 variants × 4 fractions = 12 runs × ~8 mins = ~90 mins) [GPU]
- [ ] **B5.3** Plot updated data efficiency curves showing all variants

---

## PHASE C — Variant Effect Prediction
> **Goal:** Show your model has real clinical utility by predicting the effect of known disease mutations.  
> **Timeline:** Week 3 (March 27 – April 2) · Weekday evenings for data prep, weekend for analysis  
> **This is the highest-impact addition you can make.**

---

### C1 — Download ClinVar pathogenic promoter SNPs
> **Time:** ~45 minutes · Data acquisition

- [ ] **C1.1** Go to https://www.ncbi.nlm.nih.gov/clinvar/
- [ ] **C1.2** Search filter: Clinical significance = Pathogenic, Molecular consequence = regulatory_region_variant OR 5_prime_UTR_variant
- [ ] **C1.3** Download as VCF or tab-delimited file
- [ ] **C1.4** Alternatively, download from ClinVar FTP:
  ```
  https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
  ```
  Filter for `CLNSIG=Pathogenic` and `MC=regulatory_region_variant`
- [ ] **C1.5** Target: ~200–500 pathogenic SNPs in promoter regions
- [ ] **C1.6** Save filtered SNPs to `data/clinvar_pathogenic_promoter_snps.csv`

---

### C2 — Extract reference and mutant sequences
> **Time:** ~1 hour · [AGENT]

- [ ] **C2.1** [AGENT] Create `src/variant_effects/extract_sequences.py`:
  - Input: ClinVar SNP list (chr, position, ref_allele, alt_allele)
  - Use Biopython to fetch 500bp windows centred on each SNP from hg38 reference genome
  - Output reference sequence (wild-type) and mutant sequence (with SNP substituted)
  - Save to `data/variant_sequences.csv` with columns: snp_id, ref_seq, mut_seq, clinvar_sig, gene_name
- [ ] **C2.2** Note: hg38 reference can be downloaded from UCSC or use Biopython Entrez
  ```python
  # Quick approach using UCSC DAS or local reference if available
  from Bio import Entrez, SeqIO
  ```
- [ ] **C2.3** Alternatively — if reference genome download is too slow — use the existing EPDnew promoter sequences and manually introduce known TFAP2A-disrupting mutations (GCC→ACC at the first position)
- [ ] **C2.4** Verify: `data/variant_sequences.csv` has at least 100 sequence pairs

---

### C3 — Run variant effect scoring
> **Time:** ~30 minutes · [AGENT] · No GPU needed (inference only)

- [ ] **C3.1** [AGENT] Create `src/variant_effects/score_variants.py`:
  - Load best ALiBi model checkpoint
  - For each SNP: score reference sequence AND mutant sequence
  - Compute: `delta_score = ref_score - mut_score`
  - Positive delta = mutation reduces promoter confidence (predicted damaging)
  - Save to `runs/variant_effects/variant_scores.csv`
    - Columns: snp_id, ref_score, mut_score, delta_score, clinvar_sig, overlaps_tfap2a
  - Add `overlaps_tfap2a` column: True if SNP position falls within a TFAP2A motif hit
- [ ] **C3.2** Run the script
- [ ] **C3.3** [AGENT] Create `src/variant_effects/plot_variants.py`:
  - Scatter plot: delta_score distribution for pathogenic vs benign variants
  - Box plot: delta_score for SNPs overlapping TFAP2A vs not overlapping
  - Save to `runs/variant_effects/variant_effect_plot.png`

---

### C4 — Analyse and interpret results
> **Time:** ~30 minutes · Analysis

- [ ] **C4.1** Check: what % of pathogenic promoter SNPs show delta_score > 0.1? (model predicts damaging)
- [ ] **C4.2** Check: do SNPs overlapping TFAP2A sites show larger delta_scores?
- [ ] **C4.3** Run Mann-Whitney U test: delta_scores for TFAP2A-overlapping vs non-overlapping SNPs
- [ ] **C4.4** [WRITE] Add to report: "Of X pathogenic promoter variants from ClinVar, Y% (N/X) showed a predicted reduction in promoter activity (Δscore > 0.1). Variants overlapping TFAP2A binding sites showed significantly larger predicted effects (median Δscore = A vs B, Mann-Whitney p = Z)."

---

## PHASE D — Cross-Species Validation
> **Goal:** Test if your human-trained model generalises to mouse sequences — if it does, it learned real biology.  
> **Timeline:** Week 3–4 (can overlap with Phase C) · ~2 hours total

---

### D1 — Download mouse promoter sequences
> **Time:** ~20 minutes

- [ ] **D1.1** Go to https://epd.expasy.org/epd/ — same database you used for human data
- [ ] **D1.2** Select organism: Mus musculus (mouse)
- [ ] **D1.3** Download ~3,000–5,000 promoter sequences in FASTA format
- [ ] **D1.4** Save to `data/mouse_promoters.fasta`
- [ ] **D1.5** Download ~3,000 mouse enhancers from ENCODE (same as human pipeline):
  - https://www.encodeproject.org/ → filter by Mus musculus → enhancer annotations
- [ ] **D1.6** Save to `data/mouse_enhancers.fasta`

---

### D2 — Run zero-shot classification
> **Time:** ~30 minutes · [AGENT]

- [ ] **D2.1** [AGENT] Create `src/cross_species/zero_shot_eval.py`:
  - Load your human-trained ALiBi model (no retraining, zero-shot)
  - Tokenise mouse sequences using existing CharTokenizer (same A/C/G/T vocab)
  - Run inference on mouse promoters + mouse enhancers
  - Compute AUROC and PR-AUC on mouse data
  - Save metrics to `runs/cross_species/mouse_zero_shot_metrics.json`
- [ ] **D2.2** Run the script
- [ ] **D2.3** Expected: AUROC > 0.70 would be a meaningful result (lower than 0.89 but still above chance)

---

### D3 — Run ISM on mouse sequences
> **Time:** ~45 minutes · [AGENT]

- [ ] **D3.1** [AGENT] Create `src/cross_species/mouse_ism.py`:
  - Run ISM on top 200 high-confidence mouse promoter predictions
  - Extract high-importance windows
  - Run TFAP2A fuzzy scan on these windows
  - Compare hit rate to human result (26.1%)
  - Save to `runs/cross_species/mouse_tfap2a_hit_rate.json`
  - Plot: overlay of human vs mouse ISM importance curves (averaged)
- [ ] **D3.2** Run the script
- [ ] **D3.3** [WRITE] Add to report Discussion: "Zero-shot application to mouse promoters yielded AUROC of X, with TFAP2A motif hit rate of Y% in high-ISM windows — comparable to Z% in human sequences — suggesting the model has learned an evolutionarily conserved regulatory grammar rather than human-specific sequence statistics."

---

## PHASE E — Attention Head Analysis
> **Goal:** Understand what each of the 6 attention heads specialises in.  
> **Timeline:** Week 4 (April 3–9) · Weekday evenings · No GPU needed

---

### E1 — Extract attention weights
> **Time:** ~45 minutes · [AGENT]

- [ ] **E1.1** [AGENT] Create `src/interpretation/attention_analysis.py`:
  - Hook into the model's attention layers to extract weights during inference
  - Run on 50 high-confidence promoter sequences
  - For each sequence, extract attention matrix for all 6 heads across all 6 layers
  - Focus on the final layer (most task-relevant)
  - Save raw attention weights to `runs/interpret/attention/attention_weights.npy`
- [ ] **E1.2** [AGENT] Add visualisation to same script:
  - For each of the 6 heads in the last layer, plot average attention weight as a function of sequence position
  - Overlay with ISM importance scores for the same sequences
  - Does any head peak at TFAP2A positions?
  - Save to `runs/interpret/attention/head_specialisation.png`

---

### E2 — Characterise head roles
> **Time:** ~30 minutes · Analysis

- [ ] **E2.1** For each head, compute the correlation between its attention weights and ISM importance scores across the 50 sequences
- [ ] **E2.2** Identify: which head correlates most with TFAP2A positions?
- [ ] **E2.3** Identify: which heads attend globally (flat attention) vs locally (sharp peaks)?
- [ ] **E2.4** [AGENT] Create `runs/interpret/attention/head_correlation_table.csv`
- [ ] **E2.5** [WRITE] Add to report: a 2-sentence description of what each head appears to do

---

### E3 — Attention vs ISM comparison figure
> **Time:** ~20 minutes · [AGENT]

- [ ] **E3.1** [AGENT] Create a final summary figure: for 3 example sequences, show side-by-side:
  - Row 1: ISM importance score (ground truth causal signal)
  - Row 2: Best-correlated attention head weights
  - Row 3: Sequence with TFAP2A motif positions highlighted
  - Save to `runs/interpret/attention/ism_vs_attention_comparison.png`
- [ ] **E3.2** This figure demonstrates why attention alone is insufficient (attention ≠ explanation) and why ISM is superior — which is a core argument in your report

---

## PHASE F — Report & Presentation
> **Timeline:** Week 5–6 (April 10–24) · Every available session

---

### F1 — Update report with all new findings
> **Sections to rewrite/expand:**

- [ ] **F1.1** Abstract — rewrite to include ablations, variant effects, cross-species results
- [ ] **F1.2** Chapter 2 (Literature Review) — add 3–4 new papers from 2024–2025 found in the similar papers search
- [ ] **F1.3** Chapter 5.2 (Testing) — add ablation results table
- [ ] **F1.4** Chapter 5.3 (Results Summary) — expand with Phase C, D, E findings
- [ ] **F1.5** **[NEW] Chapter 5.5 — Discussion** (this is currently missing entirely):
  - Why does TFAP2A emerge as the causal motif? (biological context)
  - What does 16bp median spacing mean biologically? (dimer binding, helical turn)
  - What do the ablations prove about each design choice?
  - Limitations: single species primary training, 500bp context window, binary classification only
- [ ] **F1.6** **[NEW] Chapter 5.6 — Conclusion**:
  - Restate the problem
  - Summarise what was achieved
  - Clinical implications (variant effect prediction)
  - Future work: MPRA experimental validation, multi-species training, larger context windows

---

### F2 — Presentation preparation
> **The 10-minute structure (from your guide doc):**

- [ ] **F2.1** Build slides — max 8 slides:
  1. Title + one-sentence problem statement
  2. Why existing models fail (interpretability gap)
  3. Your architecture (TinyDNAEncoder diagram)
  4. Results: AUROC/PR-AUC + data efficiency curve
  5. Key finding: ISM discovered TFAP2A (causal vs correlative figure)
  6. Grammar analysis: 16bp spacing, KLF7 co-occurrence
  7. Ablations + variant effect prediction (if complete)
  8. Conclusion + future work
- [ ] **F2.2** Prepare answers for guaranteed questions (see your guide doc Section 4)
- [ ] **F2.3** Do one full dry run out loud — time yourself
- [ ] **F2.4** Prepare backup slides: ablation table, JASPAR match table, Fisher's test output

---

### F3 — Paper submission (optional but recommended)
> **If ablations + variant effects look strong, consider submitting to:**

- [ ] **F3.1** **ICCBB 2025** (International Conference on Computational Biology and Bioinformatics) — check deadline ~June 2025
- [ ] **F3.2** **BIBM 2025** (IEEE International Conference on Bioinformatics and Biomedicine) — deadline ~July 2025
- [ ] **F3.3** **BioRxiv preprint** — no deadline, post anytime, gives you a citable DOI immediately
- [ ] **F3.4** [AGENT] Ask agent to help structure an abstract for submission once Phase B and C are complete

---

## QUICK REFERENCE — Agent Prompt Templates

### For any new script:
```
Context: DNA-SLM project. Lightweight ALiBi Transformer (~2.1M params, 6L/6H/d=192) 
trained on 65k human promoter/enhancer sequences (500bp). Results: AUROC 0.89, 
PR-AUC 0.92. TFAP2A identified as causal motif via ISM (p=1.04e-05, OR=1.51).
Hardware: RTX 4060 8GB, Windows 11, CUDA 12.7, PyTorch 2.x.

Task: [describe task here]

If the script will take >30 seconds to run, write the code and tell me 
the exact command to run in my terminal. Do not execute long-running jobs.
```

### For report writing help:
```
I am writing the Discussion section of my B.Tech thesis on interpretable 
DNA transformers. Here is my key finding: [paste finding]. Help me write 
2-3 paragraphs that explain the biological significance, connect it to 
existing literature, and acknowledge limitations.
```

---

## PRIORITY ORDER (if time runs short)

| Must do before April 24 | Should do | Nice to have |
|---|---|---|
| A1 Architecture fix | B Ablation studies | E Attention analysis |
| A2 Low-ISM comparison | C Variant effect prediction | F3 Paper submission |
| A3 Negative controls | D Cross-species validation | B5 Data efficiency ablation |
| A4 JASPAR report fix | F1 Full report rewrite | — |
| F2 Presentation | — | — |

---

## FILE STRUCTURE (expected at completion)

```
dna-slm/
├── data/
│   ├── clinvar_pathogenic_promoter_snps.csv     [NEW - Phase C]
│   ├── mouse_promoters.fasta                     [NEW - Phase D]
│   └── mouse_enhancers.fasta                     [NEW - Phase D]
├── src/
│   ├── interpretation/
│   │   ├── background_comparison.py              [NEW - Phase A2]
│   │   ├── negative_controls.py                  [NEW - Phase A3]
│   │   └── attention_analysis.py                 [NEW - Phase E]
│   ├── training/
│   │   ├── train_ablation.py                     [NEW - Phase B]
│   │   └── run_all_ablations.sh                  [NEW - Phase B]
│   ├── variant_effects/
│   │   ├── extract_sequences.py                  [NEW - Phase C]
│   │   ├── score_variants.py                     [NEW - Phase C]
│   │   └── plot_variants.py                      [NEW - Phase C]
│   ├── cross_species/
│   │   ├── zero_shot_eval.py                     [NEW - Phase D]
│   │   └── mouse_ism.py                          [NEW - Phase D]
│   └── analysis/
│       └── compile_ablations.py                  [NEW - Phase B]
└── runs/
    ├── ablation_summary.csv                      [NEW - Phase B]
    ├── ablation_comparison.png                   [NEW - Phase B]
    ├── variant_effects/                          [NEW - Phase C]
    ├── cross_species/                            [NEW - Phase D]
    └── interpret/
        ├── attention/                            [NEW - Phase E]
        ├── grammar/                              [EXISTS]
        └── negative_controls/                   [NEW - Phase A3]
```

---

*Last updated: March 12, 2025 — created at project Phase 6 completion*  
*Next checkpoint: April 24 — Review 3 (Final)*
