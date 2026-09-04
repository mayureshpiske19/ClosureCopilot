# Global PPA Knowledge Base — Power

## Clock power dominated by ungated registers
If a block's clock power is a large fraction of its total, and UPF intends clock gating,
the gating enable is likely not wired in RTL, so the synthesis tool cannot infer an ICG.

- **Root cause**: enable signal exists but the `always_ff` has no `if (enable)` guard.
- **Fix in RTL**: guard the register update with the activity enable so an integrated
  clock-gating (ICG) cell is inferred:
```systemverilog
always_ff @(posedge clk) if (enable) q <= d;   // ICG inferred
```
- **Verify against UPF**: the block's `set_clock_gating_style` / gating intent should now
  be realized. No SDC change needed. Trade-off: large clock/dynamic power reduction,
  negligible area/timing cost.

## Static vs dynamic vs leakage
- **Switching (dynamic)**: reduce toggling — operand isolation, clock gating, avoid
  redundant recomputation.
- **Internal**: cell input transitions; often improves with gating/isolation.
- **Leakage (static)**: use higher-Vt cells, power gating (UPF power domains + isolation
  + retention), reduce always-on area.
- **Clock**: gate unused clocks; check ICG coverage vs opportunities in synth log.
