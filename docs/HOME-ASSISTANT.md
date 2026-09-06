# Home Assistant and Apple Home

Add the device using Home Assistant's ESPHome integration and your private API encryption key. Native custom button entities 1–8 keep stable identities; their labels in Remote Builder do not rename HA entities. Empty slots cannot transmit. Explicit commands automatically enable transmission; learning and overlapping sends still block playback.

## Optional fan wrapper

The [example package](../examples/home-assistant/bzp_airbridge.yaml) is the project's three-speed Airbar wrapper. It is not a universal fan profile. Verify the number of speeds, non-wrapping speed-down behavior, and all three learned commands before using it. Adjust entity IDs to match your installation.

1. Enable packages under `homeassistant: packages: !include_dir_named packages` in your existing configuration, merging rather than duplicating that section.
2. Place the example in `packages/bzp_airbridge.yaml`.
3. Check configuration, then restart Home Assistant.
4. Set the resync selector to the fan's actual Off/Low/Medium/High state. Unsynced deliberately makes the fan unavailable.
5. Pair the dedicated **BZP Airbridge** HomeKit Bridge using its Home Assistant notification. Port 21268 must be free. Only the fan is included.

Power-on from Off normalizes to Low with two speed-down commands before stepping to the target. This assumes a three-speed fan that stops at Low rather than cycling. Every command is serialized. A completed RF replay means the bridge emitted the signal—not that the appliance received it. After using a physical remote or changing power externally, resync the estimate.

Custom buttons can be used in automations with `button.press`. They do not automatically map to fan percentages or Apple Home accessories. Build a separate suitable wrapper for each appliance; never apply this fan state model to a different remote without testing.

Keep API keys, pairing codes, and household configuration private.
