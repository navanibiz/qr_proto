from PIL import Image, ImageDraw
from typing import Tuple

# === CONFIGURATION ===
DEBUG = True  # 🔁 Set to False for production
FRACTAL_COLOR = (255, 0, 0, 255)  # 🔴 Fully opaque red for data bits
FILLER_COLOR = (0, 0, 255, 255)   # 🔵 Opaque blue for filler
DUMMY_FILLERS = [0b10101010, 0b01010101, 0b11110000, 0b00001111, 0b11001100, 0b00110011]


def generate_t_square_tile(data_byte: int, size: int = 10) -> Image.Image:
    tile = Image.new("RGBA", (size, size), (255, 255, 255, 0))
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
    if depth <= 0 or size < 1:
        return

    third = size // 3
    center_x = x + third
    center_y = y + third
    draw.rectangle([center_x, center_y, center_x + third, center_y + third], fill=FRACTAL_COLOR)

    draw_recursive_t_square(draw, x, y, third, depth - 1)
    draw_recursive_t_square(draw, x + 2 * third, y, third, depth - 1)
    draw_recursive_t_square(draw, x, y + 2 * third, third, depth - 1)
    draw_recursive_t_square(draw, x + 2 * third, y + 2 * third, third, depth - 1)


def generate_recursive_t_square_tile(data_byte: int, size: int = 27, depth: int = 2) -> Image.Image:
    tile = Image.new("RGBA", (size, size), (255, 255, 255, 0))
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


def generate_recursive_t_square_tile_from_bytes(byte_values: list[int], size: int, depth: int, color=FRACTAL_COLOR) -> Image.Image:
    expected_len = 8 ** (depth - 1)
    assert len(byte_values) == expected_len, f"Expected {expected_len} bytes for depth={depth}"

    #base_tile = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    base_tile = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base_tile)

    region_size = size // 3
    bit_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    if depth == 1:
        current_byte = byte_values[0]
        for i, (col, row) in enumerate(bit_positions):
            if (current_byte >> (7 - i)) & 1:
                x = col * region_size
                y = row * region_size
                draw.rectangle([x, y, x + region_size - 1, y + region_size - 1], fill=color)
    else:
        sub_bytes_per_region = 8 ** (depth - 2)
        for i, (col, row) in enumerate(bit_positions):
            start = i * sub_bytes_per_region
            end = start + sub_bytes_per_region
            if end > len(byte_values):
                continue
            sub_bytes = byte_values[start:end]
            x = col * region_size
            y = row * region_size
            sub_tile = generate_recursive_t_square_tile_from_bytes(sub_bytes, region_size, depth - 1, color=color)
            base_tile.paste(sub_tile, (x, y), sub_tile)

    return base_tile

from typing import Tuple
from PIL import Image

def render_qr_with_t_squares_partial(
    matrix, bitstream: str, module_size: int = 10, depth: int = 1,
    start_tile: int = 0, img: Image.Image = None, color: Tuple[int, int, int] = (255, 0, 0)
) -> Tuple[Image.Image, int]:
    qr_size = len(matrix)
    if img is None:
        image_size = qr_size * module_size
        img = Image.new("RGB", (image_size, image_size), "white")

    bytes_per_tile = 8 ** (depth - 1)
    bits_per_tile = 8 * bytes_per_tile
    bit_chunks = [
        bitstream[i:i + bits_per_tile].ljust(bits_per_tile, '0')
        for i in range(0, len(bitstream), bits_per_tile)
    ]

    tile_idx = 0
    written = 0
    for y in range(qr_size):
        for x in range(qr_size):
            if not matrix[y][x]:
                continue
            if tile_idx < start_tile:
                tile_idx += 1
                continue
            if written >= len(bit_chunks):
                return img, tile_idx

            top_left = (x * module_size, y * module_size)
            base_tile = Image.new("RGB", (module_size, module_size), "black")
            chunk_bits = bit_chunks[written]
            byte_values = [int(chunk_bits[i:i + 8], 2) for i in range(0, len(chunk_bits), 8)]
            overlay = generate_recursive_t_square_tile_from_bytes(byte_values, module_size, depth=depth, color=color)
            base_tile.paste(overlay, (0, 0), overlay)
            img.paste(base_tile, top_left)

            written += 1
            tile_idx += 1

    return img, tile_idx
