# Staged software updates

The settings page and Home Assistant expose:

- Auto updates: a persistent preference, off by default.
- Check for updates: a manual action.
- Update status and Firmware version: device-reported text.

There is no release URL, GitHub request, download, or automatic installation in
this build. The manual check reports that a release source is not configured.
When the preference is enabled, a six-hour timer calls that same staged check.
It cannot claim the firmware is up to date without an actual release check.

When GitHub releases are ready, connect the shared check_updates hook to the
release mechanism, including version comparison, artifact validation, installation
status, failure handling, and rollback testing. Honor the stored Auto updates
preference for automatic installation. Manual checks must not automatically install
when that preference is off.

Existing password-protected ESPHome OTA remains available for development.
Before publishing public update binaries, establish a provisioning scheme that
keeps each user's Wi-Fi/API/OTA credentials out of the release artifact.
