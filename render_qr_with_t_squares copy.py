from PIL import Image, ImageDraw

# === CONFIGURATION ===
DEBUG = True  # 🔁 Set to False for production
FRACTAL_COLOR = (255, 0, 0, 255)  # 🔴 Fully opaque red for max visibility
DUMMY_FILLERS = [0b10101010, 0b01010101, 0b11110000, 0b00001111, 0b11001100, 0b00110011]
FILLER_COLOR = (0, 0, 255, 255)  # 🔵 Opaque blue for fillers


def generate_t_square_tile(data_byte: int, size: int = 10) -> Image.Image:
    """
    Generates a basic 3x3 T-square fractal tile based on a single byte of data.

    Parameters:
    - data_byte: An integer (0–255) where each bit determines whether to fill a region.
    - size: The size (in pixels) of the full tile. Default is 10x10 pixels.

    Returns:
    - A transparent RGBA image of shape (size x size) with black subregions
      filled according to the data bits.
    
    Bit-to-position mapping (each bit turns on a square in the 3x3 grid):
        0 1 2
        3   4
        5 6 7

    What this DOES:
    - Encodes 8 bits of information visually into a grid pattern,
      effectively creating a t-square pattern.
    - Fills only non-center positions (i.e., omits the center cell at (1,1)).
    - Outputs a transparent tile that can overlay onto other images.

    What this DOES NOT do (yet):
    - No recursive T-square logic.
    - Does not use self-similarity to visually encode deeper data hierarchy.
    - All "black squares" are flat filled rectangles (no fractal detail).

    Scope for recursion:
    - Each black region could itself be replaced by a smaller T-square tile.
    - This allows visual nesting (fractal compression) for multilevel roles or data depth.
    """
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # transparent tile
    draw = ImageDraw.Draw(tile)

    region_size = size // 3
    bit_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    for i, (col, row) in enumerate(bit_positions):
        if (data_byte >> (7 - i)) & 1:
            x0 = col * region_size
            y0 = row * region_size
            x1 = x0 + region_size
            y1 = y0 + region_size
            draw.rectangle([x0, y0, x1, y1], fill=FRACTAL_COLOR)

    return tile

def draw_recursive_t_square(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, depth: int):
    """
    Draw a recursive T-square fractal starting at (x, y) with the given size and recursion depth.
    Fills the center square and recursively draws on four corners.
    """
    if depth <= 0 or size < 1:
        return

    third = size // 3
    center_x = x + third
    center_y = y + third
    draw.rectangle([center_x, center_y, center_x + third, center_y + third], fill=FRACTAL_COLOR)

    # Recursive calls on four corners
    draw_recursive_t_square(draw, x, y, third, depth - 1)  # top-left
    draw_recursive_t_square(draw, x + 2 * third, y, third, depth - 1)  # top-right
    draw_recursive_t_square(draw, x, y + 2 * third, third, depth - 1)  # bottom-left
    draw_recursive_t_square(draw, x + 2 * third, y + 2 * third, third, depth - 1)  # bottom-right

def generate_recursive_t_square_tile(data_byte: int, size: int = 27, depth: int = 2) -> Image.Image:
    """
    Generates a T-square tile where each active bit recursively embeds a smaller T-square tile.
    
    Parameters:
    - data_byte: 8-bit integer to encode into the tile
    - size: Size of the full tile (should be divisible by 3**depth for clean recursion)
    - depth: Number of recursive levels. At depth=1, behaves like a flat 3x3 T-square

    Returns:
    - An RGBA image with recursively embedded T-square structures
    """

    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tile)

    region_size = size // 3
    bit_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    for i, (col, row) in enumerate(bit_positions):
        if (data_byte >> (7 - i)) & 1:
            x = col * region_size
            y = row * region_size
            draw_recursive_t_square(draw, x, y, region_size, depth)

    return tile

# def render_qr_with_t_squares(matrix, bitstream: str, module_size: int = 10) -> Image.Image:
#     print(f"[ENCODE] Total bits to embed: {len(bitstream)}")
#     qr_size = len(matrix)
#     available_black_tiles = sum(1 for row in matrix for mod in row if mod)
#     print(f"[DEBUG] \U0001f4e6 Available black tiles: {available_black_tiles}")

#     image_size = qr_size * module_size
#     img = Image.new("RGB", (image_size, image_size), "white")

#     bit_chunks = [bitstream[i:i+8] for i in range(0, len(bitstream), 8)]
#     bit_pointer = 0
#     dummy_pointer = 0
#     print(f"[DEBUG] ⬛ Embedding {len(bit_chunks)} bytes across tiles")

#     for y in range(qr_size):
#         for x in range(qr_size):
#             top_left = (x * module_size, y * module_size)

#             if matrix[y][x]:  # Black QR module
#                 base_tile = Image.new("RGB", (module_size, module_size), "black")

