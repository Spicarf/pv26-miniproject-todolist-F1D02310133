"""
ui/task_dialog.py
Dialog form untuk Add / Edit task (terpisah dari jendela utama).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from controllers.task_controller import TaskController


class TaskDialog(QDialog):
    """
    Dialog input task dengan 6 field:
    1. Judul
    2. Kategori
    3. Prioritas
    4. Status
    5. Due Date
    6. Deskripsi
    """

    def __init__(self, parent=None, task_data: dict = None, controller: TaskController = None):
        super().__init__(parent)
        self.ctrl = controller or TaskController()
        self._is_edit = task_data is not None

        self.setWindowTitle("Edit Task" if self._is_edit else "Tambah Task Baru")
        self.setMinimumWidth(420)
        self.setModal(True)

        self._build_ui()

        if task_data:
            self._populate(task_data)

    # UI
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header strip
        header = QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet(
            "QFrame { background-color: #7c3aed; border-radius: 0px; }"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 20, 0)

        title_lbl = QLabel("✏️  Edit Task" if self._is_edit else "➕  Task Baru")
        title_lbl.setStyleSheet("color: white; font-size: 15px; font-weight: bold; background: transparent;")
        h_lay.addWidget(title_lbl)
        root.addWidget(header)

        # Form body
        body = QFrame()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 20, 24, 8)
        body_lay.setSpacing(14)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)
        form.setVerticalSpacing(12)

        # 1. Judul
        self.f_title = QLineEdit()
        self.f_title.setPlaceholderText("Nama task...")
        self.f_title.setMinimumHeight(36)
        form.addRow("Judul :", self.f_title)

        # 2. Kategori
        self.f_category = QComboBox()
        self.f_category.setEditable(True)
        self.f_category.addItems(self.ctrl.get_dynamic_categories())
        self.f_category.setMinimumHeight(36)
        form.addRow("Kategori :", self.f_category)

        # 3. Prioritas
        self.f_priority = QComboBox()
        self.f_priority.addItems(self.ctrl.PRIORITIES)
        self.f_priority.setMinimumHeight(36)
        self.f_priority.currentTextChanged.connect(self._update_priority_color)
        form.addRow("Prioritas :", self.f_priority)

        # 4. Status
        self.f_status = QComboBox()
        self.f_status.addItems(self.ctrl.STATUSES)
        self.f_status.setMinimumHeight(36)
        form.addRow("Status :", self.f_status)

        # 5. Due Date
        self.f_date = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDate(QDate.currentDate())
        self.f_date.setMinimumHeight(36)
        self.f_date.setDisplayFormat("dd MMMM yyyy")
        form.addRow("Due Date :", self.f_date)

        # 6. Deskripsi
        self.f_desc = QTextEdit()
        self.f_desc.setPlaceholderText("Deskripsi singkat (opsional)...")
        self.f_desc.setFixedHeight(80)
        form.addRow("Deskripsi :", self.f_desc)

        body_lay.addLayout(form)
        root.addWidget(body)

        # Footer Buttons
        footer = QFrame()
        footer.setStyleSheet("QFrame { background-color: #13132a; border-top: 1px solid #2d2d55; }")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(24, 12, 24, 14)
        f_lay.setSpacing(10)

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("💾  Simpan")
        self.btn_save.setObjectName("btnSave")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self._on_save)

        f_lay.addStretch()
        f_lay.addWidget(self.btn_cancel)
        f_lay.addWidget(self.btn_save)
        root.addWidget(footer)

        self._update_priority_color(self.f_priority.currentText())

    # Helpers
    def _populate(self, data: dict):
        self.f_title.setText(data.get("title", ""))
        self.f_category.setCurrentText(data.get("category", "General"))
        self.f_priority.setCurrentText(data.get("priority", "Medium"))
        self.f_status.setCurrentText(data.get("status", "Todo"))
        self.f_date.setDate(QDate.fromString(data.get("due_date", ""), "yyyy-MM-dd"))
        self.f_desc.setPlainText(data.get("description", ""))

    def _update_priority_color(self, text: str):
        colors = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#34d399"}
        c = colors.get(text, "#a78bfa")
        self.f_priority.setStyleSheet(
            f"QComboBox {{ color: {c}; font-weight: bold; "
            f"border: 1px solid {c}40; background-color: {c}15; "
            f"border-radius: 7px; padding: 7px 10px; }}"
        )

    def _on_save(self):
        title = self.f_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validasi", "Judul task tidak boleh kosong!")
            self.f_title.setFocus()
            return
        self.accept()

    # Public
    def get_data(self) -> dict:
        return {
            "title":       self.f_title.text().strip(),
            "category":    self.f_category.currentText(),
            "priority":    self.f_priority.currentText(),
            "status":      self.f_status.currentText(),
            "due_date":    self.f_date.date().toString("yyyy-MM-dd"),
            "description": self.f_desc.toPlainText().strip(),
        }
