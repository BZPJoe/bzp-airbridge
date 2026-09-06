# Publishing

Public project: https://github.com/BZPJoe/bzp-airbridge

Build a sanitized source archive with `python tools/package.py /tmp/bzp-airbridge-source.zip`. Publish from that archive, never by blindly adding your deployment folder. The packager restricts public directories/extensions and rejects known local secret values. Review its output too: automated scanning is not a complete security guarantee.

Use a beta/prerelease label until physical custom-remote replay, long-term Wi-Fi reliability, speed behavior, and enclosure fit have been verified. The validation report separates software checks from appliance tests.

The GitHub workflow compiles with dummy credentials and does not publish firmware binaries. Build deployment images locally. Never attach real Wi-Fi/API/OTA credentials, raw captures, logs, private backups, or deployment binaries to a public release.

Original code is MIT; vendored ESPHome C++ retains GPLv3. See THIRD_PARTY_NOTICES.md and the included upstream license. Horton Systems marks remain their owner's property.

Brand sources and PNGs are in assets/. The cover can be used as the repository social preview.
