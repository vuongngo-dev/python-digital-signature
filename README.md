# 🛡️ Internal Digital Signature App

Welcome to the **Internal Digital Signature Project**. This is a Desktop application (developed using Python and PyQt6) that provides a secure solution for digitally signing documents, creating digital envelopes, and managing local cryptographic keys.

This project uses **custom RSA** cryptography combined with **custom AES-256-CTR** to ensure data integrity, verify sender identity, and maximize content security. It uses only custom, self-made algorithms, with no external cryptographic libraries.

---

## 📑 Table of Contents
1. [Key Features](#-key-features)
2. [Project Structure](#-project-structure)
3. [Installation & Execution Guide](#-installation--execution-guide)
4. [Quick Start Guide](#-quick-start-guide)
5. [Related Documentation](#-related-documentation)

---

## 🚀 Key Features

- **🔑 Key Management**: Generate new RSA key pairs (Public/Private Key) or import existing keys in `.pem` format.
- **✍️ Digital Signature**:
  - Securely sign text content to ensure data integrity and authenticity (generates `*.sig.json` files).
  - Prompts you dynamically with an interactive dialog choosing whether to wrap the document in a digital envelope or sign it standard.
  - Supports backward compatibility for verifying older signatures containing canvas/image data.
- **✉️ Digital Envelope**: Encrypt the entire text using a custom AES-256 key, then encrypt the AES key with the recipient's Public Key (generates `*.env.json` files). Unauthorized individuals cannot read the content without the corresponding Private Key.
- **✅ Verification & Decryption**: 
  - Verify signatures to check if the document has been tampered with.
  - Open digital envelopes (requires the recipient's Private Key) and automatically verify the sender's signature.

---

## 📂 Project Structure

The project is organized following a clear layer architecture (MVC - Model View Controller) for easy expansion and maintenance:

```text
python-digital-signature/
├── main.py                 # Main application entry point
├── requirements.txt        # Dependencies (PyQt6, pytest...)
├── README.md               # Project overview and instructions (this file)
├── ARCHITECTURE.md         # In-depth technical architecture documentation
├── USER_GUIDE.md           # Detailed step-by-step user manual
├── .gitignore              # Specifies untracked files/folders (e.g., keys/)
│
├── core/                   # 🧠 Core Cryptographic Algorithms
│   ├── crypto_rsa.py       # Custom RSA algorithm implementation
│   ├── crypto_aes.py       # Custom AES-256-CTR algorithm
│   └── crypto_hash.py      # Custom Hashing algorithm (SHA-256)
│
├── controller/             # ⚙️ Business Logic Layer
│   ├── key_manager.py      # Logic for reading/writing/generating key pairs
│   ├── signer.py           # Data hashing and RSA digital signing logic
│   └── envolope.py         # Digital Envelope logic (combining AES and RSA)
│
├── gui/                    # 🖥️ Graphical User Interface Layer (PyQt6)
│   ├── main_window.py      # Main window, navigation sidebar, Stylesheet (Dark mode)
│   └── views.py            # Interfaces for Key Management, Signing, Verification
│
├── utils/                  # 🛠️ Utility Functions
│   └── file_handler.py     # Handling saving/loading files (sig.json, env.json)
│
├── keys/                   # 🔐 Internal local storage (Not pushed to Git)
│   └── *.pem               # Generated Public/Private Keys
│
└── test/                   # 🧪 Unit Test Directory
    └── ...                 # Automated tests (pytest)
```

---

## ⚙️ Installation & Execution Guide

**System Requirements:** Python 3.10 or higher.

**Step 1: Clone the repository and navigate to the folder**
```bash
git clone <your-repo-url>
cd python-digital-signature
```

**Step 2: Create and activate a Virtual Environment**
```bash
# On Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

**Step 3: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Run the application**
```bash
python main.py
```

---

## 📖 Quick Start Guide

### 1. Generate or Import Keys ("Key Management" Tab)
- You need a Private Key to Sign or Decrypt an Envelope. 
- Enter a name and click **"Tạo Khóa RSA (2048-bit)"**, the software will automatically save the key pair in the `/keys` directory.
- You can also **"Nhập Khóa (.pem)"** if you already have previously generated keys.

### 2. Sign or Create Envelope ("Ký Tài liệu" Tab)
- Select your **Private Key** (to sign) and select the recipient's **Public Key** (optional, used if you want to seal the document in an envelope).
- Enter your content in the text box.
- Click **"Thực hiện Ký / Đóng Bao Thư"**.
- A pop-up dialog will ask: **"Bạn có muốn đóng gói tài liệu này trong Bao Thư Số không?"**
  - **Click Yes (Đồng ý)**: Creates a secure Digital Envelope (`.env.json`).
  - **Click No (Không)**: Creates a Standard Digital Signature (`.sig.json`).
  - **Click Cancel (Hủy)**: Aborts the action.

### 3. Verify and Decrypt ("Xác thực" Tab)
- Click **"Duyệt File..."** to load a `.sig.json` or `.env.json` file.
- If it is an `.env.json` file, the application will prompt you to select **your Private Key** for decryption.
- Click **"Tiến hành Xác Thực / Mở Bao Thư"**, the system will report whether the document has been altered and display the original decrypted content.
- The system automatically supports legacy signature files containing canvas images for backward compatibility.

---

## 📚 Related Documentation
- **[USER_GUIDE.md](./USER_GUIDE.md)**: Detailed user guide (can be used for end-user training).
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Technical documentation detailing workflows, module architecture, and cryptographic pipeline.
