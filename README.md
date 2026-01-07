# qr_proto

Fractal QR code prototype that embeds layered data inside standard QR codes using recursive T-square tiles.
Public fields are encoded as a URL payload, while VIP/Staff sections are encrypted, protobuf-encoded, and hidden
inside QR modules.

## What it does
- Generates QR codes with public event metadata and hidden encrypted sections.
- Uses protobuf + zlib compression for structured payloads.
- Supports role-based decoding (General, VIP, Staff, Admin).
- Provides a Streamlit UI for generating and scanning event QR codes.

## Folder structure
```
.
├── main.py                     # Encode/decode pipeline
├── config.py                   # Shared constants (colors, sizes, URLs)
├── render_qr_with_t_squares.py # QR rendering + fractal tile overlays
├── reccursive_decoder.py       # Recursive tile decoding
├── decoder.py                  # Simple tile decoding helpers
├── structured_codec.py         # Protobuf section packing/unpacking
├── generate_keys.py            # RSA key generation
├── proto/
│   ├── event.proto             # Protobuf schema
│   └── event_pb2.py             # Generated protobuf module
├── ui/
│   ├── Home.py                 # Streamlit app entry (multi-page)
│   └── pages/                  # Streamlit pages
├── keys/                       # RSA keypairs (generated)
├── data/                       # Sample data (if any)
└── qr_*.png                     # Generated QR images (output)
```

## Instructions to run

### 1) Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Generate RSA keys (first run only)
```bash
python generate_keys.py
```

### 3) Run the Streamlit UI
```bash
streamlit run ui/Home.py
```

### 4) Encode via Python (optional)
```bash
python - <<'PY'
from main import encode_from_dict

event = {
    "event_id": "EVT-2025-001",
    "name": "FutureTech Expo 2025",
    "location": "Convention Center, San Francisco",
    "start_time": "2025-09-12T09:00:00Z",
    "end_time": "2025-09-12T18:00:00Z",
    "public_data": {
        "agenda_summary": "Talks on AI, IoT, and Sustainable Tech",
        "dress_code": "Smart Casual",
        "general_guidelines": ["Carry a valid photo ID", "No outside food allowed"]
    },
    "vip_data": {
        "vip_lounge_location": "2nd Floor, Sapphire Lounge",
        "vip_contact": "vip@futuretech.com",
        "exclusive_sessions": ["AI Founders Roundtable"]
    },
    "staff_data": {
        "internal_briefing": "Ensure secure entry checkpoints are staffed by 08:30AM.",
        "security_codes": ["SEC-ALPHA-2025"],
        "requires_background_check": True
    }
}

encode_from_dict(event, filename="qr_EVT-2025-001.png", dimension=1)
PY
```

### 5) Decode via Python (optional)
```bash
python - <<'PY'
from main import main

with open("qr_EVT-2025-001.png", "rb") as f:
    img_bytes = f.read()

result = main(role="admin", img_bytes=img_bytes, mode="decode")
print(result)
PY
```

## Notes
- `keys/` must contain `vip_*` and `staff_*` RSA keypairs.
- `PUBLIC_PAYLOAD_URL` in `config.py` controls the public URL payload target.
- Protobuf schema lives in `proto/event.proto`.
- For depth > 1, module size must grow with depth (e.g., `3 ** (depth + 1)`) so leaf sampling uses at least 1px.
- See `FUTURE_ENHANCEMENTS.md` for planned features and improvements.
