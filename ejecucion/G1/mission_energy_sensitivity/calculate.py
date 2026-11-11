"""Ideal acceleration and cruise energy sensitivity; not an aircraft model."""
import csv
import itertools
import math
from pathlib import Path

G_MS2 = 9.80665
HERE = Path(__file__).resolve().parent


def evaluate(mass_kg, speed_kmh, accel_g, drag_n, duration_s,
             efficiency=0.6, energy_wh_kg=150.0, power_w_kg=5000.0):
    values = (mass_kg, speed_kmh, accel_g, drag_n, duration_s,
              efficiency, energy_wh_kg, power_w_kg)
    if not all(math.isfinite(x) and x > 0 for x in values) or efficiency > 1:
        raise ValueError('All inputs must be positive and finite; efficiency must not exceed one.')
    speed_ms = speed_kmh / 3.6
    acceleration_ms2 = accel_g * G_MS2
    time_s = speed_ms / acceleration_ms2
    distance_m = speed_ms * time_s / 2
    # Constant drag is a hypothetical sensitivity in both phases, not a drag model.
    acceleration_work_j = 0.5 * mass_kg * speed_ms**2 + drag_n * distance_m
    cruise_work_j = drag_n * speed_ms * duration_s
    energy_wh = (acceleration_work_j + cruise_work_j) / efficiency / 3600
    peak_power_w = (mass_kg * acceleration_ms2 + drag_n) * speed_ms / efficiency
    mass_energy_kg = energy_wh / energy_wh_kg
    mass_power_kg = peak_power_w / power_w_kg
    return dict(mass_kg=mass_kg, speed_kmh=speed_kmh, accel_g=accel_g,
                drag_n=drag_n, cruise_duration_s=duration_s,
                assumed_efficiency=efficiency, assumed_pack_energy_wh_kg=energy_wh_kg,
                assumed_pack_power_w_kg=power_w_kg, acceleration_time_s=time_s,
                acceleration_distance_m=distance_m, electrical_energy_wh=energy_wh,
                peak_electrical_power_w=peak_power_w,
                pack_energy_mass_kg=mass_energy_kg, pack_power_mass_kg=mass_power_kg,
                pack_mass_kg=max(mass_energy_kg, mass_power_kg),
                pack_fraction_of_total=max(mass_energy_kg, mass_power_kg) / mass_kg)


def main():
    cases = itertools.product((2., 5., 10.), (600., 1000.), (.5, 1., 2., 5.),
                              (20., 50., 100., 200.), (30., 120., 300.))
    rows = [evaluate(*case) for case in cases]
    with (HERE / 'scenarios.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
