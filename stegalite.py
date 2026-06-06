#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import random
import zlib
import hashlib
import sys
import os
try:
    from PIL import Image
except ImportError:
    print("Error: Library 'Pillow' not found. Please install it using: pip install Pillow")
    sys.exit(1)

# Message end marker (Delimiter)
DELIMITER = b'====END===='

def _text_to_bits(text_bytes):
    """Convert bytes to a list of bits (0 and 1)"""
    bits = []
    for byte in text_bytes:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits

def _bits_to_text(bits):
    """Convert a list of bits back to bytes"""
    text_bytes = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bits):
                byte |= (bits[i + j] << j)
        text_bytes.append(byte)
    return bytes(text_bytes)

def _get_pixel_sequence(width, height, password):
    """Generate a random pixel index sequence based on the password"""
    # Use SHA-256 of the password as the PRNG seed
    seed = int(hashlib.sha256(password.encode('utf-8')).hexdigest(), 16)
    random.seed(seed)

    # Create a list of all possible pixel coordinates
    pixels = [(x, y) for x in range(width) for y in range(height)]

    # Shuffle the sequence using the password seed
    random.shuffle(pixels)
    return pixels

def encode(image_path, secret_text, password, output_path):
    """Hide a message inside an image"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)

    width, height = img.size
    pixels = img.load()

    # 1. Compress text and add delimiter
    text_bytes = secret_text.encode('utf-8')
    compressed_data = zlib.compress(text_bytes) + DELIMITER

    # 2. Convert data to binary
    bit_data = _text_to_bits(compressed_data)

    # Ensure the image capacity is sufficient (3 channels per pixel)
    max_capacity = width * height * 3
    if len(bit_data) > max_capacity:
        print(f"Error: Message is too long for this image. Maximum: {max_capacity // 8} bytes.")
        sys.exit(1)

    # 3. Get the random pixel sequence
    pixel_sequence = _get_pixel_sequence(width, height, password)

    bit_idx = 0
    # 4. Insert message bits into the last bit (LSB) of each RGB channel at random pixels
    for x, y in pixel_sequence:
        if bit_idx >= len(bit_data):
            break

        r, g, b = pixels[x, y]

        if bit_idx < len(bit_data):
            r = (r & ~1) | bit_data[bit_idx]
            bit_idx += 1
        if bit_idx < len(bit_data):
            g = (g & ~1) | bit_data[bit_idx]
            bit_idx += 1
        if bit_idx < len(bit_data):
            b = (b & ~1) | bit_data[bit_idx]
            bit_idx += 1

        pixels[x, y] = (r, g, b)

    try:
        img.save(output_path, format="PNG")
        print(f"Success! Message successfully hidden in: {output_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

def decode(image_path, password):
    """Extract a message from an image"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)

    width, height = img.size
    pixels = img.load()

    # 1. Get the exact same random pixel sequence using the password
    pixel_sequence = _get_pixel_sequence(width, height, password)

    extracted_bytes = bytearray()
    bit_buffer = []
    # How many extra bytes to keep before delimiter for overlap detection
    TAIL_WINDOW = len(DELIMITER) * 2

    # 2. Read LSB from pixels according to the random sequence
    for x, y in pixel_sequence:
        r, g, b = pixels[x, y]
        bit_buffer.extend([r & 1, g & 1, b & 1])

        # Convert every complete byte from the buffer
        while len(bit_buffer) >= 8:
            byte = 0
            for j in range(8):
                byte |= (bit_buffer[j] << j)
            extracted_bytes.append(byte)
            bit_buffer = bit_buffer[8:]

            # Check for delimiter only in the recent tail — O(1) window, not O(n)
            if len(extracted_bytes) >= len(DELIMITER):
                tail = bytes(extracted_bytes[-TAIL_WINDOW:])
                if DELIMITER in tail:
                    raw_data = bytes(extracted_bytes).split(DELIMITER)[0]
                    try:
                        decompressed = zlib.decompress(raw_data)
                        return decompressed.decode('utf-8')
                    except Exception:
                        # Wrong password → zlib decompress fails
                        return None

    return None

def main():
    parser = argparse.ArgumentParser(description="Lightweight Password-Protected Steganography")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Hide a message inside an image")
    encode_parser.add_argument("image", help="Path to the cover image")
    encode_parser.add_argument("message", help="Secret message to hide")
    encode_parser.add_argument("-p", "--password", nargs="?", default="DEFAULT_SECRET_KEY_123", help="Password (optional) to secure the message")
    encode_parser.add_argument("-o", "--output", default="stego_output.png", help="Output file name (must be PNG/Lossless)")

    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Extract a message from an image")
    decode_parser.add_argument("image", help="Path to the image containing the message")
    decode_parser.add_argument("-p", "--password", nargs="?", default="DEFAULT_SECRET_KEY_123", help="Password (optional) to extract the message")

    args = parser.parse_args()

    if args.action == "encode":
        encode(args.image, args.message, args.password, args.output)
    elif args.action == "decode":
        print("Extracting message...")
        result = decode(args.image, args.password)
        if result:
            print("\n[+] Message Successfully Extracted:")
            print("-" * 30)
            print(result)
            print("-" * 30)
        else:
            print("\n[-] Failed to extract message. The image might not contain a message, or the password is WRONG.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
