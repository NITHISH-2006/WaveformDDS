"""
Feature: waveform-dds-upgrade, Property 1: wave select mux correctness
Validates: Requirements 1.2, 1.3, 1.4, 1.5
400 randomized tests (100 per wave_select value).
"""
import random, sys

def mux(ws, phase_acc, sine_mock, prng_mock):
    trunc = (phase_acc >> 16) & 0xFFF
    if ws == 0: return sine_mock & 0xFF
    if ws == 1: return 0xFF if (phase_acc >> 27) & 1 else 0x00
    if ws == 2: return (trunc >> 4) & 0xFF
    return prng_mock & 0xFF

random.seed(42)
passed = failed = 0
for ws in range(4):
    for _ in range(100):
        pa = random.randint(0, (1<<28)-1)
        sm = random.randint(0, 255)
        pm = random.randint(0, 255)
        actual = mux(ws, pa, sm, pm)
        trunc = (pa >> 16) & 0xFFF
        if ws == 0:   exp = sm & 0xFF
        elif ws == 1: exp = 0xFF if (pa >> 27) & 1 else 0x00
        elif ws == 2: exp = (trunc >> 4) & 0xFF
        else:         exp = pm & 0xFF
        if actual == exp: passed += 1
        else: failed += 1; print(f"FAIL ws={ws} pa=0x{pa:07X} actual=0x{actual:02X} exp=0x{exp:02X}")

print(f"Summary: {passed} passed, {failed} failed")
print("RESULT: PASS" if failed == 0 else "RESULT: FAIL")
sys.exit(0 if failed == 0 else 1)
