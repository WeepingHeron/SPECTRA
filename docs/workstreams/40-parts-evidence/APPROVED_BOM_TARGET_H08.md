# H08 Approved COTS BOM Review Target

## Decision

- decision date: `2026-08-25`
- approval source: project-owner directive in the active Control Tower task
- approval scope: `SPECTRA_MVP_EXACT_PART_REVIEW_TARGET`
- approved manufacturer: `Microchip Technology`
- approved orderable part number: `23LC1024-I/SN`
- product family: `23LC1024`
- function: 1 Mbit volatile SPI/SDI/SQI serial SRAM used as a COTS memory radiation-experiment target; in a spacecraft design it can provide external working or buffer memory, but it is not nonvolatile storage
- quantity: not part of BOM identity, exact-part approval, shielding, TID, or per-device SEE evidence comparison

This supersedes the earlier same-day TI `5962L1420901VXC` choice, which is a Space/QML-V/RHA CAN transceiver rather than the ordinary COTS memory emphasized in the presentation. The approval fixes the catalog-level part against which evidence candidates are compared. It is not flight-suitability approval, mission applicability approval, test-article/lot identity approval, procurement authorization, or radiation assurance.

## Why this target fits the presentation

- Microchip lists the `23LC1024` as **In Production**, not as a space-qualified or radiation-hardened line.
- The manufacturer datasheet defines it as a 2.5–5.5 V, 1 Mbit serial SRAM with SPI, SDI, and SQI interfaces. The exact suffix `/I/SN` means industrial temperature range and an 8-lead SOIC package.
- ESA identifies `23LC1024` as one of the COTS SPI memories placed on the GOMX-4B CubeSat CHIMERA experiment for in-space monitoring of SEU, MBU, SEFI, and latch-up behavior.
- The supported spacecraft role is therefore **CHIMERA radiation-experiment SRAM device under test**, not a proven operational flight-computer memory and not a radiation-tolerant replacement.

## Primary-source basis

- Microchip product page: <https://www.microchip.com/en-us/product/23LC1024>
  - status `In Production`
  - 2.5–5.5 V, 1 Mbit SPI serial SRAM
- Microchip datasheet: <https://ww1.microchip.com/downloads/en/DeviceDoc/20005142C.pdf>
  - 128K × 8 volatile SRAM; SPI/SDI/SQI; 20 MHz for industrial-temperature variants
  - `/I` = −40 °C to +85 °C; `/SN` = 8-lead plastic SOIC
- ESA CHIMERA Board: <https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Onboard_Computers_and_Data_Handling/CHIMERA_Board>
  - names the base product `23LC1024` among COTS SPI memories installed on the GOMX-4B CubeSat experiment
  - states that the experiment monitors SEUs/MBUs, SEFIs, and latch-ups

ESA does not disclose the flown orderable suffix, lot/date code, die revision, or result set on that page. The manufacturer catalog identity `23LC1024-I/SN` and ESA's family-level flight-experiment identity must remain separate until exact test-article traceability is obtained.

## Quantity separation

`quantity` is removed from the BOM component contract. Part count does not change per-device shielding thickness, TID tolerance, exact identity, or per-device SEE evidence.

System-level SEE event aggregation can still depend on the number of exposed identical devices because the model is proportional to `particle flux × cross section × analysis device count × mission duration`. That count is therefore an explicit simulation-only `analysis_device_count`, not an approved-BOM or procurement quantity. It does not affect the TID/shielding branch.

## Remaining HOLD gates

- ESA flown article's exact suffix, package, lot/date code, and die revision
- public result artifact with test conditions and event-specific measurements
- source artifact manifest and action-specific rights
- TID evidence and mission-specific applicability comparison
- independent destructive-SEE and SEU/MBU coverage required by policy
- independent technical review of an issuable evidence packet

The approved target removes `BOM_APPROVAL_MISSING` only at the catalog review-target layer. It does not create a decision-usable `PART_TEST_EVIDENCE v2` packet, and assurance remains `HOLD`.

## Published experiment reference

A 2024 doctoral dissertation by Mona C. Plettenberg reports an Am-Be neutron screening of Microchip `23LC1024` SRAMs. The tested devices were 8-lead **PDIP** parts with no disclosed orderable suffix, lot, or die revision, so they are not treated as exact matches for the approved `23LC1024-I/SN` 8-lead **SOIC** target.

The screening exposed the devices for 24 hours at 3.3 V and reports an SEU cross section of `(4.10 ± 0.04) × 10^-9 cm²/device` in Figure 5.5(a), with no MCUs observed for the 1 Mbit device in that screening. The same source reports no bit flips or functional degradation during a dynamic 100 kGy X-ray exposure, but SPECTRA does not convert that observation into a `krad(Si)` TID limit because the material basis, dosimetry, parametric criteria, and exact identity are not aligned.

The machine-readable comparison is stored in `references/23lc1024-published-comparison.json`. Its only direct arithmetic is the ratio between the current synthetic cross-section input `1.0 × 10^-6 cm²/device` and the published screening value: approximately `243.9`. This number is **not** an error rate, accuracy score, validation result, or suitability result. The current SPECTRA fixture uses a different synthetic part identity, generic particle flux, and a non-physical `see_exposure_scale`, so the mission event output `0.063072 events/mission` is not directly comparable with the experiment.

Comparison status is therefore `REFERENCE_COMPARISON_AVAILABLE / NOT_COMPARABLE / HOLD`. The reference is useful for showing where the synthetic placeholder sits numerically and for defining the next test conditions, but it cannot replace an exact-part, mission-aligned Evidence Packet.

Primary source: Mona C. Plettenberg, *Effects of Cosmic Radiation on Active Implanted Medical Devices*, DOI `10.22029/jlupub-19623`, Chapter 5.1–5.2 and Figure 5.5(a), CC BY 4.0.
