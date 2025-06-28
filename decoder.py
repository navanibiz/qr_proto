from PIL import Image

def extract_tiles_from_image(image_path: str, module_size: int = 10):
    """
    Extracts a grid of RGB tiles from a QR code image with overlaid T-square tiles.

    Args:
        image_path (str): Path to the QR code image.
        module_size (int): Size of each QR module (in pixels).

    Returns:
        List[List[Image]]: 2D list of tile images for each module.
    """
    img = Image.open(image_path).convert("RGB")
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

from PIL import Image
import numpy as np

def is_black_tile(tile, threshold=80):  # was 50
    grayscale = tile.convert("L")
    avg = np.mean(np.array(grayscale))
    return avg < threshold


def extract_byte_from_tile(tile):
    """
    Extracts 8 bits from a T-square tile overlay.
    The tile is assumed to be a 3x3 grid with the center unused.
    """
    tile = tile.convert("RGB")
    pixels = np.array(tile)
    h, w = pixels.shape[:2]
    region_size = h // 3

    bit_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    bits = []
    for col, row in bit_positions:
        x0 = col * region_size
        y0 = row * region_size
        region = pixels[y0:y0 + region_size, x0:x0 + region_size, :]
        avg_intensity = np.mean(region)
        #bits.append(1 if avg_intensity > 100 else 0)  # threshold tuned for red overlay
        bits.append(1 if avg_intensity > 50 else 0)


    byte = 0
    for bit in bits:
        byte = (byte << 1) | bit
    return byte

def extract_bitstream_from_qr(image_path, module_size=10):
    """
    Processes a QR image and extracts the encoded fractal bitstream from T-square overlays.
    Logs positions of tiles that were actually used for decoding.
    """
    tiles = extract_tiles_from_image(image_path, module_size=module_size)

    # Step 1: Flatten with coordinates
    black_tiles = []
    used_coords = []

    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if is_black_tile(tile):
                black_tiles.append(tile)
                used_coords.append((x, y))

    if len(black_tiles) < 2:
        raise ValueError("Not enough black tiles to extract header.")
    

    # Step 2: Extract total_bits from first 2 tiles
    b0 = extract_byte_from_tile(black_tiles[0])
    b1 = extract_byte_from_tile(black_tiles[1])
    print(f"[DEBUG] First 2 header bytes from tiles: {b0:08b}, {b1:08b}")
    header_bytes = [b0, b1]
    print("📦 header_bytes:", header_bytes, type(header_bytes[0]))
    total_bits = (header_bytes[0] << 8) | header_bytes[1]
    print(f"[DECODE] Total bits to extract (from header): {total_bits}")

    # Step 3: Compute number of tiles needed
    needed_bytes = (total_bits + 7) // 8
    needed_total = 2 + needed_bytes

    print(f"[DECODE] Detected black tiles in image: {len(black_tiles)}")


    if len(black_tiles) < needed_total:
        raise ValueError(f"Only {len(black_tiles)} black tiles found, need {needed_total}.")

    # Step 4: Extract actual data
    data_bytes = []
    for i, (tile, coord) in enumerate(zip(black_tiles[2:2 + needed_bytes], used_coords[2:2 + needed_bytes])):
        x, y = coord
        byte = extract_byte_from_tile(tile)
        #print(f"[DEBUG] Byte {i} → {byte:08b}")
        data_bytes.append(byte)


    print(f"[DECODE] Total bits extracted: {total_bits}")
    #print(f"[DECODE] Tiles used (x, y): {used_coords[:2 + needed_bytes]}")

    return ''.join(f'{byte:08b}' for byte in data_bytes)[:total_bits]
