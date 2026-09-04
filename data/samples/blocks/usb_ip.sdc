# Block-level SDC  --  IP: usb_ip  (as delivered by IP team)
# Generated for ClosureCopilot demo (synthetic data)
create_clock -name clk_usb -period 10.00 [get_ports clk_usb]
set_input_delay  2.00 -clock clk_usb [get_ports usb_din*]
set_output_delay 2.00 -clock clk_usb [get_ports usb_dout*]
set_false_path -from [get_ports usb_test_mode]
set_multicycle_path -setup 2 -from [get_pins cfg_usb_reg*/CK] -to [get_pins usb_status_reg*/D]
