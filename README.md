# Mission Veridian: Gravity-Assist Trajectory

---

## Overview

This repository implements the full mathematical gravity-assist trajectory pipeline design for the Veridian system. The module calculates patched conics to navigate our theoretical spacecraft from a circular Caelus parking orbit, performing a gravity-assist flyby on Ventus, before matching relative velocities with Glacia (`M_INITIAL=2500kg`, `max_dv=1.5 km/s`).

---

## Operating Instructions

### 1. Requirements

Initialise your environment and install strict dependencies:
```bash
pip install -r requirements.txt
```

### 2. Search & Simulation (`main.py`)

To initiate the nested parameter search loops iterating through thousands of variations of Departure Times (*MJD 60000 - 61095*) and Times-of-Flight (*200 - 800 Days*) bounded by physical limits (`Ventus Flyby > 2000 km altitude`, etc.):

```bash
python main.py
```
*Outputs optimal constraints to: `data/optimal_trajectory.csv`*

### 3. Visual Simulation (`animate_simulation.py`)

To generate a full topological animation of the Caelus $\rightarrow$ Ventus $\rightarrow$ Glacia ephemeris parameters mapping standard orbital mechanic alignments directly from data points:
```bash
python animate_simulation.py
```
*Outputs compiled GIF file `results/planetary_simulation.gif`.*

### 4. Notebooks (Visualisations & Verification)

Load the Jupyter Notebook server:
```bash
jupyter notebook notebooks/
```

- **`01_verification.ipynb`**: Demonstrates precision testing of our Universal Variables `Lambert` formulation solver against analytical baseline equations.
- **`02_porkchop.ipynb`**: Parses grid search parameters into standard $\Delta V$ contour visualizations for the initial window search.
- **`03_optimal_trajectory.ipynb`**: Extracts the generated Caelus $\rightarrow$ Ventus $\rightarrow$ Glacia path for heliocentric comparisons.

### 5. Mathematical Methodology & Report

The methodological descriptions, equations, interpretation, and structural breakdown of the analysis has been compiled inside `report/mission_report.md`. Use any standard markdown-to-pdf converter (e.g. `pandoc` or `mdpdf`) to render it as a continuous PDF if required!
