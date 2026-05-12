# 🏗️ Pipeline & Project Architecture — Digital Signer

This document describes the **internal workings** of Digital Signer, including the module architecture, the data pipeline of each feature, and the cryptographic algorithms used.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Crypto Module — Cryptographic Core](#crypto-module--cryptographic-core)
- [Utils Module — File Utilities](#utils-module--file-utilities)
- [GUI Module — User Interface](#gui-module--user-interface)
- [Pipeline: Key Generation](#pipeline-key-generation)
- [Pipeline: Digital Signing](#pipeline-digital-signing)
- [Pipeline: Signature Verification](#pipeline-signature-verification)
- [Pipeline: Creating Digital Envelope](#pipeline-creating-digital-envelope)
- [Pipeline: Opening Digital Envelope](#pipeline-opening-digital-envelope)
- [Cryptographic Algorithms](#cryptographic-algorithms)
- [Module Dependency Diagram](#module-dependency-diagram)

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────┐
│                   GUI Layer (PyQt6)                 │
│  main_window.py │ views.py │ canvas_widget.py       │
└──────────────────────┬─────────────────────────────┘
                       │ calls
┌──────────────────────▼─────────────────────────────┐
│              Crypto / Controller Layer              │
│   key_manager.py │ signer.py │ envolope.py          │
│             core/crypto_rsa.py                      │
└──────────────────────┬─────────────────────────────┘
                       │ reads/writes
┌──────────────────────▼─────────────────────────────┐
│              Utils Layer                            │
│             file_handler.py                         │
└──────────────────────┬─────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────┐
│              File System                            │
│  keys/*.pem │ *.sig.json │ *.env.json               │
└────────────────────────────────────────────────────┘
```

The architecture is divided into **3 distinct layers**, without backward dependencies (GUI → Controller/Crypto → Utils → FileSystem).

---

## Directory Structure

```text
python-digital-signature/
├── main.py                  # Entry point — initializes QApplication
├── requirements.txt         # Dependencies: cryptography, PyQt6
│
├── core/                    # Core custom cryptographic algorithms
│   └── crypto_rsa.py        # Custom RSA algorithm implementation
│
├── controller/              # Business logic (independent of GUI)
│   ├── key_manager.py       # Generate, load, list RSA key pairs
│   ├── signer.py            # Digital signing & verification
│   └── envolope.py          # Create & open hybrid digital envelopes
│
├── utils/                   # File I/O utilities
│   └── file_handler.py      # Save/load .sig.json & .env.json
│
├── gui/                     # PyQt6 User Interface
│   ├── main_window.py       # Main window, Sidebar, QStackedWidget
│   ├── views.py             # Interfaces: KeyManagerView, SignerView, VerifierView
│   └── canvas_widget.py     # Drawing/Importing signature images
│
└── keys/                    # Key pair storage (auto-generated)
    ├── alice_private.pem
    ├── alice_public.pem
    └── ...
```

---

## Crypto / Controller Module — Cryptographic Core

### `key_manager.py`

Manages the lifecycle of RSA key pairs.

| Function | Description |
|---|---|
| `generate_key_pair(name, bits)` | Generates Custom RSA keys, saves PEM to `keys/` |
| `load_private_key(path)` | Loads a private key from a PEM file |
| `load_public_key(path)` | Loads a public key from a PEM file |
| `list_key_pairs()` | Scans `keys/`, returns a list of dictionaries with key information |
| `get_public_key_pem(path)` | Reads PEM public key content as a string |

### `signer.py`

Handles digital signing and simple verification.

| Function | Description |
|---|---|
| `sign(content, private_key)` | Signs bytes/str → returns signature bytes |
| `verify(content, signature_bytes, public_key)` | Verifies the signature → True/False |

### `envolope.py`

Hybrid digital envelope (encryption + signing).

| Function | Description |
|---|---|
| `create_envelope(content, canvas_b64, recipient_pub, sender_priv)` | Creates a digital envelope → returns a dictionary |
| `open_envelope(envelope, recipient_priv, sender_pub)` | Opens envelope → (content, canvas_b64, sig_valid) |

---

## Utils Module — File Utilities

### `file_handler.py`

| Function | Description |
|---|---|
| `save_signature_file(content_str, sig_b64, pub_pem, path)` | Saves `.sig.json` |
| `save_envelope_file(envelope_dict, pub_pem, path)` | Saves `.env.json` |
| `load_file(path)` | Loads & detects file type, returns `(dict, "signature"\|"envelope")` |

---

## GUI Module — User Interface

### `main_window.py` — Main Window

- Initializes `QMainWindow` with a dark slate theme.
- Contains a Sidebar and a `QStackedWidget` to switch between views: **KeyManagerView**, **SignerView**, **VerifierView**.

### `views.py` — Application Views

- **KeyManagerView**: Displays key lists from `key_manager`, UI to generate or import keys.
- **SignerView**: UI for signing. Includes `CanvasWidget` for drawn signatures. Calls `signer.sign()` or `envolope.create_envelope()`.
- **VerifierView**: UI for verifying signatures or opening envelopes. Automatically detects file type and adjusts UI.

### `canvas_widget.py` — Signature Canvas

- Custom QWidget for free-hand drawing using `QPainter`.
- Supports importing and scaling images (`load_image`).
- Exports canvas content as Base64 PNG.

---

## Pipeline: Key Generation

```text
[User inputs name]
        │
        ▼
KeyManagerView.generate_key()
        │
        ▼
controller/key_manager.generate_key_pair(name, bits)
        │
        ├─ core.crypto_rsa.generate_rsa_keypair()
        │
        ├─ Serialize to Custom JSON-PEM format
        │
        ├─ write to keys/<name>_private.pem
        │
        └─ write to keys/<name>_public.pem
        │
        ▼
KeyManagerView refreshes key list
```

---

## Pipeline: Digital Signing

```text
[User: selects private key + inputs text/canvas + clicks Sign]
        │
        ▼
SignerView.sign_document()
        │
        ├─ canvas_b64 = canvas.get_base64_image()
        │
        ├─ key_manager.load_private_key() → tuple(d, n)
        │
        ├─ signer.sign(content, private_key)
        │        │
        │        ├─ Format content: text + canvas
        │        └─ Custom RSA sign → signature bytes
        │
        └─ file_handler.save_signature_file(content, sig_b64, pub_pem, save_path)
                 │
                 └─ output.sig.json
```

---

## Pipeline: Signature Verification

```text
[User loads .sig.json file]
        │
        ▼
VerifierView.verify_signature_action()
        │
        ├─ file_handler.load_file(path) → (data: dict, type: "signature")
        │
        └─ signer.verify(content, signature, public_key)
                 │
                 ├─ [Verify success] → ✅ Displays VALID
                 └─ [Verify failed]  → ❌ Displays INVALID
```

---

## Pipeline: Creating Digital Envelope

```text
[User: selects sender priv key + recipient pub key + content]
        │
        ▼
SignerView.sign_document(is_envelope=True)
        │
        ▼
controller/envolope.create_envelope(content, canvas, recipient_pub, sender_priv)
        │
        ├─ [Step 1] Generate random AES-256 key and nonce
        │
        ├─ [Step 2] Encrypt content using AES-256-GCM
        │
        ├─ [Step 3] Encrypt AES key using Recipient's RSA Public Key
        │
        ├─ [Step 4] Create payload: {ciphertext, nonce, encrypted_aes_key}
        │
        ├─ [Step 5] Sign payload using Sender's RSA Private Key
        │
        └─ Return envelope dict
                 │
                 ▼
        file_handler.save_envelope_file(envelope, path)
                 → output.env.json
```

---

## Pipeline: Opening Digital Envelope

```text
[User loads .env.json + selects recipient private key]
        │
        ▼
VerifierView.open_envelope_action()
        │
        ▼
controller/envolope.open_envelope(envelope, recipient_priv, sender_pub)
        │
        ├─ [Step 1] Verify sender's signature on the payload
        │        → sig_valid: True / False
        │
        ├─ [Step 2] Decrypt AES key using Recipient's RSA Private Key
        │        → aes_key
        │
        ├─ [Step 3] Decrypt content using AES-256-GCM
        │        → Original payload
        │
        └─ Return (content_str, canvas_b64, sig_valid)
                 │
                 ▼
        VerifierView displays content + sender's signature status
```

---

## Cryptographic Algorithms

| Purpose | Algorithm | Details |
|---|---|---|
| Key Generation | Custom RSA | 2048-bit (configured) |
| Content Encryption | AES-256-GCM | Key 256-bit, Nonce 12-byte |
| AES Key Encryption | Custom RSA | Encrypted with Recipient's Public Key |
| Digital Signing | Custom RSA | Signed with Sender's Private Key |
| Encoding output | Base64 | Used for binary data inside JSON formats |

---

> **Design Principle:** The `controller/`, `core/` and `utils/` modules are **completely independent** of the GUI — they can be imported and used from pure Python scripts without a user interface.
