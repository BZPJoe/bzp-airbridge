# Setup and recovery

Disconnect USB before wiring. CC1101 VCC goes to **3V3, never 5V**. Attach the correct SMA antenna before transmitting. Keep the ESP32 antenna clear of the radio board, metal, and bundled wires.

Use Python 3.12 and the pinned requirements. Copy firmware/secrets.example.yaml to firmware/secrets.yaml and replace all values with your own. Keep this file out of version control. ESP32-C3 requires 2.4 GHz Wi-Fi, not 5 GHz.

```sh
python tools/build_ui.py
esphome run firmware/airbridge.yaml
# Subsequent wireless update:
esphome upload firmware/airbridge.yaml --device bzp-airbridge.local
```

First installation uses USB. Wait for upload success and reconnect; slow Wi-Fi can take several minutes. Never distribute binaries compiled with personal credentials.

Open http://bzp-airbridge.local or the router-assigned local IP. The HTTP page intentionally has no sign-in: trusted LAN only, no internet port forwarding. Native ESPHome API encryption is separate from HTTP.

The Wi-Fi form tests the new network before saving, with a 45-second rollback. Credentials are POSTed, not placed in URLs. HTTP still requires a trusted network.

## Recovery and preservation

Identify BOOT and RESET/RST using PCB markings. Holding BOOT while tapping RESET then releasing BOOT permits USB recovery. A normal reset does not erase stored captures.

v0.2 keeps the original power/up/down globals and names; custom remotes use separate versioned NVS storage. Do not erase flash or change partition layouts when upgrading. Export custom backups first.

Legacy captures retain the delayed preference write: wait 65 seconds after saving before removing power. Custom layout/capture success is reported after NVS commit. Custom backups exclude the original Vornado captures.
