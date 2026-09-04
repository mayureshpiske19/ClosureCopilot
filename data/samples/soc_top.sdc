# SDC Constraints  --  design: soc_top (top level)
# Generated for ClosureCopilot demo (synthetic data)
# ---------------------------------------------------------------
create_clock -name clk_core -period 1.00 [get_ports clk_core]
create_clock -name clk_cfg  -period 2.50 [get_ports clk_cfg]
create_clock -name clk_120m -period 8.33 [get_ports clk_120m]

# I/O delays
set_input_delay  0.20 -clock clk_core [get_ports din*]
set_output_delay 0.20 -clock clk_core [get_ports dout*]

# NOTE (intentional gaps for demo):
#  - No multicycle path on cfg_reg -> status_reg (config path sampled once per write)
#  - usb_ip block-level clock 'clk_usb' (10.0ns) not reconciled with top clk_120m (8.33ns)
#  - No false_path on test_mode static signal
