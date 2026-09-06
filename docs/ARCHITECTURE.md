# Architecture

ESPHome 2026.8.2 supplies Wi-Fi, encrypted native API, OTA, CC1101 state switching, and RMT pulse I/O. Airbridge adds the local UI, validated capture storage, and explicit replay controls.

## Protected Vornado controls

The original three globals retain their identities and 512-pulse capacity. Existing captures survive the builder upgrade. They use ESPHome preferences with a one-minute flash interval; allow 65 seconds after saving before disconnecting power.

## Custom Remote Builder

Four remote names share eight stable button slots. Each button has a label, icon, position, remote assignment, and at most 256 signed pulse durations. The 4,552-byte versioned store is committed as a separate NVS blob (bzp_builder/store_v2). Custom saves acknowledge only after commit; failed imports preserve the prior store. A pending candidate remains separate until Save; Cancel preserves the previously saved command.

GET /airbridge/builder returns layout, status, revision, and private captures. POST accepts raw JSON with Content-Type: application/json and X-Airbridge-Request: builder. Payloads are bounded to 26,000 bytes. Operations: replace, learn, save, cancel, send. HTTP 200 with Accepted means queued, not completed: clients poll until revision changes, then inspect error. Never automatically repeat an uncertain send request.

Input checks cover schema/profile, slot counts, name lengths, integer bounds, pulse count/polarity/duration, and active remote assignments. The device defers mutations to its main loop. Native HTTP body delivery is chunked; URL-encoded form handling is deliberately not used for layouts.

## Radio and integrations

All slots share 433.937 MHz ASK/OOK, eight repeats, zero added gap. Explicit valid sends automatically enable transmission. Learning, pending custom candidates, overlapping sends, and invalid/empty frames block replay. The radio returns to receive after transmission. These are emission checks, not appliance feedback.

Home Assistant sees the original three buttons plus eight stable Custom button entities. A separate optional three-speed fan wrapper maintains an estimate and exposes only that fan through HomeKit. Physical remote use requires resynchronization.

## Security boundary

The no-login HTTP page is for a trusted isolated LAN only. The custom request header is a cross-origin browser defense, not authentication. RF backups contain usable control data. API encryption and OTA passwords do not encrypt the web page. Keep the device off the public Internet and do not publish private backups or deployment binaries.
