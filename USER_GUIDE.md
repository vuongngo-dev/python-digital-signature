# 📖 User Guide — Digital Signer

> **Digital Signer** is a desktop application that allows you to **digitally sign** and **verify signatures** on documents, as well as securely exchange documents using **digital envelopes**.
> All cryptographic operations are performed locally on your machine — **no data is sent over the network**.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation & Execution](#installation--execution)
- [Key Management Tab](#key-management-tab-)
- [Sign Tab](#sign-tab-)
- [Verify Tab](#verify-tab-)
- [Digital Envelope](#digital-envelope)
- [File Formats](#file-formats)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## System Requirements

| Component    | Minimum Version                        |
| ------------ | -------------------------------------- |
| Python       | 3.10+                                  |
| PyQt6        | 6.6.0+                                 |
| cryptography | 42.0.0+                                |
| OS           | Windows 10, macOS 12, Linux Ubuntu 22+ |

---

## Installation & Execution

```bash
# 1. Navigate to the project directory
cd python-digital-signature

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## Key Management Tab 🔑

**The first step** before signing or verifying anything.

### Generate a New Key Pair

1. Switch to the **🔑 Key Management** tab.
2. Enter a **Key Name** (e.g., `alice`, `my-company`). Use only letters, numbers, `-`, `_`.
3. _(Optional)_ Enter a **Password** to encrypt the private key.
4. Click **➕ Generate Key**.
5. The generated key pair:
   - `alice_private.pem` — Private key (keep absolutely secret)
   - `alice_public.pem` — Public key (share freely)

> ⚠️ **Important:** If you set a password, remember it carefully. Losing the password = losing access to the private key.

### View & Share Public Key

- Select a key from the list → the PEM content is displayed in the right pane.
- Click **📋 Copy PEM** to copy, then send it to your partner via email.

### Import Someone Else's Public Key

1. Click **📥 Import Public Key**.
2. Select the `.pem` file provided by your partner.
3. The key appears in the list with a 🔓 icon (public only).

### Delete a Key

- Select a key → click **🗑️ Delete Key** → confirm. This action **cannot be undone**.

---

## Sign Tab ✍️

### Sign Standard Text

1. Switch to the **✍️ Sign Document** tab.
2. Select a **Private Key** from the dropdown (only displays keys with `_private.pem`).
3. Enter the **password** if the key is protected.
4. Enter the content in the text box, or draw/import your signature in the canvas.
5. Click **✍️ Sign** → choose where to save the `.sig.json` file.

The output `.sig.json` file contains: original content, signature image (Base64), RSA-PSS-SHA256 signature, signer's public key, timestamp.

### Create a Digital Envelope

1. Check the **Digital Envelope** option in the Sign Document tab.
2. Ensure you have selected:
   - **Sender's Private key** (for signing)
   - **Recipient's Public key** (for encryption)
   - The **Content** and **Signature** to send
3. Click **📦 Sign / Create Envelope** → save the `.env.json` file → send to the recipient.

---

## Verify Tab 🔍

### Verify Signature (`.sig.json`)

1. Switch to the **🔍 Verify** tab.
2. Click **📂 Browse File...** → select the `.sig.json` file.
3. Click **Verify**, the application automatically verifies and displays:
   - Original content and signature image
   - Signer's information
   - Result: ✅ **VALID** or ❌ **INVALID**

> The public key used for verification is **pre-embedded** within the `.sig.json` file.

### Open Digital Envelope (`.env.json`)

1. Load the `.env.json` file.
2. The UI will prompt you to select the **recipient's private key** from the dropdown.
3. Click **🔓 Verify / Open Envelope**.
4. The original content and the status of the sender's signature will be displayed.

---

## Digital Envelope

Used when you need to **both encrypt and digitally sign** for a specific recipient.

**Scenario:** Alice sends a secret document to Bob.

| Step | Action                                                                    |
| ---- | ------------------------------------------------------------------------- |
| 1    | Alice imports `bob_public.pem` into the application.                      |
| 2    | Alice creates an envelope: selects `alice` private key, `bob` public key, enters content. |
| 3    | Alice sends the `.env.json` file to Bob.                                  |
| 4    | Bob loads the file, selects `bob` private key, clicks Open Envelope.      |
| 5    | Bob reads the content and checks if Alice's signature is valid.           |

---

## File Formats

### Signature File (`.sig.json`)

```json
{
  "content": "{\"text\": \"Original text...\", \"canvas_image\": \"<Base64 PNG>\"}",
  "signature": "<Base64 signature>",
  "signer_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"
}
```

### Digital Envelope File (`.env.json`)

```json
{
  "encrypted_content": "<Base64 AES-GCM ciphertext>",
  "aes_nonce": "<Base64 nonce 12 bytes>",
  "encrypted_aes_key": "<Base64 RSA(AES key)>",
  "signature": "<Base64 signature of payload>",
  "sender_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"
}
```

### Keys (`keys/` directory)

| File                 | Description                                                      |
| -------------------- | ---------------------------------------------------------------- |
| `<name>_private.pem` | Custom RSA 2048-bit private key (JSON wrapped in PEM base64)     |
| `<name>_public.pem`  | Custom RSA 2048-bit public key (JSON wrapped in PEM base64)      |

---

## Frequently Asked Questions

**Q: Can a forgotten private key password be recovered?**
A: No. Generate a new key pair and distribute the new public key to your partners.

**Q: Can I share a `.sig.json` file publicly?**
A: This file contains **unencrypted** content. Only share it if the content doesn't need to be kept secret. Use `.env.json` for content confidentiality.

**Q: Does the public key need to be kept secret?**
A: **No.** The public key is designed to be shared freely. Only the **private key** must be protected.

**Q: Does the application send data to a server?**
A: **Absolutely not.** All operations are performed offline, locally on your machine.
