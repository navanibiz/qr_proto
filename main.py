import argparse
import json
import qrcode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from google.protobuf.json_format import MessageToDict
from proto.event_pb2 import Event, AccessLevelVIP, AccessLevelStaff, AccessLevelPublic
from render_qr_with_t_squares import render_qr_with_t_squares
from structured_codec import encode_sections_protobuf, decode_sections_protobuf
from decoder import extract_bitstream_from_qr
from reccursive_decoder import extract_bitstream_from_recursive_qr
from google.protobuf.json_format import MessageToDict
import math
import urllib.parse
import base64
import cv2
from pyzbar.pyzbar import decode as qr_decode
import re
import numpy as np

# def find_suitable_qr_matrix(bitstream: str, public_payload: str, max_version: int = 40):
#     required_bytes = math.ceil(len(bitstream) / 8) + 2
#     print(f"[SELECT] Bits to embed: {len(bitstream)} => needs {required_bytes} black tiles")
#     for version in range(1, max_version + 1):
#         qr = qrcode.QRCode(
#             version=version,
#             error_correction=qrcode.constants.ERROR_CORRECT_Q,
#             box_size=1,
#             border=4
#         )
#         qr.add_data(public_payload)
#         qr.make(fit=True)
#         matrix = qr.get_matrix()
#         black_tiles = sum(1 for row in matrix for mod in row if mod)
#         if black_tiles >= required_bytes:
#             print(f"[SELECT] ✅ Version {version} works: {black_tiles} black tiles available")
#             return matrix
#     raise ValueError(f"[ERROR] ❌ No QR version found with enough black tiles for {required_bytes} bytes")

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


def load_key(path, is_private=False):
    with open(path, "rb") as f:
        key_data = f.read()
    return serialization.load_pem_private_key(key_data, password=None) if is_private \
        else serialization.load_pem_public_key(key_data)

vip_pub = load_key("keys/vip_public.pem")
vip_priv = load_key("keys/vip_private.pem", is_private=True)
staff_pub = load_key("keys/staff_public.pem")
staff_priv = load_key("keys/staff_private.pem", is_private=True)

def encrypt_rsa(public_key, message: str) -> str:
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
        vip = AccessLevelVIP()
        vip.vip_lounge_location = encrypt_rsa(vip_pub, data["vip_data"]["vip_lounge_location"])
        vip.vip_contact = encrypt_rsa(vip_pub, data["vip_data"]["vip_contact"])
        vip.exclusive_sessions.extend([encrypt_rsa(vip_pub, s) for s in data["vip_data"]["exclusive_sessions"]])
        event.vip_data.CopyFrom(vip)
    if "staff_data" in data:
        staff = AccessLevelStaff()
        staff.internal_briefing = encrypt_rsa(staff_pub, data["staff_data"]["internal_briefing"])
        staff.security_codes.extend([encrypt_rsa(staff_pub, s) for s in data["staff_data"]["security_codes"]])
        staff.requires_background_check = data["staff_data"]["requires_background_check"]
        event.staff_data.CopyFrom(staff)
    return event




def encode_from_dict(json_data: dict, filename: str = "fractalized_qr.png", dimension: int = 1):
    event = from_json(json_data)
    base_fields = MessageToDict(event, preserving_proto_field_name=True)
    base_fields.pop("vip_data", None)
    base_fields.pop("staff_data", None)
    compact_json = json.dumps(base_fields, separators=(",", ":"), sort_keys=True)
    base64_bytes = base64.b64encode(compact_json.encode("utf-8"))
    encoded_payload = urllib.parse.quote(base64_bytes.decode("utf-8"))
    public_payload = f"https://sumanair.github.io/scanner/l1.html?data={encoded_payload}"
    print(f"Public url : {public_payload}")

    # 👉 Encode hidden roles as bitstream, passing dimension as depth
    bitstream = encode_sections_protobuf({
        "VIP": event.vip_data,
        "STAFF": event.staff_data
    }, depth=dimension)  # <-- This was missing

    # 👇 Compute bits per tile based on dimension
    bits_per_tile = 8 ** dimension
    print(f"bits_per_tile is {bits_per_tile} for (dimension={dimension})")

    # 🔍 Select a suitable QR version
    matrix = find_suitable_qr_matrix(bitstream, public_payload, bits_per_tile=bits_per_tile)

    # 🖼️ Render QR using fractal tiles (assumes render logic supports this depth)
    img = render_qr_with_t_squares(matrix, bitstream, module_size=10, depth=dimension)

    img.save(filename)
    with open("event_rsa.bin", "wb") as f:
        f.write(event.SerializeToString())

    print(f"✅ Encoded QR with fractals saved to '{filename}'")


