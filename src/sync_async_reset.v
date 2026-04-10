// sync_async_reset.v
// https://www.intel.com/content/www/us/en/docs/programmable/683082/23-1/use-synchronized-asynchronous-reset.html

module sync_async_reset (
    input  wire clock,
    input  wire reset_n,
    output reg  rst_n
);

    always @(posedge clock or negedge reset_n) begin
        if (!reset_n)
            rst_n <= 1'b0;
        else
            rst_n <= 1'b1;
    end

endmodule