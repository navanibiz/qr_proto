import argparse
import json
import qrcode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from google.protobuf.json_format import MessageToDict
from event_pb2 import Event, AccessLevelVIP, AccessLevelStaff, AccessLevelPublic
from render_qr_with_t_squares import render_qr_with_t_squares
from structured_codec import encode_sections_protobuf, decode_sections_protobuf
from decoder import extract_bitstream_from_qr
from google.protobuf.json_format import MessageToDict
import math
import urllib.parse
import base64
import cv2
from pyzbar.pyzbar import decode as qr_decode

def find_suitable_qr_matrix(bitstream: str, public_payload: str, max_version: int = 40):
    
    required_bytes = math.ceil(len(bitstream) / 8) + 2  # +2 for header
    print(f"[SELECT] Bits to embed: {len(bitstream)} => needs {required_bytes} black tiles")

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


# === Load RSA Keys ===
def load_key(path, is_private=False):
    with open(path, "rb") as f:
        key_data = f.read()
    return serialization.load_pem_private_key(key_data, password=None) if is_private \
        else serialization.load_pem_public_key(key_data)

vip_pub = load_key("keys/vip_public.pem")
vip_priv = load_key("keys/vip_private.pem", is_private=True)
staff_pub = load_key("keys/staff_public.pem")
staff_priv = load_key("keys/staff_private.pem", is_private=True)

# === RSA Encryption/Decryption ===
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

# === JSON to Protobuf (RSA-encrypted) ===
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

# === Decryption ===
def decrypt_event_fields(event: Event):
    event.vip_data.vip_lounge_location = decrypt_rsa(vip_priv, event.vip_data.vip_lounge_location)
    event.vip_data.vip_contact = decrypt_rsa(vip_priv, event.vip_data.vip_contact)
    event.vip_data.exclusive_sessions[:] = [decrypt_rsa(vip_priv, s) for s in event.vip_data.exclusive_sessions]

    event.staff_data.internal_briefing = decrypt_rsa(staff_priv, event.staff_data.internal_briefing)
    event.staff_data.security_codes[:] = [decrypt_rsa(staff_priv, s) for s in event.staff_data.security_codes]

# === Encode Path ===
def encode():
    with open("event.json", "r") as f:
        json_data = json.load(f)

    event = from_json(json_data)
    #public_payload = "https://www.space.com/astronomy/astronomers-turn-up-missing-matter-in-the-largest-structures-in-the-cosmos-the-models-were-right"
    # Extract non-sensitive event metadata
    base_fields = MessageToDict(event, preserving_proto_field_name=True)
    base_fields.pop("vip_data", None)
    base_fields.pop("staff_data", None)

    # Compact JSON and URL encode
    compact_json = json.dumps(base_fields, separators=(",", ":"))
    base64_bytes = base64.b64encode(compact_json.encode("utf-8"))
    encoded_payload = urllib.parse.quote(base64_bytes.decode("utf-8"))

    # Build the final URL
    public_payload = f"https://sumanair.github.io/scanner/l1.html?data={encoded_payload}"
    print(f"Public url : {public_payload}")

    # Encode VIP + STAFF as fractal bitstream
    bitstream = encode_sections_protobuf({
        "VIP": event.vip_data,
        "STAFF": event.staff_data
    })

    # Select best QR version
    matrix = find_suitable_qr_matrix(bitstream, public_payload)

    # Render image with T-square fractals
    img = render_qr_with_t_squares(matrix, bitstream, module_size=10)
    img.save("fractalized_qr.png")

    with open("event_rsa.bin", "wb") as f:
        f.write(event.SerializeToString())

    print("✅ Encoded QR with fractals saved to 'fractalized_qr.png'")


# === Decode Path ===
# def decode():
#     bitstream = extract_bitstream_from_qr("fractalized_qr.png", module_size=10)
#     #bitstream = ''.join(f'{byte:08b}' for byte in bitstream_bytes)
#     # Ensure length is divisible by 8
#     bitstream = bitstream[:len(bitstream) - (len(bitstream) % 8)]

#     # Convert binary string to raw bytes
#     compressed = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))

#     # Decode using protobuf
#     sections = decode_sections_protobuf(compressed, {
#         "VIP": AccessLevelVIP,
#         "STAFF": AccessLevelStaff,
#     })


#     # Decrypt sections
#     vip = sections["VIP"]
#     staff = sections["STAFF"]

#     decrypted_vip = AccessLevelVIP(
#         vip_lounge_location=decrypt_rsa(vip_priv, vip.vip_lounge_location),
#         vip_contact=decrypt_rsa(vip_priv, vip.vip_contact),
#         exclusive_sessions=[decrypt_rsa(vip_priv, s) for s in vip.exclusive_sessions]
#     )

#     decrypted_staff = AccessLevelStaff(
#         internal_briefing=decrypt_rsa(staff_priv, staff.internal_briefing),
#         security_codes=[decrypt_rsa(staff_priv, s) for s in staff.security_codes],
#         requires_background_check=staff.requires_background_check
#     )

#     print("🔓 Decrypted VIP Data:\n", decrypted_vip)
#     print("🔓 Decrypted STAFF Data:\n", decrypted_staff)

import re

def decode():
    bitstream = extract_bitstream_from_qr("fractalized_qr.png", module_size=10)
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


# === Entrypoint ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["encode", "decode"], required=True)
    args = parser.parse_args()

    if args.mode == "encode":
        encode()
    elif args.mode == "decode":
        decode()
