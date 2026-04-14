import numpy as np
import pandas as pd
from src.constants import *
from src.ephemeris import EphemerisSystem
from src.search import grid_search

def main():
    print("Mission Veridian: Gravity-Assist Trajectory Optimization")
    
    print("Loading ephemeris...")
    try:
        ephemeris = EphemerisSystem("data/veridian_ephemeris.csv")
    except Exception as e:
        print(f"Failed to load ephemeris: {e}")
        return
        
    # Grid Search bounds (per Veridian.pdf specifications)
    t_depart_grid = np.arange(60000, 61095 + 10, 10)
    tof1_grid = np.arange(200, 800 + 10, 10)
    tof2_grid = np.arange(200, 800 + 10, 10)
    
    total_combinations = len(t_depart_grid) * len(tof1_grid) * len(tof2_grid)
    print(f"Running exact specification grid search over {total_combinations} combinations...")
    
    best_solution = grid_search(ephemeris, t_depart_grid, tof1_grid, tof2_grid)
    
    if best_solution is None:
        print("No valid trajectories found within standard unpowered 1.5 km/s constraint.")
        # Create a dummy or partial solution
        df_out = pd.DataFrame({'status': ['No trajectory found']})
        df_out.to_csv("data/optimal_trajectory.csv", index=False)
        return
        
    res = best_solution['results']
    print("\nOptimal Trajectory Found:")
    print(f"Departure Date (MJD): {best_solution['t_depart']:.1f}")
    print(f"TOF 1: {best_solution['tof_1']:.1f} days")
    print(f"TOF 2: {best_solution['tof_2']:.1f} days")
    print(f"Total DV: {res['total_dv']:.3f} km/s")
    print(f"  Departure DV: {res['dv_depart']:.3f} km/s")
    print(f"  DSM / Powered DV: {res['dv_flyby']:.3f} km/s")
    print(f"  Arrival DV: {res['dv_arrive']:.3f} km/s")
    print(f"Ventus Flyby Periapsis: {res['rp_ventus']:.1f} km")
    
    output_dict = {
        'departure_mjd': [best_solution['t_depart']],
        'tof_ventus': [best_solution['tof_1']],
        'altitude': [res['rp_ventus'] - R_VENTUS_CLOUD_TOP],  # altitude = Rp - R_planet
        'tof_glacia': [best_solution['tof_2']],
        'deltaV_total': [res['total_dv']]
    }
    df_out = pd.DataFrame(output_dict)
    df_out.to_csv("data/optimal_trajectory.csv", index=False)
    print("Saved optimal trajectory properties to data/optimal_trajectory.csv")

if __name__ == "__main__":
    main()
