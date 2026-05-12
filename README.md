# 🛡️ Internal Digital Signature App

Welcome to the **Internal Digital Signature Project**. This is a Desktop application (developed using Python and PyQt6) that provides a secure solution for digitally signing documents, creating digital envelopes, and managing local cryptographic keys.

This project uses **custom RSA** cryptography combined with **AES-256-GCM** to ensure data integrity, verify sender identity, and maximize content security.

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
  - Support for entering text content and drawing signatures directly on the interface (Canvas).
  - Ability to import existing signature images into the software.
  - Digital signing to ensure data integrity (generates `*.sig.json` files).
- **✉️ Digital Envelope**: Encrypt the entire text and signature data using an AES-256 key, then encrypt the AES key with the recipient's Public Key (generates `*.env.json` files). Unauthorized individuals cannot read the content without the corresponding Private Key.
- **✅ Verification & Decryption**: 
  - Verify signatures to check if the document has been tampered with.
  - Open digital envelopes (requires the recipient's Private Key) and automatically verify the sender's signature.

---

## 📂 Project Structure

The project is organized following a clear layer architecture (MVC - Model View Controller) for easy expansion and maintenance:

```text
python-digital-signature/
├── main.py                 # Main application entry point
├── requirements.txt        # Dependencies (PyQt6, cryptography, pytest...)
├── README.md               # Project overview and instructions (this file)
├── ARCHITECTURE.md         # In-depth technical architecture documentation
├── USER_GUIDE.md           # Detailed step-by-step user manual
├── .gitignore              # Specifies untracked files/folders (e.g., keys/)
│
├── core/                   # 🧠 Core Cryptographic Algorithms
│   └── crypto_rsa.py       # RSA implementation, key generation, basic encryption/decryption
│
├── controller/             # ⚙️ Business Logic Layer
│   ├── key_manager.py      # Logic for reading/writing/generating key pairs, internal PEM format
│   ├── signer.py           # Data hashing and RSA digital signing logic
│   └── envolope.py         # Digital Envelope logic (combining AES and RSA)
│
├── gui/                    # 🖥️ Graphical User Interface Layer (PyQt6)
│   ├── main_window.py      # Main window, navigation sidebar, Stylesheet (Dark mode)
│   ├── views.py            # Interfaces for Key Management, Signing, Verification
│   └── canvas_widget.py    # Widget for drawing or importing signatures, outputs to Base64
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
- Enter a name and click **"Generate Key"**, the software will automatically save the key pair in the `/keys` directory.
- You can also **"Import Key"** (.pem) if you already have previously generated keys.

### 2. Sign or Create Envelope ("Sign Document" Tab)
- **Standard Signature**: Enter text, draw or select a signature image, choose your Private Key, and click **Sign**. The system will output a `.sig.json` file.
- **Digital Envelope**: Check the "Digital Envelope" option, you must also select the recipient's Public Key. The result will be a highly secure `.env.json` encrypted file.

### 3. Verify and Decrypt ("Verify" Tab)
- Click **"Browse File..."** to load a `.sig.json` or `.env.json` file.
- If it is an `.env.json` file, the application will prompt you to select **your Private Key** for decryption.
- Click **"Verify"**, the system will report whether the document has been altered and display the original content along with the original signature image.

---

## 📚 Related Documentation
- **[USER_GUIDE.md](./USER_GUIDE.md)**: Detailed user guide (can be used for end-user training).
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Technical documentation delving into how RSA and AES-GCM work, useful for Software Developers / Engineers.
