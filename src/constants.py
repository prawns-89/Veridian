# src/constants.py

# ==========================================
# VERIDIAN SYSTEM CONSTANTS (From Veridian.pdf)
# ==========================================

MU_STAR = 1.393e11  # km^3/s^2 (Veridian)
AU = 1.496e8  # km

# Planetary properties
MU_CAELUS = 3.986e5  # km^3/s^2
R_CAELUS = 7200.0  # km

MU_VENTUS = 1.266e8  # km^3/s^2
R_VENTUS_CLOUD_TOP = 65000.0  # km

MU_GLACIA = 1.267e7  # km^3/s^2
R_GLACIA = 30000.0  # km

# ==========================================
# MISSION PARAMETERS
# ==========================================
M_INITIAL = 2500.0  # kg
I_SP = 300.0  # seconds
G0 = 0.00980665  # km/s^2

MAX_DV_BUDGET = 1.5  # km/s
MAX_MISSION_DURATION = 2922.0  # days
THERMAL_CONSTRAINT_DIST = 0.4 * AU  # km

PARKING_ORBIT_ALT = 500.0  # km
VENTUS_MIN_FLYBY_ALT = 2000.0  # km
VENTUS_MAX_FLYBY_ALT = 20000.0  # km
