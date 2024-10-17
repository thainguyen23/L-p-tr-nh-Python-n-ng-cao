import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2

# Kết nối đến cơ sở dữ liệu PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="student_management.db",  # Đổi tên cơ sở dữ liệu
        user="postgres",
        password="0935109623tn",
        port="5432"
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Cannot connect to the database: {e}")
    exit()

# Hàm thêm sinh viên


def reset_ids():
    cursor.execute("SELECT id FROM students ORDER BY id")
    rows = cursor.fetchall()
    new_id = 1
    for row in rows:
        cursor.execute(
            "UPDATE students SET id = %s WHERE id = %s", (new_id, row[0]))
        new_id += 1
    conn.commit()


def add_student():
    name = entry_name.get()
    try:
        age = int(entry_age.get())
    except ValueError:
        messagebox.showwarning("Input Error", "Age must be a number.")
        return
    gender = entry_gender.get()
    major = combo_major.get()  # Sử dụng combo box để lấy giá trị ngành
    if name and age and gender and major:
        cursor.execute("INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s)",
                       (name, age, gender, major))
        conn.commit()
        reset_ids()
        messagebox.showinfo("Success", "Student added successfully!")
        reload_list()
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

# Hàm cập nhật thông tin sinh viên


def update_student():
    selected = tree.selection()
    if selected:
        student_id = tree.item(selected[0])['values'][0]
        name = entry_name.get()
        try:
            age = int(entry_age.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Age must be a number.")
            return
        gender = entry_gender.get()
        major = combo_major.get()  # Sử dụng combo box để lấy giá trị ngành
        if name and age and gender and major:
            cursor.execute("UPDATE students SET name=%s, age=%s, gender=%s, major=%s WHERE id=%s",
                           (name, age, gender, major, student_id))
            conn.commit()
            reset_ids()
            messagebox.showinfo("Success", "Student updated successfully!")
            reload_list()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
    else:
        messagebox.showwarning(
            "Selection Error", "Please select a student to update.")

# Hàm xóa sinh viên


def delete_student():
    selected = tree.selection()
    if selected:
        student_id = tree.item(selected[0])['values'][0]
        cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
        conn.commit()
        messagebox.showinfo("Success", "Student deleted successfully!")
        reload_list()
        reset_ids()
    else:
        messagebox.showwarning(
            "Selection Error", "Please select a student to delete.")

# Hàm tải lại danh sách sinh viên


def reload_list():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

# Hàm để hiện thông tin sinh viên theo ngành


def show_students_by_major():
    major = combo_select_major.get()  # Lấy ngành từ ComboBox
    for row in tree_major.get_children():
        tree_major.delete(row)

    # Truy vấn sinh viên dựa trên chuyên ngành đã chọn
    cursor.execute("""
        SELECT s.id, s.name, s.age, s.gender, c.teacher, c.course_code
        FROM students s
        JOIN classes c ON s.major = c.major
        WHERE s.major = %s
    """, (major,))

    # Thêm kết quả vào treeview
    for row in cursor.fetchall():
        tree_major.insert("", tk.END, values=row)


# Tạo giao diện GUI
root = tk.Tk()
root.title("Student Management")
root.configure(bg='#f0f0f0')

# Tạo style cho các nút
style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 8, "bold"),
                background="#4CAF50",
                foreground="black",
                padding=6)
style.map("TButton",
          background=[('active', '#45a049')],
          relief=[('pressed', 'sunken')])

tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

# Tab quản lý sinh viên
tab_students = ttk.Frame(tab_control)
tab_control.add(tab_students, text="Students")

# Tab hiển thị sinh viên theo chuyên ngành
tab_show_students = ttk.Frame(tab_control)
tab_control.add(tab_show_students, text="Show Students by Major")

# Frame đầu tiên để nhập thông tin (2 dòng)
frame_top = tk.Frame(tab_students, bg='#f0f0f0')
frame_top.pack(pady=10)

label_name = tk.Label(frame_top, text="Name:", bg='#f0f0f0')
label_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_name = tk.Entry(frame_top)
entry_name.grid(row=0, column=1, padx=5, pady=5)

