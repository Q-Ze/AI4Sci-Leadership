# AI4Sci Leadership

Reproducible, editable Matplotlib figures for an AI-for-Science (AI4Sci)
leadership study. The repository contains 28 self-contained plot modules grouped
by manuscript figure.

## Repository layout

```text
figure1/   Author roles and participation
figure2/   Field engagement and citation redirection
figure3/   Career timing, collaboration routes, and diversity
figure4/   Career pivots, citation audiences, and rewards
```

Every subdirectory contains a `plot.py` module with:

- `PLOT_META`: figure metadata;
- `PLOT_SCHEMA` and `PLOT_SETTINGS`: editable visual properties;
- `prepare_data()`: reconstruction of the embedded source table;
- `render(data, settings)`: figure rendering.

The aggregated research results required by each plot are embedded in its
module, so no external data files or database credentials are needed.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python render_all.py
```

Rendered PNG files are written to `rendered/` by default. Use a different
destination or resolution if needed:

```bash
python render_all.py --output-dir output --dpi 300
```

## Rendering one module

Because directory names contain hyphens, load a module by file path:

```python
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

path = Path("figure1/area-annual-active-role-shares/plot.py")
spec = spec_from_file_location("ai4sci_plot", path)
module = module_from_spec(spec)
spec.loader.exec_module(module)

figure = module.render(module.prepare_data(), module.PLOT_SETTINGS)
figure.savefig("figure.png", dpi=300, bbox_inches="tight")
```

## Notes

- The modules default to Arial; Matplotlib will use a fallback font when Arial
  is unavailable.
- `scipy` is used by the density-based scatter plot in Figure 2.
- Generated figures and local virtual environments are intentionally ignored by
  Git.
