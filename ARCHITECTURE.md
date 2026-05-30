# 🏗️ Pipeline & Project Architecture — Digital Signer

This document describes the **internal workings** of the Digital Signer application, including the module architecture, the data pipeline of each feature, and the cryptographic algorithms used.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Crypto Module — Cryptographic Core](#crypto-module--cryptographic-core)
- [Utils Module — File Utilities](#utils-module--file-utilities)
- [GUI Module — User Interface](#gui-module--user-interface)
- [Pipeline: Key Generation](#pipeline-key-generation)
- [Pipeline: Interactive Digital Signing \& Envelope Selection](#pipeline-interactive-digital-signing--envelope-selection)
- [Pipeline: Signature Verification \& Backward Compatibility](#pipeline-signature-verification--backward-compatibility)
- [Pipeline: Opening Digital Envelope](#pipeline-opening-digital-envelope)
- [Cryptographic Algorithms](#cryptographic-algorithms)
- [Module Dependency Diagram](#module-dependency-diagram)

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────┐
│                   GUI Layer (PyQt6)                 │
│        main_window.py      │       views.py        │
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
├── requirements.txt         # Dependencies: PyQt6
│
├── core/                    # 🧠 Core custom cryptographic algorithms
│   ├── crypto_rsa.py        # Custom RSA algorithm implementation
│   ├── crypto_aes.py        # Custom AES-256-CTR algorithm
│   └── crypto_hash.py       # Custom Hash implementation (SHA-256)
│
├── controller/              # ⚙️ Business logic (independent of GUI)
│   ├── key_manager.py       # Generate, load, list RSA key pairs
│   ├── signer.py            # Digital signing & verification
│   └── envolope.py          # Create & open hybrid digital envelopes
│
├── utils/                   # 🛠️ File I/O utilities
│   └── file_handler.py      # Save/load .sig.json & .env.json
│
├── gui/                     # 🖥️ PyQt6 User Interface
│   ├── main_window.py       # Main window, Sidebar, QStackedWidget
│   └── views.py             # Interfaces: KeyManagerView, SignerView, VerifierView
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

Hybrid digital envelope (encryption + signing) over the plain text content.

| Function | Description |
|---|---|
| `create_envelope(content, recipient_pub, sender_priv)` | Creates a digital envelope → returns an envelope dictionary |
| `open_envelope(envelope, recipient_priv, sender_pub)` | Opens envelope → returns `(content_str, sig_valid)` |

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

- Initializes `QMainWindow` with a sleek dark slate theme.
- Contains a Sidebar and a `QStackedWidget` to switch between views: **KeyManagerView**, **SignerView**, **VerifierView**.

### `views.py` — Application Views

- **KeyManagerView**: Displays key lists from `key_manager`, UI to generate or import keys.
- **SignerView**: UI for signing. Focuses purely on digital signatures of text content. Prompts the user using an interactive confirmation box to determine if the signature should be sealed inside a digital envelope.
- **VerifierView**: UI for verifying signatures or opening envelopes. Automatically detects file type and adjusts UI.

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

## Pipeline: Interactive Digital Signing & Envelope Selection

When the user initiates a signature, the system shows an interactive selection dialog (Yes/No/Cancel) to decide if the document should be wrapped inside a digital envelope.

```text
[User: selects private key + inputs text + clicks Sign]
        │
        ▼
SignerView.sign_document()
        │
        ▼
[Interactive Dialog Prompt: QMessageBox]
"Bạn có muốn đóng gói tài liệu này trong Bao Thư Số không?"
        │
        ├─────► [Yes] (Produce Envelope)
        │        │
        │        ├─ Check for selected recipient's Public Key
        │        ├─ key_manager.load_private_key() → sender's priv
        │        ├─ key_manager.load_public_key() → recipient's pub
        │        ├─ envelope.create_envelope(doc_text, recipient_pub, sender_priv)
        │        │    ├─ Encrypt text using Custom AES-256-CTR
        │        │    ├─ Encrypt AES key using Recipient's Public Key
        │        │    └─ Sign envelope payload using Sender's Private Key
        │        └─ file_handler.save_envelope_file(envelope, path) → *.env.json
        │
        ├─────► [No] (Produce Standard Digital Signature)
        │        │
        │        ├─ key_manager.load_private_key() → sender's priv
        │        ├─ signer.sign(doc_text, sender_priv)
        │        └─ file_handler.save_signature_file(doc_text, sig_b64, pub_pem, path) → *.sig.json
        │
        └─────► [Cancel]
                 │
                 └─ Abort operation
```

---

## Pipeline: Signature Verification & Backward Compatibility

The system is designed with backward compatibility. It can verify modern plain-text signatures as well as legacy signatures containing hand-drawn/image canvas components.

```text
[User loads .sig.json file]
        │
        ▼
VerifierView.verify_signature_action()
        │
        ├─ file_handler.load_file(path) → (data: dict, type: "signature")
        │
        ├─ Parse data.content as JSON
        │        │
        │        ├─── [Has canvas_image?] (Legacy format)
        │        │      └─ Reconstruct: text_part + "\n---CANVAS---\n" + canvas_image
        │        │
        │        └─── [No canvas_image?] (Modern format)
        │               └─ Reconstruct: text_part
        │
        └─ signer.verify(full_content_to_sign, signature, public_key)
                 │
                 ├─ [Verify success] → ✅ Displays VALID
                 └─ [Verify failed]  → ❌ Displays INVALID
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
        ├─ [Step 1] Verify sender's signature on the payload metadata
        │        → sig_valid: True / False
        │
        ├─ [Step 2] Decrypt AES key using Recipient's RSA Private Key
        │        → aes_key
        │
        ├─ [Step 3] Decrypt content using AES-256-CTR (Custom)
        │        → Original payload
        │
        └─ Return (content_str, sig_valid)
                 │
                 ▼
        VerifierView displays text content + sender's signature verification status
```

---

## Cryptographic Algorithms

| Purpose | Algorithm | Details |
|---|---|---|
| Key Generation | Custom RSA | 2048-bit |
| Content Encryption | AES-256-CTR (Custom) | Key 256-bit, Nonce 12-byte |
| AES Key Encryption | Custom RSA | Encrypted with Recipient's Public Key |
| Digital Signing | Custom RSA | Signed with Sender's Private Key |
| Encoding output | Base64 | Used for binary data inside JSON formats |

---

> **Design Principle:** The `controller/`, `core/` and `utils/` modules are **completely independent** of the GUI — they can be imported and used from pure Python scripts without a user interface.
