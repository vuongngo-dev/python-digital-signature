from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from .views import KeyManagerView, SignerView, VerifierView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Signature App")
        self.resize(1050, 750)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(20, 40, 20, 30)
        sidebar_layout.setSpacing(15)

        # App Logo/Title in Sidebar
        app_title = QLabel("🛡️ SecureSign")
        app_title.setFont(QFont("Inter", 22, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #3b82f6; margin-bottom: 40px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Navigation Buttons
        self.nav_buttons = []
        nav_items = [
            ("🔑 Quản lý Khóa", 0),
            ("✍️ Ký Tài liệu", 1),
            ("✅ Xác thực", 2)
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Capture index correctly in lambda
            btn.clicked.connect(lambda checked, idx=index: self.switch_view(idx))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Footer
        footer = QLabel("Phiên bản 1.0.0\n© 2026 Vuong Ngo")
        footer.setStyleSheet("color: #64748b; font-size: 12px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer)

        # Main Content Area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("MainContent")
        self.key_manager_view = KeyManagerView()
        self.signer_view = SignerView()
        self.verifier_view = VerifierView()

        self.stacked_widget.addWidget(self.key_manager_view)
        self.stacked_widget.addWidget(self.signer_view)
        self.stacked_widget.addWidget(self.verifier_view)

        # Layout Assembly
        main_layout.addWidget(self.sidebar_widget)
        
        # Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet("color: #1e293b; background-color: #1e293b;")
        main_layout.addWidget(line)
        
        content_wrapper = QWidget()
        content_wrapper.setObjectName("ContentWrapper")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Header
        self.header_label = QLabel("Quản lý Khóa")
        self.header_label.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #f8fafc;")
        
        content_layout.addWidget(self.header_label)
        content_layout.addWidget(self.stacked_widget)

        main_layout.addWidget(content_wrapper)

        # Set initial view
        self.switch_view(0)

    def switch_view(self, index):
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            
        self.stacked_widget.setCurrentIndex(index)
        titles = ["Quản lý Khóa", "Ký & Đóng Bao Thư", "Xác thực & Giải mã"]
        if 0 <= index < len(titles):
            self.header_label.setText(titles[index])
            
        # Refresh lists when switching tabs
        if index == 0:
            self.key_manager_view.load_key_list()
        elif index == 1:
            self.signer_view.load_keys()

    def apply_styles(self):
        # Modern Slate Dark Mode Stylesheet
        qss = """
        QMainWindow {
            background-color: #0f172a; /* Slate 900 */
        }
        QWidget {
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            color: #f8fafc; /* Slate 50 */
        }
        
        /* Sidebar Styles */
        QWidget#Sidebar {
            background-color: #0f172a;
        }
        QPushButton#NavButton {
            background-color: transparent;
            color: #94a3b8; /* Slate 400 */
            border: none;
            border-radius: 12px;
            text-align: left;
            padding-left: 20px;
            font-size: 16px;
            font-weight: 600;
        }
        QPushButton#NavButton:hover {
            background-color: #1e293b; /* Slate 800 */
            color: #f8fafc;
        }
        QPushButton#NavButton:checked {
            background-color: #1e293b; /* Slate 800 */
            color: #3b82f6; /* Blue 500 */
            border-left: 5px solid #3b82f6;
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
            padding-left: 15px; /* Offset for border */
        }
        
        /* Content Wrapper */
        QWidget#ContentWrapper {
            background-color: #0f172a;
        }
        
        /* Global Control Styles */
        QLineEdit, QTextEdit, QComboBox {
            background-color: #0f172a; /* Slate 900 inside cards */
            border: 1px solid #334155; /* Slate 700 */
            border-radius: 8px;
            padding: 12px 16px;
            color: #f8fafc;
            font-size: 14px;
            selection-background-color: #3b82f6;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #3b82f6;
            background-color: #0f172a;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #94a3b8;
            margin-right: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            selection-background-color: #3b82f6;
            outline: none;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #334155; /* Slate 700 */
            cursor: pointer;
        }
        QPushButton:pressed {
            background-color: #0f172a;
            border: 1px solid #1e293b;
        }
        QPushButton#PrimaryButton {
            background-color: #3b82f6; /* Blue 500 */
            color: #ffffff;
            border: none;
            font-size: 15px;
            border-radius: 8px;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #2563eb; /* Blue 600 */
        }
        QPushButton#PrimaryButton:pressed {
            background-color: #1d4ed8; /* Blue 700 */
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #475569; /* Slate 600 */
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #64748b; /* Slate 500 */
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """
        self.setStyleSheet(qss)
