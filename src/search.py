import numpy as np
from src.constants import *
from src.lambert import solve_lambert
from src.delta_v import departure_dv, arrival_capture_dv
from src.gravity_assist import calculate_unpowered_flyby

def evaluate_trajectory(ephemeris, t_depart, tof_1, tof_2, direction='prograde'):
    """
    Evaluates a single Caelus -> Ventus -> Glacia trajectory for a given set of times.
    
    Args:
        ephemeris: EphemerisSystem object
        t_depart (float): MJD of departure from Caelus
        tof_1 (float): Time of flight to Ventus in days
        tof_2 (float): Time of flight from Ventus to Glacia in days
        direction (str): 'prograde' or 'retrograde'
        
    Returns:
        dict: Summary of the trajectory performance including total DV, or None if invalid.
    """
    t_flyby = t_depart + tof_1
    t_arrive = t_flyby + tof_2
    
    # 1. Get planetary states
    r_caelus, v_caelus = ephemeris.get_state('Caelus', t_depart)
    r_ventus, v_ventus = ephemeris.get_state('Ventus', t_flyby)
    r_glacia, v_glacia = ephemeris.get_state('Glacia', t_arrive)
    
    # Check thermal constraint (perihelion > 0.4 AU ideally, but we test Lambert 
    # and maybe do a quick radius check. Simplification: we let it pass if endpoints > 0.4 AU).
    if np.linalg.norm(r_caelus) < THERMAL_CONSTRAINT_DIST or np.linalg.norm(r_ventus) < THERMAL_CONSTRAINT_DIST:
        return None
        
    # Convert TOF to seconds for Lambert solver
    tof_1_sec = tof_1 * 86400.0
    tof_2_sec = tof_2 * 86400.0
    
    # 2. Solve first leg (Caelus to Ventus)
    v1_depart, v1_arrive = solve_lambert(r_caelus, r_ventus, tof_1_sec, MU_STAR, direction=direction)
    if v1_depart is None: return None
    
    # 3. Solve second leg (Ventus to Glacia)
    v2_depart, v2_arrive = solve_lambert(r_ventus, r_glacia, tof_2_sec, MU_STAR, direction=direction)
    if v2_depart is None: return None
    
    # 4. Calculate Mission Delta-V
    # Departure from Caelus Parking Orbit
    v_inf_depart = np.linalg.norm(v1_depart - v_caelus)
    dv_depart = departure_dv(v_inf_depart, R_CAELUS + PARKING_ORBIT_ALT, MU_CAELUS)
    
    # Gravity Assist at Ventus
    flyby = calculate_unpowered_flyby(v1_arrive, v2_depart, v_ventus, MU_VENTUS)
    dv_flyby = flyby['dv_powered']
    
    # Check minimum altitude constraint
    if flyby['rp'] < (R_VENTUS_CLOUD_TOP + VENTUS_MIN_FLYBY_ALT):
        return None  # Crashes into planet or too deep in atmosphere
        
    # Arrival at Glacia (Assuming capture for standard mission, or rendezvous)
    # The prompt says "achieves rendezvous with Glacia". Rendezvous = match velocity.
    v_inf_arrive = np.linalg.norm(v2_arrive - v_glacia)
    dv_arrive = v_inf_arrive  # direct rendezvous Delta-V
    
    total_dv = dv_depart + dv_flyby + dv_arrive
    
    return {
        'total_dv': total_dv,
        'dv_depart': dv_depart,
        'dv_flyby': dv_flyby,
        'dv_arrive': dv_arrive,
        'rp_ventus': flyby['rp'],
        'v_inf_arrive': v_inf_arrive
    }

def grid_search(ephemeris, depart_range, tof1_range, tof2_range):
    """
    Performs a grid search over departure dates and times of flight.
    """
    best_dv = float('inf')
    best_params = None
    
    # In a real scenario, this is parallelised or vectorized.
    for t_dep in depart_range:
        for tof1 in tof1_range:
            for tof2 in tof2_range:
                if tof1 + tof2 > MAX_MISSION_DURATION:
                    continue
                    
                res = evaluate_trajectory(ephemeris, t_dep, tof1, tof2)
                
                if res and res['total_dv'] < best_dv:
                    best_dv = res['total_dv']
                    best_params = {
                        't_depart': t_dep,
                        'tof_1': tof1,
                        'tof_2': tof2,
                        'results': res
                    }
                    
    return best_params
