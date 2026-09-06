# BZP Airbridge ESP32-C3 + CC1101 Controller Case

A compact, two-piece enclosure for **BZP Airbridge**, a local RF remote-control bridge built around an ESP32-C3 Super Mini and a CC1101 radio module with an SMA antenna.

The project started as a way to bring a Vornado fan into Home Assistant. The Remote Builder beta also lets you create your own button layouts, then learn each button from a compatible RF remote.

## What is included

- Case base and removable top.
- The MakerWorld print profile/3MF supplied with this listing.
- Open-source firmware, wiring illustration, setup instructions, and Home Assistant example on GitHub.

## What Airbridge can do

- Build up to four custom remotes sharing eight custom buttons.
- Name, arrange, and assign icons to buttons before learning them.
- Learn individual commands with a listening animation and save/discard controls.
- Back up and restore custom remote layouts and learned commands privately.
- Send commands from the local settings page or Home Assistant.
- Keep the original Vornado power and speed controls separate from custom remotes.

## Electronics and parts

The case is intended for the specific boards used in this project:

- SATUY ESP32-C3 Super Mini — ASIN B0GGB1L8N5. One board is needed; the linked listing is a multipack.
- AOICRIE CC1101 radio module with SMA antenna — ASIN B0D2TM5RY2. One module is needed; the linked listing is a multipack.
- Suitable insulated hookup wire and USB-C power cable.

**Parts used in the project:** [Below Zero Productions — Gear We Use & Recommend](https://www.belowz.com/gear/)

The parts page contains Amazon affiliate links. As an Amazon Associate I earn from qualifying purchases.

**Firmware, wiring, setup, and source:** [BZP Airbridge on GitHub](https://github.com/BZPJoe/bzp-airbridge)

## Before printing and assembly

Review the supplied 3MF profile and slicer preview for your printer and material. Board revisions can differ, so check connector access and fit before final assembly. Disconnect USB while wiring. Power the CC1101 from 3.3 V, not 5 V, and keep wiring clear of the ESP32 antenna. Attach the SMA antenna before transmitting.

## Compatibility notes

This is not a universal remote. The current firmware uses a fixed **433.937 MHz ASK/OOK** profile. Other frequencies, infrared, Bluetooth remotes, and rolling-code systems are not supported by this profile. New remote compatibility requires testing. The ESP32-C3 uses 2.4 GHz Wi-Fi.

Home Assistant fan state is estimated from commands, not reported by the fan. GitHub-based automatic firmware installation is not implemented in this beta; ESPHome OTA is available separately.

This is an independent DIY project, not affiliated with or endorsed by Vornado.
