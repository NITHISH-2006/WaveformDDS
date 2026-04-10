"""
Feature: waveform-dds-upgrade, Property 2: quarter-wave reconstruction fidelity
For all 256 phase indices, reconstructed amplitude must match sine.mem within +/-1 LSB.
Validates: Requirement 3.8
"""
import os, sys

def load_mem(path):
    with open(path) as f:
        return [int(l.strip(), 16) for l in f if l.strip()]

def s8(v): return v if v < 128 else v - 256

script_dir = os.path.dirname(os.path.abspath(__file__))
sq = load_mem(os.path.join(script_dir, "sine_quarter.mem"))
sf = load_mem(os.path.join(script_dir, "sine.mem"))
assert len(sq) == 64 and len(sf) == 256

failures = []
for i in range(256):
    q = (i >> 6) & 3
    addr = i & 0x3F
    eff = ((64 - addr) if addr else 63) if (q & 1) else addr
    rd = sq[eff]
    rec = s8((~rd + 1) & 0xFF) if (q & 2) else s8(rd)
    exp = s8(sf[i])
    if abs(rec - exp) > 1:
        failures.append((i, rec, exp, abs(rec-exp)))

if failures:
    for i, r, e, d in failures:
        print(f"FAIL index={i} rec={r} exp={e} diff={d}")
    print(f"RESULT: FAIL — {len(failures)} failures")
    sys.exit(1)
else:
    print("RESULT: PASS — all 256 phase indices within +/-1 LSB")
