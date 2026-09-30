"""Render every self-contained AI4Sci plot module to PNG."""

from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent


def load_module(path: Path):
    module_name = "ai4sci_" + "_".join(path.relative_to(ROOT).parts[:-1])
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_all(output_dir: Path, dpi: int) -> int:
    paths = sorted(ROOT.glob("figure*/**/plot.py"))
    for path in paths:
        module = load_module(path)
        figure = module.render(module.prepare_data(), module.PLOT_SETTINGS)
        destination = output_dir / path.parent.relative_to(ROOT).with_suffix(".png")
        destination.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(destination, dpi=dpi, bbox_inches="tight")
        plt.close(figure)
        print(destination.relative_to(ROOT) if destination.is_relative_to(ROOT) else destination)
    return len(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "rendered")
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()
    count = render_all(args.output_dir.resolve(), args.dpi)
    print(f"Rendered {count} plots.")


if __name__ == "__main__":
    main()
