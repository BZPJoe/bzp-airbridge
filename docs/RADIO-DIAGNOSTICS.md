# Radio diagnostics

The local `cc1101` component is based on ESPHome 2026.8.2's component, with read-only register diagnostics added to its public interface. Upstream: https://github.com/esphome/esphome/tree/2026.8.2/esphome/components/cc1101 (ESPHome C++ runtime, GPLv3; see the included upstream license).

`Read radio diagnostics` is a diagnostic button exposed through ESPHome. Pressing it reads PARTNUM, VERSION, MARCSTATE, PKTCTRL0 and FSCAL1 and logs the saved Power pulse sequence without altering it. Run it when the bridge is idle.

Replay now enters TX before handing pulses to the transmitter. If MARCSTATE is not TX (`0x13`), it aborts replay and reports an error. After pulse completion, it checks RX (`0x0D`). Successful state transitions and pulse completion do not prove RF reception by the fan.

Stored frame IDs and serialization are unchanged. Raw frame timings can identify a remote's command; keep diagnostic logs private.

Live diagnostic finding: the saved Power frame contains 50 signed durations and ends in a -12000 us receiver idle period. The former extra 12 ms repeat wait doubled this separation. Replay now preserves the captured trailing gap and adds no extra repeat delay. Hardware fan response remains the final acceptance test.

Further live readback: PA=00,40; FREND0=11; MDMCFG2=32; IOCFG0=0D; FREQ=10B09C. GPIO1 output selection is 0x33 (RMT source 51), with GPIO1 output enabled. This rules out a zeroed OOK power table and a detached RMT route at the time of reading, but does not measure radiated RF.

The AIRBAR FCC grant lists 433.937 MHz: https://fccid.io/WOT-AIRBAR . The radio remains at that carrier. An eight-repeat playback trial replaces the former three repeats to test the longer burst envelope observed from the original remote. This is experimental until the user confirms fan response; the stored frame is unchanged.