#                 if bit_pointer < len(bit_chunks):
#                     byte = int(bit_chunks[bit_pointer], 2)
#                     if bit_pointer <= 2:
#                         print(f"[ENCODE] Tile ({x}, {y}) embeds byte: {byte:08b}")
#                         base_tile.save(f"tile_{bit_pointer - 1}_debug.png")
#                     bit_pointer += 1
#                 else:
#                     byte = DUMMY_FILLERS[dummy_pointer % len(DUMMY_FILLERS)]
#                     dummy_pointer += 1

#                 overlay = generate_recursive_t_square_tile(byte, module_size, depth=2)
#                 base_tile.paste(overlay, (0, 0), overlay)
#                 tile = base_tile
#             else:
#                 tile = Image.new("RGB", (module_size, module_size), "white")

#             img.paste(tile, top_left)

#     black_count = sum(1 for row in matrix for mod in row if mod)
#     print(f"[RENDER] Final QR matrix black tiles: {black_count}")
#     return img


def render_qr_with_t_squares(matrix, bitstream: str, module_size: int = 10, depth: int = 1) -> Image.Image:
    print(f"[ENCODE] Total bits to embed: {len(bitstream)}")
    qr_size = len(matrix)
    available_black_tiles = sum(1 for row in matrix for mod in row if mod)
    print(f"[DEBUG] 📦 Available black tiles: {available_black_tiles}")

    image_size = qr_size * module_size
    img = Image.new("RGB", (image_size, image_size), "white")

    bytes_per_tile = 8 ** (depth - 1)
    bits_per_tile = 8 * bytes_per_tile  # 8, 64, 512, ...
    bit_chunks = [
        bitstream[i:i + bits_per_tile].ljust(bits_per_tile, '0')
        for i in range(0, len(bitstream), bits_per_tile)
    ]
    bit_pointer = 0
    dummy_pointer = 0
    print(f"[DEBUG] ⬛ Embedding {len(bit_chunks)} chunks across tiles, depth={depth}, bits/tile={bits_per_tile}")

    for y in range(qr_size):
        for x in range(qr_size):
            top_left = (x * module_size, y * module_size)

            if matrix[y][x]:  # Black QR module
                base_tile = Image.new("RGB", (module_size, module_size), "black")

                if bit_pointer < len(bit_chunks):
                    chunk_bits = bit_chunks[bit_pointer]
                    byte_values = [int(chunk_bits[i:i + 8], 2) for i in range(0, len(chunk_bits), 8)]

                    if bit_pointer <= 2:
                        print(f"[ENCODE] Tile ({x}, {y}) embeds: {chunk_bits}")
                        base_tile.save(f"tile_{bit_pointer - 1}_debug.png")

                    overlay = generate_recursive_t_square_tile_from_bytes(byte_values, module_size, depth=depth)
                    bit_pointer += 1
                else:
                    filler_bytes = [DUMMY_FILLERS[dummy_pointer % len(DUMMY_FILLERS)]] * bytes_per_tile
                    dummy_pointer += 1
                    #overlay = generate_recursive_t_square_tile_from_bytes(filler_bytes, module_size, depth=depth)
                    overlay = generate_recursive_t_square_tile_from_bytes(
                        filler_bytes, module_size, depth=depth, color=FILLER_COLOR
                    )

                base_tile.paste(overlay, (0, 0), overlay)
                tile = base_tile
            else:
                tile = Image.new("RGB", (module_size, module_size), "white")

            img.paste(tile, top_left)

    print(f"[RENDER] Final QR matrix black tiles: {available_black_tiles}")
    return img

#def generate_recursive_t_square_tile_from_bytes(byte_values: list[int], size: int, depth: int) -> Image.Image:
def generate_recursive_t_square_tile_from_bytes(byte_values: list[int], size: int, depth: int, color=FRACTAL_COLOR) -> Image.Image:

    expected_len = 8 ** (depth - 1)
    assert len(byte_values) == expected_len, f"Expected {expected_len} bytes for depth={depth}"

    base_tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_tile)

    region_size = size // 3
    bit_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    current_byte = byte_values[0]

    if depth == 1:
        for i, (col, row) in enumerate(bit_positions):
            if (current_byte >> (7 - i)) & 1:
                x = col * region_size
                y = row * region_size
                #draw.rectangle([x, y, x + region_size - 1, y + region_size - 1], fill=FRACTAL_COLOR)
                draw.rectangle([x, y, x + region_size - 1, y + region_size - 1], fill=color)
    else:
        sub_bytes_per_region = 8 ** (depth - 2)
        for i, (col, row) in enumerate(bit_positions):
            if (current_byte >> (7 - i)) & 1:
                start = 1 + i * sub_bytes_per_region
                end = start + sub_bytes_per_region
                if end > len(byte_values):  # ⛔ avoid slicing errors
                    continue
                sub_bytes = byte_values[start:end]
                x = col * region_size
                y = row * region_size
                #sub_tile = generate_recursive_t_square_tile_from_bytes(sub_bytes, region_size, depth - 1)
                sub_tile = generate_recursive_t_square_tile_from_bytes(sub_bytes, region_size, depth - 1, color=color)
                base_tile.paste(sub_tile, (x, y), sub_tile)

    return base_tile
