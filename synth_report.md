# WaveformDDS Synthesis Report

Synthesis utilization and power comparison for the WaveformDDS upgrade targeting **Cyclone V** (5CSEMA5F31C6).
Target clock frequency: **50 MHz**.

This report compares resource usage before the upgrade (256-entry full sine ROM, no Delta-Sigma modulator, no explicit `wave_select`) against the upgraded design (64-entry quarter-wave ROM, `delta_sigma` module, `wave_select` mux).

---

## Resource Utilization Comparison

| Resource             | Pre-Upgrade | Post-Upgrade | Change                        |
|----------------------|-------------|--------------|-------------------------------|
| LUT count            | TBD         | TBD          | TBD                           |
| Flip-Flop count      | TBD         | TBD          | TBD                           |
| BRAM bits            | TBD         | TBD          | Expected ≥ 75% reduction      |
| DSP blocks           | TBD         | TBD          | Expected ≤ 1 (gain multiply)  |
| Static Power (mW)    | TBD         | TBD          | TBD                           |
| Dynamic Power (mW)   | TBD         | TBD          | TBD                           |

> Fill in the Pre-Upgrade and Post-Upgrade columns after running Quartus synthesis on each revision.
> The Change column should be updated with the absolute delta and percentage where applicable.

---

## Synthesis Target

| Parameter         | Value                  |
|-------------------|------------------------|
| Device family     | Cyclone V              |
| Device part       | 5CSEMA5F31C6           |
| Target clock      | 50 MHz                 |
| Tool              | Intel Quartus Prime    |

---

## BRAM Reduction Note

> **To be confirmed after synthesis.**
>
> The quarter-wave ROM optimization reduces the sine lookup table from 256 entries × 8 bits = **2048 bits** to
> 64 entries × 8 bits = **512 bits** — a theoretical reduction of **75%**.
>
> Once synthesis is run, verify that the BRAM bits column above reflects a reduction of **≥ 75%** compared to
> the pre-upgrade baseline. Per Requirements 6.3 and 6.6, the upgraded design must use no more than
> **1 Block RAM primitive** for `sine_quarter_memory`.

---

## DSP Block Note

> **To be confirmed after synthesis.**
>
> The gain multiplication stage (`dds_output = (sine_data * register_gain) >> 8`) is expected to infer
> **≤ 1 DSP block** on Cyclone V. Confirm this in the Post-Upgrade column above (Requirement 6.4).

---

## Notes / Observations

- Run synthesis from the Quartus project root with `dds_top` as the top-level entity for the pre-upgrade baseline, then again after applying all RTL changes for the post-upgrade numbers.
- Power estimates assume default toggle rates (12.5%) and a 50 MHz clock. Adjust the toggle rate in the Power Analyzer if a more accurate estimate is needed.
- The `delta_sigma` module adds a small number of FFs (9-bit accumulator) and no BRAM or DSP resources.
- `wave_select` routing through the synchronizer and mux adds combinational LUTs only; no additional registers beyond the synchronizer flip-flops.
