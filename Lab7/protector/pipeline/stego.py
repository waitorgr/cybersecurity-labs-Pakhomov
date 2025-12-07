from PIL import Image

def _bytes_to_bits(data: bytes):
    for b in data:
        for i in reversed(range(8)):
            yield (b >> i) & 1

def _bits_to_bytes(bits):
    b = 0
    out = bytearray()
    count = 0
    for bit in bits:
        b = (b << 1) | bit
        count += 1
        if count == 8:
            out.append(b)
            b = 0
            count = 0
    return bytes(out)

def embed_lsb(cover_path: str, payload: bytes, out_path: str):
    img = Image.open(cover_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    w, h = img.size
    pixels = img.load()
    total_channels = 3 if img.mode == 'RGB' else 4
    capacity = w * h * total_channels
    needed = len(payload) * 8 + 32  # 32 біти для збереження довжини
    if needed > capacity:
        raise ValueError("Cover image too small for payload")
    # Запакувати довжину
    length = len(payload)
    length_bits = [(length >> i) & 1 for i in reversed(range(32))]
    bits = iter(length_bits + list(_bytes_to_bits(payload)))
    for y in range(h):
        for x in range(w):
            px = list(pixels[x, y])
            for c in range(total_channels):
                try:
                    bit = next(bits)
                except StopIteration:
                    break
                px[c] = (px[c] & ~1) | bit
            pixels[x, y] = tuple(px)
    img.save(out_path, format='PNG')
    return out_path

def extract_lsb(container_path: str):
    img = Image.open(container_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    w, h = img.size
    pixels = img.load()
    total_channels = 3 if img.mode == 'RGB' else 4

    # Читати довжину (32 біти)
    it = []
    for y in range(h):
        for x in range(w):
            px = pixels[x, y]
            for c in range(total_channels):
                it.append(px[c] & 1)
                if len(it) == 32:
                    break
            if len(it) == 32:
                break
        if len(it) == 32:
            break
    length = 0
    for b in it:
        length = (length << 1) | b

    # Читати payload
    bits = []
    count = 0
    for y in range(h):
        for x in range(w):
            px = pixels[x, y]
            for c in range(total_channels):
                if count < 32:
                    count += 1
                    continue
                if len(bits) >= length * 8:
                    break
                bits.append(px[c] & 1)
            if len(bits) >= length * 8:
                break
        if len(bits) >= length * 8:
            break
    return _bits_to_bytes(bits)
