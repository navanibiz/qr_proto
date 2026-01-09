from PIL import Image
import json
import qrcode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from google.protobuf.json_format import MessageToDict
from proto.event_pb2 import Event, AccessLevelVIP, AccessLevelStaff, AccessLevelPublic, AccessLevelAsserter
from render_qr_with_t_squares import render_qr_with_t_squares_partial, generate_recursive_t_square_tile_from_bytes
from structured_codec import encode_sections_protobuf, decode_sections_protobuf
from decoder import extract_bitstream_from_qr
from reccursive_decoder import extract_bitstream_from_recursive_qr, extract_tiles_from_image, is_black_tile, extract_byte_from_recursive_tile
from google.protobuf.json_format import MessageToDict
import math
import urllib.parse
import base64
import cv2
from pyzbar.pyzbar import decode as qr_decode
import numpy as np
from config import * 


def compute_module_size(depth: int) -> int:
    if depth <= 1:
        return MODULE_SIZE
    # Ensure leaf sampling has enough pixels at depth >= 2.
    return 3 ** (depth + 1)



def generate_dummy_filler_bitstream(depth: int, tile_count: int, bits_per_tile: int, color=FILLER_COLOR_PURPLE):
    from random import choice
    print('[INFO] Filler color:', color)
    dummy_bytes = [choice(DUMMY_FILLERS) for _ in range(tile_count * (8 ** (depth - 1)))]
    bitstream = ''.join(f"{byte:08b}" for byte in dummy_bytes)
    return bitstream, color


def append_overlay_to_existing_qr(
    image_path: str,
    bitstream: str,
    module_size: int,
    depth: int,
    start_tile: int,
) -> Image.Image:
    tiles = extract_tiles_from_image(image_path, module_size=module_size)
    positions = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if is_black_tile(tile):
                positions.append((x * module_size, y * module_size))

    bits_per_tile = 8 ** depth
    bit_chunks = [
        bitstream[i:i + bits_per_tile].ljust(bits_per_tile, "0")
        for i in range(0, len(bitstream), bits_per_tile)
    ]

    if start_tile + len(bit_chunks) > len(positions):
        raise ValueError("Not enough black tiles to append the asserter overlay.")

    img = Image.open(image_path).convert("RGB")
    for idx, chunk_bits in enumerate(bit_chunks):
        tile_idx = start_tile + idx
        byte_values = [int(chunk_bits[i:i + 8], 2) for i in range(0, len(chunk_bits), 8)]
        overlay = generate_recursive_t_square_tile_from_bytes(byte_values, module_size, depth=depth)
        img.paste(overlay, positions[tile_idx], overlay)

    return img


def find_suitable_qr_matrix(bitstream: str, public_payload: str, max_version: int = 40, bits_per_tile: int = 8):
    required_bytes = math.ceil(len(bitstream) / bits_per_tile) + 2
    print(f"required_bytes is {required_bytes} for bits_per_tile={bits_per_tile}")
    print(f"[SELECT] Bits to embed: {len(bitstream)} => needs {required_bytes} black tiles (each holds {bits_per_tile} bits)")
    
    for version in range(1, max_version + 1):
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=1,
            border=4
        )
        qr.add_data(public_payload)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        black_tiles = sum(1 for row in matrix for mod in row if mod)
        if black_tiles >= required_bytes:
            print(f"[SELECT] ✅ Version {version} works: {black_tiles} black tiles available")
            return matrix

    raise ValueError(f"[ERROR] ❌ No QR version found with enough black tiles for {required_bytes} bytes")


_KEY_CACHE = {}


def load_key(path, is_private=False, required=False):
    cache_key = (path, is_private)
    if cache_key in _KEY_CACHE:
        return _KEY_CACHE[cache_key]
    try:
        with open(path, "rb") as f:
            key_data = f.read()
    except FileNotFoundError:
        if required:
            raise
        _KEY_CACHE[cache_key] = None
        return None
    key = (
        serialization.load_pem_private_key(key_data, password=None)
        if is_private
        else serialization.load_pem_public_key(key_data)
    )
    _KEY_CACHE[cache_key] = key
    return key

