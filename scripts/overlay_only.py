import argparse
import json
import os
from PIL import Image

from main import apply_overlays, compute_module_size, find_suitable_qr_matrix, generate_public_qr
from structured_codec import encode_sections_protobuf
from config import FILLER_COLOR_PURPLE, FILLER_COLOR_BLUE, FILLER_TILE_COUNT
from main import generate_dummy_filler_bitstream
import math


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply overlays to an existing visible QR image.")
    parser.add_argument("--public-payload", required=True, help="Public payload URL string")
    parser.add_argument("--input", required=True, help="Path to visible QR PNG")
    parser.add_argument("--output", required=True, help="Path for output PNG with overlays")
    parser.add_argument("--depth", type=int, default=1, help="Fractal depth")
    parser.add_argument("--vip-bin", required=True, help="VIP protobuf bytes file")
    parser.add_argument("--staff-bin", required=True, help="Staff protobuf bytes file")
    args = parser.parse_args()

    module_size = compute_module_size(args.depth)

    # Load base image
    base_img = Image.open(args.input).convert("RGB")

    # Build secret bitstream from pre-serialized protobuf bytes
    with open(args.vip_bin, "rb") as f:
        vip_bytes = f.read()
    with open(args.staff_bin, "rb") as f:
        staff_bytes = f.read()

    # Reconstruct protobuf section bytes into a faux message-like payload
    secret_bitstream = encode_sections_protobuf({
        "VIP": type("BytesObj", (), {"SerializeToString": lambda self: vip_bytes})(),
        "STAFF": type("BytesObj", (), {"SerializeToString": lambda self: staff_bytes})(),
    }, depth=args.depth)

    bits_per_tile = 8 ** args.depth
    header_json = {
        "depth": args.depth,
        "bit_length": len(secret_bitstream),
        "bits_per_tile": bits_per_tile,
        "filler_bits": FILLER_TILE_COUNT * 8,
        "module_size": module_size,
    }
    header_bytes = json.dumps(header_json, separators=(",", ":")).encode("utf-8")
    header_bitstream = "".join(f"{b:08b}" for b in header_bytes)

    filler_bitstream, _ = generate_dummy_filler_bitstream(
        depth=1,
        tile_count=FILLER_TILE_COUNT,
        bits_per_tile=8,
        color=FILLER_COLOR_PURPLE,
    )

    flattened_bitstream = header_bitstream + filler_bitstream + secret_bitstream
    matrix = find_suitable_qr_matrix(
        bitstream=flattened_bitstream,
        public_payload=args.public_payload,
        bits_per_tile=bits_per_tile,
    )

    output_img = apply_overlays(
        base_img=base_img,
        matrix=matrix,
        header_bitstream=header_bitstream,
        filler_bitstream=filler_bitstream,
        secret_bitstream=secret_bitstream,
        module_size=module_size,
        depth=args.depth,
    )

    output_img.save(args.output)
    print(f"✅ Wrote overlay image: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
