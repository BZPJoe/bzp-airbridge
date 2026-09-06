# Validation — Remote Builder beta

Built with ESPHome 2026.8.2 for ESP32-C3, ESP-IDF, 4 MB flash. Final build: 1,113,576 bytes (60.7% of app partition); static RAM 131,262 bytes (40.9%). Compiler success is not an appliance compatibility test.

| Check | Result |
|---|---|
| ESPHome configuration, generated C++, compile/link | Pass |
| Legacy pulse validation/storage native tests | Pass |
| Custom model validation, corrupted data and bounds | Pass; Store is 4,552 bytes |
| Browser backup schema, integer limits and hostile label tests | Pass |
| Desktop and 390 px embedded viewport visual review | Pass; previews contain no household data |
| Native HA custom entities | Eight entities discovered |
| Original power/up/down saved indicators | Preserved after builder upgrade |
| Custom JSON storage/reboot/error-path test | Pass: roundtrip, invalid import rejected, learn/cancel preserves capture, fixture survived OTA reboot and was cleaned |
| Physical original power replay | Confirmed by project owner before this release |
| New custom remote physical learn/send | Requires owner test with a compatible remote |
| Speed-up/down and fan estimate accuracy | Requires physical verification |
| Long-term Wi-Fi reliability | Not established; weak signal observed during OTA |
| Printed enclosure fit and snap durability | Not physically verified |
| GitHub auto-update download/install | Not implemented; staged controls only |

The opt-in device smoke test creates only known synthetic data on an empty custom store. It never sends RF. Use stage, reboot/OTA, then verify-cleanup. It refuses cleanup if the fixture changed or other custom buttons appeared. Original captures are never exported or overwritten by this test.

During testing, URL-encoded layouts exceeded ESPHome's form limit. The backend now receives bounded raw JSON chunks. ESPHome's IDF adapter also mapped unsupported HTTP 202 to 500; the API now acknowledges with 200 and clients still wait for a changed revision and inspect errors before reporting success.

Custom NVS data and the HTTP/main-loop access path are protected separately from legacy preference storage. Saved custom commands survive a discarded relearn. Synthetic tests cannot prove that an appliance responds to a new waveform.

Deployment builds contain private credentials and are excluded from public source/release archives. The public workflow uses example credentials and does not publish flashable binaries.
