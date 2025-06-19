from PIL import Image, ImageDraw

# === CONFIGURATION ===
DEBUG = True  # 🔁 Set to False for production
#FRACTAL_COLOR = (255, 0, 0, 200) if DEBUG else (0, 0, 0, 255)
FRACTAL_COLOR = (255, 0, 0, 255)  # 🔴 Fully opaque red for max visibility
DUMMY_FILLERS = [0b10101010, 0b01010101, 0b11110000, 0b00001111, 0b11001100, 0b00110011]

def generate_t_square_tile(data_byte: int, size: int = 10) -> Image.Image:
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

def render_qr_with_t_squares(matrix, bitstream: str, module_size: int = 10) -> Image.Image:
    print(f"[ENCODE] Total bits to embed: {len(bitstream)}")
    qr_size = len(matrix)
    available_black_tiles = sum(1 for row in matrix for mod in row if mod)
    print(f"[DEBUG] 📦 Available black tiles: {available_black_tiles}")

    image_size = qr_size * module_size
    img = Image.new("RGB", (image_size, image_size), "white")

    bit_chunks = [bitstream[i:i+8] for i in range(0, len(bitstream), 8)]
    bit_pointer = 0
    dummy_pointer = 0
    print(f"[DEBUG] ⬛ Embedding {len(bit_chunks)} bytes across tiles")

    for y in range(qr_size):
        for x in range(qr_size):
            top_left = (x * module_size, y * module_size)

            if matrix[y][x]:  # Black QR module
                base_tile = Image.new("RGB", (module_size, module_size), "black")

                if bit_pointer < len(bit_chunks):
                    byte = int(bit_chunks[bit_pointer], 2)
                    if bit_pointer <= 2:
                        print(f"[ENCODE] Tile ({x}, {y}) embeds byte: {byte:08b}")
                        base_tile.save(f"tile_{bit_pointer - 1}_debug.png")
                    bit_pointer += 1
                else:
                    byte = DUMMY_FILLERS[dummy_pointer % len(DUMMY_FILLERS)]
                    dummy_pointer += 1

                overlay = generate_t_square_tile(byte, module_size)
                base_tile.paste(overlay, (0, 0), overlay)
                tile = base_tile
            else:
                tile = Image.new("RGB", (module_size, module_size), "white")

            img.paste(tile, top_left)

    # Count how many original modules were black
    black_count = sum(1 for row in matrix for mod in row if mod)
    print(f"[RENDER] Final QR matrix black tiles: {black_count}")
    return img
