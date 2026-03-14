# Image Placement Guide for Report Chapters

This guide maps each generated/available image to the appropriate chapter and section in the formal report.

---

## **Chapter 1: Introduction**
No images required.

---

## **Chapter 2: Project Description and Goals**

| Section | Image | Location |
| :--- | :--- | :--- |
| 2.5 Project Plan | `runs/diagrams/biological_summary.png` | End of section, to illustrate the project flow. |

---

## **Chapter 3: Technical Specification**

| Section | Image/Table | Location |
| :--- | :--- | :--- |
| 3.3 System Specification | `runs/tables/dataset_statistics.csv` (render as table) | After 3.3.2 Software Specification. |

---

## **Chapter 4: Design Approach and Details**

| Section | Image | Location | Status |
| :--- | :--- | :--- | :---: |
| 4.1 System Architecture | `runs/diagrams/system_architecture.png` | After architecture description. | ✅ Available |
| 4.2.1 DFD Level 0 | `runs/diagrams/dfd_level0.png` | After DFD Level 0 description. | ✅ Available |
| 4.2.1 DFD Level 1 | Render from `runs/diagrams/dfd_level1.puml` | After DFD Level 1 description. | ⚠️ Needs rendering |
| 4.2.2 Class Diagram | Render from `runs/diagrams/class_diagram.puml` | After Class Diagram description. | ⚠️ Needs rendering |
| 4.3 Module Interaction | `runs/diagrams/module_interaction.png` | After module interaction description. | ✅ Available |

**How to Render PlantUML Files:**
1. Go to https://www.plantuml.com/plantuml/uml/
2. Paste the contents of the `.puml` file.
3. Download the generated PNG image.
4. Save to `runs/diagrams/` with the appropriate name (e.g., `dfd_level1.png`, `class_diagram.png`).

---

## **Chapter 5: Methodology and Testing**

| Section | Image | Location |
| :--- | :--- | :--- |
| 5.1 Module 6 (ISM) | `runs/diagrams/results_summary.png` | After ISM module description. |
| 5.2.3 Validation Testing | `runs/diagrams/data_efficiency.png` | After performance table. |
| 5.3 Results Summary | `runs/tables/motif_validation.csv` (render as table) | End of chapter. |

---

## Summary of All Available Images

| Filename | Description | Generated? |
| :--- | :--- | :---: |
| `system_architecture.png` | High-level pipeline diagram. | ✅ Yes |
| `module_interaction.png` | Software module interaction flowchart. | ✅ Yes |
| `results_summary.png` | 4-panel flagship results figure. | ✅ Yes |
| `data_efficiency.png` | ALiBi vs Baseline learning curve. | ✅ Yes |
| `biological_summary.png` | End-to-end biological discovery infographic. | ✅ Yes |
| `dfd_level0.png` | Context Diagram (DFD Level 0). | ✅ Yes |
| `dfd_level1.png` | DFD Level 1. | ⚠️ Needs rendering from `.puml` |
| `class_diagram.png` | UML Class Diagram. | ⚠️ Needs rendering from `.puml` |

---

## How to Insert Images into Word/LaTeX Report

**Word:**
1. Go to Insert > Pictures > From File.
2. Navigate to `runs/diagrams/` and select the image.
3. Resize to fit the page width (typically 15-16 cm).

**LaTeX:**
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{runs/diagrams/system_architecture.png}
\caption{System Architecture of DNA-SLM}
\label{fig:system-arch}
\end{figure}
```
