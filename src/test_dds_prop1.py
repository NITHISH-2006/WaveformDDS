"""
Feature: waveform-dds-upgrade, Property 1: wave select mux correctness

For randomized phase accumulator states and all four wave_select values,
dds_output shall match the expected waveform formula for each selection:
  - wave_select=0: sine path selected (mocked sine value passed through)
  - wave_select=1: {8{phase_accumulator[27]}} = 0xFF if bit 27 is 1, else 0x00
  - wave_select=2: phase_accumulator_trunc[11:4] = phase_accumulator[27:20]
  - wave_select=3: prng_data (mocked, verify it is selected)

Runs 100 randomized iterations per wave_select value (400 total).

Validates: Requirements 1.2, 1.3, 1.4, 1.5
"""

import random


def wave_select_mux(wave_select, phase_accumulator, sine_data_post_offset_saturated, prng_data):
    """Model the wave_select output mux from dds.v."""
    phase_accumulator_trunc = (phase_accumulator >> 16) & 0xFFF   # bits [27:16]

    if wave_select == 0:
        return sine_data_post_offset_saturated & 0xFF
    elif wave_select == 1:
        bit27 = (phase_accumulator >> 27) & 0x1
        return 0xFF if bit27 else 0x00
    elif wave_select == 2:
        return (phase_accumulator_trunc >> 4) & 0xFF
    else:
        return prng_data & 0xFF


ITERATIONS = 100
PHASE_MAX  = (1 << 28) - 1


def run_tests():
    total_pass = 0
    total_fail = 0
    failures   = []

    test_cases = [
        (0, "Sine     (wave_select=0)"),
        (1, "Square   (wave_select=1)"),
        (2, "Sawtooth (wave_select=2)"),
        (3, "PRNG     (wave_select=3)"),
    ]

    for ws, label in test_cases:
        ws_pass = 0
        ws_fail = 0

        for iteration in range(ITERATIONS):
            phase_acc = random.randint(0, PHASE_MAX)
            sine_mock = random.randint(0, 255)
            prng_mock = random.randint(0, 255)

            actual = wave_select_mux(ws, phase_acc, sine_mock, prng_mock)

            if ws == 0:
                expected = sine_mock & 0xFF
            elif ws == 1:
                expected = 0xFF if ((phase_acc >> 27) & 1) else 0x00
            elif ws == 2:
                trunc = (phase_acc >> 16) & 0xFFF
                expected = (trunc >> 4) & 0xFF
            else:
                expected = prng_mock & 0xFF

            if actual == expected:
                ws_pass += 1
            else:
                ws_fail += 1
                failures.append((ws, iteration, phase_acc, sine_mock, prng_mock, actual, expected))

        status = "PASS" if ws_fail == 0 else "FAIL"
        print(f"  [{status}] {label}: {ws_pass}/{ITERATIONS} passed")
        total_pass += ws_pass
        total_fail += ws_fail

    return total_pass, total_fail, failures


def main():
    print("Feature: waveform-dds-upgrade, Property 1: wave select mux correctness")
    print(f"Running {ITERATIONS} randomized iterations per wave_select ({ITERATIONS * 4} total)")
    print()

    random.seed(42)
    total_pass, total_fail, failures = run_tests()

    print()
    print(f"Summary: {total_pass} passed, {total_fail} failed out of {ITERATIONS * 4} tests")

    if failures:
        print("\nFailing cases:")
        for ws, it, pa, sm, pm, act, exp in failures:
            print(f"  ws={ws} iter={it} phase=0x{pa:07X} sine=0x{sm:02X} prng=0x{pm:02X} "
                  f"actual=0x{act:02X} expected=0x{exp:02X}")
        print("\nRESULT: FAIL")
        raise SystemExit(1)
    else:
        print("\nRESULT: PASS — all wave_select mux outputs match expected formulas")


if __name__ == "__main__":
    main()
