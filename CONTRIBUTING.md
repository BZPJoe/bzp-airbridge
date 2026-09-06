# Contributing

Describe the device, frequency/modulation, expected behavior, and firmware version. Do not attach private captures or credentials; use synthetic pulse data.

Run both C++ tests, node tests/test_builder.js, node --check firmware/ui/settings-bundle.js, and an ESPHome compile with the pinned toolchain. Regenerate the bundle with python tools/build_ui.py after UI/brand changes.

Check desktop/mobile layout, keyboard operation, reduced motion, offline handling, rejected imports, and legacy capture preservation. Version storage changes and plan migrations. Do not rename existing IDs casually. Keep input bounded and render labels as text. Do not infer hardware compatibility from compilation or capture alone.
