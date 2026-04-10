# DDS Waveform Generator – Sine, Square & Sawtooth  
**HacktheChip26 | Level 1**  
**Team: Photon**

### What We Built
We were given the task to create a **Direct Digital Synthesis (DDS)** waveform generator that can produce **Sine, Square, and Sawtooth** waves on the Pynq-Z2 board. Since we only had 2 laptops among 3 members and no external DAC, we had to be smart with our approach.

We started with the open-source TinyDDS project and spent the whole day modifying it to fully match the problem statement.

### Key Things We Added / Improved
- Proper `wave_select` input so we can switch between Sine, Square, and Sawtooth
- Quarter-wave symmetry for the sine LUT (reduced from 256 to 64 entries → ~75% BRAM saving)
- Three clean outputs: `clean_sine`, `clean_square`, `clean_sawtooth` (always visible in simulation)
- First-order Delta-Sigma modulator to generate analog-like signal using only one GPIO pin (no DAC needed)
- Fixed two bugs using property-based testing (Delta-Sigma convergence and quarter-wave mirroring)
- Clean testbench and `run.do` that shows all three waveforms nicely in ModelSim

### Current Status (as of 10th April 2026)
- Simulation is working well in ModelSim
- All 5 property tests are passing
- We can clearly see clean Sine, Square, and Sawtooth waveforms + the Delta-Sigma PDM output
- Design is ready to be synthesized and tested on the Pynq-Z2 board

### How to Run Simulation (ModelSim)

1. Open ModelSim
2. Go to the src folder:
   ```tcl
   cd "D:/Projects/hackathon-projects/waveform-generator/WaveformDDS/src"

3. Run:
  tclrestart -f
  log -r *
  add wave -r *
  do run.do
In the wave window you will see:

Clean Sine wave
Clean Square wave
Clean Sawtooth wave
Selected output (follows wave_select)
Delta-Sigma PDM bitstream

Block Diagrams
Overall Flow:
textClock → Phase Accumulator → [Clean Sine | Clean Square | Clean Sawtooth] 
                          → Wave Select Mux → Selected Waveform 
                          → Delta-Sigma Modulator → PDM Output (GPIO)
Sine Wave Part (Quarter-Wave):
Phase bits → Quadrant detection → Address adjustment + negate → 64-entry ROM → Clean Sine
What We Learned Today

How DDS actually works (phase accumulator + LUT)
Quarter-wave symmetry trick to save resources
Delta-Sigma modulation for DAC-less output
Importance of property testing (it caught two real bugs!)
Working as a team with limited laptops

Next Steps (Level 2)

Synthesize the design in Vivado/Quartus for Pynq-Z2
Generate bitstream
Test real output on GPIO pin using oscilloscope
Improve control using Python on Pynq if time permits

Repository
https://github.com/NITHISH-2006/WaveformDDS (dev-hack branch)
We started this project today from scratch and managed to get a working simulation with all three waveforms + Delta-Sigma in one day. It was intense but we learned a lot.
— Team Photon