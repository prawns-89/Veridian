import numpy as np
from src.constants import MU_STAR
from src.ephemeris import EphemerisSystem
from src.lambert import solve_lambert
import itertools

ephemeris = EphemerisSystem("data/veridian_ephemeris.csv")
mjd_start, mjd_end = ephemeris.get_min_max_dates()

best_dv = float('inf')
best_times = None

t_departs = np.linspace(mjd_start, mjd_start + 1000, 10)
tof1s = np.linspace(150, 400, 10)
tof2s = np.linspace(300, 800, 10)

for t, t1, t2 in itertools.product(t_departs, tof1s, tof2s):
    rc, vc = ephemeris.get_state('Caelus', t)
    rv, vv = ephemeris.get_state('Ventus', t + t1)
    rg, vg = ephemeris.get_state('Glacia', t + t1 + t2)
    
    v1_dep, v1_arr = solve_lambert(rc, rv, t1 * 86400, MU_STAR)
    if v1_dep is None: continue
        
    v2_dep, v2_arr = solve_lambert(rv, rg, t2 * 86400, MU_STAR)
    if v2_dep is None: continue
    
    # Just sum magnitude differences (very loose DV estimate)
    dv = np.linalg.norm(v1_dep - vc) + np.abs(np.linalg.norm(v2_dep - vv) - np.linalg.norm(v1_arr - vv)) + np.linalg.norm(v2_arr - vg)
    
    if dv < best_dv:
        best_dv = dv
        best_times = (t, t1, t2)

print(f"Best unconstrained DV: {best_dv}")
print(f"Times: t_depart={best_times[0]}, tof1={best_times[1]}, tof2={best_times[2]}")