def encrypt_rsa(public_key, message) -> str:
    if message is None:
        message = ""
    elif not isinstance(message, str):
        message = json.dumps(message, separators=(",", ":"), sort_keys=True)
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    ).hex()

def decrypt_rsa(private_key, ciphertext_hex: str) -> str:
    ciphertext = bytes.fromhex(ciphertext_hex)
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    ).decode()


def safe_decrypt_rsa(private_key, ciphertext_hex: str):
    if not ciphertext_hex:
        return None
    try:
        return decrypt_rsa(private_key, ciphertext_hex)
    except Exception:
        return None


def from_json(data: dict) -> Event:
    event = Event(
        event_id=data["event_id"],
        name=data["name"],
        location=data["location"],
        start_time=data["start_time"],
        end_time=data["end_time"]
    )
    if "public_data" in data:
        event.public_data.CopyFrom(AccessLevelPublic(**data["public_data"]))
    if "vip_data" in data:
        vip_pub = load_key("keys/vip_public.pem", required=True)
        vip = AccessLevelVIP()
        vip.vip_lounge_location = encrypt_rsa(vip_pub, data["vip_data"]["vip_lounge_location"])
        vip.vip_contact = encrypt_rsa(vip_pub, data["vip_data"]["vip_contact"])
        vip.exclusive_sessions.extend([encrypt_rsa(vip_pub, s) for s in data["vip_data"]["exclusive_sessions"]])
        event.vip_data.CopyFrom(vip)
    if "staff_data" in data:
        staff_pub = load_key("keys/staff_public.pem", required=True)
        staff = AccessLevelStaff()
        staff.internal_briefing = encrypt_rsa(staff_pub, data["staff_data"]["internal_briefing"])
        staff.security_codes.extend([encrypt_rsa(staff_pub, s) for s in data["staff_data"]["security_codes"]])
        staff.requires_background_check = data["staff_data"]["requires_background_check"]
        event.staff_data.CopyFrom(staff)
    if "asserter_data" in data:
        asserter_pub = load_key("keys/asserter_public.pem", required=True)
        asserter = AccessLevelAsserter()
        asserter.asserter_app_version = encrypt_rsa(asserter_pub, data["asserter_data"]["asserter_app_version"])
        asserter.geolocation = encrypt_rsa(asserter_pub, data["asserter_data"]["geolocation"])
        asserter.assertion_valid_until = encrypt_rsa(asserter_pub, data["asserter_data"]["assertion_valid_until"])
        event.asserter_data.CopyFrom(asserter)
    return event

def generate_public_qr(public_payload: str, max_version: int, module_size: int):
    matrix = find_suitable_qr_matrix(
        bitstream="0" * 8,  # placeholder to satisfy capacity check
        public_payload=public_payload,
        max_version=max_version,
        bits_per_tile=8,
    )
    qr_size = len(matrix)
    image_size = qr_size * module_size
    img = Image.new("RGB", (image_size, image_size), "white")
    for y in range(qr_size):
        for x in range(qr_size):
            if matrix[y][x]:
                img.paste("black", (x * module_size, y * module_size,
                                    (x + 1) * module_size, (y + 1) * module_size))
    return img, matrix


def save_public_qr(public_payload: str, filename: str, module_size: int, max_version: int = 40):
    img, matrix = generate_public_qr(public_payload, max_version=max_version, module_size=module_size)
    img.save(filename)
    return filename, matrix


