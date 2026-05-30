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

1. Switch to the **🔑 Quản lý Khóa** tab.
2. Enter a **Key Name** in the "Tên khóa" field (e.g., `alice`, `my-company`). Use only letters, numbers, `-`, `_`.
3. Click **Tạo Khóa RSA (2048-bit)**.
4. The generated key pair:
   - `<name>_private.pem` — Private key (keep absolutely secret, used to sign and decrypt)
   - `<name>_public.pem` — Public key (share freely with recipients, used to verify and encrypt)

### Import Someone Else's Public Key

1. Click **Nhập Khóa (.pem)**.
2. Select the public `.pem` file provided by your partner.
3. The key appears in the list showing its availability.

---

## Sign Tab ✍️

### Signing a Document / Choosing Figure

1. Switch to the **✍️ Ký Tài liệu** tab.
2. Select a **Private Key (Để Ký)** from the dropdown.
3. If you plan to send this document in a **Digital Envelope**, select the recipient's **Public Key (Người Nhận)** from the corresponding dropdown.
4. Enter the content in the **📝 Nội dung tài liệu** text box.
5. Click **Thực hiện Ký / Đóng Bao Thư**.
6. **Interactive Selection Box**: A message dialog will pop up asking:
   - **Click Yes (Đồng ý)**: Seals the document inside a **Digital Envelope** (encrypts content with AES-256 and encrypts the AES key using the recipient's Public Key). Saves as a `.env.json` file.
   - **Click No (Không)**: Performs a **Standard Digital Signature** on the plain text document. Saves as a `.sig.json` file.
   - **Click Cancel (Hủy)**: Cancels the signing action completely.

---

## Verify Tab 🔍

### Verify Signature (`.sig.json`)

1. Switch to the **✅ Xác thực** tab.
2. Click **Duyệt File...** → select the `.sig.json` file.
3. Click **Tiến hành Xác Thực / Mở Bao Thư**.
4. The application automatically verifies and displays:
   - Original text content
   - Signer's information
   - Result: ✅ **VALID** (Chữ ký hợp lệ) or ❌ **INVALID** (Chữ ký không hợp lệ)

> [!NOTE]
> The public key used for verification is **pre-embedded** within the `.sig.json` file.
> The system automatically supports legacy signature files containing canvas drawings/images for backward compatibility.

### Open Digital Envelope (`.env.json`)

1. Load the `.env.json` file.
2. The UI will prompt you to select **your private key** from the dropdown to decrypt the envelope.
3. Click **Tiến hành Xác Thực / Mở Bao Thư**.
4. The original content and the status of the sender's signature will be displayed.

---

## Digital Envelope

Used when you need to **both encrypt and digitally sign** for a specific recipient.

**Scenario:** Alice sends a secret document to Bob.

| Step | Action                                                                    |
| ---- | ------------------------------------------------------------------------- |
| 1    | Alice imports `bob_public.pem` into the application.                      |
| 2    | Alice enters the content, selects `alice` private key, and Bob's public key. |
| 3    | Alice clicks sign and confirms "Yes" to create the envelope. Alice saves the `.env.json` file. |
| 4    | Alice sends the `.env.json` file to Bob.                                  |
| 5    | Bob loads the file, selects `bob` private key, clicks Verify/Open.      |
| 6    | Bob reads the unencrypted content and checks if Alice's signature is valid. |

---

## File Formats

### Signature File (`.sig.json`)

```json
{
  "type": "digital_signature",
  "version": "1.0",
  "timestamp": "2026-05-30T18:50:00",
  "algorithm": "Custom-RSA-SHA256",
  "content": "{\"text\": \"Original text...\"}",
  "signature": "<Base64 signature>",
  "signer_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"
}
```

### Digital Envelope File (`.env.json`)

```json
{
  "type": "digital_envelope",
  "version": "1.0",
  "timestamp": "2026-05-30T18:50:00",
  "algorithm": {
    "symmetric": "Custom-AES-256-CTR",
    "asymmetric": "Custom-RSA",
    "signature": "Custom-RSA-SHA256"
  },
  "encrypted_content": "<Base64 AES-CTR ciphertext>",
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

**Q: Can I share a `.sig.json` file publicly?**
A: This file contains **unencrypted** content. Only share it if the content doesn't need to be kept secret. Use `.env.json` for content confidentiality.

**Q: Does the public key need to be kept secret?**
A: **No.** The public key is designed to be shared freely. Only the **private key** must be protected.

**Q: Does the application send data to a server?**
A: **Absolutely not.** All operations are performed offline, locally on your machine.
