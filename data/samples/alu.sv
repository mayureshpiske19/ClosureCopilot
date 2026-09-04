// alu.sv  --  synthetic demo RTL for ClosureCopilot
module alu (
  input  logic         clk_core,
  input  logic         rst_n,
  input  logic [15:0]  opa,
  input  logic [15:0]  opb,
  input  logic [3:0]   op,
  output logic [15:0]  res
);
  logic [15:0] opa_q, opb_q, res_q;

  always_ff @(posedge clk_core or negedge rst_n) begin
    if (!rst_n) begin opa_q <= '0; opb_q <= '0; end
    else        begin opa_q <= opa; opb_q <= opb; end
  end

  // Line ~210 (demo): deep combinational cone, single cycle, no pipeline register
  always_comb begin
    unique case (op)
      4'h0: res = opa_q + opb_q;
      4'h1: res = opa_q - opb_q;
      4'h2: res = opa_q * opb_q;              // <-- deep multiply feeds long XOR/add chain
      4'h3: res = (opa_q * opb_q) ^ (opa_q + opb_q) ^ (opb_q << 3);
      default: res = opa_q ^ opb_q;
    endcase
  end

  always_ff @(posedge clk_core) res_q <= res;
endmodule
