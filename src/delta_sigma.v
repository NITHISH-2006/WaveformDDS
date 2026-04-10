// delta_sigma.v — First-order Delta-Sigma Modulator
//
// Converts an 8-bit unsigned PCM sample to a 1-bit PDM output stream.
// The average duty cycle of pdm_out converges to data_in/255.
//
// First-order noise-shaping loop:
//   accumulator[8:0] += {1'b0, data_in} - {pdm_out, 8'b0}
//   pdm_out = accumulator[8]  (combinational — MSB of updated accumulator)
//
// On reset, accumulator clears to 0, pdm_out = 0.
// Requirements: 4.1, 4.2, 4.3, 4.5

module delta_sigma (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,   // 8-bit unsigned sample
    output wire       pdm_out    // 1-bit PDM (combinational from accumulator MSB)
);

    reg [8:0] accumulator;

    assign pdm_out = accumulator[8];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            accumulator <= 9'h0;
        else
            accumulator <= accumulator + {1'b0, data_in} - {pdm_out, 8'b0};
    end

endmodule
