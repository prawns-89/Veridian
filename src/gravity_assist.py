import numpy as np

def calculate_unpowered_flyby(v_in_heliocentric, v_out_heliocentric, v_planet, mu_planet):
    """
    Computes parameters for an unpowered gravity assist.
    The incoming and outgoing heliocentric velocities must be provided,
    as computed by the Lambert solver.
    
    Args:
        v_in_heliocentric (np.array): Spacecraft velocity vector arriving at the planet
        v_out_heliocentric (np.array): Spacecraft velocity vector departing the planet
        v_planet (np.array): Velocity vector of the planet
        mu_planet (float): Gravitational parameter of the planet
        
    Returns:
        dict containing:
            'is_valid': bool, whether unpowered flyby is possible (magnitudes match)
            'dv_required': float, any difference in magnitudes requiring a Deep Space Maneuver or powered flyby
            'rp': float, radius of periapsis required for the turn in km
            'delta': float, turning angle in radians
    """
    v_inf_in = v_in_heliocentric - v_planet
    v_inf_out = v_out_heliocentric - v_planet
    
    v_in_mag = np.linalg.norm(v_inf_in)
    v_out_mag = np.linalg.norm(v_inf_out)
    
    # Required delta-V if unpowered flyby is not perfectly matched
    # (A simple patched-conic assumes V_inf_in == V_inf_out for unpowered)
    dv_powered = np.abs(v_out_mag - v_in_mag)
    
    # Average the magnitude for the turn angle calculation (if slightly off)
    v_inf_avg = (v_in_mag + v_out_mag) / 2.0
    
    # Calculate required turning angle (delta)
    dot_prod = np.dot(v_inf_in, v_inf_out) / (v_in_mag * v_out_mag)
    dot_prod = np.clip(dot_prod, -1.0, 1.0)
    delta = np.arccos(dot_prod)
    
    # Required eccentricity for this turn
    e = 1.0 / np.sin(delta / 2.0)
    
    # Required periapsis radius
    rp = (mu_planet / v_inf_avg**2) * (e - 1.0)
    
    return {
        'v_inf_in': v_in_mag,
        'v_inf_out': v_out_mag,
        'dv_powered': dv_powered,
        'rp': rp,
        'delta': delta
    }
