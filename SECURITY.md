# Security and privacy

The device HTTP page and REST controls intentionally have no login. Native ESPHome encryption and OTA passwords do not protect port 80. Use a trusted LAN or restricted IoT network; never expose the device directly to the internet.

Mutation endpoints require a custom header and do not enable cross-origin requests. This mitigates ordinary browser-form CSRF, not unauthorized LAN clients.

Wi-Fi credentials are sent in a POST body and excluded from entities/logs. HTTP transport still exposes them to a hostile network. RF backups and raw logs may contain codes that operate your devices.

Do not publish secrets.yaml, private backups, raw captures/logs, compiled firmware, API keys, HomeKit pairing codes, or household configuration. Only operate authorized devices. No rolling-code bypass is supported.

Report vulnerabilities privately to the repository owner. Use GitHub private reporting if available; do not include live secrets in public issues.
