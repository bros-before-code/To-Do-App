import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # If running as an exe, return the temporary directory where the resource is extracted
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_tasks_file_path():
    """ Get the path to tasks.json for both reading and writing """
    if hasattr(sys, '_MEIPASS'):
        # When running as an exe (bundled), use the directory where the .exe is
        return os.path.join(os.path.dirname(sys.executable), "tasks.json")
    else:
        # When running as a script, save it in the same directory
        return os.path.join(os.path.abspath("."), "tasks.json")

TASKS_FILE = get_tasks_file_path()

# Load tasks from file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# Center window function
def center_window(win, width, height, y_offset=0):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2)) - y_offset
    win.geometry(f"{width}x{height}+{x}+{y}")

# App class
class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Notepad To-Do List")
        self.root.configure(bg="#fdf6e3")  # light notepad beige

        self.tasks = load_tasks()

        # Fonts (Patrick Hand font for handwritten feel)
        self.font_main = ("Patrick Hand", 14)
        self.font_tasks = ("Patrick Hand", 18)

        # Canvas for lined paper background
        self.canvas = tk.Canvas(root, bg="#fdf6e3")
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Entry
        self.task_entry = tk.Entry(root, width=40, font=self.font_main, relief="solid", bd=1)
        self.task_entry.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.root.grid_rowconfigure(0, minsize=30)
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        self.root.grid_columnconfigure(0, weight=1)

        # Add Button
        self.add_button = tk.Button(root, text="➕ Add Task", command=self.add_task,
                                    bg="#e6e6e6", relief="flat", font=self.font_main)
        self.add_button.grid(row=0, column=1, padx=5, pady=2)

        # Listbox Frame
        self.frame = tk.Frame(root, bg="#fdf6e3")
        self.frame.grid(row=1, column=0, columnspan=2, padx=10, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=2)

        self.listbox = tk.Listbox(self.frame, font=self.font_tasks, selectmode=tk.SINGLE,
                                  bg="#fdf6e3", fg="#333", bd=0, highlightthickness=0,
                                  activestyle="none")
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.refresh_tasks()

        # Bottom buttons
        self.done_button = tk.Button(root, text="✅ Mark Done", command=self.mark_done,
                                     bg="#d0f0c0", relief="flat", font=self.font_main)
        self.done_button.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.delete_button = tk.Button(root, text="🗑️ Delete", command=self.delete_task,
                                       bg="#f0d0d0", relief="flat", font=self.font_main)
        self.delete_button.grid(row=2, column=1, sticky="e", padx=10, pady=10)

        self.edit_button = tk.Button(root, text="✏️ Edit", command=self.edit_task,
                                    bg="#fff1b5", relief="flat", font=self.font_main)
        self.edit_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.listbox.bind("<<ListboxSelect>>", self.prefill_entry)

    def refresh_tasks(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            status = "✅" if task["done"] else "❌"
            title = task['title']
            created = task.get("created", "")
            done_time = task.get("done_time", "")

            if task["done"] and done_time:
                timestamp = f"🕒 Added: {created} | ✔ Done: {done_time}"
            else:
                timestamp = f"🕒 Added: {created}"

            self.listbox.insert(tk.END, f"{status} {title} — {timestamp}")

    def add_task(self):
        title = self.task_entry.get().strip().capitalize()
        if title:
            timestamp = datetime.now().strftime("%b %d, %Y %I:%M %p")
            self.tasks.append({
                "title": title,
                "done": False,
                "created": timestamp,
                "done_time": None
            })
            self.task_entry.delete(0, tk.END)
            save_tasks(self.tasks)
            self.refresh_tasks()

    def mark_done(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.tasks[index]["done"] = True
            self.tasks[index]["done_time"] = datetime.now().strftime("%b %d, %Y %I:%M %p")
            save_tasks(self.tasks)
            self.refresh_tasks()

    def delete_task(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            del self.tasks[index]
            save_tasks(self.tasks)
            self.refresh_tasks()

    def edit_task(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Edit Task", "Please select a task to edit.")
            return

        index = selection[0]
        task = self.tasks[index]

        # Create a new top-level window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.configure(bg="#fdf6e3")
        edit_window.geometry("300x150")
        edit_window.grab_set()  # Make it modal

        tk.Label(edit_window, text="Edit Task Title:", font=self.font_main, bg="#fdf6e3").pack(pady=10)

        entry = tk.Entry(edit_window, font=self.font_main, width=30)
        entry.insert(0, task["title"])
        entry.pack(pady=5)

        def save_edit():
            new_title = entry.get().strip().capitalize()
            if new_title:
                self.tasks[index]["title"] = new_title
                save_tasks(self.tasks)
                self.refresh_tasks()
                edit_window.destroy()
            else:
                messagebox.showwarning("Edit Task", "Title cannot be empty.")

        tk.Button(edit_window, text="💾 Save", command=save_edit,
                    bg="#cdeac0", font=self.font_main).pack(pady=10)

    def prefill_entry(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.task_entry.delete(0, tk.END)
            self.task_entry.insert(0, self.tasks[index]["title"])

# Run it
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)  # Allow resizing of the window
    center_window(root, 800, 600, y_offset=50)  # Initial window size and centered
    app = ToDoApp(root)
    root.mainloop()

