import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from concurrent.futures import ProcessPoolExecutor

class ProductionSonoluminescentSuite:
   def __init__(self, a_coeff=1.4, omega=1.0, damping_alpha=0.003):
       """
       Production-grade simulation platform optimizing bifurcation sweeps
       and phase-space mapping via adaptive solvers and parallel processing.
       """
       self.a = a_coeff
       self.omega = omega
       self.alpha = damping_alpha

   def dynamical_system(self, t, state, m_coupling):
       """Governing vector field parameterized explicitly for dynamic sweeps."""
       x, y, z = state

       # 1. Cyclic Permutation Base Core (Halvorsen Backbone)
       dx_base = -self.a * x - 4 * y - 4 * z - y**2
       dy_base = -self.a * y - 4 * z - 4 * x - z**2
       dz_base = -self.a * z - 4 * x - 4 * y - x**2

       # 2. Symmetrized Anamorphic Shear Funnel
       shared_shear = m_coupling * (x * y * z) * np.sin(self.omega * t)

       # 3. Cubic Non-Linear Energy Sink (Jacobian Regulator)
       r_squared = x**2 + y**2 + z**2
       damping = -self.alpha * r_squared

       dx = dx_base + shared_shear + damping * x
       dy = dy_base + shared_shear + damping * y
       dz = dz_base + shared_shear + damping * z

       return [dx, dy, dz]

   def _evaluate_single_bifurcation_point(self, args):
       """Worker function optimized for multi-core parameter execution."""
       m_val, seed, num_periods, transient_cutoff = args
       drive_period = (2 * np.pi) / self.omega

       # Total simulation time array (sampled stroboscopically at each drive period)
       t_samples = np.arange(0, num_periods * drive_period, drive_period)

       # Integrate across the entire parameter timeline using adaptive Radau/RK45 steps
       sol = solve_ivp(
           lambda t, s: self.dynamical_system(t, s, m_val),
           [0, t_samples[-1]], seed, t_eval=t_samples,
           method='RK45', rtol=1e-7, atol=1e-9
       )

       # Discard the initial transient periods to observe the true steady-state attractor
       settled_px = sol.y[0, transient_cutoff:]
       m_vector = np.full_like(settled_px, m_val)

       return m_vector, settled_px

   def generate_parallel_bifurcation(self, seed_state, m_min=0.0, m_max=0.04, resolution=150, num_periods=400, transient_cutoff=250):
       """Sweeps coupling strength parameters simultaneously across all CPU cores."""
       m_patch = np.linspace(m_min, m_max, resolution)
       tasks = [(m, seed_state, num_periods, transient_cutoff) for m in m_patch]

       print(f"Launching parallel bifurcation engine across {resolution} points...")
       m_accumulated, x_accumulated = [], []

       with ProcessPoolExecutor() as executor:
           results = executor.map(self._evaluate_single_bifurcation_point, tasks)
           for m_res, x_res in results:
               m_accumulated.extend(m_res)
               x_accumulated.extend(x_res)

       return m_accumulated, x_accumulated

# --- Execution Entry ---
if __name__ == "__main__":
   # Instantiate the parallel suite
   suite = ProductionSonoluminescentSuite(a_coeff=1.4, omega=1.0, damping_alpha=0.003)
   initial_seed = [-1.48, -1.51, 2.04]

   # Run the high-density parameter sweep
   m_data, x_data = suite.generate_parallel_bifurcation(
       seed_state=initial_seed,
       m_min=0.0,
       m_max=0.035,
       resolution=200,       # Number of individual parameter slices
       num_periods=500,      # Long-horizon tracking per slice
       transient_cutoff=350  # Prune early orbits to isolate invariant set
   )

   # Render the structural bifurcation map
   plt.figure(figsize=(11, 6), dpi=150)
   plt.scatter(m_data, x_data, s=0.08, color='midnightblue', alpha=0.4)
   plt.title("Bifurcation Diagram: Transition Matrix to Anamorphic Chaos", fontsize=12, fontweight='bold')
   plt.xlabel("Marangoni Non-Linear Coupling Factor ($m_{coupling}$)", fontsize=10)
   plt.ylabel("Stroboscopic State Coordinate $X_n$ (Mechanical Boundary)", fontsize=10)
   plt.grid(True, lw=0.4, alpha=0.2, linestyle='--')
   plt.xlim(min(m_data), max(m_data))

   # Visual anchor marking the birth of chaotic mixing
   plt.axvline(x=0.015, color='crimson', linestyle=':', alpha=0.7, label='Onset of Chaotic Flash Basin')
   plt.legend(loc='upper left')

   plt.tight_layout()
   plt.show()
