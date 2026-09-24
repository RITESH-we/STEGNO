#!/usr/bin/env python3
"""
Secure Image Steganography Utility (AES + LSB Spatial Pixel Embedding)
Author: Ritesh Paul (https://github.com/RITESH-we)
License: MIT
"""

import os
import sys
import argparse
import hashlib
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def derive_key(user_key: str, key_size: int = 32) -> bytes:
    """
    Derives an AES key from a passphrase using SHA-256.
    Default key_size: 32 bytes (AES-256).
    """
    return hashlib.sha256(user_key.encode('utf-8')).digest()[:key_size]


def encrypt_message(message: str, user_key: str) -> bytes:
    """
    Encrypts a plaintext string using AES-CBC with PKCS7 padding.
    Prepends the 16-byte random IV to the ciphertext.
    """
    key = derive_key(user_key, key_size=32)
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    # Payload format: 16-byte IV + AES ciphertext
    return cipher.iv + ciphertext


def decrypt_message(cipher_bytes: bytes, user_key: str) -> str:
    """
    Decrypts an AES-CBC ciphertext (with prepended 16-byte IV) using PKCS7 unpadding.
    """
    if len(cipher_bytes) < 16 + AES.block_size:
        raise ValueError("Invalid payload: data too short to contain IV and ciphertext.")

    key = derive_key(user_key, key_size=32)
    iv = cipher_bytes[:16]
    ct = cipher_bytes[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = unpad(cipher.decrypt(ct), AES.block_size)
    return decrypted_bytes.decode('utf-8')


def generate_carrier_image(width: int = 400, height: int = 400, color: tuple = (240, 240, 240)) -> np.ndarray:
    """
    Generates a clean solid-color RGB image as a carrier if no input image is provided.
    """
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    return img


def embed_payload(image: np.ndarray, data_bytes: bytes, key: str) -> np.ndarray:
    """
    Embeds encrypted payload into image pixels using XOR mask with user key.
    Includes a 4-byte length prefix to enable automatic payload length extraction.
    """
    stego = image.copy()
    h, w, c = stego.shape
    max_capacity = h * w * c

    # Pack 4-byte length header + payload
    payload_len = len(data_bytes)
    header = payload_len.to_bytes(4, byteorder='big')
    full_data = header + data_bytes

    if len(full_data) > max_capacity:
        raise ValueError(
            f"Image capacity exceeded. Needed: {len(full_data)} bytes, available: {max_capacity} bytes."
        )

    n, m, z = 0, 0, 0
    kl = 0
    key_len = len(key)

    for byte in full_data:
        mask = ord(key[kl % key_len])
        stego[n, m, z] = byte ^ mask
        n += 1
        if n >= h:
            n = 0
            m += 1
        if m >= w:
            m = 0
            z += 1
        kl += 1

    return stego


def extract_payload(image: np.ndarray, key: str, manual_length: int = None) -> bytes:
    """
    Extracts embedded encrypted bytes from stego image.
    Supports automatic length header detection or legacy manual length.
    """
    h, w, c = image.shape
    key_len = len(key)

    if manual_length is not None:
        # Legacy extraction without 4-byte header
        extracted = bytearray()
        n, m, z = 0, 0, 0
        for i in range(manual_length):
            mask = ord(key[i % key_len])
            extracted.append(image[n, m, z] ^ mask)
            n += 1
            if n >= h:
                n = 0
                m += 1
            if m >= w:
                m = 0
                z += 1
        return bytes(extracted)

    # Read 4-byte header to determine payload length
    header_bytes = bytearray()
    n, m, z = 0, 0, 0
    for i in range(4):
        mask = ord(key[i % key_len])
        header_bytes.append(image[n, m, z] ^ mask)
        n += 1
        if n >= h:
            n = 0
            m += 1
        if m >= w:
            m = 0
            z += 1

    payload_len = int.from_bytes(header_bytes, byteorder='big')
    max_payload = (h * w * c) - 4

    if payload_len <= 0 or payload_len > max_payload:
        raise ValueError("Incorrect key or image does not contain valid steganographic header.")

    extracted = bytearray()
    for i in range(payload_len):
        kl = (i + 4) % key_len
        mask = ord(key[kl])
        extracted.append(image[n, m, z] ^ mask)
        n += 1
        if n >= h:
            n = 0
            m += 1
        if m >= w:
            m = 0
            z += 1

    return bytes(extracted)


def interactive_mode():
    """Runs interactive terminal menu for embedding or extracting data."""
    print("=" * 60)
    print(" 🛡️  SECURE STEGANOGRAPHY SYSTEM (AES-256 + LSB)")
    print("=" * 60)
    print("1. Embed Secret Message into Image")
    print("2. Extract Secret Message from Image")
    print("3. Exit")
    choice = input("\nSelect an option (1-3): ").strip()

    if choice == '1':
        msg = input("\nEnter secret message to hide: ").strip()
        key = input("Enter encryption passphrase: ").strip()
        img_path = input("Enter path to carrier image (Leave blank to generate blank image): ").strip()

        if img_path and os.path.exists(img_path):
            img = cv2.imread(img_path)
            print(f"Loaded carrier image: {img_path} ({img.shape[1]}x{img.shape[0]})")
        else:
            img = generate_carrier_image(400, 400)
            print("Generated clean 400x400 carrier image.")

        encrypted = encrypt_message(msg, key)
        stego = embed_payload(img, encrypted, key)

        out_path = input("Enter output image filename (default: stego_output.png): ").strip()
        if not out_path:
            out_path = "stego_output.png"

        cv2.imwrite(out_path, stego)
        print(f"\n[SUCCESS] Secret embedded into '{out_path}' successfully!")

    elif choice == '2':
        img_path = input("\nEnter path to stego image: ").strip()
        if not os.path.exists(img_path):
            print(f"[ERROR] File not found: {img_path}")
            return

        key = input("Enter decryption passphrase: ").strip()
        img = cv2.imread(img_path)

        try:
            encrypted_payload = extract_payload(img, key)
            secret = decrypt_message(encrypted_payload, key)
            print("\n" + "=" * 40)
            print(f" [DECRYPTED MESSAGE]: {secret}")
            print("=" * 40)
        except Exception as e:
            print(f"\n[ERROR] Failed to extract or decrypt message: {e}")
            print("Double check that the passphrase is correct and the image was not compressed.")

    elif choice == '3':
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Secure Steganography Tool combining AES-256 and Image Embedding.")
    parser.add_argument("--embed", action="store_true", help="Embed message mode")
    parser.add_argument("--extract", action="store_true", help="Extract message mode")
    parser.add_argument("-i", "--image", help="Input image file path")
    parser.add_argument("-o", "--output", default="stego_output.png", help="Output image file path (PNG recommended)")
    parser.add_argument("-m", "--message", help="Secret message text to embed")
    parser.add_argument("-k", "--key", help="Passphrase for encryption/decryption")

    args = parser.parse_args()

    if not args.embed and not args.extract:
        interactive_mode()
        return

    if args.embed:
        if not args.message or not args.key:
            print("[ERROR] --message and --key are required for embedding.")
            sys.exit(1)
        if args.image and os.path.exists(args.image):
            img = cv2.imread(args.image)
        else:
            img = generate_carrier_image(400, 400)

        encrypted = encrypt_message(args.message, args.key)
        stego = embed_payload(img, encrypted, args.key)
        cv2.imwrite(args.output, stego)
        print(f"[SUCCESS] Embedded encrypted message into '{args.output}'.")

    elif args.extract:
        if not args.image or not args.key:
            print("[ERROR] --image and --key are required for extraction.")
            sys.exit(1)
        img = cv2.imread(args.image)
        try:
            extracted_bytes = extract_payload(img, args.key)
            decrypted = decrypt_message(extracted_bytes, args.key)
            print(f"\n[DECRYPTED MESSAGE]: {decrypted}")
        except Exception as e:
            print(f"[ERROR] Extraction failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
