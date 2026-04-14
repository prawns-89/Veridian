# Mission Veridian — Code Walkthrough

**Gravity-Assist Trajectory Design in a Fictional Exoplanetary System**
*Flight and Space Mechanics · VJTI Mumbai · R5ME2206T*

---

## Table of Contents

1. [What the codebase does](#1-what-the-codebase-does)
2. [Repository layout](#2-repository-layout)
3. [How to run it](#3-how-to-run-it)
4. [Module-by-module breakdown](#4-module-by-module-breakdown)
   - [src/constants.py](#srcconstandspy)
   - [src/ephemeris.py](#srcephemerspy)
   - [src/lambert.py](#srclambertpy)
   - [src/gravity_assist.py](#srcgravity_assistpy)
   - [src/delta_v.py](#srcdelta_vpy)
   - [src/search.py](#srcsearchpy)
5. [Entry-point scripts](#5-entry-point-scripts)
   - [main.py](#mainpy)
   - [find_any_trajectory.py](#find_any_trajectorypy)
   - [animate_simulation.py](#animate_simulationpy)
   - [plot_results.py](#plot_resultspy)
   - [build_notebooks.py](#build_notebookspy)
6. [Jupyter notebooks](#6-jupyter-notebooks)
7. [Data flow — end to end](#7-data-flow--end-to-end)
8. [Key equations in code](#8-key-equations-in-code)
9. [Constraints enforced in code](#9-constraints-enforced-in-code)
10. [Known limitations](#10-known-limitations)

---

## 1. What the codebase does

The spacecraft starts in a **500 km circular parking orbit** around **Caelus** (the Earth-analogue planet). It must reach **Glacia** (the outer ice giant) within 8 years, using a gravity assist at **Ventus** (the gas giant) to save propellant.

The code finds the *optimal launch date and transfer times* by trying thousands of combinations, computing the required Δv for each, and keeping the cheapest valid one. The pipeline is:

```
Ephemeris CSV
     │
     ▼
EphemerisSystem          ← cubic-spline interpolation of planet positions
     │
     ▼
Lambert Solver (×2)      ← find transfer velocities between two points at a given time
     │
     ▼
Gravity Assist Model     ← check if Ventus bends the trajectory enough for free
     │
     ▼
Δv Calculator            ← departure burn + any powered flyby correction + arrival burn
     │
     ▼
Grid Search              ← repeat for every (t_depart, tof₁, tof₂) combination
     │
     ▼
optimal_trajectory.csv   ← best solution saved to disk
```

---

## 2. Repository layout

```
Veridian/
├── src/                        # Core physics library (import these)
│   ├── constants.py            # All physical constants and mission limits
│   ├── ephemeris.py            # Planet state interpolator
│   ├── lambert.py              # Lambert solver (universal variables)
│   ├── gravity_assist.py       # Flyby geometry calculator
│   ├── delta_v.py              # Δv manoeuvre formulas
│   └── search.py               # Grid search + trajectory evaluator
│
├── main.py                     # ← START HERE for the full optimisation run
├── find_any_trajectory.py      # Quick/loose coarse search (development tool)
├── animate_simulation.py       # Generates planetary orbit animation GIF
├── plot_results.py             # Writes placeholder result images
├── build_notebooks.py          # Generates the three Jupyter notebooks
│
├── notebooks/
│   ├── 01_verification.ipynb   # Lambert vs Hohmann verification
│   ├── 02_porkchop.ipynb       # Δv contour launch-window plot
│   └── 03_optimal_trajectory.ipynb  # Visualise the best trajectory
│
├── data/
│   ├── veridian_ephemeris.csv  # 731-row planet state table (5-day steps)
│   └── optimal_trajectory.csv  # Output: best trajectory parameters
│
└── results/                    # Output images / animation
```

---

## 3. How to run it

```bash
# 1. Install dependencies
pip install -r requirements.txt   # numpy, scipy, matplotlib, pandas

# 2. Run the full grid search (this is the main computation — takes several minutes)
python main.py
# → writes data/optimal_trajectory.csv

# 3. View results in notebooks
python build_notebooks.py         # generates the .ipynb files
jupyter notebook notebooks/

# 4. Generate the planetary animation
python animate_simulation.py
# → writes results/planetary_simulation.gif

# 5. Quick sanity-check search (loose, fast, no flyby physics)
python find_any_trajectory.py
```

---

## 4. Module-by-module breakdown

---

### `src/constants.py`

A flat file of named numbers — no functions, no classes. Every other module imports from here so the values are never duplicated.

| Constant | Value | Meaning |
|---|---|---|
| `MU_STAR` | 1.393 × 10¹¹ km³/s² | Veridian star gravitational parameter |
| `MU_CAELUS` | 3.986 × 10⁵ km³/s² | Same order of magnitude as Earth's µ |
| `MU_VENTUS` | 1.266 × 10⁸ km³/s² | Jupiter-class planet |
| `MU_GLACIA` | 1.267 × 10⁷ km³/s² | Super-Neptune |
| `MAX_DV_BUDGET` | 1.5 km/s | Hard propellant limit |
| `MAX_MISSION_DURATION` | 2922 days | 8 Earth years |
| `VENTUS_MIN_FLYBY_ALT` | 2000 km | Must not fly lower than this |
| `THERMAL_CONSTRAINT_DIST` | 0.4 AU in km | Must not go this close to the star |

**Why this matters:** The grid search uses `MAX_MISSION_DURATION` to skip combinations early before even calling Lambert (a cheap pre-filter), and `VENTUS_MIN_FLYBY_ALT` to reject trajectories that would skim too deep into Ventus's atmosphere.

---

### `src/ephemeris.py`

**Class: `EphemerisSystem`**

Loads the CSV once on construction, fits a **cubic spline** independently for each planet, then answers queries like "where is Ventus on MJD 60450?" in microseconds.

```python
ephemeris = EphemerisSystem("data/veridian_ephemeris.csv")
r, v = ephemeris.get_state('Ventus', 60450.0)
# r → [x, y, z] in km
# v → [vx, vy, vz] in km/s
```

**Why cubic splines?** The ephemeris file has one row every 5 days. The grid search queries planets at arbitrary MJD values (e.g. MJD 60437.5). Linear interpolation of orbital positions is inaccurate because orbits curve. Cubic splines pass exactly through the tabulated points and give smooth derivatives — a much better fit to Keplerian motion.

**Implementation detail:** Position and velocity columns are splined *independently*. An alternative would be to spline only positions and take the analytical derivative of the spline for velocity, but splined velocities at the table points are exact, making them reliable at the nodes.

---

### `src/lambert.py`

**Function: `solve_lambert(r1, r2, tof, mu, direction='prograde')`**

Given two position vectors and a travel time, find the velocities at each end. This is the core numerical workhorse of the entire pipeline.

**Returns:** `(v1, v2)` — velocity at `r1` and velocity at `r2`, or `(None, None)` if no solution found.

#### Algorithm — Universal Variable formulation

The key insight is to express the orbit as a function of a single variable `z = α · x²` where `x` is a "universal anomaly." The same equations then handle elliptic, parabolic, and hyperbolic trajectories without branching.

**Step 1 — Determine transfer angle**

```python
cos_dnu = dot(r1, r2) / (|r1| * |r2|)
dnu = arccos(cos_dnu)
# If prograde and cross product z-component < 0, the long way round is needed:
if cross(r1, r2)[2] < 0:
    dnu = 2π - dnu
```

**Step 2 — Compute the `A` parameter**

```
A = sin(Δν) * sqrt(|r1| * |r2| / (1 - cos(Δν)))
```

`A` is always positive for a prograde transfer. If `A = 0` the transfer angle is exactly 180° and the problem is geometrically degenerate (undefined transfer plane).

**Step 3 — Root-find for `z`** using the Stumpff functions `C(z)` and `S(z)`:

```
C(z) = (1 - cos√z) / z          for z > 0  (ellipse)
S(z) = (√z - sin√z) / (√z)³     for z > 0
```

The time-of-flight equation in `z` is:

```
t(z) = [x³ · S(z) + A · √y] / √µ
```

where `y = |r1| + |r2| + A · (z·S - 1) / √C`. The code solves `t(z) = tof` using `scipy.optimize.root_scalar` with the Brent method on the bracket `[-100, 4π²]`. If that bracket fails (unusual geometries), it falls back to the secant method.

**Step 4 — Recover velocities via Lagrange coefficients**

```python
f      = 1 - y / |r1|
g      = A * sqrt(y / µ)
g_dot  = 1 - y / |r2|

v1 = (r2 - f * r1) / g
v2 = (g_dot * r2 - r1) / g
```

---

### `src/gravity_assist.py`

**Function: `calculate_unpowered_flyby(v_in_heliocentric, v_out_heliocentric, v_planet, mu_planet)`**

Takes the *heliocentric* spacecraft velocities arriving and departing Ventus (computed by two Lambert solves), subtracts the planet velocity to get planet-centred excess velocities, and checks whether an unpowered flyby can physically connect them.

```
v∞_in  = v_in_heliocentric  - v_planet
v∞_out = v_out_heliocentric - v_planet
```

**Turning angle** between the two excess velocity vectors:

```
δ = arccos( v∞_in · v∞_out / (|v∞_in| * |v∞_out|) )
```

**Required periapsis radius** for the implied hyperbola:

```
e  = 1 / sin(δ/2)
rp = (µ_planet / v∞_avg²) * (e - 1)
```

**`dv_powered`** is `|v∞_out| - |v∞_in|`. For a *purely* unpowered flyby these must be equal. Any difference means a propulsive manoeuvre is needed at periapsis — the code includes this in the total Δv budget.

**Key output:**

| Key | Meaning |
|---|---|
| `rp` | Required periapsis radius (km). Compared against `R_VENTUS + 2000 km` limit. |
| `dv_powered` | Extra Δv needed if the flyby is partially powered. |
| `delta` | The turning angle in radians. |

---

### `src/delta_v.py`

Three small formulas. All use the vis-viva equation from the patched-conic approximation.

**`departure_dv(v_inf_mag, r_park, mu_planet)`**

Burn at periapsis of escape hyperbola to leave circular parking orbit:

```
v_park     = sqrt(µ / r_park)
v_periapsis = sqrt(v∞² + 2µ / r_park)
ΔV_dep     = v_periapsis - v_park
```

**`arrival_capture_dv(v_inf_mag, r_park, mu_planet)`**

Same formula, used in reverse (braking into orbit). Not used in the main trajectory evaluator — see `rendezvous_dv` below.

**`rendezvous_dv(v_inf_mag)`**

Returns `v_inf_mag` directly. The assignment requires *rendezvous* with Glacia (matching its velocity), not just capture. The Δv cost of zeroing out the excess velocity is equal to `v∞` itself.

---

### `src/search.py`

Two functions that together form the optimisation loop.

---

#### `evaluate_trajectory(ephemeris, t_depart, tof_1, tof_2, direction='prograde')`

Evaluates *one* (t_depart, tof₁, tof₂) triple. Returns a dict with Δv breakdown or `None` if any constraint is violated.

**Step-by-step inside the function:**

1. **Thermal check** — if Caelus or Ventus positions are inside 0.4 AU from the star, reject immediately (early exit, no Lambert call needed).

2. **Leg 1 Lambert** — `solve_lambert(r_caelus, r_ventus, tof₁·86400, MU_STAR)` → departure velocity `v1_depart`, Ventus-arrival velocity `v1_arrive`.

3. **Leg 2 Lambert** — `solve_lambert(r_ventus, r_glacia, tof₂·86400, MU_STAR)` → Ventus-departure velocity `v2_depart`, Glacia-arrival velocity `v2_arrive`.

4. **Departure Δv** — uses `departure_dv` with the excess speed relative to Caelus.

5. **Flyby geometry** — calls `calculate_unpowered_flyby` with the two Lambert velocities at Ventus. If `rp < R_VENTUS + 2000 km`, the trajectory is rejected.

6. **Arrival Δv** — `|v2_arrive - v_glacia|` (rendezvous cost).

7. **Total Δv** = departure + powered-flyby correction + arrival.

---

#### `grid_search(ephemeris, depart_range, tof1_range, tof2_range)`

Three nested `for` loops over all parameter combinations. Applies one pre-filter:

```python
if tof1 + tof2 > MAX_MISSION_DURATION:
    continue   # skip before calling evaluate_trajectory
```

Tracks the `best_dv` seen so far. Returns the full parameter dict for the minimum-Δv solution.

**Search space size from `main.py`:**
- Departure: MJD 60000–61095 in steps of 10 → **110 values**
- TOF₁: 200–800 days in steps of 10 → **61 values**
- TOF₂: 200–800 days in steps of 10 → **61 values**
- **Total: 110 × 61 × 61 = 409,190 combinations**

---

## 5. Entry-point scripts

### `main.py`

The primary script for the full optimisation run. It:

1. Loads the ephemeris
2. Builds the three parameter grids as `np.arange` arrays
3. Calls `grid_search(...)` 
4. Prints the best result to the terminal
5. Saves it to `data/optimal_trajectory.csv` in the format required by the assignment:

```
departure_mjd, tof_ventus, altitude, tof_glacia, deltaV_total
```

Note: `altitude = rp_ventus - R_VENTUS_CLOUD_TOP`, converting periapsis radius back to altitude above the cloud tops.

---

### `find_any_trajectory.py`

A fast, constraint-loose development script. Useful for sanity-checking the Lambert solver before running the full search. Key differences from `main.py`:

- **No gravity assist model** — just sums raw velocity mismatches at Ventus
- **No altitude/thermal constraints**
- **Coarser grid** (10 departure dates, 10 TOF₁, 10 TOF₂)
- Uses `itertools.product` instead of nested for-loops (functionally identical, slightly more Pythonic)

Run this first when debugging to confirm that Lambert is returning physically reasonable velocities.

---

### `animate_simulation.py`

Produces a 200-frame GIF of planet positions over 2000 days using `matplotlib.animation.FuncAnimation`. The animation shows:

- ☀ Veridian star at the origin (fixed yellow dot)
- 🔵 Caelus (blue)
- 🟠 Ventus (orange)
- 🟣 Glacia (purple)
- Dashed orbital trails drawn once at startup (static)
- Planet dots updated each frame via `ephemeris.get_state()`

Output: `results/planetary_simulation.gif`

---

### `plot_results.py`

Creates three **placeholder** PNG files in `results/` with text labels but no actual data. These act as stubs that the notebooks will overwrite with real plots once `main.py` has been run.

---

### `build_notebooks.py`

Programmatically generates the three `.ipynb` files by writing JSON directly (no `nbformat` dependency needed). Run once before opening Jupyter:

```bash
python build_notebooks.py
jupyter notebook notebooks/
```

---

## 6. Jupyter notebooks

| Notebook | Purpose |
|---|---|
| `01_verification.ipynb` | Verify Lambert solver against the analytical Hohmann transfer from Caelus to Ventus. If the magnitudes match within ~1 m/s, the solver is correct. |
| `02_porkchop.ipynb` | Build a 2-D Δv grid over departure date vs. TOF₁ and plot it as a contour map ("pork-chop plot"). Valleys in this plot are good launch windows. |
| `03_optimal_trajectory.ipynb` | Load `optimal_trajectory.csv`, reconstruct the trajectory, and plot the heliocentric path with planet positions at each event. |

---

## 7. Data flow — end to end

```
veridian_ephemeris.csv
        │
        │ pandas.read_csv + CubicSpline fit
        ▼
  EphemerisSystem
        │
        │ .get_state('Caelus',  t_dep)    → r_C, v_C
        │ .get_state('Ventus',  t_dep+t1) → r_V, v_V
        │ .get_state('Glacia',  t_dep+t1+t2) → r_G, v_G
        │
        ▼
  solve_lambert(r_C, r_V, t1*86400, MU_STAR)
        │
        │ → v1_dep (heliocentric, at Caelus)
        │ → v1_arr (heliocentric, at Ventus arrival)
        │
  solve_lambert(r_V, r_G, t2*86400, MU_STAR)
        │
        │ → v2_dep (heliocentric, at Ventus departure)
        │ → v2_arr (heliocentric, at Glacia)
        │
        ▼
  calculate_unpowered_flyby(v1_arr, v2_dep, v_V, MU_VENTUS)
        │
        │ → dv_powered  (0 if perfect unpowered slingshot)
        │ → rp          (must be > 67,000 km)
        │
        ▼
  departure_dv(|v1_dep - v_C|, R_C+500, MU_CAELUS)  → dv_dep
  rendezvous_dv(|v2_arr - v_G|)                      → dv_arr
        │
        ▼
  total_dv = dv_dep + dv_powered + dv_arr
        │
        ▼  (inside grid_search, 409,190 times)
  keep if total_dv < best seen so far
        │
        ▼
  data/optimal_trajectory.csv
```

---

## 8. Key equations in code

| Physics concept | Where in code | Equation |
|---|---|---|
| Cubic spline interpolation | `ephemeris.py` — `CubicSpline` | Smooth polynomial fit through 5-day ephemeris table |
| Stumpff C function | `lambert.py` — `c_func(z)` | `(1 - cos√z) / z` for z > 0 |
| Stumpff S function | `lambert.py` — `s_func(z)` | `(√z - sin√z) / (√z)³` for z > 0 |
| Lagrange f, g coefficients | `lambert.py` — end of `solve_lambert` | `v1 = (r2 - f·r1) / g` |
| Gravity assist turning angle | `gravity_assist.py` | `δ = arccos(v∞_in · v∞_out / (‖v∞_in‖ · ‖v∞_out‖))` |
| Required periapsis for turn | `gravity_assist.py` | `rp = (µ / v∞²) · (e - 1)`, where `e = 1/sin(δ/2)` |
| Departure burn | `delta_v.py — departure_dv` | `ΔV = √(v∞² + 2µ/r) - √(µ/r)` |
| Rendezvous burn | `delta_v.py — rendezvous_dv` | `ΔV = ‖v_sc - v_planet‖` |

---

## 9. Constraints enforced in code

| Constraint | Location | How enforced |
|---|---|---|
| Max mission duration ≤ 2922 days | `search.py — grid_search` | `if tof1 + tof2 > MAX_MISSION_DURATION: continue` |
| Ventus min flyby altitude ≥ 2000 km | `search.py — evaluate_trajectory` | `if flyby['rp'] < R_VENTUS + 2000: return None` |
| Thermal constraint ≥ 0.4 AU | `search.py — evaluate_trajectory` | `if |r_caelus| < THERMAL_DIST: return None` |
| Lambert solver convergence | `lambert.py — solve_lambert` | Returns `None, None` on failure; `evaluate_trajectory` catches this |

---

## 10. Known limitations

**The grid search doesn't include flyby altitude as a free variable.** The problem statement asks you to sweep altitude from 2000–20000 km, but `search.py` treats the flyby as purely determined by the two Lambert legs — the altitude is a *result*, not an input. To implement an altitude sweep you would need to rotate `v∞_out` explicitly at different `rp` values (using the analytic formula) rather than reading it from the second Lambert arc.

**`find_any_trajectory.py` ignores flyby physics** — it uses raw velocity mismatches as a proxy for Δv. It will find low-cost windows, but those windows need verification through `evaluate_trajectory` before trusting the numbers.

**No multi-revolution Lambert solutions.** The bracket `[-100, 4π²]` in `lambert.py` covers only zero-revolution (direct) transfers. Very long time-of-flights on short arcs may need multi-rev solutions, which require a different parameterisation.

**Single-threaded grid search.** The three nested loops in `grid_search` run entirely on one CPU core. For the ~400k combinations this is acceptable (a few minutes on a modern machine), but parallelising with `multiprocessing` or `numpy` broadcasting would speed it up significantly.

---

*Generated for Mission Veridian — VJTI Mumbai, Semester IV AY 2025-26*
