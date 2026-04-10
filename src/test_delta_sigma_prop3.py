"""
Feature: waveform-dds-upgrade, Property 3: delta-sigma average duty cycle convergence

Property 3: Delta-Sigma average duty cycle convergence
  For any constant 8-bit input value V applied for 512 consecutive clock cycles,
  the running average of the PDM output shall converge to within ±2/255 of V/255.

Validates: Requirements 4.6, 4.7

Python simulation model mirrors the corrected Verilog (delta_sigma.v):

  assign pdm_out = accumulator[8];  // combinational

  always @(posedge clk or negedge rst_n) begin
      if (!rst_n) accumulator <= 9'h0;
      else        accumulator <= accumulator + {1'b0, data_in} - {pdm_out, 8'b0};
  end

pdm_out is combinational from accumulator[8], so on each cycle:
  new_accumulator = (accumulator + data_in - pdm_out * 256) & 0x1FF
  pdm_out         = new_accumulator[8]   (MSB of the NEW accumulator)
"""

import random
import sys

CYCLES = 512
TOLERANCE = 2 / 255  # ±2/255


def simulate_delta_sigma(data_in: int, cycles: int) -> int:
    """
    Simulate the delta_sigma module for `cycles` clock cycles with a constant
    data_in value. Returns the count of cycles where pdm_out == 1.

    Mirrors the corrected Verilog: pdm_out is combinational from accumulator[8].
    Each cycle:
      new_acc = (acc + data_in - pdm_out * 256) & 0x1FF
      pdm_out = new_acc[8]   (MSB of NEW accumulator)
    """
    assert 0 <= data_in <= 255, "data_in must be 0-255"

    accumulator = 0  # reset state
    high_count = 0

    for _ in range(cycles):
        pdm_out = (accumulator >> 8) & 1  # current pdm_out (combinational)
        new_accumulator = (accumulator + data_in - pdm_out * 256) & 0x1FF
        accumulator = new_accumulator
        # count the new pdm_out after update
        high_count += (accumulator >> 8) & 1

    return high_count


def run_property_3(num_samples: int = 100, seed: int = 42) -> bool:
    """
    Run Property 3 for `num_samples` randomized values of V in [0, 255].
    """
    rng = random.Random(seed)

    fixed_values = [0, 1, 127, 128, 254, 255]
    random_values = [rng.randint(0, 255) for _ in range(num_samples - len(fixed_values))]
    test_values = fixed_values + random_values

    passed = 0
    failed = 0
    failures = []

    print("Feature: waveform-dds-upgrade, Property 3: delta-sigma average duty cycle convergence")
    print()
    print(f"  Cycles per test : {CYCLES}")
    print(f"  Tolerance       : ±{TOLERANCE:.6f}  (±2/255)")
    print(f"  Test values     : {len(test_values)}")
    print()

    for V in test_values:
        high_count = simulate_delta_sigma(V, CYCLES)
        measured_duty = high_count / CYCLES
        expected_duty = V / 255
        error = abs(measured_duty - expected_duty)
        ok = error <= TOLERANCE

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
            failures.append((V, high_count, measured_duty, expected_duty, error))

        print(
            f"  [{status}] V={V:3d}  high={high_count:3d}/{CYCLES}"
            f"  measured={measured_duty:.6f}"
            f"  expected={expected_duty:.6f}"
            f"  error={error:.6f}"
            f"  tol={TOLERANCE:.6f}"
        )

    print()
    print(f"Summary: {passed} passed, {failed} failed out of {len(test_values)} tests")

    if failures:
        print()
        print("FAILURES:")
        for V, high_count, measured, expected, error in failures:
            print(
                f"  V={V:3d}  high={high_count:3d}/{CYCLES}"
                f"  measured={measured:.6f}  expected={expected:.6f}"
                f"  error={error:.6f}  tol={TOLERANCE:.6f}"
            )

    return failed == 0


if __name__ == "__main__":
    all_passed = run_property_3(num_samples=100, seed=42)
    print()
    if all_passed:
        print("RESULT: PASS — Property 3 holds for all test cases.")
        sys.exit(0)
    else:
        print("RESULT: FAIL — Property 3 violated for one or more test cases.")
        sys.exit(1)
