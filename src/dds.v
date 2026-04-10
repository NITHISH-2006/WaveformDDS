// dds.v
//
// Direct Digital Synthesis module with quarter-wave sine ROM,
// quadrant reconstruction, and wave_select output mux.
//
// Output frequency: F_out = FTW x F_clk / 2^28
// where F_clk is the system clock frequency.
//
// wave_select encoding:
//   2'b00 = Sine (gain/offset adjusted)
//   2'b01 = Square (MSB of phase accumulator -> 0xFF or 0x00)
//   2'b10 = Sawtooth (upper 8 bits of phase accumulator)
//   2'b11 = PRNG / noise

`default_nettype none

module dds (

    // Clock and reset
    input  wire        clk,
    input  wire        rst_n,

    // Registers
    input  wire [27:0] register_freq0,
    input  wire [27:0] register_freq1,
    input  wire [11:0] register_phase0,
    input  wire [11:0] register_phase1,
    input  wire        fselect,
    input  wire        pselect,
    input  wire [1:0]  register_mode,   // retained for backward compatibility
    input  wire [7:0]  register_gain,
    input  wire signed [7:0]  register_offset,

    // Waveform select (supersedes register_mode for output mux)
    input  wire [1:0]  wave_select,

    // DDS Output (muxed, selected by wave_select)
    output reg [7:0]   dds_output,

    // Clean individual waveform outputs (always active, for simulation visibility)
    output wire [7:0]  clean_sine,
    output wire [7:0]  clean_square,
    output wire [7:0]  clean_sawtooth

);

    /////////////////////////////////////////////////////////////////////////////
    // Phase accumulator ////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    reg [27:0] phase_accumulator;

    always @(posedge clk) begin
        if (!rst_n)
            phase_accumulator <= 0;
        else
            if (fselect == 0)
                phase_accumulator <= phase_accumulator + register_freq0;
            else
                phase_accumulator <= phase_accumulator + register_freq1;
    end

    /////////////////////////////////////////////////////////////////////////////
    // Phase offset /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    wire [11:0] phase_accumulator_trunc;
    reg [11:0] phase_accumulator_post_offset;
    assign phase_accumulator_trunc = phase_accumulator[27:16];

    always @(posedge clk) begin
        if (pselect == 0)
            phase_accumulator_post_offset <= phase_accumulator_trunc + register_phase0;
        else
            phase_accumulator_post_offset <= phase_accumulator_trunc + register_phase1;
    end

    /////////////////////////////////////////////////////////////////////////////
    // Quarter-Wave Sine ROM + Quadrant Reconstruction //////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    reg signed [7:0] sine_quarter_memory [0:63];
    initial begin
        $display("Loading rom.");
        $readmemh("sine_quarter.mem", sine_quarter_memory);
    end

    // Quadrant and address extraction
    wire [1:0] quadrant;
    wire [5:0] rom_addr;
    assign quadrant = phase_accumulator_post_offset[11:10];
    assign rom_addr = phase_accumulator_post_offset[9:4];

    // Mirrored address: quadrants 01 and 11 use (64 - rom_addr), clamped to 63 when rom_addr=0
    // This correctly maps Q1/Q3 to the descending half of the quarter-wave ROM.
    wire [5:0] effective_addr;
    assign effective_addr = (quadrant[0]) ? (rom_addr ? (6'd64 - rom_addr) : 6'd63) : rom_addr;

    // ROM output
    wire signed [7:0] rom_data;
    assign rom_data = sine_quarter_memory[effective_addr];

    reg signed [7:0] sine_data;

    // Register reconstructed sine on rising clock edge
    // Quadrants 10 and 11 negate via 2's complement: ~rom_data + 1
    always @(posedge clk) begin
        if (quadrant[1])
            sine_data <= (~rom_data + 8'sd1);
        else
            sine_data <= rom_data;
    end

    /////////////////////////////////////////////////////////////////////////////
    // Gain & Offset Stage //////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    reg signed [15:0] sine_data_post_gain;
    wire signed [7:0] sine_data_post_gain2 = sine_data_post_gain[15:8];
    reg signed [8:0] sine_data_post_offset;
    reg signed [7:0] sine_data_post_offset_satured;
    reg saturating;

    // Gain and offset
    always @(posedge clk) begin
        sine_data_post_gain   <= register_gain * sine_data;
        sine_data_post_offset <= sine_data_post_gain2 + register_offset;
    end

    // Saturation
    always @(posedge clk) begin
        if (rst_n == 0) begin
            saturating <= 0;
        end
        else begin

            // Saturation on the maximum value : +127
            if (sine_data_post_offset > 127) begin
                sine_data_post_offset_satured = 127;
                saturating = 1;
            end

            // Saturation on the minimum value : -128
            else if (sine_data_post_offset < -128) begin
                sine_data_post_offset_satured = -128;
                saturating = 1;
            end

            // No saturation : we can safely copy the data
            else begin
                sine_data_post_offset_satured = sine_data_post_offset[7:0];
                saturating = 0;
            end

        end
    end

    /////////////////////////////////////////////////////////////////////////////
    // Pseudorandom Number Generator (PRNG) /////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    wire [7:0] prng_data;

    prng inst_prng (

        // Clock and reset
        .clk(clk),
        .rst_n(rst_n),

        // Output
        .prng_data(prng_data)

    );

    /////////////////////////////////////////////////////////////////////////////
    // Clean individual waveform outputs (always active) ////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    assign clean_sine     = sine_data_post_offset_satured;
    assign clean_square   = {8{phase_accumulator[27]}};
    assign clean_sawtooth = phase_accumulator_trunc[11:4];

    /////////////////////////////////////////////////////////////////////////////
    // Mux output data //////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    // wave_select encoding:
    //   2'b00 = Sine (gain/offset adjusted)
    //   2'b01 = Square wave (phase_accumulator MSB -> 0xFF or 0x00)
    //   2'b10 = Sawtooth (upper 8 bits of phase accumulator)
    //   2'b11 = PRNG / noise
    always @(*) begin
        case (wave_select)
            2'b00:   dds_output = sine_data_post_offset_satured;
            2'b01:   dds_output = {8{phase_accumulator[27]}};
            2'b10:   dds_output = phase_accumulator_trunc[11:4];
            default: dds_output = prng_data;
        endcase
    end

endmodule
