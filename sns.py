import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


class ProductionSonoluminescentSuite:
    """
    Deterministic single-pipeline simulation platform for generating
    bifurcation diagrams of a modified Halvorsen dynamical system.
    """

    def __init__(self, a_coeff=1.4, omega=1.0, damping_alpha=0.003):
        self.a = a_coeff
        self.omega = omega
        self.alpha = damping_alpha

    def dynamical_system(self, t, state, m_coupling):
        """
        Governing nonlinear vector field.
        """
        x, y, z = state

        # Modified Halvorsen backbone
        dx_base = -self.a * x - 4 * y - 4 * z - y**2
        dy_base = -self.a * y - 4 * z - 4 * x - z**2
        dz_base = -self.a * z - 4 * x - 4 * y - x**2

        # Periodic nonlinear coupling
        shared_shear = (
            m_coupling
            * x
            * y
            * z
            * np.sin(self.omega * t)
        )

        # Cubic radial damping
        r_squared = x**2 + y**2 + z**2
        damping = -self.alpha * r_squared

        dx = dx_base + shared_shear + damping * x
        dy = dy_base + shared_shear + damping * y
        dz = dz_base + shared_shear + damping * z

        return [dx, dy, dz]

    def generate_bifurcation(
        self,
        seed_state,
        m_min=0.0,
        m_max=0.035,
        resolution=200,
        num_periods=500,
        transient_cutoff=350,
    ):
        """
        Deterministic single-pipeline parameter sweep.
        """

        if transient_cutoff >= num_periods:
            raise ValueError(
                "transient_cutoff must be smaller than num_periods."
            )

        drive_period = 2 * np.pi / self.omega

        # Exact Poincaré sampling times
        t_samples = np.linspace(
            0.0,
            (num_periods - 1) * drive_period,
            num_periods,
        )

        m_values = np.linspace(
            m_min,
            m_max,
            resolution,
        )

        m_all = []
        x_all = []

        print(
            f"Running deterministic sweep over {resolution} parameter values..."
        )

        for i, m in enumerate(m_values):

            if (i + 1) % 10 == 0 or i == 0:
                print(f"Completed {i + 1}/{resolution}")

            sol = solve_ivp(
                lambda t, s: self.dynamical_system(t, s, m),
                (0.0, t_samples[-1]),
                np.asarray(seed_state, dtype=float),
                t_eval=t_samples,
                method="DOP853",
                rtol=1e-6,
                atol=1e-8,
            )

            if not sol.success:
                raise RuntimeError(
                    f"Integration failed at m={m:.6f}\n{sol.message}"
                )

            x = sol.y[0, transient_cutoff:]

            m_all.append(np.full(x.shape, m))
            x_all.append(x)

        return (
            np.concatenate(m_all),
            np.concatenate(x_all),
        )


def main():

    suite = ProductionSonoluminescentSuite(
        a_coeff=1.4,
        omega=1.0,
        damping_alpha=0.003,
    )

    initial_seed = np.array(
        [-1.48, -1.51, 2.04],
        dtype=float,
    )

    m_data, x_data = suite.generate_bifurcation(
        seed_state=initial_seed,
        m_min=0.0,
        m_max=0.035,
        resolution=200,
        num_periods=500,
        transient_cutoff=350,
    )

    plt.figure(figsize=(11, 6), dpi=150)

    plt.scatter(
        m_data,
        x_data,
        s=0.08,
        alpha=0.4,
        color="midnightblue",
        edgecolors="none",
    )

    plt.title(
        "Bifurcation Diagram: Modified Halvorsen System",
        fontsize=12,
        fontweight="bold",
    )

    plt.xlabel(
        "Coupling Parameter (m)",
        fontsize=10,
    )

    plt.ylabel(
        "Stroboscopic Coordinate $X_n$",
        fontsize=10,
    )

    plt.grid(
        True,
        linestyle="--",
        linewidth=0.4,
        alpha=0.25,
    )

    plt.xlim(
        m_data.min(),
        m_data.max(),
    )

    # Candidate transition marker
    plt.axvline(
        x=0.015,
        color="crimson",
        linestyle=":",
        alpha=0.7,
        label="Candidate Transition Parameter",
    )

    plt.legend(loc="upper left")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
