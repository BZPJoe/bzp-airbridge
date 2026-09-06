# Wiring BZP Airbridge

Disconnect USB while wiring. Attach the included SMA antenna before transmitting.

The illustration shows component-side board outlines: ESP32 USB-C at the top,
CC1101 SMA at the bottom. ESP32 pad positions follow the Super Mini photo.
The radio's two-row header follows the matching E07-M1101D-SMA component-side
drawing: upper row left-to-right 7, 5, 3, 1; lower row 8, 6, 4, 2.
Pin 1 is the square GND pad. Confirm the marking on your radio revision.
Wire crossings without a terminal dot are not electrical junctions.

| ESP32-C3 label | CC1101 signal | Role |
|---|---|---|
| 3V3 | VCC | 3.3 V supply |
| GND | GND | Shared ground |
| GPIO4 | SCK / SCLK | SPI clock |
| GPIO5 | SO / MISO | Radio → controller |
| GPIO6 | SI / MOSI | Controller → radio |
| GPIO7 | CSN / CS | SPI chip select |
| GPIO1 | GDO0 | Raw transmit pulses |
| GPIO3 | GDO2 | Raw receive pulses |

This uses separate receive and transmit GPIOs. GDO0 belongs to the transmitter component and GDO2 belongs to the receiver component. Do not also assign GDO0 to the CC1101 configuration in this dual-pin setup.

GPIO2, GPIO8, and GPIO9 are avoided for this wiring. GPIO18/19 are left for native USB. Connect by board labels, not by a generic drawing's physical pin order. CC1101 board revisions can rotate or mirror their 2×4 headers.

Keep wires short. Power the assembly through the ESP32's USB-C connector. Use the existing case's downward-facing header clearance; permanent locating posts and retention pads are part of the enclosure. No sacrificial supports are included.

Reference: https://esphome.io/components/cc1101/#integration-with-remote-receivertransmitter
