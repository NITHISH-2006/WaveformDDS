"""
Feature: waveform-dds-upgrade, Property 3: delta-sigma average duty cycle convergence
For any constant V (0-255) applied for 512 cycles, |count/512 - V/255| <= 2/255.
Validates: Requirements 4.6, 4.7
"""
import random, sys

CYCLES = 512
TOL = 2 / 255

def simulate(V, cycles):
    acc = 0; high = 0
    for _ in range(cycles):
        pdm = (acc >> 8) & 1
        acc = (acc + V - pdm * 256) & 0x1FF
        high += (acc >> 8) & 1
    return high

random.seed(42)
fixed = [0, 1, 127, 128, 254, 255]
vals = fixed + [random.randint(0, 255) for _ in range(94)]
passed = failed = 0
for V in vals:
    h = simulate(V, CYCLES)
    err = abs(h/CYCLES - V/255)
    if err <= TOL: passed += 1
    else: failed += 1; print(f"FAIL V={V} high={h} err={err:.4f} tol={TOL:.4f}")

print(f"Summary: {passed} passed, {failed} failed")
print("RESULT: PASS" if failed == 0 else "RESULT: FAIL")
sys.exit(0 if failed == 0 else 1)