def apply_overlays(
    base_img: Image.Image,
    matrix,
    header_bitstream: str,
    filler_bitstream: str,
    secret_bitstream: str,
    module_size: int,
    depth: int,
):
    tile_index = 0
    img, tile_index = render_qr_with_t_squares_partial(
        matrix, header_bitstream, module_size=module_size, depth=1, start_tile=tile_index, img=base_img
    )
    img, tile_index = render_qr_with_t_squares_partial(
        matrix, filler_bitstream, module_size=module_size, depth=1, start_tile=tile_index, img=img, color=FILLER_COLOR_PURPLE
    )
    img, tile_index = render_qr_with_t_squares_partial(
        matrix, secret_bitstream, module_size=module_size, depth=depth, start_tile=tile_index, img=img
    )
    total_black_tiles = sum(row.count(1) for row in matrix)
    remaining_tiles = total_black_tiles - tile_index
    if remaining_tiles > 0:
        end_filler_bitstream, end_filler_color = generate_dummy_filler_bitstream(
            depth=1,
            tile_count=remaining_tiles,
            bits_per_tile=8,
            color=FILLER_COLOR_BLUE
        )
        img, tile_index = render_qr_with_t_squares_partial(
            matrix, end_filler_bitstream, module_size=module_size, depth=1, start_tile=tile_index, img=img, color=end_filler_color
        )
    return img


def encode_from_dict(
    json_data: dict,
    filename: str = "fractalized_qr.png",
    dimension: int = 1,
    return_metadata: bool = False,
    reserve_bits: int = 0,
    asserter_max_depth: int | None = None,
):
    from_json_proto = from_json(json_data)
    base_fields = MessageToDict(from_json_proto, preserving_proto_field_name=True)

    # Strip hidden roles from public layer
    base_fields.pop("vip_data", None)
    base_fields.pop("staff_data", None)
    base_fields.pop("asserter_data", None)

    # Encode public layer (URL with base64 JSON)
    compact_json = json.dumps(base_fields, separators=(",", ":"), sort_keys=True)
    base64_bytes = base64.b64encode(compact_json.encode("utf-8"))
    encoded_payload = urllib.parse.quote(base64_bytes.decode("utf-8"))
    public_payload = f"{PUBLIC_PAYLOAD_URL}={encoded_payload}"
    print(f"Public URL : {public_payload}")

    # Encode hidden protobuf data
    sections = {}
    if from_json_proto.HasField("vip_data"):
        sections["VIP"] = from_json_proto.vip_data
    if from_json_proto.HasField("staff_data"):
        sections["STAFF"] = from_json_proto.staff_data
    if from_json_proto.HasField("asserter_data"):
        sections["ASSERTER"] = from_json_proto.asserter_data
    secret_bitstream = encode_sections_protobuf(sections, depth=dimension)
    secret_bytes = bytes(
        int(secret_bitstream[i:i + 8], 2) for i in range(0, len(secret_bitstream), 8)
    )

    # Compute tile capacity
    bits_per_tile = 8 ** dimension
    print(f"bits_per_tile is {bits_per_tile} for (dimension={dimension})")
    max_depth = max(dimension, asserter_max_depth or dimension)
    module_size = compute_module_size(max_depth)

    # Filler and header (depth=1 only)
    #filler_bitstream, filler_color = generate_dummy_filler_bitstream(1, bits_per_tile=8, color=FILLER_COLOR_PURPLE)
    tile_count = FILLER_TILE_COUNT
    filler_bitstream, filler_color = generate_dummy_filler_bitstream(
        depth=1,
        tile_count=tile_count,
        bits_per_tile=8,
        color=FILLER_COLOR_PURPLE  # Make sure this is RGB if passed to an RGB image
    )

    header_json = {
        "depth": dimension,
        "bit_length": len(secret_bitstream),
        "bits_per_tile": bits_per_tile,
        "filler_bits": len(filler_bitstream),
        "module_size": module_size,
        "reserve_bits": reserve_bits,
        "asserter_max_depth": asserter_max_depth,
        "asserter_bits_per_tile": (8 ** asserter_max_depth) if asserter_max_depth else None,
        "asserter_module_size": compute_module_size(asserter_max_depth) if asserter_max_depth else None,
        "asserter_reserve_bits": reserve_bits,
    }
    header_bytes = json.dumps(header_json, separators=(",", ":")).encode("utf-8")

    print("[ENCODE] Header JSON:", header_json)
    print("[ENCODE] Header Bytes:", list(header_bytes))
    
    header_bitstream = ''.join(f"{b:08b}" for b in header_bytes)
    print("[ENCODE] Header Bitstream First 64 bits:", header_bitstream[:64])

    # Combine bitstream
    flattened_bitstream = header_bitstream + filler_bitstream + secret_bitstream

    # Find suitable QR version (reserve optional capacity for asserter layer)
    capacity_bitstream = flattened_bitstream + ("0" * max(0, reserve_bits))
    matrix = find_suitable_qr_matrix(
        bitstream=capacity_bitstream,
        public_payload=public_payload,
        bits_per_tile=bits_per_tile
    )

    # Step 1: Generate visible QR (L0)
    base_img, _ = generate_public_qr(public_payload, max_version=40, module_size=module_size)

    # Step 2: Apply overlays (header + filler + secret)
    img = apply_overlays(
        base_img=base_img,
        matrix=matrix,
        header_bitstream=header_bitstream,
        filler_bitstream=filler_bitstream,
        secret_bitstream=secret_bitstream,
        module_size=module_size,
        depth=dimension,
    )
        

    # Save QR image + proto blob
    img.save(filename)
    with open("event_rsa.bin", "wb") as f:
        f.write(from_json_proto.SerializeToString())

    print(f"✅ Encoded QR with header (depth=1) + secret (depth={dimension}) saved to '{filename}'")
    if return_metadata:
        return {
            "filename": filename,
            "public_payload": public_payload,
            "secret_bytes": secret_bytes,
            "header": header_json,
            "public_qr_image": base_img,
        }

