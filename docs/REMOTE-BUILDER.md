# Remote Builder

1. Select an empty remote in **Build your remote** and save its name.
2. **Add button**: choose label, icon, and position. Build the whole layout first.
3. Select **Learn** on a button. The animated receiver and countdown mean it is listening; press that key on the original remote.
4. **Command received** is only a candidate. Select **Save learned command** or **Discard capture**.
5. Select **Send** and observe the appliance. A completed replay is not an acknowledgement from the appliance.

Capacity is four custom remotes and eight custom buttons total. Custom captures support 16–256 valid alternating pulses. Timeout or discard preserves the previously learned command. Unsupported/noisy signals can time out.

## Organize

Edit changes label, icon, and position without changing slot identity. Delete requires confirmation and removes that custom button and capture. Original Vornado controls stay separate.

Names are limited to 32 UTF-8 bytes (emoji can use several bytes). User labels render as text, not HTML. Buttons must belong to a named remote.

## Private backups

Export downloads airbridge-private-remotes.json: remote names, slot layout, and custom pulse captures. It contains no network/API credentials and no legacy captures, but it is still private RF control data.

Import validates schema, profile, capacities, and pulse timings before replacing all custom remotes. It asks for confirmation, never transmits automatically, and rejects malformed data. Save/discard an active capture before importing or editing layouts. Export a backup before deletion.

The fixed radio-profile identifier is intentional. Changing private firmware frequency also requires updating this identifier and its validators; automatic frequency selection is not implemented.

## Home Assistant

Custom slots appear as Custom button 1–8. Default entity IDs generally look like button.bzp_airbridge_custom_button_1; verify your actual IDs. Layout renaming does not rename HA entities. Rename in HA if desired.

Arbitrary layouts are not automatically converted to fan/light/cover entities. The Airbar fan example is a separate profile with explicitly estimated state. Avoid simultaneous commands from original remote, web controls, and HA; there is no physical-state feedback.
