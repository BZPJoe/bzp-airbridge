# Physical remote observation (0.2.1 beta)

The receiver now compares incoming frames with the three saved fan commands outside learning mode. Matching uses the full signed pulse sequence with 25% + 80 microseconds tolerance, excluding the trailing receiver idle gap. Ambiguous matches are rejected. Repeated copies of the same command within 350 ms of the preceding copy count once. Holding a button is treated as one press until a 350 ms gap; rapid same-button presses may merge. This conservative behavior needs validation with the actual remote.

The diagnostic Observed command sensor reports sequence:source:slot. Source is rx (physical remote) or tx (completed bridge replay); slots 0/1/2 are power/up/down. Starting in 0.2.2, source sync means an explicit settings-page correction; values 0/1/2/3 mean Off/Low/Medium/High. Sync never transmits RF. Background listening never retransmits. Own transmissions and the first 350 ms afterward are excluded. Commands during learning, pending capture review, transmission or radio/Wi-Fi downtime can be missed.

Home Assistant's observer automation updates the existing estimate. The fan-control script already accounts for its own sends, so the automation ignores those tx reports. Direct web/button sends are counted. A physical command during a fan-control sequence stops that sequence and marks the estimate Unsynced. Since 0.2.2, disconnects and sequence gaps retain the last known estimate; reconnect snapshots are ignored. The settings-page **Sync fan state** control and the Home Assistant resync selector can correct an inaccurate estimate.

This is command observation, not appliance feedback. The three-speed model assumes bounded speed steps, speed commands do nothing while off, and power-on resumes the remembered speed. If your fan behaves differently, change the model rather than treating this estimate as fact. Fan-panel changes and missed RF packets remain invisible. Start by setting the resync selector to the actual state, then test power, individual speed presses, rapid presses and held buttons with the physical fan in view.

Recognition has synthetic tests; physical RF acceptance still requires a real remote test after installation. Custom Remote Builder buttons are not assigned fan-state semantics.

## Receive-path diagnostics

`Inspect remote reception` opens a 60-second diagnostic window. It logs saved
frames, raw callback counts and up to six received samples, without changing
saved captures. Keep diagnostic logs private: learned RF codes should not be
published with the project.

`Test receive line` is specific to this project's GDO2-to-GPIO3 wiring. It
temporarily drives GDO2 low/high twelve times, reads GPIO3, then restores the
original radio output configuration. It does not enter transmit mode. Learning
and observation are suppressed during the test. Twelve successful low and high
reads plus a receiver callback verify the digital receive path, not RF reception.

Raw mode disables packet synchronization. In the dual-pin configuration GDO0
is high-impedance while receiving, since the ESP32 RMT transmit pin remains an
output; GDO2 supplies received data independently. GDO0 is automatically the
radio's data input in asynchronous transmit mode.

The receiver bandwidth setter also applies the matching analog settings from
[TI DN022 section 3.2](https://www.ti.com/lit/an/swra215e/swra215e.pdf).
At 203.125 kHz these are FREND1=B6, TEST2=81, TEST1=35 and FIFOTHR bit 6=1.
The OOK AGC starting point is 03/00/91, with frequency compensation disabled.
These are documented starting settings, not a substitute for over-the-air
acceptance testing at the installation location. The timed reception diagnostic
also reports min/max RSSI and sampled GPIO3 levels once per second.

`Scan remote reception` is an 18-second receive-only diagnostic: nine two-second
steps from 433.137 to 434.737 MHz using a 650 kHz receive bandwidth and 355 kHz IF.
Record an untouched-remote baseline first, then repeat with the physical remote.
The scan blocks replay and learning, does not update the fan estimate, and restores
this firmware's normal 433.937 MHz / 203 kHz / 153 kHz IF profile automatically.
No scan setting or received sample is saved to flash. Restarting also restores
the normal configured profile. Background RF energy is not proof of remote reception.
# Temporary USB reception comparisons

These diagnostics are experimental, not a confirmed passive-reception fix.
`Original reception test` restores the published learning-era modem and analog
register values for five minutes, while keeping the shared TX-connected GDO0
high impedance to avoid output contention. Frequency and saved commands are
preserved. All incoming callbacks are counted before the application's validity
checks or observer matching. The normal settings are restored automatically.
This is a controlled comparison, not an exact rollback of the entire firmware.
`USB quiet reception test` records five seconds with Wi-Fi enabled, disables
Wi-Fi for 30 seconds while USB logging continues, then reenables Wi-Fi.
`Reference reception test` snapshots the normal radio configuration, reads
the chip's reset defaults and applies an OOK 270 kHz receive profile adapted
from the [Flipper CC1101 configurations](https://github.com/flipperdevices/flipperzero-firmware/blob/dev/lib/subghz/devices/cc1101_configs.c).
It retains the configured frequency and uses GDO2 for reception. After 90 seconds
it automatically restores the normal configuration. Both tests block replay and
learning, leave saved captures intact, and do not update estimated fan state.
A reboot also restores the normal configured profile. Verify actual fan state
before manually resynchronizing Home Assistant after testing.
