# Global PPA Knowledge Base — Area & Synthesis

## Unmapped cells
Operator has no matching library cell (e.g. XOR4, wide MUX). Fix options:
- **Synthesis-setup fix**: add/point to the correct target `.lib` that contains the cell,
  or allow the tool to decompose the operator.
- **RTL fix**: rewrite the operator using primitives the library supports (e.g. build a
  balanced XOR tree from XOR2), which also helps area/timing on congested blocks.

## Inferred latches
Caused by incomplete `case`/`if` (a signal not assigned on every path in an `always_comb`).
- **Fix in RTL**: add a `default:` in the case, or a preceding default assignment, so the
  signal is always assigned. Latches are almost never intended in synchronous RTL.

## High utilization / congestion
A block over ~85% utilization risks routing congestion. Large combinational XOR/adder
trees (e.g. crc_gen) are typical offenders.
- **RTL fix**: pipeline or restructure the tree; share logic.
- Trade-off: pipelining lowers congestion and improves timing; adds latency + minor area.

## Missing clock-gating opportunities
Synth log reporting `opportunities detected > cells inserted` means some enables aren't
visible to the tool — usually because the RTL doesn't express the enable as a register
guard. Fix in RTL (see power.md).
