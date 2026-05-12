# 🏗️ Pipeline & Kiến Trúc Dự Án — Digital Signer

Tài liệu này mô tả **cách hoạt động nội bộ** của Digital Signer, bao gồm kiến trúc module, luồng dữ liệu (pipeline) của từng chức năng, và các thuật toán mật mã được sử dụng.

---

## Mục Lục

- [Tổng Quan Kiến Trúc](#tổng-quan-kiến-trúc)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Module crypto — Lõi Mật Mã](#module-crypto--lõi-mật-mã)
- [Module utils — Tiện Ích File](#module-utils--tiện-ích-file)
- [Module gui — Giao Diện](#module-gui--giao-diện)
- [Pipeline: Tạo Cặp Khóa](#pipeline-tạo-cặp-khóa)
- [Pipeline: Ký Số Văn Bản](#pipeline-ký-số-văn-bản)
- [Pipeline: Xác Minh Chữ Ký](#pipeline-xác-minh-chữ-ký)
- [Pipeline: Tạo Bao Thư Số](#pipeline-tạo-bao-thư-số)
- [Pipeline: Mở Bao Thư Số](#pipeline-mở-bao-thư-số)
- [Thuật Toán Mật Mã](#thuật-toán-mật-mã)
- [Sơ Đồ Phụ Thuộc Module](#sơ-đồ-phụ-thuộc-module)

---

## Tổng Quan Kiến Trúc

```
┌────────────────────────────────────────────────────┐
│                   GUI Layer (PyQt6)                 │
│  app.py │ sign_tab.py │ verify_tab.py │ keys_tab.py │
│          └──── envelope_dialog.py ─────┘            │
└──────────────────────┬─────────────────────────────┘
                       │ gọi hàm
┌──────────────────────▼─────────────────────────────┐
│              Crypto Layer (cryptography)            │
│   key_manager.py │ signer.py │ envelope.py          │
└──────────────────────┬─────────────────────────────┘
                       │ đọc/ghi
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

Kiến trúc chia thành **3 tầng rõ ràng**, không có phụ thuộc ngược (GUI → Crypto → Utils → FileSystem).

---

## Cấu Trúc Thư Mục

```
python-simple-signer/
├── main.py                  # Entry point — khởi tạo QApplication
├── requirements.txt         # Dependency: cryptography, PyQt6
│
├── crypto/                  # Lõi mật mã (không phụ thuộc GUI)
│   ├── __init__.py
│   ├── key_manager.py       # Tạo, load, liệt kê RSA key pairs
│   ├── signer.py            # Ký số & xác minh RSA-PSS
│   └── envelope.py          # Tạo & mở bao thư số hybrid
│
├── utils/                   # Tiện ích đọc/ghi file
│   ├── __init__.py
│   └── file_handler.py      # Lưu/load .sig.json & .env.json
│
├── gui/                     # Giao diện PyQt6
│   ├── __init__.py
│   ├── app.py               # Cửa sổ chính, QTabWidget
│   ├── styles.py            # QSS stylesheet toàn cục
│   ├── sign_tab.py          # Tab Ký Số
│   ├── verify_tab.py        # Tab Xác Minh
│   ├── keys_tab.py          # Tab Quản Lý Khóa
│   └── envelope_dialog.py   # Dialog tạo bao thư số
│
└── keys/                    # Lưu trữ key pairs (tạo tự động)
    ├── alice_private.pem
    ├── alice_public.pem
    └── ...
```

---

## Module crypto — Lõi Mật Mã

### `key_manager.py`

Quản lý vòng đời RSA key pairs.

| Hàm | Chức năng |
|---|---|
| `generate_key_pair(name, passphrase)` | Tạo RSA 2048-bit, lưu PEM vào `keys/` |
| `load_private_key(path, passphrase)` | Load private key từ file PEM |
| `load_public_key(path)` | Load public key từ file PEM |
| `list_key_pairs()` | Quét `keys/`, trả list dict thông tin các cặp khóa |
| `get_public_key_pem(path)` | Đọc nội dung PEM public key dạng string |

### `signer.py`

Ký số và xác minh đơn giản.

| Hàm | Chức năng |
|---|---|
| `sign(content, private_key)` | Ký bytes/str → trả Base64 signature |
| `verify(content, signature_b64, public_key)` | Xác minh chữ ký → True/False |

### `envelope.py`

Bao thư số hybrid (mã hóa + ký số).

| Hàm | Chức năng |
|---|---|
| `create_envelope(content, recipient_pub, sender_priv)` | Tạo bao thư số → trả dict |
| `open_envelope(envelope, recipient_priv)` | Mở bao thư → (content, sig_valid, sender_pem) |

---

## Module utils — Tiện Ích File

### `file_handler.py`

| Hàm | Chức năng |
|---|---|
| `save_signature_file(content, sig_b64, pub_pem, path)` | Lưu `.sig.json` |
| `save_envelope_file(envelope, path)` | Lưu `.env.json` |
| `load_file(path)` | Load & phát hiện loại file, trả `(dict, "signature"\|"envelope")` |
| `detect_file_type(path)` | Phát hiện loại file, không raise exception |

---

## Module gui — Giao Diện

### `app.py` — Cửa Sổ Chính

- Khởi tạo `QMainWindow` với dark theme.
- Chứa `QTabWidget` với 3 tab: **SignTab**, **VerifyTab**, **KeysTab**.
- Kết nối signal `keys_tab.keys_changed` → tự động refresh dropdown khóa ở các tab khác.

### `keys_tab.py` — Tab Quản Lý Khóa

- Hiển thị danh sách key pairs từ `key_manager.list_key_pairs()`.
- Cung cấp UI tạo khóa, import public key, xóa khóa, xem & copy PEM.
- Phát signal `keys_changed` khi danh sách thay đổi.

### `sign_tab.py` — Tab Ký Số

- Dropdown chọn private key, ô nhập passphrase, editor nhập nội dung.
- Gọi `key_manager.load_private_key()` → `signer.sign()` → `file_handler.save_signature_file()`.
- Nút mở `EnvelopeDialog` để tạo bao thư số.

### `verify_tab.py` — Tab Xác Minh

- Load file `.sig.json` hoặc `.env.json`.
- Tự động phân loại và hiển thị UI phù hợp (chữ ký thường vs bao thư).
- Gọi `signer.verify()` hoặc `envelope.open_envelope()` theo loại file.

### `envelope_dialog.py` — Dialog Bao Thư Số

- Form chọn private key người gửi, public key người nhận, nhập nội dung.
- Gọi `envelope.create_envelope()` → `file_handler.save_envelope_file()`.

---

## Pipeline: Tạo Cặp Khóa

```
[Người dùng nhập tên + passphrase]
        │
        ▼
KeysTab.on_generate_clicked()
        │
        ▼
crypto/key_manager.generate_key_pair(name, passphrase)
        │
        ├─ rsa.generate_private_key(public_exponent=65537, key_size=2048)
        │
        ├─ [Có passphrase?]
        │      Yes → BestAvailableEncryption(passphrase.encode())
        │      No  → NoEncryption()
        │
        ├─ private_key.private_bytes(PEM, PKCS8, encryption)
        │        → keys/<name>_private.pem
        │
        └─ private_key.public_key().public_bytes(PEM, SubjectPublicKeyInfo)
                 → keys/<name>_public.pem
        │
        ▼
KeysTab phát signal keys_changed → refresh tất cả dropdown
```

---

## Pipeline: Ký Số Văn Bản

```
[Người dùng: chọn private key + nhập nội dung + nhấn Ký]
        │
        ▼
SignTab.on_sign_clicked()
        │
        ├─ key_manager.load_private_key(path, passphrase)
        │        → RSAPrivateKey object
        │
        ├─ signer.sign(content, private_key)
        │        │
        │        ├─ content.encode("utf-8")  [nếu là str]
        │        ├─ private_key.sign(
        │        │     content,
        │        │     PSS(mgf=MGF1(SHA256), salt=MAX_LENGTH),
        │        │     SHA256()
        │        │  )
        │        └─ base64.b64encode(signature_bytes)
        │               → "ABcd1234..." (Base64 string)
        │
        ├─ key_manager.get_public_key_pem(public_path)
        │        → "-----BEGIN PUBLIC KEY-----\n..."
        │
        └─ file_handler.save_signature_file(content, sig_b64, pub_pem, save_path)
                 │
                 └─ JSON { type, version, timestamp, algorithm,
                           content, signature, signer_public_key }
                          → output.sig.json
```

---

## Pipeline: Xác Minh Chữ Ký

```
[Người dùng tải file .sig.json]
        │
        ▼
VerifyTab.on_load_file()
        │
        ├─ file_handler.load_file(path)
        │        → (data: dict, type: "signature")
        │
        └─ signer.verify(
               content    = data["content"],
               sig_b64    = data["signature"],
               public_key = load_pem_public_key(data["signer_public_key"])
           )
                │
                ├─ base64.b64decode(sig_b64)
                ├─ public_key.verify(
                │     signature_bytes,
                │     content,
                │     PSS(mgf=MGF1(SHA256), salt=MAX_LENGTH),
                │     SHA256()
                │  )
                │
                ├─ [Không raise exception] → True  → ✅ Hiển thị HỢP LỆ
                └─ [InvalidSignature]      → False → ❌ Hiển thị KHÔNG HỢP LỆ
```

---

## Pipeline: Tạo Bao Thư Số

```
[Người dùng: chọn sender priv key + recipient pub key + nội dung]
        │
        ▼
EnvelopeDialog.on_create_clicked()
        │
        ├─ load sender_private_key (RSAPrivateKey)
        ├─ load recipient_public_key (RSAPublicKey)
        │
        ▼
crypto/envelope.create_envelope(content, recipient_pub, sender_priv)
        │
        ├─ [Bước 1] Tạo AES-256 key ngẫu nhiên
        │        aes_key = os.urandom(32)   # 256-bit
        │        nonce   = os.urandom(12)   # GCM nonce
        │
        ├─ [Bước 2] Mã hóa nội dung bằng AES-256-GCM
        │        AESGCM(aes_key).encrypt(nonce, content, None)
        │        → ciphertext (N bytes) + tag (16 bytes)
        │
        ├─ [Bước 3] Mã hóa AES key bằng RSA-OAEP
        │        recipient_pub.encrypt(
        │            aes_key,
        │            OAEP(mgf=MGF1(SHA256), algorithm=SHA256)
        │        )
        │        → encrypted_aes_key (256 bytes với RSA-2048)
        │
        ├─ [Bước 4] Tạo payload để ký (JSON canonical, sort_keys=True)
        │        payload = {
        │            encrypted_content, aes_nonce, aes_tag,
        │            encrypted_aes_key, sender_public_key
        │        }
        │
        ├─ [Bước 5] Ký payload bằng RSA-PSS-SHA256
        │        signature = signer.sign(payload_bytes, sender_priv)
        │
        └─ Trả về envelope dict
                 │
                 ▼
        file_handler.save_envelope_file(envelope, path)
                 → output.env.json
```

---

## Pipeline: Mở Bao Thư Số

```
[Người dùng tải file .env.json + chọn recipient private key]
        │
        ▼
VerifyTab.on_open_envelope()
        │
        ├─ file_handler.load_file(path)
        │        → (envelope: dict, type: "envelope")
        │
        ├─ load recipient_private_key (RSAPrivateKey)
        │
        ▼
crypto/envelope.open_envelope(envelope, recipient_priv)
        │
        ├─ [Bước 1] Xác minh chữ ký người gửi
        │        Tái tạo payload canonical từ các trường trong envelope
        │        load sender_public_key từ envelope["sender_public_key"]
        │        signer.verify(payload_bytes, envelope["signature"], sender_pub)
        │        → sig_valid: True / False (không throw nếu sai)
        │
        ├─ [Bước 2] Giải mã AES key bằng recipient private key
        │        recipient_priv.decrypt(
        │            encrypted_aes_key,
        │            OAEP(mgf=MGF1(SHA256), algorithm=SHA256)
        │        )
        │        → aes_key (32 bytes)
        │        [Sai key → ValueError: "Bạn có dùng đúng private key không?"]
        │
        ├─ [Bước 3] Giải mã nội dung bằng AES-256-GCM
        │        AESGCM(aes_key).decrypt(nonce, ciphertext + tag, None)
        │        → content (bytes gốc)
        │
        └─ Trả về (content, sig_valid, sender_public_pem)
                 │
                 ▼
        VerifyTab hiển thị nội dung + trạng thái chữ ký người gửi
```

---

## Thuật Toán Mật Mã

| Mục đích | Thuật toán | Chi tiết |
|---|---|---|
| Tạo khóa | RSA | 2048-bit, public exponent 65537 |
| Bảo vệ private key | AES (BestAvailableEncryption) | Dùng passphrase người dùng |
| Định dạng lưu trữ | PKCS#8 (private), SubjectPublicKeyInfo (public) | PEM encoding |
| Ký số | RSA-PSS + SHA-256 | MGF1(SHA-256), salt = MAX_LENGTH |
| Mã hóa AES key | RSA-OAEP + SHA-256 | MGF1(SHA-256), label = None |
| Mã hóa nội dung | AES-256-GCM | Key 256-bit, Nonce 12-byte, Tag 16-byte |
| Hashing | SHA-256 | Dùng trong PSS và OAEP |
| Encoding output | Base64 | Tất cả binary data trong JSON |

---

## Sơ Đồ Phụ Thuộc Module

```
main.py
  └─► gui/app.py
        ├─► gui/styles.py
        ├─► gui/sign_tab.py
        │      ├─► crypto/key_manager.py
        │      ├─► crypto/signer.py
        │      ├─► utils/file_handler.py
        │      └─► gui/envelope_dialog.py
        │              ├─► crypto/key_manager.py
        │              ├─► crypto/envelope.py
        │              │      └─► crypto/signer.py
        │              └─► utils/file_handler.py
        ├─► gui/verify_tab.py
        │      ├─► crypto/key_manager.py
        │      ├─► crypto/signer.py
        │      ├─► crypto/envelope.py
        │      └─► utils/file_handler.py
        └─► gui/keys_tab.py
               └─► crypto/key_manager.py
```

> **Nguyên tắc thiết kế:** Module `crypto/` và `utils/` **hoàn toàn độc lập** với GUI — có thể import và sử dụng từ script Python thuần không cần giao diện.
