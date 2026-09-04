# Global PPA Knowledge Base — UPF & Constraint Promotion

## UPF isolation
Outputs of a switchable power domain that cross into an always-on domain must be isolated,
otherwise they float (X) when the domain is powered down.
```tcl
set_isolation iso_<pd> -domain <PD> -isolation_power_net VDD_AO \
    -clamp_value 0 -applies_to outputs
set_isolation_control iso_<pd> -domain <PD> -isolation_signal <iso_en> -isolation_sense high
```

## UPF retention
State registers that must survive power-down need a retention strategy:
```tcl
set_retention ret_<pd> -domain <PD> -retention_power_net VDD_AO
set_retention_control ret_<pd> -domain <PD> -save_signal  <save> -restore_signal <restore>
```

## Constraint promotion (IP → subsystem → top)
Block-level SDC must be reconciled when integrated at top:
- **Clock reconciliation**: an IP that defines `create_clock -period 10 clk_usb` but is
  driven at top by `clk_120m` (8.33 ns) has an inconsistent budget. Promote by mapping the
  IP clock to the real top clock and re-deriving I/O delay budgets.
- **I/O delay budgeting**: convert block boundary timing into top-level `set_input_delay`/
  `set_output_delay` against the true top clock.
- **Exceptions**: promote block false/multicycle paths that remain valid at top.
