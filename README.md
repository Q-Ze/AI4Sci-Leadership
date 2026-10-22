# AI4Sci Leadership

Reproducible, editable Matplotlib figures for a study of leadership in
AI-for-Science (AI4Sci). The figures examine how researchers from AI and domain
science backgrounds participate in AI4Sci, lead collaborations, draw on existing
knowledge, and receive citations and external recognition.

The repository contains 14 main-figure modules and 9 supplementary modules.
Each module embeds the aggregated data needed to reproduce its figure and
exposes editable visual settings through Matplot Studio.

## Figures

| Figure | Topic |
| --- | --- |
| 1b | Author-origin composition and first- and last-author shares |
| 1c | Annual active-role composition |
| 1d | Career age at first AI4Sci publication within a common observation window |
| 1e | Last-author composition by historical JCR quartile |
| 2b | Extension, Foundation, and Generalization trends in three separate panels |
| 3a | Chaperoned and independent leadership routes |
| 3b | Share of papers in the top 10% of Foundation scores by leadership route |
| 3c | Complementary-specialist shares in AI-led and domain-led teams |
| 3d | Globally normalized citation entropy |
| 4a | Citation-audience counts by historical JCR quartile |
| 4b | Raw and adjusted funding and news probabilities |
| 4c | Origin-normalized citation impact by leadership route |

Supplementary figures cover author counts, role transitions, home-subfield
reception, sensitivity analyses, entry routes, collaboration, and citation-audience
composition.

## Repository layout

```text
figures/
  project.json                 Matplot Studio project manifest
  plots/fig-<panel>-<topic>/    Main-figure modules
supplementary/                 Supplementary figure modules
docs/figure-index.md           Figure index
render_all.py                  Batch rendering entry point
requirements.txt               Python dependencies
```

Each `plot.py` provides metadata (`PLOT_META`), editable properties
(`PLOT_SCHEMA` and `PLOT_SETTINGS`), embedded-data preparation (`prepare_data()`),
and figure rendering (`render(data, settings)`). Rendering requires no database
credentials or external data files.

## Quick start

Run these commands from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python render_all.py
```

By default, the renderer generates the 14 main figures as PNG files under
`rendered/figures/plots/`.

```bash
# List main-figure modules
python render_all.py --list

# Render supplementary figures
python render_all.py --collection supplementary

# Render all 23 modules at publication resolution
python render_all.py --collection all --output-dir output --dpi 300
```

## Render a single figure

```python
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import matplotlib.pyplot as plt

path = Path("figures/plots/fig-1-b-author-composition/plot.py")
spec = spec_from_file_location("ai4sci_plot", path)
module = module_from_spec(spec)
spec.loader.exec_module(module)

figure = module.render(module.prepare_data(), module.PLOT_SETTINGS)
figure.savefig("figure.png", dpi=300, bbox_inches="tight")
plt.close(figure)
```

## Edit in Matplot Studio

Import the `figures/` directory as a
[Matplot Studio](https://github.com/Q-Ze/matplot-studio) project to edit the main
figures through their visual properties and Python source. The project manifest
specifies the panel order and maps each panel to its plotting module.

## Dependencies and output

- Plotting uses Matplotlib, NumPy, and pandas. Supplementary Figure S2 also uses
  SciPy for density estimation.
- Figures use Arial by default; Matplotlib substitutes an available font when
  Arial is unavailable.
- Generated PNG, PDF, and SVG files, caches, and virtual environments are
  excluded from Git.
