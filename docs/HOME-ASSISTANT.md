# Home Assistant and Apple Home

## Add the ESPHome device to Home Assistant

Add the Airbridge through Home Assistant's ESPHome integration using its API encryption key. The Airbridge settings page now includes an API-key finding aid to help locate the existing key needed for setup. Treat the discovered key as a credential: use it only for the local ESPHome connection, and never paste it into public issues, screenshots, or GitHub files. The key finder does not replace the ESPHome pairing flow.

Native custom button entities 1–8 keep stable identities; their labels in Remote Builder do not rename Home Assistant entities. Empty slots cannot transmit. Explicit commands automatically enable transmission; learning and overlapping sends still block playback.

## Optional fan wrapper

The [example package](../examples/home-assistant/bzp_airbridge.yaml) is the project's three-speed Airbar wrapper. It is not a universal fan profile. Verify the number of speeds, non-wrapping speed-down behavior, and all three learned commands before using it. Adjust entity IDs to match your installation.

1. Enable packages under `homeassistant: packages: !include_dir_named packages` in your existing configuration, merging rather than duplicating that section.
2. Place the example in `packages/bzp_airbridge.yaml`.
3. Check configuration, then restart Home Assistant.
4. In the Airbridge settings page, use **Sync fan state** to select the fan's actual Off/Low/Medium/High state, then press **Sync fan state**. The Home Assistant estimate on the page confirms the change. The Home Assistant resync selector is also available. A first installation starts Unsynced until this is done.

Power-on from Off normalizes to Low with two speed-down commands before stepping to the target. This assumes a three-speed fan that stops at Low rather than cycling. Every command is serialized. A completed RF replay means the bridge emitted the signal—not that the appliance received it. Fan state is estimated, not physical feedback. After using a physical remote or changing power externally, resync the estimate.

## Power loss and manual sync

Starting with 0.2.2-beta.1, the package retains its last known fan estimate through an Airbridge power loss, Wi-Fi disconnect, or Home Assistant restart. HomeKit can show No Response while the bridge is actually disconnected; control returns automatically with the saved estimate after it reconnects. It does not transmit a command to force the physical fan into that state.

The estimate is stored in Home Assistant's restoring input-select helper. Changes to the physical fan while the bridge is offline can make it inaccurate. Correct it under **Sync fan state** in the device settings page: choose Off, Low, Medium, or High and press the sync button. This updates Home Assistant and HomeKit without transmitting RF. It also stops any pending fan-control sequence so it cannot overwrite your correction.

Upgrade both the firmware and the example Home Assistant package. For an existing package installation, validate configuration and reload automations after replacing the package. Remove the old `bzp_airbridge_observer_disconnect` automation if you merged the update manually; leaving it active still clears state on disconnect. Keep the existing helper and entity IDs so their stored state and Apple Home identity are preserved.

Received commands and completed web-page replays update the estimate when observed in sequence. Reconnect snapshots and sequence gaps retain the prior estimate instead of guessing what happened while offline. Passive handheld recognition depends on the radio receiving the remote reliably; it is not physical fan feedback. Failed/interrupted control sequences may still require manual sync.

## Publish the fan to Apple Home

Home Assistant and Apple Home are two separate steps. The ESPHome device appearing in Home Assistant does not automatically add an accessory to Apple Home.

The dedicated HomeKit Bridge section in the example exports **only `fan.bzp_airbridge`**, named **BZP Airbridge**, on port **21268**. When paired, Apple Home should show a fan accessory with on/off and three-speed control. Do not add the power switch and speed selector separately; the fan entity is the combined accessory.

1. Confirm `fan.bzp_airbridge` is available (not `unavailable`). On first setup, or if the estimate is Unsynced after an interrupted command, use **Sync fan state** to enter the fan's actual state. Ordinary reconnects preserve the estimate.
2. Check Home Assistant configuration, then restart Home Assistant or run the HomeKit reload action to apply YAML changes.
3. In Home Assistant, open **Settings → Devices & services → HomeKit Bridge**. Find **BZP Airbridge** and its pairing card/code in Notifications.
4. In Apple Home, choose **Add Accessory**, then scan the QR code or use **More Options / Don't Have a Code?** and enter the current code. Keep the iPhone and Home Assistant on the same local network so discovery can work.
5. Look for the **BZP Airbridge** fan accessory in Apple Home. The Home Assistant HomeKit *service device* page may say “This device has no entities”; that page represents the bridge service and is not the accessory list.

### If the bridge is already in Apple Home but has no fan

Confirm `fan.bzp_airbridge` is available and the HomeKit filter includes that entity. If the bridge was forcefully unpaired or reset in Home Assistant, Apple Home may still show its old saved bridge entry even though it no longer matches the active pairing.

Remove **only the stale BZP Airbridge bridge** from Apple Home, then add it again using the current BZP Airbridge pairing notice in Home Assistant Notifications. Unpairing applies to this HomeKit bridge; it does not affect other Home Assistant HomeKit bridges. After re-pairing, check the Home app's bridge/accessory details and its room for the fan tile.

If the bridge cannot be discovered, verify both devices are on the same LAN and the router allows local multicast/mDNS discovery; guest Wi-Fi, client isolation, VLANs, or multicast filtering can prevent discovery. Do not delete unrelated HomeKit bridges.

Home Assistant uses entity IDs as HomeKit accessory identity, so keep `fan.bzp_airbridge` stable if you want to preserve its Home app settings. HomeKit changes may take a moment to appear after a reload.

## Custom commands

Custom buttons can be used in automations with `button.press`. They do not automatically map to fan percentages or Apple Home accessories. Build a separate suitable wrapper for each appliance; never apply this fan state model to a different remote without testing.

Keep API keys, Wi-Fi credentials, pairing codes, and household configuration private. Do not put live setup codes or personal network details in this repository.
