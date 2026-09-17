# Formal / Logical Equivalence Checking (LEC)

LEC proves the synthesized/ECO'd netlist is functionally equivalent to the golden RTL.
When compare points fail, the fix rarely belongs in RTL — it is usually a **setup** issue in
the formal flow, or an *intended* transformation the checker was not told about.

## Clock-gating ECO mismatch
Inserting an integrated clock-gating cell (ICG) during an ECO changes the sequential behavior
at the register's compare point. This is an **intended** change, not an RTL bug. Model the ICG
in the LEC setup (guide the gating cell) instead of editing RTL:
```
# Formality
set_dont_verify_points -type cell {dma_ctrl/ICG_buf_q}
# or model the gating so the compare point matches
guide_clock_gate -gated_reg dma_ctrl/buf_q -enable dma_active
```

## Retiming / register-movement mismatch
Retiming moves a register across combinational logic, so the golden and revised registers no
longer line up 1:1. Enable sequential analysis and provide the moved-register mapping:
```
set_analysis_mode -sequential
add_mapped_points crc_gen/crc_q_reg  crc_gen/crc_q_retimed
```

## Genuine functional mismatch
If neither an intended ECO nor retiming explains the failure, it is a **real RTL bug** — fix the
RTL and re-run LEC. Never blindly `set_dont_verify` a real mismatch.
