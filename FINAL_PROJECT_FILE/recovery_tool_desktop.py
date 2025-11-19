import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from file_operations import scan_files, recover_files
import os

ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")


class RecoveryToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Recovery Tool - Modern Desktop Version")
        self.geometry("1000x650")

        # ========== LEFT PANEL (Controls) ==========
        left_frame = ctk.CTkFrame(self, width=300, corner_radius=15)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="File Recovery Tool", font=("Arial", 22, "bold")).pack(pady=15)

        # Drive input
        ctk.CTkLabel(left_frame, text="Select Drive").pack()
        self.drive_entry = ctk.CTkEntry(left_frame, width=250)
        self.drive_entry.pack()
        ctk.CTkButton(left_frame, text="Browse", command=self.browse_drive).pack(pady=5)

        # Save directory
        ctk.CTkLabel(left_frame, text="Select Save Directory").pack()
        self.save_entry = ctk.CTkEntry(left_frame, width=250)
        self.save_entry.pack()
        ctk.CTkButton(left_frame, text="Browse", command=self.browse_save).pack(pady=5)

        # File type dropdown
        ctk.CTkLabel(left_frame, text="Select File Type").pack(pady=5)
        self.file_type_var = ctk.StringVar(value=".txt")
        self.file_type_dropdown = ctk.CTkOptionMenu(
            left_frame, variable=self.file_type_var,
            values=[".txt", ".docx", ".xlsx", ".pptx", ".pdf", ".jpg", ".png"]
        )
        self.file_type_dropdown.pack()

        # Scan Button
        ctk.CTkButton(left_frame, text="Scan Files", command=self.start_scan).pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(left_frame, width=250)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # Status Label
        self.status_label = ctk.CTkLabel(left_frame, text="")
        self.status_label.pack(pady=5)

        # Appearance mode toggle
        ctk.CTkLabel(left_frame, text="Theme").pack(pady=5)
        self.theme_switch = ctk.CTkSwitch(
            left_frame, text="Dark Mode", command=self.toggle_theme, onvalue="dark", offvalue="light"
        )
        self.theme_switch.select()
        self.theme_switch.pack(pady=5)

        # Recover button
        ctk.CTkButton(left_frame, text="Recover Selected Files", command=self.start_recovery).pack(pady=20)

        # ========== RIGHT PANEL (File List + Preview) ==========
        right_frame = ctk.CTkFrame(self, corner_radius=15)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Files Found", font=("Arial", 18)).pack()
        
        # File Listbox
        self.file_listbox = ctk.CTkTextbox(right_frame, height=300)
        self.file_listbox.pack(fill="x", padx=10, pady=10)

        # Bind click for preview
        self.file_listbox.bind("<ButtonRelease-1>", self.show_preview)

        # Preview frame
        preview_frame = ctk.CTkFrame(right_frame, height=200, corner_radius=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(preview_frame, text="File Preview", font=("Arial", 16)).pack()

        self.preview_label = ctk.CTkLabel(preview_frame, text="")
        self.preview_label.pack(pady=10)

        self.preview_image_label = ctk.CTkLabel(preview_frame, text="")
        self.preview_image_label.pack()

    # ========== Core Functions ==========

    def browse_drive(self):
        path = filedialog.askdirectory()
        if path:
            self.drive_entry.delete(0, "end")
            self.drive_entry.insert(0, path)

    def browse_save(self):
        path = filedialog.askdirectory()
        if path:
            self.save_entry.delete(0, "end")
            self.save_entry.insert(0, path)

    def start_scan(self):
        threading.Thread(target=self.scan).start()

    def scan(self):
        drive = self.drive_entry.get()
        file_type = self.file_type_var.get()

        if not drive:
            messagebox.showerror("Error", "Please select a drive")
            return

        self.status_label.configure(text="Scanning...")
        self.progress.set(0)
        self.file_listbox.delete("1.0", "end")

        files = scan_files(drive, file_type)

        # Sort by size (descending)
        files.sort(key=lambda x: x['size_kb'], reverse=True)

        for f in files:
            self.file_listbox.insert("end", f"{f['path']}\n")

        self.status_label.configure(text=f"Scan Complete. {len(files)} files found.")
        self.progress.set(1)

    def start_recovery(self):
        threading.Thread(target=self.recover).start()

    def recover(self):
        save_dir = self.save_entry.get()

        if not save_dir:
            messagebox.showerror("Error", "Please select a save directory")
            return

        selected_text = self.file_listbox.get("sel.first", "sel.last")

        if not selected_text:
            messagebox.showerror("Error", "Please select files to recover")
            return

        selected_files = selected_text.split("\n")
        selected_files = [{'path': f} for f in selected_files if f.strip() != ""]

        self.status_label.configure(text="Recovering files...")
        recover_files(selected_files, save_dir)

        self.status_label.configure(text="Recovery complete!")
        self.progress.set(1)

    def show_preview(self, event=None):
        try:
            selected_line = self.file_listbox.get("sel.first", "sel.last").strip()

            if selected_line.lower().endswith((".jpg", ".png", ".jpeg")):
                img = Image.open(selected_line)
                img = img.resize((200, 200))
                img = ImageTk.PhotoImage(img)

                self.preview_image_label.configure(image=img)
                self.preview_image_label.image = img
            else:
                # Show text preview
                self.preview_image_label.configure(image="", text="")
                with open(selected_line, "r", errors="ignore") as f:
                    content = f.read(300)
                self.preview_label.configure(text=content)
        except:
            self.preview_label.configure(text="Preview not available.")

    def toggle_theme(self):
        mode = self.theme_switch.get()
        ctk.set_appearance_mode(mode)


if __name__ == "__main__":
    app = RecoveryToolApp()
    app.mainloop()
