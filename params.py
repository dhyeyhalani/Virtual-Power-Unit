"""
params.py - Car and rules parameters for the Virtual 2026 Power Unit project.
Supports the 2026, 2027 and (approved) 2028 power unit rules: set YEAR below.

Every value is tagged with WHERE it comes from:
  [REG Cx.y]   = FIA 2026 F1 Technical Regulations, Section C, Issue 21 (19 Oct 2026)
  [DERIVED]    = calculated from regulation values + basic physics
  [CALIBRATED] = tuned so the simulation matches a real 2026 measurement
  [ESTIMATE]   = engineering estimate; not published anywhere. Treat with caution.

Usage:  from params import *

Chassis values (mass, weight split, wheelbase) are IDENTICAL in the 2026 and 2027
regulations (C4.1, C4.2, C2.3.3), so only the power unit section changes by year.
"""

# ---------------------------------------------------------------------------
# PHYSICS CONSTANTS
# ---------------------------------------------------------------------------
G = 9.81                      # m/s^2   gravitational acceleration

# ---------------------------------------------------------------------------
# MASS  [REG C4.1, C4.2, C4.5]
# ---------------------------------------------------------------------------
NOMINAL_TYRE_MASS = 46.4      # kg  [ESTIMATE] Pirelli publishes this each season (C4.7);
                              #     46.4 kg is the widely reported 2026 figure.
MIN_MASS_QUALI = 726.0 + NOMINAL_TYRE_MASS   # kg [REG C4.1] incl. 82 kg driver (C4.5.2), no fuel
MIN_MASS_RACE = 724.0 + NOMINAL_TYRE_MASS    # kg [REG C4.1] all other sessions
QUALI_FUEL = 5.0              # kg  [ESTIMATE] a few kg of fuel for a qualifying run
MASS = MIN_MASS_QUALI + QUALI_FUEL           # kg  ~777 kg: car at the limit, quali trim

# Static weight split. Front axle >= 44% and rear axle >= 54% of min mass [REG C4.2].
REAR_WEIGHT_FRACTION = 0.55   # [DERIVED] rear must be 0.54-0.56, so 0.55 is the middle
WHEELBASE = 3.40              # m   [REG C2.3.3] max 3400 mm
COG_HEIGHT = 0.30             # m   [ESTIMATE] centre-of-gravity height, not published

# ---------------------------------------------------------------------------
# POWER UNIT + ENERGY STORE - depends on the regulation YEAR
# ---------------------------------------------------------------------------
# Sources: 2026 Section C Issue 21 and 2027 Section C Issue 04 (both 19 Oct 2026).
# 2028 values come from Appendix C7 "Approved changes for future years" in the 2027 document.
YEAR = 2026                   # <- change to 2027 or 2028 to switch rule sets

RULES = {
    2026: {
        "fuel_energy_flow_MJh": 3000,   # [REG C5.2.3]
        "ers_k_dc_max_kW": 350,         # [REG C5.2.7]
        "es_soc_window_MJ": 4.0,        # [REG C5.2.9]
        "recharge_per_lap_MJ": 8.5,     # [REG C5.2.10] (7 MJ at some events; quali can be cut)
        "race_normal_cap_kW": 350,      # [REG C5.2.8 i] speed curve, effectively capped at 350
        "race_overtake_cap_kW": 350,    # [REG C5.2.8 ii] speed curve up to 355 kph
        "speed_curves_public": True,    # formulas are written in C5.2.8
    },
    2027: {
        "fuel_energy_flow_MJh": 3150,   # [REG C5.2.3]  +5%
        "ers_k_dc_max_kW": 375,         # [REG C5.2.7]  +25 kW
        "es_soc_window_MJ": 4.5,        # [REG C5.2.9]  +0.5 MJ
        "recharge_per_lap_MJ": 8.5,     # [REG C5.2.10a] unchanged (10 MJ on SC/formation/out laps)
        "race_normal_cap_kW": 300,      # [REG C5.2.8 ii] race, Overtake NOT active
        "race_overtake_cap_kW": 350,    # [REG C5.2.8 i]  race, Overtake active
        "speed_curves_public": False,   # moved to FIA-F1-DOC-111 (not public)
                                        # [ESTIMATE] we ASSUME the 2026 speed-curve shape still applies
    },
    2028: {                             # [REG Appendix C7 of the 2027 doc] approved future changes
        "fuel_energy_flow_MJh": 3400,
        "ers_k_dc_max_kW": 400,
        "es_soc_window_MJ": 5.0,
        "recharge_per_lap_MJ": 8.5,     # not changed in Appendix C7
        "race_normal_cap_kW": 300,      # [ESTIMATE] assumed same as 2027
        "race_overtake_cap_kW": 350,    # [ESTIMATE] assumed same as 2027
        "speed_curves_public": False,
    },
}
R = RULES[YEAR]

