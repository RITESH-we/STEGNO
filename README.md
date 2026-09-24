# 🔒 Dual-Layer Image Steganography System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Encryption-AES--256--CBC-red.svg)](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
[![OpenCV](https://img.shields.io/badge/Library-OpenCV%20%7C%20NumPy-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/RITESH-we/STEGNO/pulls)

A secure, dual-layer covert communication tool developed in Python. Combines **AES-256-CBC cryptographic encryption** with **spatial-domain pixel steganography** to hide confidential data within lossless RGB images without introducing perceptible visual artifacts.

---

## 🏛️ Security Architecture & Workflow

Traditional steganography only conceals the *presence* of a message—if extracted by an adversary, the plaintext is exposed. This system implements a **two-tier defense-in-depth model**:

1. **Cryptographic Layer (Confidentiality):** The plaintext is padded (PKCS7) and encrypted using **AES-256-CBC** with a unique Initialization Vector (IV) and a key derived via **SHA-256**.
2. **Steganographic Layer (Covert Carrier):** The resulting encrypted payload (IV + Ciphertext) is embedded into the RGB matrix of a carrier image utilizing key-derived pixel permutation masks.

```text
                     [ SENDER WORKFLOW ]
   [ Secret Message ]
           │
           ▼
┌───────────────────────┐
│   AES-256-CBC Layer   │ ◄─── Passphrase (SHA-256 Key Derivation)
│ (PKCS7 + 16-byte IV)  │
└──────────┬────────────┘
           │ [ Encrypted Ciphertext ]
           ▼
┌───────────────────────┐
│ Pixel Embedding Layer │ ◄─── Carrier Image (PNG / Lossless RGB)
│  (XOR Stego Mapping)  │
└──────────┬────────────┘
           │
           ▼
   [ 🖼️ Stego Image ] ──────────────► [ Insecure Transmission Channel ]
                                                        │
                     [ RECEIVER WORKFLOW ]              │
                                                        ▼
┌───────────────────────┐                      [ 🖼️ Stego Image ]
│ Extraction Layer      │ ◄─── Passphrase
│ (Length Header + IV)  │
└──────────┬────────────┘
           │ [ Extracted Ciphertext ]
           ▼
┌───────────────────────┐
│   AES-256 Decryption  │ ◄─── Passphrase
│ (Unpad Verification)  │
└──────────┬────────────┘
           │
           ▼
   [ Secret Message ]
```

---

## ✨ Features

* **Military-Grade Cryptography:** Employs AES-256-CBC with PKCS7 padding to guarantee zero-knowledge confidentiality even if steganographic presence is suspected.
* **Imperceptible Embedding:** High signal-to-noise ratio preserving visual fidelity across RGB channels.
* **Auto-Sizing Length Header:** Embeds a 4-byte payload length header, eliminating manual length tracking during recovery.
* **Flexible Carrier Support:** Accepts custom PNG/JPG carrier images, or auto-generates a clean carrier canvas on demand.
* **Dual Execution Modes:** Includes both an interactive/CLI utility (`stego.py`) and a research notebook (`notebooks/stego_analysis.ipynb`).

---

## 📂 Repository Structure

```text
STEGNO/
├── .gitignore                    # Ignores bytecode, venv, and checkpoints
├── LICENSE                       # MIT Open Source License
├── README.md                     # Technical documentation & usage guide
├── requirements.txt              # Dependencies (opencv-python, pycryptodome, numpy)
├── stego.py                      # Standalone CLI / Interactive Python utility
├── notebooks/
│   └── stego_analysis.ipynb      # Step-by-step Jupyter research notebook
└── assets/
    └── stego_image.png           # Example embedded stego image
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/RITESH-we/STEGNO.git
cd STEGNO
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Option A: Interactive Menu (Recommended)
Run the script without arguments for an interactive guide:
```bash
python stego.py
```

### Option B: Command-Line Interface (CLI)

#### 1. Embed Secret Message into Image
```bash
python stego.py --embed -m "Classified Alert: Target IP 192.168.1.105 compromised" -k "SecretPassphrase@2026" -o secret_output.png
```
*(Optional: Pass `-i carrier.png` to use an existing image as the carrier canvas).*

#### 2. Extract and Decrypt Secret Message
```bash
python stego.py --extract -i secret_output.png -k "SecretPassphrase@2026"
```

Output:
```text
[DECRYPTED MESSAGE]: Classified Alert: Target IP 192.168.1.105 compromised
```

### Option C: Jupyter Notebook
For research, step-by-step mathematical breakdown, and visual histogram analysis, launch the notebook:
```bash
jupyter notebook notebooks/stego_analysis.ipynb
```

---

## 🛡️ Security & Steganalysis Resistance

* **Why Plaintext Steganography Fails:** Plaintext ASCII text embedded into raw images exhibits predictable statistical entropy shifts and repetitive byte frequencies easily flagged by tools like `zsteg` or Chi-Square tests.
* **Why AES-256 Ciphertext Resists Detection:** AES-256 ciphertext exhibits near-maximum Shannon entropy (~7.99 bits/byte), making embedded bits statistically indistinguishable from high-frequency image sensor noise.
* **Lossless Requirement:** Stego images must be stored and transmitted in lossless formats (such as PNG) to prevent lossy compression algorithms (such as JPEG quantization tables) from destroying lower-order bit patterns.

---

## 👤 Author

* **Ritesh Paul** — [GitHub Profile](https://github.com/RITESH-we) | [LinkedIn](https://linkedin.com/in/riteshpaul262)
