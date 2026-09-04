# Top-level SDC  --  design: soc_top  (integrator's current top constraints)
# Generated for ClosureCopilot demo (synthetic data)
create_clock -name clk_core -period 1.00  [get_ports clk_core]
create_clock -name clk_cfg  -period 2.50  [get_ports clk_cfg]
create_clock -name clk_120m -period 8.33  [get_ports clk_120m]
create_clock -name clk_dma  -period 2.50  [get_ports clk_dma]

# usb_ip is driven at top by clk_120m (8.33ns) but the IP block SDC assumes clk_usb 10.0ns.
# dma_ip block clock clk_dma constrained at 2.00ns in block, but top defines 2.50ns (relaxed).
# usb_ip block false_path on usb_test_mode NOT promoted to top.
# usb_ip block multicycle on cfg_usb_reg -> usb_status_reg NOT promoted to top.
