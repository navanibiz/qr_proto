# Future Enhancements and Recommendations

This document captures learnings, design considerations, and potential enhancements for the fractal QR system.

## Key learnings
- **Module size must scale with depth**: for depth > 1, use a larger module size so recursive sampling has at least 1px at the leaf level (e.g., `module_size = 3 ** (depth + 1)`).
- **Depth can be auto-selected**: compute the smallest depth that fits the secret payload into available black tiles.

## Recommended features

### 1) Auto depth and module size selection
- Derive a depth that satisfies `black_tiles * (8 ** depth) >= required_bits`.
- Compute module size from depth and store it in the header so decode can follow automatically.
- UI can offer "Auto" with a preview of computed depth and module size.

### 2) Generalize encode/decode logic
- Create a single "codec" module that handles:
  - header packing/unpacking
  - payload compression/validation
  - tile mapping (depth, module size)
- Remove duplicated assumptions (module sizes, filler counts) across modules.

### 3) Key generation and management
- Move key management out of the repo:
  - support `KEYS_DIR` env var
  - detect missing keys and provide a guided generation flow
- Consider per-event or per-role key rotation and versioning in the header.

### 4) Color versus black-and-white robustness
- Optionally encode the header in a dedicated color (e.g., solid red) and decode with color tolerance.
- Add a black-and-white fallback path for low-quality scans.
- Add a calibration step to detect average module color per image.

### 5) Multiple fractal patterns
- Support alternate tiling patterns beyond T-squares (e.g., Sierpinski, Hilbert, H-tree).
- Store the pattern ID in the header so decode can choose the correct renderer.

### 6) Compression and payload format
- Add a content-type/version field to the header (protobuf schema version, compression type).
- Allow alternate compression (zlib, zstd, none) and pick based on payload size.

### 7) Integrity and tamper detection
- Add a checksum or HMAC of the secret payload.
- Include a signature for public payload to detect tampering.

### 8) QR capacity modeling
- Compute black tile capacity based on actual QR matrix instead of relying on version only.
- Provide a "capacity report" in the UI before encoding.

### 9) Decode diagnostics
- Add a debug mode that saves:
  - sampled tile grid
  - extracted bitstream length
  - zlib header index
- Emit clear user-facing errors (misaligned tiles, depth mismatch, key missing).

### 10) UX improvements
- Visualize tile layout (header/filler/secret) on the generated QR.
- Add download links for generated QR and raw protobuf.

## Suggested next steps
- Implement auto-depth selection + module size computation.
- Consolidate header handling in a single utility function.
- Add a `--debug` flag for CLI and a toggle in Streamlit UI.
