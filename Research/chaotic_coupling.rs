// Recursive Amplification Manifold Computing Pipeline (Rust)

// Input Parameters
//       |
//       v
// Nonlinear State Manifold Initialization
//       |
//       v
// Adaptive ODE Integrator
//       |
//       v
// Recursive Coupling Evolution
//       |
//       v
// Poincaré / Manifold Sampling
//       |
//       v
// Bifurcation Data Accumulation
//       |
//       v
// Phase Transition Diagnostics
//       |
//       v
// Visualization / Export

use std::f64::consts::PI;

#[derive(Clone, Copy)]
struct State {
    x: f64,
    y: f64,
    z: f64,
}

struct Parameters {
    a: f64,
    omega: f64,
    alpha: f64,
    coupling: f64,
}


// Recursive nonlinear manifold vector field
fn manifold_dynamics(
    t: f64,
    s: State,
    p: &Parameters,
) -> State {

    // Halvorsen-inspired cyclic quadratic core
    let dx_base =
        -p.a*s.x - 4.0*s.y - 4.0*s.z - s.y.powi(2);

    let dy_base =
        -p.a*s.y - 4.0*s.z - 4.0*s.x - s.z.powi(2);

    let dz_base =
        -p.a*s.z - 4.0*s.x - 4.0*s.y - s.x.powi(2);


    // Recursive cubic coupling
    let recursive_coupling =
        p.coupling
        * s.x
        * s.y
        * s.z
        * (p.omega*t).sin();


    // Nonlinear radial damping
    let r2 =
        s.x*s.x +
        s.y*s.y +
        s.z*s.z;

    let damping =
        -p.alpha*r2;


    State {
        x: dx_base + recursive_coupling + damping*s.x,
        y: dy_base + recursive_coupling + damping*s.y,
        z: dz_base + recursive_coupling + damping*s.z,
    }
}


// Single RK4 integration step
fn rk4_step(
    t: f64,
    dt: f64,
    state: State,
    params: &Parameters,
) -> State {

    let k1 = manifold_dynamics(t,state,params);

    let k2 = manifold_dynamics(
        t + dt/2.0,
        State {
            x: state.x+k1.x*dt/2.0,
            y: state.y+k1.y*dt/2.0,
            z: state.z+k1.z*dt/2.0,
        },
        params
    );

    let k3 = manifold_dynamics(
        t + dt/2.0,
        State {
            x: state.x+k2.x*dt/2.0,
            y: state.y+k2.y*dt/2.0,
            z: state.z+k2.z*dt/2.0,
        },
        params
    );

    let k4 = manifold_dynamics(
        t+dt,
        State {
            x: state.x+k3.x*dt,
            y: state.y+k3.y*dt,
            z: state.z+k3.z*dt,
        },
        params
    );


    State {
        x: state.x + dt/6.0 *
            (k1.x+2.0*k2.x+2.0*k3.x+k4.x),

        y: state.y + dt/6.0 *
            (k1.y+2.0*k2.y+2.0*k3.y+k4.y),

        z: state.z + dt/6.0 *
            (k1.z+2.0*k2.z+2.0*k3.z+k4.z),
    }
}



fn run_pipeline() {

    let seed = State {
        x:-1.48,
        y:-1.51,
        z:2.04,
    };


    let period = 2.0*PI;

    let mut bifurcation_data:
        Vec<(f64,f64)> = Vec::new();


    // Coupling sweep
    for m_index in 0..200 {

        let coupling =
            0.035 *
            m_index as f64 /
            200.0;


        let params = Parameters {
            a:1.4,
            omega:1.0,
            alpha:0.003,
            coupling,
        };


        let mut state = seed;

        let total_periods = 500;
        let transient = 350;

        let dt = 0.01;

        let mut t = 0.0;


        for step in 0..
            ((total_periods as f64 * period)/dt) as usize
        {

            state =
                rk4_step(
                    t,
                    dt,
                    state,
                    &params
                );

            t += dt;


            // Poincare sampling
            if step % ((period/dt) as usize)==0
                &&
               step > (transient as f64 *
                        period/dt) as usize
            {
                bifurcation_data.push(
                    (
                        coupling,
                        state.x
                    )
                );
            }
        }
    }


    println!(
        "Generated {} manifold samples",
        bifurcation_data.len()
    );
}



fn main() {

    println!(
        "Recursive Amplification Manifold Pipeline"
    );

    run_pipeline();
}
