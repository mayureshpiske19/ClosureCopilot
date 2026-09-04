// dma_ctrl.sv  --  synthetic demo RTL for ClosureCopilot
module dma_ctrl (
  input  logic        clk,        // <-- always-on clock; intended to be gated
  input  logic        rst_n,
  input  logic        dma_active, // enable that SHOULD gate the clock
  input  logic [31:0] wdata,
  output logic [31:0] rdata
);
  logic [31:0] buf_q;

  // Line ~142 (demo): clock is NOT gated by dma_active.
  // UPF intends clock gating on this block, but enable 'dma_active' is unused here,
  // so every register toggles clk every cycle -> high clock power (see power.rpt).
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) buf_q <= '0;
    else        buf_q <= wdata;      // no 'if (dma_active)' guard -> ICG not inferred
  end

  assign rdata = buf_q;
endmodule
