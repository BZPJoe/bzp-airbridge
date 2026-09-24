# Changelog

## Unreleased

- Document the API-key finding aid for Home Assistant setup and reinforce that discovered keys must stay private.
- Clarify that the dedicated HomeKit bridge publishes the combined BZP Airbridge fan entity, not separate power/speed controls.
- Explain why the Home Assistant HomeKit service-device page can appear empty and how to recover a stale Apple Home pairing after a bridge reset.

## 0.2.0-beta.1

- Four custom remote layouts and eight stable custom button slots.
- Label/icon/order editing and individual learning with countdown, explicit save/discard.
- Private JSON backups, schema/pulse validation, separate versioned NVS storage.
- Existing Vornado global IDs and button names preserved.
- Explicit commands automatically enable transmission; learning blocks sending.
- Storage, pulse, and backup validation tests.
- Updated setup, integration, recovery, security, and branding documentation.

GitHub auto-update delivery is not implemented. RF compatibility and speed behavior still require testing with the target appliance.
