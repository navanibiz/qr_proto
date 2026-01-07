from PIL import Image
import numpy as np

# def extract_tiles_from_image(image_path: str, module_size: int = 27):
#     """
#     Extracts a grid of RGBA tiles from a QR code image with overlaid recursive T-square tiles.
#     """
#     img = Image.open(image_path).convert("RGBA")
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

#     return tiles

def extract_tiles_from_image(image_path: str, module_size: int = 27, **kwargs):
    """
    Extracts a grid of RGBA tiles from a QR code image with overlaid recursive T-square tiles.
    Accepts and ignores extra keyword arguments for compatibility.
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
def extract_bitstream_from_recursive_qr(
    image_path,
    module_size=27,
    depth=1,
    tile_start=0,
    bit_limit=None
):
    """
    Extracts a raw bitstream from the QR image using T-square fractal decoding.
    Caller must specify depth, tile_start, and optional bit_limit in bits.

    Parameters:
    - image_path: Path to QR image file.
    - module_size: Pixel size of each tile (default 27).
    - depth: Fractal depth used for each tile (default 1).
    - tile_start: Tile index to start from (default 0).
    - bit_limit: Optional cap on number of bits to return.

    Returns:
    - bitstream: String of 0s and 1s
    """
    tiles = extract_tiles_from_image(image_path, module_size=module_size)

    black_tiles = []
    for row in tiles:
        for tile in row:
            if is_black_tile(tile):
                black_tiles.append(tile)

    if tile_start >= len(black_tiles):
        raise ValueError(f"tile_start={tile_start} exceeds available black tiles={len(black_tiles)}")

    usable_tiles = black_tiles[tile_start:]

    bits_per_tile = 8 * (8 ** (depth - 1))  # Each tile gives this many bits
    tiles_to_extract = len(usable_tiles)

    if bit_limit:
        max_tiles = (bit_limit + bits_per_tile - 1) // bits_per_tile
        tiles_to_extract = min(tiles_to_extract, max_tiles)

    bit_chunks = []
    for tile in usable_tiles[:tiles_to_extract]:
        byte_data = extract_byte_from_recursive_tile(tile, depth=depth)
        if isinstance(byte_data, bytes):
            byte_data = int.from_bytes(byte_data, byteorder='big')
        bin_str = format(byte_data, f'0{bits_per_tile}b')
        bit_chunks.append(bin_str)

    bitstream = ''.join(bit_chunks)
    if bit_limit:
        bitstream = bitstream[:bit_limit]

    print(f"[DECODE] depth={depth}, tile_start={tile_start}, bits_per_tile={bits_per_tile}")
    print(f"[DECODE] Extracted {tiles_to_extract} tiles → {len(bitstream)} bits")
    return bitstream


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
