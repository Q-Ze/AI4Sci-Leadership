"""Render the current AI4Sci main and supplementary figures."""

from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
COLLECTIONS = ("main", "supplementary", "all")


def load_module(path: Path):
    module_name = "ai4sci_" + "_".join(path.relative_to(ROOT).parts[:-1])
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plot_paths(collection: str = "main") -> list[Path]:
    """Use the current project manifest for panel ordering and membership."""
    if collection not in COLLECTIONS:
        raise ValueError(f"Unknown collection: {collection}")
    paths = []
    if collection in ("main", "all"):
        project = ROOT / "figures"
        manifest = json.loads((project / "project.json").read_text(encoding="utf-8"))
        paths.extend(project / "plots" / item["directory"] / "plot.py"
                     for item in manifest["plots"])
    if collection in ("supplementary", "all"):
        paths.extend(sorted((ROOT / "supplementary").glob("*/plot.py")))
    if not paths:
        raise ValueError(f"No plots found for collection: {collection}")
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Missing plot module: {path}")
    return paths


def render_all(output_dir: Path, dpi: int, collection: str = "main") -> int:
    if dpi <= 0:
        raise ValueError("DPI must be positive")
    paths = plot_paths(collection)
    for path in paths:
        module = load_module(path)
        figure = module.render(module.prepare_data(), module.PLOT_SETTINGS)
        try:
            destination = output_dir / path.parent.relative_to(ROOT).with_suffix(".png")
            destination.parent.mkdir(parents=True, exist_ok=True)
            figure.savefig(destination, dpi=dpi, bbox_inches="tight")
        finally:
            plt.close(figure)
        print(destination.relative_to(ROOT) if destination.is_relative_to(ROOT) else destination)
    return len(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "rendered")
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--collection", choices=COLLECTIONS, default="main",
                        help="Figure set to render (default: main, the current 14 modules)")
    parser.add_argument("--list", action="store_true", help="List selected modules without rendering")
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("--dpi must be positive")
    if args.list:
        for path in plot_paths(args.collection):
            print(path.relative_to(ROOT))
        return
    count = render_all(args.output_dir.resolve(), args.dpi, args.collection)
    print(f"Rendered {count} plots ({args.collection}).")


if __name__ == "__main__":
    main()
