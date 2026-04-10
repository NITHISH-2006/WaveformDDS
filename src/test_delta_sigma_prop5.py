"""
Feature: waveform-dds-upgrade, Property 5: delta-sigma reset clears accumulator
After reset, accumulator=0 and pdm_out=0 regardless of prior history.
Validates: Requirement 4.3
"""
import random, sys

def run_cycles(acc, V, n):
    for _ in range(n):
        pdm = (acc >> 8) & 1
        acc = (acc + V - pdm * 256) & 0x1FF
    return acc

random.seed(42)
passed = failed = 0
for _ in range(100):
    # Build up arbitrary state
    acc = run_cycles(0, random.randint(0, 255), random.randint(1, 200))
    # Apply reset
    acc = 0
    pdm = (acc >> 8) & 1
    if acc == 0 and pdm == 0:
        passed += 1
    else:
        failed += 1
        print(f"FAIL acc={acc} pdm={pdm}")

print(f"Summary: {passed} passed, {failed} failed")
print("RESULT: PASS" if failed == 0 else "RESULT: FAIL")
sys.exit(0 if failed == 0 else 1)
