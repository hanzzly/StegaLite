# StegaLite

**StegaLite** is a lightweight, password-protected steganography tool written in Python. It provides a highly secure alternative to classic LSB steganography without relying on massive machine learning libraries like PyTorch or TensorFlow.

## Features
- **Scattered Data Dispersion**: Unlike classic LSB tools that hide data sequentially from the top-left corner, StegaLite uses a Pseudo-Random Number Generator (PRNG) to scatter the bits randomly across the image.
- **Password Protected**: The PRNG seed is generated using the SHA-256 hash of your password. Without the exact password, the data cannot be extracted, providing pseudo-cryptographic security.
- **Data Compression**: Uses `zlib` to compress your secret messages before hiding them, allowing you to store more text in a smaller image.
- **Extremely Lightweight**: Only requires standard Python libraries and `Pillow`.

## Installation

You only need `Pillow` to handle image processing.
```bash
pip install Pillow
```

## Usage

### 1. Encode (Hide a Message)
Hide a secret message inside a cover image. The output image **must** be a PNG to avoid lossy compression destroying the hidden bits.

**With Password (Recommended for maximum security):**
```bash
python stegalite.py encode cover_image.png "This is a highly classified secret." -p MySecurePassword123 -o stego_output.png
```

**Without Password (Uses default internal key, similar to SteganoGAN default behavior):**
```bash
python stegalite.py encode cover_image.png "This is a highly classified secret." -o stego_output.png
```

### 2. Decode (Extract a Message)
Extract a hidden message from an image. You must use the exact same password that was used during encoding.

**With Password:**
```bash
python stegalite.py decode stego_output.png -p MySecurePassword123
```

**Without Password:**
```bash
python stegalite.py decode stego_output.png
```

## Author
**Farhan** — [@hanzzly](https://github.com/hanzzly)
