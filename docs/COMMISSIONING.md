# First hardware test

## What is known

The target fan is the Vornado Airbar 4; the manufacturer describes an RF remote. The hardware consists of an ESP32-C3 Super Mini and a CC1101/SMA 433 MHz module.

## What is still unknown

Power replay has been confirmed by the project owner using the current ASK/OOK profile at 433.937 MHz. This does not establish compatibility with every revision or other remotes. Speed behavior and custom-remote appliance playback still require physical testing. A different modulation, rolling code, full-state protocol, or longer frame would require adapting the software.

## Capture procedure

1. Check wiring and confirm startup logs show a healthy CC1101, not an SPI identification failure.
2. Put the original remote roughly 0.5–1 m from the antenna. Start without transmitting from the bridge.
3. Open ESPHome logs. Press Learn power, then briefly press the remote power button once.
4. A structurally valid frame becomes a candidate. This check rejects malformed timing data; it does not identify the sender. Save only when capture coincides with your button press.
5. Repeat the capture several times and compare raw logs before trusting a frame. Cancel unexpected candidates.
6. Save one candidate for each command. Confirm the command-saved indicator becomes active. Wait 65 seconds, reboot, and confirm all three indicators remain active.
7. Test one button at a time. Explicit send requests enable transmission automatically. Watch the actual fan.
8. Current playback uses eight repeats, with no added gap because the saved frame already includes trailing silence. If one press causes multiple changes, measure the original sequence before changing repeats or timing.
9. Test the original remote afterward. Record which fan and remote revisions were tested.

The bridge sends no RF command at startup. Starting a learning window disables transmission. New capture attempts replace only the temporary candidate; a saved command remains until explicitly overwritten by Save capture.

## Capture boundaries

Frames must start with a positive mark, alternate sign, contain 16–512 timings, use individual durations of 50–30,000 microseconds, and total 3–500 ms. Receive idle time is 12 ms. A longer silence ends a capture; multi-frame protocols may need a different idle threshold. Do not stretch timing limits without checking the waveform and memory requirements.

## If nothing works

- If there are no plausible captures: verify GDO2 wiring and investigate frequency/modulation with a suitable RF capture tool.
- If captures appear without remote presses: those may be noise or another 433 MHz device.
- If repeated presses produce changing payloads: investigate addressing, counters, or rolling codes before replay.
- If the fan uses FSK: this OOK learning profile will need a measured FSK configuration or protocol implementation.
- If commands work but the displayed activity seems stale: Bridge activity reports bridge actions only, never fan telemetry.

Keep capture logs private by default; transmitter IDs may identify your remote. Record the successful settings and a sanitized trace before marking Airbar support verified.
