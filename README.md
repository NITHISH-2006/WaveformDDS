# DDS Waveform Generator - Sine, Square & Sawtooth  
**HacktheChip26 | Level 1**

We are a 3-member team working on the problem:  
**"Waveform Generator: DDS sine, square, and sawtooth wave generation"**  
on a bare FPGA board (Pynq-Z2) with only 2 laptops and **no external DAC**.

### What We Did
Started from TinyDDS and extended it to fully meet the problem statement.

**Main Achievements:**
- Clean generation of **Sine, Square, and Sawtooth** waves using DDS
- Added `wave_select` to switch between the three waveforms
- Used **quarter-wave symmetry** for sine (64-entry LUT) → saves ~75% Block RAM
- Added **first-order Delta-Sigma modulator** so we can generate analog output using only one GPIO pin (no DAC needed)
- Fully working simulation with clean waveforms visible

### Block Diagrams

**1. Overall Architecture**
Clock (100 MHz)
│
▼
Phase Accumulator (28-bit)
│
┌───────────┼───────────┐
│           │           │
Clean Sine    Clean Square   Clean Sawtooth
│           │           │
└───────────┼───────────┘
▼
Wave Select Mux
│
Selected Waveform
│
▼
Delta-Sigma Modulator
│
▼
PDM Output (to GPIO)
text**2. Sine Wave Generation (Quarter-Wave Optimization)**
Phase Accumulator Output
│
▼
Top 2 bits → Quadrant Selector (Q1/Q2/Q3/Q4)
│
Lower bits → Address (64-entry ROM)
│
Forward / Backward addressing + Conditional Negate
│
▼
Clean Sine Wave (8-bit)
text**3. Delta-Sigma Modulator (No DAC Solution)**
Selected Waveform (8-bit)
│
▼
Accumulator (9-bit) += Input
│
▼
MSB (Carry) → PDM Output (1-bit high-speed stream)
(On board: Parasitic capacitance of pin + probe acts as simple low-pass filter)
text### How to Run Simulation (ModelSim)

```tcl
cd "D:/Projects/hackathon-projects/waveform-generator/WaveformDDS/src"

restart -f
log -r *
add wave -r *
do run.do
In the Wave window:

Right-click clean_sine → Format → Analog → Radix Signed
Right-click clean_square & clean_sawtooth → Format → Analog → Radix Unsigned

You will clearly see all three waveforms + the Delta-Sigma bitstream.
Team Work (With Only 2 Laptops)

Two members handled coding, debugging, and simulation
One member (without laptop) did math (sine table generation, FTW calculations), verification, documentation, and slides

We caught and fixed two bugs using property-based testing:

Delta-Sigma convergence issue
Quarter-wave mirroring off-by-one error

Current Status

Simulation fully polished and working
All three waveforms clearly visible
Ready for Pynq-Z2 hardware implementation (next round)

Repository: https://github.com/NITHISH-2006/WaveformDDS (branch: dev-hack)
We took a lightweight open-source base and customized it under tight constraints (time, laptops, no DAC) to solve the exact problem statement. Looking forward to bringing it live on the Pynq-Z2 board!