# Table Placement Guide for Report Chapters

This guide shows exactly where to insert each table from `runs/tables/` into your formal report.

---

## **Chapter 2: Project Description and Goals**

### Section 2.2: Gaps Identified
**Table: Gaps Identified**
- **Source:** Create manually based on the text in `chapter2_project_description.md`
- **Format:** 2-column table (Gap ID | Description)
- Already included in the chapter text.

---

## **Chapter 3: Technical Specification**

### Section 3.1.1: Functional Requirements
**Table: Functional Requirements**
- **Source:** Already formatted in `chapter3_technical_specification.md`
- **Format:** 3-column table (FR ID | Requirement | Priority)

### Section 3.1.2: Non-Functional Requirements
**Table: Non-Functional Requirements**
- **Source:** Already formatted in `chapter3_technical_specification.md`
- **Format:** 3-column table (NFR ID | Requirement | Category)

### Section 3.2.2: Economic Feasibility
**Table: Economic Feasibility**
- **Source:** Already formatted in `chapter3_technical_specification.md`
- **Format:** 3-column table (Resource | Cost | Notes)

### Section 3.3.1: Hardware Specification
**Table: Hardware Requirements**
- **Source:** Already formatted in `chapter3_technical_specification.md`
- **Format:** 3-column table (Component | Minimum | Recommended)

### Section 3.3.2: Software Specification
**Table: Software Dependencies**
- **Source:** Already formatted in `chapter3_technical_specification.md`
- **Format:** 3-column table (Software | Version | Purpose)

### Section 3.3 (End): Dataset Statistics
**Table: Dataset Statistics Summary**
- **Source:** `runs/tables/dataset_statistics.csv`
- **LaTeX Version:** `runs/tables/dataset_statistics.tex`
- **Format:** 6-column table (Dataset | Total Sequences | Positive | Negative | Avg Length | GC Content)

**How to Insert:**
- **Word:** Import CSV → Data → From Text/CSV → Select `dataset_statistics.csv` → Format as table.
- **LaTeX:** Copy the contents of `dataset_statistics.tex` directly into your document.

---

## **Chapter 4: Design Approach and Details**

### Section 4.1: System Architecture
**Table: Model Architecture Comparison**
- **Source:** `runs/tables/model_architecture.csv`
- **Format:** 3-column table (Component | Baseline | ALiBi)
- **Placement:** After the system architecture description, before the DFD section.

**How to Insert:**
```latex
\begin{table}[h]
\centering
\caption{Model Architecture Specifications}
\begin{tabular}{lcc}
\hline
\textbf{Component} & \textbf{Baseline} & \textbf{ALiBi} \\ \hline
Layers & 4 & 4 \\
Attention Heads & 8 & 8 \\
Hidden Dimension & 256 & 256 \\
Positional Encoding & Learned & ALiBi (linear bias) \\
Parameters & ~2.1M & ~2.1M \\
... & ... & ... \\ \hline
\end{tabular}
\end{table}
```

---

## **Chapter 5: Methodology and Testing**

### Section 5.2.1: Unit Testing
**Table: Unit Test Cases**
- **Source:** Already formatted in `chapter5_methodology_testing.md`
- **Format:** 5-column table (Test Case | Module | Input | Expected Output | Status)

### Section 5.2.2: Integration Testing
**Table: Integration Test Cases**
- **Source:** Already formatted in `chapter5_methodology_testing.md`
- **Format:** 3-column table (Test Case | Description | Status)

### Section 5.2.3: Validation Testing (Model Performance)
**Table: Performance Metrics Comparison**
- **Source:** `runs/tables/performance_metrics.csv`
- **Format:** 4-column table (Metric | Baseline | ALiBi | Target)
- **Placement:** After the validation testing description.

**CSV Contents:**
```
Metric,Baseline,ALiBi,Improvement
AUROC,0.87,0.89,+2.3%
PR-AUC,0.90,0.92,+2.2%
Accuracy,0.81,0.83,+2.5%
Precision,0.80,0.82,+2.5%
Recall,0.82,0.84,+2.4%
F1-Score,0.81,0.83,+2.5%
ECE (Calibration),0.08,0.06,-25%
```

### Section 5.3: Results Summary
**Table: Motif Validation Summary**
- **Source:** `runs/tables/motif_validation.csv`
- **Format:** 7-column table (Analysis Method | Discovered Motif | JASPAR Match | Correlation | Enrichment | P-value | Interpretation)
- **Placement:** End of Chapter 5.

**CSV Contents:**
```
Analysis Method,Discovered Motif,JASPAR Match,Correlation,Enrichment,P-value,Interpretation
K-mer Enrichment,GC-rich clusters,ZNF610,0.972,0.65x,0.013,Background (depleted)
ISM Windows,GCCNNNGGC,TFAP2A,0.869,1.51x,1.04e-05,Causal (enriched)
Core Element Test,TATA/Inr,TBP/Inr,0.72,1.2x,0.004,Architecture (significant)
```

---

## **Appendix (Optional)**

### Implementation Status Table
**Table: Module Implementation Status**
- **Source:** `runs/tables/implementation_status.csv`
- **Format:** 5-column table (Module | Component | Status | Output | Lines of Code)
- **Placement:** Appendix A or at the end of Chapter 5.

**CSV Contents:**
```
Module,Component,Status,Output,Lines of Code
Data Prep,make_splits.py,✅ Complete,Train/val/test CSVs,150
Data Prep,CharTokenizer,✅ Complete,Encoded sequences,80
Model,TinyDNAEncoder,✅ Complete,Baseline model,200
...
```

---

## Quick Reference: Table to Chapter Mapping

| Table File | Chapter | Section | Description |
| :--- | :---: | :--- | :--- |
| `dataset_statistics.csv` | 3 | 3.3 System Specification | Dataset breakdown by split and class. |
| `model_architecture.csv` | 4 | 4.1 System Architecture | Baseline vs ALiBi model specs. |
| `performance_metrics.csv` | 5 | 5.2.3 Validation Testing | AUROC, PR-AUC, F1, etc. |
| `motif_validation.csv` | 5 | 5.3 Results Summary | TFAP2A enrichment validation. |
| `implementation_status.csv` | 5 or Appendix | End of Chapter 5 | Code audit summary. |

---

## How to Format Tables in Word

1. Open the CSV file in Excel.
2. Copy the table.
3. Paste into Word.
4. Select the pasted content → Insert → Table → Convert Text to Table.
5. Apply a professional table style (e.g., "Grid Table 5 Dark - Accent 1").

## How to Format Tables in LaTeX

Use the `\begin{table}` environment with `\begin{tabular}` for the content. Example:

```latex
\begin{table}[h]
\centering
\caption{Performance Metrics Comparison}
\begin{tabular}{lccc}
\hline
\textbf{Metric} & \textbf{Baseline} & \textbf{ALiBi} & \textbf{Improvement} \\ \hline
AUROC & 0.87 & 0.89 & +2.3\% \\
PR-AUC & 0.90 & 0.92 & +2.2\% \\
... & ... & ... & ... \\ \hline
\end{tabular}
\label{tab:performance}
\end{table}
```
