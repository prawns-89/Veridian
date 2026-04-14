import numpy as np
from scipy.optimize import root_scalar

def c_func(z):
    """Stumpff C function"""
    if z > 0:
        # z = alpha * x^2
        return (1 - np.cos(np.sqrt(z))) / z
    elif z < 0:
        return (np.cosh(np.sqrt(-z)) - 1) / (-z)
    else:
        return 1/2.0

def s_func(z):
    """Stumpff S function"""
    if z > 0:
        sqz = np.sqrt(z)
        return (sqz - np.sin(sqz)) / (sqz**3)
    elif z < 0:
        sqz = np.sqrt(-z)
        return (np.sinh(sqz) - sqz) / (sqz**3)
    else:
        return 1/6.0

def solve_lambert(r1, r2, tof, mu, direction='prograde'):
    """
    Solves Lambert's problem using the Universal Variable formulation (Bate, Mueller, White).
    
    Args:
        r1 (np.array): Initial position vector
        r2 (np.array): Final position vector
        tof (float): Time of flight
        mu (float): Gravitational parameter
        direction (str): 'prograde' (short way if < 180 deg) or 'retrograde'
        
    Returns:
        v1 (np.array): Velocity at r1
        v2 (np.array): Velocity at r2
    """
    mag_r1 = np.linalg.norm(r1)
    mag_r2 = np.linalg.norm(r2)
    
    cross_r1_r2 = np.cross(r1, r2)
    cos_dnu = np.dot(r1, r2) / (mag_r1 * mag_r2)
    
    # Clip to avoid numerical issues
    cos_dnu = np.clip(cos_dnu, -1.0, 1.0)
    
    # Determine the transfer angle
    dnu = np.arccos(cos_dnu)
    
    if direction == 'prograde':
        if cross_r1_r2[2] < 0:
            dnu = 2 * np.pi - dnu
    elif direction == 'retrograde':
        if cross_r1_r2[2] >= 0:
            dnu = 2 * np.pi - dnu
    else:
        raise ValueError("Direction must be 'prograde' or 'retrograde'")

    A = np.sin(dnu) * np.sqrt(mag_r1 * mag_r2 / (1 - np.cos(dnu)))
    
    if A == 0:
        raise ValueError("Cannot compute a Lambert transfer with transfer angle exactly 180 degrees.")

    def tof_equation(z):
        C = c_func(z)
        S = s_func(z)
        y = mag_r1 + mag_r2 + A * (z * S - 1) / np.sqrt(C)
        if y < 0: 
            return np.nan
        x = np.sqrt(y / C)
        dt = (x**3 * S + A * np.sqrt(y)) / np.sqrt(mu)
        return dt - tof

    # Find the universal parameter z using SciPy's root_scalar
    # Bracket depends on the number of revolutions. For 0 revs, typically z is between -100 and +4*pi**2.
    try:
        sol = root_scalar(tof_equation, bracket=[-100, 4*np.pi**2], method='brentq')
        z = sol.root
    except ValueError:
        # If no root in bracket, meaning it might be multiple revolutions or failed bracket
        # Let's fallback to secant method
        try:
            sol = root_scalar(tof_equation, x0=1.0, x1=2.0, method='secant')
            z = sol.root
        except:
            return None, None # No solution found
    
    C = c_func(z)
    S = s_func(z)
    y = mag_r1 + mag_r2 + A * (z * S - 1) / np.sqrt(C)
    
    # Calculate Lagrange coefficients
    f = 1 - y / mag_r1
    g = A * np.sqrt(y / mu)
    g_dot = 1 - y / mag_r2
    
    v1 = (r2 - f * r1) / g
    v2 = (g_dot * r2 - r1) / g
    
    return v1, v2
