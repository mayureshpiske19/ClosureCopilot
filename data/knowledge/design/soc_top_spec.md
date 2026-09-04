# Design Context Memory — soc_top (demo chip)

## Overview
`soc_top` is a small demo SoC used for the ClosureCopilot hackathon prototype. It contains
a compute core (alu, pipe_stage3), a DMA controller (dma_ctrl), a USB IP (usb_ip), a CRC
generator (crc_gen), SPI/SPI-config blocks, and a configuration controller (cfg_ctrl).

## Clocking
- `clk_core` (1.00 ns / 1 GHz): main compute (alu, pipe_stage3, spi_ctrl).
- `clk_cfg`  (2.50 ns): configuration/CSR logic (cfg_ctrl). CSR/config registers are
  written **once per configuration write** and are quasi-static between writes.
- `clk_usb`  (block-level 10.0 ns) driven at top by `clk_120m` (8.33 ns).

## Power intent
- `dma_ctrl` sits in switchable domain **PD_DMA** and is **intended to be clock-gated** by
  its `dma_active` enable. Leakage saved via power gating when idle.
- `usb_ip` in **PD_USB**; state registers are expected to retain across power-down.

## Known design intent notes (authoritative for analysis)
- The path `cfg_reg -> status_reg` is a **multicycle configuration path** by design
  (sampled once per write); a single-cycle setup check is a false failure.
- `test_mode` is a **static strap** signal; paths from it are false paths.
- `crc_gen` is a wide XOR-tree block; some area/congestion is expected but should be
  pipelined if it limits timing.
