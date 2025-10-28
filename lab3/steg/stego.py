from PIL import Image, ImageChops
import hashlib

DELIMITER = b"<END_OF_MSG>"  # marker

def _to_bitstring(data: bytes) -> str:
    return ''.join(f"{byte:08b}" for byte in data)

def _from_bitstring(bits: str) -> bytes:
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        b.append(int(byte, 2))
    return bytes(b)

def _xor_encrypt(data: bytes, key: str) -> bytes:
    if key is None:
        return data
    key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    return bytes(out)

def hide_message(input_image_path: str, output_image_path: str, message: str, key: str = None, use_channels=(0,1,2)) -> dict:
    """
    Hides message into image LSBs across specified channels.
    use_channels: tuple of channel indices to use (0=R,1=G,2=B)
    Returns dict with metadata for analysis.
    """
    img = Image.open(input_image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size
    pixels = list(img.getdata())

    data = message.encode('utf-8') + DELIMITER
    data = _xor_encrypt(data, key)
    bits = _to_bitstring(data)

    capacity = width * height * len(use_channels)
    if len(bits) > capacity:
        raise ValueError(f"Message too large. Bits: {len(bits)}, capacity: {capacity}")

    new_pixels = []
    bit_iter = iter(bits)
    used_bits = 0

    for px in pixels:
        r, g, b = px
        channels = [r, g, b]
        for ci in use_channels:
            try:
                bit = next(bit_iter)
                channels[ci] = (channels[ci] & ~1) | int(bit)
                used_bits += 1
            except StopIteration:
                # no more bits -> leave remaining channels as is
                pass
        new_pixels.append(tuple(channels))

    out = Image.new('RGB', (width, height))
    out.putdata(new_pixels)
    out.save(output_image_path)

    # Analysis
    orig_size = None
    try:
        import os
        orig_size = os.path.getsize(input_image_path)
        new_size = os.path.getsize(output_image_path)
    except Exception:
        new_size = None

    # visual difference
    diff = ImageChops.difference(img, out)
    # count non-zero pixels in diff
    nonzero = 0
    for px in diff.getdata():
        if px != (0,0,0):
            nonzero += 1
    changed_pixels = nonzero
    total_pixels = width * height

    return {
        'width': width,
        'height': height,
        'capacity_bits': capacity,
        'used_bits': used_bits,
        'orig_size_bytes': orig_size,
        'new_size_bytes': new_size,
        'changed_pixels': changed_pixels,
        'total_pixels': total_pixels,
    }


def extract_message(image_path: str, key: str = None, use_channels=(0,1,2)) -> str:
    """
    Extracts message from image by reading LSBs in the same order channels used.
    Returns decoded message (after optional XOR decryption).
    """
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = list(img.getdata())
    bits = []
    for px in pixels:
        for ci in use_channels:
            bits.append(str(px[ci] & 1))

    bits_str = ''.join(bits)
    data = _from_bitstring(bits_str)

    # look for delimiter
    idx = data.find(DELIMITER)
    if idx == -1:
        # maybe encrypted, try decryption after XOR with key
        if key is None:
            raise ValueError('Delimiter not found; message may be missing or key required')
        dec = _xor_encrypt(data, key)
        idx = dec.find(DELIMITER)
        if idx == -1:
            raise ValueError('Delimiter not found after decryption; wrong key or no message')
        return dec[:idx].decode('utf-8', errors='replace')
    else:
        # found delimiter without decryption
        possible = data[:idx]
        if key:
            possible = _xor_encrypt(possible, key)
        return possible.decode('utf-8', errors='replace')