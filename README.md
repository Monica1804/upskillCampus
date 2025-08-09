# Student Attendance System

## 📌 Overview
A simple Python project for managing student attendance using **Tkinter** for the GUI and **SQLite** for the database. It supports adding students, marking attendance, viewing reports, and exporting data.

## ✨ Features
- **Admin Login** (default: `admin` / `admin`)
- **Add / Edit / Delete Students**
- **Mark Attendance** by date (Present/Absent)
- **View Attendance Reports** by student or by date
- **Export Data** to CSV or Excel

## 🛠 Tech Stack
- Python 3.8+
- Tkinter (GUI)
- SQLite3 (Database)
- Pandas (Export to CSV/Excel)
- Openpyxl (Excel support)

## 📂 Installation
1. Make sure Python 3.8+ is installed.
2. Install required dependencies:
```bash
pip install pandas openpyxl
```
3. Download the project files.

## ▶️ Usage
Run the following command:
```bash
python student_attendance_system.py
```
Login with:
```
Username: admin
Password: admin
```

## 📊 Database
The project automatically creates an SQLite database file named `attendance.db` with two tables:
- **students**: Stores student details.
- **attendance**: Stores attendance records.

## 📦 Export
You can export either the `students` or `attendance` table to CSV/Excel from the Export menu.

## 📄 License
This project is free to use for educational and internship purposes.