# ICE: the rules limit FUEL ENERGY FLOW, not power.
FUEL_ENERGY_FLOW_MAX = R["fuel_energy_flow_MJh"] * 1e6 / 3600   # W of fuel energy (~833 kW in 2026)
ICE_THERMAL_EFFICIENCY = 0.48           # [ESTIMATE] ~48% of fuel energy becomes crank power
P_ICE = FUEL_ENERGY_FLOW_MAX * ICE_THERMAL_EFFICIENCY   # W [DERIVED] 400 / 420 / 453 kW

# MGU-K (electric motor)
P_ERS_K_DC_MAX = R["ers_k_dc_max_kW"] * 1e3   # W [REG C5.2.7] absolute max ELECTRICAL (DC) power
ERS_EFFICIENCY = 0.97         # [REG C5.2.21] same in 2026 and 2027: mechanical = 0.97 x DC
# Speed-dependent limits (C5.2.8) -> implement them in mguk_dc_limit() (your task).

# Energy Store (battery)
ES_SOC_WINDOW = R["es_soc_window_MJ"] * 1e6          # J  most you can deploy "in one go"
RECHARGE_LIMIT_PER_LAP = R["recharge_per_lap_MJ"] * 1e6   # J  needed for full laps later

# ---------------------------------------------------------------------------
# AERODYNAMICS & RESISTANCE
# ---------------------------------------------------------------------------
CDA_STRAIGHT = 0.945          # m^2 [CALIBRATED] drag area in Straight Mode. Tuned so the sim
                              #     hits 341 km/h = fastest 2026 Monza qualifying speed trap.
                              #     "Effective" value: also absorbs gearbox losses we don't model.
RHO = 1.16                    # kg/m^3 [DERIVED] air density at Monza in September (~25 C, ~160 m)
                              #     sea level 15 C = 1.225 ; Mexico City = ~0.96
CRR = 0.015                   #     [ESTIMATE] rolling resistance; tiny effect (~11 kW at 340 km/h)

# ---------------------------------------------------------------------------
# TYRES  [ESTIMATE - Pirelli does not publish friction coefficients]
# ---------------------------------------------------------------------------
# mu = tyre friction coefficient on the track condition each tyre is DESIGNED for.
# Turn mu into a traction limit with traction_limit_g() (your task) - it accounts for
# rear-wheel drive (REAR_WEIGHT_FRACTION) and weight transfer (COG_HEIGHT / WHEELBASE).
TYRE_MU = {
    "C1": 1.55,               # hardest
    "C2": 1.62,
    "C3": 1.70,
    "C4": 1.77,
    "C5": 1.85,               # softest
    "Intermediate": 1.30,     # damp track
    "Wet": 1.05,              # soaked track
}

# ---------------------------------------------------------------------------
# SIMULATION SETTINGS (scenario choices, not car properties)
# ---------------------------------------------------------------------------
DT = 0.005                    # s   halve it: if results barely change, DT is small enough
STRAIGHT_LENGTH = 1000.0      # m
START_SPEED = 100 / 3.6       # m/s slow-corner exit
