# Virtual 2026 F1 Power Unit

A physics-based simulation of a 2026 Formula 1 power unit (engine + MGU-K + battery),
built to study energy deployment and "clipping" under the new 2026 regulations.

## Lesson 1: Straight-line simulation
Simulates an F1 car accelerating down a 1 km straight with different battery sizes.
When the battery runs out, the car loses ~350 kW of electric power and clips.

![Speed trace](/Users/dhyey/Virtual-Power-Unit/lesson1_speed_trace.png)

## Run it
pip install -r requirements.txt
python lesson1_straight_line.py