def decode_with_role(role: str, img_bytes: bytes):
    import numpy as np
    import json

    # Step 1: Convert image bytes → image
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    cv2.imwrite("temp_qr.png", img)

    # Step 2: Extract and decode bitstream using embedded header
    bitstream = extract_bitstream_from_recursive_qr("temp_qr.png", module_size=10)
    bitstream = bitstream[:len(bitstream) - (len(bitstream) % 8)]
    compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))

    # Step 3: Decode protobuf sections
    sections = decode_sections_protobuf(compressed, {
        "VIP": AccessLevelVIP,
        "STAFF": AccessLevelStaff,
    })

    vip = sections["VIP"]
    staff = sections["STAFF"]

    decrypted_vip = {
        "vip_lounge_location": decrypt_rsa(vip_priv, vip.vip_lounge_location),
        "vip_contact": decrypt_rsa(vip_priv, vip.vip_contact),
        "exclusive_sessions": [decrypt_rsa(vip_priv, s) for s in vip.exclusive_sessions]
    }

    decrypted_staff = {
        "internal_briefing": decrypt_rsa(staff_priv, staff.internal_briefing),
        "security_codes": [decrypt_rsa(staff_priv, s) for s in staff.security_codes],
        "requires_background_check": staff.requires_background_check
    }
    print("🔓 Decrypted VIP Data:\n", decrypted_vip)
    print("🔓 Decrypted STAFF Data:\n", decrypted_staff)

    # Step 4: Decode visible QR content (general data)
    general_data = {}
    #qr_result = qr_decode(img)
    # Create a black & white version of the image just for QR detection
    bw_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw_thresh = cv2.threshold(bw_img, 128, 255, cv2.THRESH_BINARY)

    # Try decoding from the thresholded image
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

    # Step 5: Role-based response
    role = role.lower()
    if role == "general":
        return {"general": general_data}
    elif role == "vip":
        return {"general": general_data, "vip": decrypted_vip}
    elif role == "staff":
        return {"general": general_data, "staff": decrypted_staff}
    elif role == "admin":
        return {"general": general_data, "vip": decrypted_vip, "staff": decrypted_staff}
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
    
################################################################
# For CLI usage
################################################################
def encode():
    with open("./data/event.json", "r") as f:
        json_data = json.load(f)
    encode_from_dict(json_data, filename="fractalized_qr.png")