def extract_tiles_by_color(img, color, module_size=10, tolerance=10):
    import numpy as np

    h, w = img.shape[:2]
    tiles = []

    for y in range(0, h, module_size):
        for x in range(0, w, module_size):
            tile = img[y:y+module_size, x:x+module_size]
            avg_color = np.mean(tile.reshape(-1, 3), axis=0)
            if np.all(np.abs(avg_color - np.array(color)) < tolerance):
                tiles.append(tile)

    return tiles


def extract_header_from_qr(img_path: str, module_size: int = MODULE_SIZE, max_tiles: int = 256) -> tuple:
    # Step 1: Extract tiles and keep only black tiles in scan order
    tile_grid = extract_tiles_from_image(
        img_path,
        module_size=module_size,
        depth=HEADER_DEPTH,
    )

    if isinstance(tile_grid[0], list):
        tiles = [tile for row in tile_grid for tile in row]
    else:
        tiles = tile_grid

    black_tiles = []
    for tile in tiles:
        if isinstance(tile, np.ndarray):
            tile = Image.fromarray(tile)
        if not isinstance(tile, Image.Image):
            raise TypeError(f"Unexpected tile type: {type(tile)}")
        if is_black_tile(tile):
            black_tiles.append(tile)
        if len(black_tiles) >= max_tiles:
            break

    # Step 4: Decode bytes from header tiles
    header_bytes = []
    for i, tile in enumerate(black_tiles):
        byte = extract_byte_from_recursive_tile(tile, depth=HEADER_DEPTH)
        byte_val = byte[0] if isinstance(byte, bytes) else byte
        header_bytes.append(byte_val)

    # Step 5: Extract JSON substring
    header_raw = bytes(header_bytes)
    json_start = header_raw.find(b"{")
    json_end = header_raw.find(b"}", json_start + 1) if json_start != -1 else -1
    if json_start != -1 and json_end != -1 and json_end > json_start:
        header_str = header_raw[json_start:json_end + 1].decode("utf-8", errors="ignore")
    else:
        header_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in header_bytes)
        print("[ERROR] No JSON bounds detected in header bytes")
        print("[DEBUG] Raw header string:", repr(header_str))
        print("[DEBUG] Raw header bytes:", header_bytes)
        raise ValueError("No JSON bounds detected in header bytes")

    # Step 6: Parse JSON
    try:
        header = json.loads(header_str)
    except Exception as e:
        print("[ERROR] JSON decode failed:", e)
        print("[DEBUG] Raw header string:", repr(header_str))
        print("[DEBUG] Raw header bytes:", header_bytes)
        raise

    return header, json_end + 1


