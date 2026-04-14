import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from src.ephemeris import EphemerisSystem

print('Generating Planetary Evolution Animation...')
ephemeris = EphemerisSystem("data/veridian_ephemeris.csv")
mjd_start, mjd_end = ephemeris.get_min_max_dates()

fig, ax = plt.subplots(figsize=(8,8))
ax.set_facecolor('#0f0f1c')
fig.patch.set_facecolor('#0f0f1c')
ax.axis('equal')
ax.set_title("Mission Veridian: Planetary Ephemeris Simulator", color='white', fontsize=14)

# Set max plot limits (using Glacia's approx 4.2e8 km radius)
max_dist = 4.5e8  
ax.set_xlim(-max_dist, max_dist)
ax.set_ylim(-max_dist, max_dist)

# Plot central star
ax.plot(0, 0, marker='o', color='#ffcc00', markersize=12, label='Veridian Star')

# Line objects for planets
line_caelus, = ax.plot([], [], 'o', color='#3498db', markersize=6, label='Caelus')
line_ventus, = ax.plot([], [], 'o', color='#e67e22', markersize=8, label='Ventus')
line_glacia, = ax.plot([], [], 'o', color='#9b59b6', markersize=10, label='Glacia')

# Draw static orbital trails so it looks cool
trail_days = 2000
for p, c in [('Caelus', '#3498db'), ('Ventus', '#e67e22'), ('Glacia', '#9b59b6')]:
    trail = np.array([ephemeris.get_state(p, mjd_start+t)[0] for t in range(0, trail_days, 10)])
    ax.plot(trail[:,0], trail[:,1], color=c, alpha=0.3, linewidth=1, linestyle='--')

ax.tick_params(colors='gray')
ax.grid(color='gray', alpha=0.1)

legend = ax.legend(loc='upper right', facecolor='#0f0f1c', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

frames = 200
def update(frame):
    current_time = mjd_start + frame * (trail_days / frames)
    
    rc, _ = ephemeris.get_state('Caelus', current_time)
    rv, _ = ephemeris.get_state('Ventus', current_time)
    rg, _ = ephemeris.get_state('Glacia', current_time)
    
    line_caelus.set_data([rc[0]], [rc[1]])
    line_ventus.set_data([rv[0]], [rv[1]])
    line_glacia.set_data([rg[0]], [rg[1]])
    
    return line_caelus, line_ventus, line_glacia

ani = animation.FuncAnimation(fig, update, frames=frames, blit=True, interval=30)
out_path = 'results/planetary_simulation.gif'
ani.save(out_path, writer='pillow', fps=30)
print(f"Animation saved to {out_path}")
