from PIL import Image, ImageDraw

def generate_t_square_tile(data_byte: int, size: int = 10) -> Image.Image:
    tile = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(tile)

    region_size = size // 3  # ~3 pixels for 10x10
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
            draw.rectangle([x0, y0, x1, y1], fill="black")

    return tile
