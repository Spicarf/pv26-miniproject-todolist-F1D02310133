# 📋 Task Manager Pro

Aplikasi manajemen tugas berbasis **PySide6** dengan tampilan modern dark theme, integrasi **SQLite**, dan arsitektur **Separation of Concerns**.

---

## 👤 Identitas

| | |
|---|---|
| **Nama** | Raffi Fatthoni |
| **NIM** | F1D02310133 |
| **Mata Kuliah** | Pemrograman Visual |

---

## ✨ Fitur Utama

- ✅ **CRUD Lengkap** — Tambah, edit, hapus task dengan konfirmasi dialog
- 🎨 **Stat Cards** — Ringkasan Total / Done / In Progress / Todo / High Priority
- 🔍 **Search + Filter Pills** — Filter by status & prioritas secara real-time
- 📅 **Deteksi Overdue** — Due date merah otomatis jika terlewat
- 🗂 **Kategori Task** — General, Work, Personal, Study, Health, dll.
- 🌙 **Dark Theme Modern** — Styling QSS dari file eksternal

---

## 📁 Struktur Project (SoC)

```
task_manager/
├── main.py                     ← Entry point
├── tasks.db                    ← Database SQLite (auto-generated)
├── styles/
│   └── style.qss               ← Styling eksternal (Dark Indigo Theme)
├── database/
│   └── db_manager.py           ← Layer Data: operasi SQLite
├── controllers/
│   └── task_controller.py      ← Layer Logika: bisnis & validasi
└── ui/
    ├── main_window.py          ← Layer View: jendela utama
    └── task_dialog.py          ← Layer View: dialog form
```

---

## 🗃 Schema Database

Tabel `tasks` — 8 kolom:

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | Auto increment |
| `title` | TEXT | Judul task (wajib) |
| `category` | TEXT | Kategori (General/Work/dll) |
| `priority` | TEXT | High / Medium / Low |
| `status` | TEXT | Todo / In Progress / Done |
| `due_date` | TEXT | Format yyyy-MM-dd |
| `description` | TEXT | Deskripsi singkat |
| `created_at` | TEXT | Timestamp dibuat |

---

## 🚀 Cara Menjalankan

```bash
# 1. Install dependency
pip install PySide6

# 2. Jalankan aplikasi
python main.py
```

> Database `tasks.db` akan dibuat otomatis di direktori yang sama saat pertama kali dijalankan.

---

## 🛠 Teknologi

- **Python 3.10+**
- **PySide6** — GUI Framework
- **SQLite3** — Database lokal
- **QSS** — Styling eksternal (Dark Indigo Theme)
