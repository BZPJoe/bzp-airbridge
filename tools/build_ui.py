"""Embed Horton Systems branding and the Airbridge icon for offline device serving."""
from pathlib import Path
import base64
import json
root=Path(__file__).resolve().parents[1]
logo="data:image/png;base64,"+base64.b64encode((root/"assets/horton-systems.png").read_bytes()).decode()
icon="data:image/svg+xml;base64,"+base64.b64encode((root/"assets/icon.svg").read_bytes()).decode()
prefix="const HORTON_LOGO="+json.dumps(logo)+";\nconst AIRBRIDGE_ICON="+json.dumps(icon)+";\n"
(root/"firmware/ui/settings-bundle.js").write_text(prefix+(root/"firmware/ui/settings.js").read_text()+"\n"+(root/"firmware/ui/builder.js").read_text())
