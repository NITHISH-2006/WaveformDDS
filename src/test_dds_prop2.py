"""
Feature: waveform-dds-upgrade, Property 2: quarter-wave reconstruction fidelity

For all 256 phase indices (0-255), the amplitude reconstructed by the quarter-wave
symmetry logic shall match the corresponding entry in the original full sine.mem
table within ±1 LSB.

Validates: Requirements 3.8
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_mem_file(path):
    """Load a .mem file (one hex byte per line) and return a list of unsigned ints."""
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(int(line, 16))
    return entries


def to_signed8(v):
    """Convert unsigned 8-bit value to signed."""
    return v if v < 128 else v - 256


def reconstruct(phase_index, sine_quarter_memory):
    """
    Reconstruct the full sine value for a given 8-bit phase index using the
    same quadrant logic as dds.v.

    phase_index: 0-255 (8-bit)
    sine_quarter_memory: list of 64 unsigned 8-bit values

    Returns: signed 8-bit integer
    """
    quadrant = (phase_index >> 6) & 0x03   # top 2 bits  [7:6]
    rom_addr  = phase_index & 0x3F          # bottom 6 bits [5:0]

    # Address mirroring: quadrants 01 and 11 use (64 - rom_addr), clamped to 63 when rom_addr=0
    # Mirrors the corrected dds.v formula: rom_addr ? (64 - rom_addr) : 63
    if quadrant & 0x01:
        effective_addr = (64 - rom_addr) if rom_addr else 63
    else:
        effective_addr = rom_addr

    # ROM lookup (unsigned)
    rom_data_unsigned = sine_quarter_memory[effective_addr]

    # Negation: quadrants 10 and 11 negate via 2's complement
    if quadrant & 0x02:
        reconstructed_unsigned = (~rom_data_unsigned + 1) & 0xFF
    else:
        reconstructed_unsigned = rom_data_unsigned

    return to_signed8(reconstructed_unsigned)


def main():
    sine_quarter_path = os.path.join(SCRIPT_DIR, "sine_quarter.mem")
    sine_full_path     = os.path.join(SCRIPT_DIR, "sine.mem")

    sine_quarter = load_mem_file(sine_quarter_path)
    sine_full    = load_mem_file(sine_full_path)

    assert len(sine_quarter) == 64,  f"Expected 64 entries in sine_quarter.mem, got {len(sine_quarter)}"
    assert len(sine_full)    == 256, f"Expected 256 entries in sine.mem, got {len(sine_full)}"

    failures = []
    print(f"{'Index':>6}  {'Reconstructed':>14}  {'Expected':>9}  {'Diff':>5}  Result")
    print("-" * 55)

    for i in range(256):
        reconstructed = reconstruct(i, sine_quarter)
        expected      = to_signed8(sine_full[i])
        diff          = abs(reconstructed - expected)
        ok            = diff <= 1
        status        = "PASS" if ok else "FAIL"
        print(f"{i:>6}  {reconstructed:>14}  {expected:>9}  {diff:>5}  {status}")
        if not ok:
            failures.append((i, reconstructed, expected, diff))

    print("-" * 55)
    if failures:
        print(f"\nFAIL — {len(failures)} index(es) exceeded ±1 LSB tolerance:")
        for idx, rec, exp, d in failures:
            print(f"  index={idx}: reconstructed={rec}, expected={exp}, diff={d}")
        raise SystemExit(1)
    else:
        print(f"\nPASS — all 256 phase indices reconstructed within ±1 LSB")


if __name__ == "__main__":
    main()
