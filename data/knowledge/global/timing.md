# Global PPA Knowledge Base — Timing (Performance)

## Root-cause routing for setup violations
A negative-slack (setup) path is NOT always an RTL problem. Diagnose first:

- **Config / quasi-static paths** (registers written once per configuration, mode bits,
  CSR fields sampled rarely): the path is falsely treated as single-cycle. **Fix in
  constraints (SDC)** with `set_multicycle_path`, not RTL.
- **Static / mode signals** (test_mode, scan_enable, strap pins) feeding datapaths:
  add `set_false_path` in SDC.
- **Genuine deep combinational logic** (large multipliers, long adder/XOR chains, high
  logic depth): **fix in RTL** by pipelining, retiming, or restructuring.
- **Wrong / missing clock definition, or block-vs-top clock period mismatch**: **fix in
  constraints** by reconciling `create_clock` and re-budgeting I/O delays. Common at
  IP→top integration (constraint promotion).

## Multicycle path pattern (SDC)
```tcl
set_multicycle_path -setup 2 -from [get_pins <src>*/CK] -to [get_pins <dst>*/D]
set_multicycle_path -hold  1 -from [get_pins <src>*/CK] -to [get_pins <dst>*/D]
```

## Pipeline (RTL) pattern
Insert a pipeline register to split a deep combinational cone across two cycles.
Trade-off: improves timing; adds a small amount of area and dynamic power; adds one
cycle of latency (confirm architecturally acceptable).
