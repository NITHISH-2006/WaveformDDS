# ============================================================
# Wave window configuration for DDS Waveform Generator
# ============================================================

config wave -signalnamewidth 1

# --- Control signals ---
add wave sim:/testbench/clk
add wave sim:/testbench/rst_n
add wave sim:/testbench/wave_select

# --- Clean Waveforms (Always Visible - This is what judges want to see) ---
add wave -format analog -min -128 -max 127 -height 100 -radix signed \
    sim:/testbench/inst_tt_um_tinydds/inst_dds_top/inst_dds/clean_sine

add wave -format analog -min 0 -max 255 -height 80 -radix unsigned \
    sim:/testbench/inst_tt_um_tinydds/inst_dds_top/inst_dds/clean_square

add wave -format analog -min 0 -max 255 -height 80 -radix unsigned \
    sim:/testbench/inst_tt_um_tinydds/inst_dds_top/inst_dds/clean_sawtooth

# --- Selected Output (follows wave_select) ---
add wave -format analog -min -128 -max 127 -height 100 -radix signed \
    sim:/testbench/inst_tt_um_tinydds/inst_dds_top/inst_dds/dds_output

# --- Delta-Sigma PDM Output ---
add wave sim:/testbench/inst_tt_um_tinydds/inst_dds_top/pdm_out

# --- Optional Internal Signals for Debugging ---
add wave sim:/testbench/inst_tt_um_tinydds/inst_dds_top/inst_dds/*

# ============================================================
# Run the simulation
# ============================================================
run 20 us