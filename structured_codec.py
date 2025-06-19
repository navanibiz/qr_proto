import zlib

def encode_sections_protobuf(sections: dict) -> str:
    full_bytes = b""

    for name, proto_obj in sections.items():
        name_bytes = name.encode()
        content_bytes = proto_obj.SerializeToString()

        full_bytes += len(name_bytes).to_bytes(1, "big")
        full_bytes += name_bytes
        full_bytes += len(content_bytes).to_bytes(2, "big")
        full_bytes += content_bytes

    compressed = zlib.compress(full_bytes)

    # ⏱️ Add total bit length as first 2 bytes (big endian)
    total_bits = len(compressed) * 8
    header = total_bits.to_bytes(2, "big")
    final_bytes = header + compressed

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

    decompressed = zlib.decompress(byte_data)


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