label_age = tk.Label(frame_top, text="Age:", bg='#f0f0f0')
label_age.grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_age = tk.Entry(frame_top)
entry_age.grid(row=0, column=3, padx=5, pady=5)

label_gender = tk.Label(frame_top, text="Gender:", bg='#f0f0f0')
label_gender.grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_gender = tk.Entry(frame_top)
entry_gender.grid(row=1, column=1, padx=5, pady=5)

label_major = tk.Label(frame_top, text="Major:", bg='#f0f0f0')
label_major.grid(row=1, column=2, padx=5, pady=5, sticky="w")
combo_major = ttk.Combobox(frame_top, values=[
    "Công nghệ thông tin", "Quan hệ công chúng", "Thiết kế", "Quản trị kinh doanh", "Kế toán", "Cơ khí - Điện tử"])  # Danh sách ngành
combo_major.grid(row=1, column=3, padx=5, pady=5)

# Frame giữa để chứa các nút chức năng
frame_buttons = tk.Frame(tab_students, bg='#f0f0f0')
frame_buttons.pack(pady=10)

button_width = 15
btn_add = ttk.Button(frame_buttons, text="Add Student", command=add_student)
btn_add.grid(row=0, column=0, padx=5, pady=5)

btn_update = ttk.Button(
    frame_buttons, text="Update Student", command=update_student)
btn_update.grid(row=0, column=1, padx=5, pady=5)

btn_delete = ttk.Button(
    frame_buttons, text="Delete Student", command=delete_student)
btn_delete.grid(row=0, column=2, padx=5, pady=5)

btn_reload = ttk.Button(frame_buttons, text="Reload List", command=reload_list)
btn_reload.grid(row=0, column=3, padx=5, pady=5)

# Frame dưới để chứa danh sách sinh viên
frame_bottom = tk.Frame(tab_students)
frame_bottom.pack(pady=10)

tree = ttk.Treeview(frame_bottom, columns=(
    "ID", "Name", "Age", "Gender", "Major"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Age", text="Age")
tree.heading("Gender", text="Gender")
tree.heading("Major", text="Major")

tree.column("ID", anchor="center", width=50)
tree.column("Name", anchor="center", width=150)
tree.column("Age", anchor="center", width=50)
tree.column("Gender", anchor="center", width=100)
tree.column("Major", anchor="center", width=150)

tree.pack(padx=10, pady=5)

# Khởi tạo danh sách sinh viên khi ứng dụng khởi động
reload_list()

# Tab thứ hai để chọn ngành
label_select_major = tk.Label(
    tab_show_students, text="Select Major:", bg='#f0f0f0')
label_select_major.pack(pady=5)

combo_select_major = ttk.Combobox(tab_show_students, values=[
    "Công nghệ thông tin", "Quan hệ công chúng", "Thiết kế", "Quản trị kinh doanh", "Kế toán", "Cơ khí - Điện tử"])
combo_select_major.pack(pady=5)

btn_show_students = ttk.Button(
    tab_show_students, text="Show Students", command=show_students_by_major)
btn_show_students.pack(pady=5)

# Treeview để hiển thị thông tin sinh viên theo ngành
tree_major = ttk.Treeview(tab_show_students, columns=(
    "ID", "Name", "Age", "Gender", "Teacher", "Course Code"), show="headings")
tree_major.heading("ID", text="ID")
tree_major.heading("Name", text="Name")
tree_major.heading("Age", text="Age")
tree_major.heading("Gender", text="Gender")
tree_major.heading("Teacher", text="Teacher")
tree_major.heading("Course Code", text="Course Code")

tree_major.column("ID", anchor="center", width=50)
tree_major.column("Name", anchor="center", width=150)
tree_major.column("Age", anchor="center", width=50)
tree_major.column("Gender", anchor="center", width=100)
tree_major.column("Teacher", anchor="center", width=150)
tree_major.column("Course Code", anchor="center", width=150)

tree_major.pack(padx=10, pady=5)

root.mainloop()

# Đóng kết nối cơ sở dữ liệu khi ứng dụng kết thúc
conn.close()
