"""
Lesson 2 - Simulating an F1 car accelerating down a straight and considering the battery clipping depending on the tyres,
and when can the driver deploy to get the maximum battery usage

Project: Virtual 2026 Power Unit + Energy Strategy Optimizer
Goal of this lesson: Understand how tyre used affects the battery on different tracks

Run:  python lesson2_smart_deployment.py
"""

import numpy as np
import matplotlib.pyplot as plt
from params import *

def traction_limit_g(mu):
    return (REAR_WEIGHT_FRACTION * mu) / (1 - mu * COG_HEIGHT / WHEELBASE)

def mguk_dc_limit(speed_kph, rules):
    if speed_kph < 340:
        value = max(0, min(rules["ers_k_dc_max_kW"]*1_000, (1800-5*speed_kph)*1_000))
        return value
    elif speed_kph >=340 and speed_kph < 345:
        value = max(0, min(rules["ers_k_dc_max_kW"]*1_000, (6900-20*speed_kph)*1_000))
        return value
    else:
        return 0
def drive_force(speed, power,grip_g):
    """Force the power unit can push the car with at this speed.

    Power = Force x Speed   ->   Force = Power / Speed
    But the tyres can only handle so much force before spinning,
    so we cap it at the grip limit.
    """
    force_from_power = power / speed
    force_grip_max = grip_g * MASS * G
    return min(force_from_power, force_grip_max)


def resistive_forces(speed):
    """Forces slowing the car down."""
    drag = 0.5 * RHO * CDA_STRAIGHT * speed**2      # grows with speed SQUARED
    rolling = CRR * MASS * G               # roughly constant
    return drag + rolling


def simulate_straight(BAT_CAP,grip, rules):
    """Simulate the car down the straight at a constant power.

    Returns arrays of distance (m) and speed (km/h).
    """
    distance = 0.0
    time = 0.0
    speed = START_SPEED
    energy = BAT_CAP
    distances, speeds, energies, times= [distance], [speed], [energy], [time]

    while distance < STRAIGHT_LENGTH:

        if energy > 0:
            p_dc_allowed = mguk_dc_limit(speed * 3.6, rules)       # from battery (DC)
            p_mech_allowed = ERS_EFFICIENCY * p_dc_allowed          # what reaches the car
            max_tyre_power = grip * MASS * G * speed                # traction force x speed
            useful_room = max_tyre_power - P_ICE                    # minus what the engine already gives
            p_mech = max(0, min(p_mech_allowed, useful_room))
            p_dc = p_mech / ERS_EFFICIENCY

            if p_dc > energy / DT:
                p_dc = energy / DT
                p_mech = p_dc * ERS_EFFICIENCY

            accel = (drive_force(speed, P_ICE + p_mech, grip) - resistive_forces(speed)) / MASS
            energy = max(energy - p_dc * DT, 0)
        else:
            accel = (drive_force(speed,P_ICE,grip) - resistive_forces(speed)) / MASS

        # Euler integration: nudge speed and position forward one tiny step
        time = time + DT
        speed = speed + accel * DT
        distance = distance + speed * DT
        distances.append(distance)
        speeds.append(speed)
        energies.append(energy)
        times.append(time)



    return np.array(distances), np.array(speeds) * 3.6 , np.array(energies), np.array(times) # m/s -> km/h


# ---------------------------------------------------------------------------
# 3. RUN TWO SCENARIOS AND COMPARE
# ---------------------------------------------------------------------------

plt.figure(figsize=(9, 5))
for name,mu in TYRE_MU.items():
    grip = traction_limit_g(mu)
    dist_MJ, speed_MJ, energy_MJ, time_MJ = simulate_straight(ES_SOC_WINDOW,grip,R)
    mj = ES_SOC_WINDOW / 1_000_000

    found = None
    for i in range(len(energy_MJ)):
        if energy_MJ[i] == 0:
            found = i
            break

    if found is None:
        empty = "battery never emptied"
    else:
        empty = f"battery empty at {time_MJ[found]:.2f} s ({dist_MJ[found]:.0f} m)"

    print(f"Tyre = {name}: {speed_MJ[-1]:.0f} km/h, "
          f"straight took {time_MJ[-1]:.2f} s, {empty}, Energy Used :{(ES_SOC_WINDOW-energy_MJ[-1])/1_000_000:.2f} MJ")
    plt.plot(dist_MJ, speed_MJ, label=f"Tyre type = {name}", linewidth=2)
plt.xlabel("Distance along the straight (m)")
plt.ylabel("Speed (km/h)")
plt.title("Lesson 2: Understanding the need of Smart Deployment")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("lesson2_SmartDeployment_trace.png", dpi=120)
plt.show()



