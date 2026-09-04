# Block-level SDC  --  IP: dma_ip  (as delivered by IP team)
# Generated for ClosureCopilot demo (synthetic data)
create_clock -name clk_dma -period 2.00 [get_ports clk_dma]
set_input_delay  0.40 -clock clk_dma [get_ports dma_din*]
set_output_delay 0.40 -clock clk_dma [get_ports dma_dout*]
