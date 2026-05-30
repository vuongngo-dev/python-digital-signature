import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QLineEdit, QFileDialog, QMessageBox, QComboBox,
    QFormLayout, QCheckBox, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from .canvas_widget import CanvasWidget

import controller.key_manager as km
from controller.signer import Signer
from controller.envolope import create_envelope, open_envelope
from utils.file_handler import save_signature_file, load_file, save_envelope_file

class CardWidget(QFrame):
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setObjectName("CardWidget")
        self.setStyleSheet("""
            QFrame#CardWidget {
                background-color: #1e293b;
                border-radius: 16px;
                border: 1px solid #334155;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)
        
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #f8fafc; border: none; background: transparent;")
            self.main_layout.addWidget(title_label)
            
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: #334155; border: none; max-height: 1px;")
            self.main_layout.addWidget(line)

    def addWidget(self, widget, alignment=None):
        if alignment:
            self.main_layout.addWidget(widget, alignment=alignment)
        else:
            self.main_layout.addWidget(widget)

    def addLayout(self, layout):
        self.main_layout.addLayout(layout)

class KeyManagerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # Generate Key Card
        gen_card = CardWidget("✨ Tạo Khóa Mới")
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.key_name_input = QLineEdit()
        self.key_name_input.setPlaceholderText("VD: khoa_ca_nhan")
        self.gen_btn = QPushButton("Tạo Khóa RSA (2048-bit)")
        self.gen_btn.setObjectName("PrimaryButton")
        self.gen_btn.clicked.connect(self.generate_key)
        
        name_label = QLabel("Tên khóa:")
        name_label.setStyleSheet("font-weight: bold; color: #cbd5e1;")
        form_layout.addRow(name_label, self.key_name_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.gen_btn)
        
        self.import_key_btn = QPushButton("Nhập Khóa (.pem)")
        self.import_key_btn.clicked.connect(self.import_key)
        btn_layout.addWidget(self.import_key_btn)
        
        form_layout.addRow("", btn_layout)
        gen_card.addLayout(form_layout)

        # List Keys Card
        list_card = CardWidget("📋 Danh sách Khóa hiện có")
        
        self.refresh_btn = QPushButton("Làm mới danh sách")
        self.refresh_btn.clicked.connect(self.load_key_list)
        
        self.key_list_display = QTextEdit()
        self.key_list_display.setReadOnly(True)
        self.key_list_display.setStyleSheet("font-family: 'Consolas', monospace;")
        
        list_card.addWidget(self.refresh_btn)
        list_card.addWidget(self.key_list_display)

        layout.addWidget(gen_card)
        layout.addWidget(list_card)
        
        self.load_key_list()

    def generate_key(self):
        name = self.key_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên khóa!")
            return
        
        try:
            priv, pub = km.generate_key_pair(name, bits=2048)
            QMessageBox.information(self, "Thành công", f"Đã tạo khóa thành công!\nPrivate: {priv.name}\nPublic: {pub.name}")
            self.key_name_input.clear()
            self.load_key_list()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {e}")

    def import_key(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Chọn file khóa (.pem)", "", "PEM Files (*.pem)")
        if not paths:
            return
            
        import shutil
        from pathlib import Path
        
        try:
            km.ensure_keys_dir()
            count = 0
            for path in paths:
                src = Path(path)
                dst = km.KEYS_DIR / src.name
                if not dst.exists():
                    shutil.copy2(src, dst)
                    count += 1
            if count > 0:
                QMessageBox.information(self, "Thành công", f"Đã nhập thành công {count} khóa!")
                self.load_key_list()
            else:
                QMessageBox.information(self, "Thông báo", "Không có khóa mới nào được nhập (khóa đã tồn tại).")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi nhập khóa: {e}")

    def load_key_list(self):
        try:
            keys = km.list_key_pairs()
            display_text = ""
            for k in keys:
                display_text += f"🔑 {k['name']}\n"
                display_text += f"   ├── Public Key:  {'Có' if k['has_public'] else 'Không'}\n"
                display_text += f"   └── Private Key: {'Có' if k['has_private'] else 'Không'}\n\n"
            
            if not display_text:
                display_text = "Chưa có khóa nào được tạo."
                
            self.key_list_display.setText(display_text)
        except Exception as e:
            self.key_list_display.setText(f"Lỗi tải danh sách: {e}")

class SignerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # Cấu Hình
        config_card = CardWidget("⚙️ Cấu Hình Ký & Bảo Mật")
        config_layout = QFormLayout()
        config_layout.setSpacing(15)
        
        self.key_combo = QComboBox()
        lbl1 = QLabel("Private Key (Để Ký):")
        lbl1.setStyleSheet("font-weight: bold; color: #cbd5e1;")
        config_layout.addRow(lbl1, self.key_combo)

        self.recipient_key_combo = QComboBox()
        
        lbl2 = QLabel("Public Key (Người Nhận):")
        lbl2.setStyleSheet("font-weight: bold; color: #cbd5e1;")
        
        config_layout.addRow(lbl2, self.recipient_key_combo)
        
        self.refresh_keys_btn = QPushButton("Làm mới danh sách khóa")
        self.refresh_keys_btn.clicked.connect(self.load_keys)
        config_layout.addRow("", self.refresh_keys_btn)
        
        config_card.addLayout(config_layout)

        # Nội dung
        doc_card = CardWidget("📝 Nội dung tài liệu")
        self.doc_input = QTextEdit()
        self.doc_input.setPlaceholderText("Nhập nội dung cần ký/mã hóa...")
        doc_card.addWidget(self.doc_input)
        # Sign Button
        self.sign_btn = QPushButton("Thực hiện Ký / Đóng Bao Thư")
        self.sign_btn.setObjectName("PrimaryButton")
        self.sign_btn.setMinimumHeight(50)
        self.sign_btn.clicked.connect(self.sign_document)

        layout.addWidget(config_card)
        layout.addWidget(doc_card)
        layout.addWidget(self.sign_btn)

        self.load_keys()

    def load_keys(self):
        self.key_combo.clear()
        self.recipient_key_combo.clear()
        keys = km.list_key_pairs()
        for k in keys:
            if k['has_private']:
                self.key_combo.addItem(k['name'], userData=k)
            if k['has_public']:
                self.recipient_key_combo.addItem(k['name'], userData=k)

    def sign_document(self):
        doc_text = self.doc_input.toPlainText().strip()
        if not doc_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập nội dung tài liệu!")
            return
        
        sender_data = self.key_combo.currentData()
        if not sender_data:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khóa bí mật của bạn để ký!")
            return

        # Hiển thị hộp thoại hỏi người dùng có muốn đóng bao thư số hay không
        reply = QMessageBox.question(
            self, 
            "Xác nhận hình thức ký",
            "Bạn có muốn đóng gói tài liệu này trong Bao Thư Số không?\n\n"
            "- Chọn 'Yes' (Đồng ý): Sẽ tạo bao thư số (mã hóa + ký bằng Public Key của người nhận).\n"
            "- Chọn 'No' (Không): Chỉ ký số thông thường (không mã hóa).\n"
            "- Chọn 'Cancel' (Hủy): Hủy bỏ thao tác.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        is_envelope = (reply == QMessageBox.StandardButton.Yes)
        recipient_data = self.recipient_key_combo.currentData()
        if is_envelope and not recipient_data:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khóa Public của người nhận để đóng bao thư!")
            return

        try:
            sender_private_key = km.load_private_key(sender_data['private_path'])
            sender_public_pem = km.get_public_key_pem(sender_data['public_path'])
             
            if is_envelope:
                recipient_public_key = km.load_public_key(recipient_data['public_path'])
                envelope_dict = create_envelope(doc_text, recipient_public_key, sender_private_key)
                
                save_path, _ = QFileDialog.getSaveFileName(self, "Lưu file Bao thư số", "", "Envelope Files (*.env.json)")
                if save_path:
                    save_envelope_file(envelope_dict, sender_public_pem, Path(save_path))
                    QMessageBox.information(self, "Thành công", f"Đã đóng bao thư và lưu tại:\n{save_path}")
            else:
                full_content_to_sign = doc_text
                signer = Signer()
                signature_bytes = signer.sign(full_content_to_sign.encode('utf-8'), sender_private_key)
                
                import base64, json
                signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
                saved_content = {"text": doc_text}
                
                save_path, _ = QFileDialog.getSaveFileName(self, "Lưu file Chữ ký số", "", "Signature Files (*.sig.json)")
                if save_path:
                    save_signature_file(json.dumps(saved_content), signature_b64, sender_public_pem, Path(save_path))
                    QMessageBox.information(self, "Thành công", f"Đã ký và lưu file tại:\n{save_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {e}")

class VerifierView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # File Select
        file_card = CardWidget("📁 Chọn File cần Xác thực/Giải mã")
        file_layout = QHBoxLayout()
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("Chưa chọn file nào...")
        self.browse_btn = QPushButton("Duyệt File...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_display)
        file_layout.addWidget(self.browse_btn)
        file_card.addLayout(file_layout)

        # Recipient Private Key (for opening envelope)
        self.priv_key_card = CardWidget("🔐 Khóa Bí Mật của bạn (Để mở bao thư)")
        priv_layout = QHBoxLayout()
        self.priv_key_combo = QComboBox()
        self.priv_key_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.refresh_keys_btn = QPushButton("Làm mới")
        self.refresh_keys_btn.clicked.connect(self.load_keys)
        priv_layout.addWidget(self.priv_key_combo)
        priv_layout.addWidget(self.refresh_keys_btn)
        self.priv_key_card.addLayout(priv_layout)
        self.priv_key_card.hide()

        # Display Content
        doc_card = CardWidget("📄 Nội dung tài liệu (Sau khi mở)")
        self.doc_display = QTextEdit()
        self.doc_display.setReadOnly(True)
        self.doc_display.setPlaceholderText("Nội dung sẽ hiển thị ở đây sau khi xác thực...")
        doc_card.addWidget(self.doc_display)

        # Verify Button
        self.verify_btn = QPushButton("Tiến hành Xác Thực / Mở Bao Thư")
        self.verify_btn.setObjectName("PrimaryButton")
        self.verify_btn.setMinimumHeight(50)
        self.verify_btn.clicked.connect(self.verify_action)

        layout.addWidget(file_card)
        layout.addWidget(self.priv_key_card)
        layout.addWidget(doc_card)
        layout.addWidget(self.verify_btn)
        
        self.loaded_data = None
        self.loaded_type = None

    def load_keys(self):
        self.priv_key_combo.clear()
        keys = km.list_key_pairs()
        for k in keys:
            if k['has_private']:
                self.priv_key_combo.addItem(k['name'], userData=k)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file", "", "All Supported (*.sig.json *.env.json);;Signature (*.sig.json);;Envelope (*.env.json)")
        if path:
            self.file_path_display.setText(path)
            try:
                data, ftype = load_file(Path(path))
                self.loaded_data = data
                self.loaded_type = ftype
                self.doc_display.clear()
                
                if ftype == "envelope":
                    self.priv_key_card.show()
                    self.load_keys()
                    self.doc_display.setText("[🔒 File đã bị mã hóa Bao Thư Số. Cần Private Key của bạn để mở!]")
                else:
                    self.priv_key_card.hide()
                    import json
                    content_str = data.get("content", "")
                    try:
                        content_json = json.loads(content_str)
                        text_part = content_json.get("text", content_str)
                        self.doc_display.setText(text_part)
                    except json.JSONDecodeError:
                        self.doc_display.setText(content_str)
                    
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file: {e}")

    def verify_action(self):
        if not self.loaded_data:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn file trước!")
            return
            
        if self.loaded_type == "envelope":
            self.open_envelope_action()
        else:
            self.verify_signature_action()

    def open_envelope_action(self):
        recipient_data = self.priv_key_combo.currentData()
        if not recipient_data:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn Private Key của bạn để mở bao thư!")
            return
            
        try:
            import tempfile, os
            recipient_priv_key = km.load_private_key(recipient_data['private_path'])
            sender_pub_pem = self.loaded_data.get("sender_public_key", "")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w", encoding="utf-8") as f:
                f.write(sender_pub_pem)
                temp_path = f.name
                
            try:
                sender_pub_key = km.load_public_key(Path(temp_path))
            finally:
                os.remove(temp_path)
                
            content_str, is_valid = open_envelope(self.loaded_data, recipient_priv_key, sender_pub_key)
            self.doc_display.setText(content_str)
            
            if is_valid:
                QMessageBox.information(self, "Kết Quả Mở", "✅ ĐÃ MỞ BAO THƯ THÀNH CÔNG!\nChữ ký người gửi hợp lệ và dữ liệu toàn vẹn.")
            else:
                QMessageBox.warning(self, "Kết Quả Mở", "⚠️ MỞ THÀNH CÔNG, NHƯNG:\nChữ ký người gửi KHÔNG hợp lệ. Dữ liệu có thể đã bị sửa đổi.")
                
        except ValueError as ve:
            QMessageBox.critical(self, "Lỗi Giải Mã", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Quá trình mở thất bại: {e}")

    def verify_signature_action(self):
        try:
            import json, base64, tempfile, os
            public_key_pem = self.loaded_data.get("signer_public_key", "")
            signature_b64 = self.loaded_data.get("signature", "")
            content_str = self.loaded_data.get("content", "")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w", encoding="utf-8") as f:
                f.write(public_key_pem)
                temp_path = f.name
                
            try:
                public_key = km.load_public_key(Path(temp_path))
            finally:
                os.remove(temp_path)
                
            signature_bytes = base64.b64decode(signature_b64)
            
            try:
                content_json = json.loads(content_str)
                text_part = content_json.get("text", "")
                canvas_part = content_json.get("canvas_image", None)
                if canvas_part is not None:
                    full_content_to_sign = text_part + "\n---CANVAS---\n" + canvas_part
                else:
                    full_content_to_sign = text_part
            except json.JSONDecodeError:
                full_content_to_sign = content_str
                
            signer = Signer()
            is_valid = signer.verify(full_content_to_sign.encode('utf-8'), signature_bytes, public_key)
            
            if is_valid:
                QMessageBox.information(self, "Kết Quả", "✅ CHỮ KÝ HỢP LỆ!\nTài liệu toàn vẹn và do đúng người có Public Key ký.")
            else:
                QMessageBox.critical(self, "Kết Quả", "❌ CHỮ KÝ KHÔNG HỢP LỆ!\nTài liệu có thể đã bị sửa đổi hoặc Public Key không khớp.")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Quá trình xác thực thất bại: {e}")
