import numpy as np
import matplotlib.pyplot as plt

# Generate dummy images for the expected results just in case 
# the user wants to run them or we provide placeholder outputs.
import os
os.makedirs('results', exist_ok=True)

fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'Porkchop Plot\n(Delta-V Contours)', ha='center', va='center')
ax.axis('off')
plt.savefig('results/porkchop_plot.png')
plt.close()

fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'Heliocentric Trajectory\n(Caelus -> Ventus -> Glacia)', ha='center', va='center')
ax.axis('off')
plt.savefig('results/heliocentric_trajectory.png')
plt.close()

fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'Velocity Vector Diagram\nVentus Flyby', ha='center', va='center')
ax.axis('off')
plt.savefig('results/velocity_diagram_ventus.png')
plt.close()

print("Generated dummy plots in results/")
