import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "library.db"

# ---------------- DATABASE ---------------- #
def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT,
        member_type TEXT,
        contact TEXT,
        email TEXT,
        valid_till TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_code TEXT UNIQUE,
        book_name TEXT,
        author TEXT,
        category TEXT,
        status TEXT DEFAULT 'Available'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        book_id INTEGER,
        issue_date TEXT,
        return_date TEXT,
        actual_return_date TEXT,
        fine REAL DEFAULT 0,
        status TEXT DEFAULT 'Issued'
    )
    """)

    # Default users
    cur.execute("SELECT * FROM users WHERE username='adm'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("adm", "adm", "admin"))

    cur.execute("SELECT * FROM users WHERE username='user'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user", "user", "user"))

    # Sample books
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        sample_books = [
            ("SCB000001", "Physics Fundamentals", "R.K. Sharma", "Science"),
            ("SCB000002", "Chemistry Basics", "Amit Verma", "Science"),
            ("ECB000001", "Indian Economy", "Ramesh Singh", "Economics"),
            ("FCB000001", "The Alchemist", "Paulo Coelho", "Fiction"),
            ("CHB000001", "Moral Stories", "Unknown", "Children"),
            ("PDB000001", "Atomic Habits", "James Clear", "Personal Development"),
        ]
        cur.executemany("INSERT INTO books (book_code, book_name, author, category) VALUES (?, ?, ?, ?)", sample_books)

    conn.commit()
    conn.close()

def validate_login(username, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# ---------------- BOOK MANAGEMENT ---------------- #
def open_books_window():
    win = tk.Toplevel()
    win.title("Book Maintenance")
    win.geometry("900x550")

    tk.Label(win, text="Book Maintenance", font=("Arial", 18, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Book Code").grid(row=0, column=0, padx=5, pady=5)
    code_entry = tk.Entry(form)
    code_entry.grid(row=0, column=1)

    tk.Label(form, text="Book Name").grid(row=1, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form)
    name_entry.grid(row=1, column=1)

    tk.Label(form, text="Author").grid(row=2, column=0, padx=5, pady=5)
    author_entry = tk.Entry(form)
    author_entry.grid(row=2, column=1)

    tk.Label(form, text="Category").grid(row=3, column=0, padx=5, pady=5)
    category_entry = tk.Entry(form)
    category_entry.grid(row=3, column=1)

    tree = ttk.Treeview(win, columns=("ID", "Code", "Name", "Author", "Category", "Status"), show="headings")
    for col in ("ID", "Code", "Name", "Author", "Category", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=140)
    tree.pack(pady=20, fill="both", expand=True)

    def load_books():
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM books")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def add_book():
        code = code_entry.get().strip()
        name = name_entry.get().strip()
        author = author_entry.get().strip()
        category = category_entry.get().strip()

        if not code or not name or not author or not category:
            messagebox.showwarning("Validation", "All fields are required")
            return

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO books (book_code, book_name, author, category) VALUES (?, ?, ?, ?)",
                        (code, name, author, category))
            conn.commit()
            messagebox.showinfo("Success", "Book Added Successfully")
            load_books()
        except:
            messagebox.showerror("Error", "Book Code already exists")
        conn.close()

    tk.Button(form, text="Add Book", bg="green", fg="white", command=add_book).grid(row=4, column=0, columnspan=2, pady=10)

    load_books()

# ---------------- MEMBERSHIP MANAGEMENT ---------------- #
def open_membership_window():
    win = tk.Toplevel()
    win.title("Membership Management")
    win.geometry("900x550")

    tk.Label(win, text="Membership Management", font=("Arial", 18, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Member Name").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form)
    name_entry.grid(row=0, column=1)

    tk.Label(form, text="Member Type").grid(row=1, column=0, padx=5, pady=5)
    type_entry = tk.Entry(form)
    type_entry.grid(row=1, column=1)

    tk.Label(form, text="Contact").grid(row=2, column=0, padx=5, pady=5)
    contact_entry = tk.Entry(form)
    contact_entry.grid(row=2, column=1)

    tk.Label(form, text="Email").grid(row=3, column=0, padx=5, pady=5)
    email_entry = tk.Entry(form)
    email_entry.grid(row=3, column=1)

    tk.Label(form, text="Valid Till").grid(row=4, column=0, padx=5, pady=5)
    valid_entry = tk.Entry(form)
    valid_entry.grid(row=4, column=1)

    tree = ttk.Treeview(win, columns=("ID", "Name", "Type", "Contact", "Email", "Valid"), show="headings")
    for col in ("ID", "Name", "Type", "Contact", "Email", "Valid"):
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(fill="both", expand=True, pady=20)

    def load_members():
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM memberships")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def add_member():
        if not name_entry.get().strip():
            messagebox.showwarning("Validation", "Member Name required")
            return
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO memberships (member_name, member_type, contact, email, valid_till)
        VALUES (?, ?, ?, ?, ?)
        """, (name_entry.get(), type_entry.get(), contact_entry.get(), email_entry.get(), valid_entry.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Membership Added")
        load_members()

    tk.Button(form, text="Add Membership", bg="blue", fg="white", command=add_member).grid(row=5, column=0, columnspan=2, pady=10)

    load_members()

# ---------------- ISSUE / RETURN ---------------- #
def open_issue_return_window():
    win = tk.Toplevel()
    win.title("Transactions")
    win.geometry("1050x600")

    tk.Label(win, text="Book Issue / Return", font=("Arial", 18, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Member ID").grid(row=0, column=0, padx=5, pady=5)
    member_entry = tk.Entry(form)
    member_entry.grid(row=0, column=1)

    tk.Label(form, text="Book ID").grid(row=1, column=0, padx=5, pady=5)
    book_entry = tk.Entry(form)
    book_entry.grid(row=1, column=1)

    tree = ttk.Treeview(win, columns=("IssueID", "MemberID", "BookID", "IssueDate", "ReturnDate", "ActualReturn", "Fine", "Status"), show="headings")
    for col in ("IssueID", "MemberID", "BookID", "IssueDate", "ReturnDate", "ActualReturn", "Fine", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, pady=20)

    def load_issues():
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM issues")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def issue_book():
        member_id = member_entry.get().strip()
        book_id = book_entry.get().strip()

        if not member_id or not book_id:
            messagebox.showwarning("Validation", "Enter Member ID and Book ID")
            return

        issue_date = datetime.today().strftime("%Y-%m-%d")
        return_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT status FROM books WHERE id=?", (book_id,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", "Book not found")
            conn.close()
            return

        if row[0] != "Available":
            messagebox.showwarning("Unavailable", "Book already issued")
            conn.close()
            return

        cur.execute("INSERT INTO issues (member_id, book_id, issue_date, return_date) VALUES (?, ?, ?, ?)",
                    (member_id, book_id, issue_date, return_date))
        cur.execute("UPDATE books SET status='Issued' WHERE id=?", (book_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Book Issued Successfully")
        load_issues()

    def return_book():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an issue record")
            return

        values = tree.item(selected[0], "values")
        issue_id = values[0]
        book_id = values[2]
        due_date = datetime.strptime(values[4], "%Y-%m-%d")
        today = datetime.today()
        late_days = (today - due_date).days
        fine = late_days * 5 if late_days > 0 else 0

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        UPDATE issues
        SET actual_return_date=?, fine=?, status='Returned'
        WHERE id=?
        """, (today.strftime("%Y-%m-%d"), fine, issue_id))
        cur.execute("UPDATE books SET status='Available' WHERE id=?", (book_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Returned", f"Book Returned. Fine = ₹{fine}")
        load_issues()

    btn_frame = tk.Frame(win)
    btn_frame.pack()

    tk.Button(btn_frame, text="Issue Book", bg="green", fg="white", width=15, command=issue_book).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Return Book", bg="orange", fg="white", width=15, command=return_book).grid(row=0, column=1, padx=10)

    load_issues()

# ---------------- REPORTS ---------------- #
def open_reports_window():
    win = tk.Toplevel()
    win.title("Reports")
    win.geometry("950x550")

    tk.Label(win, text="Reports", font=("Arial", 18, "bold")).pack(pady=10)

    tree = ttk.Treeview(win, columns=("Col1", "Col2", "Col3", "Col4", "Col5"), show="headings")
    for col in ("Col1", "Col2", "Col3", "Col4", "Col5"):
        tree.heading(col, text=col)
        tree.column(col, width=170)
    tree.pack(fill="both", expand=True, pady=20)

    def clear_tree():
        for row in tree.get_children():
            tree.delete(row)

    def show_books():
        clear_tree()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, book_code, book_name, author, status FROM books")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def show_members():
        clear_tree()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, member_name, member_type, contact, valid_till FROM memberships")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def show_active_issues():
        clear_tree()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, member_id, book_id, issue_date, return_date FROM issues WHERE status='Issued'")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Master List of Books", width=20, command=show_books).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Membership Report", width=20, command=show_members).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Active Issues", width=20, command=show_active_issues).grid(row=0, column=2, padx=5)

# ---------------- ADMIN HOME ---------------- #
def open_admin_home():
    root = tk.Tk()
    root.title("Admin Home Page")
    root.geometry("700x500")
    root.config(bg="white")

    tk.Label(root, text="Admin Home Page", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

    frame = tk.Frame(root, bg="white")
    frame.pack(pady=20)

    tk.Button(frame, text="Maintenance - Books", width=25, height=2, bg="#4CAF50", fg="white",
              command=open_books_window).grid(row=0, column=0, padx=10, pady=10)

    tk.Button(frame, text="Maintenance - Membership", width=25, height=2, bg="#2196F3", fg="white",
              command=open_membership_window).grid(row=0, column=1, padx=10, pady=10)

    tk.Button(frame, text="Transactions", width=25, height=2, bg="#FF9800", fg="white",
              command=open_issue_return_window).grid(row=1, column=0, padx=10, pady=10)

    tk.Button(frame, text="Reports", width=25, height=2, bg="#9C27B0", fg="white",
              command=open_reports_window).grid(row=1, column=1, padx=10, pady=10)

    def logout():
        root.destroy()
        start_login()

    tk.Button(root, text="Logout", width=15, bg="red", fg="white", command=logout).pack(pady=20)

    root.mainloop()

# ---------------- USER HOME ---------------- #
def open_user_home():
    root = tk.Tk()
    root.title("User Home Page")
    root.geometry("700x450")
    root.config(bg="white")

    tk.Label(root, text="User Home Page", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

    frame = tk.Frame(root, bg="white")
    frame.pack(pady=30)

    tk.Button(frame, text="Transactions", width=25, height=2, bg="#FF9800", fg="white",
              command=open_issue_return_window).grid(row=0, column=0, padx=15, pady=10)

    tk.Button(frame, text="Reports", width=25, height=2, bg="#9C27B0", fg="white",
              command=open_reports_window).grid(row=0, column=1, padx=15, pady=10)

    def logout():
        root.destroy()
        start_login()

    tk.Button(root, text="Logout", width=15, bg="red", fg="white", command=logout).pack(pady=20)

    root.mainloop()

# ---------------- LOGIN ---------------- #
def start_login():
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("500x350")
    root.config(bg="#f5f5f5")

    tk.Label(root, text="Library Management System", font=("Arial", 18, "bold"), bg="#f5f5f5").pack(pady=20)

    tk.Label(root, text="User ID", bg="#f5f5f5", font=("Arial", 12)).pack()
    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.pack(pady=5)

    tk.Label(root, text="Password", bg="#f5f5f5", font=("Arial", 12)).pack()
    password_entry = tk.Entry(root, show="*", font=("Arial", 12))
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        role = validate_login(username, password)

        if role == "admin":
            root.destroy()
            open_admin_home()
        elif role == "user":
            root.destroy()
            open_user_home()
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")

    tk.Button(root, text="Login", width=15, bg="green", fg="white", font=("Arial", 12), command=login).pack(pady=20)

    tk.Label(root, text="Admin: adm / adm | User: user / user", bg="#f5f5f5", fg="gray").pack()

    root.mainloop()

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    create_tables()
    start_login()
