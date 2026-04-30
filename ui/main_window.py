"""
ui/main_window.py
Jendela utama aplikasi Task Manager Pro.
Menampilkan: header, stat-cards, toolbar, filter, tabel, status bar.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLineEdit, QLabel, QFrame,
    QStatusBar, QMessageBox, QMenuBar, QMenu,
    QAbstractItemView, QStyledItemDelegate, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QAction

from controllers.task_controller import TaskController
from ui.task_dialog import TaskDialog

# Identitas Mahasiswa
NAMA = "Raffi Fatthoni"
NIM  = "F1D02310133"


class MainWindow(QMainWindow):
    """Jendela utama aplikasi."""

    # Filter aktif saat ini
    _active_status   = "Semua"
    _active_priority = "Semua"
    _search_text     = ""

    def __init__(self):
        super().__init__()
        self.ctrl = TaskController()
        self._current_tasks: list[dict] = []   # data yang sedang ditampilkan

        self.setWindowTitle("Task Manager Pro")
        self.setMinimumSize(960, 620)
        self.resize(1080, 680)

        self._build_menu()
        self._build_ui()
        self._refresh()

    #  MENU BAR
    def _build_menu(self):
        bar = self.menuBar()

        # Menu File
        m_file = bar.addMenu("File")

        act_new = QAction("➕  Tambah Task", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._add_task)
        m_file.addAction(act_new)

        m_file.addSeparator()

        act_clear = QAction("🗑  Hapus Semua Done", self)
        act_clear.triggered.connect(self._delete_done_tasks)
        m_file.addAction(act_clear)

        m_file.addSeparator()

        act_exit = QAction("⏻  Keluar", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        m_file.addAction(act_exit)

        # Menu Tentang Aplikasi  ← WAJIB sesuai spesifikasi
        m_about = bar.addMenu("Tentang Aplikasi")
        act_about = QAction("ℹ️  Tentang Task Manager Pro", self)
        act_about.triggered.connect(self._show_about)
        m_about.addAction(act_about)

    #  UI BUILDER
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_stat_cards())
        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_filter_bar())
        root.addWidget(self._build_table(), stretch=1)

        self.setCentralWidget(central)

        # Status Bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

    # Header
    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("headerBar")
        bar.setFixedHeight(58)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)

        icon_lbl = QLabel("📋")
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")

        app_title = QLabel("Task Manager Pro")
        app_title.setObjectName("appTitle")

        sep = QLabel("  |  ")
        sep.setStyleSheet("color: #2d2d55; background: transparent;")

        identity = QLabel(f"👤 {NAMA}   •   🆔 {NIM}")
        identity.setObjectName("identityLabel")

        lay.addWidget(icon_lbl)
        lay.addWidget(app_title)
        lay.addWidget(sep)
        lay.addWidget(identity)
        lay.addStretch()
        return bar

    # Stat Cards
    def _build_stat_cards(self) -> QWidget:
        wrapper = QFrame()
        wrapper.setStyleSheet("QFrame { background-color: #0f0f1a; border-bottom: 1px solid #1e1e35; }")
        lay = QHBoxLayout(wrapper)
        lay.setContentsMargins(20, 12, 20, 12)
        lay.setSpacing(12)

        # (label, number_id, default)
        defs = [
            ("Total",        "statNumberTotal",  "0", "#a78bfa"),
            ("Done",         "statNumberDone",   "0", "#34d399"),
            ("In Progress",  "statNumberProg",   "0", "#60a5fa"),
            ("Todo",         "statNumberTodo",   "0", "#f59e0b"),
            ("High Priority","statNumberHigh",   "0", "#f87171"),
        ]

        self._stat_labels: dict[str, QLabel] = {}

        for label_text, num_id, default, color in defs:
            card = QFrame()
            card.setObjectName("statCard")
            card.setFixedHeight(72)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            v = QVBoxLayout(card)
            v.setContentsMargins(16, 8, 16, 8)
            v.setSpacing(2)
            v.setAlignment(Qt.AlignCenter)

            num = QLabel(default)
            num.setObjectName("statNumber")
            num.setAlignment(Qt.AlignCenter)
            num.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; background: transparent;")

            lbl = QLabel(label_text)
            lbl.setObjectName("statLabel")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #7c7c9e; font-size: 10px; background: transparent;")

            v.addWidget(num)
            v.addWidget(lbl)

            self._stat_labels[num_id] = num
            lay.addWidget(card)

        return wrapper

    # Toolbar (Add / Edit / Delete + Search)
    def _build_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("QFrame { background-color: #0f0f1a; }")
        bar.setFixedHeight(56)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 8, 20, 8)
        lay.setSpacing(8)

        self.btn_add = QPushButton("➕  Tambah")
        self.btn_add.setObjectName("btnAdd")
        self.btn_add.setToolTip("Tambah task baru  (Ctrl+N)")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self._add_task)

        self.btn_edit = QPushButton("✏️  Edit")
        self.btn_edit.setObjectName("btnEdit")
        self.btn_edit.setToolTip("Edit task terpilih")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self._edit_task)

        self.btn_delete = QPushButton("🗑  Hapus")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setToolTip("Hapus task terpilih")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._delete_task)

        self._search = QLineEdit()
        self._search.setObjectName("searchBox")
        self._search.setPlaceholderText("🔍  Cari judul atau deskripsi...")
        self._search.textChanged.connect(self._on_search)

        lay.addWidget(self.btn_add)
        lay.addWidget(self.btn_edit)
        lay.addWidget(self.btn_delete)
        lay.addStretch()
        lay.addWidget(self._search)
        return bar

    # Filter Pills
    def _build_filter_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("QFrame { background-color: #0d0d1c; border-bottom: 1px solid #1e1e35; }")
        bar.setFixedHeight(44)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 6, 20, 6)
        lay.setSpacing(6)

        self._status_pills: dict[str, QPushButton] = {}
        self._priority_pills: dict[str, QPushButton] = {}

        # Status pills
        lbl_s = QLabel("Status:")
        lbl_s.setStyleSheet("color: #4a4a6a; font-size: 11px; background: transparent;")
        lay.addWidget(lbl_s)

        for s in ["Semua", "Todo", "In Progress", "Done"]:
            btn = self._make_pill(s)
            btn.clicked.connect(lambda _, v=s: self._set_status_filter(v))
            self._status_pills[s] = btn
            lay.addWidget(btn)

        sep = QLabel("  │  ")
        sep.setStyleSheet("color: #2d2d55; background: transparent;")
        lay.addWidget(sep)

        # Priority pills
        lbl_p = QLabel("Prioritas:")
        lbl_p.setStyleSheet("color: #4a4a6a; font-size: 11px; background: transparent;")
        lay.addWidget(lbl_p)

        for p in ["Semua", "High", "Medium", "Low"]:
            btn = self._make_pill(p)
            btn.clicked.connect(lambda _, v=p: self._set_priority_filter(v))
            self._priority_pills[p] = btn
            lay.addWidget(btn)

        lay.addStretch()

        # Aktifkan default
        self._status_pills["Semua"].setProperty("active", "true")
        self._priority_pills["Semua"].setProperty("active", "true")
        return bar

    @staticmethod
    def _make_pill(text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("filterBtn")
        btn.setCheckable(False)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(28)
        return btn

    # Table
    def _build_table(self) -> QWidget:
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["No", "Judul", "Kategori", "Prioritas", "Status", "Due Date", "Deskripsi"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 46)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setFocusPolicy(Qt.ClickFocus)
        self._table.itemSelectionChanged.connect(self._on_selection)
        self._table.doubleClicked.connect(self._edit_task)
        return self._table

    #  CRUD ACTIONS
    def _add_task(self):
        dlg = TaskDialog(self, controller=self.ctrl)
        if dlg.exec():
            try:
                self.ctrl.add(dlg.get_data())
                self._refresh()
                self._show_status("✅  Task berhasil ditambahkan.", 3000)
            except ValueError as e:
                QMessageBox.warning(self, "Gagal", str(e))

    def _edit_task(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._current_tasks):
            return
        task = self._current_tasks[row]
        dlg = TaskDialog(self, task_data=task, controller=self.ctrl)
        if dlg.exec():
            try:
                self.ctrl.edit(task["id"], dlg.get_data())
                self._refresh()
                self._show_status("✏️  Task berhasil diperbarui.", 3000)
            except ValueError as e:
                QMessageBox.warning(self, "Gagal", str(e))

    def _delete_task(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._current_tasks):
            return
        task = self._current_tasks[row]
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus task:\n\n「{task['title']}」\n\nTindakan ini tidak dapat dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ctrl.delete(task["id"])
            self._refresh()
            self._show_status("🗑  Task berhasil dihapus.", 3000)

    def _delete_done_tasks(self):
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Hapus semua task yang berstatus Done?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ctrl.delete_done_tasks()
            self._refresh()
            self._show_status("🗑  Semua task Done telah dihapus.", 3000)

    #  FILTER / SEARCH
    def _on_search(self, text: str):
        self._search_text = text
        self._apply_filter()

    def _set_status_filter(self, value: str):
        self._active_status = value
        self._refresh_pills(self._status_pills, value)
        self._apply_filter()

    def _set_priority_filter(self, value: str):
        self._active_priority = value
        self._refresh_pills(self._priority_pills, value)
        self._apply_filter()

    @staticmethod
    def _refresh_pills(pills: dict, active: str):
        for key, btn in pills.items():
            btn.setProperty("active", "true" if key == active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _apply_filter(self):
        status   = self._active_status   if self._active_status   != "Semua" else ""
        priority = self._active_priority if self._active_priority != "Semua" else ""
        tasks = self.ctrl.search(
            keyword=self._search_text,
            status=status,
            priority=priority
        )
        self._load_table(tasks)
        
    #  TABLE POPULATION
    def _refresh(self):
        self._apply_filter()
        self._update_stats()

    def _load_table(self, tasks: list[dict]):
        self._current_tasks = tasks
        self._table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            self._set_cell(row, 0, str(row + 1), align=Qt.AlignCenter)
            self._set_cell(row, 1, task["title"])
            self._set_cell(row, 2, task.get("category", "General"), align=Qt.AlignCenter)
            self._set_priority_cell(row, 3, task["priority"])
            self._set_status_cell(row, 4, task["status"])
            self._set_due_date_cell(row, 5, task["due_date"])
            self._set_cell(row, 6, task.get("description", ""), color="#6b6b8e")

            # Warna baris per prioritas (subtle tint)
            row_bg = self._priority_row_bg(task["priority"])
            for col in range(7):
                item = self._table.item(row, col)
                if item:
                    item.setBackground(row_bg)

        self._table.clearSelection()
        self._update_action_buttons(False)
        count = len(tasks)
        self._show_status(
            f"  Menampilkan {count} task"
            + (f" dari filter '{self._active_status}' / '{self._active_priority}'" if
            self._active_status != "Semua" or self._active_priority != "Semua" else "")
        )

    # Cell helpers
    def _set_cell(self, row, col, text, align=Qt.AlignVCenter | Qt.AlignLeft, color: str = None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        if color:
            item.setForeground(QColor(color))
        self._table.setItem(row, col, item)

    def _set_priority_cell(self, row, col, priority: str):
        colors = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#34d399"}
        icons  = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        item = QTableWidgetItem(f"{icons.get(priority,'')} {priority}")
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QColor(colors.get(priority, "#a78bfa")))
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self._table.setItem(row, col, item)

    def _set_status_cell(self, row, col, status: str):
        icons = {"Todo": "⭕", "In Progress": "🔄", "Done": "✅"}
        colors = {"Todo": "#f59e0b", "In Progress": "#60a5fa", "Done": "#34d399"}
        item = QTableWidgetItem(f"{icons.get(status,'')} {status}")
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QColor(colors.get(status, "#a78bfa")))
        self._table.setItem(row, col, item)

    def _set_due_date_cell(self, row, col, date_str: str):
        try:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            display = qdate.toString("dd MMM yyyy")
            overdue = qdate < QDate.currentDate()
        except Exception:
            display, overdue = date_str, False

        item = QTableWidgetItem(("⚠️ " if overdue else "📅 ") + display)
        item.setTextAlignment(Qt.AlignCenter)
        if overdue:
            item.setForeground(QColor("#f87171"))
        self._table.setItem(row, col, item)

    @staticmethod
    def _priority_row_bg(priority: str) -> QColor:
        tints = {
            "High":   QColor(248, 113, 113, 18),
            "Medium": QColor(251, 191,  36, 14),
            "Low":    QColor( 52, 211, 153, 14),
        }
        return tints.get(priority, QColor(0, 0, 0, 0))

    #  STATS
    def _update_stats(self):
        stats = self.ctrl.get_stats()
        mapping = {
            "statNumberTotal": str(stats["total"]),
            "statNumberDone":  str(stats["done"]),
            "statNumberProg":  str(stats["in_progress"]),
            "statNumberTodo":  str(stats["todo"]),
            "statNumberHigh":  str(stats["high"]),
        }
        for key, val in mapping.items():
            if key in self._stat_labels:
                self._stat_labels[key].setText(val)

    #  MISC
    def _on_selection(self):
        has_sel = len(self._table.selectedItems()) > 0
        self._update_action_buttons(has_sel)

    def _update_action_buttons(self, enabled: bool):
        self.btn_edit.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)

    def _show_status(self, msg: str, timeout: int = 0):
        self._status_bar.showMessage(msg, timeout)

    def _show_about(self):
        QMessageBox.about(
            self, "Tentang Task Manager Pro",
            f"""<h2 style='color:#a78bfa'>📋 Task Manager Pro</h2>
            <p>Aplikasi manajemen tugas berbasis PySide6 dengan antarmuka modern.</p>
            <hr>
            <table>
                <tr><td><b>Nama&nbsp;&nbsp;</b></td><td>: {NAMA}</td></tr>
                <tr><td><b>NIM</b></td><td>: {NIM}</td></tr>
                <tr><td><b>Framework</b></td><td>: PySide6 + SQLite</td></tr>
                <tr><td><b>Versi</b></td><td>: 1.0.0</td></tr>
            </table>
            <p style='color:#7c7c9e; font-size:11px; margin-top:10px;'>
                Mini Project Pemrograman Visual — 2026
            </p>"""
        )