def decode_asserter_overlay(
    image_path: str,
    header: dict,
    header_end_tile: int,
) -> dict | None:
    reserve_bits = header.get("asserter_reserve_bits") or header.get("reserve_bits") or 0
    asserter_max_depth = header.get("asserter_max_depth") or 1
    if reserve_bits <= 0:
        return None

    filler_bits = header.get("filler_bits", FILLER_TILE_COUNT * 8)
    filler_tiles = math.ceil(filler_bits / 8)
    issuer_bits_per_tile = header.get("bits_per_tile", 8)
    issuer_tiles = math.ceil(header.get("bit_length", 0) / issuer_bits_per_tile)
    tile_start = header_end_tile + filler_tiles + issuer_tiles

    for depth in range(int(asserter_max_depth), 0, -1):
        try:
            bitstream = extract_bitstream_from_recursive_qr(
                image_path=image_path,
                module_size=header.get("module_size", MODULE_SIZE),
                depth=depth,
                tile_start=tile_start,
                bit_limit=reserve_bits,
            )
            if not bitstream:
                continue
            compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))
            sections = decode_sections_protobuf(compressed, {
                "ASSERTER": AccessLevelAsserter,
            })
            if sections.get("ASSERTER"):
                return {"sections": sections, "depth": depth}
        except Exception:
            continue
    return None

# def extract_header_from_image(img_np: np.ndarray, module_size: int = 27):
#     from PIL import Image
#     import numpy as np

#     img = Image.fromarray(img_np).convert("RGBA")
#     width, height = img.size
#     grid_size_x = width // module_size
#     grid_size_y = height // module_size

#     tiles = []
#     for y in range(grid_size_y):
#         row = []
#         for x in range(grid_size_x):
#             left = x * module_size
#             upper = y * module_size
#             tile = img.crop((left, upper, left + module_size, upper + module_size))
#             row.append(tile)
#         tiles.append(row)

#     black_tiles = []
#     header_bytes = []
#     header_end_tile = 0

#     for row in tiles:
#         for tile in row:
#             if is_black_tile(tile):
#                 black_tiles.append(tile)

#     for i, tile in enumerate(black_tiles[:64]):
#         byte = extract_byte_from_recursive_tile(tile, depth=1)
#         if isinstance(byte, bytes):
#             byte = byte[0]
#         header_bytes.append(byte)
#         if byte == ord('}'):
#             header_end_tile = i + 1
#             break

#     header_str = bytes(header_bytes).decode("utf-8", errors="ignore")
#     json_start = header_str.find('{')
#     if json_start != -1:
#         header_str = header_str[json_start:]

#     print("[DEBUG] Cleaned Header String:", repr(header_str))
#     for i, b in enumerate(header_bytes):
#         char = chr(b) if 32 <= b <= 126 else '.'
#         print(f"[Tile {i:02}] Byte: {b:3} Char: {char}")

#     try:
#         header = json.loads(header_str)
#     except json.JSONDecodeError as e:
#         print("[ERROR] Failed to parse header JSON.")
#         print("[DEBUG] Raw header bytes:", header_bytes)
#         raise e  # Reraise so Streamlit reports it

#     return header, header_end_tile



