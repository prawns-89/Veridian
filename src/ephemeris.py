import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

class EphemerisSystem:
    """
    Loads orbital data from veridian_ephemeris.csv and provides continuous
    position and velocity vectors for the planets using cubic spline interpolation.
    """
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.mjd = self.df['MJD'].values
        
        # We will interpolate Caelus, Ventus, Glacia
        # Aether is also available if needed
        self.bodies = ['Caelus', 'Ventus', 'Glacia', 'Aether']
        self.splines = {}
        
        for body in self.bodies:
            x = self.df[f'{body}_x'].values
            y = self.df[f'{body}_y'].values
            z = self.df[f'{body}_z'].values
            
            vx = self.df[f'{body}_vx'].values
            vy = self.df[f'{body}_vy'].values
            vz = self.df[f'{body}_vz'].values
            
            # Fit position and velocity individually. 
            # Note: We could derive velocity from position spline derivative, 
            # but interpolating both ensures exact matching at the ephemeris points.
            pos_spline = CubicSpline(self.mjd, np.column_stack((x, y, z)))
            vel_spline = CubicSpline(self.mjd, np.column_stack((vx, vy, vz)))
            
            self.splines[body] = {'r': pos_spline, 'v': vel_spline}
            
    def get_state(self, body_name, t_mjd):
        """
        Get the position and velocity vectors of a body at a specific Modified Julian Date.
        Returns:
            r (np.array): [x, y, z] in km
            v (np.array): [vx, vy, vz] in km/s
        """
        if body_name not in self.splines:
            raise ValueError(f"Body {body_name} not found in ephemeris.")
            
        r = self.splines[body_name]['r'](t_mjd)
        v = self.splines[body_name]['v'](t_mjd)
        return r, v
        
    def get_min_max_dates(self):
        return self.mjd[0], self.mjd[-1]
