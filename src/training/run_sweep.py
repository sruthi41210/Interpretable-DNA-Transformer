# src/run_sweep.py
import argparse, os, subprocess, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--splits", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    import yaml
    cfg = yaml.safe_load(open(args.config, "r"))
    fractions = cfg.get("fractions", [0.1,0.25,0.5,1.0])
    seeds = cfg.get("seeds", [42])

    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    for frac in fractions:
        for seed in seeds:
            run_name = f"frac{int(frac*100):03d}_seed{seed}"
            out = Path(args.out_dir) / run_name
            out.mkdir(parents=True, exist_ok=True)

            cmd = [
                "python", "-m", "src.train",
                "--splits_csv", args.splits,
                "--fraction", str(frac),
                "--seed", str(seed),
                "--out_dir", str(out),
            ]
            # append remaining args from yaml
            for k,v in cfg["train_args"].items():
                cmd += [f"--{k}", str(v)]
            print("RUN:", " ".join(cmd))
            subprocess.check_call(cmd)

if __name__ == "__main__":
    main()
