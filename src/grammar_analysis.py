"""
Motif Grammar Analysis  (Phase 6)
=================================
Analyses TFAP2A motif spacing, co-occurrence with other JASPAR motifs,
and outputs figures + summary CSV/TXT to runs/interpret/grammar/.

Usage
-----
python src/grammar_analysis.py \
    --top_windows  runs/csv/top_windows_alibi.csv \
    --splits_csv   data/pro_splits.csv data/enh_splits.csv \
    --jaspar_file  data/JASPAR2024_CORE_vertebrates.txt \
    --jaspar_matches runs/interpret/jaspar_matches_k6.csv \
    --out_dir      runs/interpret/grammar \
    --n_windows    1000
"""

import argparse, os, sys, textwrap
import numpy as np
import pandas as pd
import regex
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from Bio import motifs as bio_motifs
from collections import Counter, defaultdict

# ── Constants ────────────────────────────────────────────────────────────
TFAP2A_PATTERN = r"GCC[ACGT]{3}GGC"       # canonical GCCNNNGGC
TFAP2A_IDS     = {"MA0872.1", "MA0810.2", "MA0003.5"}
CONTEXT_FLANK  = 50   # bp flanking each side of a high-ISM window


# ── Helpers ──────────────────────────────────────────────────────────────

def fuzzy_motif_positions(seq, pattern=TFAP2A_PATTERN, max_sub=1):
    """Return list of (start, end, matched_string) for fuzzy matches."""
    hits = []
    for m in regex.finditer(f"({pattern}){{s<={max_sub}}}", seq, overlapped=True):
        hits.append((m.start(), m.end(), m.group()))
    return hits


def extract_context(seq, start, window_len, flank=CONTEXT_FLANK):
    """Extract a context window from *seq* centred on [start, start+window_len)."""
    left  = max(0, start - flank)
    right = min(len(seq), start + window_len + flank)
    return seq[left:right], left


def load_sequences(splits_csvs, split="test"):
    """Load sequences from one or more splits CSV files.
    Returns dict  seq_index -> sequence  (global index across all files)."""
    all_seqs = {}
    offset = 0
    for csv_path in splits_csvs:
        df = pd.read_csv(csv_path)
        df_split = df[df["split"] == split].reset_index(drop=True)
        for i, row in df_split.iterrows():
            all_seqs[offset + i] = str(row["seq"]).upper()
        offset += len(df_split)
    return all_seqs


def jaspar_pwm_to_scorer(jaspar_motif):
    """Convert a Biopython JASPAR motif to a simple PWM log-odds scorer.
    Returns (pwm_array[4, L], consensus_len)."""
    arr = np.array([jaspar_motif.counts[b] for b in "ACGT"], dtype=float)
    arr = arr / (arr.sum(axis=0, keepdims=True) + 1e-9)        # freq
    log_odds = np.log2(arr / 0.25 + 1e-9)                       # vs uniform bg
    return log_odds, arr.shape[1]


BASE2IDX = {"A": 0, "C": 1, "G": 2, "T": 3}

def scan_pwm(seq, log_odds, threshold_frac=0.70):
    """Scan *seq* with a log-odds PWM; return True if any window >= threshold."""
    L = log_odds.shape[1]
    if len(seq) < L:
        return False
    max_possible = log_odds.max(axis=0).sum()
    threshold = threshold_frac * max_possible
    for i in range(len(seq) - L + 1):
        score = 0.0
        for j in range(L):
            b = seq[i + j]
            if b in BASE2IDX:
                score += log_odds[BASE2IDX[b], j]
            # unknown bases contribute 0
        if score >= threshold:
            return True
    return False


# ── Main Analysis ────────────────────────────────────────────────────────

def analyse_spacing(context_windows):
    """Compute inter-motif distances for windows with >=2 TFAP2A hits."""
    all_distances = []
    n_multi = 0
    for ctx_seq, _ in context_windows:
        hits = fuzzy_motif_positions(ctx_seq)
        if len(hits) >= 2:
            n_multi += 1
            starts = sorted(h[0] for h in hits)
            for i in range(len(starts)):
                for j in range(i + 1, len(starts)):
                    all_distances.append(starts[j] - starts[i])
    return all_distances, n_multi


def analyse_cooccurrence(context_windows, jaspar_motifs_subset):
    """For each JASPAR motif, count how many context windows contain it."""
    cooccurrence = {}
    n_windows = len(context_windows)
    for jm in jaspar_motifs_subset:
        lo, L = jaspar_pwm_to_scorer(jm)
        count = 0
        for ctx_seq, _ in context_windows:
            if scan_pwm(ctx_seq, lo):
                count += 1
        cooccurrence[f"{jm.name} ({jm.matrix_id})"] = {
            "count": count,
            "fraction": count / max(n_windows, 1),
        }
    return cooccurrence


