import zlib
import json

def encode_sections_protobuf(sections: dict, depth: int = 1) -> str:
    full_bytes = b""

    for name, proto_obj in sections.items():
        name_bytes = name.encode()
        content_bytes = proto_obj.SerializeToString()

        full_bytes += len(name_bytes).to_bytes(1, "big")
        full_bytes += name_bytes
        full_bytes += len(content_bytes).to_bytes(2, "big")
        full_bytes += content_bytes

    compressed = zlib.compress(full_bytes)
    bit_length = len(compressed) * 8

    # 🧩 Create JSON header
    header_dict = {"depth": depth, "bit_length": bit_length}
    header_json = json.dumps(header_dict, separators=(",", ":")).encode("utf-8")

    if len(header_json) > 255:
        raise ValueError("Header too long to encode in a single byte length field")

    header_length = len(header_json).to_bytes(1, "big")

    # 👇 Final byte stream
    final_bytes = header_length + header_json + compressed

    return ''.join(f'{byte:08b}' for byte in final_bytes)



def decode_sections_protobuf(byte_data: bytes, message_factory: dict) -> dict:
    """
    Input:
        - byte_data: compressed byte stream starting with a 2-byte length header
        - message_factory: {section_name: ProtobufMessageClass}
    Output:
        - {section_name: parsed Protobuf object}
    """
    # try:
    #     byte_data = bytes(int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8))
    # except ValueError as e:
    #     print(f"[ERROR] Failed to convert bitstream to bytes: {e}")
    #     print(f"[DEBUG] Bad segment: {bitstream[i:i+8]}")
    #     raise

    # print(f"[DEBUG] Bitstream length: {len(bitstream)} bits")
    # print(f"[DEBUG] First 32 bits: {bitstream[:32]}")
    # print(f"[DEBUG] Byte dump (first 8 bytes): {[bitstream[i:i+8] for i in range(0, 64, 8)]}")

    def try_decompress(data: bytes) -> bytes:
        return zlib.decompress(data)

    # First try as-is.
    try:
        decompressed = try_decompress(byte_data)
    except zlib.error:
        # Handle optional 1-byte JSON header prefix from encode_sections_protobuf.
        if byte_data and len(byte_data) > 2:
            header_len = byte_data[0]
            header_start = 1
            header_end = header_start + header_len
            header_bytes = byte_data[header_start:header_end]
            if header_end <= len(byte_data) and header_bytes.startswith(b"{") and header_bytes.endswith(b"}"):
                decompressed = try_decompress(byte_data[header_end:])
            else:
                # Fall through to zlib header scan.
                decompressed = None
        else:
            decompressed = None

        if decompressed is None:
            # Attempt resync by scanning for a valid zlib header.
            candidates = (b"\x78\x01", b"\x78\x9c", b"\x78\xda")
            for i in range(len(byte_data) - 2):
                if byte_data[i:i + 2] in candidates:
                    try:
                        decompressed = try_decompress(byte_data[i:])
                        break
                    except zlib.error:
                        continue
            if decompressed is None:
                raise


    print(f"[DEBUG] Zlib input (first 16 bytes): {byte_data[:16].hex()}")

    idx = 0
    sections = {}

    while idx < len(decompressed):
        name_len = decompressed[idx]
        idx += 1
        name = decompressed[idx:idx + name_len].decode()
        idx += name_len
        content_len = int.from_bytes(decompressed[idx:idx + 2], "big")
        idx += 2
        content_bytes = decompressed[idx:idx + content_len]
        idx += content_len

        if name not in message_factory:
            raise ValueError(f"No parser found for section '{name}'")

        proto_cls = message_factory[name]
        message = proto_cls()
        message.ParseFromString(content_bytes)
        sections[name] = message

    return sections
