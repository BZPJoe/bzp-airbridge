# ESP32-C3 + AOICRIE CC1101 snap-fit enclosure

**Earlier generated prototype.** For the current owner-supplied case files, see [base and top](user-supplied/README.md). The instructions and measurements below apply only to this older design.

This enclosure is for two separate boards:

- **Controller:** SATUY ESP32-C3 Super Mini, Amazon ASIN **B0GGB1L8N5**
- **Radio/antenna assembly:** AOICRIE 433 MHz CC1101 blue PCB with gold SMA connector and the supplied black antenna, Amazon ASIN **B0D2TM5RY2**

The case body is 36.0 × 43.5 × 25.0 mm when closed, excluding the exposed SMA connector and screw-on antenna. The two low-profile side snap arms make the maximum width 38.0 mm. It uses no enclosure screws and no board screws.

## Hardware dimensions used

| Part | Design envelope |
|---|---|
| SATUY ESP32-C3 PCB | 22.5 × 18.0 mm; USB-C centered on the 18 mm end; two 8-pin rows at 2.54 mm pitch |
| AOICRIE/CC1101 radio PCB | 28.0 × 15.0 × 1.2 mm; 2×4 header on one end; SMA centered on the opposite end |
| CC1101 mounting holes | 3.0 mm diameter; hole centerline 10.0 mm from the SMA-side PCB edge |
| SMA connector | 6.2 mm diameter × 9.6 mm long beyond the PCB |
| Supplied black antenna | approximately 50 mm long × 7 mm diameter |

The AOICRIE Amazon dimension graphic repeats “28 mm” on both PCB axes, but its photographed board is rectangular. The official EBYTE mechanical drawing for the visually matching E07-M1101D-SMA layout gives the consistent dimensions: **28 × 15 mm**, with the same SMA connector, 2×4 header, hole pattern, and pin arrangement. Those dimensions—not 28 × 28 mm—were used here.

## Print settings

- Print the base upright with the open side facing up.
- Print the lid exactly as supplied: its smooth outside face goes on the bed.
- 0.4 mm nozzle, 0.20 mm layers, three walls, and 15–25% infill are suitable.
- PETG is preferred for the repeated-flex snap arms; PLA should also work if the lid is not removed frequently.
- **Turn slicer-generated supports off.** Every feature is oriented to print without support material. A brim is optional.
- The lid has 0.25 mm skirt clearance per side and two flexible snap arms. Do not scale only one part unless a test print shows your printer needs compensation.

## Assembly

1. Wire and test the electronics before putting them in the enclosure. Both boards use 3.3 V logic; do not feed the CC1101 from 5 V.
2. The enclosure provides 15 mm below each PCB for downward-facing header pins and female Dupont housings. On the ESP32-C3, solder the supplied headers with the long pins facing down, or solder short insulated wires directly to the board.
3. Connect the inter-board wires before seating the boards. Route them underneath and through the open center channel, keeping the bundle away from the ESP32's onboard antenna end.
4. Insert the CC1101's gold SMA connector through the round opening. Lower its two 3 mm mounting holes onto the locating pins. Its 2×4 electrical header faces the opposite wall. No screws are used.
5. Insert the ESP32-C3's USB-C connector through the rectangular opening and lower the PCB between its locating guides. This board has no mounting holes, so the guides—not screws—keep it positioned.
6. Screw the supplied black antenna onto the SMA connector outside the case, finger-tight only.
7. Align the lid and press both long sides evenly until the two exterior latches click into their wall pockets. To remove it, flex one snap arm slightly outward while lifting at the shallow front-edge notch, then release the other side.

Do not force a board that differs visibly from the specified products. Clone “ESP32-C3 Super Mini” and CC1101 boards can use different PCB outlines or connector positions. The included parametric source keeps the important dimensions near the top of the file if a measured adjustment is needed.

## Included files

- `vornado_rf_enclosure_base.stl` — print-ready base
- `vornado_rf_enclosure_lid.stl` — print-ready removable lid
- `vornado_rf_enclosure_source.py` — editable parametric CAD source
- `vornado_rf_enclosure_preview.png` — exploded fit reference
- `mesh_validation.txt` — closed-mesh and interference-check report

To regenerate the STLs from the source, install Python packages `numpy`, `trimesh`, `manifold3d`, and `matplotlib`, then run:

```text
python3 vornado_rf_enclosure_source.py --output-dir .
```