def decode_with_role(role: str, img_bytes: bytes):
    import numpy as np
    import json
    import re
    import urllib.parse

    # Step 1: Convert image bytes → image and save temporarily
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    cv2.imwrite("temp_qr.png", img)

 
    # Step 2: Extract header (always depth=1)
    header = None
    header_end_tile = None
    header_module_size = None
    module_size_candidates = [MODULE_SIZE] + MODULE_SIZE_RECURSIVE_CANDIDATES
    for candidate_size in module_size_candidates:
        try:
            header, header_end_tile = extract_header_from_qr("temp_qr.png", module_size=candidate_size)
            header_module_size = candidate_size
            break
        except Exception:
            continue
    if header is None or header_end_tile is None:
        raise ValueError("Failed to extract header from QR image.")
    #header, header_end_tile = extract_header_from_image(img)
    actual_depth = header["depth"]
    bit_length = header["bit_length"]
    module_size = header.get("module_size", header_module_size or MODULE_SIZE)
    filler_bits = header.get("filler_bits")
    if filler_bits is not None:
        filler_tiles = math.ceil(filler_bits / 8)  # filler is always depth=1 (8 bits per tile)
    else:
        filler_tiles = FILLER_TILE_COUNT
    # Adjust starting tile for secret data based on header + filler tiles
    tile_start = header_end_tile + filler_tiles
    print(f"[DEBUG] Header: {header}")
    print(f"[DEBUG] header_end_tile={header_end_tile} filler_tiles={filler_tiles} tile_start={tile_start}")

    # Step 3: Decode secret bitstream using declared depth
    bitstream = extract_bitstream_from_recursive_qr(
        image_path="temp_qr.png",
        module_size=module_size,
        depth=actual_depth,
        tile_start=tile_start,       # 32 for header + 8 filler (adjustable)
        bit_limit=bit_length
    )

    # Step 4: Decode protobuf sections
    compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))
    zlib_idx = -1
    for i in range(len(compressed) - 1):
        if compressed[i] == 0x78 and compressed[i + 1] in (0x01, 0x9C, 0xDA):
            zlib_idx = i
            break
    print(f"[DEBUG] Compressed bytes (first 32): {compressed[:32].hex()}")
    print(f"[DEBUG] zlib_header_index={zlib_idx}")
    sections = decode_sections_protobuf(compressed, {
        "VIP": AccessLevelVIP,
        "STAFF": AccessLevelStaff,
    })

    vip = sections.get("VIP")
    staff = sections.get("STAFF")
    asserter = None
    asserter_decode = decode_asserter_overlay("temp_qr.png", header, header_end_tile)
    if asserter_decode:
        asserter = asserter_decode["sections"].get("ASSERTER")

    decrypted_vip = None
    decrypted_staff = None
    decrypted_asserter = None

    role = role.lower()
    has_hidden = False
    if role in ("vip", "admin") and vip is not None:
        vip_priv = load_key("keys/vip_private.pem", is_private=True)
        if vip_priv:
            decrypted_vip = {
                "vip_lounge_location": safe_decrypt_rsa(vip_priv, vip.vip_lounge_location),
                "vip_contact": safe_decrypt_rsa(vip_priv, vip.vip_contact),
                "exclusive_sessions": [safe_decrypt_rsa(vip_priv, s) for s in vip.exclusive_sessions],
            }
            has_hidden = True

    if role in ("staff", "admin") and staff is not None:
        staff_priv = load_key("keys/staff_private.pem", is_private=True)
        if staff_priv:
            decrypted_staff = {
                "internal_briefing": safe_decrypt_rsa(staff_priv, staff.internal_briefing),
                "security_codes": [safe_decrypt_rsa(staff_priv, s) for s in staff.security_codes],
                "requires_background_check": staff.requires_background_check
            }
            has_hidden = True

    if role == "asserter" and asserter is not None:
        asserter_priv = load_key("keys/asserter_private.pem", is_private=True)
        if asserter_priv:
            decrypted_asserter = {
                "asserter_app_version": safe_decrypt_rsa(asserter_priv, asserter.asserter_app_version),
                "geolocation": safe_decrypt_rsa(asserter_priv, asserter.geolocation),
                "assertion_valid_until": safe_decrypt_rsa(asserter_priv, asserter.assertion_valid_until),
            }
            has_hidden = True

    def has_content(payload: dict) -> bool:
        if not payload:
            return False
        for key, val in payload.items():
            if isinstance(val, list):
                if any(item for item in val):
                    return True
            elif val not in (None, "", False):
                return True
        return False

    if decrypted_vip and not has_content(decrypted_vip):
        decrypted_vip = None
    if decrypted_staff and not has_content(decrypted_staff):
        decrypted_staff = None
    if decrypted_asserter and not has_content(decrypted_asserter):
        decrypted_asserter = None

    if role == "vip":
        has_hidden = decrypted_vip is not None
    elif role == "staff":
        has_hidden = decrypted_staff is not None
    elif role == "asserter":
        has_hidden = decrypted_asserter is not None
    elif role == "admin":
        has_hidden = any([decrypted_vip, decrypted_staff])

    print("🔓 Decrypted VIP Data:\n", decrypted_vip)
    print("🔓 Decrypted STAFF Data:\n", decrypted_staff)

    # Step 5: Decode public visible QR content
    general_data = {}
    bw_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw_thresh = cv2.threshold(bw_img, 128, 255, cv2.THRESH_BINARY)
    qr_result = qr_decode(bw_thresh)
    print(f"QR result: {qr_result}")

    if qr_result:
        public_url = qr_result[0].data.decode()
        match = re.search(r'data=([^&]+)', public_url)
        if match:
            encoded_segment = match.group(1)
            try:
                decoded_json = base64.b64decode(urllib.parse.unquote(encoded_segment)).decode("utf-8")
                general_data = json.loads(decoded_json)
            except Exception as e:
                general_data = {"error": f"Failed to decode public payload: {str(e)}"}
        else:
            general_data = {"warning": "No 'data=' segment found in the URL."}
    else:
        general_data = {"error": "Could not detect a QR code for the public payload."}

    # Step 6: Role-based response
    if role == "general":
        return {"general": general_data}
    elif role == "vip":
        if not has_hidden:
            return {"general": general_data, "notice": "No additional information found for this ticket."}
        return {"general": general_data, "vip": decrypted_vip or {}}
    elif role == "staff":
        if not has_hidden:
            return {"general": general_data, "notice": "No additional information found for this ticket."}
        return {"general": general_data, "staff": decrypted_staff or {}}
    elif role == "asserter":
        if not has_hidden:
            return {"general": general_data, "notice": "No additional information found for this ticket."}
        return {"general": general_data, "asserter": decrypted_asserter or {}}
    elif role == "admin":
        if not has_hidden:
            return {"general": general_data, "notice": "No additional information found for this ticket."}
        return {
            "general": general_data,
            **({"vip": decrypted_vip} if decrypted_vip else {}),
            **({"staff": decrypted_staff} if decrypted_staff else {}),
        }
    else:
        return {"error": f"Unknown role '{role}'"}


def main(role: str = "general", img_bytes: bytes = None, json_data: dict = None, mode: str = "decode"):
    """
    Main entrypoint for Streamlit or CLI.
    - If mode is "encode", json_data must be provided.
    - If mode is "decode", img_bytes and role must be provided.
    """
    if mode == "encode":
        if not json_data:
            raise ValueError("Encoding requires input JSON data")
        return encode_from_dict(json_data)
    elif mode == "decode":
        if not img_bytes:
            raise ValueError("Decoding requires image bytes")
        return decode_with_role(role, img_bytes)
    else:
        raise ValueError("Unsupported mode. Use 'encode' or 'decode'.")
    
