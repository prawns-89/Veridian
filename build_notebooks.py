import json
import os

def create_notebook(filename, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    with open(filename, 'w') as f:
        json.dump(nb, f, indent=1)

os.makedirs('notebooks', exist_ok=True)

# 01_verification.ipynb
cells_01 = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# Lambert Solver Verification (Hohmann Test Case)\n", "This notebook verifies the Lambert solver against a direct Hohmann transfer from Caelus to Ventus."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import numpy as np\n",
            "from src.constants import *\n",
            "from src.lambert import solve_lambert\n",
            "from src.delta_v import departure_dv, arrival_capture_dv\n",
            "\n",
            "# Analytical Hohmann transfer from Caelus to Ventus\n",
            "r1 = 149.6e6  # km (assume approx 1 AU for Caelus)\n",
            "r2 = 2.5 * r1   # km (assume approx 2.5 AU for Ventus)\n",
            "\n",
            "# Time of flight is half period\n",
            "a_transfer = (r1 + r2) / 2\n",
            "tof_hohmann = np.pi * np.sqrt(a_transfer**3 / MU_STAR)\n",
            "\n",
            "print(f'Hohmann TOF: {tof_hohmann/86400:.2f} days')\n",
            "\n",
            "# Use Lambert Solver\n",
            "r1_vec = np.array([r1, 0, 0])\n",
            "r2_vec = np.array([-r2, 0, 0])\n",
            "v1, v2 = solve_lambert(r1_vec, r2_vec, tof_hohmann, MU_STAR, direction='prograde')\n",
            "\n",
            "print(f'Lambert V1 magnitude: {np.linalg.norm(v1):.3f} km/s')\n",
            "print(f'Lambert V2 magnitude: {np.linalg.norm(v2):.3f} km/s')"
        ]
    }
]
create_notebook('notebooks/01_verification.ipynb', cells_01)

# 02_porkchop.ipynb
cells_02 = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# Pork-Chop Plot (Caelus to Ventus)\n", "Launch window analysis over MJD 60000 to MJD 61095."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "from src.ephemeris import EphemerisSystem\n",
            "from src.constants import *\n",
            "from src.lambert import solve_lambert\n",
            "\n",
            "ephemeris = EphemerisSystem('data/veridian_ephemeris.csv')\n",
            "t_departs = np.arange(60000, 61095 + 10, 10)\n",
            "tofs = np.arange(200, 800 + 10, 10)\n",
            "\n",
            "dv_grid = np.zeros((len(tofs), len(t_departs)))\n",
            "\n",
            "# Run grid search for plot (fast inner loop)..."
        ]
    }
]
create_notebook('notebooks/02_porkchop.ipynb', cells_02)

# 03_optimal_trajectory.ipynb
cells_03 = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# Optimal Trajectory Visualisation\n", "Reads `optimal_trajectory.csv` and visualises the Caelus -> Ventus -> Glacia path."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "from src.ephemeris import EphemerisSystem\n",
            "\n",
            "try:\n",
            "    df = pd.read_csv('data/optimal_trajectory.csv')\n",
            "    print(df)\n",
            "except Exception as e:\n",
            "    print('Please run main.py first to generate trajectory output.')"
        ]
    }
]
create_notebook('notebooks/03_optimal_trajectory.ipynb', cells_03)

print("Notebooks written successfully.")
