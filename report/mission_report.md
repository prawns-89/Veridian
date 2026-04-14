# Mission Veridian: Mission Analysis Report

## 1. Introduction
Mission Veridian is a rigorous trajectory optimization targeting a rendezvous with the exoplanet Glacia utilizing a gravity assist at the gas giant Ventus. Navigating entirely upon chemical propulsion (Isp = 300s), the maximum operational budget allocated is strictly constrained at $\Delta V = 1.5$ km/s. In this report, we trace the analytical mechanisms allowing us to find the absolute minimum mechanical work via a planetary flyby utilizing the Patched-Conic approximation framework.

## 2. Methodology
The entire pipeline relies on three main mathematical structures:

- **Ephemeris Extrapolation**: The continuous Cartesian mapping is established through a cubic spline interpolation bounding all values across the mission period seamlessly from `veridian_ephemeris.csv`.
- **Universal Variables Lambert Solver**: Utilising Bate, Mueller, and White's methodology, the universal approach eliminates trajectory singularities allowing the automated search engine to sweep bounds independent of prograde/retrograde angular states.
- **Patched Conic Flyby Limits**: Flybys occur within Ventus's Sphere of Influence. Incoming $V_{\infty,in}$ converges with outgoing $V_{\infty,out}$. We impose deep-space thrusts ($\Delta V_{dsm}$) equivalent to the magnitude deficit if Lambert geometries dictate impossible angular configurations that puncture within the $2000$ km atmospheric bound.

## 3. Results
- **Direct Hohmann Transfer**: Requires significantly more $\Delta V$ bounded primarily by radial launch penalties from Caelus to Glacia natively.
- **Gravity Assist Outcome**: By skimming $R_p \geq 67000$ km (2000 km above $R_V$), Ventus shares its angular orbital momentum seamlessly into the probe, rotating the vector by angle $\delta$ without expending propulsive energy.

## 4. Physical Interpretation
In a sun-centric view, entering the sphere of influence behind Ventus increases the spacecraft's orbital energy and angular momentum as you are accelerated through the planet's gravitational pull whilst it is moving on its orbit, acting exactly like an elastic bounce. As long as incoming magnitude perfectly traces outbound magnitude natively around the asymptote, the spacecraft performs a pure slingshot.

## 5. Verification 
As logged within `01_verification.ipynb`, the universal variables Lambert calculation executes the classical Hohmann boundary tests producing matching magnitudes accurately against $T_{Hohmann} = \pi \sqrt{a^3/\mu_{star}}$!
