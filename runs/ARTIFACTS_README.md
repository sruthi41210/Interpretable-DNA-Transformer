# DNA-SLM: Artifacts Overview

This directory contains all the materials required for your mid-term project submission and presentation. These assets have been generated based on the actual model outputs, statistical validations, and scientific discovery of the TFAP2A motif.

## 1. Directory Structure

-   `diagrams/`: High-resolution (300 DPI) PNG files for your slides and report.
-   `tables/`: Data summaries in CSV format (for Excel/Sheets) and LaTeX (for the formal report).
-   `report_sections/`: Individual Markdown files for each chapter of your midterm report.
-   `presentation/`: Slide-by-slide content, including speaker notes and visual cues.
-   `final_deliverables/`: Combined report draft and ready-to-move files.

## 2. Graphic Assets (`diagrams/`)

| File | Description | Recommended Slide |
| :--- | :--- | :--- |
| `system_architecture.png` | The high-level pipeline flow. | Slide 07 |
| `module_interaction.png` | Interaction between training, evaluation, and ISM. | Slide 08 |
| `results_summary.png` | 4-panel flagship figure (Performance + Discovery). | Slide 13 |
| `data_efficiency.png` | Line plot showing ALiBi vs. Baseline advantage. | Slide 12 |
| `biological_summary.png` | Infographic of the biological discovery flow. | Slide 06 |

## 3. Using the Tables (`tables/`)

-   **Excel/Google Sheets:** Import the `.csv` files directly to create your own stylized tables.
-   **LaTeX:** Copy the content of `dataset_statistics.tex` into your LaTeX main file.
-   **Word:** You can copy-paste the CSV data into Word and use the "Convert Text to Table" feature.

## 4. Presentation Instructions (`presentation/`)

1.  Open `presentation/slide_content.md`.
2.  Use the "Bullet Points" section for the text on each slide.
3.  Use the "Visual Elements" section to identify which diagram from `diagrams/` to insert.
4.  Use the "Speaker Notes" for your oral presentation script.

## 5. Report Assembly

The combined report draft is available at `final_deliverables/report_draft.md`. It follows the standard scientific structure: Abstract -> Intro -> Lit Review -> Methodology -> Discussion -> Future Work.

---
**Technical Specs:**
- All figures are 300 DPI minimum.
- All code implementation stats reflect the ~2000 lines developed in the `src/` directory.
- Statistical significance is calculated using a one-sided Fisher's Exact Test.
