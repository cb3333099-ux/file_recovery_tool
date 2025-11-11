import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from file_operations import scan_files, recover_files

class RecoveryToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Recovery Tool - Desktop Version")
        self.root.geometry("800x600")

        # Drive selection
        tk.Label(root, text="Select Drive").pack()
        self.drive_entry = tk.Entry(root, width=50)
        self.drive_entry.pack()
        tk.Button(root, text="Browse", command=self.browse_drive).pack()

        # Save directory
        tk.Label(root, text="Select Save Directory").pack()
        self.save_entry = tk.Entry(root, width=50)
        self.save_entry.pack()
        tk.Button(root, text="Browse", command=self.browse_save).pack()

        # File type selection
        tk.Label(root, text="Select File Type").pack()
        self.file_type_var = tk.StringVar(value=".txt")
        tk.OptionMenu(root, self.file_type_var, ".txt", ".docx", ".xlsx", ".pptx", ".pdf", ".jpg", ".png").pack()

        # Scan button
        tk.Button(root, text="Scan for Deleted Files", command=self.start_scan).pack(pady=10)

        # Progress
        tk.Label(root, text="Scanning Progress").pack()
        self.progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=5)

        # File list
        tk.Label(root, text="Deleted Files Found").pack()
        self.file_list = tk.Listbox(root, width=100, height=15, selectmode=tk.MULTIPLE)
        self.file_list.pack(pady=5)

        # Recover button
        tk.Button(root, text="Recover Selected Files", command=self.start_recovery).pack(pady=10)

    def browse_drive(self):
        path = filedialog.askdirectory()
        self.drive_entry.delete(0, tk.END)
        self.drive_entry.insert(0, path)

    def browse_save(self):
        path = filedialog.askdirectory()
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(0, path)

    def start_scan(self):
        threading.Thread(target=self.scan).start()

    def scan(self):
        drive = self.drive_entry.get()
        file_type = self.file_type_var.get()
        if not drive:
            messagebox.showerror("Error", "Please select a drive")
            return
        self.status_label.config(text="Scanning...")
        self.progress_bar['value'] = 0
        files = scan_files(drive, file_type)
        self.file_list.delete(0, tk.END)
        for f in files:
            self.file_list.insert(tk.END, f"{f['modified_time']} - {f['path']}")
        self.status_label.config(text="Scan complete.")
        self.progress_bar['value'] = 100

    def start_recovery(self):
        threading.Thread(target=self.recover).start()

    def recover(self):
        save_dir = self.save_entry.get()
        selected = self.file_list.curselection()
        if not save_dir:
            messagebox.showerror("Error", "Please select a save directory")
            return
        if not selected:
            messagebox.showerror("Error", "Please select files to recover")
            return
        self.status_label.config(text="Recovering files...")
        selected_files = [{'path': self.file_list.get(i).split(" - ")[1]} for i in selected]
        recover_files(selected_files, save_dir)
        self.status_label.config(text="Recovery complete.")
        self.progress_bar['value'] = 100


if __name__ == "__main__":
    root = tk.Tk()
    app = RecoveryToolApp(root)
    root.mainloop()
