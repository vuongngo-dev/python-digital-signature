# 📖 Hướng Dẫn Sử Dụng — Digital Signer

> **Digital Signer** là ứng dụng desktop cho phép bạn **ký số** và **xác minh chữ ký** trên văn bản, cũng như trao đổi tài liệu an toàn bằng **bao thư số (digital envelope)**.
> Toàn bộ thao tác mật mã thực hiện cục bộ trên máy — **không có dữ liệu nào được gửi lên mạng**.

---

## Mục Lục

- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt &amp; Khởi Chạy](#cài-đặt--khởi-chạy)
- [Tab Quản Lý Khóa](#tab-quản-lý-khóa-)
- [Tab Ký Số](#tab-ký-số-)
- [Tab Xác Minh](#tab-xác-minh-)
- [Bao Thư Số](#bao-thư-số-digital-envelope)
- [Định Dạng File](#định-dạng-file)
- [Câu Hỏi Thường Gặp](#câu-hỏi-thường-gặp)

---

## Yêu Cầu Hệ Thống

| Thành phần   | Phiên bản tối thiểu                    |
| ------------ | -------------------------------------- |
| Python       | 3.13+                                  |
| PyQt6        | 6.6.0+                                 |
| cryptography | 42.0.0+                                |
| Hệ điều hành | Windows 10, macOS 12, Linux Ubuntu 22+ |

---

## Cài Đặt & Khởi Chạy

```bash
# 1. Di chuyển vào thư mục dự án
cd python-simple-signer

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Khởi chạy ứng dụng
python main.py
```

---

## Tab Quản Lý Khóa 🔑

**Bước đầu tiên** trước khi ký hoặc xác minh bất kỳ thứ gì.

### Tạo Cặp Khóa Mới

1. Chuyển sang tab **🔑 Quản Lý Khóa**.
2. Nhập **Tên khóa** (ví dụ: `alice`, `my-company`). Chỉ dùng chữ cái, số, `-`, `_`.
3. _(Tùy chọn)_ Nhập **Mật khẩu bảo vệ** để mã hóa private key.
4. Nhấn **➕ Tạo Cặp Khóa**.
5. Cặp khóa tạo ra:
   - `alice_private.pem` — Private key (giữ bí mật tuyệt đối)
   - `alice_public.pem` — Public key (chia sẻ tự do)

> ⚠️ **Quan trọng:** Nếu đặt mật khẩu, hãy ghi nhớ cẩn thận. Mất mật khẩu = mất quyền truy cập private key.

### Xem & Chia Sẻ Public Key

- Chọn một khóa trong danh sách → nội dung PEM hiển thị ở khung phải.
- Nhấn **📋 Sao chép PEM** để copy, sau đó gửi cho đối tác qua email.

### Import Public Key Của Người Khác

1. Nhấn **📥 Import Public Key**.
2. Chọn file `.pem` được cung cấp bởi đối tác.
3. Khóa xuất hiện trong danh sách với biểu tượng 🔓 (chỉ public).

### Xóa Khóa

- Chọn khóa → nhấn **🗑️ Xóa Khóa** → xác nhận. Hành động **không thể hoàn tác**.

---

## Tab Ký Số ✍️

### Ký Văn Bản Thông Thường

1. Chuyển sang tab **✍️ Ký Số**.
2. Chọn **Private Key** từ dropdown (chỉ hiển thị khóa có `_private.pem`).
3. Nhập **mật khẩu** nếu key được bảo vệ.
4. Nhập nội dung vào ô văn bản, hoặc nhấn **📂 Tải từ file** để đọc file `.txt`.
5. Nhấn **✍️ Ký Số** → chọn nơi lưu file `.sig.json`.

File `.sig.json` xuất ra chứa: nội dung gốc, chữ ký RSA-PSS-SHA256, public key người ký, timestamp.

### Tạo Bao Thư Số

1. Nhấn **📨 Tạo Bao Thư Số** trong tab Ký Số.
2. Dialog mở ra, chọn:
   - **Private key người gửi** (để ký)
   - **Public key người nhận** (để mã hóa)
   - **Nội dung** cần gửi
3. Nhấn **📦 Tạo & Lưu** → lưu file `.env.json` → gửi cho người nhận.

---

## Tab Xác Minh 🔍

### Xác Minh Chữ Ký (`.sig.json`)

1. Chuyển sang tab **🔍 Xác Minh**.
2. Nhấn **📂 Tải File** → chọn file `.sig.json`.
3. Ứng dụng tự động xác minh và hiển thị:
   - Nội dung gốc
   - Thông tin người ký
   - Kết quả: ✅ **HỢP LỆ** hoặc ❌ **KHÔNG HỢP LỆ**

> Public key dùng để xác minh đã được **nhúng sẵn** trong file `.sig.json`.

### Mở Bao Thư Số (`.env.json`)

1. Tải file `.env.json`.
2. Chọn **private key của người nhận** từ dropdown.
3. Nhấn **🔓 Mở Bao Thư**.
4. Nội dung gốc và trạng thái chữ ký người gửi hiển thị.

---

## Bao Thư Số (Digital Envelope)

Dùng khi bạn cần **vừa mã hóa vừa ký số** cho một người nhận cụ thể.

**Kịch bản:** Alice gửi tài liệu bí mật cho Bob.

| Bước | Thực hiện                                                                    |
| ---- | ---------------------------------------------------------------------------- |
| 1    | Alice import `bob_public.pem` vào ứng dụng                                   |
| 2    | Alice tạo bao thư: chọn private key `alice`, public key `bob`, nhập nội dung |
| 3    | Alice gửi file `.env.json` cho Bob                                           |
| 4    | Bob tải file, chọn private key `bob`, nhấn Mở Bao Thư                        |
| 5    | Bob đọc nội dung + xem chữ ký của Alice có hợp lệ không                      |

---

## Định Dạng File

### File Chữ Ký (`.sig.json`)

```json
{
  "type": "digital_signature",
  "version": "1.0",
  "timestamp": "2024-05-08T10:30:00.000000",
  "algorithm": "RSA-PSS-SHA256",
  "content": "Nội dung gốc...",
  "signature": "<Base64 RSA-PSS signature>",
  "signer_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"
}
```

### File Bao Thư Số (`.env.json`)

```json
{
  "type": "digital_envelope",
  "version": "1.0",
  "timestamp": "2024-05-08T10:30:00.000000",
  "encrypted_content": "<Base64 AES-GCM ciphertext>",
  "aes_nonce": "<Base64 nonce 12 bytes>",
  "aes_tag": "<Base64 auth tag 16 bytes>",
  "encrypted_aes_key": "<Base64 RSA-OAEP(AES key)>",
  "sender_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
  "signature": "<Base64 RSA-PSS signature of payload>",
  "algorithm": {
    "symmetric": "AES-256-GCM",
    "asymmetric": "RSA-OAEP-SHA256",
    "signature": "RSA-PSS-SHA256"
  }
}
```

### Khóa (thư mục `keys/`)

| File                 | Mô tả                                                            |
| -------------------- | ---------------------------------------------------------------- |
| `<name>_private.pem` | RSA 2048-bit private key (PKCS#8, tùy chọn mã hóa bằng mật khẩu) |
| `<name>_public.pem`  | RSA 2048-bit public key (SubjectPublicKeyInfo)                   |

---

## Câu Hỏi Thường Gặp

**Q: Quên mật khẩu private key có khôi phục được không?**
A: Không. Hãy tạo lại cặp khóa mới và phân phối public key mới cho đối tác.

**Q: File `.sig.json` có thể chia sẻ công khai không?**
A: File này chứa nội dung **không mã hóa**. Chỉ chia sẻ nếu nội dung không cần bảo mật. Dùng `.env.json` nếu cần bảo mật nội dung.

**Q: Public key có cần giữ bí mật không?**
A: **Không.** Public key được thiết kế để chia sẻ tự do. Chỉ **private key** mới cần bảo vệ.

**Q: Ứng dụng có gửi dữ liệu lên server không?**
A: **Hoàn toàn không.** Mọi thao tác thực hiện offline, cục bộ trên máy bạn.