# Retain other decode and main CLI logic unchanged
def decode():
    #bitstream = extract_bitstream_from_qr("fractalized_qr.png", module_size=10)
    bitstream = extract_bitstream_from_recursive_qr("fractalized_qr.png", module_size=10, depth=2)
    bitstream = bitstream[:len(bitstream) - (len(bitstream) % 8)]
    compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))

    # === Decode hidden VIP/STAFF ===
    sections = decode_sections_protobuf(compressed, {
        "VIP": AccessLevelVIP,
        "STAFF": AccessLevelStaff,
    })
    vip = sections["VIP"]
    staff = sections["STAFF"]

    decrypted_vip = AccessLevelVIP(
        vip_lounge_location=decrypt_rsa(vip_priv, vip.vip_lounge_location),
        vip_contact=decrypt_rsa(vip_priv, vip.vip_contact),
        exclusive_sessions=[decrypt_rsa(vip_priv, s) for s in vip.exclusive_sessions]
    )
    decrypted_staff = AccessLevelStaff(
        internal_briefing=decrypt_rsa(staff_priv, staff.internal_briefing),
        security_codes=[decrypt_rsa(staff_priv, s) for s in staff.security_codes],
        requires_background_check=staff.requires_background_check
    )

    print("🔓 Decrypted VIP Data:\n", decrypted_vip)
    print("🔓 Decrypted STAFF Data:\n", decrypted_staff)

    # === Decode visible QR data (public payload URL) ===


    img = cv2.imread("fractalized_qr.png")
    qr_result = qr_decode(img)

    if not qr_result:
        print("❌ Could not detect a QR code for public payload.")
        return

    public_url = qr_result[0].data.decode()
    print(f"🌐 Public URL found: {public_url}")

    # Extract base64 segment from URL
    match = re.search(r'data=([^&]+)', public_url)
    if match:
        encoded_segment = match.group(1)
        try:
            decoded_json = base64.b64decode(urllib.parse.unquote(encoded_segment)).decode("utf-8")
            public_data = json.loads(decoded_json)
            print("🌍 Public Event Data:\n", json.dumps(public_data, indent=2))
        except Exception as e:
            print("❌ Failed to decode public payload:", e)
    else:
        print("⚠️ No 'data=' segment found in the URL.")


    # Convert image bytes to OpenCV image and save for fractal bitstream extraction
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    cv2.imwrite("temp_qr.png", img)

    # === Fractal bitstream decode (VIP/STAFF) ===
    #bitstream = extract_bitstream_from_qr("temp_qr.png", module_size=10)
    bitstream = extract_bitstream_from_recursive_qr("fractalized_qr.png", module_size=10, depth=2)
    bitstream = bitstream[:len(bitstream) - (len(bitstream) % 8)]
    compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))

    sections = decode_sections_protobuf(compressed, {
        "VIP": AccessLevelVIP,
        "STAFF": AccessLevelStaff,
    })

    vip = sections["VIP"]
    staff = sections["STAFF"]

    decrypted_vip = {
        "vip_lounge_location": decrypt_rsa(vip_priv, vip.vip_lounge_location),
        "vip_contact": decrypt_rsa(vip_priv, vip.vip_contact),
        "exclusive_sessions": [decrypt_rsa(vip_priv, s) for s in vip.exclusive_sessions]
    }

    decrypted_staff = {
        "internal_briefing": decrypt_rsa(staff_priv, staff.internal_briefing),
        "security_codes": [decrypt_rsa(staff_priv, s) for s in staff.security_codes],
        "requires_background_check": staff.requires_background_check
    }

    # === Public QR content (General) ===
    general_data = {}
    qr_result = qr_decode(img)
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
        general_data = {"error": "Could not detect a QR code for public payload."}

    # === Return role-specific section ===
    role = role.lower()
    if role == "general":
        return general_data
    elif role == "vip":
        return decrypted_vip
    elif role == "staff":
        return decrypted_staff
    else:
        return {"error": f"Unknown role '{role}'"}

# === CLI Entrypoint ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["encode", "decode"], required=True)
    parser.add_argument("--role", choices=["general", "vip", "staff", "admin"], help="Role to decode as (used only in decode mode)")
    args = parser.parse_args()

    if args.mode == "encode":
        with open("./data/event.json", "r") as f:
            json_data = json.load(f)
        main(mode="encode", json_data=json_data)
    elif args.mode == "decode":
        with open("fractalized_qr.png", "rb") as f:
            img_bytes = f.read()
        role = args.role or "general"
        result = main(mode="decode", role=role, img_bytes=img_bytes)
        print(json.dumps(result, indent=2))


