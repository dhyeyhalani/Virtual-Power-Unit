"""
Lesson 1 - Simulating an F1 car accelerating down a straight.

Project: Virtual 2026 Power Unit + Energy Strategy Optimizer
Goal of this lesson: turn Newton's 2nd law (F = m * a) into a simulation.

Run:  python lesson1_straight_line.py
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. CAR PARAMETERS  (round, realistic-ish numbers - NOT official team data)
# ---------------------------------------------------------------------------
MASS = 800.0          # kg   car + driver + some fuel
BATTERY_CAPACITY = [0.0, 2_000_000.0, 4_000_000.0, 6_000_000.0]
P_ICE = 400_000.0     # W    combustion engine power (~400 kW)
P_MGUK = 350_000.0    # W    electric motor power (~350 kW)
CDA = 1.2             # m^2  drag coefficient x frontal area ("how draggy")
RHO = 1.225           # kg/m^3 air density at sea level
CRR = 0.015           # rolling resistance coefficient (tyre friction losses)
G = 9.81              # m/s^2 gravity
TYRE_GRIP = {"C1":1.25,"C2":1.30,"C3":1.35,"C4":1.40,"C5":1.45,"Intermediate":1.05,"Wet":0.85}     # max forward acceleration in g before the tyres spin

# ---------------------------------------------------------------------------
# 2. SIMULATION SETTINGS
# ---------------------------------------------------------------------------
DT = 0.01                     # s    time step (100 updates per second)
STRAIGHT_LENGTH = 1000.0      # m    roughly a Monza-length straight
START_SPEED = 100 / 3.6       # m/s  corner-exit speed (100 km/h)


def drive_force(speed, power):
    """Force the power unit can push the car with at this speed.

    Power = Force x Speed   ->   Force = Power / Speed
    But the tyres can only handle so much force before spinning,
    so we cap it at the grip limit.
    """
    force_from_power = power / speed
    force_grip_max = GRIP_LIMIT * MASS * G
    return min(force_from_power, force_grip_max)


def resistive_forces(speed):
    """Forces slowing the car down."""
    drag = 0.5 * RHO * CDA * speed**2      # grows with speed SQUARED
    rolling = CRR * MASS * G               # roughly constant
    return drag + rolling


def simulate_straight(Power_Ice, Power_MGUK, BAT_CAP):
    """Simulate the car down the straight at a constant power.

    Returns arrays of distance (m) and speed (km/h).
    """
    distance = 0.0
    time = 0.0
    speed = START_SPEED
    energy = BAT_CAP
    distances, speeds, energies, times= [distance], [speed], [energy], [time]

    while distance < STRAIGHT_LENGTH:

        if energy>0:
        # Newton's 2nd law:  a = (F_push - F_resist) / m
            accel = (drive_force(speed, Power_Ice + Power_MGUK) - resistive_forces(speed)) / MASS
            energy_used = Power_MGUK * DT
            energy = max(energy - energy_used, 0)
        else:
            accel = (drive_force(speed,Power_Ice) - resistive_forces(speed)) / MASS

        # Euler integration: nudge speed and position forward one tiny step
        time = time + DT
        speed = speed + accel * DT
        distance = distance + speed * DT

        distances.append(distance)
        speeds.append(speed)
        energies.append(energy)
        times.append(time)
        #print(energies)
        #print(times)


    return np.array(distances), np.array(speeds) * 3.6 , np.array(energies), np.array(times) # m/s -> km/h


# ---------------------------------------------------------------------------
# 3. RUN TWO SCENARIOS AND COMPARE
# ---------------------------------------------------------------------------

plt.figure(figsize=(9, 5))
for caps in BATTERY_CAPACITY:
    dist_MJ, speed_MJ, energy_MJ, time_MJ = simulate_straight(P_ICE, P_MGUK, caps)
    mj = caps / 1_000_000

    found = None
    for i in range(len(energy_MJ)):
        if energy_MJ[i] == 0:
            found = i
            break

    if found is None:
        empty = "battery never emptied"
    else:
        empty = f"battery empty at {time_MJ[found]:.2f} s ({dist_MJ[found]:.0f} m)"

    print(f"Battery = {mj:.0f} MJ: {speed_MJ[-1]:.0f} km/h, "
          f"straight took {time_MJ[-1]:.2f} s, {empty}")
    plt.plot(dist_MJ, speed_MJ, label=f"Battery = {mj:.0f} MJ", linewidth=2)
plt.xlabel("Distance along the straight (m)")
plt.ylabel("Speed (km/h)")
plt.title("Lesson 1: F1 car accelerating down a 1 km straight")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("lesson1_speed_trace.png", dpi=120)
plt.show()





#print(f"Engine only (ICE)        : end-of-straight speed = {speed_ice[-1]:.0f} km/h")


# Theoretical top speed: where push force = drag  ->  P = 0.5*rho*CdA*v^3
for name, p in [("Full power", P_ICE + P_MGUK), ("Engine only", P_ICE)]:
    v_top = (2 * p / (RHO * CDA)) ** (1 / 3)
    print(f"{name:11s} theoretical top speed = {v_top * 3.6:.0f} km/h")



