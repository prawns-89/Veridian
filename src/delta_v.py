import numpy as np
from src.constants import *

def departure_dv(v_inf_mag, r_park, mu_planet):
    """
    Calculates the required Delta-V to depart from a circular parking orbit.
    Uses the patched-conic approximation (vis-viva equation).
    """
    # Velocity in circular parking orbit
    v_park = np.sqrt(mu_planet / r_park)
    # Velocity required at periapsis of the escape hyperbola
    v_periapsis = np.sqrt(v_inf_mag**2 + 2 * mu_planet / r_park)
    
    return v_periapsis - v_park

def rendezvous_dv(v_inf_mag):
    """
    If the mission ends with a rendezvous (matching heliocentric velocity),
    the delta-V is simply the magnitude of the arrival v_inf.
    """
    return v_inf_mag

def arrival_capture_dv(v_inf_mag, r_park, mu_planet):
    """
    Calculates the required Delta-V to insert into a circular parking orbit.
    """
    v_park = np.sqrt(mu_planet / r_park)
    v_periapsis = np.sqrt(v_inf_mag**2 + 2 * mu_planet / r_park)
    
    return v_periapsis - v_park
