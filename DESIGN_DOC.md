# Fractal QR System — Design Doc

This document describes what is currently implemented in the project and outlines planned improvements.

## 1) Goals
- Encode standard QR codes with **public metadata** and **hidden, encrypted sections**.
- Support role-based decoding for General, VIP, Staff, and Admin.
- Provide both a Python API and Streamlit UI for encode/decode.

## 2) Non-goals
- Production-grade cryptographic key management.
- Strong adversarial resistance against dedicated steganalysis.
- Full QR spec compliance beyond core encoding/decoding needs.

## 3) Current architecture

### 3.1 Data layers
- **Public layer**: URL payload containing base64-encoded JSON (general event fields).
- **Hidden layer**: Protobuf sections (VIP/Staff), zlib-compressed and encoded into fractal tiles.

### 3.2 Core modules
- `main.py`
  - `encode_from_dict`: produces QR with public URL + hidden payload.
  - `decode_with_role`: extracts header, bitstream, decrypts sections.
- `structured_codec.py`
  - Packs protobuf sections into a zlib-compressed byte stream.
  - Handles optional header stripping on decode.
- `render_qr_with_t_squares.py`
  - Generates fractal tiles and overlays them on QR modules.
- `reccursive_decoder.py`
  - Extracts bitstream by walking tiles recursively.
- `proto/event.proto`
  - Event schema (public, VIP, staff fields).

### 3.3 Encoding flow
1. Build protobuf `Event` from JSON input.
2. Strip VIP/Staff from public JSON.
3. Encode public JSON into URL payload.
4. Encode VIP/Staff protobuf into compressed bitstream.
5. Build header with `depth`, `bit_length`, `filler_bits`, `module_size`.
6. Render QR: header tiles → filler → secret tiles → end filler.

### 3.4 Decoding flow
1. Extract header from black tiles and parse JSON.
2. Use `depth` + `module_size` to decode bitstream.
3. Convert bitstream to bytes and decompress.
4. Parse protobuf sections and decrypt role-specific fields.
5. Parse public payload from QR’s visible layer.

## 4) Depth, module size, and capacity
- Each black tile encodes `8 ** depth` bits.
- For depth > 1, module size must be large enough for recursive sampling:
  - Recommended: `module_size = 3 ** (depth + 1)`
  - Depth 1 → 9 or 10; Depth 2 → 27; Depth 3 → 81.
- Required black tiles:
  - `required_tiles = ceil(required_bits / (8 ** depth))`

## 5) Security considerations
- RSA is used to encrypt VIP/Staff fields.
- Keys are currently stored in `keys/` and loaded at runtime.
- Public payload is not authenticated; a signature would improve integrity.

## 6) Current limitations
- Depth selection is manual (no auto sizing).
- Key management is local and not versioned.
- Header extraction is sensitive to tile ordering; assumes QR black tiles preserve scan order.
- Public payload integrity is not verified.

## 7) Planned improvements

### 7.1 Auto depth selection
- Compute `depth` based on public QR capacity and hidden payload size.
- Compute `module_size` automatically and embed in header.

### 7.2 Generalize codec logic
- Centralize header packing/unpacking, payload validation, and tile mapping.
- Reduce duplicate constants across modules.

### 7.3 Key management
- Support `KEYS_DIR` and key rotation per event/role.
- Allow encrypted private keys with passphrase.

### 7.4 Color vs black-and-white decoding
- Optional colored headers for precise extraction.
- Add BW fallback and calibration for low-quality images.

### 7.5 Alternative fractal patterns
- Store pattern ID in header.
- Implement multiple patterns (T-square, Sierpinski, Hilbert).

### 7.6 Integrity and tamper checks
- Add checksum or signature for the hidden payload.
- Optionally sign public payload.

## 8) Testing strategy (recommended)
- Golden QR fixtures per depth (1, 2, 3).
- Unit tests for:
  - header encode/decode
  - bitstream integrity
  - protobuf round-trip
- Visual inspection baseline images for regression checks.

## 9) Open questions
- Should header tiles be color-encoded or always use black tiles?
- What is the desired balance between QR readability and hidden capacity?
- How should role-based key rotation be handled?
