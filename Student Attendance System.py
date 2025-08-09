"""
Student Attendance System
Single-file Python project using Tkinter + SQLite3 + Pandas for export

How to run:
1. Make sure Python 3.8+ is installed.
2. Install dependencies:
   pip install pandas openpyxl
3. Run:
   python student_attendance_system.py

Features:
- Admin login (default: admin / admin)
- Add / Edit / Delete students
- Mark attendance for a selected date (Present / Absent)
- View attendance by student or by date
- Export attendance or students table to CSV / Excel

Notes:
- Database file: attendance.db (created automatically in the same folder)
- This file is intentionally a single-file app for easy submission to internships.

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import pandas as pd
import os

DB_FILE = "attendance.db"

# ------------------------------- Database helpers -------------------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE,
            name TEXT,
            class TEXT
        )
    ''')
    # attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()


def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        data = c.fetchall()
        conn.close()
        return data
    conn.commit()
    conn.close()

# ------------------------------- GUI: Login -----------------------------------

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Student Attendance System")
        self.root.geometry("350x220")
        self.root.resizable(False, False)

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Admin Login", font=(None, 14, 'bold')).pack(pady=(0,10))

        ttk.Label(frame, text="Username:").pack(anchor='w')
        self.username = ttk.Entry(frame)
        self.username.pack(fill='x')

        ttk.Label(frame, text="Password:").pack(anchor='w', pady=(8,0))
        self.password = ttk.Entry(frame, show='*')
        self.password.pack(fill='x')

        btn = ttk.Button(frame, text="Login", command=self.check_login)
        btn.pack(pady=12)

        # default creds displayed for convenience (remove for production)
        ttk.Label(frame, text="(default: admin / admin)", foreground='gray').pack()

    def check_login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if user == 'admin' and pwd == 'admin':
            self.root.destroy()
            root = tk.Tk()
            Dashboard(root)
            root.mainloop()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password")

# ------------------------------- GUI: Dashboard -------------------------------

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System - Dashboard")
        self.root.geometry("800x500")

        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill='x')

        ttk.Label(top, text="Student Attendance System", font=(None, 18, 'bold')).pack(side='left')

        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="Add Student", command=self.open_add_student).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="View Students", command=self.open_view_students).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="Mark Attendance", command=self.open_mark_attendance).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="View Report", command=self.open_view_report).grid(row=0, column=3, padx=6)
        ttk.Button(btn_frame, text="Export Data", command=self.open_export).grid(row=0, column=4, padx=6)
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).grid(row=0, column=5, padx=6)

        # Quick summary area
        summary = ttk.Frame(self.root, padding=10)
        summary.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(summary, columns=("roll", "name", "class"), show='headings')
        self.tree.heading('roll', text='Roll No')
        self.tree.heading('name', text='Name')
        self.tree.heading('class', text='Class')
        self.tree.pack(fill='both', expand=True)

        self.refresh_student_list()

    def refresh_student_list(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = run_query("SELECT roll_no, name, class FROM students ORDER BY class, roll_no", fetch=True)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def open_add_student(self):
        AddStudentWindow(self)

    def open_view_students(self):
        ViewStudentsWindow(self)

    def open_mark_attendance(self):
        MarkAttendanceWindow(self)

    def open_view_report(self):
        ReportWindow(self)

    def open_export(self):
        ExportWindow(self)

# ------------------------------- Add Student ---------------------------------

class AddStudentWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        self.win.title("Add Student")
        self.win.geometry("350x250")

        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Roll No:").pack(anchor='w')
        self.roll = ttk.Entry(frm)
        self.roll.pack(fill='x')

        ttk.Label(frm, text="Name:").pack(anchor='w', pady=(8,0))
        self.name = ttk.Entry(frm)
        self.name.pack(fill='x')

        ttk.Label(frm, text="Class:").pack(anchor='w', pady=(8,0))
        self.cls = ttk.Entry(frm)
        self.cls.pack(fill='x')

        ttk.Button(frm, text="Save", command=self.save_student).pack(pady=12)

    def save_student(self):
        roll = self.roll.get().strip()
        name = self.name.get().strip()
        cls = self.cls.get().strip()
        if not (roll and name and cls):
            messagebox.showwarning("Required", "Please fill all fields")
            return
        try:
            run_query("INSERT INTO students (roll_no, name, class) VALUES (?, ?, ?)", (roll, name, cls))
            messagebox.showinfo("Saved", "Student added successfully")
            self.parent.refresh_student_list()
            self.win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll number already exists")

# ------------------------------- View / Edit Students -------------------------

class ViewStudentsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        self.win.title("View Students")
        self.win.geometry("600x400")

        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frm, columns=("id","roll","name","class"), show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('roll', text='Roll No')
        self.tree.heading('name', text='Name')
        self.tree.heading('class', text='Class')
        self.tree.column('id', width=40)
        self.tree.pack(fill='both', expand=True)

        btnf = ttk.Frame(self.win, padding=8)
        btnf.pack()
        ttk.Button(btnf, text="Edit", command=self.edit_selected).grid(row=0, column=0, padx=6)
        ttk.Button(btnf, text="Delete", command=self.delete_selected).grid(row=0, column=1, padx=6)

        self.populate()

    def populate(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = run_query("SELECT id, roll_no, name, class FROM students ORDER BY class, roll_no", fetch=True)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student")
            return None
        return self.tree.item(sel[0])['values']

    def edit_selected(self):
        data = self.get_selected()
        if data:
            EditStudentWindow(self, data)

    def delete_selected(self):
        data = self.get_selected()
        if data:
            sid = data[0]
            if messagebox.askyesno("Confirm", "Delete this student? This will also remove related attendance records."):
                run_query("DELETE FROM attendance WHERE student_id = ?", (sid,))
                run_query("DELETE FROM students WHERE id = ?", (sid,))
                messagebox.showinfo("Deleted", "Student removed")
                self.populate()
                self.parent.refresh_student_list()

class EditStudentWindow:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data
        self.win = tk.Toplevel()
        self.win.title("Edit Student")
        self.win.geometry("350x250")
        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        self.id = data[0]
        ttk.Label(frm, text="Roll No:").pack(anchor='w')
        self.roll = ttk.Entry(frm)
        self.roll.insert(0, data[1])
        self.roll.pack(fill='x')

        ttk.Label(frm, text="Name:").pack(anchor='w', pady=(8,0))
        self.name = ttk.Entry(frm)
        self.name.insert(0, data[2])
        self.name.pack(fill='x')

        ttk.Label(frm, text="Class:").pack(anchor='w', pady=(8,0))
        self.cls = ttk.Entry(frm)
        self.cls.insert(0, data[3])
        self.cls.pack(fill='x')

        ttk.Button(frm, text="Update", command=self.update_student).pack(pady=12)

    def update_student(self):
        r = self.roll.get().strip()
        n = self.name.get().strip()
        c = self.cls.get().strip()
        if not (r and n and c):
            messagebox.showwarning("Required", "Please fill all fields")
            return
        try:
            run_query("UPDATE students SET roll_no=?, name=?, class=? WHERE id=?", (r,n,c,self.id))
            messagebox.showinfo("Updated", "Student updated")
            self.parent.populate()
            self.parent.parent.refresh_student_list()
            self.win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll number already exists")

# ------------------------------- Mark Attendance -----------------------------

class MarkAttendanceWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        self.win.title("Mark Attendance")
        self.win.geometry("600x500")

        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        topf = ttk.Frame(frm)
        topf.pack(fill='x')

        ttk.Label(topf, text="Date (YYYY-MM-DD):").pack(side='left')
        self.date_entry = ttk.Entry(topf)
        self.date_entry.pack(side='left', padx=6)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

        ttk.Button(topf, text="Load Students", command=self.load_students).pack(side='left', padx=6)

        self.canvas = tk.Canvas(frm)
        self.scroll = ttk.Scrollbar(frm, orient='vertical', command=self.canvas.yview)
        self.scroll.pack(side='right', fill='y')
        self.canvas.pack(fill='both', expand=True, side='left')
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.chk_vars = {}

        btnf = ttk.Frame(self.win, padding=8)
        btnf.pack()
        ttk.Button(btnf, text="Save Attendance", command=self.save_attendance).grid(row=0,column=0, padx=6)

    def load_students(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.chk_vars.clear()
        rows = run_query("SELECT id, roll_no, name, class FROM students ORDER BY class, roll_no", fetch=True)
        date = self.date_entry.get().strip()
        # validate date
        try:
            _ = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Date error', 'Enter date in YYYY-MM-DD format')
            return

        # fetch attendance for date
        attendance_map = {r[0]: r[3] for r in run_query("SELECT student_id, date, status, status FROM attendance WHERE date=?", (date,), fetch=True)}
        # above query returns student_id,date,status,status (duplicate) - but we'll just use student_id->status (index 0 -> id, 2->status)
        attendance_map = {r[0]: r[2] for r in run_query("SELECT student_id, date, status FROM attendance WHERE date=?", (date,), fetch=True)}

        row = 0
        for sid, roll, name, cls in rows:
            var = tk.IntVar()
            # if present mark 1 else 0
            prev = attendance_map.get(sid)
            if prev == 'Present':
                var.set(1)
            else:
                var.set(0)
            cb = ttk.Checkbutton(self.inner, text=f"{roll} - {name} ({cls})", variable=var)
            cb.grid(row=row, column=0, sticky='w', pady=4, padx=6)
            self.chk_vars[sid] = var
            row += 1

    def save_attendance(self):
        date = self.date_entry.get().strip()
        try:
            _ = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Date error', 'Enter date in YYYY-MM-DD format')
            return

        for sid, var in self.chk_vars.items():
            status = 'Present' if var.get() == 1 else 'Absent'
            # insert or update
            try:
                run_query("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (sid, date, status))
            except sqlite3.IntegrityError:
                run_query("UPDATE attendance SET status=? WHERE student_id=? AND date=?", (status, sid, date))
        messagebox.showinfo('Saved', 'Attendance saved')

# ------------------------------- Reports -------------------------------------

class ReportWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        self.win.title("View Reports")
        self.win.geometry("800x500")

        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        topf = ttk.Frame(frm)
        topf.pack(fill='x')

        ttk.Label(topf, text="Filter by:").pack(side='left')
        self.filter_var = tk.StringVar(value='student')
        ttk.Radiobutton(topf, text='Student', variable=self.filter_var, value='student', command=self.switch_filter).pack(side='left')
        ttk.Radiobutton(topf, text='Date', variable=self.filter_var, value='date', command=self.switch_filter).pack(side='left')

        self.option_frame = ttk.Frame(frm)
        self.option_frame.pack(fill='x', pady=8)

        # student option
        self.student_combo = ttk.Combobox(self.option_frame)
        self.student_combo.pack(side='left', padx=6)

        # date option
        self.date_entry = ttk.Entry(self.option_frame)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.date_entry.pack(side='left', padx=6)

        ttk.Button(self.option_frame, text='Load', command=self.load_report).pack(side='left', padx=6)

        self.tree = ttk.Treeview(frm, columns=('roll','name','date','status'), show='headings')
        for col, txt in (('roll','Roll No'),('name','Name'),('date','Date'),('status','Status')):
            self.tree.heading(col, text=txt)
        self.tree.pack(fill='both', expand=True)

        self.switch_filter()
        self.populate_students()

    def switch_filter(self):
        mode = self.filter_var.get()
        for w in self.option_frame.winfo_children():
            w.pack_forget()
        if mode == 'student':
            self.student_combo.pack(side='left', padx=6)
            self.populate_students()
            ttk.Button(self.option_frame, text='Load', command=self.load_report).pack(side='left', padx=6)
        else:
            self.date_entry.pack(side='left', padx=6)
            ttk.Button(self.option_frame, text='Load', command=self.load_report).pack(side='left', padx=6)

    def populate_students(self):
        rows = run_query("SELECT id, roll_no || ' - ' || name FROM students ORDER BY class, roll_no", fetch=True)
        options = [r[1] for r in rows]
        ids = [r[0] for r in rows]
        self.student_map = {r[1]: r[0] for r in rows}
        self.student_combo['values'] = options
        if options:
            self.student_combo.current(0)

    def load_report(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        mode = self.filter_var.get()
        if mode == 'student':
            sel = self.student_combo.get()
            if not sel:
                messagebox.showwarning('Select', 'Select a student')
                return
            sid = self.student_map.get(sel)
            rows = run_query('''
                SELECT s.roll_no, s.name, a.date, a.status
                FROM attendance a JOIN students s ON a.student_id = s.id
                WHERE s.id = ? ORDER BY a.date
            ''', (sid,), fetch=True)
        else:
            date = self.date_entry.get().strip()
            try:
                _ = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror('Date error', 'Enter date in YYYY-MM-DD format')
                return
            rows = run_query('''
                SELECT s.roll_no, s.name, a.date, a.status
                FROM attendance a JOIN students s ON a.student_id = s.id
                WHERE a.date = ? ORDER BY s.class, s.roll_no
            ''', (date,), fetch=True)

        for r in rows:
            self.tree.insert('', 'end', values=r)

# ------------------------------- Export --------------------------------------

class ExportWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        self.win.title('Export Data')
        self.win.geometry('400x200')

        frm = ttk.Frame(self.win, padding=10)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text='Choose table to export:').pack(anchor='w')
        self.table_var = tk.StringVar(value='attendance')
        ttk.Radiobutton(frm, text='Attendance', variable=self.table_var, value='attendance').pack(anchor='w')
        ttk.Radiobutton(frm, text='Students', variable=self.table_var, value='students').pack(anchor='w')

        ttk.Button(frm, text='Export', command=self.export).pack(pady=12)

    def export(self):
        table = self.table_var.get()
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv'),('Excel','*.xlsx')])
        if not path:
            return
        if table == 'students':
            rows = run_query('SELECT id, roll_no, name, class FROM students', fetch=True)
            df = pd.DataFrame(rows, columns=['id','roll_no','name','class'])
        else:
            rows = run_query('''
                SELECT a.id, s.roll_no, s.name, s.class, a.date, a.status
                FROM attendance a JOIN students s ON a.student_id = s.id
                ORDER BY a.date, s.class, s.roll_no
            ''', fetch=True)
            df = pd.DataFrame(rows, columns=['id','roll_no','name','class','date','status'])
        try:
            if path.lower().endswith('.xlsx'):
                df.to_excel(path, index=False)
            else:
                df.to_csv(path, index=False)
            messagebox.showinfo('Exported', f'Data exported to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export: {e}')

# ------------------------------- Start App -----------------------------------

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
