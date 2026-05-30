# =======================================================
# Script: controller/envolope.py
# Description: Digital Envelope logic (AES + Custom RSA)
# =======================================================

import os
import json
import base64

from core.crypto_aes import CryptoAES
from .signer import Signer

def create_envelope(content_str: str, recipient_public_key: tuple, sender_private_key: tuple) -> dict:
    """
    Tạo bao thư số (Digital Envelope).
    Sử dụng AES-256-CTR (Custom) để mã hóa nội dung.
    Sử dụng RSA của recipient để mã hóa khóa AES.
    Sử dụng RSA của sender để ký toàn bộ khối dữ liệu.
    """
    # 1. Tạo AES-256 key ngẫu nhiên
    aes_key = CryptoAES.generate_key()
    nonce = CryptoAES.generate_nonce()

    # 2. Đóng gói content lại thành 1 JSON dict
    payload_data = {
        "text": content_str
    }
    payload_bytes = json.dumps(payload_data).encode('utf-8')

    # 3. Mã hóa bằng custom AES-256-CTR
    aes = CryptoAES(aes_key)
    ciphertext = aes.encrypt(payload_bytes, nonce)

    # 4. Mã hóa AES key bằng RSA của Recipient (Textbook RSA)
    e, n = recipient_public_key
    aes_key_int = int.from_bytes(aes_key, 'big')
    encrypted_aes_key_int = pow(aes_key_int, e, n)
    encrypted_aes_key_bytes = encrypted_aes_key_int.to_bytes((encrypted_aes_key_int.bit_length() + 7) // 8, 'big')

    # 5. Ký điện tử (Sign) toàn bộ các phần quan trọng
    # Định dạng dữ liệu để ký
    envelope_meta = {
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "encrypted_aes_key": base64.b64encode(encrypted_aes_key_bytes).decode('utf-8')
    }
    canonical_data_to_sign = json.dumps(envelope_meta, sort_keys=True).encode('utf-8')
    
    signer = Signer()
    signature_bytes = signer.sign(canonical_data_to_sign, sender_private_key)

    # 6. Trả về cấu trúc bao thư
    envelope = {
        "encrypted_content": envelope_meta["ciphertext"],
        "aes_nonce": envelope_meta["nonce"],
        "encrypted_aes_key": envelope_meta["encrypted_aes_key"],
        "signature": base64.b64encode(signature_bytes).decode('utf-8')
    }
    return envelope


def open_envelope(envelope: dict, recipient_private_key: tuple, sender_public_key: tuple) -> tuple:
    """
    Mở bao thư số (Digital Envelope).
    Trả về (content_str, is_signature_valid)
    """
    # 1. Trích xuất thông tin
    ciphertext = base64.b64decode(envelope["encrypted_content"])
    nonce = base64.b64decode(envelope["aes_nonce"])
    encrypted_aes_key_bytes = base64.b64decode(envelope["encrypted_aes_key"])
    signature_bytes = base64.b64decode(envelope["signature"])

    # 2. Xác thực chữ ký của Sender
    envelope_meta = {
        "ciphertext": envelope["encrypted_content"],
        "nonce": envelope["aes_nonce"],
        "encrypted_aes_key": envelope["encrypted_aes_key"]
    }
    canonical_data_to_sign = json.dumps(envelope_meta, sort_keys=True).encode('utf-8')
    
    signer = Signer()
    is_valid = signer.verify(canonical_data_to_sign, signature_bytes, sender_public_key)

    # 3. Giải mã AES key bằng RSA của Recipient (Textbook RSA)
    d, n = recipient_private_key
    encrypted_aes_key_int = int.from_bytes(encrypted_aes_key_bytes, 'big')
    aes_key_int = pow(encrypted_aes_key_int, d, n)
    
    # 32 bytes for AES-256
    try:
        aes_key = aes_key_int.to_bytes(32, 'big')
    except OverflowError:
        raise ValueError("Lỗi giải mã khóa AES: Private key của bạn không đúng hoặc bao thư bị hỏng.")

    # 4. Giải mã nội dung bằng custom AES-256-CTR
    try:
        aes = CryptoAES(aes_key)
        decrypted_payload_bytes = aes.decrypt(ciphertext, nonce)
        payload_data = json.loads(decrypted_payload_bytes.decode('utf-8'))
    except Exception:
        raise ValueError("Không thể giải mã nội dung. Chìa khóa sai hoặc dữ liệu đã bị sửa đổi!")

    content_str = payload_data.get("text", "")

    return content_str, is_valid
