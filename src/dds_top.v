// dds_top.v
// Top module of our design : it contains the SPI Slave interface, the DDS module,
// and the Delta-Sigma modulator for DAC-less analog output.

`default_nettype none

module dds_top (
    
    // Clock and reset
    input  wire        clk,
    input  wire        rst_n,

    // SPI Interface
    input  wire        spi_clock,
    input  wire        spi_cs_n,
    input  wire        spi_mosi,

    // Inputs
    input  wire        fselect,
    input  wire        pselect,

    // Waveform select (2'b00=sine, 2'b01=square, 2'b10=sawtooth, 2'b11=PRNG)
    input  wire [1:0]  wave_select,

    // DDS output (8-bit signed waveform sample)
    output wire [7:0]  dds_output,

    // Clean individual waveform outputs (for simulation visibility)
    output wire [7:0]  clean_sine,
    output wire [7:0]  clean_square,
    output wire [7:0]  clean_sawtooth,

    // Delta-Sigma PDM output (1-bit)
    output wire        pdm_out

);

    /////////////////////////////////////////////////////////////////////////////
    // Wires ////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    // SPI Registers
    wire [27:0] register_freq0;
    wire [27:0] register_freq1;
    wire [11:0] register_phase0;
    wire [11:0] register_phase1;
    wire [1:0]  register_mode;
    wire [7:0]  register_gain;
    wire [7:0]  register_offset;

    // Internal DDS output wire (feeds both module output and delta_sigma input)
    wire [7:0]  dds_output_wire;
    assign dds_output = dds_output_wire;

    /////////////////////////////////////////////////////////////////////////////
    // SPI Slave Interface //////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    spi_slave_interface inst_spi_slave_interface (
        
        // Clock and reset
        .clk(clk),
        .rst_n(rst_n),
        
        // SPI Interface
        .spi_clock(spi_clock),
        .spi_cs_n(spi_cs_n),
        .spi_mosi(spi_mosi),
        
        // Registers
        .register_freq0(register_freq0),
        .register_freq1(register_freq1),
        .register_phase0(register_phase0),
        .register_phase1(register_phase1),
        .register_mode(register_mode),
        .register_gain(register_gain),
        .register_offset(register_offset)

    );

    /////////////////////////////////////////////////////////////////////////////
    // DDS //////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    dds inst_dds (
    
        // Clock and reset
        .clk(clk),
        .rst_n(rst_n),
        
        // Registers
        .register_freq0(register_freq0),
        .register_freq1(register_freq1),
        .register_phase0(register_phase0),
        .register_phase1(register_phase1),
        .fselect(fselect),
        .pselect(pselect),
        .register_mode(register_mode),
        .register_gain(register_gain),
        .register_offset(register_offset),

        // Waveform select
        .wave_select(wave_select),

        // DDS Output
        .dds_output(dds_output_wire),

        // Clean individual outputs
        .clean_sine(clean_sine),
        .clean_square(clean_square),
        .clean_sawtooth(clean_sawtooth)

    );

    /////////////////////////////////////////////////////////////////////////////
    // Delta-Sigma Modulator ////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    delta_sigma inst_delta_sigma (

        .clk(clk),
        .rst_n(rst_n),
        .data_in(dds_output_wire),
        .pdm_out(pdm_out)

    );

endmodule
