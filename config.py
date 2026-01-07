# config.py

# --- General Encoding Parameters ---
FILLER_TILE_COUNT = 100  # Must match encoder filler tile count
DUMMY_FILLERS = [
    0b10101010, 0b01010101,
    0b11110000, 0b00001111,
    0b11001100, 0b00110011
]

# --- Tile Colors (BGRA format) ---
FILLER_COLOR_BLUE   = (255, 0,   0,   255)  # Blue
FILLER_COLOR_PURPLE = (200, 0,   200, 255)  # Purple
HEADER_COLOR        = (0,   0,   255, 255)  # Red

# --- Tile Layer Parameters ---
HEADER_DEPTH = 1
BITS_PER_TILE = 8
MODULE_SIZE = 10
MODULE_SIZE_RECURSIVE_CANDIDATES = [27, 81]

PUBLIC_PAYLOAD_URL="https://sumanair.github.io/scanner/l1.html?data"
