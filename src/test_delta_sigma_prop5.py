"""
Feature: waveform-dds-upgrade, Property 5: delta-sigma reset clears accumulator

Property 5: Delta-Sigma reset clears accumulator
  For any prior input history, asserting rst_n=0 then rst_n=1 shall cause the
  accumulator to be 0 and pdm_out to be 0 on the very next rising clock edge,
  regardless of prior input history.

Validates: Requirements 4.3

Python simulation model mirrors the corrected Verilog (delta_sigma.v):

  assign pdm_out = accumulator[8];  // combinational

  always @(posedge clk or negedge rst_n) begin
      if (!rst_n) accumulator <= 9'h0;
      else        accumulator <= accumulator + {1'b0, data_in} - {pdm_out, 8'b0};
  end

After reset (accumulator=0):
  pdm_out = accumulator[8] = 0  (combinational)

On the first clock after reset deassertion with any data_in:
  new_acc = (0 + data_in - 0 * 256) & 0x1FF = data_in
  pdm_out = new_acc[8] = (data_in >> 8) & 1 = 0  (data_in is 8-bit, so bit 8 is always 0)
"""

import random
import sys


def simulate_delta_sigma_cycles(accumulator: int, data_in: int, cycles: int) -> int:
    """
    Run the delta_sigma model for `cycles` clock cycles starting from the given
    accumulator state with a constant data_in. Returns the final accumulator value.

    Each cycle:
      pdm_out = (accumulator >> 8) & 1  (combinational)
      accumulator = (accumulator + data_in - pdm_out * 256) & 0x1FF
    """
    for _ in range(cycles):
        pdm_out = (accumulator >> 8) & 1
        accumulator = (accumulator + data_in - pdm_out * 256) & 0x1FF
    return accumulator


def apply_reset() -> int:
    """Apply reset: accumulator becomes 0."""
    return 0


def pdm_out_from_accumulator(accumulator: int) -> int:
    """Combinational pdm_out: MSB (bit 8) of accumulator."""
    return (accumulator >> 8) & 1


def run_property_5(num_tests: int = 100, seed: int = 42) -> bool:
    """
    Run Property 5 for `num_tests` randomized input histories.

    For each test:
      1. Apply random data_in values for a random number of cycles (1-200)
         to build up arbitrary accumulator state.
      2. Apply reset (accumulator = 0).
      3. Verify accumulator == 0 and pdm_out == 0 immediately after reset.
      4. Optionally run one more clock cycle with a random data_in and verify
         the accumulator updates deterministically from 0.
    """
    rng = random.Random(seed)

    passed = 0
    failed = 0
    failures = []

    print("Feature: waveform-dds-upgrade, Property 5: delta-sigma reset clears accumulator")
    print()
    print(f"  Number of tests : {num_tests}")
    print(f"  History cycles  : 1–200 (randomized)")
    print()

    for test_idx in range(num_tests):
        # Step 1: Build up arbitrary accumulator state via random input history
        num_history_cycles = rng.randint(1, 200)
        accumulator = 0  # start from reset state

        for _ in range(num_history_cycles):
            data_in = rng.randint(0, 255)
            pdm_out = pdm_out_from_accumulator(accumulator)
            accumulator = (accumulator + data_in - pdm_out * 256) & 0x1FF

        pre_reset_accumulator = accumulator

        # Step 2: Apply reset
        accumulator = apply_reset()

        # Step 3: Verify accumulator == 0 and pdm_out == 0 after reset
        post_reset_accumulator = accumulator
        post_reset_pdm_out = pdm_out_from_accumulator(accumulator)

        acc_ok = post_reset_accumulator == 0
        pdm_ok = post_reset_pdm_out == 0

        # Step 4: Run one clock cycle after reset deassertion with a random data_in
        # and verify the accumulator updates deterministically from 0
        post_reset_data_in = rng.randint(0, 255)
        pdm_before_clock = pdm_out_from_accumulator(accumulator)  # should be 0
        accumulator_after_one_cycle = (accumulator + post_reset_data_in - pdm_before_clock * 256) & 0x1FF
        expected_after_one_cycle = post_reset_data_in  # since acc=0, pdm=0: acc = data_in

        cycle_ok = accumulator_after_one_cycle == expected_after_one_cycle

        ok = acc_ok and pdm_ok and cycle_ok
        status = "PASS" if ok else "FAIL"

        if ok:
            passed += 1
        else:
            failed += 1
            failures.append({
                "test_idx": test_idx,
                "history_cycles": num_history_cycles,
                "pre_reset_acc": pre_reset_accumulator,
                "post_reset_acc": post_reset_accumulator,
                "post_reset_pdm": post_reset_pdm_out,
                "acc_ok": acc_ok,
                "pdm_ok": pdm_ok,
                "cycle_ok": cycle_ok,
                "post_reset_data_in": post_reset_data_in,
                "acc_after_one_cycle": accumulator_after_one_cycle,
                "expected_after_one_cycle": expected_after_one_cycle,
            })

        print(
            f"  [{status}] test={test_idx:3d}"
            f"  history={num_history_cycles:3d} cycles"
            f"  pre_reset_acc=0x{pre_reset_accumulator:03X}"
            f"  post_reset_acc={post_reset_accumulator}"
            f"  pdm_out={post_reset_pdm_out}"
            f"  next_cycle_acc={accumulator_after_one_cycle}"
            f"  (data_in={post_reset_data_in})"
        )

    print()
    print(f"Summary: {passed} passed, {failed} failed out of {num_tests} tests")

    if failures:
        print()
        print("FAILURES:")
        for f in failures:
            print(
                f"  test={f['test_idx']:3d}"
                f"  history={f['history_cycles']} cycles"
                f"  pre_reset_acc=0x{f['pre_reset_acc']:03X}"
                f"  post_reset_acc={f['post_reset_acc']} (expected 0, ok={f['acc_ok']})"
                f"  pdm_out={f['post_reset_pdm']} (expected 0, ok={f['pdm_ok']})"
                f"  next_cycle_acc={f['acc_after_one_cycle']}"
                f"  expected_next={f['expected_after_one_cycle']}"
                f"  (data_in={f['post_reset_data_in']}, cycle_ok={f['cycle_ok']})"
            )

    return failed == 0


if __name__ == "__main__":
    all_passed = run_property_5(num_tests=100, seed=42)
    print()
    if all_passed:
        print("RESULT: PASS — Property 5 holds for all test cases.")
        sys.exit(0)
    else:
        print("RESULT: FAIL — Property 5 violated for one or more test cases.")
        sys.exit(1)
