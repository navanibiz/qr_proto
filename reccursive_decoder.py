from PIL import Image
import numpy as np

def extract_tiles_from_image(image_path: str, module_size: int = 27):
    """
    Extracts a grid of RGBA tiles from a QR code image with overlaid recursive T-square tiles.
    """
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    grid_size_x = width // module_size
    grid_size_y = height // module_size

    tiles = []
    for y in range(grid_size_y):
        row = []
        for x in range(grid_size_x):
            left = x * module_size
            upper = y * module_size
            tile = img.crop((left, upper, left + module_size, upper + module_size))
            row.append(tile)
        tiles.append(row)

    return tiles

def is_black_tile(tile, threshold=80):
    grayscale = tile.convert("L")
    avg = np.mean(np.array(grayscale))
    return avg < threshold

def extract_byte_from_recursive_tile(tile, depth=1):
    """
    Recursively extracts bits from a T-square tile based on the specified depth.
    Each depth level increases the number of bits by a factor of 8.
    Depth 1 = 8 bits, Depth 2 = 64 bits, Depth 3 = 512 bits, etc.
    """
    tile = tile.convert("RGBA")
    pixels = np.array(tile)
    h, w = pixels.shape[:2]

    def extract_recursive(region, current_depth):
        region_h, region_w = region.shape[:2]
        region_size = region_h // 3
        bit_positions = [
            (0, 0), (1, 0), (2, 0),
            (0, 1),         (2, 1),
            (0, 2), (1, 2), (2, 2)
        ]

        bits = []
        for col, row in bit_positions:
            x0 = col * region_size
            y0 = row * region_size
            sub_region = region[y0:y0 + region_size, x0:x0 + region_size, :]

            if current_depth == 1:
                # Sample center of subregion
                inner_third = region_size // 3
                inner_x = inner_y = inner_third
                center_region = sub_region[inner_y:inner_y + inner_third, inner_x:inner_x + inner_third, :]
                avg_intensity = np.mean(center_region[:, :, :3])  # RGB only
                bits.append(1 if avg_intensity > 50 else 0)
            else:
                bits.extend(extract_recursive(sub_region, current_depth - 1))
        return bits

    bits = extract_recursive(pixels, depth)
    byte_stream = 0
    for bit in bits:
        byte_stream = (byte_stream << 1) | bit
    total_bits = 8 ** depth
    return byte_stream.to_bytes(total_bits // 8, byteorder='big')

def extract_bitstream_from_recursive_qr(image_path, module_size=27):
    """
    Extracts the fractal bitstream from a QR image, using the embedded JSON header
    to determine depth and bit length. Assumes each tile contains a full byte.
    """
    import json

    tiles = extract_tiles_from_image(image_path, module_size=module_size)

    black_tiles = []
    used_coords = []

    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if is_black_tile(tile):
                black_tiles.append(tile)
                used_coords.append((x, y))

    if len(black_tiles) < 3:
        raise ValueError("Not enough black tiles to extract header.")

    # === Step 1: Parse header from first N bytes (e.g. until '}')
    header_bytes = []
    for tile in black_tiles[:64]:  # cap at 64 header tiles
        byte = extract_byte_from_recursive_tile(tile, depth=1)
        if isinstance(byte, bytes):  # handle bytes object
            byte = byte[0]
        header_bytes.append(byte)
        if byte == ord('}'):
            break

    try:
        header_str = bytes(header_bytes).decode("utf-8", errors="ignore")  # ignore bad chars
        json_start = header_str.find('{')
        if json_start != -1:
            header_str = header_str[json_start:]  # strip anything before {
        print("[DEBUG] Cleaned Header String:", repr(header_str))
        header = json.loads(header_str)
        depth = header["depth"]
        bit_length = header["bit_length"]
    except Exception as e:
        raise ValueError(f"Failed to parse header JSON: {e}")

    bits_per_tile = 8 * (8 ** (depth - 1))
    tiles_needed = (bit_length + bits_per_tile - 1) // bits_per_tile
    total_tiles_to_read = len(header_bytes) + tiles_needed

    if len(black_tiles) < total_tiles_to_read:
        raise ValueError(f"QR has only {len(black_tiles)} black tiles, but need {total_tiles_to_read}")

    # === Step 2: Extract payload bytes using calculated depth
    payload_tiles = black_tiles[len(header_bytes):len(header_bytes) + tiles_needed]
    bit_chunks = [
        format(int.from_bytes(extract_byte_from_recursive_tile(tile, depth=depth), byteorder='big'), f'0{bits_per_tile}b')
        for tile in payload_tiles
    ]

    full_bitstream = ''.join(bit_chunks)[:bit_length]
    print(f"[HEADER] depth={depth}, bit_length={bit_length}, bits_per_tile={bits_per_tile}")
    print(f"[DECODE] Extracted {len(payload_tiles)} tiles → {len(full_bitstream)} bits")
    return full_bitstream
