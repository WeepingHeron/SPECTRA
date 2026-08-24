# H09 COTS Flight-and-Test Data Recheck

## Decision

- recheck date: `2026-08-25`
- search question: whether a COTS component has both confirmed satellite use and public numerical radiation-test data that permits a more direct comparison than the current `23LC1024-I/SN` target
- result for like-for-like COTS memory: `NO_STRONGER_PUBLIC_EXACT_MATCH_FOUND`
- result for broader COTS components: `STRONG_FAMILY_LEVEL_CASE_FOUND — Intel Movidius Myriad 2`
- BOM action: retain `Microchip 23LC1024-I/SN` as the current SRAM review target
- assurance decision: `HOLD`

The recheck found no public source package that simultaneously closes exact orderable identity, package, lot/die traceability, satellite use, numerical radiation-test conditions, and mission applicability for a COTS memory compatible with the current SPECTRA SRAM comparison. The current `23LC1024` family remains the best presentation-aligned memory case because ESA confirms its GOMX-4B/CHIMERA flight experiment and a separate open dissertation provides numerical neutron-screening data. The SOIC-versus-PDIP and suffix/lot/die gaps remain.

## Candidate matrix

| Candidate | Satellite evidence | Public radiation evidence | Direct-comparison result |
|---|---|---|---|
| Microchip `23LC1024` | ESA identifies it as a CHIMERA COTS SPI memory flown on GOMX-4B | Am-Be neutron screening reports `(4.10 ± 0.04) × 10^-9 cm²/device` for a PDIP family-level article | Keep as reference; approved `/I/SN` is SOIC and exact test suffix/lot/die is unresolved |
| Cypress `FM25W256` | ESA identifies it as a CHIMERA flight memory | No public numerical report tied to the flown/tested exact article was found in the recheck | Do not replace target |
| onsemi `LE25U40CMC` | ESA identifies it as a CHIMERA flight memory | No public numerical report tied to the flown/tested exact article was found in the recheck | Do not replace target |
| onsemi `N25S830H` | ESA identifies it as a CHIMERA flight memory | No public numerical report tied to the flown/tested exact article was found in the recheck | Do not replace target |
| Intel Movidius `Myriad 2` VPU | ESA confirms Φsat-1 launch and successful in-orbit AI processing powered by Myriad 2 | The primary IEEE paper reports TID/SEE characterization; the NSREC 2020 data-workshop program identifies five sessions spanning Co-60, proton and heavy-ion tests plus Φsat-1 flight data | Strong broader COTS case, but not a drop-in SRAM comparison |

## Why Myriad 2 is not the new BOM target

Myriad 2 is a stronger public **system story**: an ordinary commercial AI/vision processor was radiation-characterized and then performed operational cloud-image classification in orbit. The published derisk results include functional survival through `49 krad(Si)` TID and no confirmed latch-up at the reported `8.8 MeV·cm²/mg` test point, with additional memory- and function-level cross sections in the source paper.

It is nevertheless unsuitable as an immediate replacement for `23LC1024-I/SN`:

- the current SPECTRA Core comparison expects a simple memory-device cross section, while Myriad 2 is a multi-core SoC with DDR, caches, CMX memory, interfaces and functional-event modes;
- a single device-level synthetic SEU input cannot faithfully represent its multiple memory and SEFI cross sections;
- the public ESA mission pages name the Myriad 2 family but do not close orderable variant, package, lot, die revision or board-to-test-article identity;
- changing to Myriad 2 would change the approved component role from external SRAM to onboard AI accelerator and require a new evidence/applicability model, not merely a better fixture value.

The Myriad 2 case should be retained as a presentation/Q&A example of the real COTS qualification pathway: `commercial component → radiation characterization → hardware/software mitigation → in-orbit demonstration`. It must not be used to validate the current SRAM result numerically.

## Sources checked

- ESA CHIMERA Board: <https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Onboard_Computers_and_Data_Handling/CHIMERA_Board>
- ESA Φsat-1/Φsat-2 mission report: <https://www.esa.int/Applications/Observing_the_Earth/Phsat/Next_artificial_intelligence_mission_selected>
- ESA ADCSS 2020 Φsat-1 in-orbit result: <https://indico.esa.int/event/338/contributions/5692/>
- ESA Myriad 2 derisk activity: <https://nebula.esa.int/content/de-risk-assessment-space-qualification-and-reference-design-myriad2-video-processor>
- G. Furano et al., *Towards the Use of Artificial Intelligence on the Edge in Space Systems: Challenges and Opportunities*, DOI `10.1109/MAES.2020.3008468`
- IEEE NSREC 2020 Radiation Effects Data Workshop, DW-2: *Total Dose and SEE Test of Intel Movidius Myriad2 VPU and First Flight Data*

## Next engineering action

Keep the published `23LC1024` screening as a non-decision reference and continue implementing the evidence comparison path without changing the Core physical claims. A direct validation attempt remains blocked until a source binds the approved orderable target to package, lot/die, test conditions and a mission-aligned environment.