def plot_spacing_histogram(distances, out_path):
    """Plot histogram of inter-TFAP2A-site distances."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if distances:
        bins = np.arange(0, max(distances) + 5, 5)
        ax.hist(distances, bins=bins, color="#3b82f6", edgecolor="white",
                linewidth=0.6, alpha=0.85)
    ax.set_xlabel("Inter-motif distance (bp)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("TFAP2A Inter-Motif Spacing in High-ISM Windows", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"  Saved {out_path}")


def plot_cooccurrence(cooccurrence, out_path, top_n=20):
    """Horizontal bar chart of motif co-occurrence fractions."""
    if not cooccurrence:
        return
    df = (pd.DataFrame(cooccurrence).T
            .sort_values("fraction", ascending=False)
            .head(top_n))
    fig, ax = plt.subplots(figsize=(8, max(4, 0.35 * len(df))))
    bars = ax.barh(df.index[::-1], df["fraction"][::-1],
                   color="#8b5cf6", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Fraction of high-ISM windows containing motif", fontsize=11)
    ax.set_title("Motif Co-occurrence with TFAP2A in High-ISM Windows", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    # value labels
    for bar, val in zip(bars, df["fraction"][::-1]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"  Saved {out_path}")


def write_summary_txt(out_path, n_windows, n_tfap2a_windows, n_multi,
                      distances, cooccurrence):
    """Write 3-4 sentence plain-English interpretation."""
    med_dist = int(np.median(distances)) if distances else 0
    mean_dist = float(np.mean(distances)) if distances else 0.0
    pct_with = n_tfap2a_windows / max(n_windows, 1) * 100

    top_cooc = ""
    if cooccurrence:
        by_frac = sorted(cooccurrence.items(), key=lambda x: x[1]["fraction"],
                         reverse=True)
        top3 = [name for name, _ in by_frac[:3]]
        top_cooc = ", ".join(top3)

    lines = [
        f"Of the {n_windows} high-ISM context windows analysed, "
        f"{n_tfap2a_windows} ({pct_with:.1f}%) contain at least one "
        f"TFAP2A motif instance (GCCNNNGGC, <=1 mismatch).",

        f"{n_multi} windows contain two or more TFAP2A sites, yielding "
        f"{len(distances)} pairwise inter-motif distances with a median "
        f"spacing of {med_dist} bp (mean {mean_dist:.1f} bp)."
        + (" This relatively tight spacing suggests the model has learned "
           "to recognise clustered TFAP2A binding sites as a feature of "
           "promoter sequences." if med_dist and med_dist < 40 else ""),
    ]
    if top_cooc:
        lines.append(
            f"The motifs most frequently co-occurring with TFAP2A in "
            f"these windows are: {top_cooc}."
        )

    with open(out_path, "w") as f:
        f.write("\n\n".join(lines) + "\n")
    print(f"  Saved {out_path}")


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Motif Grammar Analysis (Phase 6)")
    ap.add_argument("--top_windows", required=True,
                    help="Path to top_windows_alibi.csv")
    ap.add_argument("--splits_csv", nargs="+", required=True,
                    help="One or more splits CSV files (pro + enh)")
    ap.add_argument("--jaspar_file",
                    default="data/JASPAR2024_CORE_vertebrates.txt",
                    help="Path to JASPAR PFM file")
    ap.add_argument("--jaspar_matches",
                    default="runs/interpret/jaspar_matches_k6.csv",
                    help="Ranked JASPAR matches CSV (for co-occurrence subset)")
    ap.add_argument("--out_dir", default="runs/interpret/grammar")
    ap.add_argument("--n_windows", type=int, default=1000,
                    help="Number of top ISM windows to analyse")
    ap.add_argument("--split", default="test")
    ap.add_argument("--cooc_top_n", type=int, default=50,
                    help="Number of top JASPAR motifs for co-occurrence scan")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # ── 1. Load top ISM windows ──────────────────────────────────────
    print("Loading top ISM windows...")
    wdf = pd.read_csv(args.top_windows)
    wdf = wdf.head(args.n_windows)
    print(f"  Using top {len(wdf)} windows")

    # ── 2. Load full sequences from both splits ──────────────────────
    print("Loading sequences from splits CSV(s)...")
    seqs = load_sequences(args.splits_csv, split=args.split)
    print(f"  Loaded {len(seqs)} sequences")

    # ── 3. Extract context windows ───────────────────────────────────
    print("Extracting context windows...")
    context_windows = []
    for _, row in wdf.iterrows():
        si = int(row["seq_index"])
        if si not in seqs:
            continue
        full_seq = seqs[si]
        start = int(row["start"])
        w_len = int(row["window"])
        ctx_seq, ctx_start = extract_context(full_seq, start, w_len)
        context_windows.append((ctx_seq, ctx_start))
    print(f"  Extracted {len(context_windows)} context windows "
          f"(+-{CONTEXT_FLANK}bp flanks)")

    # ── 4. TFAP2A occurrence scan ────────────────────────────────────
    print("Scanning for TFAP2A motifs (fuzzy)...")
    n_with_tfap2a = 0
    for ctx_seq, _ in context_windows:
        if fuzzy_motif_positions(ctx_seq):
            n_with_tfap2a += 1
    print(f"  {n_with_tfap2a}/{len(context_windows)} windows contain "
          f">= 1 TFAP2A hit")

    # ── 5. Inter-motif spacing ───────────────────────────────────────
    print("Analysing inter-motif spacing...")
    distances, n_multi = analyse_spacing(context_windows)
    print(f"  {n_multi} windows with >= 2 TFAP2A sites, "
          f"{len(distances)} pairwise distances")

    plot_spacing_histogram(
        distances, os.path.join(args.out_dir, "tfap2a_spacing_histogram.png"))

    # ── 6. Co-occurrence with other JASPAR motifs ────────────────────
    print("Loading JASPAR motifs for co-occurrence scan...")
    jaspar_all = []
    try:
        with open(args.jaspar_file) as f:
            jaspar_all = list(bio_motifs.parse(f, "jaspar"))
    except Exception as e:
        print(f"  Warning: could not load JASPAR file: {e}")

    # Select top N motifs from the matches CSV, excluding TFAP2A
    cooccurrence = {}
    if jaspar_all and os.path.exists(args.jaspar_matches):
        matches_df = pd.read_csv(args.jaspar_matches)
        # Determine the ID column name
        id_col = "jaspar_id" if "jaspar_id" in matches_df.columns else "id"
        top_ids = (matches_df[~matches_df[id_col].isin(TFAP2A_IDS)]
                   .head(args.cooc_top_n)[id_col].tolist())

        jaspar_subset = [jm for jm in jaspar_all if jm.matrix_id in set(top_ids)]
        print(f"  Scanning {len(jaspar_subset)} JASPAR motifs for co-occurrence "
              f"across {len(context_windows)} windows...")

        cooccurrence = analyse_cooccurrence(context_windows, jaspar_subset)

        plot_cooccurrence(
            cooccurrence,
            os.path.join(args.out_dir, "cooccurrence_heatmap.png"),
            top_n=20)
    else:
        print("  Skipping co-occurrence (JASPAR data unavailable)")

    # ── 7. Summary CSV ───────────────────────────────────────────────
    summary_rows = []
    summary_rows.append({
        "metric": "total_context_windows",
        "value": len(context_windows),
    })
    summary_rows.append({
        "metric": "windows_with_tfap2a",
        "value": n_with_tfap2a,
    })
    summary_rows.append({
        "metric": "windows_with_multi_tfap2a",
        "value": n_multi,
    })
    summary_rows.append({
        "metric": "pairwise_distances_count",
        "value": len(distances),
    })
    if distances:
        summary_rows.append({
            "metric": "median_inter_motif_distance_bp",
            "value": int(np.median(distances)),
        })
        summary_rows.append({
            "metric": "mean_inter_motif_distance_bp",
            "value": round(float(np.mean(distances)), 1),
        })

    # Add top co-occurring motifs as rows
    if cooccurrence:
        by_frac = sorted(cooccurrence.items(),
                         key=lambda x: x[1]["fraction"], reverse=True)
        for rank, (name, info) in enumerate(by_frac[:10], 1):
            summary_rows.append({
                "metric": f"cooccurrence_rank{rank}",
                "value": f"{name}: {info['fraction']:.3f}",
            })

    summary_csv = os.path.join(args.out_dir, "grammar_summary.csv")
    pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)
    print(f"  Saved {summary_csv}")

    # ── 8. Plain-text summary ────────────────────────────────────────
    write_summary_txt(
        os.path.join(args.out_dir, "grammar_summary.txt"),
        n_windows=len(context_windows),
        n_tfap2a_windows=n_with_tfap2a,
        n_multi=n_multi,
        distances=distances,
        cooccurrence=cooccurrence,
    )

    print("\nDone! All outputs in:", args.out_dir)


if __name__ == "__main__":
    main()
