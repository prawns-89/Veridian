# Mission Veridian: Gravity-Assist Trajectory Design

**Course:** Flight and Space Mechanics (R5ME2206T)  
**Institute:** VJTI Mumbai — Second-Year Aerospace Engineering MDM, Semester IV (2025-26)

---

## Overview

This repository implements a full gravity-assist trajectory design pipeline for the fictional Veridian exoplanetary system. The mission departs from **Caelus** (Earth-analogue), performs a gravity-assist flyby at **Ventus** (gas giant), and achieves rendezvous with **Glacia** (ice giant destination).

The pipeline uses the **patched-conic approximation** and solves **Lambert's problem** (universal variable formulation) to search over thousands of launch windows and identify the optimal trajectory.

---

## Repository Structure

```
Veridian/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py                        # Entry point — runs the full pipeline
│
├── src/
│   ├── __init__.py
│   ├── constants.py               # All physical constants & system parameters
│   ├── ephemeris.py               # Ephemeris loader & Keplerian propagator
│   ├── lambert.py                 # Lambert solver (universal variable method)
│   ├── gravity_assist.py          # Gravity-assist flyby model
│   ├── delta_v.py                 # ΔV calculations (departure, arrival, DSM)
│   └── search.py                  # Launch window search & optimisation
│
├── data/
│   ├── veridian_ephemeris.csv     # Provided heliocentric ephemeris (MJD 60000–63650)
│   └── optimal_trajectory.csv    # Output: best trajectory parameters
│
├── notebooks/
│   ├── 01_verification.ipynb      # Lambert solver verification (Hohmann test case)
│   ├── 02_porkchop.ipynb          # Pork-chop plot & launch window analysis
│   └── 03_optimal_trajectory.ipynb# Final trajectory visualisation & report figures
│
├── results/
│   ├── porkchop_plot.png          # ΔV vs departure date & TOF to Ventus
│   ├── heliocentric_trajectory.png# Optimal heliocentric path
│   └── velocity_diagram_ventus.png# Velocity vectors at the Ventus flyby
│
└── report/
    └── mission_report.pdf         # Final 5-page mission report
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place the ephemeris file

Copy `veridian_ephemeris.csv` into the `data/` directory.

### 3. Run the full pipeline

```bash
python main.py
```

This will:
- Load the ephemeris
- Verify the Lambert solver against the Hohmann test case
- Run the coarse + fine launch window search
- Save the optimal trajectory to `data/optimal_trajectory.csv`
- Generate all plots in `results/`

### 4. Explore interactively

Open the notebooks in order:
```bash
jupyter notebook notebooks/
```

---

## Mission Parameters

| Parameter | Value |
|---|---|
| Departure orbit | Circular, 500 km altitude above Caelus |
| Initial mass | 2500 kg |
| Propulsion Isp | 300 s (bipropellant chemical) |
| Max ΔV budget | 1.5 km/s |
| Max mission duration | 8 years (2922 days) |
| Ventus min flyby altitude | 2000 km above cloud tops |
| Thermal constraint | > 0.4 AU from Veridian |

---

## Deliverables Checklist

- [ ] Lambert solver with Hohmann verification
- [ ] Gravity-assist model (`gravity_assist.py`)
- [ ] Launch window search (pork-chop plot)
- [ ] Optimal trajectory parameters saved to `data/optimal_trajectory.csv`
- [ ] Three result plots in `results/`
- [ ] 5-page mission report in `report/`

---

## References

1. GTOC 13 Problem Statement — NASA JPL, 2025
2. Lantukh, D.V. — *Preliminary design of spacecraft trajectories*, UT Austin, 2015
3. Spacecraft Orbital Mechanics (SESA6076) — University of Southampton, 2026